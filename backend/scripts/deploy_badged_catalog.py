import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeployBadged")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DATA_DIR = ROOT_DIR / "frontend" / "public" / "data"
INDEX_PATH = FRONTEND_DATA_DIR / "index.json"

BADGED_BRANDS = [
    "adam-audio",
    "warm-audio",
    "amphion",
    "drumdots",
    "fzone",
    "bespeco"
]


def main():
    if not INDEX_PATH.exists():
        logger.error(f"Index not found at {INDEX_PATH}")
        return

    # Load original index
    with open(INDEX_PATH, "r") as f:
        master_index = json.load(f)

    original_count = len(master_index.get("brands", []))
    logger.info(f"Loaded master index with {original_count} brands.")

    # Filter brands
    filtered_brands = []
    total_products = 0

    for brand_entry in master_index.get("brands", []):
        if brand_entry["id"] in BADGED_BRANDS:

            # Update the entry with latest stats from the processed file if possible
            processed_path = FRONTEND_DATA_DIR / f"{brand_entry['id']}.json"
            if processed_path.exists():
                with open(processed_path, "r") as pf:
                    pdata = json.load(pf)
                    # Update product count since we may have refined it
                    p_count = len(pdata.get("products", []))
                    brand_entry["product_count"] = p_count
                    brand_entry["verified_count"] = p_count
                    brand_entry["count"] = p_count

            filtered_brands.append(brand_entry)
            total_products += brand_entry.get("product_count", 0)

    # Construct new index
    new_index = {
        **master_index,
        "total_products": total_products,
        "total_verified": total_products,
        "brands": filtered_brands
    }

    # Backup original (just in case)
    backup_path = FRONTEND_DATA_DIR / "index.json.bak"
    if not backup_path.exists():
        with open(backup_path, "w") as f:
            json.dump(master_index, f, indent=2)
        logger.info(f"Backed up original index to {backup_path}")

    # Write new index
    with open(INDEX_PATH, "w") as f:
        json.dump(new_index, f, indent=2)

    logger.info(f"Deployed filtered index with {len(filtered_brands)} brands.")


if __name__ == "__main__":
    main()
