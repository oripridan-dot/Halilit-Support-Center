"""
Official Data Harvester - Extracts manufacturer data from brand websites.

This harvester is responsible for:
- Scraping official product pages
- Extracting specifications, descriptions, images
- Downloading manuals and documentation
- Creating OfficialData records
"""

import asyncio
import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from ..config import config
from ..models import OfficialData

logger = logging.getLogger(__name__)


class OfficialHarvester:
    """Harvests official manufacturer data from brand websites."""

    def __init__(self):
        self.output_dir = config.OFFICIAL_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headless = config.SCRAPER_HEADLESS
        self.timeout = config.SCRAPER_TIMEOUT_MS

    async def harvest_brand(
        self,
        brand_id: str,
        brand_name: str,
        official_url: str,
        product_urls: Optional[List[str]] = None
    ) -> List[OfficialData]:
        """
        Harvest all products from a brand's official website.

        Args:
            brand_id: Normalized brand identifier (e.g., "adam-audio")
            brand_name: Display name (e.g., "ADAM Audio")
            official_url: Brand's official website base URL
            product_urls: Optional list of specific product page URLs to scrape

        Returns:
            List of OfficialData records
        """
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not installed, using mock data")
            return await self._harvest_mock(brand_id, brand_name)

        logger.info(
            f"🔍 Harvesting official data for {brand_name} from {official_url}")

        products = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context()

            try:
                if product_urls:
                    # Scrape specific product pages
                    for url in product_urls:
                        product = await self._scrape_product_page(context, url, brand_id, brand_name)
                        if product:
                            products.append(product)
                else:
                    # Discover and scrape all products from brand site
                    products = await self._discover_and_scrape(
                        context, official_url, brand_id, brand_name
                    )
            finally:
                await browser.close()

        # Save harvested data
        self._save_results(brand_id, products)

        logger.info(f"✅ Harvested {len(products)} products for {brand_name}")
        return products

    async def _scrape_product_page(
        self,
        context,
        url: str,
        brand_id: str,
        brand_name: str
    ) -> Optional[OfficialData]:
        """Scrape a single product page."""
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)

            # Extract product data
            name = await self._extract_name(page)
            if not name:
                logger.warning(f"Could not extract name from {url}")
                return None

            sku = await self._extract_sku(page, name)
            description = await self._extract_description(page)
            specs = await self._extract_specifications(page)
            images = await self._extract_images(page)
            category = await self._extract_category(page)

            # Generate product ID
            product_id = self._generate_id(brand_id, sku or name)

            return OfficialData(
                manufacturer_sku=sku or product_id,
                official_name=name,
                brand_id=brand_id,
                brand_name=brand_name,
                category=category,
                description=description,
                specifications=specs,
                images=images,
                official_url=url,
            )

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
        finally:
            await page.close()

    async def _discover_and_scrape(
        self,
        context,
        base_url: str,
        brand_id: str,
        brand_name: str
    ) -> List[OfficialData]:
        """Discover product pages and scrape them."""
        page = await context.new_page()
        products = []

        try:
            await page.goto(base_url, wait_until="domcontentloaded", timeout=self.timeout)

            # Find product links (common patterns)
            product_links = await page.evaluate('''() => {
                const links = Array.from(document.querySelectorAll('a[href*="product"], a[href*="/p/"], a[href*="item"]'));
                return links.map(a => a.href).filter((v, i, a) => a.indexOf(v) === i);
            }''')

            logger.info(f"Found {len(product_links)} product links")

            # Scrape each product (with concurrency limit)
            # Limit to prevent overload
            for url in product_links[:config.SCRAPER_CONCURRENT * 10]:
                product = await self._scrape_product_page(context, url, brand_id, brand_name)
                if product:
                    products.append(product)
                await asyncio.sleep(0.5)  # Rate limiting

        except Exception as e:
            logger.error(f"Error discovering products: {e}")
        finally:
            await page.close()

        return products

    async def _extract_name(self, page: Page) -> str:
        """Extract product name from page."""
        selectors = [
            'h1[class*="product"]',
            'h1[class*="title"]',
            '.product-title h1',
            '#product-name',
            'h1',
        ]
        for selector in selectors:
            try:
                el = await page.query_selector(selector)
                if el:
                    text = await el.inner_text()
                    if text and len(text.strip()) > 2:
                        return text.strip()[:200]
            except:
                pass
        return ""

    async def _extract_sku(self, page: Page, name: str) -> str:
        """Extract SKU/model number."""
        # Try common SKU patterns
        selectors = [
            '[class*="sku"]',
            '[class*="model"]',
            '[data-sku]',
        ]
        for selector in selectors:
            try:
                el = await page.query_selector(selector)
                if el:
                    text = await el.inner_text()
                    if text:
                        return text.strip()
            except:
                pass

        # Extract from name using regex (common model patterns)
        match = re.search(r'([A-Z0-9]{2,}[-]?[A-Z0-9]+)', name)
        if match:
            return match.group(1)

        return ""

    async def _extract_description(self, page: Page) -> str:
        """Extract product description."""
        selectors = [
            '[class*="description"]',
            '.product-description',
            'meta[name="description"]',
        ]
        for selector in selectors:
            try:
                if 'meta' in selector:
                    el = await page.query_selector(selector)
                    if el:
                        return (await el.get_attribute('content') or '')[:2000]
                else:
                    el = await page.query_selector(selector)
                    if el:
                        text = await el.inner_text()
                        if text:
                            return text.strip()[:2000]
            except:
                pass
        return ""

    async def _extract_specifications(self, page: Page) -> Dict[str, Dict[str, str]]:
        """Extract technical specifications."""
        specs = {}

        try:
            # Look for spec tables
            tables = await page.query_selector_all('table')
            for table in tables:
                rows = await table.query_selector_all('tr')
                for row in rows:
                    cells = await row.query_selector_all('td, th')
                    if len(cells) >= 2:
                        key = await cells[0].inner_text()
                        value = await cells[1].inner_text()
                        if key and value:
                            category = "Specifications"
                            if category not in specs:
                                specs[category] = {}
                            specs[category][key.strip()] = value.strip()

            # Look for definition lists
            dls = await page.query_selector_all('dl')
            for dl in dls:
                dts = await dl.query_selector_all('dt')
                dds = await dl.query_selector_all('dd')
                for dt, dd in zip(dts, dds):
                    key = await dt.inner_text()
                    value = await dd.inner_text()
                    if key and value:
                        if "Technical" not in specs:
                            specs["Technical"] = {}
                        specs["Technical"][key.strip()] = value.strip()

        except Exception as e:
            logger.debug(f"Error extracting specs: {e}")

        return specs

    async def _extract_images(self, page: Page) -> List[Dict[str, Any]]:
        """Extract product images."""
        images = []

        try:
            img_elements = await page.query_selector_all('img[src*="product"], img[class*="product"], .gallery img')

            for i, img in enumerate(img_elements[:10]):  # Limit to 10 images
                src = await img.get_attribute('src')
                alt = await img.get_attribute('alt') or "Product image"

                if src and ('http' in src or src.startswith('/')):
                    role = "hero" if i == 0 else "gallery"
                    images.append({
                        "url": src,
                        "alt": alt[:100],
                        "role": role,
                    })
        except Exception as e:
            logger.debug(f"Error extracting images: {e}")

        return images

    async def _extract_category(self, page: Page) -> str:
        """Extract product category from breadcrumbs or metadata."""
        try:
            # Try breadcrumbs
            breadcrumbs = await page.query_selector_all('.breadcrumb a, nav[aria-label="breadcrumb"] a')
            if len(breadcrumbs) >= 2:
                # Second to last is usually category
                category_el = breadcrumbs[-2]
                text = await category_el.inner_text()
                if text:
                    return text.strip()
        except:
            pass
        return "Other"

    def _generate_id(self, brand_id: str, identifier: str) -> str:
        """Generate a URL-safe product ID."""
        clean = re.sub(r'[^a-zA-Z0-9]', '-', identifier.lower())
        clean = re.sub(r'-+', '-', clean).strip('-')
        return f"{brand_id}-{clean}"

    def _save_results(self, brand_id: str, products: List[OfficialData]) -> None:
        """Save harvested data to JSON."""
        output_file = self.output_dir / f"{brand_id}.json"
        data = {
            "brand_id": brand_id,
            "harvested_at": datetime.utcnow().isoformat(),
            "product_count": len(products),
            "products": [p.model_dump(mode='json') for p in products],
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved official data to {output_file}")

    async def _harvest_mock(self, brand_id: str, brand_name: str) -> List[OfficialData]:
        """Return mock data when Playwright is not available."""
        logger.info(f"Using mock official data for {brand_name}")
        return [
            OfficialData(
                manufacturer_sku=f"{brand_id.upper()}-SAMPLE-001",
                official_name=f"{brand_name} Sample Product",
                brand_id=brand_id,
                brand_name=brand_name,
                category="Studio Monitors",
                description=f"Sample product from {brand_name}. This is mock data.",
                specifications={
                    "Audio": {
                        "Frequency Response": "45Hz - 50kHz",
                        "Max SPL": "106 dB",
                    }
                },
                images=[{
                    "url": f"https://example.com/{brand_id}/product.jpg",
                    "alt": f"{brand_name} Product",
                    "role": "hero",
                }],
            )
        ]

    def load_cached(self, brand_id: str) -> Optional[List[OfficialData]]:
        """Load previously harvested data from cache."""
        cache_file = self.output_dir / f"{brand_id}.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [OfficialData(**p) for p in data.get('products', [])]
        return None
