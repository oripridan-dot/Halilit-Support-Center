#!/usr/bin/env python3
"""
Halilit Product Extractor (Enhanced)
Extracts product data from Halilit with improved handling for:
- Local JSON file extraction (primary method)
- API reverse engineering preparation
- Database queries
- Batch extraction for multiple brands
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class HalilitExtractor:
    """
    Extracts product data from Halilit sources
    Priority: Local JSON → Database → API → Selenium
    """

    def __init__(self,
                 json_dir="frontend/public/data",
                 db_path="backend/scrapers/ingestion/products.db",
                 output_dir="backend/scrapers"):
        self.json_dir = Path(json_dir)
        self.db_path = Path(db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def method_1_json_extraction(self, brand: str) -> Tuple[List[Dict], bool]:
        """
        Method 1: Extract from local JSON files (FASTEST - 2 minutes)

        Returns:
            (products_list, success_flag)
        """
        logger.info(f"[METHOD 1] Extracting {brand} from local JSON...")

        json_file = self.json_dir / f"{brand.lower()}.json"

        if not json_file.exists():
            logger.warning(f"JSON file not found: {json_file}")
            return [], False

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                products = json.load(f)

            # Validate structure
            if not isinstance(products, list):
                logger.error(f"JSON is not a list: {type(products)}")
                return [], False

            if not products:
                logger.warning(f"JSON file is empty")
                return [], False

            # Inspect first product structure
            first = products[0]
            logger.info(f"Sample product keys: {first.keys()}")

            logger.info(f"✓ Loaded {len(products)} {brand} products from JSON")

            return products, True

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return [], False
        except Exception as e:
            logger.error(f"Error reading JSON: {e}")
            return [], False

    def method_2_database_extraction(self, brand: str) -> Tuple[List[Dict], bool]:
        """
        Method 2: Extract from SQLite database (MEDIUM - 5 minutes)

        Returns:
            (products_list, success_flag)
        """
        logger.info(f"[METHOD 2] Extracting {brand} from database...")

        if not self.db_path.exists():
            logger.warning(f"Database not found: {self.db_path}")
            return [], False

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check available tables
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"Available tables: {tables}")

            # Try to find products table
            product_table = None
            for table_name in ['products', 'product', 'halilit_products', f'{brand.lower()}']:
                if table_name in tables:
                    product_table = table_name
                    break

            if not product_table:
                logger.warning(f"No suitable product table found")
                conn.close()
                return [], False

            # Query products for brand
            query = f"""
                SELECT * FROM {product_table}
                WHERE brand ILIKE ? OR product_name ILIKE ?
                LIMIT 500
            """

            cursor.execute(query, (f"%{brand}%", f"%{brand}%"))
            columns = [description[0] for description in cursor.description]

            products = []
            for row in cursor.fetchall():
                product = dict(zip(columns, row))
                products.append(product)

            conn.close()

            if products:
                logger.info(
                    f"✓ Loaded {len(products)} {brand} products from database")
                return products, True
            else:
                logger.warning(f"No {brand} products found in database")
                return [], False

        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return [], False
        except Exception as e:
            logger.error(f"Error accessing database: {e}")
            return [], False

    def method_3_api_preparation(self, brand: str) -> Dict:
        """
        Method 3: Prepare for API reverse engineering (MEDIUM - 10-20 minutes)

        Provides guidance for manual API discovery via browser network tab
        Returns API endpoint information
        """
        logger.info(f"[METHOD 3] Preparing for API reverse engineering...")

        guidance = {
            "step_1": "Open https://www.halilit.com in Chrome",
            "step_2": "Open DevTools (F12) → Network tab",
            "step_3": f"Search for '{brand}'",
            "step_4": "Look for XHR/Fetch requests containing product data",
            "step_5": "Common patterns: /api/products, /api/search, /api/catalog",

            "likely_endpoints": [
                f"https://www.halilit.com/api/products?brand={brand}",
                f"https://www.halilit.com/api/search?q={brand}&limit=500",
                f"https://www.halilit.com/api/catalog?category={brand.lower()}",
            ],

            "instructions": f"""
MANUAL STEPS TO GET HALILIT API:
1. Open this in a browser: https://www.halilit.com
2. Press F12 (DevTools)
3. Go to Network tab
4. Search for: {brand}
5. Look for requests returning JSON with product data
6. Copy the request URL and headers
7. Test endpoint with: curl -H "User-Agent: ..." {brand_search_url}
            """,

            "status": "Awaiting manual API discovery",
            "source": "manual"
        }

        logger.info("API method requires manual discovery - see guidance above")
        return guidance

    def method_4_selenium_preparation(self) -> Dict:
        """
        Method 4: Prepare for Selenium automation (SLOWEST - 30-60 minutes)

        Provides setup and code template
        """
        logger.info(f"[METHOD 4] Preparing Selenium automation...")

        instructions = {
            "installation": "pip install selenium webdriver-manager",
            "status": "Ready for implementation",
            "estimated_time": "30-60 minutes per brand",
            "pros": [
                "Works with any site structure",
                "Can handle JavaScript rendering",
                "Most reliable fallback"
            ],
            "cons": [
                "Slowest method",
                "Resource intensive",
                "Fragile (breaks if site changes)"
            ]
        }

        logger.info("Selenium method ready - see instructions above")
        return instructions

    def normalize_product(self, product: Dict, brand: str) -> Dict:
        """
        Normalize product data to standard structure
        Handles different field names from different sources
        """

        # Map common field names
        normalized = {
            'product_id': product.get('id') or product.get('product_id'),
            'product_name': product.get('product_name') or product.get('name') or product.get('title'),
            'brand': brand,
            'price_ils': product.get('price_il') or product.get('price_ils') or product.get('price'),
            'price_usd': None,
            'currency': 'ILS',
            'url': product.get('url') or product.get('link'),
            'description': product.get('description'),
            'category': product.get('category'),
            'subcategory': product.get('subcategory'),
            'in_stock': product.get('in_stock', True),
            'image_url': product.get('image') or product.get('image_url'),
            'source': 'halilit'
        }

        # Convert ILS to USD (approximate)
        if normalized['price_ils'] and normalized['price_ils'] > 0:
            normalized['price_usd'] = normalized['price_ils'] / 3.7

        return normalized

    def extract_brand(self, brand: str) -> List[Dict]:
        """
        Master method: Extract products for a brand using best available method
        Tries methods in order of speed/reliability
        """

        logger.info(f"\n{'='*80}")
        logger.info(f"EXTRACTING HALILIT {brand.upper()} PRODUCTS")
        logger.info(f"{'='*80}")

        # Method 1: JSON (fastest)
        products, success = self.method_1_json_extraction(brand)
        if success and len(products) > 50:
            logger.info(f"✓ Method 1 successful with {len(products)} products")
            return [self.normalize_product(p, brand) for p in products]

        logger.warning(f"Method 1 found only {len(products)} products")

        # Method 2: Database (medium speed)
        db_products, success = self.method_2_database_extraction(brand)
        if success and len(db_products) > len(products):
            logger.info(f"✓ Method 2 better: {len(db_products)} products")
            return [self.normalize_product(p, brand) for p in db_products]

        logger.warning(
            f"Method 2 found only {len(db_products)} additional products")

        # If we have some products, return what we have
        if products:
            logger.info(f"Returning {len(products)} products from Method 1")
            return [self.normalize_product(p, brand) for p in products]

        # Methods 3 & 4: Need manual intervention
        logger.warning(
            f"Methods 1-2 failed. Methods 3-4 require manual/async setup.")

        api_info = self.method_3_api_preparation(brand)
        selenium_info = self.method_4_selenium_preparation()

        logger.warning(f"""
Next steps:
1. METHOD 3: Reverse engineer Halilit API
   - See above for endpoints and browser instructions
   - Once you find the API, report the endpoint
   
2. METHOD 4: Use Selenium automation
   - Install selenium: pip install selenium webdriver-manager
   - Uncomment Selenium code in scraper
   - Run with: python3 halilit_scraper.py --method=selenium
        """)

        return []

    def run(self, brands: List[str] = ["RCF", "Mackie"]):
        """Run extraction for all brands"""

        all_data = {}
        summary = {}

        for brand in brands:
            products = self.extract_brand(brand)
            all_data[brand] = products

            # Save individual brand file
            output_file = self.output_dir / \
                f"halilit_{brand.lower()}_full.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)

            logger.info(f"✓ Saved to {output_file}")

            # Summary stats
            prices = [p.get('price_ils', 0)
                      for p in products if p.get('price_ils', 0) > 0]
            summary[brand] = {
                'total_products': len(products),
                'with_pricing': len(prices),
                'avg_price_ils': sum(prices) / len(prices) if prices else 0,
                'min_price_ils': min(prices) if prices else 0,
                'max_price_ils': max(prices) if prices else 0,
                'total_value_ils': sum(prices)
            }

        # Save merged
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
            logger.info(f"  Total: {stats['total_products']}")
            logger.info(f"  With pricing: {stats['with_pricing']}")
            if stats['avg_price_ils'] > 0:
                logger.info(
                    f"  Price range: ₪{stats['min_price_ils']:.0f} - ₪{stats['max_price_ils']:.0f}")
                logger.info(f"  Avg price: ₪{stats['avg_price_ils']:.0f}")


if __name__ == "__main__":
    extractor = HalilitExtractor()
    extractor.run(["RCF", "Mackie"])
