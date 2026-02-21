#!/usr/bin/env python3
"""
Halilit Complete Catalog Scraper
Extracts ALL RCF and Mackie products with prices from halilit.com
"""

import json
import logging
import time
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


class HalilitCompleteScraper:
    """
    Comprehensive scraper for Halilit product catalog
    """

    def __init__(self, output_dir="backend/scrapers"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.scraper = cloudscraper.create_scraper()

    def scrape_brand_category(self, brand: str) -> List[Dict]:
        """
        Scrape brand category page from Halilit
        Try multiple URL patterns
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Scraping Halilit for ALL {brand.upper()} products")
        logger.info(f"{'='*80}")

        products = []

        # Try different URL patterns
        urls_to_try = [
            f"https://www.halilit.com/{brand.lower()}",
            f"https://www.halilit.com/en/{brand.lower()}",
            f"https://www.halilit.com/search/{brand.lower()}",
            f"https://www.halilit.com/en/search/{brand.lower()}",
        ]

        for url in urls_to_try:
            logger.info(f"Trying: {url}")
            try:
                response = self.scraper.get(url, timeout=30)

                if response.status_code == 200:
                    logger.info(f"✓ Got {len(response.text)} bytes from {url}")
                    products = self.extract_from_page(response.text, brand)

                    if len(products) > 10:
                        logger.info(
                            f"✓ Successfully extracted {len(products)} products from {url}")
                        return products
                    else:
                        logger.warning(
                            f"Only got {len(products)} products, trying next URL...")
                else:
                    logger.warning(f"Status {response.status_code} for {url}")

            except Exception as e:
                logger.warning(f"Failed {url}: {e}")

            time.sleep(1)  # Be respectful to server

        # If web scraping didn't work, load from JSON as fallback
        if len(products) < 10:
            logger.warning(
                "Web scraping insufficient, loading JSON fallback...")
            products = self.load_json_fallback(brand)

        return products

    def extract_from_page(self, html: str, brand: str) -> List[Dict]:
        """
        Extract products from page HTML
        """
        products = []
        seen_names = set()

        soup = BeautifulSoup(html, 'html.parser')

        # Strategy 1: Look for product containers by common classes
        product_containers = []

        # Common product container patterns
        selectors = [
            ('div', {'class': re.compile(r'product', re.I)}),
            ('div', {'class': re.compile(r'item', re.I)}),
            ('article', {}),
            ('li', {'class': re.compile(r'product', re.I)}),
        ]

        for tag, attrs in selectors:
            if tag and attrs:
                product_containers.extend(soup.find_all(tag, attrs))
            elif tag:
                product_containers.extend(soup.find_all(tag))

        logger.info(
            f"Found {len(product_containers)} potential product containers")

        # Extract data from each container
        for container in product_containers:
            try:
                # Get product name
                name_elem = container.find(['a', 'h2', 'h3', 'span'])
                if not name_elem:
                    continue

                name = name_elem.get_text(strip=True)
                if not name or len(name) < 3:
                    continue

                # Must contain brand name
                if brand.lower() not in name.lower():
                    continue

                # Skip duplicates
                key = name.lower()
                if key in seen_names:
                    continue
                seen_names.add(key)

                # Get price
                price = self.extract_price_from_container(container)

                # Get URL
                url = ""
                link = container.find('a', href=True)
                if link:
                    url = link.get('href', '')
                    if url and not url.startswith('http'):
                        url = f"https://www.halilit.com{url}"

                product = {
                    'name': name,
                    'brand': brand,
                    'price_ils': price,
                    'url': url,
                    'source': 'halilit'
                }

                products.append(product)

            except Exception as e:
                logger.debug(f"Error parsing container: {e}")
                continue

        # Strategy 2: If few products, look for all links with brand name
        if len(products) < 10:
            logger.info("Trying alternative extraction (all links)...")

            all_links = soup.find_all('a', href=True)
            for link in all_links:
                text = link.get_text(strip=True)
                href = link.get('href', '')

                if not text or len(text) < 3:
                    continue
                if brand.lower() not in text.lower():
                    continue

                key = text.lower()
                if key in seen_names:
                    continue
                seen_names.add(key)

                # Extract price from link or parent
                price = self.extract_price_from_element(link)

                if not href.startswith('http'):
                    href = f"https://www.halilit.com{href}"

                product = {
                    'name': text,
                    'brand': brand,
                    'price_ils': price,
                    'url': href,
                    'source': 'halilit'
                }

                products.append(product)

        logger.info(
            f"Extracted {len(products)} unique {brand} products from page")
        return products

    def extract_price_from_container(self, container) -> float:
        """
        Extract price from product container
        """
        try:
            text = container.get_text()

            # Look for ₪ symbol
            matches = re.findall(r'₪\s*([\d,]+(?:\.\d{2})?)', text)
            if matches:
                # Get the first price found
                price_str = matches[0].replace(',', '')
                return float(price_str)

            # Look for numeric prices that might be already in ILS
            # Pattern: number followed by optional decimal, might have comma
            matches = re.findall(
                r'\b(\d+(?:[,\.]\d{3})*(?:[.,]\d{2})?)\b', text)
            if matches:
                # Check if this looks like a price (not too small, not too large for typical audio equipment)
                for match in matches:
                    try:
                        price = float(match.replace(',', '').replace(
                            '.', '').replace('₪', ''))
                        if 50 < price < 100000:  # Reasonable price range for audio equipment
                            return price
                    except:
                        continue

        except Exception as e:
            logger.debug(f"Error extracting price: {e}")

        return 0.0

    def extract_price_from_element(self, element) -> float:
        """
        Extract price from single element or nearby elements
        """
        # Try the element itself
        price = self.extract_price_from_container(element)
        if price > 0:
            return price

        # Try parent
        if hasattr(element, 'parent') and element.parent:
            price = self.extract_price_from_container(element.parent)
            if price > 0:
                return price

        return 0.0

    def load_json_fallback(self, brand: str) -> List[Dict]:
        """
        Load JSON fallback data
        """
        json_file = Path("frontend/public/data") / f"{brand.lower()}.json"

        if not json_file.exists():
            logger.warning(f"JSON file not found: {json_file}")
            return []

        try:
            with open(json_file) as f:
                data = json.load(f)

            logger.info(f"✓ Loaded {len(data)} {brand} products from JSON")

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
        """Remove duplicates by name"""
        seen = {}
        deduped = []

        for p in products:
            key = p['name'].lower().strip()
            if key not in seen:
                seen[key] = p
                deduped.append(p)

        removed = len(products) - len(deduped)
        if removed > 0:
            logger.info(
                f"Removed {removed} duplicates, {len(deduped)} unique products remain")

        return deduped

    def run(self, brands: List[str] = ["RCF", "Mackie"]):
        """Run complete scraping"""

        logger.info(f"\n{'='*80}")
        logger.info("HALILIT COMPLETE CATALOG SCRAPING")
        logger.info(f"{'='*80}")

        all_data = {}
        summary = {}

        for brand in brands:
            # Scrape brand category
            products = self.scrape_brand_category(brand)

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
                'total_value_ils': sum(prices),
                'source': 'web_scrape_with_json_fallback'
            }

            # Save
            output_file = self.output_dir / \
                f"halilit_{brand.lower()}_full.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)

            logger.info(
                f"✓ Saved {len(products)} {brand} products to {output_file}")

        # Save merged and summary
        merged_file = self.output_dir / "halilit_full_merged.json"
        with open(merged_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

        summary_file = self.output_dir / "halilit_extraction_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        # Print summary
        logger.info(f"\n{'='*80}")
        logger.info("HALILIT SCRAPING COMPLETE")
        logger.info(f"{'='*80}")

        total_products = sum(stats['total_products']
                             for stats in summary.values())
        total_priced = sum(stats['with_pricing'] for stats in summary.values())
        total_value = sum(stats['total_value_ils']
                          for stats in summary.values())

        logger.info(f"\nTOTAL RESULTS:")
        logger.info(f"  All Products: {total_products}")
        logger.info(f"  With Pricing: {total_priced}")
        logger.info(f"  Total Catalog Value: ₪{total_value:,.0f}")

        for brand, stats in summary.items():
            logger.info(f"\n{brand}:")
            logger.info(f"  Total: {stats['total_products']}")
            logger.info(f"  With Pricing: {stats['with_pricing']}")
            if stats['avg_price_ils'] > 0:
                logger.info(
                    f"  Price Range: ₪{stats['min_price_ils']:,.0f} - ₪{stats['max_price_ils']:,.0f}")
                logger.info(f"  Avg Price: ₪{stats['avg_price_ils']:,.0f}")
                logger.info(f"  Total Value: ₪{stats['total_value_ils']:,.0f}")

        return all_data, summary


if __name__ == "__main__":
    scraper = HalilitCompleteScraper()
    scraper.run(["RCF", "Mackie"])
