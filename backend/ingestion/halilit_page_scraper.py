"""
HALILIT PRODUCT PAGE SCRAPER v1.0

Extracts COMPLETE product data from individual Halilit.com product pages.

Each Halilit product page contains rich structured data (JSON-LD):
  - Product name (Hebrew + English)
  - Price (ILS)
  - SKU
  - Brand
  - Description
  - High-res images (gallery)
  - Features (additionalProperty)
  - FAQ
  - Audience info

This replaces the old approach of only scraping search result listings.
Now we scrape each product's INDIVIDUAL page for maximum data quality.

Usage:
    scraper = HalilitPageScraper()
    product_data = scraper.scrape_product_page("https://www.halilit.com/items/2276780-adam-audio-t5v")
    all_products = scraper.scrape_brand_catalog("adam audio")
"""

import json
import logging
import re
import time
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("HalilitPageScraper")

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

HALILIT_BASE = "https://www.halilit.com"
CDN_PREFIX = "https://d3m9l0v76dty0.cloudfront.net"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
}
REQUEST_TIMEOUT = 12
# Rate and concurrency from ingestion_config (sustainable defaults)
def _ingestion_settings():
    try:
        from backend.ingestion.ingestion_config import (
            RATE_LIMIT_DELAY as _R,
            MAX_WORKERS as _W,
            SCRAPE_BATCH_SIZE as _B,
            BATCH_DELAY_SECONDS as _D,
            MAX_PRODUCTS_PER_BRAND as _M,
        )
        return _R, _W, _B, _D, _M
    except Exception:
        return 0.5, 3, 40, 1.0, 0

_RATE, _WORKERS, _BATCH, _BATCH_DELAY, _MAX_PRODUCTS = _ingestion_settings()
RATE_LIMIT_DELAY = _RATE
MAX_WORKERS = _WORKERS
SCRAPE_BATCH_SIZE = _BATCH
BATCH_DELAY_SECONDS = _BATCH_DELAY
MAX_PRODUCTS_PER_BRAND = _MAX_PRODUCTS
MAX_SEARCH_PAGES = 50  # support brands with 500+ products
ITEMS_PER_PAGE = 25  # Halilit shows 25 items per search/brand page
BRANDS_PAGE_URL = f"{HALILIT_BASE}/pages/4367"  # "המותגים שלנו" page
BRAND_GROUP_PREFIX = f"{HALILIT_BASE}/g/5193"  # Brand group page pattern
MAX_SITEMAP_PAGES = 20  # Halilit sitemap has 20 sub-pages


# ═══════════════════════════════════════════════════════════════════════════
# MODEL NAME EXTRACTION — Extract English model from Hebrew product names
# ═══════════════════════════════════════════════════════════════════════════

# Common Hebrew prefixes that appear before model names
_HEBREW_PRODUCT_PREFIXES = [
    "סינתיסייזר", "סט תופים אלקטרוניים", "מוניטור אולפני",
    "אוזניות מקצועיות לאולפן", "אוזניות עם מיקרופון", "אוזניות",
    "מיקרופון", "מערכת שמע", "גיטרה חשמלית", "גיטרה אקוסטית",
    "גיטרה בס", "בס חשמלי", "פסנתר דיגיטלי", "פסנתר במה",
    "מגבר גיטרה", "מגבר בס", "קונטרולר מידי", "אפקט",
    "סאבוופר אולפני", "סאבוופר", "מוניטור", "מיקסר",
    "כרטיס קול", "ממשק שמע", "מכונת תופים", "פדל",
    "זוג מוניטורים", "מוניטור אולפני צד ימין", "מוניטור אולפני צד שמאל",
    "כבל", "מעמד", "נרתיק", "תיק",
]

# Sort by length (longest first) for greedy matching
_HEBREW_PRODUCT_PREFIXES.sort(key=len, reverse=True)


def extract_model_name(full_name: str, brand: str = "") -> str:
    """
    Extract the English model name from a Hebrew+English product name.

    Examples:
        "סינתיסייזר Moog Mavis" → "Moog Mavis"
        "מוניטור אולפני ADAM Audio T5V" → "ADAM Audio T5V"
        "Roland VAD716" → "Roland VAD716"
    """
    if not full_name:
        return ""

    # Try to find where English text starts
    # Look for first ASCII letter sequence (brand/model)
    match = re.search(r'[A-Za-z][\w\s\-\.\/]+', full_name)
    if match:
        english_part = match.group(0).strip()
        # Clean trailing whitespace artifacts
        english_part = re.sub(r'\s+', ' ', english_part).strip()
        return english_part

    return full_name.strip()


def extract_model_number(model_name: str, brand: str = "") -> str:
    """
    Extract just the model number from the model name.

    Examples:
        "ADAM Audio T5V" (brand="ADAM Audio") → "T5V"
        "Moog Mavis" (brand="Moog") → "Mavis"
        "Roland VAD716" (brand="Roland") → "VAD716"
    """
    if not model_name:
        return ""

    name = model_name.strip()

    # Remove brand name from the start
    if brand:
        brand_lower = brand.lower().strip()
        name_lower = name.lower()
        # Handle multi-word brand names
        for variant in [brand_lower, brand_lower.replace(" ", "-"), brand_lower.replace("-", " ")]:
            if name_lower.startswith(variant):
                name = name[len(variant):].strip()
                break
            # Also try with common suffixes removed
            for suffix in [" audio", " professional", " guitars", " instruments"]:
                if name_lower.startswith(variant.replace(suffix, "")):
                    name = name[len(variant.replace(suffix, "")):].strip()
                    break

    return name.strip(" -–—")


# ═══════════════════════════════════════════════════════════════════════════
# HALILIT PRODUCT PAGE SCRAPER
# ═══════════════════════════════════════════════════════════════════════════

class HalilitPageScraper:
    """
    Scrapes individual Halilit.com product pages for rich structured data.

    Two-phase approach:
    1. Scrape search results to get product URLs (listing)
    2. Scrape each product page to get full data (detail)
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self._last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.time()

    @staticmethod
    def _is_anti_bot_page(html: str) -> bool:
        """Detect Konimbo's anti-bot referrer check page (page_no_referer)."""
        return (len(html) < 2000
                and ("page_no_referer" in html or "limit_no_referer" in html))

    def _get(self, url: str, retries: int = 2) -> Optional[requests.Response]:
        """Make a rate-limited GET request with anti-bot detection and retry."""
        for attempt in range(retries + 1):
            self._rate_limit()
            try:
                resp = self.session.get(url, timeout=REQUEST_TIMEOUT)
                if resp.status_code != 200:
                    logger.warning(f"HTTP {resp.status_code} for {url}")
                    return None
                # Check for Konimbo anti-bot page
                if self._is_anti_bot_page(resp.text):
                    if attempt < retries:
                        wait = (attempt + 1) * 3  # 3s, 6s backoff
                        logger.debug(
                            f"Anti-bot detected for {url}, retry in {wait}s...")
                        time.sleep(wait)
                        continue
                    logger.debug(f"Anti-bot blocked: {url}")
                    return None
                return resp
            except requests.RequestException as e:
                logger.warning(f"Request failed for {url}: {e}")
                if attempt < retries:
                    time.sleep(2)
                    continue
                return None
        return None

    # ─── Phase 1: Search/Brand Results (Product Listing) ──────────────

    def _extract_total_results(self, soup: BeautifulSoup) -> int:
        """Extract total result count from Halilit search/brand page (Hebrew text 'תוצאות: NNN')."""
        text = soup.get_text()
        match = re.search(r'תוצאות:\s*(\d[\d,]*)', text)
        if match:
            return int(match.group(1).replace(',', ''))
        return 0

    def _extract_max_page(self, soup: BeautifulSoup) -> int:
        """Extract the last page number from pagination div."""
        pagination = soup.select_one('.pagination')
        if not pagination:
            return 1
        max_page = 1
        for link in pagination.find_all('a', href=True):
            page_match = re.search(r'page=(\d+)', link.get('href', ''))
            if page_match:
                pg = int(page_match.group(1))
                if pg > max_page:
                    max_page = pg
        return max_page

    def _parse_listing_page(
        self, soup: BeautifulSoup, brand: str, seen_urls: set
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Parse products from a search/brand listing page. Returns (items, new_count)."""
        items = soup.select(
            ".layout_list_item, .box, .item, .product_item, .product_box"
        )
        results = []
        new_count = 0
        for item in items:
            try:
                parsed = self._parse_listing_item(item, brand)
                if parsed and parsed["url"] and parsed["url"] not in seen_urls:
                    seen_urls.add(parsed["url"])
                    results.append(parsed)
                    new_count += 1
            except Exception as e:
                logger.debug(f"  Skip item parse error: {e}")
        return results, new_count

    def scrape_brand_listing(self, brand: str, brand_group_url: str = "") -> List[Dict[str, Any]]:
        """
        Scrape Halilit to get ALL product URLs for a brand.

        Strategy (ordered by reliability):
        1. Brand group page (/g/5193-Brand/...) — most accurate, no cross-brand noise
        2. Search results (/search?q=brand) — fallback if no group page

        Uses proper pagination: reads total result count, calculates expected
        pages, and iterates through ALL of them.

        Returns list of {url, name, price, image_url} dicts.
        """
        # Try brand group page first (more accurate than search)
        if brand_group_url:
            result = self._scrape_brand_group_listing(brand, brand_group_url)
            if result:
                return result

        # Fallback to search
        return self._scrape_search_listing(brand)

    def _scrape_brand_group_listing(self, brand: str, group_url: str) -> List[Dict[str, Any]]:
        """Scrape brand group page with full pagination."""
        all_items = []
        seen_urls = set()

        logger.info(f"  📋 Scraping brand group page: {group_url}")
        resp = self._get(group_url)
        if not resp:
            logger.warning(
                f"  Brand group page failed, falling back to search")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        total_results = self._extract_total_results(soup)
        max_page_from_dom = self._extract_max_page(soup)
        expected_pages = max(
            max_page_from_dom,
            (total_results + ITEMS_PER_PAGE -
             1) // ITEMS_PER_PAGE if total_results > 0 else 1
        )
        expected_pages = min(expected_pages, MAX_SEARCH_PAGES)

        logger.info(
            f"  📊 Brand group: {total_results} total products, {expected_pages} pages")

        # Parse page 1
        items, new_count = self._parse_listing_page(soup, brand, seen_urls)
        all_items.extend(items)
        logger.info(f"  Page 1: {new_count} new products")

        if new_count == 0:
            return all_items

        # Pages 2..N
        consecutive_empty = 0
        for page in range(2, expected_pages + 1):
            separator = "&" if "?" in group_url else "?"
            page_url = f"{group_url}{separator}page={page}"
            logger.info(
                f"  Scraping brand group page {page}/{expected_pages}: {page_url}")

            resp = self._get(page_url)
            if not resp:
                consecutive_empty += 1
                if consecutive_empty >= 2:
                    break
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            items, new_count = self._parse_listing_page(soup, brand, seen_urls)
            all_items.extend(items)
            logger.info(
                f"  Page {page}: {new_count} new products (total: {len(all_items)})")

            if new_count == 0:
                consecutive_empty += 1
                if consecutive_empty >= 2:
                    logger.info(f"  2 consecutive empty pages, stopping.")
                    break
            else:
                consecutive_empty = 0

        logger.info(
            f"  ✅ Brand group listing for {brand}: {len(all_items)} products (expected ~{total_results})")
        return all_items

    def _scrape_search_listing(self, brand: str) -> List[Dict[str, Any]]:
        """Scrape Halilit search results with full pagination."""
        from urllib.parse import quote
        encoded = quote(brand)
        all_items = []
        seen_urls = set()
        expected_pages = MAX_SEARCH_PAGES  # Will be refined after page 1

        for page in range(1, MAX_SEARCH_PAGES + 1):
            url = f"{HALILIT_BASE}/search?q={encoded}&page={page}"
            logger.info(f"  Scraping search page {page}: {url}")

            resp = self._get(url)
            if not resp:
                break

            soup = BeautifulSoup(resp.text, "html.parser")

            # On page 1, extract total results and calculate expected pages
            if page == 1:
                total_results = self._extract_total_results(soup)
                max_page_from_dom = self._extract_max_page(soup)
                if total_results > 0:
                    calculated_pages = (
                        total_results + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
                    expected_pages = min(
                        max(max_page_from_dom, calculated_pages), MAX_SEARCH_PAGES)
                else:
                    expected_pages = min(max_page_from_dom, MAX_SEARCH_PAGES)
                logger.info(
                    f"  📊 Search: {total_results} total results, {expected_pages} pages to scrape")

            items, new_count = self._parse_listing_page(soup, brand, seen_urls)
            all_items.extend(items)
            logger.info(
                f"  Page {page}/{expected_pages}: {new_count} new products (total: {len(all_items)})")

            if new_count == 0:
                break

            # Stop if we've exceeded expected pages
            if page >= expected_pages:
                logger.info(
                    f"  Reached expected page count ({expected_pages}), stopping.")
                break

        logger.info(
            f"  ✅ Search listing for {brand}: {len(all_items)} products")
        return all_items

    def _parse_listing_item(self, item, brand: str) -> Optional[Dict]:
        """Parse a single item from search results."""
        title_el = item.select_one(
            ".title, .product-title, h3, h4, .title_with_brand, .item-title"
        )
        if not title_el:
            return None

        name = title_el.get_text(strip=True)
        if not name:
            return None

        # Extract URL
        link_el = item.select_one("a")
        url = ""
        if link_el:
            href = link_el.get("href", "").strip()
            if href:
                # Clean any whitespace/newlines in href before constructing URL
                href = href.replace("\n", "").replace("\r", "").strip()
                url = href if href.startswith("http") else HALILIT_BASE + href
                # Collapse any spaces in the final URL
                url = url.replace(" ", "")

        # Extract price
        price = 0.0
        price_el = item.select_one(
            ".price, .price-new, .current-price, .price_value, .item_price"
        )
        if price_el:
            digits = "".join(c for c in price_el.get_text()
                             if c.isdigit() or c == ".")
            try:
                price = float(digits) if digits else 0.0
            except ValueError:
                price = 0.0

        # Extract image
        image_url = ""
        img_el = item.select_one("img")
        if img_el:
            image_url = img_el.get("data-src") or img_el.get("src") or ""
            if image_url.startswith("//"):
                image_url = "https:" + image_url
            elif image_url and not image_url.startswith("http"):
                image_url = HALILIT_BASE + image_url

        return {
            "name": name,
            "brand": brand,
            "url": url,
            "price": price,
            "image_url": image_url,
        }

    # ─── Phase 2: Product Page Scraping (Full Detail) ───────────────────

    def scrape_product_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single Halilit product page for complete data.

        Extracts from JSON-LD structured data:
        - name, description, brand, price, SKU
        - images (gallery)
        - features, FAQ, audience

        Returns a rich product dict or None if page can't be scraped.
        """
        if not url or not url.startswith("http"):
            return None

        resp = self._get(url)
        if not resp:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract all JSON-LD blocks
        jsonld_products = []
        jsonld_faq = None
        jsonld_webpage = None

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if "@graph" in data:
                    for item in data["@graph"]:
                        t = item.get("@type", "")
                        if t == "Product":
                            jsonld_products.append(item)
                        elif t == "FAQPage":
                            jsonld_faq = item
                        elif t == "WebPage":
                            jsonld_webpage = item
                elif data.get("@type") == "Product":
                    jsonld_products.append(data)
            except (json.JSONDecodeError, TypeError):
                continue

        if not jsonld_products:
            logger.warning(f"No JSON-LD Product found on {url}")
            return None

        # Merge data from all Product blocks (Halilit pages often have 2+)
        product = self._merge_jsonld_products(jsonld_products)

        # Extract gallery images from DOM
        gallery_images = self._extract_gallery_images(soup)

        # Extract description from webpage JSON-LD or meta
        page_description = ""
        if jsonld_webpage:
            page_description = jsonld_webpage.get("description", "")
        if not page_description:
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                page_description = meta_desc.get("content", "")

        # Extract FAQ
        faq_items = []
        if jsonld_faq:
            for q in jsonld_faq.get("mainEntity", []):
                faq_items.append({
                    "question": q.get("name", ""),
                    "answer": q.get("acceptedAnswer", {}).get("text", ""),
                })

        # Extract brand from DOM
        brand_el = soup.select_one(".item_brand")
        dom_brand = brand_el.get_text(strip=True) if brand_el else ""

        # Build final product data
        brand_name = product.get("brand_name") or dom_brand or ""
        full_name = product.get("name", "")
        model_name = extract_model_name(full_name, brand_name)
        model_number = extract_model_number(model_name, brand_name)

        # Compute stable ID from URL
        item_id_match = re.search(r"/items/(\d+)", url)
        halilit_id = item_id_match.group(
            1) if item_id_match else f"h-{hashlib.md5(url.encode()).hexdigest()[:10]}"

        # Merge gallery from JSON-LD images + DOM gallery
        all_images = []
        seen_img = set()
        for img_url in product.get("images", []) + gallery_images:
            if img_url and img_url not in seen_img and CDN_PREFIX in img_url:
                # Prefer large/original size
                normalized = self._normalize_image_url(img_url)
                if normalized not in seen_img:
                    all_images.append(normalized)
                    seen_img.add(normalized)

        # Features from additionalProperty
        features = product.get("features", [])

        # Audiences
        audiences = product.get("audiences", [])

        result = {
            "halilit_id": halilit_id,
            "product_name": full_name,
            "official_name": model_name,
            "model_number": model_number if model_number else product.get("sku"),
            "brand": brand_name,
            "sku": product.get("sku"),

            # Pricing (from Halilit — commercial source of truth)
            "price_il": product.get("price", 0.0),
            "price_eilat": round(product.get("price", 0.0) / 1.17, 2) if product.get("price", 0) > 0 else 0.0,

            # Description (from Halilit page)
            "description": product.get("description", ""),
            "page_description": page_description,

            # Images
            "image_url": all_images[0] if all_images else "",
            "image_gallery": all_images,
            "official_images": [
                {
                    "url": img,
                    "type": "image",
                    "display_purpose": "hero" if i == 0 else "gallery",
                    "source": "halilit_product_page",
                    "priority": 100 - i * 10,
                }
                for i, img in enumerate(all_images)
            ],

            # Features & Knowledge
            "features": features,
            "faq": faq_items,
            "audiences": audiences,

            # Source tracking
            "halilit_url": url,
            "source": "halilit_product_page",
        }

        return result

    def _merge_jsonld_products(self, products: List[Dict]) -> Dict:
        """Merge multiple JSON-LD Product blocks into one rich dict."""
        merged = {
            "name": "",
            "description": "",
            "brand_name": "",
            "price": 0.0,
            "sku": "",
            "images": [],
            "features": [],
            "audiences": [],
        }

        for p in products:
            # Name — prefer the one with English characters
            name = p.get("name", "")
            if name and (not merged["name"] or "|" not in name):
                merged["name"] = name.split("|")[0].strip()

            # Description
            desc = p.get("description", "")
            if desc and len(desc) > len(merged["description"]):
                merged["description"] = desc

            # Brand
            brand = p.get("brand", {})
            if isinstance(brand, dict) and brand.get("name"):
                merged["brand_name"] = brand["name"]

            # Price
            offers = p.get("offers", {})
            if isinstance(offers, dict):
                try:
                    price = float(offers.get("price", 0))
                    if price > 0 and (merged["price"] == 0 or price < merged["price"]):
                        merged["price"] = price
                except (ValueError, TypeError):
                    pass

            # SKU
            sku = p.get("sku", "")
            if sku and not merged["sku"]:
                merged["sku"] = sku

            # Images
            imgs = p.get("image", [])
            if isinstance(imgs, str):
                imgs = [imgs]
            for img in imgs:
                if img and img not in merged["images"]:
                    merged["images"].append(img)

            # Features (additionalProperty) — preserve name:value structure
            for prop in p.get("additionalProperty", []):
                name = (prop.get("name") or "").strip().rstrip("\t")
                val = (prop.get("value") or "").strip()
                if val:
                    merged["features"].append({"name": name, "value": val})

            # Audiences
            for aud in p.get("audience", []):
                aud_type = aud.get("audienceType", "")
                if aud_type and aud_type not in merged["audiences"]:
                    merged["audiences"].append(aud_type)

        return merged

    def _extract_gallery_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract product gallery images from DOM."""
        images = []
        gallery = soup.select_one(".item_gallery, .gallery, .product-gallery")
        if gallery:
            for img in gallery.find_all("img"):
                src = img.get("data-src") or img.get("src") or ""
                if src and CDN_PREFIX in src:
                    images.append(src)
        return images

    def _normalize_image_url(self, url: str) -> str:
        """Normalize image URL to use 'large' size (good balance of quality/speed)."""
        # Convert /medium/ or /original/ or /extra_large/ to /large/
        url = re.sub(r"/system/photos/(\d+)/(medium|original|extra_large|thumb)/",
                     r"/system/photos/\1/large/", url)
        # Remove query string timestamps
        url = re.sub(r"\?\d+$", "", url)
        return url

    # ─── Full Brand Scrape (Listing + Detail) ───────────────────────────

    def scrape_brand_full(
        self,
        brand: str,
        max_products: int = 0,
        skip_existing_urls: set = None,
        brand_group_url: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Full pipeline: scrape brand listing → scrape each product page.

        Uses brand group page for listing when available (more reliable),
        falls back to search. NO artificial product cap — scrapes ALL products.

        Args:
            brand: Brand name to search on Halilit
            max_products: Maximum products to scrape (0 = unlimited)
            skip_existing_urls: URLs to skip (already scraped)
            brand_group_url: Direct brand group page URL (preferred over search)

        Returns:
            List of fully enriched product dicts
        """
        skip_existing_urls = skip_existing_urls or set()

        logger.info(f"🛒 Starting full scrape for brand: {brand}")

        # Phase 1: Get product URLs from brand group page or search
        listings = self.scrape_brand_listing(
            brand, brand_group_url=brand_group_url)
        logger.info(f"  Found {len(listings)} products in listing")

        # Filter to products we haven't scraped yet
        to_scrape = [
            item for item in listings
            if item["url"] and item["url"] not in skip_existing_urls
        ]
        if max_products > 0:
            to_scrape = to_scrape[:max_products]

        if MAX_PRODUCTS_PER_BRAND > 0:
            to_scrape = to_scrape[:MAX_PRODUCTS_PER_BRAND]
            logger.info(f"  Capped at {len(to_scrape)} products (INGESTION_MAX_PRODUCTS)")

        logger.info(f"  Scraping {len(to_scrape)} product pages...")

        # Phase 2: Scrape each product page (with parallelism + inter-batch delay)
        products = []
        failed = 0
        batch_size = SCRAPE_BATCH_SIZE
        for batch_start in range(0, len(to_scrape), batch_size):
            if batch_start > 0 and BATCH_DELAY_SECONDS > 0:
                time.sleep(BATCH_DELAY_SECONDS)
            batch = to_scrape[batch_start:batch_start + batch_size]
            batch_num = batch_start // batch_size + 1
            total_batches = (len(to_scrape) + batch_size - 1) // batch_size

            if total_batches > 1:
                logger.info(
                    f"  📦 Batch {batch_num}/{total_batches} ({len(batch)} products)")

            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                future_to_listing = {
                    executor.submit(self._scrape_and_merge, item): item
                    for item in batch
                }
                for future in as_completed(future_to_listing):
                    listing = future_to_listing[future]
                    try:
                        result = future.result()
                        if result:
                            products.append(result)
                        else:
                            failed += 1
                    except Exception as e:
                        logger.warning(
                            f"  Failed to scrape {listing['url']}: {e}")
                        failed += 1

            # Progress file for monitoring (scrape phase)
            try:
                from backend.ingestion.ingestion_config import get_progress_dir
                prog = get_progress_dir() / f"{brand}.json"
                import json
                prog.write_text(json.dumps({
                    "brand": brand,
                    "phase": "scrape",
                    "batch_num": batch_num,
                    "total_batches": total_batches,
                    "scraped_so_far": len(products),
                    "failed_so_far": failed,
                }, indent=2))
            except Exception:
                pass

        logger.info(
            f"  ✅ Scraped {len(products)} products, {failed} failures"
        )
        return products

    def _scrape_and_merge(self, listing: Dict) -> Optional[Dict]:
        """Scrape a product page and merge with listing data."""
        page_data = self.scrape_product_page(listing["url"])

        if not page_data:
            # Fall back to listing data only
            return {
                "halilit_id": f"scraped-{hashlib.md5(listing['url'].encode()).hexdigest()[:10]}",
                "product_name": listing["name"],
                "brand": listing["brand"],
                "price_il": listing["price"],
                "price_eilat": round(listing["price"] / 1.17, 2) if listing["price"] > 0 else 0.0,
                "halilit_url": listing["url"],
                "image_url": listing.get("image_url", ""),
                "official_images": [
                    {"url": listing.get("image_url", ""), "type": "image",
                     "display_purpose": "hero", "source": "halilit_listing"}
                ] if listing.get("image_url") else [],
                "source": "halilit_listing_only",
            }

        # Merge: page data wins, but fill gaps from listing
        if not page_data.get("price_il") and listing.get("price"):
            page_data["price_il"] = listing["price"]
            page_data["price_eilat"] = round(listing["price"] / 1.17, 2)

        if not page_data.get("image_url") and listing.get("image_url"):
            page_data["image_url"] = listing["image_url"]

        return page_data

    # ─── Brand Discovery (Golden List Foundation) ───────────────────────

    def discover_all_brands(self) -> List[Dict[str, str]]:
        """
        Discover ALL brands from Halilit's official brands page (/pages/4367).

        Scrapes the "המותגים שלנו" (Our Brands) page which lists every brand
        with their group page URL. This is the AUTHORITATIVE source for what
        brands exist on Halilit.

        Returns list of {name, slug, group_url, brand_id} dicts.
        """
        from urllib.parse import unquote

        logger.info(f"🔍 Discovering all brands from {BRANDS_PAGE_URL}")

        resp = self._get(BRANDS_PAGE_URL)
        if not resp:
            logger.warning(
                "Failed to fetch brands page, falling back to sitemap")
            return self._discover_brands_from_sitemap()

        soup = BeautifulSoup(resp.text, "html.parser")
        brands = {}

        for a in soup.find_all('a', href=True):
            href = a.get('href', '').strip()
            # Match /g/5193-Brand/NNN-Name or /g/5193-יצרן/NNN-Name
            match = re.search(r'/g/5193[^/]*/(\d+)-(.+?)(?:\s|$)', href)
            if not match:
                continue

            brand_id = match.group(1)
            brand_slug = unquote(match.group(2)).replace('-', ' ').strip()

            # Build canonical URL
            clean_href = href.replace('\n', '').replace(
                '\r', '').replace(' ', '').strip()
            if clean_href.startswith('..'):
                clean_href = HALILIT_BASE + clean_href[2:]
            elif clean_href.startswith('/'):
                clean_href = HALILIT_BASE + clean_href
            elif 'konimbo.co.il' in clean_href:
                clean_href = clean_href.replace(
                    'http://halilit.konimbo.co.il', HALILIT_BASE
                ).replace(
                    'https://halilit.konimbo.co.il', HALILIT_BASE
                )

            # Use lowercase slug as dedup key
            key = brand_slug.lower()
            if key not in brands:
                brands[key] = {
                    "name": brand_slug,
                    "slug": key,
                    "group_url": clean_href,
                    "brand_id": brand_id,
                }

        result = sorted(brands.values(), key=lambda b: b["name"].lower())
        logger.info(
            f"✅ Discovered {len(result)} brands from Halilit brands page")
        return result

    def _discover_brands_from_sitemap(self) -> List[Dict[str, str]]:
        """
        Fallback brand discovery from sitemap product URLs.
        Scrapes sitemap pages and extracts unique brands from product page data.
        """
        from urllib.parse import unquote

        logger.info("🗺️ Discovering brands from sitemap (fallback)...")

        brands = set()
        for page in range(1, MAX_SITEMAP_PAGES + 1):
            url = f"{HALILIT_BASE}/sitemap.xml?page={page}"
            resp = self._get(url)
            if not resp:
                break

            # Extract product URLs from sitemap XML
            product_urls = re.findall(r'<loc>(.*?/items/.*?)</loc>', resp.text)
            if not product_urls:
                break

            # Sample a few products per page to discover brands
            sample = product_urls[:5]  # Just need a few to find brands
            for product_url in sample:
                try:
                    page_resp = self._get(product_url)
                    if page_resp:
                        page_soup = BeautifulSoup(
                            page_resp.text, "html.parser")
                        brand_el = page_soup.select_one('.item_brand')
                        if brand_el:
                            brand_name = brand_el.get_text(strip=True)
                            if brand_name:
                                brands.add(brand_name)
                except Exception:
                    continue

        result = [{"name": b, "slug": b.lower(), "group_url": "", "brand_id": ""}
                  for b in sorted(brands)]
        logger.info(f"🗺️ Discovered {len(result)} brands from sitemap")
        return result

    def scrape_all_product_urls_from_sitemap(self) -> List[str]:
        """
        Get ALL product URLs from Halilit's sitemap (all 20 pages).

        This is the most complete way to discover every product on Halilit.com.
        Returns list of product page URLs (/items/...).
        """
        all_product_urls = []

        logger.info(
            f"🗺️ Fetching all product URLs from sitemap ({MAX_SITEMAP_PAGES} pages)...")

        for page in range(1, MAX_SITEMAP_PAGES + 1):
            url = f"{HALILIT_BASE}/sitemap.xml?page={page}"
            resp = self._get(url)
            if not resp:
                logger.warning(f"  Sitemap page {page} failed")
                break

            product_urls = re.findall(r'<loc>(.*?/items/.*?)</loc>', resp.text)
            if not product_urls:
                logger.info(
                    f"  Sitemap page {page}: no product URLs, stopping")
                break

            all_product_urls.extend(product_urls)
            logger.info(
                f"  Sitemap page {page}: {len(product_urls)} products (total: {len(all_product_urls)})")

        logger.info(f"✅ Sitemap total: {len(all_product_urls)} product URLs")
        return all_product_urls

    def get_brand_product_count(self, brand: str, brand_group_url: str = "") -> int:
        """
        Quick check: how many products does a brand have on Halilit?
        Just reads page 1 and extracts the total result count.
        """
        from urllib.parse import quote

        if brand_group_url:
            url = brand_group_url
        else:
            url = f"{HALILIT_BASE}/search?q={quote(brand)}"

        resp = self._get(url)
        if not resp:
            return 0

        soup = BeautifulSoup(resp.text, "html.parser")
        return self._extract_total_results(soup)


# ═══════════════════════════════════════════════════════════════════════════
# ENRICHMENT UTILITY — Enrich existing products with page data
# ═══════════════════════════════════════════════════════════════════════════

def enrich_product_from_page(
    product: Dict[str, Any],
    scraper: Optional[HalilitPageScraper] = None,
) -> Dict[str, Any]:
    """
    Enrich an existing product dict by scraping its Halilit product page.

    Only updates fields that are missing or have placeholder values.
    Never overwrites valid commercial data (price, brand, name).

    Args:
        product: Existing product dict
        scraper: Optional scraper instance (creates one if needed)

    Returns:
        Enriched product dict (mutated in place)
    """
    url = product.get("halilit_url", "")

    # Skip if no real URL
    if not url or url == "https://halilit.com" or "/items/" not in url:
        return product

    if scraper is None:
        scraper = HalilitPageScraper()

    page_data = scraper.scrape_product_page(url)
    if not page_data:
        return product

    # ─── Merge Strategy: Fill gaps, never overwrite valid data ───

    # Price: update if missing
    if not product.get("price_il") and page_data.get("price_il"):
        product["price_il"] = page_data["price_il"]
        product["price_eilat"] = page_data.get("price_eilat", 0)

    # SKU: always useful
    if page_data.get("sku") and not product.get("sku"):
        product["sku"] = page_data["sku"]

    # Model number: extract English name
    if page_data.get("official_name"):
        product["official_name"] = page_data["official_name"]
    if page_data.get("model_number"):
        product["model_number"] = page_data["model_number"]

    # Description: update if missing or placeholder
    # NOTE: Halilit descriptions are COMMERCIAL data used for matching/display
    # until the OfficialBrandScraper replaces them with real official content.
    # We store them in description_commercial first, and only fall back to
    # official_description if it's truly empty (no official data yet).
    current_desc = product.get("official_description") or product.get(
        "description_short") or ""
    is_placeholder = (
        not current_desc
        or current_desc == "No description available."
        or "ultimate stage piano" in current_desc.lower()
    )
    if is_placeholder:
        if page_data.get("description"):
            product["description_commercial"] = page_data["description"]
            product["description_short"] = page_data["description"][:200]
            # Only set official_description if nothing better exists
            if not product.get("official_description"):
                product["official_description"] = page_data["description"]
        elif page_data.get("page_description"):
            product["description_commercial"] = page_data["page_description"]
            product["description_short"] = page_data["page_description"][:200]
            if not product.get("official_description"):
                product["official_description"] = page_data["page_description"]

    # Images: update if missing or placeholder
    current_img = product.get("image_url", "")
    is_placeholder_img = not current_img or "placeholder" in current_img.lower()

    if is_placeholder_img and page_data.get("image_url"):
        product["image_url"] = page_data["image_url"]

    if page_data.get("official_images"):
        # Replace placeholder images, keep real ones
        existing = product.get("official_images", [])
        if not existing or all(
            "placeholder" in (img.get("url", "") if isinstance(
                img, dict) else str(img)).lower()
            for img in existing
        ):
            product["official_images"] = page_data["official_images"]

    if page_data.get("image_gallery"):
        product["image_gallery"] = page_data["image_gallery"]

    # Features
    if page_data.get("features") and not product.get("feature_list"):
        product["feature_list"] = page_data["features"]

    # FAQ
    if page_data.get("faq"):
        product["faq"] = page_data["faq"]

    # Specs: update if only has the placeholder note
    current_specs = product.get("official_specs", {})
    is_placeholder_specs = (
        not current_specs
        or (isinstance(current_specs, dict) and
            set(current_specs.keys()) <= {"note", "extracted_name"})
    )
    if is_placeholder_specs and page_data.get("features"):
        # Build specs from features
        specs = {}
        for i, feat in enumerate(page_data["features"]):
            specs[f"feature_{i+1}"] = feat
        if page_data.get("sku"):
            specs["sku"] = page_data["sku"]
        product["official_specs"] = specs

    # Update display hero image
    display = product.get("display") or {}
    if isinstance(display, dict):
        hero = display.get("hero_image")
        if not hero or (isinstance(hero, dict) and "placeholder" in hero.get("url", "")):
            if page_data.get("image_url"):
                display["hero_image"] = {
                    "url": page_data["image_url"],
                    "type": "image",
                    "display_purpose": "hero",
                    "source": "halilit_product_page",
                }
                product["display"] = display

    return product
