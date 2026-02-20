"""
Official (Brand) Page Scraper — JIT Phase 1  [Resilient v2]

Fetches a candidate official product page and extracts:
  - og:image, og:description  (stable meta tags — kept from v1)
  - Specs via Gemini Semantic Extraction (replaces brittle CSS/regex heuristics)
  - __NEXT_DATA__ probe for Next.js brand sites

Used by jit_agent for the Auditor (visual verification) and merge step.
URL discovery chain:
  1. BRAND_DOMAINS slug lookup (fast, no API)
  2. Gemini-powered URL suggestion (fallback, uses AI knowledge to find page)

Resilience model (spec: specs/data_pipeline/03_resilient_ingestion.md):
  - No soup.find() or hardcoded CSS selectors for spec extraction
  - Gemini Structured Output is the primary spec extractor
  - Failures are logged to the dead-letter queue
"""

import logging
import os
import re
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger("OfficialScraper")

# Resilient semantic extraction (per spec 03_resilient_ingestion.md)
try:
    from backend.ingestion.semantic_extractor import (
        sniff_next_data,
        html_to_markdown,
        extract_with_gemini,
        _write_dlq,
    )
    _SEMANTIC_AVAILABLE = True
except ImportError:
    _SEMANTIC_AVAILABLE = False
    def sniff_next_data(html): return None  # noqa: E704
    def html_to_markdown(html, **kw): return ""  # noqa: E704
    def extract_with_gemini(text, **kw): return None  # noqa: E704
    def _write_dlq(url, reason, ctx=None): pass  # noqa: E704

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; HalilitSupport/1.0; +https://halilit.com)",
    "Accept-Language": "en-US,en;q=0.9",
}

# Brand domain hints for discovering official URLs (same as jit_agent.read_brand_page)
BRAND_DOMAINS: Dict[str, str] = {
    "roland": "roland.com",
    "yamaha": "yamaha.com",
    "nord": "nordkeyboards.com",
    "clavia": "nordkeyboards.com",
    "korg": "korg.com",
    "casio": "casio.com",
    "boss": "boss.info",
    "fender": "fender.com",
    "gibson": "gibson.com",
    "shure": "shure.com",
    "sennheiser": "sennheiser.com",
    "focusrite": "focusrite.com",
    "native instruments": "native-instruments.com",
    "arturia": "arturia.com",
    "moog": "moogmusic.com",
    "adam audio": "adam-audio.com",
    "genelec": "genelec.com",
    "krk": "krk.com",
    "marshall": "marshall.com",
    "orange": "orangeamps.com",
    "behringer": "behringer.com",
    "presonus": "presonus.com",
    "universal audio": "uaudio.com",
    "steinberg": "steinberg.net",
    "novation": "novationmusic.com",
    "akai": "akaipro.com",
}


def fetch_official_page(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Fetch a single URL and extract og:image, og:description, and specs.

    Returns dict: url, image_url, description, specs (flat key/value),
                  raw_text, stock_status, sku.

    Extraction strategy (spec 03_resilient_ingestion.md):
      1. __NEXT_DATA__ probe — free, no API call, covers Next.js brand sites
      2. Gemini Semantic Extraction — pass rendered page Markdown to Gemini
         Structured Output; immune to CSS class / DOM restructures
      3. og:meta tags (regex on raw HTML) — always fast, universally stable
      4. Graceful degradation: failures write to dead-letter queue
    """
    result: Dict[str, Any] = {
        "url": url,
        "image_url": "",
        "description": "",
        "specs": {},
        "raw_text": "",
        "stock_status": "unknown",
        "sku": "",
    }
    try:
        resp = requests.get(url, headers=HEADERS,
                            timeout=timeout, allow_redirects=True)
        if resp.status_code == 404:
            _write_dlq(url, "HTTP 404 on official page")
            return result
        if resp.status_code >= 400:
            _write_dlq(url, f"HTTP {resp.status_code} on official page")
            return result
        html = resp.text
        result["raw_text"] = html[:50000]  # cap for verify_integrity

        # ── Stage 1: __NEXT_DATA__ probe (free) ───────────────────────────
        if _SEMANTIC_AVAILABLE:
            nd = sniff_next_data(html)
            if nd:
                logger.info("[API-FIRST] __NEXT_DATA__ found on official page: %s", url)
                if nd.get("image_url"):
                    result["image_url"] = nd["image_url"]
                if nd.get("description"):
                    result["description"] = nd["description"]
                if nd.get("specs"):
                    result["specs"] = nd["specs"]
                if nd.get("stock_status"):
                    result["stock_status"] = nd["stock_status"]
                if nd.get("sku"):
                    result["sku"] = nd["sku"]
                # Still fall through to og:image if missing
                if result["image_url"] and result["description"]:
                    return result

        # ── og:image (stable meta tag — kept from v1) ─────────────────────
        m = re.search(
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
        if m:
            result["image_url"] = m.group(1).strip()

        # ── og:description (stable meta tag — kept from v1) ───────────────
        if not result["description"]:
            m = re.search(
                r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']*)["\']', html, re.I)
            if m:
                result["description"] = m.group(1).strip()

        # ── Stage 2: Gemini Semantic Extraction for specs ─────────────────
        # Replace brittle table/dt regex with LLM-powered extraction.
        # Gemini reads the page meaning — not the CSS structure.
        if _SEMANTIC_AVAILABLE and not result["specs"]:
            markdown = html_to_markdown(html)
            if len(markdown) > 100:
                semantic = extract_with_gemini(markdown)
                if semantic:
                    if semantic.get("specs"):
                        result["specs"] = semantic["specs"]
                    if not result["description"] and semantic.get("description"):
                        result["description"] = semantic["description"]
                    if not result["image_url"] and semantic.get("image_url"):
                        result["image_url"] = semantic["image_url"]
                    if semantic.get("stock_status") and semantic["stock_status"] != "unknown":
                        result["stock_status"] = semantic["stock_status"]
                    if semantic.get("sku"):
                        result["sku"] = semantic["sku"]
                    logger.info(
                        "[SEMANTIC] Official page %s — extracted %d specs via Gemini",
                        url, len(result["specs"]),
                    )
                else:
                    _write_dlq(url, "Gemini returned no data for official page")

        return result
    except requests.exceptions.Timeout:
        _write_dlq(url, "Timeout fetching official page")
    except requests.exceptions.ConnectionError as exc:
        _write_dlq(url, f"Connection error fetching official page: {exc}")
    except Exception as e:
        logger.debug("fetch_official_page %s: %s", url, e)
        _write_dlq(url, f"fetch_official_page exception: {e}")
    return result


def _find_url_with_gemini(brand: str, product_name: str) -> Optional[str]:
    """
    Use Gemini's world-knowledge to find the official product page URL.
    Gemini is used purely as a NAVIGATOR (finding the URL), not as a spec generator.
    The returned URL is always verified with a HEAD request before returning.
    """
    try:
        from backend.env_secrets import get_gemini_api_key
        api_key = get_gemini_api_key()
        if not api_key:
            return None
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = (
            f"What is the exact official product page URL for '{product_name}' by {brand}? "
            "Reply with ONLY the URL (no extra text). If you don't know the exact URL, "
            "reply with the brand's main product listing URL (e.g. https://brand.com/products). "
            "Do not invent or guess URLs you are not confident about."
        )
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
        )
        raw = (response.text or "").strip()
        # Extract first http(s) URL from response
        m = re.search(r'https?://[^\s\'"<>]+', raw)
        if not m:
            return None
        candidate = m.group(0).rstrip(".,;)")
        logger.info("Gemini suggested official URL: %s", candidate)
        # Do a lightweight connectivity check — accept any non-404 response
        try:
            resp = requests.head(candidate, headers=HEADERS,
                                 timeout=8, allow_redirects=True)
            if resp.status_code != 404:
                return resp.url
            # 404 = page doesn't exist; try without HEAD (some servers block HEAD)
            resp2 = requests.get(candidate, headers=HEADERS,
                                 timeout=8, stream=True)
            resp2.close()
            if resp2.status_code != 404:
                return resp2.url
        except Exception:
            # Network error is not a 404 — still return the candidate URL
            return candidate
    except Exception as e:
        logger.debug("Gemini URL finder: %s", e)
    return None


def find_official_product_url(brand: str, product_name: str) -> Optional[str]:
    """
    Discover the official product page URL using a two-stage approach:
      Stage 1 — Slug-based domain lookup (instant, no API)
      Stage 2 — Gemini-powered URL discovery (fallback for unknown brands)
    """
    brand_lower = brand.lower().strip()
    domain = None
    for key, d in BRAND_DOMAINS.items():
        if key in brand_lower or brand_lower in key:
            domain = d
            break

    # Stage 1: slug-based lookup for known brands
    if domain:
        slug = re.sub(r"[^a-z0-9\s-]", "", product_name.lower())
        slug = re.sub(r"\s+", "-", slug).strip("-")[:60]
        candidates = [
            f"https://{domain}/products/{slug}",
            f"https://www.{domain}/products/{slug}",
            f"https://{domain}/{slug}",
        ]
        for url in candidates:
            try:
                resp = requests.head(url, headers=HEADERS,
                                     timeout=5, allow_redirects=True)
                if resp.status_code == 200:
                    return resp.url
            except Exception:
                continue

    # Stage 2: Gemini-powered URL discovery (handles unknown brands, unusual slugs)
    return _find_url_with_gemini(brand, product_name)
