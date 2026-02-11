"""
OFFICIAL BRAND PAGE SCRAPER v1.0

Finds and extracts product data from OFFICIAL manufacturer websites.

The flow:
1. Given a product name + brand, construct search URL for the brand's official site
2. Scrape the official product page for specs, descriptions, images
3. Return structured data that is clearly sourced from the official brand

This is the "Official Knowledge" layer — separate from Halilit commercial data.

Supported brands have their official site URL patterns defined below.
For unknown brands, falls back to Google search.

Usage:
    scraper = OfficialBrandScraper()
    data = scraper.scrape_official("ADAM Audio T5V", "ADAM Audio")
"""

import json
import logging
import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("OfficialBrandScraper")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
REQUEST_TIMEOUT = 12
RATE_LIMIT_DELAY = 0.5


# ═══════════════════════════════════════════════════════════════════════════
# BRAND OFFICIAL SITE REGISTRY
# ═══════════════════════════════════════════════════════════════════════════

# Maps brand → (base_url, product_search_pattern, product_page_selectors)
BRAND_SITES: Dict[str, Dict[str, Any]] = {
    "adam audio": {
        "base_url": "https://www.adam-audio.com",
        "search_url": "https://www.adam-audio.com/en/?s={query}",
        "product_url_pattern": "/en/products/{model_lower}/",
        "selectors": {
            "description": ".product-description, .entry-content, .product-text",
            "specs": ".specifications, .tech-specs, table",
            "images": ".product-image img, .gallery img",
        },
    },
    "roland": {
        "base_url": "https://www.roland.com",
        "search_url": "https://www.roland.com/global/search/?q={query}",
        "product_url_pattern": "/global/products/{model_lower}/",
        "selectors": {
            "description": ".product-description, .mainCopy",
            "specs": ".specTable, .specifications table",
            "images": ".product-hero img, .gallery-image img",
        },
    },
    "moog": {
        "base_url": "https://www.moogmusic.com",
        "search_url": "https://www.moogmusic.com/search?keys={query}",
        "product_url_pattern": "/products/{model_lower}",
        "selectors": {
            "description": ".field--name-body, .product-description",
            "specs": ".field--name-field-specifications, table",
            "images": ".product-image img, .gallery img",
        },
    },
    "nord": {
        "base_url": "https://www.nordkeyboards.com",
        "product_url_pattern": "/products/{model_lower}/",
        "selectors": {
            "description": ".product-page__intro, .product-description",
            "specs": ".specifications, .tech-specs",
            "images": ".product-image img",
        },
    },
    "rode": {
        "base_url": "https://www.rode.com",
        "product_url_pattern": "/microphones/{model_lower}",
        "selectors": {
            "description": ".product-description, .product-intro",
            "specs": ".specifications table, .tech-specs",
            "images": ".product-hero img, .product-gallery img",
        },
    },
    "shure": {
        "base_url": "https://www.shure.com",
        "product_url_pattern": "/en-US/products/{model_lower}",
        "selectors": {
            "description": ".product-description, [class*='description']",
            "specs": ".specifications, [class*='spec']",
            "images": ".product-image img",
        },
    },
    "universal audio": {
        "base_url": "https://www.uaudio.com",
        "product_url_pattern": "/hardware/{model_lower}",
        "selectors": {
            "description": ".product-description",
            "specs": ".specifications, .tech-specs",
            "images": ".product-image img",
        },
    },
    "arturia": {
        "base_url": "https://www.arturia.com",
        "product_url_pattern": "/products/{model_lower}/overview",
        "selectors": {
            "description": ".product-description, .text-block",
            "specs": ".specifications",
            "images": ".product-image img",
        },
    },
    "akai": {
        "base_url": "https://www.akaipro.com",
        "product_url_pattern": "/products/{model_lower}",
        "selectors": {
            "description": ".product-description",
            "specs": ".specifications",
            "images": ".product-image img",
        },
    },
    "mackie": {
        "base_url": "https://mackie.com",
        "product_url_pattern": "/products/{model_lower}",
        "selectors": {
            "description": ".product-description",
            "specs": ".specifications, .tech-specs",
            "images": ".product-image img",
        },
    },
    "focusrite": {
        "base_url": "https://focusrite.com",
        "product_url_pattern": "/products/{model_lower}",
        "selectors": {
            "description": ".product-description",
            "specs": ".specifications",
            "images": ".product-image img",
        },
    },
    "presonus": {
        "base_url": "https://www.presonus.com",
        "product_url_pattern": "/products/{model_lower}/",
        "selectors": {
            "description": ".body-text, .product-description",
            "specs": ".specifications",
            "images": ".product-image img",
        },
    },
}

# Aliases for brands with different names
BRAND_ALIASES = {
    "akai professional": "akai",
    "adam-audio": "adam audio",
    "ua": "universal audio",
    "boss": "roland",  # Boss is a Roland subsidiary
}


class OfficialBrandScraper:
    """
    Scrapes official manufacturer product pages for specs, descriptions, images.

    Strategy:
    1. Check if brand has a known site pattern
    2. Try direct URL construction (fastest)
    3. Fall back to site search
    4. Fall back to generic web search
    5. Extract structured data from the page
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self._last_request_time = 0

    def _rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.time()

    def _get(self, url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[requests.Response]:
        self._rate_limit()
        try:
            resp = self.session.get(url, timeout=timeout, allow_redirects=True)
            if resp.status_code == 200:
                return resp
            logger.debug(f"HTTP {resp.status_code} for {url}")
            return None
        except requests.RequestException as e:
            logger.debug(f"Request failed: {url} — {e}")
            return None

    def scrape_official(
        self,
        model_name: str,
        brand: str,
        product_name: str = "",
    ) -> Optional[Dict[str, Any]]:
        """
        Find and scrape the official product page for the given model.

        Args:
            model_name: English model name (e.g., "T5V", "Mavis")
            brand: Brand name (e.g., "ADAM Audio", "Moog")
            product_name: Full product name for context

        Returns:
            Dict with official_specs, official_description, official_images, official_url
            or None if page can't be found/scraped
        """
        if not model_name or not brand:
            return None

        brand_key = brand.lower().strip()
        brand_key = BRAND_ALIASES.get(brand_key, brand_key)

        site_config = BRAND_SITES.get(brand_key)
        if not site_config:
            logger.debug(f"No official site config for brand: {brand}")
            return None

        # Try direct URL construction
        page_url = self._try_direct_url(model_name, brand, site_config)

        # If direct URL fails, try search
        if not page_url and site_config.get("search_url"):
            page_url = self._try_site_search(model_name, site_config)

        if not page_url:
            logger.info(
                f"Could not find official page for {brand} {model_name}")
            return None

        # Scrape the official page
        return self._extract_official_data(page_url, site_config)

    def _try_direct_url(
        self,
        model_name: str,
        brand: str,
        config: Dict,
    ) -> Optional[str]:
        """Try constructing a direct URL to the product page."""
        pattern = config.get("product_url_pattern")
        if not pattern:
            return None

        # Generate model slug variations
        model_lower = model_name.lower().strip()
        model_slug = re.sub(r"[^a-z0-9]+", "-", model_lower).strip("-")

        # Try several URL patterns
        base = config["base_url"]
        candidates = [
            base + pattern.format(model_lower=model_slug),
            base + pattern.format(model_lower=model_lower.replace(" ", "-")),
            base + pattern.format(model_lower=model_lower.replace(" ", "")),
        ]

        for url in candidates:
            resp = self._get(url)
            if resp and len(resp.text) > 1000:
                logger.info(f"  Found official page: {url}")
                return url

        return None

    def _try_site_search(
        self,
        model_name: str,
        config: Dict,
    ) -> Optional[str]:
        """Try finding the product via the brand's site search."""
        search_url = config.get("search_url")
        if not search_url:
            return None

        url = search_url.format(query=quote(model_name))
        resp = self._get(url)
        if not resp:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # Look for product links in search results
        base = config["base_url"]
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True).lower()

            # Check if link text contains model name
            if model_name.lower() in text:
                full_url = href if href.startswith(
                    "http") else urljoin(base, href)
                if "/product" in full_url.lower():
                    return full_url

        return None

    def _extract_official_data(
        self,
        url: str,
        config: Dict,
    ) -> Optional[Dict[str, Any]]:
        """Extract structured data from an official product page."""
        resp = self._get(url)
        if not resp:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        selectors = config.get("selectors", {})

        # Extract description
        description = ""
        for sel in selectors.get("description", "").split(","):
            sel = sel.strip()
            if sel:
                el = soup.select_one(sel)
                if el:
                    text = el.get_text(strip=True)
                    if len(text) > len(description):
                        description = text

        # Extract specs from tables
        specs = {}
        for sel in selectors.get("specs", "").split(","):
            sel = sel.strip()
            if sel:
                for el in soup.select(sel):
                    specs.update(self._parse_spec_table(el))

        # Extract JSON-LD specs if available
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") == "Product":
                        if item.get("description") and not description:
                            description = item["description"]
                        for prop in item.get("additionalProperty", []):
                            name = prop.get("name", "")
                            value = prop.get("value", "")
                            if name and value:
                                specs[name] = value
            except (json.JSONDecodeError, TypeError):
                continue

        # Extract images
        images = []
        seen = set()
        for sel in selectors.get("images", "").split(","):
            sel = sel.strip()
            if sel:
                for img in soup.select(sel):
                    src = img.get("src") or img.get("data-src") or ""
                    if src and src not in seen and src.startswith("http"):
                        images.append(src)
                        seen.add(src)

        # OG image as fallback
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            img_url = og_img["content"]
            if img_url not in seen:
                images.insert(0, img_url)

        if not description and not specs and not images:
            return None

        # Extract meta description as fallback
        if not description:
            meta = soup.find("meta", attrs={"name": "description"})
            if meta:
                description = meta.get("content", "")

        return {
            "official_url": url,
            "official_description": description,
            "official_specs": specs if specs else {},
            "official_images": [
                {
                    "url": img,
                    "type": "image",
                    "display_purpose": "hero" if i == 0 else "gallery",
                    "source": "official_brand_page",
                    "priority": 100 - i * 10,
                }
                for i, img in enumerate(images[:10])
            ],
            "official_features": [],
            "source_confidence": "official",
        }

    def _parse_spec_table(self, element) -> Dict[str, str]:
        """Parse a spec table or definition list into key-value pairs."""
        specs = {}

        # Try table rows
        for row in element.select("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                val = cells[1].get_text(strip=True)
                if key and val:
                    specs[key] = val

        # Try definition lists
        dts = element.find_all("dt")
        dds = element.find_all("dd")
        for dt, dd in zip(dts, dds):
            key = dt.get_text(strip=True)
            val = dd.get_text(strip=True)
            if key and val:
                specs[key] = val

        # Try labeled spans/divs
        for label in element.select(".spec-label, .label, .key"):
            value_el = label.find_next_sibling()
            if value_el:
                key = label.get_text(strip=True)
                val = value_el.get_text(strip=True)
                if key and val:
                    specs[key] = val

        return specs


def enrich_product_with_official(
    product: Dict[str, Any],
    scraper: Optional[OfficialBrandScraper] = None,
) -> Dict[str, Any]:
    """
    Enrich a product dict with data from the official brand page.

    Only updates if higher-quality data is found.
    Never overwrites Halilit commercial data (price, halilit_id, etc.)
    """
    brand = product.get("brand", "")
    model_name = product.get(
        "official_name") or product.get("model_number") or ""

    if not model_name:
        # Try to extract from product name
        from backend.ingestion.halilit_page_scraper import extract_model_name
        full_name = product.get("product_name", "")
        model_name = extract_model_name(full_name, brand)

    if not model_name or not brand:
        return product

    if scraper is None:
        scraper = OfficialBrandScraper()

    official_data = scraper.scrape_official(model_name, brand)
    if not official_data:
        return product

    # Merge: official data fills gaps, improves quality

    # Description: prefer official over Halilit's
    if official_data.get("official_description"):
        current = product.get("official_description", "")
        if not current or len(official_data["official_description"]) > len(current):
            product["official_description"] = official_data["official_description"]

    # Specs: merge official into existing
    if official_data.get("official_specs"):
        current_specs = product.get("official_specs", {})
        # Remove placeholder specs
        if isinstance(current_specs, dict) and set(current_specs.keys()) <= {"note", "extracted_name"}:
            current_specs = {}
        current_specs.update(official_data["official_specs"])
        product["official_specs"] = current_specs

    # Images: official images take priority
    if official_data.get("official_images"):
        existing = product.get("official_images", [])
        # Prepend official images (they're higher quality)
        official_urls = {img.get("url")
                         for img in official_data["official_images"]}
        non_duplicate = [
            img for img in existing
            if (img.get("url") if isinstance(img, dict) else img) not in official_urls
        ]
        product["official_images"] = official_data["official_images"] + non_duplicate

    # Official URL
    if official_data.get("official_url"):
        product["official_url"] = official_data["official_url"]

    return product
