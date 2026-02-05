#!/usr/bin/env python3
"""
v6.0 Ingestion-to-Frontend Synchronizer

Converts backend ingestion output to frontend-consumable JSON format.
Called by conductor after ingestion pipeline completes.

Flow:
1. Read approved products from backend/data/ingestion/products/{brand}/approved_*.json
2. Extract product data into frontend format
3. Write to frontend/public/data/{brand}.json
4. Update index files
"""

from backend.ingestion.data_models import IngestionProductDraft
import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IngestToFrontend")

INGESTION_DIR = Path(
    "/workspaces/Halilit-Support-Center/backend/data/ingestion")
FRONTEND_DATA_DIR = Path(
    "/workspaces/Halilit-Support-Center/frontend/public/data")


def sync_brand_to_frontend(brand: str) -> bool:
    """
    Sync approved products from ingestion to frontend format.

    Args:
        brand: Brand name (e.g., "Nord")

    Returns:
        True if successful, False otherwise
    """
    try:
        brand_dir = INGESTION_DIR / "products" / brand

        # Find the latest approved_*.json file
        if not brand_dir.exists():
            logger.warning(f"No product directory for {brand}")
            return False

        approved_files = sorted(brand_dir.glob(
            "approved_*.json"), reverse=True)
        if not approved_files:
            logger.warning(f"No approved products file for {brand}")
            return False

        approved_dir = approved_files[0]  # Latest file

        # Load approved products
        with open(approved_dir) as f:
            approved_data = json.load(f)

        if isinstance(approved_data, dict) and "products" in approved_data:
            products = approved_data["products"]
        else:
            products = approved_data if isinstance(approved_data, list) else []

        # Convert to frontend format (simplified)
        frontend_products = []
        for p in products:
            # Extract nested data
            pricing = p.get("pricing", {})
            display = p.get("display", {})
            content = p.get("content", {})
            taxonomy = p.get("taxonomy", {})

            # HALILIT TIER 1: Extract category from ingestion taxonomy (canonical_category)
            halilit_category = taxonomy.get(
                "canonical_category") if isinstance(taxonomy, dict) else None
            halilit_subcategory = taxonomy.get(
                "canonical_subcategory") if isinstance(taxonomy, dict) else None

            fp = {
                "id": p.get("halilit_id") or p.get("id"),
                "sku": p.get("sku") or p.get("model_number"),
                "name": p.get("product_name") or p.get("name"),
                "brand": p.get("brand"),
                "brand_id": p.get("brand", "unknown").lower(),
                # HALILIT TIER 1: Use canonical category from ingestion as primary source of truth
                "category": halilit_category,
                "subCategory": halilit_subcategory,
                "description": content.get("description_long") or content.get("description"),
                "description_short": content.get("description_short"),
                "description_full": content.get("description_long"),
                "price": pricing.get("price_il"),
                "price_eilat": pricing.get("price_eilat"),
                "currency": p.get("currency", "ILS"),
                "tier": pricing.get("tier"),
                "tier_level": display.get("display_tier_level"),
                "images": p.get("images") or {},
                "specifications": p.get("specifications") or {},
                # Pass official specs to frontend
                "official_specs": p.get("official_specs") or {},
                "completeness": p.get("data_completeness"),
                "quality_score": p.get("quality_score"),
            }
            frontend_products.append(fp)

        # Write to frontend
        output_file = FRONTEND_DATA_DIR / f"{brand.lower()}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(frontend_products, f, indent=2, ensure_ascii=False)

        logger.info(f"  ✓ Synced to {output_file.name}")
        return True

    except Exception as e:
        logger.error(f"  ✗ Failed to sync {brand}: {e}")
        return False


def sync_all_brands() -> Dict[str, bool]:
    """Sync all brands."""
    logger.info("📊 Syncing ingestion output to frontend...")

    # Find all brands with approved products
    products_dir = INGESTION_DIR / "products"
    if not products_dir.exists():
        logger.warning("No ingestion products directory")
        return {}

    results = {}
    for brand_dir in products_dir.iterdir():
        if brand_dir.is_dir():
            brand = brand_dir.name
            results[brand] = sync_brand_to_frontend(brand)

    success_count = sum(1 for v in results.values() if v)
    logger.info(f"✅ Synced {success_count}/{len(results)} brands")

    return results


if __name__ == "__main__":
    sync_all_brands()
    logger.info("Done!")
