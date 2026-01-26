"""
Enhancements for all brand scrapers to capture:
1. Support articles and knowledge base content
2. White background product images for thumbnails
3. Brand logos (download and store)
4. Main product image selection

This module provides utility functions used by all scrapers.
"""

import asyncio
import logging
from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path
import re
from playwright.async_api import Page
from datetime import datetime
import aiohttp
import os

logger = logging.getLogger(__name__)

# Image storage paths
LOGO_DIR = Path("/workspaces/hsc-jit-v3/frontend/public/data/logos")
PRODUCT_IMAGES_DIR = Path("/workspaces/hsc-jit-v3/frontend/public/data/product_images")

# Ensure directories exist
LOGO_DIR.mkdir(parents=True, exist_ok=True)
PRODUCT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


class SupportArticleExtractor:
    """Extract support articles and knowledge base content for all brands"""

    @staticmethod
    async def extract_roland_support_articles(page: Page, product_url: str, product_name: str) -> Dict:
        """Extract support articles from Roland's support portal"""
        
        support_data = {
            "support_articles": [],
            "knowledge_base_links": [],
            "faq_links": [],
            "documentation_links": [],
            "video_tutorials": []
        }

        try:
            # Try to find support section on product page
            support_links = []
            
            # Look for support tab or section
            support_selectors = [
                'a[href*="support"]',
                'a[href*="help"]',
                'a[href*="faq"]',
                'a[href*="learn"]',
                'a[href*="guides"]',
                'a[href*="manual"]'
            ]
            
            for selector in support_selectors:
                try:
                    elements = await page.locator(selector).all()
                    for elem in elements:
                        href = await elem.get_attribute('href')
                        text = await elem.inner_text()
                        if href and text:
                            support_links.append({
                                'url': href,
                                'title': text.strip(),
                                'type': selector
                            })
                except:
                    continue
            
            # Navigate to support pages and extract content
            for link in support_links[:5]:  # Limit to 5 to avoid too many navigations
                try:
                    href = link['url']
                    
                    # Make absolute URL
                    if href.startswith('/'):
                        href = f"https://www.roland.com{href}"
                    elif not href.startswith('http'):
                        href = f"https://www.roland.com/{href}"
                    
                    # Categorize by URL pattern
                    if 'faq' in href.lower():
                        support_data['faq_links'].append({'url': href, 'title': link['title']})
                    elif 'knowledge' in href.lower() or 'articles' in href.lower():
                        support_data['knowledge_base_links'].append({'url': href, 'title': link['title']})
                    elif 'manual' in href.lower() or 'guide' in href.lower():
                        support_data['documentation_links'].append({'url': href, 'title': link['title']})
                    elif 'video' in href.lower() or 'tutorial' in href.lower():
                        support_data['video_tutorials'].append({'url': href, 'title': link['title']})
                    else:
                        support_data['support_articles'].append({'url': href, 'title': link['title']})
                        
                except Exception as e:
                    logger.debug(f"Error processing support link: {e}")
                    continue
            
        except Exception as e:
            logger.warning(f"Error extracting support articles for {product_name}: {e}")
        
        return support_data

    @staticmethod
    async def extract_boss_support_articles(page: Page, product_url: str, product_name: str) -> Dict:
        """Extract support articles from Boss's support portal"""
        
        support_data = {
            "support_articles": [],
            "knowledge_base_links": [],
            "faq_links": [],
            "documentation_links": [],
            "video_tutorials": []
        }

        try:
            # Boss support URLs typically follow pattern: /support/, /manuals/, /downloads/
            
            # Look for support/help links
            support_selectors = [
                'a[href*="support"]',
                'a[href*="manual"]',
                'a[href*="download"]',
                'a[href*="faq"]',
                'a[href*="help"]',
                'a[href*="guide"]'
            ]
            
            for selector in support_selectors:
                try:
                    elements = await page.locator(selector).all()
                    for elem in elements[:10]:  # Limit per selector
                        href = await elem.get_attribute('href')
                        text = await elem.inner_text()
                        if href and text:
                            # Make absolute
                            if href.startswith('/'):
                                href = f"https://www.boss.info{href}"
                            elif not href.startswith('http'):
                                href = f"https://www.boss.info/{href}"
                            
                            # Categorize
                            if 'faq' in href.lower():
                                support_data['faq_links'].append({'url': href, 'title': text.strip()})
                            elif 'manual' in href.lower() or 'download' in href.lower():
                                support_data['documentation_links'].append({'url': href, 'title': text.strip()})
                            else:
                                support_data['support_articles'].append({'url': href, 'title': text.strip()})
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error extracting Boss support articles: {e}")
        
        return support_data

    @staticmethod
    async def extract_nord_support_articles(page: Page, product_url: str, product_name: str) -> Dict:
        """Extract support articles from Nord's website"""
        
        support_data = {
            "support_articles": [],
            "knowledge_base_links": [],
            "faq_links": [],
            "documentation_links": [],
            "video_tutorials": []
        }

        try:
            # Nord typically has downloads, manuals, OS updates, patches
            
            support_selectors = [
                'a[href*="download"]',
                'a[href*="manual"]',
                'a[href*="support"]',
                'a[href*="patch"]',
                'a[href*="update"]',
                'a[href*="OS"]'
            ]
            
            for selector in support_selectors:
                try:
                    elements = await page.locator(selector).all()
                    for elem in elements[:10]:
                        href = await elem.get_attribute('href')
                        text = await elem.inner_text()
                        if href and text:
                            # Make absolute
                            if href.startswith('/'):
                                href = f"https://www.nordkeyboards.com{href}"
                            elif not href.startswith('http'):
                                href = f"https://www.nordkeyboards.com/{href}"
                            
                            # Categorize
                            if 'manual' in href.lower():
                                support_data['documentation_links'].append({'url': href, 'title': text.strip()})
                            elif 'patch' in href.lower() or 'update' in href.lower() or 'os' in href.lower():
                                support_data['knowledge_base_links'].append({'url': href, 'title': text.strip()})
                            else:
                                support_data['support_articles'].append({'url': href, 'title': text.strip()})
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error extracting Nord support articles: {e}")
        
        return support_data

    @staticmethod
    async def extract_moog_support_articles(page: Page, product_url: str, product_name: str) -> Dict:
        """Extract support articles from Moog's website"""
        
        support_data = {
            "support_articles": [],
            "knowledge_base_links": [],
            "faq_links": [],
            "documentation_links": [],
            "video_tutorials": []
        }

        try:
            # Moog has support portal with manuals, patches, firmware updates
            
            support_selectors = [
                'a[href*="support"]',
                'a[href*="manual"]',
                'a[href*="firmware"]',
                'a[href*="patch"]',
                'a[href*="download"]',
                'a[href*="resources"]'
            ]
            
            for selector in support_selectors:
                try:
                    elements = await page.locator(selector).all()
                    for elem in elements[:10]:
                        href = await elem.get_attribute('href')
                        text = await elem.inner_text()
                        if href and text:
                            # Make absolute
                            if href.startswith('/'):
                                href = f"https://www.moogmusic.com{href}"
                            elif not href.startswith('http'):
                                href = f"https://www.moogmusic.com/{href}"
                            
                            # Categorize
                            if 'manual' in href.lower() or 'firmware' in href.lower():
                                support_data['documentation_links'].append({'url': href, 'title': text.strip()})
                            elif 'patch' in href.lower():
                                support_data['knowledge_base_links'].append({'url': href, 'title': text.strip()})
                            else:
                                support_data['support_articles'].append({'url': href, 'title': text.strip()})
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error extracting Moog support articles: {e}")
        
        return support_data


class ProductImageEnhancer:
    """Identify and tag white background product images for thumbnails"""

    @staticmethod
    async def identify_white_background_image(page: Page, images_found: List[Dict]) -> Optional[Dict]:
        """
        Identify white background product image (best for thumbnails/navigator)
        
        Returns the image that best represents the product on white background
        """
        
        try:
            # Heuristics for finding white background images:
            # 1. Images with "white" in filename
            # 2. Images from product galleries (usually white bg)
            # 3. Main product shot (typically white bg)
            
            best_image = None
            
            for img in images_found:
                url = img.get('url', '')
                alt_text = img.get('alt_text', '').lower()
                img_type = img.get('type', '')
                
                # Check filename for white/product indicators
                if any(indicator in url.lower() for indicator in ['white', 'product', 'main', 'hero', 'poster']):
                    if not any(skip in url.lower() for skip in ['icon', 'logo', 'button']):
                        # Prioritize main type
                        if img_type == 'main':
                            return img
                        if not best_image:
                            best_image = img
            
            # If no white bg found, return main image
            if best_image:
                return best_image
            
            # Fallback: use first main image
            for img in images_found:
                if img.get('type') == 'main':
                    return img
            
            # Last resort: first image of any type
            return images_found[0] if images_found else None
            
        except Exception as e:
            logger.debug(f"Error identifying white background image: {e}")
            return images_found[0] if images_found else None

    @staticmethod
    def tag_images_with_background_info(images: List[Dict]) -> List[Dict]:
        """Tag images with background type info for filtering"""
        
        for img in images:
            img['background_type'] = 'unknown'
            
            url_lower = img.get('url', '').lower()
            filename_lower = url_lower.split('/')[-1]
            
            # Try to identify background from filename/URL
            if any(x in filename_lower for x in ['white', 'clean', 'flat', 'bg']):
                img['background_type'] = 'white'
            elif any(x in filename_lower for x in ['black', 'dark']):
                img['background_type'] = 'dark'
            elif any(x in filename_lower for x in ['lifestyle', 'scene', 'environment']):
                img['background_type'] = 'lifestyle'
            elif any(x in filename_lower for x in ['studio', 'product']):
                img['background_type'] = 'studio'
        
        return images


class BrandLogoDownloader:
    """Download and store brand logos"""

    @staticmethod
    async def download_brand_logo(brand_name: str, logo_url: str) -> Optional[str]:
        """
        Download brand logo and save to system
        
        Returns: Path to saved logo file (relative to public/data)
        """
        
        if not logo_url:
            return None
        
        try:
            # Make absolute URL if needed
            if logo_url.startswith('/'):
                # Need to determine base URL from brand
                base_urls = {
                    'roland': 'https://www.roland.com',
                    'boss': 'https://www.boss.info',
                    'nord': 'https://www.nordkeyboards.com',
                    'moog': 'https://www.moogmusic.com'
                }
                base_url = base_urls.get(brand_name.lower(), '')
                if base_url:
                    logo_url = f"{base_url}{logo_url}"
                else:
                    return None
            
            if not logo_url.startswith('http'):
                return None
            
            # Determine filename
            filename = f"{brand_name.lower()}_logo.{logo_url.split('.')[-1].split('?')[0]}"
            filepath = LOGO_DIR / filename
            
            # Download logo
            async with aiohttp.ClientSession() as session:
                async with session.get(logo_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        filepath.write_bytes(content)
                        
                        logger.info(f"✓ Downloaded {brand_name} logo: {filename}")
                        return f"logos/{filename}"
        
        except Exception as e:
            logger.warning(f"Error downloading {brand_name} logo from {logo_url}: {e}")
        
        return None

    @staticmethod
    async def scrape_brand_logo(page: Page, brand_name: str) -> Optional[str]:
        """
        Scrape brand logo from brand homepage
        
        Returns: Path to downloaded logo
        """
        
        try:
            # Common logo selectors
            logo_selectors = [
                'img[src*="logo"]',
                'img[alt*="logo"]',
                'img[class*="logo"]',
                'header img',
                '.navbar img',
                '.header img'
            ]
            
            logo_url = None
            
            for selector in logo_selectors:
                try:
                    logo_elem = page.locator(selector).first
                    if await logo_elem.count() > 0:
                        logo_url = await logo_elem.get_attribute('src')
                        if logo_url:
                            break
                except:
                    continue
            
            if logo_url:
                return await BrandLogoDownloader.download_brand_logo(brand_name, logo_url)
            
        except Exception as e:
            logger.debug(f"Error scraping {brand_name} logo: {e}")
        
        return None
