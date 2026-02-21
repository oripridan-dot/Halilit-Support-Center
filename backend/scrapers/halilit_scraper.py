"""
Halilit.com Web Scraper with Full Pagination Support

Comprehensive scraper for halilit.com that handles:
- Multiple product categories
- Full pagination crawling
- Data extraction with fallbacks
- Rate limiting and error handling
- Deduplication
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
import time
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
import json
from urllib.parse import urljoin, parse_qs, urlparse

logger = logging.getLogger(__name__)


@dataclass
class HalilitProduct:
    """Represents a product scraped from Halilit"""
    product_id: str
    product_name: str
    brand: str
    category: str
    subcategory: str
    price_ils: float
    price_eilat_ils: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    specifications: Optional[Dict] = None
    in_stock: Optional[bool] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    scraped_at: str = ""
    source: str = "halilit.com"

    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.utcnow().isoformat()


class HalilitScraper:
    """Web scraper for Halilit.com with pagination support"""

    BASE_URL = "https://www.halilit.com"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    REQUEST_TIMEOUT = 15
    RATE_LIMIT_DELAY = 1  # seconds between requests

    # Product categories to scrape
    CATEGORIES = {
        "PA Speakers": "/5-pa-speakers",
        "Studio Monitors": "/6-studio-monitors",
        "Microphones": "/8-microphones",
        "Amplifiers": "/10-amplifiers",
        "Cables": "/12-cables",
        "Headphones": "/18-headphones",
        "Synthesizers": "/20-synthesizers",
        "Keyboards": "/21-keyboards",
        "Drums": "/22-drums",
        "Guitars": "/23-guitars",
        "Bass": "/24-bass",
        "Percussion": "/25-percussion",
    }

    def __init__(self, max_pages_per_category: int = 999):
        """
        Initialize scraper.

        Args:
            max_pages_per_category: Maximum pages to scrape per category
        """
        self.max_pages_per_category = max_pages_per_category
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.scraped_products = []
        self.seen_product_ids = set()

    def scrape_all_categories(self) -> Tuple[List[HalilitProduct], Dict]:
        """
        Scrape all categories with complete pagination.

        Returns:
            Tuple of (list of products, summary statistics)
        """
        stats = {
            "total_products": 0,
            "categories_scraped": 0,
            "categories_failed": 0,
            "errors": [],
            "start_time": datetime.utcnow().isoformat(),
        }

        for category_name, category_url in self.CATEGORIES.items():
            try:
                logger.info(f"Scraping category: {category_name}")
                products = self._scrape_category(category_name, category_url)
                self.scraped_products.extend(products)
                stats["categories_scraped"] += 1
                stats["total_products"] += len(products)
                logger.info(f"  → {len(products)} products found")
            except Exception as e:
                logger.error(f"Failed to scrape {category_name}: {e}")
                stats["categories_failed"] += 1
                stats["errors"].append(f"{category_name}: {str(e)}")

            # Rate limiting
            time.sleep(self.RATE_LIMIT_DELAY)

        stats["end_time"] = datetime.utcnow().isoformat()
        stats["unique_products"] = len(self.seen_product_ids)
        return self.scraped_products, stats

    def _scrape_category(
        self, category_name: str, category_url: str
    ) -> List[HalilitProduct]:
        """
        Scrape all pages in a category.

        Args:
            category_name: Display name of category
            category_url: URL path for category

        Returns:
            List of products from category
        """
        category_products = []
        page = 1

        while page <= self.max_pages_per_category:
            # Build pagination URL
            if page == 1:
                url = urljoin(self.BASE_URL, category_url)
            else:
                url = urljoin(self.BASE_URL, f"{category_url}?p={page}")

            logger.debug(f"  Page {page}: {url}")

            try:
                # Fetch page
                response = self.session.get(url, timeout=self.REQUEST_TIMEOUT)
                response.raise_for_status()

                # Parse products
                soup = BeautifulSoup(response.content, "lxml")
                products_on_page = self._extract_products(
                    soup, category_name, response.url
                )

                if not products_on_page:
                    # No products found, assume end of pagination
                    logger.debug(f"  No products on page {page}, stopping")
                    break

                category_products.extend(products_on_page)

                # Check if there's a next page
                if not self._has_next_page(soup):
                    logger.debug(f"  Last page reached at page {page}")
                    break

                page += 1
                time.sleep(self.RATE_LIMIT_DELAY)

            except requests.RequestException as e:
                logger.warning(f"Request error on page {page}: {e}")
                break
            except Exception as e:
                logger.warning(f"Error parsing page {page}: {e}")
                page += 1

        return category_products

    def _extract_products(
        self, soup: BeautifulSoup, category_name: str, page_url: str
    ) -> List[HalilitProduct]:
        """
        Extract product data from a parsed page.

        Looks for common product listing HTML patterns on Halilit.
        """
        products = []

        # Try multiple selectors for product containers
        product_containers = (
            soup.find_all("div", class_="product-item")
            or soup.find_all("div", class_="product")
            or soup.find_all("article", class_="product")
            or soup.find_all("div", {"data-product": True})
        )

        for container in product_containers:
            try:
                product = self._parse_product(
                    container, category_name, page_url)
                if product:
                    # Check for duplicates
                    if product.product_id not in self.seen_product_ids:
                        products.append(product)
                        self.seen_product_ids.add(product.product_id)
            except Exception as e:
                logger.debug(f"Error parsing product: {e}")
                continue

        return products

    def _parse_product(
        self, container, category_name: str, page_url: str
    ) -> Optional[HalilitProduct]:
        """
        Extract data from a single product container.

        Handles multiple HTML structures with fallbacks.
        """
        # Product name
        name_elem = container.find(
            ["h2", "h3", "a"], class_=["product-name", "name", "title"]
        )
        product_name = name_elem.get_text(strip=True) if name_elem else None

        if not product_name:
            return None

        # Product URL and ID
        link_elem = container.find("a", href=True)
        product_url = link_elem["href"] if link_elem else None
        if product_url and not product_url.startswith("http"):
            product_url = urljoin(self.BASE_URL, product_url)

        # Extract product ID from URL
        product_id = self._extract_product_id(product_url) or self._hash_product(
            product_name
        )

        # Brand (often in title or separate field)
        brand = self._extract_brand(product_name)

        # Price
        price_elem = container.find(
            ["span", "div"], class_=["price", "product-price", "price-now"]
        )
        price_text = price_elem.get_text(strip=True) if price_elem else None
        price_ils = self._parse_price(price_text)

        if price_ils is None or price_ils <= 0:
            return None

        # Eilat price (sometimes shown)
        eilat_elem = container.find(
            ["span", "div"], class_=["eilat-price", "price-eilat", "special-price"]
        )
        price_eilat_text = eilat_elem.get_text(
            strip=True) if eilat_elem else None
        price_eilat = self._parse_price(price_eilat_text)

        # Image
        img_elem = container.find("img")
        image_url = img_elem.get("src") if img_elem else None
        if image_url and not image_url.startswith("http"):
            image_url = urljoin(self.BASE_URL, image_url)

        # Subcategory (if available)
        subcat_elem = container.find(["span", "div"], class_=["subcategory"])
        subcategory = subcat_elem.get_text(strip=True) if subcat_elem else ""

        # In stock indicator
        in_stock = not bool(
            container.find(
                ["span", "div"],
                class_=["out-of-stock", "unavailable", "no-stock"],
            )
        )

        # Description/short text
        desc_elem = container.find(
            ["p", "span", "div"], class_=["description", "short-desc"]
        )
        description = desc_elem.get_text(strip=True) if desc_elem else None

        # Rating (if available)
        rating_elem = container.find(
            ["span", "div"], class_=["rating", "stars"])
        rating = None
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            try:
                rating = float(rating_text.split()[0])
            except (ValueError, IndexError):
                pass

        return HalilitProduct(
            product_id=product_id,
            product_name=product_name,
            brand=brand,
            category=category_name,
            subcategory=subcategory,
            price_ils=price_ils,
            price_eilat_ils=price_eilat,
            description=description,
            image_url=image_url,
            product_url=product_url,
            in_stock=in_stock,
            rating=rating,
        )

    def _extract_product_id(self, url: str) -> Optional[str]:
        """Extract product ID from Halilit URL (e.g., 22555 from /22555-pa-speakers)"""
        if not url:
            return None
        try:
            parts = url.strip("/").split("?")[0].split("/")
            for part in parts:
                if part.isdigit():
                    return part
        except Exception:
            pass
        return None

    def _extract_brand(self, product_name: str) -> str:
        """Extract brand name from product name"""
        # Common brands - could be expanded
        known_brands = [
            "Montarbo",
            "EAW",
            "RCF",
            "Mackie",
            "Akai",
            "Roland",
            "Yamaha",
            "Nord",
            "Korg",
            "Elektron",
            "Shure",
            "AKG",
            "Rode",
            "Sennheiser",
            "Audio-Technica",
            "Behringer",
        ]

        for brand in known_brands:
            if brand.lower() in product_name.lower():
                return brand

        # Extract first word as fallback
        return product_name.split()[0]

    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price from text (e.g., '₪ 1,234.50' -> 1234.50)"""
        if not price_text:
            return None

        try:
            # Remove currency symbols and spaces
            price_clean = (
                price_text.replace("₪", "")
                .replace("$", "")
                .replace("€", "")
                .replace(",", "")
                .strip()
            )

            # Extract first number
            price_str = "".join(
                c for c in price_clean if c.isdigit() or c == ".")
            return float(price_str) if price_str else None
        except (ValueError, IndexError):
            return None

    def _has_next_page(self, soup: BeautifulSoup) -> bool:
        """Check if pagination suggests there's a next page"""
        # Look for "Next" link
        next_link = soup.find("a", {"rel": "next"}) or soup.find(
            "a", string=lambda s: s and "next" in s.lower()
        )

        if next_link:
            return True

        # Check for pagination indicators
        pagination = soup.find("ul", class_=["pagination", "pager"])
        if pagination:
            # If current page doesn't have "disabled" or is last, assume there's next
            current = pagination.find("li", class_="active")
            return current is not None

        return False

    def _hash_product(self, product_name: str) -> str:
        """Generate ID from product name for deduplication"""
        import hashlib

        return hashlib.md5(product_name.encode()).hexdigest()[:12]

    def export_to_json(self, products: List[HalilitProduct], filepath: str):
        """Export scraped products to JSON"""
        data = {
            "total": len(products),
            "products": [asdict(p) for p in products],
            "exported_at": datetime.utcnow().isoformat(),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(products)} products to {filepath}")

    def dedup_products(self) -> List[HalilitProduct]:
        """Remove duplicate products from scraped list"""
        seen = set()
        unique = []

        for product in self.scraped_products:
            key = (
                product.brand.lower(),
                product.product_name.lower(),
                product.category,
            )
            if key not in seen:
                seen.add(key)
                unique.append(product)

        self.scraped_products = unique
        return unique


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scraper = HalilitScraper(max_pages_per_category=999)  # scrape all pages
    products, stats = scraper.scrape_all_categories()

    print(f"\n✅ Scraping complete:")
    print(f"   Total products: {stats['total_products']}")
    print(
        f"   Categories: {stats['categories_scraped']}/{len(scraper.CATEGORIES)}")
    print(f"   Errors: {stats['categories_failed']}")

    # Deduplicate
    unique_products = scraper.dedup_products()
    print(f"   Unique products: {len(unique_products)}")

    # Export
    scraper.export_to_json(unique_products, "/tmp/halilit_products.json")
