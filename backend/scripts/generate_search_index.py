
import json
import logging
from pathlib import Path
import sys

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
FRONTEND_DATA = Path("../frontend/public/data")
SEARCH_INDEX_FILE = FRONTEND_DATA / "search_index.json"


def generate_search_index():
    logger.info("Starting Search Index Generation...")

    if not FRONTEND_DATA.exists():
        logger.error(
            f"Frontend data directory not found at {FRONTEND_DATA.resolve()}")
        sys.exit(1)

    all_items = []

    excluded_files = {
        'index.json',
        'search_index.json',
        'search_index_min.json',
        'galaxy_db.json',
        'package.json'
    }

    json_files = list(FRONTEND_DATA.glob("*.json"))

    for json_file in json_files:
        if json_file.name in excluded_files:
            continue

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = json.load(f)

            products = []
            if isinstance(content, list):
                products = content
            elif isinstance(content, dict) and "products" in content:
                products = content["products"]

            for p in products:
                # --- APPLY QUALITY GATES (MIRROR SERVER.PY) ---

                # 1. Price Check
                price = p.get('price')
                if not price or price == 0:
                    price = p.get('price_il', 0)
                if not price or price == 0:
                    price = p.get('pricing', {}).get('price_il', 0)

                if float(price) <= 0:
                    continue  # Skip junk

                # 2. Image Check
                image_url = p.get('image_url')
                if not image_url:
                    # Try official
                    imgs = p.get('official_images', [])
                    if imgs and isinstance(imgs, list) and len(imgs) > 0:
                        image_url = imgs[0].get('url')
                if not image_url:
                    # Try display
                    image_url = p.get('display', {}).get(
                        'hero_image', {}).get('url')

                if not image_url:
                    continue  # Skip no image

                # --- TRANSFORM TO SEARCH ITEM ---
                name = p.get('name') or p.get('product_name') or "Unknown"
                brand = p.get('brand', json_file.stem)

                # Get category
                category = p.get('category')
                if not category:
                    category = p.get('taxonomy', {}).get(
                        'canonical_category', 'Other')

                search_item = {
                    "id": p.get('id') or p.get('halilit_id'),
                    "label": name,
                    "brand": brand.lower().replace(" ", "-"),
                    "brand_name": brand,  # Keep original casing if possible, or title()
                    "category": category,
                    "subcategory": p.get('taxonomy', {}).get('canonical_subcategory'),
                    "keywords": p.get('taxonomy', {}).get('keywords', []),
                    "description": p.get('description_short') or p.get('official_description') or "",
                    "image_url": image_url
                }

                all_items.append(search_item)

        except Exception as e:
            logger.warning(f"Error processing {json_file.name}: {e}")

    logger.info(f"Generated index with {len(all_items)} valid items.")

    with open(SEARCH_INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False)

    logger.info(f"Successfully wrote search index to {SEARCH_INDEX_FILE}")


if __name__ == "__main__":
    generate_search_index()
