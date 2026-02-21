#!/usr/bin/env python3
"""
Halilit Full Catalog Scraper
Extracts ALL RCF and Mackie products from Halilit website
"""

import json
import logging
from pathlib import Path
from typing import List, Dict
import cloudscraper
from bs4 import BeautifulSoup
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class HalilitFullCatalogScraper:
    """
    Scrapes Halilit search pages to collect all RCF and Mackie products
    Uses CloudScraper to bypass any protection
    """

    def __init__(self, output_dir="backend/scrapers"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.scraper = cloudscraper.create_scraper()

        self.categories = {
            'RCF': {
                'search_url': 'https://www.halilit.com/en/search?q=rcf',
                'output': self.output_dir / 'halilit_rcf_full.json',
                'target': 178
            },
            'Mackie': {
                'search_url': 'https://www.halilit.com/en/search?q=mackie',
                'output': self.output_dir / 'halilit_mackie_full.json',
                'target': 220
            }
        }

    def scrape_brand(self, brand: str) -> List[Dict]:
        """
        Scrape Halilit search results for a brand
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Scraping Halilit {brand.upper()} Products")
        logger.info(f"{'='*80}")

        category = self.categories[brand]
        url = category['search_url']

        try:
            logger.info(f"Fetching: {url}")
            response = self.scraper.get(url, timeout=30)

            if response.status_code != 200:
                logger.error(f"Failed to fetch page: {response.status_code}")
                return []

            logger.info(f"✓ Page loaded ({len(response.text)} bytes)")

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract products
            products = self.extract_products(soup, brand)

            logger.info(f"✓ Found {len(products)} {brand.upper()} products")
            return products

        except Exception as e:
            logger.error(f"Error scraping {brand}: {e}")
            import traceback
            traceback.print_exc()
            return []

    def extract_products(self, soup: BeautifulSoup, brand: str) -> List[Dict]:
        """
        Extract product data from search results page
        """
        logger.info(f"Parsing {brand} products from HTML...")

        products = []
        seen_names = set()

        # Look for product links and containers
        # Search for common product selectors
        product_elements = []

        # Try different selectors
        product_elements.extend(soup.find_all(
            'a', href=re.compile(r'/product/', re.I)))
        product_elements.extend(soup.find_all(
            'a', href=re.compile(r'/products/', re.I)))
        product_elements.extend(soup.find_all(
            'div', class_=re.compile(r'product', re.I)))

        logger.info(
            f"Found {len(product_elements)} potential product elements")

        for element in product_elements:
            # If it's a div, try to find link inside
            if element.name == 'div':
                link = element.find('a', href=True)
                if not link:
                    continue
                element = link

            # Get product name and URL
            href = element.get('href', '').strip()
            text = element.get_text(strip=True)

            if not href or not text:
                continue

            # Must contain brand name
            if brand.lower() not in text.lower() and brand.lower() not in href.lower():
                continue

            # Skip duplicates
            product_key = text.lower().strip()
            if product_key in seen_names or len(product_key) < 3:
                continue

            seen_names.add(product_key)

            # Try to extract price
            price_ils = self.extract_price(element)

            # Build product record
            product = {
                'name': text,
                'brand': brand,
                'price_ils': price_ils,
                'url': href if href.startswith('http') else f"https://www.halilit.com{href}",
                'source': 'halilit'
            }

            products.append(product)

            if len(products) <= 10:
                logger.info(
                    f"  {len(products)}. {text[:50]} - ₪{price_ils if price_ils else 'TBD'}")

        logger.info(
            f"✓ Parsed {len(products)} unique {brand.upper()} products")
        return products

    def extract_price(self, element) -> float:
        """
        Extract price from element or nearby elements
        """
        try:
            # Look for price in text content
            text = element.get_text()
            price_match = re.search(r'₪\s*([\d,]+(?:\.\d{2})?)', text)
            if price_match:
                return float(price_match.group(1).replace(',', ''))

            # Look in parent or siblings
            parent = element.parent if hasattr(element, 'parent') else None
            if parent:
                text = parent.get_text()
                price_match = re.search(r'₪\s*([\d,]+(?:\.\d{2})?)', text)
                if price_match:
                    return float(price_match.group(1).replace(',', ''))
        except:
            pass

        return 0.0

    def load_fallback_data(self, brand: str) -> List[Dict]:
        """
        Load fallback data from JSON files if web scraping fails
        """
        logger.info(f"Loading fallback {brand} data from JSON...")

        json_file = Path("frontend/public/data") / f"{brand.lower()}.json"
        if json_file.exists():
            try:
                with open(json_file) as f:
                    data = json.load(f)
                logger.info(f"✓ Loaded {len(data)} {brand} products from JSON")

                # Normalize to standard format
                products = []
                for p in data:
                    products.append({
                        'name': p.get('product_name', ''),
                        'brand': brand,
                        'price_ils': p.get('price_il', 0),
                        'url': p.get('halilit_url', ''),
                        'source': 'halilit_json'
                    })
                return products
            except Exception as e:
                logger.error(f"Error loading JSON: {e}")

        return []

    def deduplicate(self, products: List[Dict]) -> List[Dict]:
        """
        Remove duplicate products by name
        """
        seen = {}
        deduped = []

        for p in products:
            key = p['name'].lower().strip()
            if key not in seen:
                seen[key] = p
                deduped.append(p)

        removed = len(products) - len(deduped)
        if removed > 0:
            logger.info(f"Removed {removed} duplicates")

        return deduped

    def run(self, brands: List[str] = ["RCF", "Mackie"]):
        """
        Run full scraping for all brands
        """
        logger.info(f"\n{'='*80}")
        logger.info("HALILIT FULL-CATALOG SCRAPING")
        logger.info(f"{'='*80}")

        all_data = {}
        summary = {}

        for brand in brands:
            # Try web scraping first
            products = self.scrape_brand(brand)

            # If web scraping didn't work well, supplement with JSON
            if len(products) < 10:
                logger.warning(
                    f"Web scraping got {len(products)} products, loading JSON fallback...")
                json_products = self.load_fallback_data(brand)
                products.extend(json_products)

            # Deduplicate
            products = self.deduplicate(products)
            all_data[brand] = products

            # Statistics
            prices = [p['price_ils'] for p in products if p['price_ils'] > 0]
            summary[brand] = {
                'total_products': len(products),
                'with_pricing': len(prices),
                'avg_price_ils': sum(prices) / len(prices) if prices else 0,
                'min_price_ils': min(prices) if prices else 0,
                'max_price_ils': max(prices) if prices else 0,
                'total_value_ils': sum(prices)
            }

            # Save
            output_file = self.categories[brand]['output']
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)

            logger.info(f"✓ Saved {len(products)} products to {output_file}")

        # Save merged and summary
        merged_file = self.output_dir / "halilit_full_merged.json"
        with open(merged_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

        summary_file = self.output_dir / "halilit_extraction_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        # Print summary
        logger.info(f"\n{'='*80}")
        logger.info("HALILIT EXTRACTION COMPLETE")
        logger.info(f"{'='*80}")

        for brand, stats in summary.items():
            logger.info(f"\n{brand}:")
            logger.info(f"  Total Products: {stats['total_products']}")
            logger.info(f"  With Pricing: {stats['with_pricing']}")
            if stats['avg_price_ils'] > 0:
                logger.info(
                    f"  Price Range: ₪{stats['min_price_ils']:.0f} - ₪{stats['max_price_ils']:.0f}")
                logger.info(f"  Avg Price: ₪{stats['avg_price_ils']:.0f}")
                logger.info(f"  Total Value: ₪{stats['total_value_ils']:.0f}")

        return all_data, summary


if __name__ == "__main__":
    scraper = HalilitFullCatalogScraper()
    scraper.run(["RCF", "Mackie"])
