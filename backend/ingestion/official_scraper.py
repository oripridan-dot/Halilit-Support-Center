"""
Official (Brand) Page Scraper — JIT Phase 1

Fetches a candidate official product page and extracts:
  - og:image, og:description
  - Specs from tables/lists (simple heuristics)

Used by jit_agent for the Auditor (visual verification) and merge step.
"""

import logging
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
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if resp.status_code != 200:
            return result
        html = resp.text
        result["raw_text"] = html[:50000]  # cap for verify_integrity

        # og:image
        m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
        if m:
            result["image_url"] = m.group(1).strip()

        # og:description
        m = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']*)["\']', html, re.I)
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


def find_official_product_url(brand: str, product_name: str) -> Optional[str]:
    """
    Suggest a candidate official product page URL.
    Uses brand domain + product name slug. Does not use Google Search.
    Returns None if no domain or if we don't want to guess.
    """
    brand_lower = brand.lower().strip().replace(" ", " ")
    domain = None
    for key, d in BRAND_DOMAINS.items():
        if key in brand_lower or brand_lower in key:
            domain = d
            break
    if not domain:
        domain = brand_lower.replace(" ", "") + ".com"

    # Simple slug from product name (alphanumeric and dash)
    slug = re.sub(r"[^a-z0-9\s-]", "", product_name.lower())
    slug = re.sub(r"\s+", "-", slug).strip("-")[:60]

    # Common paths (many brand sites use /products/... or /.../product-name)
    candidates = [
        f"https://{domain}/products/{slug}",
        f"https://www.{domain}/products/{slug}",
        f"https://{domain}/{slug}",
    ]
    for url in candidates:
        try:
            resp = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=True)
            if resp.status_code == 200:
                return resp.url
        except Exception:
            continue
    return None
