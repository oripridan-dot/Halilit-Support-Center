#!/usr/bin/env python3
"""
THOMANN UNIFIED SCRAPING WORKFLOW
Comprehensive, production-ready scraper for all target brands
Brands: RCF, MACKIE, ALLEN&HEATH, MONTARBO, EAW
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass, asdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
EU_VAT_RATE = 0.19
BASE_URL = "https://www.thomannmusic.com/en/search"
TARGET_BRANDS = ["RCF", "MACKIE", "ALLEN&HEATH", "MONTARBO", "EAW"]

# Brand name variations to match
BRAND_ALIASES = {
    "RCF": ["RCF"],
    "MACKIE": ["Mackie", "Mackie Designs"],
    "ALLEN&HEATH": ["Allen & Heath", "Allen&Heath", "Allen and Heath"],
    "MONTARBO": ["Montarbo"],
    "EAW": ["EAW", "Eastern Acoustic Works"]
}

# Flattened list for quick lookup
ALL_BRAND_VARIANTS = set()
for variants in BRAND_ALIASES.values():
    for v in variants:
        ALL_BRAND_VARIANTS.add(v.upper())


@dataclass
class ThomannProduct:
    """Product data from Thomann"""
    product_id: str
    product_name: str
    brand: str
    category: str
    description: str
    specifications: str
    price_eur_base: float
    price_eur_with_vat_19pct: float
    shipping_estimate_eur: float
    total_with_vat_shipping_eur: float
    in_stock: str
    rating: Optional[float] = None
    review_count: Optional[int] = 0
    product_url: str = ""
    weight_kg: Optional[float] = None
    scraped_at: str = ""

    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        return asdict(self)


class ThomannUnifiedScraper:
    """Production-grade unified scraper"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        self.products = []
        self.seen_ids = set()
        self.brand_products = {brand: [] for brand in TARGET_BRANDS}

    def scrape_all_products(self, max_pages: int = 100) -> List[ThomannProduct]:
        """Scrape all products across all pages"""
        logger.info(f"\n{'='*70}")
        logger.info("🚀 STARTING COMPREHENSIVE THOMANN SCRAPE")
        logger.info(f"Target Brands: {', '.join(TARGET_BRANDS)}")
        logger.info(f"Max Pages: {max_pages}")
        logger.info(f"{'='*70}\n")

        all_products = []
        consecutive_errors = 0

        for page in range(1, max_pages + 1):
            try:
                logger.info(f"📄 Page {page}/{max_pages}")

                # Fetch page with simple pagination (no search parameter since it's ignored)
                url = f"{BASE_URL}?p={page}"
                response = self.session.get(url, timeout=20)

                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning(f"Rate limited (429). Waiting 60s...")
                    time.sleep(60)
                    continue

                if response.status_code != 200 and 'js-product' not in response.text:
                    logger.info(
                        f"No more products found on page {page}, stopping")
                    break

                # Parse page
                soup = BeautifulSoup(response.content, 'html.parser')
                product_elements = soup.find_all('a', class_='js-product')

                logger.info(
                    f"  Found {len(product_elements)} products on this page")

                if not product_elements:
                    logger.info("  No products to parse, stopping")
                    break

                # Extract products
                page_products = []
                for elem in product_elements:
                    try:
                        product = self._parse_product(elem)
                        if product and product.product_id not in self.seen_ids:
                            all_products.append(product)
                            self.seen_ids.add(product.product_id)

                            # Track by brand
                            for target_brand in TARGET_BRANDS:
                                if product.brand.upper() == target_brand.upper() or self._brand_matches(product.brand, target_brand):
                                    self.brand_products[target_brand].append(
                                        product)

                            page_products.append(product)
                    except Exception as e:
                        logger.debug(f"Error parsing product: {e}")
                        continue

                logger.info(f"  Added {len(page_products)} new products")
                consecutive_errors = 0

                # Respectful delay
                time.sleep(2)

            except Exception as e:
                logger.error(f"Error on page {page}: {e}")
                consecutive_errors += 1
                if consecutive_errors >= 3:
                    logger.warning("Too many consecutive errors, stopping")
                    break
                time.sleep(5)
                continue

        return all_products

    def _parse_product(self, element) -> Optional[ThomannProduct]:
        """Parse a single product element"""
        try:
            # Get href
            href = element.get('href', '')
            if not href:
                return None

            # Build URL
            if not href.startswith('http'):
                product_url = f"https://www.thomannmusic.com{href}" if href.startswith(
                    '/') else f"https://www.thomannmusic.com/{href}"
            else:
                product_url = href

            # Extract product ID
            product_id = href.rstrip('/').split('/')[-1].replace('.htm', '')
            if not product_id:
                return None

            # Get description with brand
            desc_div = element.find('div', class_='description')
            if not desc_div:
                return None

            manufacturer_elem = desc_div.find(
                'span', class_='description__manufacturer')
            brand = manufacturer_elem.get_text(
                strip=True) if manufacturer_elem else ""

            full_text = desc_div.get_text(' ', strip=True)
            product_name = full_text.replace(
                brand, '').strip() if brand else full_text
            product_name = product_name[:200] if product_name else full_text[:100]

            # Get price
            price_div = element.find('div', class_='price')
            if not price_div:
                return None

            price_span = price_div.find('span', class_='price__primary') or price_div.find(
                'span', class_='fx-typography-price-primary')
            if not price_span:
                return None

            price_text = price_span.get_text(strip=True)
            match = re.search(r'(\d+(?:[.,]\d{2})?)', price_text)
            if not match:
                return None

            price_str = match.group(1).replace(',', '.')
            try:
                base_price = float(price_str)
            except:
                return None

            # Calculate derived fields
            price_with_vat = base_price * (1 + EU_VAT_RATE)
            weight_kg = self._estimate_weight(product_name, brand)
            shipping = self._estimate_shipping(weight_kg)
            total = price_with_vat + shipping

            # Stock and rating
            stock_status = self._extract_stock(element)
            rating, review_count = self._extract_rating(element)

            product = ThomannProduct(
                product_id=product_id,
                product_name=product_name,
                brand=brand if brand else "Unknown",
                category=brand if brand else "Music Equipment",
                description=f"{brand} {product_name}".strip()[:300],
                specifications="",
                price_eur_base=base_price,
                price_eur_with_vat_19pct=round(price_with_vat, 2),
                shipping_estimate_eur=shipping,
                total_with_vat_shipping_eur=round(total, 2),
                in_stock=stock_status,
                rating=rating,
                review_count=review_count,
                product_url=product_url,
                weight_kg=weight_kg
            )

            return product

        except Exception as e:
            logger.debug(f"Error parsing product: {e}")
            return None

    def _brand_matches(self, brand_text: str, target_brand: str) -> bool:
        """Check if brand matches target"""
        if not brand_text:
            return False
        brand_upper = brand_text.upper()
        target_upper = target_brand.upper()

        if brand_upper == target_upper:
            return True

        # Check aliases
        if target_brand in BRAND_ALIASES:
            for variant in BRAND_ALIASES[target_brand]:
                if variant.upper() in brand_upper or brand_upper in variant.upper():
                    return True

        return False

    def _estimate_weight(self, name: str, category: str) -> float:
        """Estimate weight"""
        weight = 5.0
        combined = f"{category} {name}".lower()

        if 'microphone' in combined or 'mic' in combined:
            weight = 0.5
        elif 'cable' in combined:
            weight = 0.2
        elif 'speaker' in combined or 'monitor' in combined:
            weight = 15.0
        elif 'amplifier' in combined or 'amp' in combined:
            weight = 10.0
        elif 'mixer' in combined:
            weight = 8.0

        if 'compact' in combined or 'portable' in combined:
            weight *= 0.5
        elif 'pro' in combined:
            weight *= 1.3

        return round(weight, 1)

    def _estimate_shipping(self, weight_kg: float) -> float:
        """Estimate shipping"""
        if weight_kg < 2:
            return 12
        elif weight_kg < 10:
            return 18
        elif weight_kg < 30:
            return 35
        else:
            return 65

    def _extract_stock(self, element) -> str:
        """Extract stock status"""
        try:
            text = element.get_text().lower()
            if 'in stock' in text or 'available' in text:
                return "In Stock"
            return "Unknown"
        except:
            return "Unknown"

    def _extract_rating(self, element) -> tuple:
        """Extract rating and review count"""
        rating = None
        review_count = 0
        try:
            rating_container = element.find(
                'div', class_='rating-stars-container')
            if rating_container:
                filler = rating_container.find(
                    'div', class_='fx-rating-stars__filler')
                if filler:
                    style = filler.get('style', '')
                    match = re.search(r'width:\s*(\d+(?:\.\d+)?)', style)
                    if match:
                        percentage = float(match.group(1))
                        rating = round((percentage / 100) * 5, 1)

                desc = rating_container.find(
                    'div', class_='fx-rating-stars__description')
                if desc:
                    text = desc.get_text(strip=True)
                    m = re.search(r'(\d+)', text)
                    if m:
                        review_count = int(m.group(1))
        except:
            pass
        return rating, review_count

    def save_comprehensive_csv(self, products: List[ThomannProduct], output_path: str):
        """Save all products to CSV"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not products:
            logger.error("No products to save")
            return

        fieldnames = [
            'product_id', 'product_name', 'brand', 'category', 'description',
            'specifications', 'price_eur_base', 'price_eur_with_vat_19pct',
            'shipping_estimate_eur', 'total_with_vat_shipping_eur', 'in_stock',
            'rating', 'review_count', 'product_url', 'weight_kg', 'scraped_at'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for product in products:
                writer.writerow(product.to_dict())

        logger.info(f"\n✅ Saved {len(products)} products to {output_path}")

    def print_summary(self, products: List[ThomannProduct]):
        """Print comprehensive summary"""
        print(f"\n{'='*70}")
        print(f"✅ THOMANN SCRAPING COMPLETE")
        print(f"{'='*70}")
        print(f"📊 Total Products Scraped: {len(products)}")

        # By brand
        by_brand = {}
        for p in products:
            by_brand[p.brand] = by_brand.get(p.brand, 0) + 1

        print(f"\n📈 Products by Brand:")
        for brand in TARGET_BRANDS:
            count = sum(
                1 for p in products if self._brand_matches(p.brand, brand))
            print(f"  {brand}: {count} products")

        print(
            f"\n  Other manufacturers: {len([p for p in products if not any(self._brand_matches(p.brand, b) for b in TARGET_BRANDS)])} products")

        # Price statistics
        prices = [p.price_eur_base for p in products if p.price_eur_base > 0]
        if prices:
            print(f"\n💰 Price Statistics (Base EUR):")
            print(f"  Min: €{min(prices):.2f}")
            print(f"  Max: €{max(prices):.2f}")
            print(f"  Avg: €{sum(prices)/len(prices):.2f}")

        vat_prices = [
            p.price_eur_with_vat_19pct for p in products if p.price_eur_with_vat_19pct > 0]
        if vat_prices:
            print(f"\n💵 Price Statistics (With 19% VAT):")
            print(f"  Min: €{min(vat_prices):.2f}")
            print(f"  Max: €{max(vat_prices):.2f}")
            print(f"  Avg: €{sum(vat_prices)/len(vat_prices):.2f}")

        total_prices = [
            p.total_with_vat_shipping_eur for p in products if p.total_with_vat_shipping_eur > 0]
        if total_prices:
            print(f"\n🚚 Price Statistics (VAT + Shipping):")
            print(f"  Min: €{min(total_prices):.2f}")
            print(f"  Max: €{max(total_prices):.2f}")
            print(f"  Avg: €{sum(total_prices)/len(total_prices):.2f}")
            print(f"  Total Value: €{sum(total_prices):.2f}")

        print(f"{'='*70}\n")


def main():
    """Main execution"""
    scraper = ThomannUnifiedScraper()

    # Scrape all products
    products = scraper.scrape_all_products(max_pages=200)

    if products:
        # Save comprehensive CSV
        output_file = "/workspaces/Halilit-Support-Center/backend/reports/thomann_brands_report.csv"
        scraper.save_comprehensive_csv(products, output_file)

        # Print summary
        scraper.print_summary(products)
    else:
        logger.error("❌ No products scraped")


if __name__ == "__main__":
    main()
