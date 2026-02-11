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
RATE_LIMIT_DELAY = 0.3  # seconds between requests
MAX_SEARCH_PAGES = 15
MAX_WORKERS = 4  # parallel page scrapes


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

    def _get(self, url: str) -> Optional[requests.Response]:
        """Make a rate-limited GET request."""
        self._rate_limit()
        try:
            resp = self.session.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                return resp
            logger.warning(f"HTTP {resp.status_code} for {url}")
            return None
        except requests.RequestException as e:
            logger.warning(f"Request failed for {url}: {e}")
            return None

    # ─── Phase 1: Search Results (Product Listing) ──────────────────────

    def scrape_brand_listing(self, brand: str) -> List[Dict[str, Any]]:
        """
        Scrape Halilit search results to get product URLs for a brand.

        Returns list of {url, name, price, image_url} dicts.
        """
        from urllib.parse import quote
        encoded = quote(brand)
        all_items = []
        seen_urls = set()

        for page in range(1, MAX_SEARCH_PAGES + 1):
            url = f"{HALILIT_BASE}/search?q={encoded}&page={page}"
            logger.info(f"  Scraping listing page {page}: {url}")

            resp = self._get(url)
            if not resp:
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.select(".box, .item, .product_item, .product_box")

            if not items:
                logger.info(f"  No items on page {page}, stopping.")
                break

            page_count = 0
            for item in items:
                try:
                    parsed = self._parse_listing_item(item, brand)
                    if parsed and parsed["url"] and parsed["url"] not in seen_urls:
                        seen_urls.add(parsed["url"])
                        all_items.append(parsed)
                        page_count += 1
                except Exception as e:
                    logger.debug(f"  Skip item parse error: {e}")

            logger.info(f"  Page {page}: {page_count} new products")

            if page_count == 0:
                break

        logger.info(f"  Total listing items for {brand}: {len(all_items)}")
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
            href = link_el.get("href", "")
            if href:
                url = href if href.startswith("http") else HALILIT_BASE + href

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
            1) if item_id_match else f"h-{abs(hash(url))}"

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
        max_products: int = 200,
        skip_existing_urls: set = None,
    ) -> List[Dict[str, Any]]:
        """
        Full pipeline: scrape search listing → scrape each product page.

        Args:
            brand: Brand name to search on Halilit
            max_products: Maximum products to scrape
            skip_existing_urls: URLs to skip (already scraped)

        Returns:
            List of fully enriched product dicts
        """
        skip_existing_urls = skip_existing_urls or set()

        logger.info(f"🛒 Starting full scrape for brand: {brand}")

        # Phase 1: Get product URLs from search
        listings = self.scrape_brand_listing(brand)
        logger.info(f"  Found {len(listings)} products in search results")

        # Filter to products we haven't scraped yet
        to_scrape = [
            item for item in listings
            if item["url"] and item["url"] not in skip_existing_urls
        ][:max_products]

        logger.info(f"  Scraping {len(to_scrape)} product pages...")

        # Phase 2: Scrape each product page (with parallelism)
        products = []
        failed = 0

        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_listing = {
                executor.submit(self._scrape_and_merge, item): item
                for item in to_scrape
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
                    logger.warning(f"  Failed to scrape {listing['url']}: {e}")
                    failed += 1

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
                "halilit_id": f"scraped-{abs(hash(listing['url']))}",
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
    current_desc = product.get("official_description") or product.get(
        "description_short") or ""
    is_placeholder = (
        not current_desc
        or current_desc == "No description available."
        or "ultimate stage piano" in current_desc.lower()
    )
    if is_placeholder:
        if page_data.get("description"):
            product["official_description"] = page_data["description"]
            product["description_short"] = page_data["description"][:200]
        elif page_data.get("page_description"):
            product["official_description"] = page_data["page_description"]
            product["description_short"] = page_data["page_description"][:200]

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
