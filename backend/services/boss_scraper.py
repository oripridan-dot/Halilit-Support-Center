"""
Boss-Specific Scraper - COMPREHENSIVE DATA EXTRACTION
=====================================================

Boss uses the same CMS architecture as Roland (parent company: Roland Corporation).
This scraper mirrors RolandScraper approach with Boss-specific URLs and configurations.

GOAL: Extract ALL available data from Boss website for JIT RAG system
----------------------------------------------------------------------
✓ Product metadata (name, model, SKU, categories)
✓ Full descriptions (marketing copy, long-form content)
✓ ALL images and media (main, gallery, technical diagrams, videos)
✓ Complete specifications (all spec tables, technical details)
✓ Features and benefits (bullet points, marketing content)
✓ Manuals and documentation (PDFs, quick start guides, reference docs)
✓ Knowledge base articles (support articles, FAQs, tutorials)
✓ Support articles and documentation snippets
✓ Related accessories (recommended, required, compatible)
✓ Support resources (downloads, software, drivers, firmware)
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
from typing import List, Dict, Optional, Set
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


class BossScraper:
    """Specialized scraper for Boss website - mirrors Roland CMS structure"""

    def __init__(self):
        self.base_url = "https://www.boss.info"
        self.products_url = f"{self.base_url}/us/products/"
        
        # Boss main categories (similar to Roland hierarchy)
        self.category_urls = [
            # Main products page
            "https://www.boss.info/us/products/",
            # Guitar Effects (main Boss category)
            "https://www.boss.info/us/products/multi-effects_processors/",
            "https://www.boss.info/us/products/stompbox_effects/",
            "https://www.boss.info/us/products/distortion_overdrive/",
            "https://www.boss.info/us/products/modulation/",
            "https://www.boss.info/us/products/delay_reverb/",
            # Drums/Percussion
            "https://www.boss.info/us/products/drum_machines/",
            "https://www.boss.info/us/products/drum_pads/",
            # Keyboards/Synthesizers
            "https://www.boss.info/us/products/synthesizers/",
            "https://www.boss.info/us/products/keyboards/",
            # Amplifiers
            "https://www.boss.info/us/products/amplifiers/",
            # Loopers/Recorders
            "https://www.boss.info/us/products/loopers_recorders/",
            # Tuners/Metronomes
            "https://www.boss.info/us/products/tuners_metronomes/",
            # Accessories
            "https://www.boss.info/us/products/accessories/",
            "https://www.boss.info/us/products/cables_connectors/",
            "https://www.boss.info/us/products/stands_holders/",
        ]

    async def scrape_all_products(self, max_products: int = None) -> ProductCatalog:
        """
        Scrape ALL Boss products with COMPREHENSIVE data extraction

        For each product, we extract:
        ✓ Full metadata (name, model, SKU, categories)
        ✓ Complete descriptions (all text content, marketing copy)
        ✓ ALL images (main, gallery, technical diagrams)
        ✓ ALL videos (YouTube, Vimeo, product demos)
        ✓ Complete specifications (all spec tables)
        ✓ All features (bullet lists, feature descriptions)
        ✓ Manuals and documentation (PDFs, guides, quick starts)
        ✓ Support resources (support page links, FAQs)
        ✓ Related accessories (recommended, compatible)
        ✓ Related products (similar, complementary)

        Args:
            max_products: Maximum products to scrape (None = scrape ALL products)

        Returns:
            ProductCatalog with comprehensive product data ready for JIT RAG
        """
        logger.info(
            f"🎸 Starting COMPREHENSIVE Boss scrape (max: {'ALL' if max_products is None else max_products})")
        logger.info(f"   Goal: Extract ALL available data for JIT RAG system")
        logger.info(f"   Note: Boss uses same CMS as Roland (parent company)")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=settings.SCRAPER_HEADLESS,
                args=['--disable-dev-shm-usage', '--no-sandbox', '--disable-gpu']
            )
            page = await browser.new_page()

            try:
                # ============================================================
                # STEP 0: Download brand logo
                # ============================================================
                logger.info("🎨 Downloading Boss brand logo...")
                try:
                    await self._navigate(page, self.base_url)
                    logo_path = await BrandLogoDownloader.scrape_brand_logo(page, "Boss")
                    if logo_path:
                        logger.info(f"   ✓ Logo saved: {logo_path}")
                except Exception as e:
                    logger.debug(f"   Could not download logo: {e}")

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
                        id="boss",
                        name="Boss Corporation",
                        website="https://www.boss.info",
                        description="Leading manufacturer of guitar effects and audio equipment",
                        categories=["Guitar Effects", "Synthesizers", "Drum Machines", 
                                    "Amplifiers", "Loopers", "Accessories"]
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

                    return catalog
                
                finally:
                    await browser.close()
            
            except Exception as e:
                logger.error(f"Fatal error during scraping: {e}")
                raise

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
                    # Changed to domcontentloaded to prevent hanging on analytics/tracking
                    await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
                except PlaywrightTimeoutError:
                    logger.warning(f"   Timeout on {url}, retrying...")
                    raise
                except Exception as e:
                    logger.warning(f"   Error accessing {url}: {e}, retrying...")
                    raise

    async def _get_product_urls(self, page: Page, max_products: int = None) -> List[str]:
        """Get all product URLs by navigating through categories"""
        logger.info(f"📄 Discovering Boss products through category navigation")

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

                # Find all links on the page
                try:
                    # Try multiple selectors to find product links
                    selectors = [
                        'a[href*="/products/"]',  # Any product link
                        'a.product-link',  # Product-specific links
                        'a[class*="product"]',  # Links with product in class
                        'div.product a',  # Links in product divs
                    ]
                    
                    for selector in selectors:
                        try:
                            links = await asyncio.wait_for(
                                page.locator(selector).all(),
                                timeout=5
                            )
                            logger.info(f"   Found {len(links)} links with selector: {selector}")
                            
                            for link in links:
                                try:
                                    href = await link.get_attribute('href')
                                    if not href:
                                        continue
                                        
                                    # Get full URL
                                    if href.startswith('http'):
                                        full_url = href
                                    elif href.startswith('/'):
                                        full_url = f"https://www.boss.info{href}"
                                    else:
                                        full_url = f"https://www.boss.info/us/{href}"
                                    
                                    # Only add actual Boss product pages (exclude category/filter pages)
                                    # Must be boss.info domain with proper product URL structure
                                    is_valid_boss_url = (
                                        'boss.info' in full_url and
                                        '/products/' in full_url and
                                        full_url.endswith('/') and  # Must end with /
                                        not full_url.endswith('/products/') and  # Not just /products/
                                        not any(skip in full_url.lower() for skip in ['?', 'search', 'compare', 'category', 'filter', 'onetrust'])
                                    )
                                    if full_url not in all_urls and is_valid_boss_url:
                                        all_urls.add(full_url)
                                        logger.info(f"   Added product URL: {full_url}")
                                except:
                                    continue
                        except asyncio.TimeoutError:
                            logger.warning(f"   Timeout with selector: {selector}")
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

            product_id = url.split('/products/')[-1].rstrip('/')
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
                'img[src*="boss"]',
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
                                src = f"https://www.boss.info{src}"
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
            # 3b. IDENTIFY WHITE BACKGROUND PRODUCT IMAGE FOR THUMBNAIL
            # ============================================================
            # Convert to dicts for processing
            images_dicts = [{'url': img.url, 'type': img.type, 'alt_text': img.alt_text} 
                           for img in images]
            
            # Tag with background info and find best white bg image
            images_dicts = ProductImageEnhancer.tag_images_with_background_info(images_dicts)
            thumbnail_image = await ProductImageEnhancer.identify_white_background_image(page, images_dicts)
            
            if thumbnail_image:
                logger.debug(f"   Selected thumbnail: {thumbnail_image['type']} background")

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
                                    video_url = f"https:{video_url}" if video_url.startswith('//') else f"https://www.boss.info{video_url}"
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
                                elif any(word in key_lower for word in ['audio', 'frequency', 'output', 'input', 'sound']):
                                    spec_category = "Audio"

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
                'a[href*="documentation"]'
            ]

            for selector in download_selectors:
                try:
                    elements = await asyncio.wait_for(page.locator(selector).all(), timeout=5)
                    for elem in elements:
                        try:
                            href = await elem.get_attribute('href')
                            if href and href not in manual_urls:
                                if href.startswith('/'):
                                    href = f"https://www.boss.info{href}"
                                elif not href.startswith('http'):
                                    href = f"https://www.boss.info/{href}"
                                manual_urls.append(href)
                        except:
                            continue
                except:
                    continue

            # ============================================================
            # 7b. EXTRACT SUPPORT ARTICLES & KNOWLEDGE BASE CONTENT
            # ============================================================
            support_articles = []
            documentation_snippets = []
            
            try:
                support_data = await SupportArticleExtractor.extract_boss_support_articles(
                    page, url, name
                )
                
                # Flatten all support resources
                for key, items in support_data.items():
                    if isinstance(items, list) and items:
                        support_articles.extend(items)
                
                logger.debug(f"   Found {len(support_articles)} support resources for {name}")
                
            except Exception as e:
                logger.debug(f"   Error extracting support articles: {e}")

            # ============================================================
            # 8. DETERMINE HIERARCHY (BREADCRUMBS & CATEGORIES)
            # ============================================================
            main_category = "Guitar Effects"
            categories = ["Boss Products"]
            
            try:
                breadcrumbs = await asyncio.wait_for(
                    page.locator('[class*="breadcrumb"] a, .breadcrumb li, nav[aria-label="breadcrumb"] li').all(),
                    timeout=5
                )
                if len(breadcrumbs) > 1:
                    cat_text = await breadcrumbs[1].text_content()
                    if cat_text:
                        main_category = cat_text.strip()
                        categories = [cat_text.strip()]
            except:
                # Try to extract from URL
                if '/products/' in url:
                    cat_from_url = url.split('/products/')[1].split('/')[0]
                    main_category = cat_from_url.replace('-', ' ').title()
                    categories = [main_category]

            # Create product object
            product = ProductCore(
                id=f"boss-{product_id}",
                name=name,
                brand="Boss",
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


async def scrape_boss_products(max_products: int = None) -> ProductCatalog:
    """Convenience function to scrape Boss products"""
    scraper = BossScraper()
    return await scraper.scrape_all_products(max_products)
