"""
Nord-Specific Scraper - COMPREHENSIVE DATA EXTRACTION
======================================================

Nord Keyboards (Clavia DMI AB) - Premium keyboard and synthesizer manufacturer.
Website: https://www.nordkeyboards.com

GOAL: Extract ALL available data from Nord website for JIT RAG system
----------------------------------------------------------------------
✓ Product metadata (name, model, SKU, categories)
✓ Full descriptions (marketing copy, long-form content)
✓ ALL images and media (main, gallery, technical diagrams, videos)
✓ Complete specifications (all spec tables, technical details)
✓ Features and benefits (bullet points, marketing content)
✓ Manuals and documentation (PDFs, quick start guides, reference docs)
✓ Support articles and knowledge base (OS updates, patches)
✓ Sound libraries and patches (Nord's famous sound banks)
✓ Support resources (downloads, software, OS updates)
✓ White background product images for thumbnails
✓ Brand logo downloads
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


class NordScraper:
    """Specialized scraper for Nord Keyboards website"""

    def __init__(self):
        self.base_url = "https://www.nordkeyboards.com"
        self.products_url = f"{self.base_url}/products"
        
        # Nord main categories (based on brand_recipes.json)
        self.category_urls = [
            # Main products page
            "https://www.nordkeyboards.com/products",
            # Specific product families
            "https://www.nordkeyboards.com/products/nord-stage",
            "https://www.nordkeyboards.com/products/nord-piano",
            "https://www.nordkeyboards.com/products/nord-grand",
            "https://www.nordkeyboards.com/products/nord-electro",
            "https://www.nordkeyboards.com/products/nord-lead",
            "https://www.nordkeyboards.com/products/nord-wave",
            "https://www.nordkeyboards.com/products/nord-drum",
        ]
        
        # Meta keywords from brand_recipes.json
        self.meta_keywords = ["Piano", "Organ", "Synth", "Drum", "Stage", "Grand", "Electro", "Lead", "Wave"]

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
        Generic implementation for Nord.
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
                     src = f"https://www.nordkeyboards.com{src}"
                 images.append({"url": src, "alt_text": alt})
                 
        videos = []
        iframes = await page.locator('iframe').all()
        for frame in iframes:
            src = await frame.get_attribute('src')
            if src: videos.append(src)
            
        # 4. Description Blocks
        desc_text = ""
        try:
             # Nord specific content container
             main_content = await page.evaluate("() => document.querySelector('.region-content') ? document.querySelector('.region-content').innerText : document.body.innerText")
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
            "brand": "Nord",
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
        Scrape ALL Nord products with COMPREHENSIVE data extraction

        Args:
            max_products: Maximum products to scrape (None = scrape ALL products)

        Returns:
            ProductCatalog with comprehensive product data ready for JIT RAG
        """
        logger.info(
            f"🎹 Starting COMPREHENSIVE Nord scrape (max: {'ALL' if max_products is None else max_products})")
        logger.info(f"   Goal: Extract ALL available data for JIT RAG system")
        logger.info(f"   Note: Nord is known for exceptional product pages with rich specs")

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
                    id="nord",
                    name="Nord Keyboards",
                    website="https://www.nordkeyboards.com",
                    description="Premium manufacturer of stage keyboards, pianos, and synthesizers with iconic red design",
                    categories=["Stage Keyboards", "Pianos", "Synthesizers", "Organs", "Drum Machines"]
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
        logger.info(f"📄 Discovering Nord products through category navigation")

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
                    # Try multiple selectors for Nord website
                    selectors = [
                        'a[href*="/products/"]',
                        'a[href*="/nord-"]',
                        'a.product-link',
                        'a[class*="product"]',
                        'div.product a',
                        '.product-grid a',
                        '.product-list a'
                    ]
                    
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
                                    
                                    # Only add actual Nord product pages
                                    # Must have one of the meta keywords in URL
                                    has_keyword = any(keyword.lower() in full_url.lower() for keyword in self.meta_keywords)
                                    is_valid_nord_url = (
                                        'nordkeyboards.com' in full_url and
                                        '/products/' in full_url and
                                        has_keyword and
                                        not any(skip in full_url.lower() for skip in 
                                               ['?', 'search', 'compare', 'category', 'filter', 
                                                'cart', 'checkout', 'accessories'])
                                    )
                                    if full_url not in all_urls and is_valid_nord_url:
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
        """Scrape comprehensive data from product page (ENHANCED FOR COMPLETE DATA)"""
        try:
            await asyncio.wait_for(
                self._navigate(page, url),
                timeout=30
            )
            await asyncio.sleep(1)

            # ============================================================
            # 1. EXTRACT PRODUCT NAME
            # ============================================================
            try:
                name = await asyncio.wait_for(page.locator('h1').first.text_content(), timeout=5)
                name = name.strip() if name else "Unknown"
            except:
                name = "Unknown"

            product_id = url.split('/products/')[-1].rstrip('/').replace('/', '-')
            logger.info(f"   Extracting: {name} ({product_id})")

            # ============================================================
            # 2. EXTRACT FULL DESCRIPTION (ALL TEXT CONTENT)
            # ============================================================
            description = ""
            short_description = ""
            
            # Try meta description first
            try:
                meta_desc = await page.locator('meta[name="description"]').get_attribute('content')
                if meta_desc:
                    short_description = meta_desc[:200]
            except:
                pass

            # Collect ALL description paragraphs
            description_parts = []
            desc_selectors = [
                '.product-description',
                '.description',
                '[class*="description"]',
                '[class*="intro"]',
                '[class*="overview"]',
                'article p',
                'main p',
                '.content p'
            ]

            for selector in desc_selectors:
                try:
                    elements = await asyncio.wait_for(page.locator(selector).all(), timeout=5)
                    for elem in elements:
                        try:
                            text = await asyncio.wait_for(elem.inner_text(), timeout=2)
                            if text and len(text.strip()) > 20 and text not in description_parts:
                                description_parts.append(text.strip())
                        except:
                            continue
                except asyncio.TimeoutError:
                    continue

            description = "\n\n".join(description_parts) if description_parts else (short_description or name)

            # ============================================================
            # 3. EXTRACT ALL IMAGES & MEDIA (COMPLETE GALLERY)
            # ============================================================
            images = []
            seen_urls: Set[str] = set()

            # Try multiple image selectors
            img_selectors = [
                'img[src*="product"]',
                'img[src*="nord"]',
                'img[alt*="Nord"]',
                '.product-image img',
                '.gallery img',
                '.image-gallery img',
                '[class*="image"] img',
                '[class*="gallery"] img',
                'main img',
                'article img'
            ]

            for selector in img_selectors:
                try:
                    img_elements = await asyncio.wait_for(page.locator(selector).all(), timeout=5)
                    for img_elem in img_elements:
                        try:
                            src = await asyncio.wait_for(img_elem.get_attribute('src'), timeout=2)
                            alt = await asyncio.wait_for(img_elem.get_attribute('alt'), timeout=2) or name

                            if not src or src in seen_urls:
                                continue

                            # Skip icons, logos, tiny images
                            if any(skip in src.lower() for skip in ['icon', 'logo', 'button', 'banner', 'sprite']):
                                continue
                            
                            # Skip data URIs
                            if src.startswith('data:'):
                                continue

                            # Make absolute URL
                            if src.startswith('//'):
                                src = f"https:{src}"
                            elif src.startswith('/'):
                                src = f"{self.base_url}{src}"
                            elif not src.startswith('http'):
                                continue

                            # Determine image type
                            img_type = "main"
                            if 'gallery' in src.lower() or len(images) > 0:
                                img_type = "gallery"
                            if 'spec' in src.lower() or 'diagram' in src.lower():
                                img_type = "technical"

                            images.append(ProductImage(
                                url=src,
                                type=img_type,
                                alt_text=alt
                            ))
                            seen_urls.add(src)
                        except (asyncio.TimeoutError, Exception):
                            continue
                except asyncio.TimeoutError:
                    continue

            # ============================================================
            # 4. EXTRACT ALL VIDEOS
            # ============================================================
            video_urls = []
            video_selectors = [
                'iframe[src*="youtube"]',
                'iframe[src*="vimeo"]',
                'video source',
                'a[href*="youtube"]',
                'a[href*="vimeo"]',
                '[class*="video"]'
            ]

            for selector in video_selectors:
                try:
                    elements = await asyncio.wait_for(page.locator(selector).all(), timeout=5)
                    for elem in elements:
                        try:
                            video_url = await asyncio.wait_for(elem.get_attribute('src'), timeout=2) or \
                                       await asyncio.wait_for(elem.get_attribute('href'), timeout=2)
                            if video_url and video_url not in video_urls:
                                if not video_url.startswith('http'):
                                    video_url = f"https:{video_url}" if video_url.startswith('//') else f"{self.base_url}{video_url}"
                                video_urls.append(video_url)
                        except (asyncio.TimeoutError, Exception):
                            continue
                except asyncio.TimeoutError:
                    continue

            # ============================================================
            # 5. EXTRACT ALL SPECIFICATIONS (COMPLETE TABLES)
            # ============================================================
            specifications = []

            # Look for specification tables
            try:
                tables = await asyncio.wait_for(page.locator('table').all(), timeout=5)
            except asyncio.TimeoutError:
                tables = []
            
            for table in tables:
                try:
                    rows = await table.locator('tr').all()
                    for row in rows:
                        cells = await row.locator('td, th').all()
                        if len(cells) >= 2:
                            key = await cells[0].inner_text()
                            value = await cells[1].inner_text()
                            if key and value and len(key.strip()) > 0:
                                # Determine spec category
                                spec_category = "General"
                                key_lower = key.lower()
                                if any(word in key_lower for word in ['dimension', 'size', 'width', 'height', 'depth']):
                                    spec_category = "Dimensions"
                                elif any(word in key_lower for word in ['weight', 'mass']):
                                    spec_category = "Weight"
                                elif any(word in key_lower for word in ['power', 'voltage', 'current']):
                                    spec_category = "Power"
                                elif any(word in key_lower for word in ['audio', 'frequency', 'output', 'input', 'sound', 'polyphony']):
                                    spec_category = "Audio"
                                elif any(word in key_lower for word in ['keyboard', 'keys', 'velocity']):
                                    spec_category = "Keyboard"

                                specifications.append(ProductSpecification(
                                    category=spec_category,
                                    key=key.strip(),
                                    value=value.strip(),
                                    source=SourceType.BRAND_OFFICIAL
                                ))
                except:
                    continue

            # Also look for dl/dt/dd specification lists
            try:
                dl_elements = await page.locator('dl').all()
                for dl in dl_elements:
                    try:
                        dt_elements = await dl.locator('dt').all()
                        dd_elements = await dl.locator('dd').all()
                        for dt, dd in zip(dt_elements, dd_elements):
                            key = await dt.inner_text()
                            value = await dd.inner_text()
                            if key and value:
                                specifications.append(ProductSpecification(
                                    category="General",
                                    key=key.strip(),
                                    value=value.strip(),
                                    source=SourceType.BRAND_OFFICIAL
                                ))
                    except:
                        continue
            except:
                pass

            # ============================================================
            # 6. EXTRACT FEATURES LIST
            # ============================================================
            features = []
            feature_selectors = [
                'ul li',
                '.features li',
                '.feature-list li',
                '[class*="feature"] li'
            ]

            for selector in feature_selectors:
                try:
                    elements = await asyncio.wait_for(page.locator(selector).all(), timeout=5)
                    for elem in elements[:30]:  # Limit to reasonable number
                        try:
                            text = await elem.inner_text()
                            if text and len(text.strip()) > 10 and text not in features:
                                features.append(text.strip())
                        except:
                            continue
                except:
                    continue

            # ============================================================
            # 7. EXTRACT MANUALS & DOCUMENTATION
            # ============================================================
            manual_urls = []
            download_selectors = [
                'a[href$=".pdf"]',
                'a[href*="manual"]',
                'a[href*="download"]',
                'a[href*="guide"]',
                'a[href*="documentation"]',
                'a[href*="user-guide"]'
            ]

            for selector in download_selectors:
                try:
                    elements = await asyncio.wait_for(page.locator(selector).all(), timeout=5)
                    for elem in elements:
                        try:
                            href = await elem.get_attribute('href')
                            if href and href not in manual_urls:
                                if href.startswith('/'):
                                    href = f"{self.base_url}{href}"
                                elif not href.startswith('http'):
                                    href = f"{self.base_url}/{href}"
                                manual_urls.append(href)
                        except:
                            continue
                except:
                    continue

            # ============================================================
            # 8. DETERMINE HIERARCHY (BREADCRUMBS & CATEGORIES)
            # ============================================================
            main_category = "Keyboards"
            categories = ["Nord Keyboards"]
            
            # Determine category from URL and keywords
            for keyword in self.meta_keywords:
                if keyword.lower() in url.lower() or keyword.lower() in name.lower():
                    main_category = keyword
                    categories = [f"Nord {keyword}"]
                    break
            
            try:
                breadcrumbs = await asyncio.wait_for(
                    page.locator('[class*="breadcrumb"] a, nav[aria-label="breadcrumb"] li, .breadcrumb li').all(),
                    timeout=5
                )
                if len(breadcrumbs) > 1:
                    cat_text = await breadcrumbs[1].text_content()
                    if cat_text:
                        main_category = cat_text.strip()
                        categories = [cat_text.strip()]
            except:
                pass

            # Create product object
            product = ProductCore(
                id=f"nord-{product_id}",
                name=name,
                brand="Nord",
                description=description,
                main_category=main_category,
                images=images,
                status=ProductStatus.IN_STOCK,
                specifications=specifications,
                features=features,
                video_urls=video_urls,
                manual_urls=manual_urls,
                accessories=[],
                data_sources=[SourceType.BRAND_OFFICIAL],
                brand_product_url=url
            )

            logger.info(f"   ✓ Extracted: {name} | {len(images)} images, {len(video_urls)} videos, {len(specifications)} specs, {len(manual_urls)} manuals")
            return product

        except asyncio.TimeoutError:
            logger.error(f"   Timeout on {url}")
            return None
        except Exception as e:
            logger.error(f"   Error scraping {url}: {e}")
            return None


async def scrape_nord_products(max_products: int = None) -> ProductCatalog:
    """Convenience function to scrape Nord products"""
    scraper = NordScraper()
    return await scraper.scrape_all_products(max_products)
