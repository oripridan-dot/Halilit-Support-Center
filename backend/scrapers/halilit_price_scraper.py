#!/usr/bin/env python3
"""
Halilit Price Scraper
Scrapes actual prices for RCF and Mackie products from Halilit.com
Updates JSON files with real pricing data
"""

import json
import logging
import time
import re
from pathlib import Path
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import cloudscraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class HalilitPriceScraper:
    """Scrapes Halilit.com for product prices"""

    def __init__(self, data_dir="backend/scrapers"):
        self.data_dir = Path(data_dir)
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://www.halilit.com"
        self.search_url = f"{self.base_url}/search"

    def scrape_product_price(self, product_name: str) -> Optional[Dict]:
        """
        Search for a product on Halilit and extract its price
        Returns: {'price_il': float, 'price_eilat': float, 'url': str} or None
        """
        try:
            logger.info(f"Searching for: {product_name}")

            # Search for the product
            params = {'q': product_name}
            response = self.scraper.get(
                self.search_url, params=params, timeout=10)

            if response.status_code != 200:
                logger.warning(
                    f"Search failed for '{product_name}' (status: {response.status_code})")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the first product result
            # Halilit typically uses product containers with specific classes
            product_items = soup.select(
                '.product-item, .product_item, .product-box, [data-product-id], .item'
            )

            if not product_items:
                logger.warning(f"No products found for '{product_name}'")
                return None

            # Process the first (most relevant) result
            product = product_items[0]

            # Extract link
            link_elem = product.select_one('a')
            product_url = None
            if link_elem and link_elem.get('href'):
                product_url = link_elem['href']
                if not product_url.startswith('http'):
                    product_url = self.base_url + product_url

            # Extract price
            price_elem = product.select_one(
                '.price, .price-il, .price-shekel, .item-price, [data-price], .current-price'
            )

            if not price_elem:
                logger.warning(f"No price element found for '{product_name}'")
                return None

            price_text = price_elem.get_text(strip=True)

            # Extract numeric price (remove ₪, commas, etc.)
            price_match = re.search(r'[\d,]+(?:\.[\d]+)?', price_text)
            if not price_match:
                logger.warning(
                    f"Could not parse price from text: '{price_text}'")
                return None

            price_il = float(price_match.group(0).replace(',', ''))

            # Calculate Eilat price (typically 15% discount, or check if specified)
            # Halilit shows Eilat prices separately - try to find them
            eilat_price_elem = product.select_one(
                '.price-eilat, .eilat-price, [data-eilat-price]'
            )

            if eilat_price_elem:
                eilat_text = eilat_price_elem.get_text(strip=True)
                eilat_match = re.search(r'[\d,]+(?:\.[\d]+)?', eilat_text)
                if eilat_match:
                    price_eilat = float(eilat_match.group(0).replace(',', ''))
                else:
                    # Default: 15% discount for Eilat
                    price_eilat = round(price_il * 0.85, 2)
            else:
                # Default: 15% discount for Eilat
                price_eilat = round(price_il * 0.85, 2)

            logger.info(
                f"✓ Found: {product_name} | IL: ₪{price_il:.0f} | Eilat: ₪{price_eilat:.0f}")

            return {
                'price_il': price_il,
                'price_eilat': price_eilat,
                'url': product_url
            }

        except Exception as e:
            logger.error(f"Error scraping '{product_name}': {e}")
            return None

    def load_json_products(self, filepath: str) -> List[Dict]:
        """Load products from JSON file"""
        if not Path(filepath).exists():
            logger.error(f"File not found: {filepath}")
            return []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return []

    def save_json_products(self, filepath: str, products: List[Dict]):
        """Save products to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved {len(products)} products to {filepath}")
        except Exception as e:
            logger.error(f"Error saving {filepath}: {e}")

    def scrape_and_update_brand(self, brand: str) -> Dict:
        """
        Scrape prices for all products of a brand and update JSON
        Returns statistics about the scraping
        """
        json_file = self.data_dir / f"halilit_{brand.lower()}_complete.json"

        logger.info(f"\n{'='*80}")
        logger.info(f"SCRAPING HALILIT PRICES: {brand.upper()}")
        logger.info(f"{'='*80}\n")

        # Load products
        products = self.load_json_products(str(json_file))
        if not products:
            return {
                'brand': brand,
                'total': 0,
                'updated': 0,
                'failed': 0,
                'skipped': 0
            }

        updated = 0
        failed = 0
        skipped = 0

        # Scrape each product
        for i, product in enumerate(products, 1):
            product_name = product.get('product_name', '')
            current_price = product.get('price_il', 0)

            # Skip if already has a price (don't overwrite)
            if current_price > 0:
                logger.info(
                    f"[{i}/{len(products)}] Skipping (already has price): {product_name}")
                skipped += 1
                continue

            # Scrape price
            price_data = self.scrape_product_price(product_name)

            if price_data:
                product['price_il'] = price_data['price_il']
                product['price_eilat'] = price_data['price_eilat']
                if price_data.get('url'):
                    product['halilit_url'] = price_data['url']
                updated += 1
            else:
                failed += 1

            # Rate limiting - be respectful to the server
            if i < len(products):
                time.sleep(2)

        # Save updated products
        self.save_json_products(str(json_file), products)

        stats = {
            'brand': brand,
            'total': len(products),
            'updated': updated,
            'failed': failed,
            'skipped': skipped
        }

        logger.info(f"\n{'='*80}")
        logger.info(f"SCRAPING COMPLETE: {brand.upper()}")
        logger.info(f"{'='*80}")
        logger.info(f"Total Products: {len(products)}")
        logger.info(f"Updated (new prices): {updated}")
        logger.info(f"Failed (price not found): {failed}")
        logger.info(f"Skipped (already had prices): {skipped}")
        logger.info(f"{'='*80}\n")

        return stats

    def scrape_all_brands(self) -> Dict:
        """Scrape prices for all brands"""
        brands = ['rcf', 'mackie']
        all_stats = {}

        for brand in brands:
            stats = self.scrape_and_update_brand(brand)
            all_stats[brand] = stats

            # Delay between brands
            time.sleep(3)

        return all_stats

    def generate_report(self, stats: Dict):
        """Generate scraping report"""
        logger.info("\n")
        logger.info("╔" + "="*78 + "╗")
        logger.info("║" + "HALILIT PRICE SCRAPING REPORT".center(78) + "║")
        logger.info("╚" + "="*78 + "╝")
        logger.info("")

        total_updated = 0
        total_products = 0

        for brand, brand_stats in stats.items():
            logger.info(f"\n{brand.upper()}:")
            logger.info(f"  Total Products: {brand_stats['total']}")
            logger.info(f"  With Updated Prices: {brand_stats['updated']}")
            logger.info(f"  Failed to Find Price: {brand_stats['failed']}")
            logger.info(f"  Already Had Prices: {brand_stats['skipped']}")
            logger.info(
                f"  Success Rate: {brand_stats['updated']}/{brand_stats['total']} ({100*brand_stats['updated']//max(1, brand_stats['total']-brand_stats['skipped'])}%)")

            total_updated += brand_stats['updated']
            total_products += brand_stats['total']

        logger.info(f"\n{'─'*80}")
        logger.info(f"TOTAL ACROSS ALL BRANDS:")
        logger.info(f"  Products Updated: {total_updated}/{total_products}")
        logger.info(
            f"  Success Rate: {100*total_updated//max(1, total_products)}%")
        logger.info(f"{'─'*80}\n")


def main():
    """Main execution"""
    scraper = HalilitPriceScraper()

    # Scrape prices for all brands
    stats = scraper.scrape_all_brands()

    # Generate report
    scraper.generate_report(stats)


if __name__ == "__main__":
    main()
