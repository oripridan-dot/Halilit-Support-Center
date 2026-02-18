#!/usr/bin/env python3
"""
Batch Catalog Enrichment Script (FAST ASYNC VERSION)
====================================================
Processes all existing brand JSON files and enriches products by:
1. Scraping individual Halilit product pages for JSON-LD data (ASYNC - MUCH FASTER)
2. Optionally attempting official brand page scraping
3. Deduplicating products across variant brand files
4. Saving enriched data back to disk

Usage:
    # Enrich all brands (ASYNC - 10-50x faster!)
    python -m backend.scripts.enrich_catalog

    # Enrich specific brand
    python -m backend.scripts.enrich_catalog --brand "adam-audio"

    # Dry run (don't save)
    python -m backend.scripts.enrich_catalog --dry-run

    # Skip visual validation (even faster)
    python -m backend.scripts.enrich_catalog --skip-visual

    # With custom concurrency (default: 50)
    python -m backend.scripts.enrich_catalog --concurrency 100
"""

import asyncio
from backend.ingestion.halilit_page_scraper_async import AsyncHalilitPageScraper
import argparse
import json
import logging
import sys
import time
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


async def _enrich_one_async(product: dict, scraper: AsyncHalilitPageScraper) -> Tuple[dict, Dict[str, int]]:
    """
    Enrich a single product asynchronously; returns (enriched_product, stats_delta).
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
        page_data = await scraper.scrape_product_page(url)
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

        delta = {"scraped": 1}
        if (page_data.get("image_gallery") or page_data.get("official_images")) and not (
            (page_data.get("image_url") or "").strip()
        ):
            delta["image_rejected"] = 1
        return enriched, delta

    except Exception as e:
        logger.warning(f"Error scraping {url}: {e}")
        return product, {"scrape_error": 1}


# Legacy sync version kept for compatibility
def enrich_product(product: dict, scraper, stats: dict) -> dict:
    """Enrich a single product (sync version - deprecated, use async)."""
    # This is kept for compatibility but shouldn't be used
    logger.warning("Using deprecated sync enrich_product - use async version instead")
    return product


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


async def enrich_brand_file_async(
    path: Path,
    scraper: AsyncHalilitPageScraper,
    dry_run: bool = False,
    concurrency: int = 50,
) -> dict:
    """
    Enrich all products in a brand JSON file using async concurrent scraping.
    
    This is MUCH faster than sync version - scrapes 50+ products simultaneously.
    """
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
        "image_rejected": 0,
    }

    # Filter products that need scraping
    to_scrape = []
    for i, product in enumerate(products):
        url = product.get("halilit_url") or product.get("source_url") or ""
        if not is_real_halilit_url(url):
            stats["skipped_no_url"] += 1
            continue
        
        has_desc = bool(product.get("official_description") or product.get("description"))
        has_price = bool(product.get("price") or product.get("price_il"))
        has_image = bool(product.get("image_url"))
        has_gallery = len(product.get("gallery_images") or product.get("image_gallery") or []) > 1
        
        if has_desc and has_price and has_image and has_gallery:
            stats["skipped_already_rich"] += 1
            continue
        
        to_scrape.append((i, product))

    if not to_scrape:
        logger.info(f"  [{path.stem}] All products already enriched")
        return stats

    logger.info(f"  [{path.stem}] Scraping {len(to_scrape)}/{len(products)} products concurrently...")

    # Scrape all products concurrently
    tasks = [_enrich_one_async(product, scraper) for _, product in to_scrape]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    enriched_products = list(products)
    for (idx, _), result in zip(to_scrape, results):
        if isinstance(result, Exception):
            logger.warning(f"  Error enriching product {idx}: {result}")
            stats["scrape_error"] += 1
        else:
            enriched, delta = result
            enriched_products[idx] = enriched
            for k, v in delta.items():
                stats[k] = stats.get(k, 0) + v

    # Progress logging
    if stats["scraped"] > 0:
        logger.info(
            f"  [{path.stem}] Scraped {stats['scraped']}/{len(to_scrape)} "
            f"(skipped: {stats['skipped_already_rich']} already rich, {stats['skipped_no_url']} no URL)"
        )

    if not dry_run and stats["scraped"] > 0:
        save_brand_file(path, enriched_products, fmt)
        logger.info(f"  ✅ Saved {path.name} ({stats['scraped']} enriched)")

    return stats


async def main_async():
    """Async main function."""
    parser = argparse.ArgumentParser(
        description="Enrich catalog from Halilit pages (ASYNC - FAST)")
    parser.add_argument(
        "--brand", help="Enrich specific brand file (stem name)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't save changes")
    parser.add_argument("--merge-dupes", action="store_true",
                        help="Merge duplicate brand files first")
    parser.add_argument("--concurrency", type=int, default=50,
                        help="Max concurrent requests (default: 50, higher = faster but more aggressive)")
    parser.add_argument("--skip-visual", action="store_true",
                        help="Skip visual validation (much faster)")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Catalog Enrichment Script (ASYNC - FAST)")
    logger.info("=" * 60)

    if not DATA_DIR.exists():
        logger.error(f"Data directory not found: {DATA_DIR}")
        sys.exit(1)

    # Set environment variable to skip visual validation if requested
    if args.skip_visual:
        import os
        os.environ["INGESTION_SKIP_VISUAL_VALIDATION"] = "1"
        logger.info("⚠️  Visual validation DISABLED (faster scraping)")

    # Set concurrency
    import os
    os.environ["INGESTION_ASYNC_CONCURRENCY"] = str(args.concurrency)
    logger.info(f"📊 Concurrency: {args.concurrency} concurrent requests")

    # Step 1: Merge duplicates if requested
    if args.merge_dupes:
        logger.info("\n--- Merging duplicate brand files ---")
        merge_duplicate_brands(dry_run=args.dry_run)

    # Step 2: Enrich products (ASYNC)
    if args.brand:
        matches = list(DATA_DIR.glob(f"{args.brand}*.json"))
        if not matches:
            logger.error(f"No brand file matching '{args.brand}' found")
            sys.exit(1)
        files = matches
    else:
        files = sorted(DATA_DIR.glob("*.json"))
        files = [f for f in files if f.name not in EXCLUDED_FILES]

    logger.info(f"\n🚀 Processing {len(files)} brand files with async scraper...")
    if args.dry_run:
        logger.info("(DRY RUN — no files will be modified)")

    all_stats = []
    total_scraped = 0

    # Use single async scraper for all files (connection pooling)
    async with AsyncHalilitPageScraper() as scraper:
        for i, path in enumerate(files, 1):
            logger.info(f"\n[{i}/{len(files)}] {path.name}")
            stats = await enrich_brand_file_async(
                path, scraper,
                dry_run=args.dry_run,
                concurrency=args.concurrency,
            )
            all_stats.append(stats)
            total_scraped += stats.get("scraped", 0)

    # Summary
    total_products = sum(s.get("total", 0) for s in all_stats)
    total_skipped_url = sum(s.get("skipped_no_url", 0) for s in all_stats)
    total_skipped_rich = sum(s.get("skipped_already_rich", 0) for s in all_stats)
    total_failed = sum(s.get("scrape_failed", 0) for s in all_stats)
    total_errors = sum(s.get("scrape_error", 0) for s in all_stats)
    total_image_rejected = sum(s.get("image_rejected", 0) for s in all_stats)

    logger.info("\n" + "=" * 60)
    logger.info("ENRICHMENT SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total products:      {total_products}")
    logger.info(f"Successfully scraped: {total_scraped}")
    logger.info(f"Skipped (no URL):    {total_skipped_url}")
    logger.info(f"Skipped (already rich): {total_skipped_rich}")
    logger.info(f"Scrape failed:       {total_failed}")
    if total_failed > 0:
        logger.info("  (Halilit often returns anti-bot/referrer page or timeout)")
    logger.info(f"Scrape errors:       {total_errors}")
    logger.info(f"Hero image rejected: {total_image_rejected}")
    logger.info("=" * 60)


def main():
    """Main entry point - runs async version."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
