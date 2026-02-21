"""
Thomannmusic.com Web Scraper with Full Pagination Support

Comprehensive scraper for thomannmusic.com that handles:
- Multiple product categories
- Full pagination crawling
- Data extraction with fallbacks
- Currency handling (EUR)
- Rate limiting and error handling
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
import time
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
import json
from urllib.parse import urljoin, urlencode
import re

logger = logging.getLogger(__name__)


@dataclass
class ThomannProduct:
    """Represents a product scraped from Thomann"""
    product_id: str
    product_name: str
    brand: str
    category: str
    subcategory: str
    price_eur: float
    price_gbp: Optional[float] = None
    price_usd: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    specifications: Optional[Dict] = None
    in_stock: Optional[str] = None  # "In Stock", "3-5 days", etc.
    rating: Optional[float] = None
    review_count: Optional[int] = None
    weight_kg: Optional[float] = None  # For shipping calculations
    scraped_at: str = ""
    source: str = "thomannmusic.com"

    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.utcnow().isoformat()


class ThomannScraper:
    """Web scraper for Thomannmusic.com with pagination support"""

    BASE_URL = "https://www.thomannmusic.com"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    REQUEST_TIMEOUT = 20
    RATE_LIMIT_DELAY = 2  # Base delay between requests (seconds)
    MAX_RETRIES = 3  # Maximum retries per page
    BACKOFF_MULTIPLIER = 2  # Exponential backoff multiplier

    # Product categories to scrape (with Thomann URL paths)
    CATEGORIES = {
        "Loudspeakers": "/loudspeakers.html",
        "Active Monitors": "/active-monitors.html",
        "Microphones": "/microphones.html",
        "Headphones": "/headphones.html",
        "Amplifiers": "/amplifiers.html",
        "Audio Cables": "/audio-cables.html",
        "Synthesizers": "/synthesizers.html",
        "Keyboards": "/keyboards.html",
        "Drums": "/drums.html",
        "Guitars": "/guitars.html",
        "Bass": "/bass-guitars.html",
        "Studio Furniture": "/studio-furniture.html",
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

    def scrape_all_categories(self) -> Tuple[List[ThomannProduct], Dict]:
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

            time.sleep(self.RATE_LIMIT_DELAY)

        stats["end_time"] = datetime.utcnow().isoformat()
        stats["unique_products"] = len(self.seen_product_ids)
        return self.scraped_products, stats

    def _scrape_category(
        self, category_name: str, category_url: str
    ) -> List[ThomannProduct]:
        """
        Scrape all pages in a category using pagination with exponential backoff.

        Handles rate limiting (429) and other errors gracefully.
        """
        category_products = []
        page = 1
        consecutive_errors = 0

        while page <= self.max_pages_per_category:
            # Build pagination URL
            if page == 1:
                url = urljoin(self.BASE_URL, category_url)
            else:
                base = category_url
                separator = "&" if "?" in base else "?"
                url = urljoin(self.BASE_URL, f"{base}{separator}page={page}")

            logger.debug(f"  Page {page}: {url}")

            # Retry logic with exponential backoff
            for attempt in range(1, self.MAX_RETRIES + 1):
                try:
                    # Calculate delay with backoff
                    delay = self.RATE_LIMIT_DELAY * \
                        (self.BACKOFF_MULTIPLIER ** (attempt - 1))
                    if attempt > 1:
                        logger.info(
                            f"  ⏳ Retry #{attempt} for {category_name} page {page} (waiting {delay}s)")
                        time.sleep(delay)
                    else:
                        # Normal rate limiting on first attempt
                        if page > 1:
                            time.sleep(self.RATE_LIMIT_DELAY)

                    response = self.session.get(
                        url, timeout=self.REQUEST_TIMEOUT)

                    # Handle rate limiting gracefully
                    if response.status_code == 429:
                        if attempt < self.MAX_RETRIES:
                            logger.warning(
                                f"Rate limited (429) on {category_name} - retrying...")
                            continue
                        else:
                            logger.error(
                                f"Rate limited (429) on {category_name} - max retries reached")
                            return category_products

                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, "lxml")

                    # Check if page is empty (loaded but no content)
                    if not soup.body or len(soup.body.text.strip()) < 100:
                        logger.debug(f"  Empty page {page}, stopping")
                        return category_products

                    products_on_page = self._extract_products(
                        soup, category_name, response.url
                    )

                    if not products_on_page:
                        logger.debug(f"  No products on page {page}, stopping")
                        return category_products

                    category_products.extend(products_on_page)
                    consecutive_errors = 0  # Reset error counter on success

                    # Check for next page indicator
                    if not self._has_next_page(soup):
                        logger.debug(f"  Last page reached at page {page}")
                        return category_products

                    page += 1
                    break  # Break retry loop on success

                except requests.exceptions.Timeout:
                    logger.warning(
                        f"Timeout on {category_name} page {page}, attempt {attempt}/{self.MAX_RETRIES}")
                    if attempt == self.MAX_RETRIES:
                        return category_products

                except requests.exceptions.ConnectionError as e:
                    logger.warning(
                        f"Connection error on {category_name}: {e}, attempt {attempt}/{self.MAX_RETRIES}")
                    if attempt == self.MAX_RETRIES:
                        return category_products

                except requests.RequestException as e:
                    logger.warning(
                        f"HTTP error on {category_name} page {page}: {e}")
                    if "404" in str(e):
                        # 404 means URL doesn't exist, skip this category
                        logger.warning(f"  Category URL not found: {url}")
                        return category_products
                    elif attempt == self.MAX_RETRIES:
                        return category_products

                except Exception as e:
                    logger.warning(
                        f"Parse error on {category_name} page {page}: {e}")
                    if attempt == self.MAX_RETRIES:
                        return category_products

        return category_products

    def _extract_products(
        self, soup: BeautifulSoup, category_name: str, page_url: str
    ) -> List[ThomannProduct]:
        """
        Extract product data from a parsed Thomann page.

        Thomann uses specific HTML classes for product listing.
        """
        products = []

        # Thomann typically uses article.product-item or div with data attributes
        product_containers = (
            soup.find_all("article", class_="product-item")
            or soup.find_all("div", class_="product-item")
            or soup.find_all("div", {"data-product-id": True})
            or soup.find_all("div", class_=re.compile("product", re.I))
        )

        for container in product_containers:
            try:
                product = self._parse_product(
                    container, category_name, page_url)
                if product:
                    if product.product_id not in self.seen_product_ids:
                        products.append(product)
                        self.seen_product_ids.add(product.product_id)
            except Exception as e:
                logger.debug(f"Error parsing product: {e}")
                continue

        return products

    def _parse_product(
        self, container, category_name: str, page_url: str
    ) -> Optional[ThomannProduct]:
        """
        Extract data from a single product container.
        """
        # Product name
        name_elem = container.find(
            ["h3", "h2", "a"], class_=re.compile("name|title|product-name", re.I)
        )
        product_name = name_elem.get_text(strip=True) if name_elem else None

        if not product_name:
            return None

        # Product URL and ID
        link_elem = container.find("a", href=True)
        product_url = link_elem["href"] if link_elem else None
        if product_url and not product_url.startswith("http"):
            product_url = urljoin(self.BASE_URL, product_url)

        # Extract product ID
        product_id = container.get("data-product-id") or self._extract_product_id(
            product_url
        )
        if not product_id:
            product_id = self._hash_product(product_name)

        # Brand
        brand = self._extract_brand(product_name)

        # Price in EUR
        price_elem = container.find(
            ["span", "div"], class_=re.compile("price|cost", re.I)
        )
        price_text = price_elem.get_text(strip=True) if price_elem else None
        price_eur = self._parse_price(price_text)

        if price_eur is None or price_eur <= 0:
            return None

        # Image
        img_elem = container.find("img")
        image_url = img_elem.get("src") or img_elem.get(
            "data-src") if img_elem else None
        if image_url and not image_url.startswith("http"):
            image_url = urljoin(self.BASE_URL, image_url)

        # Stock status
        stock_elem = container.find(
            ["span", "div"], class_=re.compile("stock|availability", re.I)
        )
        in_stock = stock_elem.get_text(strip=True) if stock_elem else None

        # Description
        desc_elem = container.find(
            ["p", "span"], class_=re.compile("description|desc"))
        description = desc_elem.get_text(strip=True) if desc_elem else None

        # Rating
        rating_elem = container.find(
            ["span", "div"], class_=re.compile("rating|stars"))
        rating = None
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            try:
                rating = float(re.findall(r"[\d.]+", rating_text)[0])
            except (ValueError, IndexError):
                pass

        # Weight (for shipping calculation)
        weight = None
        specs_elem = container.find(
            ["div", "span"], class_=re.compile("specs|weight"))
        if specs_elem:
            weight_text = specs_elem.get_text(strip=True)
            try:
                weight = float(re.findall(r"[\d.]+", weight_text)[0])
            except (ValueError, IndexError):
                pass

        return ThomannProduct(
            product_id=product_id,
            product_name=product_name,
            brand=brand,
            category=category_name,
            subcategory="",
            price_eur=price_eur,
            description=description,
            image_url=image_url,
            product_url=product_url,
            in_stock=in_stock,
            rating=rating,
            weight_kg=weight,
        )

    def _extract_product_id(self, url: str) -> Optional[str]:
        """Extract product ID from Thomann URL"""
        if not url:
            return None
        try:
            # ID usually in path like /pr12345 or at end of slug
            match = re.search(r"/pr(\d+)", url)
            if match:
                return match.group(1)

            # Try to get from query params
            if "id=" in url:
                return re.search(r"id=(\d+)", url).group(1)

            # Extract longest number sequence
            numbers = re.findall(r"\d+", url)
            return numbers[-1] if numbers else None
        except Exception:
            pass
        return None

    def _extract_brand(self, product_name: str) -> str:
        """Extract brand from product name"""
        known_brands = [
            "Montarbo",
            "EAW",
            "RCF",
            "Mackie",
            "Roland",
            "Yamaha",
            "Korg",
            "Nord",
            "Elektron",
            "Shure",
            "AKG",
            "Rode",
            "Sennheiser",
            "Audio-Technica",
            "Behringer",
            "Moog",
            "Sequential",
        ]

        for brand in known_brands:
            if brand.lower() in product_name.lower():
                return brand

        return product_name.split()[0]

    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse EUR price from text"""
        if not price_text:
            return None

        try:
            # Remove currency symbols
            price_clean = (
                price_text.replace("€", "")
                .replace("£", "")
                .replace("$", "")
                .replace(",", ".")
                .strip()
            )

            # Extract first number
            match = re.search(r"[\d.]+", price_clean)
            return float(match.group()) if match else None
        except (ValueError, AttributeError):
            return None

    def _has_next_page(self, soup: BeautifulSoup) -> bool:
        """Check if there's a next page"""
        # Look for next pagination link
        next_link = soup.find("a", {"rel": "next"}) or soup.find(
            "a", string=lambda s: s and "next" in s.lower()
        )

        if next_link:
            return True

        # Check pagination element
        pagination = soup.find("ul", class_=re.compile("pagination|pager"))
        if pagination:
            current = pagination.find(
                "li", class_=re.compile("active|current"))
            return current is not None

        return False

    def _hash_product(self, product_name: str) -> str:
        """Generate ID from product name"""
        import hashlib

        return hashlib.md5(product_name.encode()).hexdigest()[:12]

    def export_to_json(self, products: List[ThomannProduct], filepath: str):
        """Export products to JSON"""
        data = {
            "total": len(products),
            "products": [asdict(p) for p in products],
            "exported_at": datetime.utcnow().isoformat(),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(products)} products to {filepath}")

    def dedup_products(self) -> List[ThomannProduct]:
        """Remove duplicates"""
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

    scraper = ThomannScraper(max_pages_per_category=999)
    products, stats = scraper.scrape_all_categories()

    print(f"\n✅ Scraping complete:")
    print(f"   Total products: {stats['total_products']}")
    print(
        f"   Categories: {stats['categories_scraped']}/{len(scraper.CATEGORIES)}")
    print(f"   Errors: {stats['categories_failed']}")

    unique_products = scraper.dedup_products()
    print(f"   Unique products: {len(unique_products)}")

    scraper.export_to_json(unique_products, "/tmp/thomann_products.json")
