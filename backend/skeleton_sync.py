#!/usr/bin/env python3
"""
SKELETON SYNC — Lightweight Halilit Inventory Fetcher

Fetches basic product inventory from Halilit.com listing pages.
No AI agents, no per-product detail scraping. Just listing pages.

Output:
  frontend/public/data/inventory.json      — Full inventory
  frontend/public/data/search_index_min.json — Search index for frontend worker

Target: ~500+ products in under 30 seconds.

Usage:
    PYTHONPATH=. python3 backend/skeleton_sync.py
    PYTHONPATH=. python3 backend/skeleton_sync.py --brand Roland
"""

import json
import logging

# Import version from backend when available (script may run standalone)
try:
    from backend import __version__
except ImportError:
    __version__ = "9.3.0"
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("SkeletonSync")


def _slugify(name: str) -> str:
    """Create a URL-safe slug from a product name."""
    s = name.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s-]+', '-', s)
    return s[:80] or hashlib.md5(name.encode()).hexdigest()[:12]


def _guess_category(name: str, brand: str) -> str:
    """Guess a broad category from the product name (for galaxy view)."""
    n = name.lower()
    b = brand.lower()

    # Drums & Percussion
    if any(w in n for w in ['drum', 'cymbal', 'snare', 'tom', 'kick', 'hi-hat',
                            'percussion', 'cajon', 'bongo', 'pad', 'תופים']):
        return 'drums & percussion'
    if any(w in b for w in ['pearl', 'dixon', 'paiste', 'remo', 'turkish']):
        return 'drums & percussion'

    # Guitars & Bass
    if any(w in n for w in ['guitar', 'bass', 'ukulele', 'גיטרה', 'בס']):
        return 'guitars & bass'
    if any(w in n for w in ['amp', 'pedal', 'pedalboard']):
        return 'guitars & bass'
    if any(w in b for w in ['fender', 'gibson', 'ibanez', 'esp', 'solar']):
        return 'guitars & bass'

    # Keys & Synths
    if any(w in n for w in ['piano', 'keyboard', 'synth', 'organ', 'פסנתר',
                            'סינתיסייזר', 'קלידים']):
        return 'keys & synths'
    if any(w in b for w in ['nord', 'moog', 'arturia', 'sequential']):
        return 'keys & synths'
    if 'roland' in b and any(w in n for w in ['fp-', 'rd-', 'juno', 'jupiter']):
        return 'keys & synths'

    # Studio & Recording
    if any(w in n for w in ['monitor', 'interface', 'preamp', 'compressor',
                            'headphone', 'אוזניות', 'מוניטור', 'מיקרופון',
                            'microphone', 'mic ']):
        return 'studio & recording'
    if any(w in b for w in ['adam audio', 'krk', 'focal', 'neumann', 'rode',
                            'shure', 'universal audio', 'warm audio']):
        return 'studio & recording'

    # Live & DJ
    if any(w in n for w in ['pa ', 'speaker', 'mixer', 'dj', 'wireless',
                            'lighting', 'רמקול', 'מיקסר']):
        return 'live & dj'
    if any(w in b for w in ['mackie', 'rcf', 'allen & heath']):
        return 'live & dj'

    # Accessories & Utility
    if any(w in n for w in ['cable', 'stand', 'case', 'bag', 'strap',
                            'string', 'pick', 'כבל', 'מעמד', 'נרתיק']):
        return 'accessories & utility'

    return 'general'


def run_skeleton_sync(brand_filter: Optional[str] = None) -> bool:
    """
    Main entry point for skeleton sync.

    1. Discover all brands from Halilit.com
    2. For each brand, scrape the listing pages (name, price, URL, thumbnail)
    3. Write inventory.json and search_index_min.json
    """
    from backend.ingestion.halilit_page_scraper import HalilitPageScraper
    from backend.project_config import FRONTEND_PUBLIC_DATA

    scraper = HalilitPageScraper()
    output_dir = Path(FRONTEND_PUBLIC_DATA)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Discover brands
    if brand_filter:
        logger.info(f"Skeleton sync for brand: {brand_filter}")
        # Find the brand group URL
        all_brands = scraper.discover_all_brands()
        matching = [b for b in all_brands if b["name"].lower() == brand_filter.lower()]
        if not matching:
            # Try partial match
            matching = [b for b in all_brands if brand_filter.lower() in b["name"].lower()]
        if not matching:
            logger.error(f"Brand '{brand_filter}' not found on Halilit.com")
            return False
        brands_to_sync = matching
    else:
        logger.info("Skeleton sync: discovering all brands from Halilit.com...")
        brands_to_sync = scraper.discover_all_brands()

    logger.info(f"Found {len(brands_to_sync)} brands to sync")

    # Step 2: Scrape listing pages for each brand
    all_products: List[Dict] = []
    brand_names: List[str] = []
    brand_counts: Dict[str, int] = {}

    for brand_info in brands_to_sync:
        brand_name = brand_info["name"]
        group_url = brand_info.get("group_url", "")

        try:
            listings = scraper.scrape_brand_listing(brand_name, brand_group_url=group_url)
            if not listings:
                continue

            brand_names.append(brand_name)
            brand_counts[brand_name] = len(listings)

            for item in listings:
                product_id = _slugify(f"{brand_name}-{item.get('name', '')}")
                price = item.get("price", 0)

                all_products.append({
                    "id": product_id,
                    "name": item.get("name", ""),
                    "brand": brand_name,
                    "price": price,
                    "price_eilat": round(price / 1.17, 2) if price > 0 else 0,
                    "halilit_url": item.get("url", ""),
                    "thumbnail": item.get("image_url", ""),
                    "category_hint": _guess_category(item.get("name", ""), brand_name),
                    "in_stock": True,
                })

            logger.info(f"  {brand_name}: {len(listings)} products")

        except Exception as e:
            logger.warning(f"  {brand_name}: Failed — {e}")

    # Step 3: Write inventory.json
    inventory = {
        "last_sync": datetime.now(timezone.utc).isoformat(),
        "total_products": len(all_products),
        "total_brands": len(brand_names),
        "brands": sorted(brand_names),
        "brand_counts": brand_counts,
        "products": all_products,
    }

    inventory_path = output_dir / "inventory.json"
    inventory_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2))
    logger.info(f"Wrote {len(all_products)} products to {inventory_path}")

    # Step 4: Write search_index_min.json
    search_items = []
    for p in all_products:
        search_items.append({
            "id": p["id"],
            "label": p["name"],
            "brand": p["brand"].lower(),
            "brand_name": p["brand"],
            "category": p["category_hint"],
            "keywords": p["name"].lower().split()[:6],
            "description": "",
            "image_url": p["thumbnail"],
        })

    search_path = output_dir / "search_index_min.json"
    search_path.write_text(json.dumps(search_items, ensure_ascii=False))
    logger.info(f"Wrote search index ({len(search_items)} items) to {search_path}")

    # Step 5: Write/update index.json for the catalog builder
    index_brands = []
    for bn in sorted(brand_names):
        count = brand_counts.get(bn, 0)
        index_brands.append({
            "id": bn.lower().replace(" ", "-"),
            "name": bn,
            "product_count": count,
            "verified_count": count,
            "data_file": f"inventory.json",
        })

    index_data = {
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
        "version": __version__,
        "total_products": len(all_products),
        "total_verified": len(all_products),
        "brands": index_brands,
    }
    index_path = output_dir / "index.json"
    index_path.write_text(json.dumps(index_data, ensure_ascii=False, indent=2))

    logger.info(f"\nSkeleton sync complete: {len(all_products)} products across {len(brand_names)} brands")
    return True


if __name__ == "__main__":
    import argparse
    import sys

    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s')

    parser = argparse.ArgumentParser(description="Skeleton Sync — Lightweight Halilit Inventory")
    parser.add_argument("--brand", help="Sync a specific brand only")
    args = parser.parse_args()

    success = run_skeleton_sync(args.brand)
    sys.exit(0 if success else 1)
