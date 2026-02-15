#!/usr/bin/env python3
"""
Batch Catalog Enrichment Script
================================
Processes all existing brand JSON files and enriches products by:
1. Scraping individual Halilit product pages for JSON-LD data
2. Optionally attempting official brand page scraping
3. Deduplicating products across variant brand files
4. Saving enriched data back to disk

Usage:
    # Enrich all brands
    python -m backend.scripts.enrich_catalog

    # Enrich specific brand
    python -m backend.scripts.enrich_catalog --brand "adam-audio"

    # Dry run (don't save)
    python -m backend.scripts.enrich_catalog --dry-run

    # With official brand scraping (slower)
    python -m backend.scripts.enrich_catalog --official
"""

from backend.ingestion.halilit_page_scraper import HalilitPageScraper
import argparse
import json
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Setup path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("enrich_catalog")

DATA_DIR = ROOT / "frontend" / "public" / "data"
EXCLUDED_FILES = {
    "index.json", "search_index.json", "search_index_min.json",
    "galaxy_db.json", "package.json",
}


def load_brand_file(path: Path) -> Tuple[List[dict], str]:
    """Load products from a brand JSON file. Returns (products, format_type)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data, "list"
    elif isinstance(data, dict) and "products" in data:
        return data["products"], "dict"
    else:
        return [], "unknown"


def save_brand_file(path: Path, products: List[dict], format_type: str):
    """Save products back in the original format."""
    if format_type == "list":
        data = products
    elif format_type == "dict":
        with open(path, "r", encoding="utf-8") as f:
            original = json.load(f)
        original["products"] = products
        data = original
    else:
        data = products

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def is_real_halilit_url(url: str) -> bool:
    """Check if URL is a real Halilit product page URL."""
    if not url:
        return False
    return (
        "halilit.com" in url
        and "/items/" in url
        and "halilit.com/search" not in url
    )


def _enrich_one(product: dict, scraper: HalilitPageScraper) -> Tuple[dict, Dict[str, int]]:
    """
    Enrich a single product; returns (enriched_product, stats_delta).
    Used for parallel processing so we don't share mutable stats.
    """
    url = product.get("halilit_url") or product.get("source_url") or ""

    if not is_real_halilit_url(url):
        return product, {"skipped_no_url": 1}

    has_desc = bool(product.get("official_description") or product.get("description"))
    has_price = bool(product.get("price") or product.get("price_il"))
    has_image = bool(product.get("image_url"))
    has_gallery = len(product.get("gallery_images") or product.get("image_gallery") or []) > 1

    if has_desc and has_price and has_image and has_gallery:
        return product, {"skipped_already_rich": 1}

    try:
        page_data = scraper.scrape_product_page(url)
        if not page_data:
            return product, {"scrape_failed": 1}

        enriched = dict(product)
        if page_data.get("description") and not has_desc:
            enriched["official_description"] = page_data["description"]
            enriched["page_description"] = page_data["description"]
        if page_data.get("price") and not has_price:
            enriched["price"] = page_data["price"]
            enriched["price_il"] = page_data["price"]
        if page_data.get("gallery_images") and not has_gallery:
            enriched["gallery_images"] = page_data["gallery_images"]
        if page_data.get("image_gallery") and not has_gallery:
            enriched["image_gallery"] = page_data["image_gallery"]
            if not enriched.get("gallery_images"):
                enriched["gallery_images"] = page_data["image_gallery"]
        if not product.get("image_url"):
            if page_data.get("image_url"):
                enriched["image_url"] = page_data["image_url"]
            elif page_data.get("image"):
                enriched["image_url"] = page_data["image"]
        if page_data.get("official_images") and not product.get("official_images"):
            enriched["official_images"] = page_data["official_images"]
        if page_data.get("sku") and not product.get("sku"):
            enriched["sku"] = page_data["sku"]
        if page_data.get("features") and not product.get("features"):
            enriched["features"] = page_data["features"]
        if page_data.get("faq") and not product.get("faq"):
            enriched["faq"] = page_data["faq"]
        if page_data.get("audiences") and not product.get("audiences"):
            enriched["audiences"] = page_data["audiences"]

        return enriched, {"scraped": 1}

    except Exception as e:
        logger.warning(f"Error scraping {url}: {e}")
        return product, {"scrape_error": 1}


def enrich_product(product: dict, scraper: HalilitPageScraper,
                   stats: dict) -> dict:
    """Enrich a single product by scraping its Halilit page (mutates stats)."""
    enriched, delta = _enrich_one(product, scraper)
    for k, v in delta.items():
        stats[k] = stats.get(k, 0) + v
    return enriched


def find_duplicate_brand_files() -> List[Tuple[str, List[Path]]]:
    """Find brand files that likely represent the same brand."""
    brand_groups: Dict[str, List[Path]] = {}

    for f in sorted(DATA_DIR.glob("*.json")):
        if f.name in EXCLUDED_FILES:
            continue
        # Normalize: "adam audio.json" -> "adam-audio", "adam-audio.json" -> "adam-audio"
        key = f.stem.lower().replace(" ", "-").replace("_", "-")
        brand_groups.setdefault(key, []).append(f)

    return [(k, v) for k, v in brand_groups.items() if len(v) > 1]


def merge_duplicate_brands(dry_run: bool = False):
    """Merge duplicate brand files (e.g., 'adam audio.json' + 'adam-audio.json')."""
    dupes = find_duplicate_brand_files()

    if not dupes:
        logger.info("No duplicate brand files found")
        return

    for key, files in dupes:
        logger.info(f"Duplicate brand: {key} -> {[f.name for f in files]}")

        if dry_run:
            continue

        # Load all products from all files
        all_products: Dict[str, dict] = {}  # id -> product
        primary_format = "list"

        for f in files:
            products, fmt = load_brand_file(f)
            if f == files[0]:
                primary_format = fmt
            for p in products:
                pid = p.get("id") or p.get("halilit_id") or p.get("sku", "")
                if pid and pid not in all_products:
                    all_products[pid] = p

        # Save merged to the hyphenated version, delete the others
        primary = None
        for f in files:
            if "-" in f.stem:
                primary = f
                break
        if not primary:
            primary = files[0]

        save_brand_file(primary, list(all_products.values()), primary_format)
        logger.info(
            f"  Merged {len(all_products)} products into {primary.name}")

        for f in files:
            if f != primary:
                f.unlink()
                logger.info(f"  Deleted duplicate: {f.name}")


def enrich_brand_file(
    path: Path,
    scraper: HalilitPageScraper,
    dry_run: bool = False,
    delay: float = 0.5,
    concurrent_products: int = 1,
) -> dict:
    """Enrich all products in a brand JSON file. Use concurrent_products > 1 to scrape multiple pages at once per file."""
    products, fmt = load_brand_file(path)
    if not products:
        return {"file": path.name, "total": 0}

    stats = {
        "file": path.name,
        "total": len(products),
        "scraped": 0,
        "skipped_no_url": 0,
        "skipped_already_rich": 0,
        "scrape_failed": 0,
        "scrape_error": 0,
    }

    if concurrent_products <= 1:
        # Sequential (original behavior)
        enriched_products = []
        for i, product in enumerate(products):
            enriched = enrich_product(product, scraper, stats)
            enriched_products.append(enriched)
            if stats["scraped"] > 0 and stats["scraped"] % 5 == 0:
                logger.info(f"  [{path.stem}] Processed {i+1}/{len(products)}, scraped {stats['scraped']}")
            if stats["scraped"] > 0:
                time.sleep(delay)
    else:
        # Parallel: process in chunks to preserve order and rate-limit
        concurrency = min(concurrent_products, len(products))
        enriched_products = [None] * len(products)  # type: ignore

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            for chunk_start in range(0, len(products), concurrency):
                chunk = products[chunk_start : chunk_start + concurrency]
                futures = [executor.submit(_enrich_one, p, scraper) for p in chunk]
                for j, future in enumerate(futures):
                    enriched, delta = future.result()
                    idx = chunk_start + j
                    enriched_products[idx] = enriched
                    for k, v in delta.items():
                        stats[k] = stats.get(k, 0) + v
                done = min(chunk_start + concurrency, len(products))
                if done % max(5, concurrency * 2) < concurrency or done == len(products):
                    logger.info(f"  [{path.stem}] Processed {done}/{len(products)}, scraped {stats['scraped']}")
                # One delay per chunk to keep rate limit
                time.sleep(delay * min(len(chunk), concurrency))

        enriched_products = [p for p in enriched_products if p is not None]

    if not dry_run and stats["scraped"] > 0:
        save_brand_file(path, enriched_products, fmt)
        logger.info(f"  Saved {path.name} ({stats['scraped']} enriched)")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Enrich catalog from Halilit pages")
    parser.add_argument(
        "--brand", help="Enrich specific brand file (stem name)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't save changes")
    parser.add_argument("--official", action="store_true",
                        help="Also try official brand page scraping (slower)")
    parser.add_argument("--merge-dupes", action="store_true",
                        help="Merge duplicate brand files first")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Delay between HTTP requests (seconds)")
    parser.add_argument("--workers", type=int, default=1,
                        help="Number of brand files to process in parallel (default 1)")
    parser.add_argument("--concurrent-products", type=int, default=1,
                        help="Within each brand file, scrape this many products at once (default 1; try 4–6 to speed up)")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Catalog Enrichment Script")
    logger.info("=" * 60)

    if not DATA_DIR.exists():
        logger.error(f"Data directory not found: {DATA_DIR}")
        sys.exit(1)

    # Step 1: Merge duplicates if requested
    if args.merge_dupes:
        logger.info("\n--- Merging duplicate brand files ---")
        merge_duplicate_brands(dry_run=args.dry_run)

    # Step 2: Enrich products
    scraper = HalilitPageScraper()

    if args.brand:
        # Single brand
        matches = list(DATA_DIR.glob(f"{args.brand}*.json"))
        if not matches:
            logger.error(f"No brand file matching '{args.brand}' found")
            sys.exit(1)
        files = matches
    else:
        files = sorted(DATA_DIR.glob("*.json"))
        files = [f for f in files if f.name not in EXCLUDED_FILES]

    workers = max(1, getattr(args, "workers", 1))
    concurrent_products = max(1, getattr(args, "concurrent_products", 1))
    logger.info(f"\nProcessing {len(files)} brand files (workers={workers}, concurrent_products={concurrent_products})...")
    if args.dry_run:
        logger.info("(DRY RUN — no files will be modified)")

    all_stats = []
    total_scraped = 0

    def process_file(item):
        i, path = item
        logger.info(f"\n[{i+1}/{len(files)}] {path.name}")
        # Each worker gets its own scraper to avoid shared state
        worker_scraper = HalilitPageScraper()
        return enrich_brand_file(
            path, worker_scraper,
            dry_run=args.dry_run,
            delay=args.delay,
            concurrent_products=concurrent_products,
        )

    if workers <= 1:
        for i, path in enumerate(files):
            stats = process_file((i, path))
            all_stats.append(stats)
            total_scraped += stats.get("scraped", 0)
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_path = {
                executor.submit(process_file, (i, path)): (i, path)
                for i, path in enumerate(files)
            }
            for future in as_completed(future_to_path):
                try:
                    stats = future.result()
                    all_stats.append(stats)
                    total_scraped += stats.get("scraped", 0)
                except Exception as e:
                    logger.error(f"Enrich task failed: {e}", exc_info=True)

    # Summary
    total_products = sum(s.get("total", 0) for s in all_stats)
    total_skipped_url = sum(s.get("skipped_no_url", 0) for s in all_stats)
    total_skipped_rich = sum(s.get("skipped_already_rich", 0)
                             for s in all_stats)
    total_failed = sum(s.get("scrape_failed", 0) for s in all_stats)
    total_errors = sum(s.get("scrape_error", 0) for s in all_stats)

    logger.info("\n" + "=" * 60)
    logger.info("ENRICHMENT SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total products:      {total_products}")
    logger.info(f"Successfully scraped: {total_scraped}")
    logger.info(f"Skipped (no URL):    {total_skipped_url}")
    logger.info(f"Skipped (already rich): {total_skipped_rich}")
    logger.info(f"Scrape failed:       {total_failed}")
    logger.info(f"Scrape errors:       {total_errors}")


if __name__ == "__main__":
    main()
