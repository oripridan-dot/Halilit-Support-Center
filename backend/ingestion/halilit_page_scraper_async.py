"""
Async Halilit Page Scraper - High-Performance Version
=====================================================
Uses async/await with httpx for concurrent requests, making scraping 10-50x faster.

Usage:
    import asyncio
    from backend.ingestion.halilit_page_scraper_async import AsyncHalilitPageScraper
    
    async def main():
        scraper = AsyncHalilitPageScraper()
        products = await scraper.scrape_brand_full("adam audio")
        await scraper.close()
    
    asyncio.run(main())
"""

import asyncio
import json
import logging
import os
import re
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from backend.ingestion.visual_validator import validate_hero_candidates, INGESTION_SKIP_VISUAL_VALIDATION
from backend.ingestion.halilit_page_scraper import (
    HALILIT_BASE,
    CDN_PREFIX,
    HEADERS,
    REQUEST_TIMEOUT,
    DISCOVERY_TIMEOUT,
    DISCOVERY_RETRIES,
    DISCOVERY_RETRY_BACKOFF,
    extract_model_name,
    extract_model_number,
    MAX_SEARCH_PAGES,
    ITEMS_PER_PAGE,
    BRANDS_PAGE_URL,
    MAX_SITEMAP_PAGES,
)

try:
    from backend.ingestion.ingestion_config import (
        ASYNC_CONCURRENCY,
        MAX_PRODUCTS_PER_BRAND,
    )
except ImportError:
    ASYNC_CONCURRENCY = 50
    MAX_PRODUCTS_PER_BRAND = 0

# Resilient extraction — API-first + Gemini semantic fallback
from backend.ingestion.semantic_extractor import (
    SemanticExtractor,
    sniff_next_data,
    html_to_markdown,
    extract_with_gemini,
)

logger = logging.getLogger("AsyncHalilitPageScraper")

# Semaphore for rate limiting (concurrent requests)
_rate_limit_semaphore: Optional[asyncio.Semaphore] = None


def _get_rate_limit_semaphore():
    """Get or create rate limit semaphore."""
    global _rate_limit_semaphore
    if _rate_limit_semaphore is None:
        # Allow up to ASYNC_CONCURRENCY concurrent requests
        _rate_limit_semaphore = asyncio.Semaphore(ASYNC_CONCURRENCY)
    return _rate_limit_semaphore


class AsyncHalilitPageScraper:
    """
    Async version of HalilitPageScraper using httpx for concurrent requests.
    
    Much faster than sync version - can scrape 50+ products simultaneously.
    """

    def __init__(self, timeout: float = None):
        """
        Initialize async scraper.
        
        Args:
            timeout: Request timeout in seconds (default: REQUEST_TIMEOUT)
        """
        self.timeout = timeout or REQUEST_TIMEOUT
        self.client: Optional[httpx.AsyncClient] = None
        self._request_count = 0

    async def _ensure_client(self):
        """Ensure httpx client is initialized."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                headers=HEADERS,
                timeout=self.timeout,
                follow_redirects=True,
                limits=httpx.Limits(max_keepalive_connections=50, max_connections=100),
            )

    async def close(self):
        """Close httpx client."""
        if self.client:
            await self.client.aclose()
            self.client = None

    async def __aenter__(self):
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @staticmethod
    def _is_anti_bot_page(html: str) -> bool:
        """Detect Konimbo's anti-bot referrer check page."""
        return (len(html) < 2000
                and ("page_no_referer" in html or "limit_no_referer" in html))

    async def _get(self, url: str, retries: int = 2) -> Optional[str]:
        """
        Make async GET request with rate limiting and retry logic.
        
        Returns HTML text or None if failed.
        """
        await self._ensure_client()
        semaphore = _get_rate_limit_semaphore()
        
        for attempt in range(retries + 1):
            async with semaphore:
                try:
                    resp = await self.client.get(url)
                    self._request_count += 1
                    
                    if resp.status_code != 200:
                        if attempt < retries:
                            await asyncio.sleep(1)
                            continue
                        logger.warning(f"HTTP {resp.status_code} for {url}")
                        return None
                    
                    html = resp.text
                    
                    # Check for anti-bot page
                    if self._is_anti_bot_page(html):
                        if attempt < retries:
                            wait = (attempt + 1) * 1  # 1s, 2s backoff
                            logger.debug(f"Anti-bot detected for {url}, retry in {wait}s...")
                            await asyncio.sleep(wait)
                            continue
                        logger.debug(f"Anti-bot blocked: {url}")
                        return None
                    
                    return html
                    
                except httpx.RequestError as e:
                    logger.warning(f"Request failed for {url}: {e}")
                    if attempt < retries:
                        await asyncio.sleep(1)
                        continue
                    return None
        
        return None

    async def _get_discovery(self, url: str) -> Optional[str]:
        """GET for discovery pages (brands, sitemap) with longer timeout."""
        await self._ensure_client()
        semaphore = _get_rate_limit_semaphore()
        
        for attempt in range(DISCOVERY_RETRIES):
            async with semaphore:
                try:
                    resp = await self.client.get(url, timeout=DISCOVERY_TIMEOUT)
                    self._request_count += 1
                    
                    if resp.status_code != 200:
                        if attempt < DISCOVERY_RETRIES - 1:
                            await asyncio.sleep(DISCOVERY_RETRY_BACKOFF)
                        continue
                    
                    html = resp.text
                    if self._is_anti_bot_page(html):
                        if attempt < DISCOVERY_RETRIES - 1:
                            await asyncio.sleep(DISCOVERY_RETRY_BACKOFF)
                        continue
                    
                    return html
                    
                except httpx.RequestError as e:
                    logger.warning(f"Discovery request failed for {url}: {e}")
                    if attempt < DISCOVERY_RETRIES - 1:
                        await asyncio.sleep(DISCOVERY_RETRY_BACKOFF)
        
        return None

    def _extract_total_results(self, soup: BeautifulSoup) -> int:
        """Extract total result count from search/brand page."""
        text = soup.get_text()
        match = re.search(r'תוצאות:\s*(\d[\d,]*)', text)
        if match:
            return int(match.group(1).replace(',', ''))
        return 0

    def _extract_max_page(self, soup: BeautifulSoup) -> int:
        """Extract max page number from pagination."""
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
                href = href.replace("\n", "").replace("\r", "").strip()
                url = href if href.startswith("http") else HALILIT_BASE + href
                url = url.replace(" ", "")

        # Extract price - try multiple methods
        price = 0.0
        
        # Method 1: Try price selectors
        price_el = item.select_one(
            ".price, .price-new, .current-price, .price_value, .item_price"
        )
        if price_el:
            text = price_el.get_text(strip=True)
            # Look for Hebrew price pattern: "מחיר 1,234 ₪" or "1,234 ₪"
            price_match = re.search(r'([\d,]+)\s*₪', text)
            if price_match:
                try:
                    price = float(price_match.group(1).replace(',', ''))
                except (ValueError, TypeError):
                    pass
            # Fallback: extract digits
            if price == 0:
                digits = "".join(c for c in text if c.isdigit() or c == ".")
                if digits:
                    try:
                        price = float(digits)
                    except ValueError:
                        price = 0.0
        
        # Method 2: Try data attributes
        if price == 0:
            for attr in ["data-price", "data-item-price"]:
                price_val = item.get(attr)
                if price_val:
                    try:
                        price = float(str(price_val).replace(',', ''))
                        if price > 0:
                            break
                    except (ValueError, TypeError):
                        continue
        
        # Method 3: Search entire item text for price pattern
        if price == 0:
            item_text = item.get_text()
            price_match = re.search(r'מחיר\s*([\d,]+)\s*₪', item_text)
            if price_match:
                try:
                    price = float(price_match.group(1).replace(',', ''))
                except (ValueError, TypeError):
                    pass

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

    async def scrape_product_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single product page asynchronously.
        
        Returns same format as sync version.
        """
        if not url or not url.startswith("http"):
            return None

        html = await self._get(url)
        if not html:
            return None

        # ── Stage 1: API-First / Ghost Protocol ──────────────────────────
        # Try __NEXT_DATA__ before paying the BeautifulSoup parse cost.
        # Halilit's Next.js frontend often embeds the full product object here.
        _next_data = sniff_next_data(html)
        if _next_data:
            logger.info("[API-FIRST] __NEXT_DATA__ hit for %s", url)
            # Wrap into the downstream pipeline's expected skeleton
            # and return immediately — no CSS selector parsing needed.
            item_id_match = re.search(r"/items/(\d+)", url)
            halilit_id = (
                f"halilit-{item_id_match.group(1)}" if item_id_match
                else f"h-{hashlib.md5(url.encode()).hexdigest()[:10]}"
            )
            nd_price = _next_data.get("price", 0.0) or 0.0
            return {
                "halilit_id": halilit_id,
                "product_name": _next_data.get("title", ""),
                "official_name": _next_data.get("title", ""),
                "model_number": _next_data.get("sku", ""),
                "brand": _next_data.get("brand", ""),
                "sku": _next_data.get("sku", ""),
                "price_il": nd_price,
                "price_eilat": round(nd_price / 1.17, 2) if nd_price > 0 else 0.0,
                "description": _next_data.get("description", ""),
                "page_description": _next_data.get("description", ""),
                "image_url": _next_data.get("image_url", ""),
                "image_gallery": [_next_data["image_url"]] if _next_data.get("image_url") else [],
                "official_images": [],
                "features": [
                    {"name": k, "value": v}
                    for k, v in _next_data.get("specs", {}).items()
                ],
                "faq": [],
                "audiences": [],
                "halilit_url": url,
                "source": "halilit_next_data",
                "_extraction_source": "__NEXT_DATA__",
            }

        soup = BeautifulSoup(html, "html.parser")

        # Extract JSON-LD
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
            # ── Stage 2: Gemini Semantic Fallback ────────────────────────
            # JSON-LD is missing (SPA, JS-heavy, theme change). Pass the
            # rendered HTML to Gemini Structured Output — no CSS selectors.
            logger.info("[SEMANTIC] No JSON-LD on %s — trying Gemini extraction", url)
            markdown = html_to_markdown(html)
            semantic = extract_with_gemini(markdown) if len(markdown) > 100 else None
            if not semantic:
                logger.debug("[SEMANTIC] Gemini extraction yielded nothing for %s", url)
                return None
            item_id_match = re.search(r"/items/(\d+)", url)
            halilit_id = (
                f"halilit-{item_id_match.group(1)}" if item_id_match
                else f"h-{hashlib.md5(url.encode()).hexdigest()[:10]}"
            )
            sem_price = semantic.get("price", 0.0) or 0.0
            return {
                "halilit_id": halilit_id,
                "product_name": semantic.get("title", ""),
                "official_name": semantic.get("title", ""),
                "model_number": semantic.get("sku", ""),
                "brand": semantic.get("brand", ""),
                "sku": semantic.get("sku", ""),
                "price_il": sem_price,
                "price_eilat": round(sem_price / 1.17, 2) if sem_price > 0 else 0.0,
                "description": semantic.get("description", ""),
                "page_description": semantic.get("description", ""),
                "image_url": semantic.get("image_url", ""),
                "image_gallery": [semantic["image_url"]] if semantic.get("image_url") else [],
                "official_images": [],
                "features": [
                    {"name": k, "value": v}
                    for k, v in semantic.get("specs", {}).items()
                ],
                "faq": [],
                "audiences": [],
                "halilit_url": url,
                "source": "halilit_product_page",
                "_extraction_source": "gemini_semantic",
            }

        # Merge products
        product = self._merge_jsonld_products(jsonld_products)

        # Extract gallery images
        gallery_images = self._extract_gallery_images(soup)

        # Extract price from DOM if JSON-LD price is missing
        if product.get("price", 0) == 0:
            dom_price = self._extract_price_from_dom(soup)
            if dom_price > 0:
                product["price"] = dom_price
                logger.debug(f"Extracted price from DOM: {dom_price}")

        # Extract features from DOM if JSON-LD features are missing
        if not product.get("features"):
            dom_features = self._extract_features_from_dom(soup)
            if dom_features:
                product["features"] = dom_features
                logger.debug(f"Extracted {len(dom_features)} features from DOM")

        # Extract description
        page_description = ""
        if jsonld_webpage:
            page_description = jsonld_webpage.get("description", "")
        if not page_description:
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                page_description = meta_desc.get("content", "")
        # Fallback to DOM extraction if still empty
        if not page_description or len(page_description.strip()) < 20:
            dom_desc = self._extract_description_from_dom(soup)
            if dom_desc:
                page_description = dom_desc
                # Also update product description if empty
                if not product.get("description"):
                    product["description"] = dom_desc

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

        # Compute stable ID - use format "halilit-{id}" to match existing data
        item_id_match = re.search(r"/items/(\d+)", url)
        if item_id_match:
            halilit_id = f"halilit-{item_id_match.group(1)}"
        else:
            halilit_id = f"h-{hashlib.md5(url.encode()).hexdigest()[:10]}"

        # Merge gallery images
        all_images = []
        seen_img = set()
        for img_url in product.get("images", []) + gallery_images:
            if img_url and img_url not in seen_img and CDN_PREFIX in img_url:
                normalized = self._normalize_image_url(img_url)
                if normalized not in seen_img:
                    all_images.append(normalized)
                    seen_img.add(normalized)

        # Visual validation (can be skipped for speed)
        hero_url = None
        gallery_order = all_images
        if not INGESTION_SKIP_VISUAL_VALIDATION and all_images:
            hero_url, gallery_order, _ = validate_hero_candidates(
                all_images,
                purpose="hero",
                product_name=full_name,
                brand=brand_name,
            )
        elif all_images:
            hero_url = all_images[0] if all_images else None

        # Features
        features = product.get("features", [])
        audiences = product.get("audiences", [])

        # Ensure price is set correctly
        price_il = product.get("price", 0.0)
        if price_il <= 0:
            # Last resort: try extracting from URL or other sources
            # Some products might have price in structured data we missed
            pass
        
        result = {
            "halilit_id": halilit_id,
            "product_name": full_name,
            "official_name": model_name,
            "model_number": model_number if model_number else product.get("sku"),
            "brand": brand_name,
            "sku": product.get("sku"),
            "price_il": price_il,
            "price_eilat": round(price_il / 1.17, 2) if price_il > 0 else 0.0,
            "description": product.get("description", "") or page_description,
            "page_description": page_description,
            "image_url": hero_url or "",
            "image_gallery": gallery_order,
            "official_images": [
                {
                    "url": img,
                    "type": "image",
                    "display_purpose": "hero" if i == 0 else "gallery",
                    "source": "halilit_product_page",
                    "priority": 100 - i * 10,
                }
                for i, img in enumerate(gallery_order)
            ],
            "features": features,
            "faq": faq_items,
            "audiences": audiences,
            "halilit_url": url,
            "source": "halilit_product_page",
        }

        return result

    def _merge_jsonld_products(self, products: List[Dict]) -> Dict:
        """Merge multiple JSON-LD Product blocks."""
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
            name = p.get("name", "")
            if name and (not merged["name"] or "|" not in name):
                merged["name"] = name.split("|")[0].strip()

            desc = p.get("description", "")
            if desc and len(desc) > len(merged["description"]):
                merged["description"] = desc

            brand = p.get("brand", {})
            if isinstance(brand, dict) and brand.get("name"):
                merged["brand_name"] = brand["name"]

            offers = p.get("offers", {})
            if isinstance(offers, dict):
                try:
                    price = float(offers.get("price", 0))
                    if price > 0 and (merged["price"] == 0 or price < merged["price"]):
                        merged["price"] = price
                except (ValueError, TypeError):
                    pass

            sku = p.get("sku", "")
            if sku and not merged["sku"]:
                merged["sku"] = sku

            imgs = p.get("image", [])
            if isinstance(imgs, str):
                imgs = [imgs]
            for img in imgs:
                if img and img not in merged["images"]:
                    merged["images"].append(img)

            for prop in p.get("additionalProperty", []):
                name = (prop.get("name") or "").strip().rstrip("\t")
                val = (prop.get("value") or "").strip()
                if val:
                    merged["features"].append({"name": name, "value": val})

            for aud in p.get("audience", []):
                aud_type = aud.get("audienceType", "")
                if aud_type and aud_type not in merged["audiences"]:
                    merged["audiences"].append(aud_type)

        return merged

    def _extract_gallery_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract gallery images from DOM."""
        images = []
        gallery = soup.select_one(".item_gallery, .gallery, .product-gallery")
        if gallery:
            for img in gallery.find_all("img"):
                src = img.get("data-src") or img.get("src") or ""
                if src and CDN_PREFIX in src:
                    images.append(src)
        return images

    def _normalize_image_url(self, url: str) -> str:
        """Normalize image URL to use 'large' size."""
        url = re.sub(r"/system/photos/(\d+)/(medium|original|extra_large|thumb)/",
                     r"/system/photos/\1/large/", url)
        url = re.sub(r"\?\d+$", "", url)
        return url

    def _extract_price_from_dom(self, soup: BeautifulSoup) -> float:
        """
        Extract price from DOM when JSON-LD is missing.

        First tries semantic Gemini extraction (resilient to CSS changes);
        falls back to structured-data attributes only (no fragile CSS selectors).
        """
        # Try structured data attributes — these come from the server and are stable
        raw_html = str(soup)
        # Look for JSON price in __NEXT_DATA__ first (free, no API call)
        nd = sniff_next_data(raw_html)
        if nd and nd.get("price", 0) > 0:
            return float(nd["price"])

        # Try data-price attributes (server-rendered, stable)
        for el in soup.select("[data-price]"):
            try:
                price = float(el.get("data-price", 0))
                if price > 0:
                    return price
            except (ValueError, TypeError):
                continue

        # Gemini semantic fallback — read the page as text, no CSS dependency
        markdown = html_to_markdown(raw_html)
        if len(markdown) > 100:
            semantic = extract_with_gemini(markdown)
            if semantic and semantic.get("price", 0) > 0:
                logger.debug("[SEMANTIC] Price extracted via Gemini: %s", semantic["price"])
                return float(semantic["price"])

        return 0.0

    def _extract_features_from_dom(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract features/specs from DOM when JSON-LD is missing.

        Uses Gemini Semantic Extraction — immune to CSS class / DOM restructures.
        """
        raw_html = str(soup)
        markdown = html_to_markdown(raw_html)
        if len(markdown) < 100:
            return []
        semantic = extract_with_gemini(markdown)
        if not semantic:
            return []
        features: List[Dict[str, str]] = []
        for k, v in semantic.get("specs", {}).items():
            features.append({"name": k, "value": v})
        for feat in semantic.get("features", []):
            if isinstance(feat, str) and ":" in feat:
                parts = feat.split(":", 1)
                features.append({"name": parts[0].strip(), "value": parts[1].strip()})
            elif isinstance(feat, str):
                features.append({"name": feat, "value": ""})
        logger.debug("[SEMANTIC] Extracted %d features via Gemini", len(features))
        return features[:50]

    def _extract_description_from_dom(self, soup: BeautifulSoup) -> str:
        """
        Extract description from DOM when JSON-LD is missing.

        Uses Gemini Semantic Extraction — immune to CSS class / DOM restructures.
        Falls back to <meta name="description"> (server-rendered, always stable).
        """
        # Meta description is server-rendered and stable across theme changes
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            text = (meta_desc.get("content") or "").strip()
            if len(text) > 20:
                return text

        # Gemini semantic fallback
        raw_html = str(soup)
        markdown = html_to_markdown(raw_html)
        if len(markdown) < 100:
            return ""
        semantic = extract_with_gemini(markdown)
        if semantic and semantic.get("description"):
            desc = semantic["description"].strip()
            logger.debug("[SEMANTIC] Description extracted via Gemini (%d chars)", len(desc))
            return desc
        return ""

    async def scrape_brand_full(
        self,
        brand: str,
        max_products: int = 0,
        skip_existing_urls: set = None,
        brand_group_url: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Full async pipeline: scrape brand listing → scrape all product pages concurrently.
        
        This is MUCH faster than sync version - scrapes 50+ products simultaneously.
        """
        skip_existing_urls = skip_existing_urls or set()

        logger.info(f"🛒 Starting async full scrape for brand: {brand}")

        # Phase 1: Get product URLs (still sequential for listing pages)
        listings = await self._scrape_brand_listing_async(brand, brand_group_url)
        logger.info(f"  Found {len(listings)} products in listing")

        # Filter
        to_scrape = [
            item for item in listings
            if item["url"] and item["url"] not in skip_existing_urls
        ]
        if max_products > 0:
            to_scrape = to_scrape[:max_products]
        if MAX_PRODUCTS_PER_BRAND > 0:
            to_scrape = to_scrape[:MAX_PRODUCTS_PER_BRAND]

        logger.info(f"  Scraping {len(to_scrape)} product pages concurrently...")

        # Phase 2: Scrape all product pages concurrently
        tasks = [self.scrape_product_page(item["url"]) for item in to_scrape]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        products = []
        failed = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"  Failed to scrape {to_scrape[i]['url']}: {result}")
                failed += 1
            elif result:
                # Merge with listing data
                merged = self._merge_page_with_listing(result, to_scrape[i])
                if merged:
                    products.append(merged)
            else:
                failed += 1

        logger.info(f"  ✅ Scraped {len(products)} products, {failed} failures")
        logger.info(f"  Total requests: {self._request_count}")
        return products

    async def _scrape_brand_listing_async(self, brand: str, brand_group_url: str = "") -> List[Dict[str, Any]]:
        """Scrape brand listing pages (async but sequential for pagination)."""
        if brand_group_url:
            return await self._scrape_brand_group_listing_async(brand, brand_group_url)
        return await self._scrape_search_listing_async(brand)

    async def _scrape_brand_group_listing_async(self, brand: str, group_url: str) -> List[Dict[str, Any]]:
        """Scrape brand group page with pagination."""
        all_items = []
        seen_urls = set()

        logger.info(f"  📋 Scraping brand group page: {group_url}")
        html = await self._get(group_url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        total_results = self._extract_total_results(soup)
        max_page_from_dom = self._extract_max_page(soup)
        expected_pages = max(
            max_page_from_dom,
            (total_results + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if total_results > 0 else 1
        )
        expected_pages = min(expected_pages, MAX_SEARCH_PAGES)

        logger.info(f"  📊 Brand group: {total_results} total products, {expected_pages} pages")

        # Parse page 1
        items, new_count = self._parse_listing_page(soup, brand, seen_urls)
        all_items.extend(items)

        # Scrape remaining pages concurrently
        if expected_pages > 1:
            tasks = []
            for page in range(2, expected_pages + 1):
                separator = "&" if "?" in group_url else "?"
                page_url = f"{group_url}{separator}page={page}"
                tasks.append(self._get(page_url))

            htmls = await asyncio.gather(*tasks, return_exceptions=True)
            for page, html in enumerate(htmls, start=2):
                if isinstance(html, Exception) or not html:
                    continue
                soup = BeautifulSoup(html, "html.parser")
                items, new_count = self._parse_listing_page(soup, brand, seen_urls)
                all_items.extend(items)

        logger.info(f"  ✅ Brand group listing: {len(all_items)} products")
        return all_items

    async def _scrape_search_listing_async(self, brand: str) -> List[Dict[str, Any]]:
        """Scrape search results with pagination."""
        from urllib.parse import quote
        encoded = quote(brand)
        all_items = []
        seen_urls = set()

        # Get page 1 first to determine total pages
        url = f"{HALILIT_BASE}/search?q={encoded}&page=1"
        html = await self._get(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        total_results = self._extract_total_results(soup)
        max_page_from_dom = self._extract_max_page(soup)
        expected_pages = min(
            max(max_page_from_dom, (total_results + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if total_results > 0 else 1),
            MAX_SEARCH_PAGES
        )

        items, _ = self._parse_listing_page(soup, brand, seen_urls)
        all_items.extend(items)

        # Scrape remaining pages concurrently
        if expected_pages > 1:
            tasks = [
                self._get(f"{HALILIT_BASE}/search?q={encoded}&page={page}")
                for page in range(2, expected_pages + 1)
            ]
            htmls = await asyncio.gather(*tasks, return_exceptions=True)
            for html in htmls:
                if isinstance(html, Exception) or not html:
                    continue
                soup = BeautifulSoup(html, "html.parser")
                items, _ = self._parse_listing_page(soup, brand, seen_urls)
                all_items.extend(items)

        return all_items

    def _parse_listing_page(
        self, soup: BeautifulSoup, brand: str, seen_urls: set
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Parse products from listing page."""
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

    def _merge_page_with_listing(self, page_data: Dict, listing: Dict) -> Optional[Dict]:
        """Merge page data with listing data. ALWAYS prefer listing price if available."""
        if not page_data:
            # Fall back to listing data only
            return {
                "halilit_id": f"scraped-{hashlib.md5(listing['url'].encode()).hexdigest()[:10]}",
                "product_name": listing["name"],
                "brand": listing["brand"],
                "price_il": listing.get("price", 0.0),
                "price_eilat": round(listing.get("price", 0.0) / 1.17, 2) if listing.get("price", 0) > 0 else 0.0,
                "halilit_url": listing["url"],
                "image_url": listing.get("image_url", ""),
                "official_images": [
                    {"url": listing.get("image_url", ""), "type": "image",
                     "display_purpose": "hero", "source": "halilit_listing"}
                ] if listing.get("image_url") else [],
                "source": "halilit_listing_only",
            }

        # CRITICAL: Always prefer listing price if it exists (listing prices are more reliable)
        listing_price = listing.get("price", 0.0)
        page_price = page_data.get("price_il", 0.0) or page_data.get("price", 0.0)
        
        if listing_price > 0:
            # Use listing price if it's valid, or if page price is 0
            if page_price == 0 or listing_price > 0:
                page_data["price_il"] = listing_price
                page_data["price_eilat"] = round(listing_price / 1.17, 2)
                logger.debug(f"Using listing price: {listing_price} (page price was {page_price})")
        elif page_price > 0:
            # Only use page price if listing price is missing
            page_data["price_il"] = page_price
            page_data["price_eilat"] = round(page_price / 1.17, 2) if page_price > 0 else 0.0

        # Fill image gaps from listing
        if not page_data.get("image_url") and listing.get("image_url"):
            page_data["image_url"] = listing["image_url"]
            # Also add to gallery if not already there
            if listing.get("image_url") not in page_data.get("image_gallery", []):
                if "image_gallery" not in page_data:
                    page_data["image_gallery"] = []
                page_data["image_gallery"].insert(0, listing["image_url"])

        return page_data
