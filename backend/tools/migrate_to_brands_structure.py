"""
Migrate To Brands Structure - Production-ready v5.2.4
"""


import os
import logging
import json
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)
# Config
SOURCE_DIR = Path("frontend/public/data")
TARGET_ROOT = Path("backend/data/brands")
EXCLUDED_BRANDS = ["focal", "neumann"]
EXCLUDED_FILES = ["galaxy_db.json", "index.json",
                  "search_index.json", "taxonomy.json"]

def normalize_brand_name(name):
    return name.lower().replace(" ", "-").replace(".", "")

def migrate():
    print(f"🚀 Starting Migration from {SOURCE_DIR} to {TARGET_ROOT}")

    if not SOURCE_DIR.exists():
        logger.info("❌ Source directory not found!")
        return

    # Clean target if exists to ensure SSOT purity
    if TARGET_ROOT.exists():
        print(f"🧹 Clearing existing target directory: {TARGET_ROOT}")
        shutil.rmtree(TARGET_ROOT)

    TARGET_ROOT.mkdir(parents=True, exist_ok=True)

    files = list(SOURCE_DIR.glob("*.json"))
    print(f"found {len(files)} files to process.")

    for file_path in files:
        if file_path.name in EXCLUDED_FILES:
            continue

        brand_key = file_path.stem.lower()

        # 1. Check Exclusion
        if brand_key in EXCLUDED_BRANDS:
            print(f"🚫 SKIPPING EXCLUDED BRAND: {brand_key}")
            continue

        print(f"📦 Processing {brand_key}...")

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Determine Brand Name for Folder
            brand_name = brand_key.title()  # Default
            products = []

            # Handle different formats
            if isinstance(data, list):
                products = data
                if products:
                    brand_name = products[0].get('brand', brand_name)
            elif isinstance(data, dict):
                brand_name = data.get(
                    'brand', data.get('brand_name', brand_key))
                products = data.get('products', [])

            # Create Brand Folder
            safe_folder_name = brand_name.strip().replace(" ", "-")
            brand_dir = TARGET_ROOT / safe_folder_name
            brand_dir.mkdir(parents=True, exist_ok=True)

            # Save as SSOT for this brand
            target_file = brand_dir / "products.json"

            ssot_data = {
                "brand": brand_name,
                "metadata": {
                    "source": "migration_v5.2",
                    "original_file": file_path.name
                },
                "products": products
            }

            with open(target_file, 'w') as f:
                json.dump(ssot_data, f, indent=2)

            print(f"   ✅ Created {target_file} ({len(products)} products)")

        except Exception as e:
            print(f"   ❌ Error validating {file_path}: {e}")

    logger.info("🎉 Migration Complete. The 'brands' folder is now the SSOT.")

if __name__ == "__main__":
    migrate()
