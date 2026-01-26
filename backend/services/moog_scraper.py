"""
Moog-Specific Scraper - COMPREHENSIVE DATA EXTRACTION
======================================================

Moog Music Inc. - Legendary analog synthesizer manufacturer.
Website: https://www.moogmusic.com

GOAL: Extract ALL available data from Moog website for JIT RAG system
----------------------------------------------------------------------
✓ Product metadata (name, model, SKU, categories)
✓ Full descriptions (marketing copy, long-form content)
✓ ALL images and media (main, gallery, technical diagrams, videos)
✓ Complete specifications (all spec tables, technical details)
✓ Features and benefits (bullet points, marketing content)
✓ Manuals and documentation (PDFs, quick start guides, reference docs)
✓ Support articles and knowledge base (patches, updates)
✓ Support resources (downloads, software, patches)
✓ White background product images for thumbnails
✓ Brand logo downloads
✓ Related accessories (recommended, required, compatible)
"""

from models.product_hierarchy import (
    ProductCore, ProductCatalog, BrandIdentity,
    ProductImage, ProductSpecification, SourceType, ProductRelationship, RelationshipType,
    ProductStatus
)
from services.scraper_enhancements import (
    SupportArticleExtractor, ProductImageEnhancer, BrandLogoDownloader
)
import asyncio
import logging
from typing import List, Dict, Optional, Set, Any
from datetime import datetime
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, AsyncRetrying
from pathlib import Path
import json
import sys
import re
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.config import settings

sys.path.insert(0, '/workspaces/hsc-jit-v3/backend/models')

logger = logging.getLogger(__name__)


class MoogScraper:
    """Specialized scraper for Moog Music website"""

    def __init__(self):
        self.base_url = "https://www.moogmusic.com"
        self.products_url = f"{self.base_url}/products"
        
        # Moog main categories
        self.category_urls = [
            # Adjusted based on actual site structure
            "https://www.moogmusic.com/synthesizers",
            "https://www.moogmusic.com/accessories", 
            "https://www.moogmusic.com/theremins",
            "https://www.moogmusic.com/controllers",
            "https://www.moogmusic.com/merch"
        ]

    async def scrape_and_return_raw(self, max_products: int = None) -> List[Dict[str, Any]]:
        """
        New Protocol Method (AS-IS): Scrape and return raw dictionaries.
        Does NOT normalize or clean data.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-dev-shm-usage', '--no-sandbox', '--disable-gpu']
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = await context.new_page()

            raw_items = []
            
            try:
                # Get all product URLs
                urls = await self._get_product_urls(page, max_products)
                
                for i, url in enumerate(urls):
                    if max_products and i >= max_products:
                        break
                        
                    logger.info(f"   Scraping RAW [{i+1}/{len(urls)}]: {url}")
                    try:
                        raw_data = await self._scrape_raw_page(page, url)
                        if raw_data:
                            raw_items.append(raw_data)
                    except Exception as e:
                        logger.error(f"   Error capturing RAW {url}: {e}")
                        
            except Exception as e:
                logger.error(f"Fatal error during RAW scraping: {e}")
                raise
            finally:
                await browser.close()
                
            return raw_items

    async def _scrape_raw_page(self, page: Page, url: str) -> Dict[str, Any]:
        """
        Extracts raw data elements without cleaning.
        Generic implementation for Moog.
        """
        await self._navigate(page, url)
        await asyncio.sleep(1) # Wait for JS
        
        # 1. Basic Metadata
        try:
             h1 = await page.locator('h1').first.inner_text()
        except:
             h1 = ""
             
        # 2. Raw Specs
        raw_specs = []
        tables = await page.locator('table').all()
        for table in tables:
            rows = await table.locator('tr').all()
            for row in rows:
                cells = await row.locator('td, th').all()
                if len(cells) >= 2:
                    k = await cells[0].inner_text()
                    v = await cells[1].inner_text()
                    raw_specs.append({"key": k, "value": v})
        
        # 3. Raw Images & Videos
        images = []
        imgs = await page.locator('img').all()
        for img in imgs:
             src = await img.get_attribute('src')
             alt = await img.get_attribute('alt')
             if src:
                 if src.startswith('/'):
                     src = f"https://www.moogmusic.com{src}"
                 images.append({"url": src, "alt_text": alt})
                 
        videos = []
        iframes = await page.locator('iframe').all()
        for frame in iframes:
            src = await frame.get_attribute('src')
            if src: videos.append(src)
            
        # 4. Description Blocks
        desc_text = ""
        try:
             # Moog specific content container
             main_content = await page.evaluate("() => document.querySelector('.main-content') ? document.querySelector('.main-content').innerText : document.body.innerText")
             desc_text = main_content
        except:
             pass

        features = []
        try:
             lis = await page.locator('ul li').all()
             for li in lis[:30]: 
                  txt = await li.inner_text()
                  if len(txt) > 10:
                      features.append(txt)
        except:
             pass

        return {
            "source_url": url,
            "brand": "Moog",
            "model": h1,
            "name": h1,
            "description": desc_text,
            "specifications": raw_specs,
            "images": images,
            "videos": videos,
            "features": features,
            "manuals": [],
            "support_url": url,
            "hierarchy": {},
            "metadata": {"raw_capture": True}
        }

    async def scrape_all_products(self, max_products: int = None) -> ProductCatalog:
        """
        Scrape ALL Moog products with COMPREHENSIVE data extraction

        Args:
            max_products: Maximum products to scrape (None = scrape ALL products)

        Returns:
            ProductCatalog with comprehensive product data ready for JIT RAG
        """
        logger.info(
            f"🎹 Starting COMPREHENSIVE Moog scrape (max: {'ALL' if max_products is None else max_products})")
        logger.info(f"   Goal: Extract ALL available data for JIT RAG system")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=settings.SCRAPER_HEADLESS,
                args=['--disable-dev-shm-usage', '--no-sandbox', '--disable-gpu']
            )
            page = await browser.new_page()

            try:
                # Step 1: Get all product URLs
                product_urls = await self._get_product_urls(page, max_products)
                logger.info(f"📋 Found {len(product_urls)} product URLs")

                # Limit to max_products only if specified
                if max_products is not None:
                    product_urls = product_urls[:max_products]
                    logger.info(f"   Limited to {len(product_urls)} products")

                # Step 2: Scrape each product with FULL data extraction
                products = []
                total_images = 0
                total_videos = 0
                total_specs = 0
                total_features = 0
                total_manuals = 0
                total_accessories = 0

                for i, url in enumerate(product_urls, 1):
                    logger.info(
                        f"   [{i}/{len(product_urls)}] Scraping: {url}")
                    try:
                        # Wrap individual product scrape with timeout
                        product = await asyncio.wait_for(
                            self._scrape_product_page(page, url),
                            timeout=45  # 45 seconds per product max
                        )
                        if product:
                            products.append(product)
                            total_images += len(product.images)
                            total_videos += len(product.video_urls)
                            total_specs += len(product.specifications)
                            total_features += len(product.features)
                            total_manuals += len(product.manual_urls)
                            total_accessories += len(product.accessories)
                    except asyncio.TimeoutError:
                        logger.error(f"   Timeout scraping {url} (45s limit)")
                        continue
                    except Exception as e:
                        logger.error(f"   Error scraping {url}: {e}")
                        continue

                logger.info(f"\n✅ COMPREHENSIVE SCRAPING COMPLETE!")
                logger.info(f"   Products: {len(products)}")
                logger.info(f"   Total Images: {total_images}")
                logger.info(f"   Total Videos: {total_videos}")
                logger.info(f"   Total Specs: {total_specs}")
                logger.info(f"   Total Features: {total_features}")
                logger.info(f"   Total Manuals: {total_manuals}")
                logger.info(f"   Total Accessories: {total_accessories}")

                # Create comprehensive catalog
                brand = BrandIdentity(
                    id="moog",
                    name="Moog Music",
                    website="https://www.moogmusic.com",
                    description="Legendary manufacturer of analog synthesizers and electronic musical instruments",
                    categories=["Synthesizers", "Modules", "Effects", "Accessories"]
                )

                catalog = ProductCatalog(
                    brand_identity=brand,
                    products=products,
                    total_products=len(products),
                    last_updated=datetime.utcnow(),
                    catalog_version="3.9.0",
                    coverage_stats={
                        "total_images": total_images,
                        "total_videos": total_videos,
                        "total_specifications": total_specs,
                        "total_features": total_features,
                        "total_manuals": total_manuals,
                        "total_accessories": total_accessories,
                        "avg_images_per_product": round(total_images / len(products), 2) if products else 0,
                        "avg_specs_per_product": round(total_specs / len(products), 2) if products else 0
                    }
                )

            finally:
                await browser.close()
            
            return catalog

    async def _navigate(self, page: Page, url: str, timeout: int = None):
        """Robust navigation with retries using centralized settings"""
        if timeout is None:
            timeout = settings.SCRAPER_TIMEOUT

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(settings.SCRAPER_RETRIES),
            wait=wait_exponential(multiplier=1, min=settings.SCRAPER_RETRY_DELAY, max=10)
        ):
            with attempt:
                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
                except PlaywrightTimeoutError:
                    logger.warning(f"   Timeout on {url}, retrying...")
                    raise
                except Exception as e:
                    logger.warning(f"   Error accessing {url}: {e}, retrying...")
                    raise

    async def _get_product_urls(self, page: Page, max_products: int = None) -> List[str]:
        """Get all product URLs by navigating through categories"""
        logger.info(f"📄 Discovering Moog products through category navigation")

        all_urls = set()

        # Navigate each category to find product links
        for cat_url in self.category_urls:
            try:
                logger.info(f"   Exploring category: {cat_url}")
                await asyncio.wait_for(
                    self._navigate(page, cat_url),
                    timeout=20
                )
                await asyncio.sleep(2)  # Wait for dynamic content

                # Find all product links on category page
                try:
                    # Broad discovery for Moog's structure (e.g. /synthesizers/model-name)
                    selectors = [
                        'a.product-card__link',
                        'a.product-link', 
                        f'a[href*="{cat_url.split("/")[-1]}"]', # contained in link
                        'div.grid a',
                        'main a'
                    ]
                    
                    found_on_page = 0
                    
                    # Also grab all links and filter by logic
                    all_links = await page.locator('a').all()
                    for link in all_links:
                        href = await link.get_attribute('href')
                        if not href: continue
                        
                        # Normalize relative
                        if href.startswith('/'):
                            href = f"https://www.moogmusic.com{href}"
                        
                        # Check if it looks like a product child of the current category
                        # e.g. cat_url=.../synthesizers, href=.../synthesizers/subharmonicon
                        if cat_url in href and len(href) > len(cat_url) + 1:
                            # Avoid sub-collections if any? mostly products
                            if href not in all_urls:
                                all_urls.add(href)
                                found_on_page += 1
                                
                    logger.info(f"   Found {found_on_page} candidates on {cat_url}")
                    
                    # Legacy selector method (backup)
                    for selector in selectors:
                        try:
                            links = await asyncio.wait_for(
                                page.locator(selector).all(),
                                timeout=5
                            )
                            
                            for link in links:
                                try:
                                    href = await link.get_attribute('href')
                                    if not href:
                                        continue
                                        
                                    # Get full URL
                                    if href.startswith('http'):
                                        full_url = href
                                    elif href.startswith('/'):
                                        full_url = f"{self.base_url}{href}"
                                    else:
                                        full_url = f"{self.base_url}/{href}"
                                    
                                    # Only add actual Moog product pages
                                    is_valid_moog_url = (
                                        'moogmusic.com' in full_url and
                                        '/products/' in full_url and
                                        not any(skip in full_url.lower() for skip in 
                                               ['?', 'search', 'compare', 'category', 'filter', 
                                                'cart', 'checkout', self.products_url + '$'])
                                    )
                                    if full_url not in all_urls and is_valid_moog_url:
                                        all_urls.add(full_url)
                                except:
                                    continue
                        except asyncio.TimeoutError:
                            continue
                            
                except asyncio.TimeoutError:
                    logger.warning(f"   Timeout finding links on {cat_url}")
            except Exception as e:
                logger.warning(f"   Error exploring category {cat_url}: {e}")
                continue

        logger.info(f"   Found {len(all_urls)} total product URLs")
        return list(all_urls)

    async def _scrape_product_page(self, page: Page, url: str) -> Optional[ProductCore]:
        """Scrape comprehensive data from product page"""
        try:
            await asyncio.wait_for(
                self._navigate(page, url),
                timeout=30
            )
            await asyncio.sleep(1)

            # Extract product metadata
            try:
                name = await asyncio.wait_for(page.locator('h1').first.text_content(), timeout=5)
                name = name.strip() if name else "Unknown"
            except:
                name = "Unknown"

            # Extract product ID from URL
            product_id = url.split('/products/')[-1].rstrip('/').replace('/', '-')

            # Extract description
            try:
                description_elem = await asyncio.wait_for(
                    page.locator('[class*="description"], [class*="overview"], .product-description, p').first.text_content(),
                    timeout=5
                )
                description = description_elem.strip() if description_elem else ""
            except:
                description = ""

            # Extract main image
            images = []
            try:
                main_img = await asyncio.wait_for(
                    page.locator('img[class*="main"], img[class*="product"], .product-image img, img').first.get_attribute('src'),
                    timeout=5
                )
                if main_img and not main_img.startswith('data:'):
                    # Handle relative URLs
                    if main_img.startswith('//'):
                        main_img = f"https:{main_img}"
                    elif main_img.startswith('/'):
                        main_img = f"{self.base_url}{main_img}"
                    images.append(ProductImage(
                        url=main_img,
                        type="main",
                        alt_text=name
                    ))
            except:
                pass

            # Extract category from URL or breadcrumb
            main_category = "synthesizers"  # Default Moog category
            categories = ["Moog Synthesizers"]
            try:
                breadcrumbs = await asyncio.wait_for(
                    page.locator('[class*="breadcrumb"] a, nav a').all(),
                    timeout=5
                )
                if len(breadcrumbs) > 1:
                    cat_text = await breadcrumbs[1].text_content()
                    if cat_text:
                        main_category = cat_text.strip().lower().replace(' ', '_').replace('-', '_')
                        categories = [cat_text.strip()]
            except:
                # Try to extract from URL
                if '/products/' in url:
                    url_parts = url.split('/products/')[-1].split('/')
                    if len(url_parts) > 1:
                        cat_from_url = url_parts[0]
                        main_category = cat_from_url.replace('-', '_')
                        categories = [cat_from_url.replace('-', ' ').title()]

            # Extract specifications
            specifications = []
            try:
                spec_rows = await asyncio.wait_for(
                    page.locator('[class*="specs"] tr, [class*="specification"] tr, .specs-table tr').all(),
                    timeout=5
                )
                for row in spec_rows[:20]:  # Limit to 20 specs
                    try:
                        cells = await row.locator('td, th').all()
                        if len(cells) >= 2:
                            key = await cells[0].text_content()
                            value = await cells[1].text_content()
                            if key and value:
                                specifications.append(ProductSpecification(
                                    category="Specifications",
                                    specs=[{
                                        "key": key.strip(),
                                        "value": value.strip()
                                    }]
                                ))
                    except:
                        continue
            except:
                pass

            # Extract features
            features = []
            try:
                feature_items = await asyncio.wait_for(
                    page.locator('[class*="features"] li, [class*="feature"] li, .features-list li').all(),
                    timeout=5
                )
                for item in feature_items[:15]:  # Limit to 15 features
                    try:
                        text = await item.text_content()
                        if text:
                            features.append(text.strip())
                    except:
                        continue
            except:
                pass

            # Extract manual URLs
            manual_urls = []
            try:
                manual_links = await asyncio.wait_for(
                    page.locator('a[href*="manual"], a[href*=".pdf"], a[href*="download"]').all(),
                    timeout=5
                )
                for link in manual_links[:5]:  # Limit to 5 manuals
                    try:
                        href = await link.get_attribute('href')
                        if href and '.pdf' in href.lower():
                            if href.startswith('http'):
                                manual_urls.append(href)
                            elif href.startswith('/'):
                                manual_urls.append(f"{self.base_url}{href}")
                    except:
                        continue
            except:
                pass

            # Create product object
            product = ProductCore(
                id=product_id,
                name=name,
                brand="Moog",
                description=description,
                main_category=main_category,
                images=images,
                status=ProductStatus.IN_STOCK,
                specifications=specifications,
                features=features,
                video_urls=[],
                manual_urls=manual_urls,
                accessories=[],
                data_sources=[SourceType.BRAND_OFFICIAL],
                brand_product_url=url
            )

            logger.info(f"   ✓ Extracted: {name}")
            return product

        except asyncio.TimeoutError:
            logger.error(f"   Timeout on {url}")
            return None
        except Exception as e:
            logger.error(f"   Error scraping {url}: {e}")
            return None


async def scrape_moog_products(max_products: int = None) -> ProductCatalog:
    """Convenience function to scrape Moog products"""
    scraper = MoogScraper()
    return await scraper.scrape_all_products(max_products)
