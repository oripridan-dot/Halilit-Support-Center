"""
Commercial Data Harvester - Extracts pricing/SKU data from Halilit website.

This harvester is responsible for:
- Scraping Halilit product pages for prices
- Extracting SKUs, stock status, delivery info
- Creating CommercialData records
"""

import asyncio
import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from playwright.async_api import async_playwright, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from ..config import config
from ..models import CommercialData, StockStatus

logger = logging.getLogger(__name__)


class CommercialHarvester:
    """Harvests commercial data from Halilit website."""

    def __init__(self):
        self.output_dir = config.COMMERCIAL_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = config.HALILIT_BASE_URL
        self.headless = config.SCRAPER_HEADLESS
        self.timeout = config.SCRAPER_TIMEOUT_MS

        # ILS to USD conversion (approximate)
        self.ils_to_usd = 0.27

    async def harvest_brand(
        self,
        brand_id: str,
        brand_name: str,
        product_urls: Optional[List[str]] = None
    ) -> List[CommercialData]:
        """
        Harvest commercial data for a brand from Halilit.

        Args:
            brand_id: Brand identifier
            brand_name: Brand display name
            product_urls: Optional list of Halilit product URLs

        Returns:
            List of CommercialData records
        """
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not installed, using mock data")
            return await self._harvest_mock(brand_id)

        logger.info(
            f"💰 Harvesting commercial data for {brand_name} from Halilit")

        products = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context()

            try:
                if product_urls:
                    for url in product_urls:
                        product = await self._scrape_product_page(context, url, brand_id)
                        if product:
                            products.append(product)
                else:
                    # Search for brand on Halilit
                    products = await self._search_and_scrape(context, brand_id, brand_name)

            finally:
                await browser.close()

        # Save results
        self._save_results(brand_id, products)

        logger.info(
            f"✅ Harvested {len(products)} commercial entries for {brand_name}")
        return products

    async def _search_and_scrape(
        self,
        context,
        brand_id: str,
        brand_name: str
    ) -> List[CommercialData]:
        """Search Halilit for brand products and scrape."""
        page = await context.new_page()
        products = []

        try:
            # Go to brand search page
            search_url = f"{self.base_url}/search?q={brand_name.replace(' ', '+')}"
            await page.goto(search_url, wait_until="domcontentloaded", timeout=self.timeout)

            # Wait for products to load
            await asyncio.sleep(2)

            # Find all product links
            product_links = await page.evaluate('''() => {
                const links = Array.from(document.querySelectorAll('a[href*="product"], .product-item a'));
                return links.map(a => a.href).filter((v, i, a) => a.indexOf(v) === i);
            }''')

            logger.info(f"Found {len(product_links)} product links on Halilit")

            # Scrape each product
            for url in product_links[:50]:  # Limit
                product = await self._scrape_product_page(context, url, brand_id)
                if product:
                    products.append(product)
                await asyncio.sleep(0.3)  # Rate limit

        except Exception as e:
            logger.error(f"Error searching Halilit: {e}")
        finally:
            await page.close()

        return products

    async def _scrape_product_page(
        self,
        context,
        url: str,
        brand_id: str
    ) -> Optional[CommercialData]:
        """Scrape pricing data from a Halilit product page."""
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)

            # Extract data
            sku = await self._extract_sku(page)
            price_ils = await self._extract_price(page)
            stock_status = await self._extract_stock(page)

            if not sku:
                logger.debug(f"No SKU found at {url}")
                return None

            product_id = f"{brand_id}-{sku.lower().replace(' ', '-')}"

            return CommercialData(
                halilit_sku=sku,
                product_id=product_id,
                price_ils=price_ils,
                price_usd=round(price_ils * self.ils_to_usd,
                                2) if price_ils else None,
                stock_status=stock_status,
                product_url=url,
            )

        except Exception as e:
            logger.debug(f"Error scraping {url}: {e}")
            return None
        finally:
            await page.close()

    async def _extract_sku(self, page: Page) -> str:
        """Extract SKU from Halilit page."""
        selectors = [
            '[class*="sku"]',
            '[class*="product-code"]',
            '[data-sku]',
            '.product-sku',
        ]
        for selector in selectors:
            try:
                el = await page.query_selector(selector)
                if el:
                    text = await el.inner_text()
                    if text:
                        # Clean up SKU
                        sku = re.sub(r'^(SKU|מק"ט)[:：\s]*', '', text.strip())
                        return sku
            except:
                pass
        return ""

    async def _extract_price(self, page: Page) -> Optional[float]:
        """Extract price in ILS."""
        selectors = [
            '.price-value',
            '[class*="price"]',
            '.product-price',
        ]
        for selector in selectors:
            try:
                el = await page.query_selector(selector)
                if el:
                    text = await el.inner_text()
                    # Extract number from text like "₪1,234.00"
                    match = re.search(r'[\d,]+\.?\d*', text.replace(',', ''))
                    if match:
                        return float(match.group())
            except:
                pass
        return None

    async def _extract_stock(self, page: Page) -> StockStatus:
        """Extract stock status."""
        try:
            # Look for common stock indicators
            page_text = await page.inner_text('body')
            page_lower = page_text.lower()

            if 'out of stock' in page_lower or 'אזל' in page_text:
                return StockStatus.OUT_OF_STOCK
            elif 'pre-order' in page_lower or 'הזמנה מראש' in page_text:
                return StockStatus.PRE_ORDER
            elif 'in stock' in page_lower or 'במלאי' in page_text:
                return StockStatus.IN_STOCK
            elif 'discontinued' in page_lower:
                return StockStatus.DISCONTINUED
        except:
            pass

        return StockStatus.UNKNOWN

    def _save_results(self, brand_id: str, products: List[CommercialData]) -> None:
        """Save harvested data to JSON."""
        output_file = self.output_dir / f"{brand_id}.json"
        data = {
            "brand_id": brand_id,
            "source": "halilit",
            "harvested_at": datetime.utcnow().isoformat(),
            "product_count": len(products),
            "products": [p.model_dump(mode='json') for p in products],
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved commercial data to {output_file}")

    async def _harvest_mock(self, brand_id: str) -> List[CommercialData]:
        """Return mock commercial data."""
        return [
            CommercialData(
                halilit_sku=f"HL-{brand_id.upper()[:4]}-001",
                product_id=f"{brand_id}-sample-001",
                price_ils=2499.00,
                price_usd=674.73,
                stock_status=StockStatus.IN_STOCK,
                product_url=f"{self.base_url}/product/{brand_id}-sample",
            )
        ]

    def load_cached(self, brand_id: str) -> Optional[List[CommercialData]]:
        """Load previously harvested data."""
        cache_file = self.output_dir / f"{brand_id}.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [CommercialData(**p) for p in data.get('products', [])]
        return None
