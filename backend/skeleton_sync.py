"""
Skeleton Sync — Lightweight inventory sync from Halilit.com.

This is NOT the heavy pipeline. It does ONE thing:
  Read the existing brand JSON files in frontend/public/data/
  and ensure they're the source of truth for the inventory catalog.

In the future, this can be replaced by a nightly scraper that
fetches fresh data from halilit.com. For now, it validates and
indexes the existing data files.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "frontend" / "public" / "data"


def run_skeleton_sync() -> dict:
    """
    Sync inventory from the brand JSON files.

    Returns:
        Summary dict with counts and status.
    """
    if not DATA_DIR.exists():
        logger.error(f"Data directory not found: {DATA_DIR}")
        return {"status": "error", "message": f"Data dir not found: {DATA_DIR}"}

    total_products = 0
    brands_found = 0
    errors = []

    for json_file in sorted(DATA_DIR.glob("*.json")):
        brand_name = json_file.stem
        # Skip metadata files
        if brand_name in ("index", "search_index", "search_index_min"):
            continue

        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            products = data if isinstance(
                data, list) else data.get("products", [])
            if products:
                brands_found += 1
                total_products += len(products)
                logger.debug(f"  {brand_name}: {len(products)} products")
        except Exception as e:
            errors.append(f"{brand_name}: {e}")
            logger.warning(f"Error reading {json_file}: {e}")

    logger.info(
        f"✅ Skeleton sync: {total_products} products from {brands_found} brands")

    return {
        "status": "ok",
        "total_products": total_products,
        "brands": brands_found,
        "errors": errors,
    }
