"""
Complete Data Ingestion Orchestrator

Manages:
- Running web scrapers for both Halilit and Thomann
- Storing products in SQLite database
- Normalizing/cleaning data
- Generating comprehensive comparison reports
"""

import logging
import json
from datetime import datetime
from pathlib import Path
import sqlite3
from typing import List, Dict, Tuple, Optional
from dataclasses import asdict

from backend.scrapers.halilit_scraper import HalilitScraper, HalilitProduct
from backend.scrapers.thomann_scraper import ThomannScraper, ThomannProduct

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent / "ingestion" / "products.db"


class ProductDatabase:
    """SQLite database for product storage"""

    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Halilit products table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS halilit_products (
                    id TEXT PRIMARY KEY,
                    product_name TEXT NOT NULL,
                    brand TEXT,
                    category TEXT,
                    subcategory TEXT,
                    price_ils REAL,
                    price_eilat_ils REAL,
                    description TEXT,
                    image_url TEXT,
                    product_url TEXT,
                    in_stock INTEGER,
                    rating REAL,
                    review_count INTEGER,
                    scraped_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Thomann products table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS thomann_products (
                    id TEXT PRIMARY KEY,
                    product_name TEXT NOT NULL,
                    brand TEXT,
                    category TEXT,
                    subcategory TEXT,
                    price_eur REAL,
                    price_gbp REAL,
                    price_usd REAL,
                    description TEXT,
                    image_url TEXT,
                    product_url TEXT,
                    in_stock TEXT,
                    rating REAL,
                    review_count INTEGER,
                    weight_kg REAL,
                    scraped_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Comparison results table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS comparisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    halilit_product_id TEXT,
                    thomann_product_id TEXT,
                    brand TEXT,
                    product_name TEXT,
                    halilit_price_ils REAL,
                    thomann_total_ils REAL,
                    price_difference_percent REAL,
                    cheaper_at TEXT,
                    confidence_score REAL,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (halilit_product_id) REFERENCES halilit_products(id),
                    FOREIGN KEY (thomann_product_id) REFERENCES thomann_products(id)
                )
            """
            )

            conn.commit()

    def insert_halilit_products(self, products: List[HalilitProduct]):
        """Bulk insert Halilit products"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Clear old data
            cursor.execute("DELETE FROM halilit_products")

            # Insert new data
            for product in products:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO halilit_products
                    (id, product_name, brand, category, subcategory, price_ils,
                     price_eilat_ils, description, image_url, product_url, in_stock,
                     rating, review_count, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        product.product_id,
                        product.product_name,
                        product.brand,
                        product.category,
                        product.subcategory,
                        product.price_ils,
                        product.price_eilat_ils,
                        product.description,
                        product.image_url,
                        product.product_url,
                        int(product.in_stock) if product.in_stock else None,
                        product.rating,
                        product.review_count,
                        product.scraped_at,
                    ),
                )

            conn.commit()
            logger.info(
                f"Inserted {len(products)} Halilit products into database")

    def insert_thomann_products(self, products: List[ThomannProduct]):
        """Bulk insert Thomann products"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Clear old data
            cursor.execute("DELETE FROM thomann_products")

            # Insert new data
            for product in products:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO thomann_products
                    (id, product_name, brand, category, subcategory, price_eur,
                     price_gbp, price_usd, description, image_url, product_url,
                     in_stock, rating, review_count, weight_kg, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        product.product_id,
                        product.product_name,
                        product.brand,
                        product.category,
                        product.subcategory,
                        product.price_eur,
                        product.price_gbp,
                        product.price_usd,
                        product.description,
                        product.image_url,
                        product.product_url,
                        product.in_stock,
                        product.rating,
                        product.review_count,
                        product.weight_kg,
                        product.scraped_at,
                    ),
                )

            conn.commit()
            logger.info(
                f"Inserted {len(products)} Thomann products into database")

    def get_all_halilit_products(self) -> List[Dict]:
        """Fetch all Halilit products"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM halilit_products")
            return [dict(row) for row in cursor.fetchall()]

    def get_all_thomann_products(self) -> List[Dict]:
        """Fetch all Thomann products"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM thomann_products")
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM halilit_products")
            halilit_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM thomann_products")
            thomann_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM comparisons")
            comparison_count = cursor.fetchone()[0]

            return {
                "halilit_products": halilit_count,
                "thomann_products": thomann_count,
                "comparisons": comparison_count,
            }


class IngestionOrchestrator:
    """Orchestrates complete data ingestion workflow"""

    def __init__(self):
        self.db = ProductDatabase()
        self.halilit_scraper = HalilitScraper(max_pages_per_category=999)
        self.thomann_scraper = ThomannScraper(max_pages_per_category=999)

    def run_full_ingestion(self, skip_halilit: bool = False, skip_thomann: bool = False) -> Dict:
        """
        Run complete ingestion pipeline for both retailers.

        Args:
            skip_halilit: Skip Halilit scraping (for testing)
            skip_thomann: Skip Thomann scraping (for testing)

        Returns:
            Summary statistics
        """
        stats = {
            "start_time": datetime.utcnow().isoformat(),
            "halilit": None,
            "thomann": None,
            "database": None,
            "end_time": None,
        }

        try:
            # Scrape Halilit
            if not skip_halilit:
                logger.info("=" * 60)
                logger.info("🔍 SCRAPING HALILIT.COM")
                logger.info("=" * 60)

                halilit_products, halilit_stats = self.halilit_scraper.scrape_all_categories()
                halilit_products = self.halilit_scraper.dedup_products()

                stats["halilit"] = {
                    "total_products": len(halilit_products),
                    "categories_scraped": halilit_stats["categories_scraped"],
                    "errors": halilit_stats["errors"],
                }

                # Store in database
                self.db.insert_halilit_products(halilit_products)
                logger.info(
                    f"✅ Stored {len(halilit_products)} unique Halilit products")

            # Scrape Thomann
            if not skip_thomann:
                logger.info("\n" + "=" * 60)
                logger.info("🔍 SCRAPING THOMANNMUSIC.COM")
                logger.info("=" * 60)

                thomann_products, thomann_stats = self.thomann_scraper.scrape_all_categories()
                thomann_products = self.thomann_scraper.dedup_products()

                stats["thomann"] = {
                    "total_products": len(thomann_products),
                    "categories_scraped": thomann_stats["categories_scraped"],
                    "errors": thomann_stats["errors"],
                }

                # Store in database
                self.db.insert_thomann_products(thomann_products)
                logger.info(
                    f"✅ Stored {len(thomann_products)} unique Thomann products")

            # Get database stats
            stats["database"] = self.db.get_stats()
            stats["end_time"] = datetime.utcnow().isoformat()

            logger.info("\n" + "=" * 60)
            logger.info("📊 INGESTION SUMMARY")
            logger.info("=" * 60)
            logger.info(
                f"Halilit products: {stats['database']['halilit_products']}")
            logger.info(
                f"Thomann products: {stats['database']['thomann_products']}")
            logger.info("=" * 60)

            return stats

        except Exception as e:
            logger.error(f"Ingestion failed: {e}", exc_info=True)
            raise

    def export_database_to_json(self):
        """Export database to JSON files for API use"""
        halilit_products = self.db.get_all_halilit_products()
        thomann_products = self.db.get_all_thomann_products()

        # Export Halilit
        with open(
            Path(__file__).parent / "ingestion" /
            "halilit_products_full.json", "w"
        ) as f:
            json.dump(
                {
                    "source": "halilit.com",
                    "count": len(halilit_products),
                    "products": halilit_products,
                    "exported_at": datetime.utcnow().isoformat(),
                },
                f,
                indent=2,
                default=str,
            )

        # Export Thomann
        with open(
            Path(__file__).parent / "ingestion" /
            "thomann_products_full.json", "w"
        ) as f:
            json.dump(
                {
                    "source": "thomannmusic.com",
                    "count": len(thomann_products),
                    "products": thomann_products,
                    "exported_at": datetime.utcnow().isoformat(),
                },
                f,
                indent=2,
                default=str,
            )

        logger.info(
            f"✅ Exported {len(halilit_products)} Halilit + "
            f"{len(thomann_products)} Thomann products to JSON"
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    orchestrator = IngestionOrchestrator()

    # Run full ingestion
    stats = orchestrator.run_full_ingestion()

    # Export to JSON
    orchestrator.export_database_to_json()

    print("\n✅ Ingestion complete!")
    print(json.dumps(stats, indent=2))
