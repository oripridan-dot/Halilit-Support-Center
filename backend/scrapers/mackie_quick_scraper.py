#!/usr/bin/env python3
"""Quick Mackie price scraper - single brand focus"""

import json
import logging
import time
import re
from pathlib import Path
import cloudscraper
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class MackieQuickScraper:
    """Fast Mackie product price scraper"""

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://www.halilit.com"

    def scrape_product_price(self, product_name: str) -> dict:
        """Scrape single product price"""
        try:
            logger.info(f"Searching: {product_name}")

            response = self.scraper.get(
                f"{self.base_url}/search",
                params={'q': product_name},
                timeout=10
            )

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            products = soup.select(
                '.product-item, .product_item, [data-product-id]')

            if not products:
                return None

            product = products[0]
            price_elem = product.select_one('.price, .price-il, [data-price]')

            if not price_elem:
                return None

            price_text = price_elem.get_text(strip=True)
            price_match = re.search(r'[\d,]+(?:\.[\d]+)?', price_text)

            if not price_match:
                return None

            price_il = float(price_match.group(0).replace(',', ''))
            price_eilat = round(price_il * 0.85, 2)

            return {
                'price_il': price_il,
                'price_eilat': price_eilat
            }

        except Exception as e:
            logger.warning(f"Error: {e}")
            return None

    def run(self):
        """Scrape all Mackie prices"""
        json_file = Path('backend/scrapers/halilit_mackie_complete.json')

        with open(json_file, 'r', encoding='utf-8') as f:
            products = json.load(f)

        logger.info(
            f"\n{'='*60}\nSCRAPE START: {len(products)} Mackie products\n{'='*60}\n")

        updated = 0
        for i, product in enumerate(products, 1):
            name = product.get('product_name', '')

            if product.get('price_il', 0) > 0:
                logger.info(f"[{i}/{len(products)}] SKIP (has price): {name}")
                continue

            result = self.scrape_product_price(name)

            if result:
                product['price_il'] = result['price_il']
                product['price_eilat'] = result['price_eilat']
                logger.info(f"  ✓ ₪{result['price_il']:.0f}")
                updated += 1
            else:
                logger.info(f"  ✗ Not found")

            if i < len(products):
                time.sleep(2)

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)

        logger.info(f"\n{'='*60}")
        logger.info(f"COMPLETE: {updated} products updated")
        logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    s = MackieQuickScraper()
    s.run()
