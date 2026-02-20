"""
Official (Brand) Page Scraper — JIT Phase 1

Fetches a candidate official product page and extracts:
  - og:image, og:description
  - Specs from tables/lists (simple heuristics)

Used by jit_agent for the Auditor (visual verification) and merge step.
URL discovery chain:
  1. BRAND_DOMAINS slug lookup (fast, no API)
  2. Gemini-powered URL suggestion (fallback, uses AI knowledge to find page)
"""

import logging
import os
import re
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger("OfficialScraper")

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
    Fetch a single URL and extract og:image, og:description, and simple specs.
    Returns dict: url, image_url, description, specs (flat key/value), raw_text (for verify_integrity).
    """
    result: Dict[str, Any] = {
        "url": url,
        "image_url": "",
        "description": "",
        "specs": {},
        "raw_text": "",
    }
    try:
        resp = requests.get(url, headers=HEADERS,
                            timeout=timeout, allow_redirects=True)
        if resp.status_code == 404:
            return result  # Truly missing page — skip
        html = resp.text
        result["raw_text"] = html[:50000]  # cap for verify_integrity

        # og:image
        m = re.search(
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
        if m:
            result["image_url"] = m.group(1).strip()

        # og:description
        m = re.search(
            r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']*)["\']', html, re.I)
        if m:
            result["description"] = m.group(1).strip()

        # Simple spec table: <td>key</td><td>value</td> or dt/dd
        for pattern in [
            r"<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>",
            r"<dt[^>]*>([^<]+)</dt>\s*<dd[^>]*>([^<]+)</dd>",
        ]:
            for m in re.finditer(pattern, html, re.I | re.DOTALL):
                k = re.sub(r"\s+", " ", m.group(1)).strip()
                v = re.sub(r"\s+", " ", m.group(2)).strip()
                if len(k) < 50 and len(v) < 200 and k and v:
                    result["specs"][k] = v

        return result
    except Exception as e:
        logger.debug("fetch_official_page %s: %s", url, e)
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
