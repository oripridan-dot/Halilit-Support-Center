#!/usr/bin/env python3
"""
Organize all per-brand catalogs into a unified structure (consolidated schema).

Each brand file becomes: brand_identity, categories, products, search_index.
Uses OpenClaw when OPENCLAW_URL is set (skill: organize_brand_catalog), else Python fallback.

Run from project root:
  PYTHONPATH=. python backend/scripts/organize_brand_catalogs.py
  PYTHONPATH=. python backend/scripts/organize_brand_catalogs.py --dry-run
  PYTHONPATH=. python backend/scripts/organize_brand_catalogs.py --brand roland
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.catalog_organizer import (
    load_brand_products,
    write_consolidated_catalog,
)
# Use AI organizer if enabled, otherwise fallback to basic organizer
import os
if os.getenv("AI_ORGANIZER_ENABLED", "true").lower() == "true":
    from backend.ai_catalog_organizer import organize_brand_sync
else:
    from backend.catalog_organizer import organize_brand_sync
from backend.project_config import FRONTEND_PUBLIC_DATA

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

SKIP_FILES = {"index", "search_index_min", "galaxy_db", "inventory"}


def main() -> None:
    ap = argparse.ArgumentParser(description="Organize per-brand catalogs into unified structure")
    ap.add_argument("--dry-run", action="store_true", help="Do not write files")
    ap.add_argument("--brand", type=str, help="Only process this brand (file stem, e.g. roland)")
    args = ap.parse_args()
    data_dir = Path(FRONTEND_PUBLIC_DATA)
    if not data_dir.exists():
        logger.error("Data dir not found: %s", data_dir)
        sys.exit(1)
    # Brand files: *.json except index, search_index_min, galaxy_db, inventory
    candidates = [
        f
        for f in data_dir.glob("*.json")
        if f.stem not in SKIP_FILES and not f.name.startswith("_")
    ]
    if args.brand:
        candidates = [f for f in candidates if f.stem.lower() == args.brand.lower()]
        if not candidates:
            logger.error("No brand file found for: %s", args.brand)
            sys.exit(1)
    total = 0
    for path in sorted(candidates):
        try:
            brand_slug, brand_name, products = load_brand_products(path)
        except Exception as e:
            logger.warning("Skip %s: %s", path.name, e)
            continue
        if not products:
            logger.info("Skip %s: no products", path.name)
            continue
        logger.info("Organizing %s (%s products)...", path.stem, len(products))
        consolidated = organize_brand_sync(brand_slug, brand_name, products)
        if not args.dry_run:
            write_consolidated_catalog(brand_slug, consolidated, out_dir=data_dir)
        total += 1
    logger.info("Done. Consolidated %s brand(s).", total)


if __name__ == "__main__":
    main()
