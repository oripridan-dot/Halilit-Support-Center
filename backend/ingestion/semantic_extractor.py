"""
Semantic Extractor — Resilient Ingestion Engine
================================================
Implements the "Semantic Extraction" layer from spec:
  specs/data_pipeline/03_resilient_ingestion.md

Two-stage strategy to replace brittle CSS/regex scraping:

  Stage 1 — API Sniffer (Ghost Protocol):
    Probes for hidden JSON endpoints (__NEXT_DATA__, Shopify API, WooCommerce REST,
    Magento REST) before attempting HTML parsing. If a clean JSON payload is found,
    we use it directly — no HTML parsing at all.

  Stage 2 — LLM Semantic Fallback:
    When no API endpoint is available, convert the rendered page HTML to plain
    Markdown text and pass it to Gemini with a strict `response_schema` (Structured
    Output). Gemini reads the *meaning* of the page — not the CSS classes — making
    extraction immune to cosmetic website restructures.

Graceful Degradation:
    Every failure is logged to a dead-letter queue (JSONL file). The pipeline
    retains the last known cached data for the SKU and continues.

Usage:
    extractor = SemanticExtractor()

    # API-first probe (Halilit / any e-com site):
    product = extractor.api_first_extract(url)

    # LLM fallback (official brand pages that block bots or use SPAs):
    product = extractor.semantic_extract(html_or_url, source_type="official")

    # Combined pipeline:
    product = extractor.extract(url, html=rendered_html)
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger("SemanticExtractor")

# ═══════════════════════════════════════════════════════════════════════════
# DEAD-LETTER QUEUE
# ═══════════════════════════════════════════════════════════════════════════

_DLQ_PATH = Path(os.environ.get(
    "INGESTION_DLQ_PATH",
    str(Path(__file__).parent.parent / "data" /
        "ingestion" / "dead_letter_queue.jsonl"),
))


def _write_dlq(url: str, reason: str, context: Optional[Dict] = None) -> None:
    """Append an extraction failure record to the dead-letter queue."""
    try:
        _DLQ_PATH.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "url": url,
            "reason": reason,
            "context": context or {},
        }
        with _DLQ_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        logger.warning("[DLQ] %s — %s", url, reason)
    except Exception as exc:
        logger.debug("[DLQ] Could not write record: %s", exc)


# ═══════════════════════════════════════════════════════════════════════════
# GEMINI STRUCTURED OUTPUT SCHEMA
# ═══════════════════════════════════════════════════════════════════════════

# Gemini response_schema (Pydantic-compatible dict for google.genai)
_PRODUCT_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "price": {
            "type": "NUMBER",
            "description": "Product price as a float (e.g. 1249.0). Use 0 if not found.",
        },
        "price_currency": {
            "type": "STRING",
            "description": "ISO 4217 currency code (e.g. ILS, USD, EUR). Empty string if unknown.",
        },
        "stock_status": {
            "type": "STRING",
            "description": "One of: 'in_stock', 'out_of_stock', 'limited', 'unknown'.",
        },
        "sku": {
            "type": "STRING",
            "description": "Product SKU / model number as shown on the page. Empty string if not found.",
        },
        "title": {
            "type": "STRING",
            "description": "Full product title as shown on the page.",
        },
        "description": {
            "type": "STRING",
            "description": "Product description or marketing copy. Empty string if not found.",
        },
        "brand": {
            "type": "STRING",
            "description": "Brand / manufacturer name.",
        },
        "image_url": {
            "type": "STRING",
            "description": "Primary product image URL. Empty string if not found.",
        },
        "specs": {
            "type": "OBJECT",
            "description": "Technical specifications as key-value pairs. Keys are spec names, values are spec values.",
            "additionalProperties": {"type": "STRING"},
        },
        "features": {
            "type": "ARRAY",
            "description": "List of key product features / bullet points.",
            "items": {"type": "STRING"},
        },
    },
    "required": ["price", "stock_status", "sku", "title", "specs"],
}

_EXTRACTION_PROMPT_TEMPLATE = """\
You are a product data extraction assistant. Extract the following data from the page text below.
Follow these rules STRICTLY:
- Only extract data that is EXPLICITLY present on the page.
- Do NOT invent, infer, or fabricate any values.
- For "specs", extract key-value technical specifications (e.g. "Frequency Response": "20Hz-20kHz").
- For "stock_status", use exactly one of: "in_stock", "out_of_stock", "limited", "unknown".
- For "price", extract the numeric value only (e.g. 1249.0). Use 0 if not shown.
- For "sku", extract the part number or model code if visible.
- Set empty string ("") for any field that is not present on the page.

--- PAGE CONTENT ---
{page_text}
--- END PAGE CONTENT ---

Respond ONLY with JSON matching the specified schema. No markdown, no commentary.
"""


# ═══════════════════════════════════════════════════════════════════════════
# SHOPIFY / WOOCOMMERCE / MAGENTO / __NEXT_DATA__ SNIFFERS
# ═══════════════════════════════════════════════════════════════════════════

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8",
}


def _sniff_shopify_json(base_url: str, session: requests.Session, timeout: int = 8) -> Optional[Dict]:
    """
    Probe Shopify product JSON endpoint.
    Shopify exposes: {product_url}.json → {"product": {...}}
    """
    # Strip query string
    clean_url = base_url.split("?")[0].rstrip("/")
    candidates = [
        f"{clean_url}.json",
        re.sub(r"/products/", "/products/", clean_url) + ".json",
    ]
    for url in candidates:
        try:
            r = session.get(url, timeout=timeout)
            if r.status_code == 200:
                data = r.json()
                if "product" in data or "variants" in data.get("product", {}):
                    logger.info("[API-FIRST] Shopify endpoint found: %s", url)
                    return _normalize_shopify(data.get("product", data))
        except Exception:
            continue
    return None


def _normalize_shopify(product: Dict) -> Dict:
    """Normalize a Shopify product payload to our internal schema."""
    variants = product.get("variants", [{}])
    first = variants[0] if variants else {}
    images = product.get("images", [])
    specs: Dict[str, str] = {}
    for meta in product.get("metafields", []):
        key = meta.get("key", "")
        value = str(meta.get("value", ""))
        if key:
            specs[key] = value

    price_raw = first.get("price", "0")
    try:
        price = float(price_raw)
    except (ValueError, TypeError):
        price = 0.0

    available = first.get("available", True)
    if isinstance(available, bool):
        stock_status = "in_stock" if available else "out_of_stock"
    else:
        stock_status = "unknown"

    return {
        "title": product.get("title", ""),
        "brand": product.get("vendor", ""),
        "description": re.sub(r"<[^>]+>", " ", product.get("body_html", "")),
        "price": price,
        "price_currency": "ILS",
        "stock_status": stock_status,
        "sku": first.get("sku", ""),
        "image_url": images[0].get("src", "") if images else "",
        "specs": specs,
        "features": [],
        "_source": "shopify_api",
    }


def _sniff_woocommerce_json(base_url: str, session: requests.Session, timeout: int = 8) -> Optional[Dict]:
    """
    Probe WooCommerce REST API v3.
    Requires no auth for public products (with public keys) OR uses slug lookup.
    """
    # Extract slug from URL
    slug_match = re.search(r'/product/([^/?#]+)', base_url)
    if not slug_match:
        return None
    slug = slug_match.group(1)
    domain_match = re.match(r'(https?://[^/]+)', base_url)
    if not domain_match:
        return None
    domain = domain_match.group(1)

    endpoints = [
        f"{domain}/wp-json/wc/v3/products?slug={slug}&per_page=1",
        f"{domain}/wp-json/wc/v2/products?slug={slug}&per_page=1",
    ]
    for url in endpoints:
        try:
            r = session.get(url, timeout=timeout)
            if r.status_code == 200:
                products = r.json()
                if products and isinstance(products, list):
                    logger.info(
                        "[API-FIRST] WooCommerce endpoint found: %s", url)
                    return _normalize_woocommerce(products[0])
        except Exception:
            continue
    return None


def _normalize_woocommerce(product: Dict) -> Dict:
    """Normalize WooCommerce product to our internal schema."""
    images = product.get("images", [])
    specs: Dict[str, str] = {}
    for attr in product.get("attributes", []):
        name = attr.get("name", "")
        options = attr.get("options", [])
        if name and options:
            specs[name] = ", ".join(str(o) for o in options)

    price_raw = product.get("price", "0")
    try:
        price = float(price_raw)
    except (ValueError, TypeError):
        price = 0.0

    stock_map = {
        "instock": "in_stock",
        "outofstock": "out_of_stock",
        "onbackorder": "limited",
    }
    raw_stock = product.get("stock_status", "")
    stock_status = stock_map.get(raw_stock, "unknown")

    return {
        "title": product.get("name", ""),
        "brand": "",
        "description": re.sub(r"<[^>]+>", " ", product.get("description", "")),
        "price": price,
        "price_currency": "ILS",
        "stock_status": stock_status,
        "sku": product.get("sku", ""),
        "image_url": images[0].get("src", "") if images else "",
        "specs": specs,
        "features": [],
        "_source": "woocommerce_api",
    }


def _sniff_next_data(html: str) -> Optional[Dict]:
    """
    Extract product data from Next.js __NEXT_DATA__ JSON blob embedded in HTML.
    Many modern React/Next.js storefronts embed their full page data here.
    """
    match = re.search(
        r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return None
    try:
        next_data = json.loads(match.group(1))
        props = next_data.get("props", {})
        page_props = props.get("pageProps", {})
        # Common field names across Next.js storefronts
        for key in ("product", "item", "productData", "data"):
            candidate = page_props.get(key)
            if candidate and isinstance(candidate, dict):
                logger.info(
                    "[API-FIRST] __NEXT_DATA__ product payload found (key: %s)", key)
                return _normalize_next_data_product(candidate)
        # Deep search: walk the structure looking for price field
        product = _deep_find_product(page_props)
        if product:
            logger.info(
                "[API-FIRST] __NEXT_DATA__ (deep search) product payload found")
            return _normalize_next_data_product(product)
    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        logger.debug("[__NEXT_DATA__] Parse error: %s", exc)
    return None


def _deep_find_product(obj: Any, depth: int = 0) -> Optional[Dict]:
    """Recursively locate a dict that looks like a product (has price or sku)."""
    if depth > 4 or not isinstance(obj, dict):
        return None
    if any(k in obj for k in ("price", "sku", "Price", "SKU", "מחיר")):
        return obj
    for v in obj.values():
        result = _deep_find_product(v, depth + 1)
        if result:
            return result
    return None


def _normalize_next_data_product(product: Dict) -> Dict:
    """Normalize a generic __NEXT_DATA__ product dict to our internal schema."""
    # Price: try various common keys
    raw_price = (
        product.get("price")
        or product.get("Price")
        or product.get("price_ils")
        or product.get("salePrice")
        or product.get("מחיר")
        or 0
    )
    try:
        price = float(str(raw_price).replace(
            ",", "").replace("₪", "").strip() or 0)
    except (ValueError, TypeError):
        price = 0.0

    sku = str(
        product.get("sku")
        or product.get("SKU")
        or product.get("catalogNumber")
        or product.get("catalog_number")
        or ""
    )

    title = str(
        product.get("name")
        or product.get("title")
        or product.get("productName")
        or product.get("שם")
        or ""
    )

    description = str(
        product.get("description")
        or product.get("shortDescription")
        or product.get("תיאור")
        or ""
    )

    images = product.get("images") or []
    image_url = ""
    if isinstance(images, list) and images:
        first = images[0]
        image_url = first if isinstance(
            first, str) else first.get("url", first.get("src", ""))
    elif isinstance(product.get("image"), str):
        image_url = product["image"]

    # Specs
    specs: Dict[str, str] = {}
    for key in ("specs", "specifications", "features", "attributes"):
        spec_block = product.get(key)
        if isinstance(spec_block, dict):
            for k, v in spec_block.items():
                specs[str(k)] = str(v)
        elif isinstance(spec_block, list):
            for item in spec_block:
                if isinstance(item, dict):
                    k = item.get("name") or item.get("key") or ""
                    v = item.get("value") or item.get("val") or ""
                    if k:
                        specs[str(k)] = str(v)

    stock_raw = str(product.get("stockStatus")
                    or product.get("availability") or "").lower()
    stock_map = {
        "instock": "in_stock", "in stock": "in_stock", "in_stock": "in_stock",
        "outofstock": "out_of_stock", "out of stock": "out_of_stock", "out_of_stock": "out_of_stock",
    }
    stock_status = stock_map.get(stock_raw, "unknown")

    return {
        "title": title,
        "brand": str(product.get("brand") or product.get("Brand") or product.get("manufacturer") or ""),
        "description": description,
        "price": price,
        "price_currency": "ILS",
        "stock_status": stock_status,
        "sku": sku,
        "image_url": image_url,
        "specs": specs,
        "features": [],
        "_source": "__NEXT_DATA__",
    }


# ═══════════════════════════════════════════════════════════════════════════
# HTML → MARKDOWN CONVERTER
# ═══════════════════════════════════════════════════════════════════════════

def html_to_markdown(html: str, max_chars: int = 15000) -> str:
    """
    Convert HTML to plain readable text suitable for LLM consumption.
    Strips scripts, styles, and nav noise. Converts tables to text.
    Truncates to max_chars to stay within Gemini context limits.
    """
    # Remove script/style/nav/header/footer noise
    html = re.sub(r"<(script|style|nav|header|footer|noscript)[^>]*>.*?</\1>",
                  " ", html, flags=re.DOTALL | re.IGNORECASE)
    # Convert table cells to pipe-delimited text
    html = re.sub(r"<th[^>]*>", " | ", html, flags=re.IGNORECASE)
    html = re.sub(r"<td[^>]*>", " | ", html, flags=re.IGNORECASE)
    html = re.sub(r"</tr>", "\n", html, flags=re.IGNORECASE)
    # Convert breaks and block elements to newlines
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</(p|div|li|h[1-6]|section|article)>",
                  "\n", html, flags=re.IGNORECASE)
    # Strip remaining tags
    text = re.sub(r"<[^>]+>", " ", html)
    # Decode HTML entities
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace(
        "&gt;", ">").replace("&nbsp;", " ").replace("&#x27;", "'")
    # Collapse whitespace
    text = re.sub(r" +", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:max_chars]


# ═══════════════════════════════════════════════════════════════════════════
# GEMINI LLM EXTRACTOR
# ═══════════════════════════════════════════════════════════════════════════

def _build_gemini_client():
    """Initialize Gemini client using project key management."""
    try:
        from backend.env_secrets import get_gemini_api_key
        api_key = get_gemini_api_key()
    except ImportError:
        api_key = os.environ.get(
            "GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No Gemini API key found. Set GEMINI_API_KEY env var.")
    from google import genai
    return genai.Client(api_key=api_key)


def extract_with_gemini(
    page_text: str,
    model: str = "gemini-2.0-flash",
) -> Optional[Dict[str, Any]]:
    """
    Pass rendered page Markdown to Gemini with a strict Structured Output schema.
    Returns a normalized product dict or None if extraction fails.

    This is the LLM Semantic Fallback — immune to CSS class changes.
    """
    try:
        from google import genai
        from google.genai import types

        client = _build_gemini_client()
        prompt = _EXTRACTION_PROMPT_TEMPLATE.format(page_text=page_text)

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=_PRODUCT_SCHEMA,
                temperature=0.0,  # Deterministic extraction
            ),
        )
        raw_json = response.text or ""
        data = json.loads(raw_json)
        data["_source"] = "gemini_semantic"
        logger.info(
            "[GEMINI] Extracted: title=%r price=%s sku=%r specs=%d keys",
            data.get("title", "")[:60],
            data.get("price"),
            data.get("sku", ""),
            len(data.get("specs", {})),
        )
        return data
    except json.JSONDecodeError as exc:
        logger.warning("[GEMINI] JSON parse error: %s", exc)
    except Exception as exc:
        logger.warning("[GEMINI] Extraction failed: %s", exc)
    return None


# ═══════════════════════════════════════════════════════════════════════════
# MAIN SEMANTIC EXTRACTOR CLASS
# ═══════════════════════════════════════════════════════════════════════════

class SemanticExtractor:
    """
    Resilient product data extractor:
      1. API Sniffer (Ghost Protocol): __NEXT_DATA__, Shopify, WooCommerce
      2. LLM Semantic Fallback: Gemini Structured Outputs on Markdown text
      3. Graceful degradation: dead-letter queue on failure
    """

    def __init__(self, request_timeout: int = 15):
        self.timeout = request_timeout
        self._session = requests.Session()
        self._session.headers.update(_HEADERS)

    # ── Stage 1: API Sniffer ─────────────────────────────────────────────

    def api_first_extract(self, url: str, html: Optional[str] = None) -> Optional[Dict]:
        """
        Attempt to extract product data from hidden JSON APIs before parsing HTML.

        Order of attempts:
          1. __NEXT_DATA__ JSON blob (embedded in HTML, no extra HTTP request)
          2. Shopify product JSON endpoint
          3. WooCommerce REST API v3/v2

        Returns a normalized product dict with `_source` field, or None.
        """
        # If we already have HTML, try __NEXT_DATA__ first (free)
        if html:
            result = _sniff_next_data(html)
            if result:
                return result

        # Probe Shopify endpoint
        result = _sniff_shopify_json(url, self._session, self.timeout)
        if result:
            return result

        # Probe WooCommerce endpoint
        result = _sniff_woocommerce_json(url, self._session, self.timeout)
        if result:
            return result

        return None

    # ── Stage 2: LLM Semantic Fallback ───────────────────────────────────

    def semantic_extract(
        self,
        html: str,
        url: str = "",
        model: str = "gemini-2.0-flash",
    ) -> Optional[Dict]:
        """
        Convert HTML to Markdown and use Gemini Structured Output to extract
        product data. Immune to CSS class / DOM structure changes.

        Logs to DLQ if Gemini extraction fails.
        """
        try:
            markdown = html_to_markdown(html)
            if len(markdown) < 100:
                _write_dlq(url, "Page text too short for semantic extraction",
                           {"text_length": len(markdown)})
                return None
            result = extract_with_gemini(markdown, model=model)
            if not result:
                _write_dlq(url, "Gemini returned no data")
            return result
        except Exception as exc:
            _write_dlq(url, f"Semantic extraction exception: {exc}")
            return None

    # ── Combined Pipeline ────────────────────────────────────────────────

    def extract(
        self,
        url: str,
        html: Optional[str] = None,
        fetch_if_needed: bool = True,
        model: str = "gemini-2.0-flash",
    ) -> Optional[Dict]:
        """
        Full extraction pipeline:
          1. Fetch HTML if not provided
          2. Try API-first (Ghost Protocol)
          3. Fall back to Gemini Semantic Extraction
          4. On total failure: log to DLQ, return None (caller uses cached data)

        Args:
            url: Product page URL
            html: Pre-fetched HTML (from Playwright or httpx) — avoids extra request
            fetch_if_needed: If True and html is None, fetch via requests
            model: Gemini model to use for fallback

        Returns:
            Normalized product dict or None (graceful degradation).
        """
        # Fetch HTML if not supplied
        if html is None and fetch_if_needed:
            try:
                resp = self._session.get(url, timeout=self.timeout)
                if resp.status_code == 404:
                    _write_dlq(url, "HTTP 404")
                    return None
                if resp.status_code >= 400:
                    _write_dlq(url, f"HTTP {resp.status_code}")
                    return None
                html = resp.text
            except requests.exceptions.Timeout:
                _write_dlq(url, "Request timeout")
                return None
            except requests.exceptions.ConnectionError as exc:
                _write_dlq(url, f"Connection error: {exc}")
                return None
            except Exception as exc:
                _write_dlq(url, f"Fetch error: {exc}")
                return None

        if not html:
            _write_dlq(url, "No HTML available and fetch disabled")
            return None

        # Stage 1: API Sniffer
        result = self.api_first_extract(url, html=html)
        if result:
            return result

        # Stage 2: LLM Semantic Fallback
        return self.semantic_extract(html, url=url, model=model)

    def close(self) -> None:
        """Close the underlying requests session."""
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

_default_extractor: Optional[SemanticExtractor] = None


def get_extractor() -> SemanticExtractor:
    """Return the module-level singleton SemanticExtractor."""
    global _default_extractor
    if _default_extractor is None:
        _default_extractor = SemanticExtractor()
    return _default_extractor


def sniff_next_data(html: str) -> Optional[Dict]:
    """Convenience: extract __NEXT_DATA__ from an HTML string."""
    return _sniff_next_data(html)


def semantic_extract_url(url: str, html: Optional[str] = None) -> Optional[Dict]:
    """Convenience: full pipeline for a single URL."""
    return get_extractor().extract(url, html=html)
