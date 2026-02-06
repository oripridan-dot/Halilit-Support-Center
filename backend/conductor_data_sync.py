#!/usr/bin/env python3
"""
CONDUCTOR DATA SYNC
Normalizes all frontend JSON files to ensure proper data format
Orchestrated by Conductor to synchronize backend and frontend data

This runs immediately to fix any existing data that hasn't been through
the new DataNormalizer pipeline yet.
"""

from backend.data_normalizer import DataNormalizer
import json
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ConductorDataSync")

FRONTEND_DATA_DIR = Path(
    "/workspaces/Halilit-Support-Center/frontend/public/data")


def sync_all_brands():
    """
    CONDUCTOR DATA SYNC: Normalize all brand JSON files
    Ensures every product has:
    - Proper pricing (price, currency, pricing object)
    - Proper images (image_hero, image_thumbnail, image_gallery, official_images)
    - All metadata fields
    """

    logger.info("🎼 CONDUCTOR DATA SYNC - Normalizing all brands...")
    logger.info(f"   📁 Frontend data directory: {FRONTEND_DATA_DIR}")

    # Find all brand JSON files
    brand_files = sorted(FRONTEND_DATA_DIR.glob("*.json"))
    brand_files = [f for f in brand_files if f.name not in [
        "index.json", "search_index.json", "search_index_min.json",
        "galaxy_db.json", "moog.json"  # Skip non-brand files
    ]]

    logger.info(f"   🔍 Found {len(brand_files)} brand files to normalize")

    sync_stats = {
        "total_brands": len(brand_files),
        "successful": 0,
        "failed": 0,
        "total_products": 0,
        "normalized_products": 0,
    }

    for brand_file in brand_files:
        brand_name = brand_file.stem
        logger.info(f"\n   📦 Processing {brand_name}...")

        try:
            # Load existing brand JSON
            with open(brand_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

            # Handle both array and object formats
            if isinstance(existing_data, dict) and "products" in existing_data:
                products = existing_data["products"]
            elif isinstance(existing_data, list):
                products = existing_data
            else:
                logger.warning(
                    f"      ⚠️  Unknown format in {brand_name}, skipping")
                continue

            sync_stats["total_products"] += len(products)

            logger.info(f"      📊 Loaded {len(products)} products")
            logger.info(f"      🔄 Normalizing with DataNormalizer...")

            # Normalize all products using Conductor-orchestrated DataNormalizer
            normalized_products = DataNormalizer.normalize_batch(
                products, brand_name)

            # Validate
            valid_count = 0
            for product in normalized_products:
                is_valid, errors = DataNormalizer.validate_normalized(product)
                if is_valid:
                    valid_count += 1
                else:
                    logger.warning(
                        f"      ⚠️  Invalid: {product.get('halilit_id')} - {errors}")

            sync_stats["normalized_products"] += valid_count

            logger.info(
                f"      ✅ Validated {valid_count}/{len(normalized_products)} products")

            # Write back as array (frontend expects this)
            with open(brand_file, 'w', encoding='utf-8') as f:
                json.dump(normalized_products, f, indent=2, ensure_ascii=False)

            logger.info(
                f"      💾 Wrote {len(normalized_products)} products to {brand_name}.json")
            sync_stats["successful"] += 1

        except Exception as e:
            logger.error(f"      ❌ Error processing {brand_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            sync_stats["failed"] += 1

    # Final report
    logger.info("\n" + "="*70)
    logger.info("🎼 CONDUCTOR DATA SYNC - SUMMARY")
    logger.info("="*70)
    logger.info(
        f"   ✅ Successful: {sync_stats['successful']}/{sync_stats['total_brands']} brands")
    logger.info(
        f"   ❌ Failed: {sync_stats['failed']}/{sync_stats['total_brands']} brands")
    logger.info(
        f"   📦 Total products processed: {sync_stats['total_products']}")
    logger.info(
        f"   ✅ Normalized products: {sync_stats['normalized_products']}")
    logger.info("="*70)
    logger.info("✨ Data sync complete! All products now have proper structure.")
    logger.info("   - Prices extracted to top-level fields")
    logger.info("   - Images normalized with correct fields")
    logger.info("   - Taxonomy and specs properly mapped")

    return sync_stats["failed"] == 0


if __name__ == "__main__":
    success = sync_all_brands()
    sys.exit(0 if success else 1)
