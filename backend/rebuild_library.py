import glob
from backend.pipeline.data_refinery import DataRefinery
import sys
import os
import json
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.synchronize_frontend_data import sync as sync_frontend
except ImportError:
    # Try local import
    try:
        from synchronize_frontend_data import sync as sync_frontend
    except ImportError:
        sync_frontend = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GalaxyLibrarian")

def rebuild():
    logger.info("🔧 Starting Galaxy Library Rebuild...")

    # Paths
    root_dir = Path("/workspaces/Halilit-Support-Center")
    # NEW PATTERN: scan brands folder
    raw_data_pattern = str(root_dir / "backend/data/brands/**/*.json")
    output_path = root_dir / "frontend/public/data/galaxy_db.json"

    # Initialize Refinery
    refinery = DataRefinery()

    files = glob.glob(raw_data_pattern, recursive=True)
    if not files:
        logger.error(f"❌ No data files found in {raw_data_pattern}")
        return False

    logger.info(f"📂 Found {len(files)} source files")

    count = 0
    for file_path in files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Normalize input format (list vs dict wrapper)
            items_to_ingest = []
            if isinstance(data, list):
                items_to_ingest = data
            elif isinstance(data, dict):
                if 'products' in data and isinstance(data['products'], list):
                    items_to_ingest = data['products']
                    # Inject brand if missing in children but present in parent
                    parent_brand = data.get('brand_name') or data.get('brand')
                    if parent_brand:
                        for item in items_to_ingest:
                            if not item.get('brand'):
                                item['brand'] = parent_brand
                else:
                    items_to_ingest = [data]

            if items_to_ingest:
                refinery.ingest_raw_data(items_to_ingest)
                logger.info(
                    f"  Processed {file_path}: {len(items_to_ingest)} items")
                count += 1
            else:
                logger.warning(f"  Skipping {file_path}: No items found")

        except Exception as e:
            logger.error(f"  Failed to process {file_path}: {e}")

    # Export
    try:
        # Create directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        success = refinery.export_golden_json(str(output_path))
        if success:
            logger.info("✅ Rebuild Complete!")

            # AUTOMATIC SYNC TO LEGACY FRONTEND FILES
            if sync_frontend:
                logger.info("🔄 Synchronizing Frontend Legacy Data...")
                try:
                    sync_frontend()
                    logger.info("✅ Frontend Sync Complete!")
                except Exception as e:
                    logger.error(f"❌ Frontend Sync Failed: {e}")
            else:
                logger.warning("⚠️ Skipping Frontend Sync (module not found)")

            return True
        else:
            logger.error("❌ Export failed")
            return False

    except Exception as e:
        logger.error(f"❌ Rebuild Failed during export: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = rebuild()
    sys.exit(0 if success else 1)
