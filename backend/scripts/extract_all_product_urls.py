#!/usr/bin/env python3
"""
HALILIT PRODUCT URL EXTRACTOR using Playwright

Extracts ALL product URLs from Halilit.com using a real browser to bypass anti-bot protection.

Strategy:
1. Navigate to brands page (/pages/4367)
2. Extract all brand group links
3. For each brand, extract product count and all product URLs across all pages
4. Save results to files

Usage:
    python3 extract_all_product_urls.py
"""

import asyncio
import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Any
from playwright.async_api import async_playwright, Page, Browser

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
HALILIT_BASE = "https://www.halilit.com"
BRANDS_PAGE_URL = f"{HALILIT_BASE}/pages/4367"
BRAND_GROUP_PREFIX = "/g/5193"
OUTPUT_DIR = Path(__file__).parent.parent / "data"
PRODUCT_URLS_FILE = OUTPUT_DIR / "all_product_urls.txt"
BRAND_DATA_FILE = OUTPUT_DIR / "brand_discovery.json"

# Rate limiting
PAGE_LOAD_TIMEOUT = 30000  # 30 seconds
NAVIGATION_DELAY = 1000  # 1 second between navigations


class HalilitBrowserScraper:
    """Scrapes Halilit.com using Playwright to bypass anti-bot protection."""
    
    def __init__(self):
        self.browser: Browser = None
        self.page: Page = None
        self.all_product_urls: set = set()
        self.brand_data: List[Dict[str, Any]] = []
    
    async def initialize(self):
        """Initialize Playwright browser."""
        logger.info("🚀 Initializing Playwright browser...")
        playwright = await async_playwright().start()
        
        # Launch browser with realistic settings
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        # Create context with realistic user agent
        context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='he-IL',
            timezone_id='Asia/Jerusalem',
        )
        
        self.page = await context.new_page()
        
        # Set extra headers
        await self.page.set_extra_http_headers({
            'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })
        
        logger.info("✅ Browser initialized")
    
    async def close(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()
            logger.info("🔒 Browser closed")
    
    async def navigate_with_retry(self, url: str, retries: int = 3, check_antibot: bool = True) -> bool:
        """Navigate to URL with retry logic and anti-bot handling."""
        for attempt in range(retries):
            try:
                logger.info(f"🌐 Navigating to: {url}")
                response = await self.page.goto(
                    url,
                    wait_until='domcontentloaded',
                    timeout=PAGE_LOAD_TIMEOUT
                )
                
                if response and response.status == 200:
                    # Wait a bit for dynamic content
                    await asyncio.sleep(1)
                    
                    # Check for anti-bot protection
                    if check_antibot:
                        content = await self.page.content()
                        if 'page_no_referer' in content or 'limit_no_referer' in content:
                            logger.info("🔄 Anti-bot detected, reloading page...")
                            # The page sets localStorage and needs a reload
                            await asyncio.sleep(1)
                            await self.page.reload(wait_until='domcontentloaded')
                            await asyncio.sleep(2)
                    
                    return True
                else:
                    logger.warning(f"⚠️  HTTP {response.status if response else 'None'} for {url}")
                    
            except Exception as e:
                logger.warning(f"⚠️  Attempt {attempt + 1}/{retries} failed: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
        
        return False
    
    async def extract_brands_from_page(self) -> List[Dict[str, Any]]:
        """Extract all brand links from the brands page."""
        logger.info("🔍 Extracting brands from brands page...")
        
        # First visit homepage to establish session and set referrer
        logger.info("🏠 Visiting homepage first to establish session...")
        if not await self.navigate_with_retry(HALILIT_BASE):
            logger.error("❌ Failed to load homepage")
            return []
        
        await asyncio.sleep(2)
        
        # Now navigate to brands page with proper referrer
        if not await self.navigate_with_retry(BRANDS_PAGE_URL):
            logger.error("❌ Failed to load brands page")
            return []
        
        # Wait for page to fully load
        await asyncio.sleep(3)
        
        # Extract all links that match brand group pattern
        brands = []
        seen_ids = set()
        
        # Get page content to debug
        content = await self.page.content()
        
        # Save HTML for debugging
        debug_file = OUTPUT_DIR / "brands_page_debug.html"
        debug_file.write_text(content, encoding='utf-8')
        logger.info(f"💾 Saved page HTML to: {debug_file}")
        
        # Try multiple selectors
        all_links = await self.page.query_selector_all('a[href]')
        logger.info(f"📋 Found {len(all_links)} total links on page")
        
        # Filter for brand group links
        brand_links = []
        for link in all_links:
            try:
                href = await link.get_attribute('href')
                if href and '/g/5193' in href:
                    brand_links.append(link)
            except:
                continue
        
        logger.info(f"📋 Found {len(brand_links)} potential brand links")
        
        # If no links found with selector, try parsing HTML directly
        if len(brand_links) == 0:
            logger.info("🔍 No links found with selector, parsing HTML directly...")
            
            # Find all /g/5193 patterns in HTML
            pattern = r'href=["\']([^"\']*?/g/5193[^"\']*?)["\']'
            matches = re.findall(pattern, content)
            logger.info(f"📋 Found {len(matches)} brand URLs in HTML")
            
            for href in matches:
                try:
                    # Match pattern: /g/5193-*/XXXXX-BrandName
                    match = re.search(r'/g/5193[^/]*/(\d+)-(.+?)(?:[?&"\'\s]|$)', href)
                    if not match:
                        continue
                    
                    brand_id = match.group(1)
                    brand_name = match.group(2).replace('-', ' ').strip()
                    
                    # Skip duplicates
                    if brand_id in seen_ids:
                        continue
                    seen_ids.add(brand_id)
                    
                    # Build full URL
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = HALILIT_BASE + href
                    else:
                        full_url = HALILIT_BASE + '/' + href
                    
                    # Clean URL
                    full_url = full_url.split('?')[0].split('"')[0].split("'")[0]
                    
                    brands.append({
                        'name': brand_name,
                        'id': brand_id,
                        'url': full_url,
                        'product_count': 0  # Will be filled later
                    })
                    
                except Exception as e:
                    logger.debug(f"Error parsing brand link: {e}")
                    continue
        else:
            # Process links found with selector
            for link in brand_links:
                try:
                    href = await link.get_attribute('href')
                    if not href:
                        continue
                    
                    # Match pattern: /g/5193-*/XXXXX-BrandName
                    match = re.search(r'/g/5193[^/]*/(\d+)-(.+?)(?:\?|$)', href)
                    if not match:
                        continue
                    
                    brand_id = match.group(1)
                    brand_name = match.group(2).replace('-', ' ').strip()
                    
                    # Skip duplicates
                    if brand_id in seen_ids:
                        continue
                    seen_ids.add(brand_id)
                    
                    # Build full URL
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = HALILIT_BASE + href
                    else:
                        full_url = HALILIT_BASE + '/' + href
                    
                    # Clean URL
                    full_url = full_url.split('?')[0]  # Remove query params for now
                    
                    brands.append({
                        'name': brand_name,
                        'id': brand_id,
                        'url': full_url,
                        'product_count': 0  # Will be filled later
                    })
                    
                except Exception as e:
                    logger.debug(f"Error parsing brand link: {e}")
                    continue
        
        # Deduplicate by ID
        unique_brands = {b['id']: b for b in brands}.values()
        brands = sorted(unique_brands, key=lambda x: x['name'])
        
        logger.info(f"✅ Found {len(brands)} unique brands")
        return brands
    
    async def extract_product_count(self, brand_url: str) -> int:
        """Extract total product count from brand page."""
        try:
            if not await self.navigate_with_retry(brand_url):
                return 0
            
            # Look for Hebrew text "תוצאות: NNN"
            content = await self.page.content()
            match = re.search(r'תוצאות:\s*(\d[\d,]*)', content)
            
            if match:
                count = int(match.group(1).replace(',', ''))
                logger.info(f"  📊 Found {count} products")
                return count
            
            # Fallback: count product items on page and estimate
            items = await self.page.query_selector_all('.layout_list_item, .box, .item, .product_item')
            if items:
                logger.info(f"  📊 Estimated ~{len(items)} products (no total count found)")
                return len(items)
            
            return 0
            
        except Exception as e:
            logger.warning(f"  ⚠️  Error extracting product count: {e}")
            return 0
    
    async def extract_products_from_page(self) -> List[str]:
        """Extract product URLs from current page."""
        try:
            # Find all product links (format: /items/NNNNNNN-product-name)
            links = await self.page.query_selector_all('a[href*="/items/"]')
            
            product_urls = []
            for link in links:
                href = await link.get_attribute('href')
                if not href or '/items/' not in href:
                    continue
                
                # Build full URL
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('/'):
                    full_url = HALILIT_BASE + href
                else:
                    full_url = HALILIT_BASE + '/' + href
                
                # Clean URL (remove query params)
                full_url = full_url.split('?')[0]
                
                # Validate format
                if re.search(r'/items/\d+', full_url):
                    product_urls.append(full_url)
            
            return list(set(product_urls))  # Deduplicate
            
        except Exception as e:
            logger.warning(f"  ⚠️  Error extracting products: {e}")
            return []
    
    async def check_next_page(self) -> bool:
        """Check if there's a next page and navigate to it."""
        try:
            # Look for pagination links
            pagination = await self.page.query_selector('.pagination')
            if not pagination:
                return False
            
            # Find current page and next page
            current_url = self.page.url
            
            # Try to find "next" button or highest page number
            links = await pagination.query_selector_all('a[href*="page="]')
            
            max_page = 0
            current_page = 1
            
            # Extract current page from URL
            current_match = re.search(r'[?&]page=(\d+)', current_url)
            if current_match:
                current_page = int(current_match.group(1))
            
            # Find max page
            for link in links:
                href = await link.get_attribute('href')
                page_match = re.search(r'[?&]page=(\d+)', href)
                if page_match:
                    page_num = int(page_match.group(1))
                    if page_num > max_page:
                        max_page = page_num
            
            # Check if there's a next page
            next_page = current_page + 1
            if next_page <= max_page:
                # Build next page URL
                if '?' in current_url:
                    if 'page=' in current_url:
                        next_url = re.sub(r'page=\d+', f'page={next_page}', current_url)
                    else:
                        next_url = f"{current_url}&page={next_page}"
                else:
                    next_url = f"{current_url}?page={next_page}"
                
                logger.info(f"  📄 Navigating to page {next_page}/{max_page}")
                return await self.navigate_with_retry(next_url)
            
            return False
            
        except Exception as e:
            logger.warning(f"  ⚠️  Error checking next page: {e}")
            return False
    
    async def scrape_brand_products(self, brand: Dict[str, Any]) -> int:
        """Scrape all product URLs for a brand."""
        logger.info(f"\n{'='*60}")
        logger.info(f"🏷️  Scraping brand: {brand['name']} (ID: {brand['id']})")
        logger.info(f"{'='*60}")
        
        # Navigate to brand page
        if not await self.navigate_with_retry(brand['url']):
            logger.error(f"❌ Failed to load brand page: {brand['url']}")
            return 0
        
        # Extract product count
        product_count = await self.extract_product_count(brand['url'])
        brand['product_count'] = product_count
        
        if product_count == 0:
            logger.warning(f"⚠️  No products found for {brand['name']}")
            return 0
        
        # Calculate expected pages (24-25 products per page)
        items_per_page = 24
        expected_pages = (product_count + items_per_page - 1) // items_per_page
        
        logger.info(f"📊 Expected ~{expected_pages} pages for {product_count} products")
        
        # Scrape page 1
        page_num = 1
        products = await self.extract_products_from_page()
        logger.info(f"  ✅ Page {page_num}: Found {len(products)} product URLs")
        
        for url in products:
            self.all_product_urls.add(url)
        
        # Scrape remaining pages
        consecutive_empty = 0
        max_pages = min(expected_pages + 2, 100)  # Safety limit
        
        while page_num < max_pages:
            has_next = await self.check_next_page()
            if not has_next:
                logger.info(f"  ℹ️  No more pages found")
                break
            
            page_num += 1
            
            # Extract products from this page
            page_products = await self.extract_products_from_page()
            
            if not page_products:
                consecutive_empty += 1
                logger.info(f"  ⚠️  Page {page_num}: No products found (empty: {consecutive_empty}/2)")
                
                if consecutive_empty >= 2:
                    logger.info(f"  ℹ️  2 consecutive empty pages, stopping")
                    break
            else:
                consecutive_empty = 0
                logger.info(f"  ✅ Page {page_num}: Found {len(page_products)} product URLs")
                
                for url in page_products:
                    self.all_product_urls.add(url)
            
            # Small delay between pages
            await asyncio.sleep(0.5)
        
        total_found = len([url for url in self.all_product_urls if brand['name'].lower().replace(' ', '-') in url.lower()])
        logger.info(f"✅ Brand {brand['name']}: Scraped {page_num} pages, found {total_found} product URLs")
        
        return total_found
    
    async def scrape_all(self):
        """Main scraping workflow."""
        try:
            await self.initialize()
            
            # Step 1: Extract all brands
            logger.info("\n" + "="*60)
            logger.info("STEP 1: EXTRACTING BRANDS")
            logger.info("="*60)
            
            brands = await self.extract_brands_from_page()
            
            if not brands:
                logger.error("❌ No brands found! Exiting.")
                return
            
            self.brand_data = brands
            
            # Step 2: Scrape products for each brand
            logger.info("\n" + "="*60)
            logger.info(f"STEP 2: SCRAPING PRODUCTS FOR {len(brands)} BRANDS")
            logger.info("="*60)
            
            for idx, brand in enumerate(brands, 1):
                logger.info(f"\n[{idx}/{len(brands)}] Processing: {brand['name']}")
                
                try:
                    await self.scrape_brand_products(brand)
                except Exception as e:
                    logger.error(f"❌ Error scraping {brand['name']}: {e}")
                    continue
                
                # Small delay between brands
                await asyncio.sleep(1)
            
            # Step 3: Save results
            logger.info("\n" + "="*60)
            logger.info("STEP 3: SAVING RESULTS")
            logger.info("="*60)
            
            await self.save_results()
            
        finally:
            await self.close()
    
    async def save_results(self):
        """Save extracted data to files."""
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save product URLs
        sorted_urls = sorted(self.all_product_urls)
        PRODUCT_URLS_FILE.write_text('\n'.join(sorted_urls) + '\n')
        logger.info(f"✅ Saved {len(sorted_urls)} product URLs to: {PRODUCT_URLS_FILE}")
        
        # Save brand data
        BRAND_DATA_FILE.write_text(json.dumps(self.brand_data, indent=2, ensure_ascii=False))
        logger.info(f"✅ Saved {len(self.brand_data)} brands to: {BRAND_DATA_FILE}")
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("📊 SUMMARY")
        logger.info("="*60)
        logger.info(f"Total brands: {len(self.brand_data)}")
        logger.info(f"Total product URLs: {len(sorted_urls)}")
        
        # Top brands by product count
        top_brands = sorted(self.brand_data, key=lambda x: x['product_count'], reverse=True)[:10]
        logger.info("\n🏆 Top 10 brands by product count:")
        for i, brand in enumerate(top_brands, 1):
            logger.info(f"  {i}. {brand['name']}: {brand['product_count']} products")


async def main():
    """Main entry point."""
    scraper = HalilitBrowserScraper()
    await scraper.scrape_all()


if __name__ == '__main__':
    asyncio.run(main())
