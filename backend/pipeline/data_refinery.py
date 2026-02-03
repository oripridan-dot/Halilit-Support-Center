import json
import time
import glob
import os
import uuid
from typing import List, Dict, Any
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DataRefinery")

class DataRefinery:
    def __init__(self):
        self.products = []
        self.validation_errors = []  # Critical errors that prevent ingestion
        self.validation_warnings = []  # Soft warnings (e.g. zero price)
        self.seen_ids = set()

        # Brand normalization map
        self.brand_map = {
            "Nord Keyboards": "Nord",
            "Moog Music": "Moog",
            "Universal Audio": "Universal-Audio",
            "Roland Inc.": "Roland",
            "Yamaha Ltd.": "Yamaha",
            "KORG Synths": "Korg",
            "Korg Synths": "Korg",
            "Native Instruments": "Native"
        }

    def ingest_raw_data(self, raw_items: List[Dict]) -> int:
        """
        Takes raw dumps (from scrapers/agents) and attempts to refine them.
        Returns the number of successfully ingested items.
        """
        logger.info(f"Refining {len(raw_items)} raw items...")
        count = 0

        for item in raw_items:
            try:
                refined = self._refine_item(item)

                if not refined:
                    logger.warning(
                        f"Refinement returned None for item: {item.get('name', 'Unknown')}")
                    continue

                # Deduplication / ID Logic
                original_id = refined['id']
                dup_count = 1
                while refined['id'] in self.seen_ids:
                    refined['id'] = f"{original_id}-dup-{dup_count}"
                    dup_count += 1

                self.seen_ids.add(refined['id'])

                if self._validate_item(refined):
                    self.products.append(refined)
                    count += 1
                else:
                    reason = self.validation_errors[-1] if self.validation_errors else "Unknown"
                    logger.warning(
                        f"Validation failed for {refined['id']}: {reason}")
            except Exception as e:
                logger.warning(
                    f"Skipping item {item.get('name', 'Unknown')}: {e}")
        return count

    def _normalize_brand(self, brand_raw: Any) -> str:
        """Standardizes brand names"""
        if not brand_raw:
            return ""
        b = str(brand_raw).strip()
        return self.brand_map.get(b, b.title())

    def _parse_price(self, price_raw: Any) -> float:
        """Robust price parsing"""
        try:
            if isinstance(price_raw, (int, float)):
                return float(price_raw)
            if isinstance(price_raw, str):
                cleaned = price_raw.strip().replace('$', '').replace(
                    '€', '').replace('£', '').replace(',', '')
                return float(cleaned) if cleaned else 0.0
            return 0.0
        except ValueError:
            return 0.0

    def _determine_tier(self, price: float) -> str:
        """Calculates tier from price"""
        if price < 500:
            return 'entry'
        elif price < 1500:
            return 'mid'
        elif price < 4000:
            return 'pro'
        return 'flagship'

    def _generate_search_tokens(self, item: Dict, brand: str, tags: List[str]) -> str:
        """Creates searchable string"""
        parts = [
            str(item.get('name', '')),
            brand,
            str(item.get('category', '')),
            str(item.get('subCategory', '')),
            " ".join(tags)
        ]
        return " ".join(parts).lower()

    def _refine_item(self, item: Dict) -> Dict:
        """
        TRANSFORMATION LAYER: Cleans and standardizes data.
        """
        # Flatten 'commercial' wrapper if present (Roland/Generic scraping format)
        commercial = item.get('commercial', {})
        if commercial and isinstance(commercial, dict):
            # Map commercial fields to top level if missing
            if not item.get('name') and commercial.get('title'):
                item['name'] = commercial.get('title')
            if not item.get('price') and commercial.get('price_il'):
                item['price'] = commercial.get('price_il')
            if not item.get('brand') and commercial.get('brand'):
                item['brand'] = commercial.get('brand')
            if not item.get('image_url') and commercial.get('image_url'):
                item['image_url'] = commercial.get('image_url')
            if not item.get('stock_status'):
                item['stock_status'] = 'in_stock' if commercial.get(
                    'in_stock') else 'out_of_stock'

        # Critical Filter: Drop garbage items
        name = str(item.get('name', '')).strip()
        if not name or name.lower() in ['untitled product', 'product', 'item a', 'item b', 'item c']:
            return None
            # Overlay commercial data onto item if not present
            if 'name' not in item and 'title' in commercial:
                item['name'] = commercial['title']
            if 'price' not in item:
                item['price'] = commercial.get('price_il', 0)
            if 'image_url' not in item:
                item['image_url'] = commercial.get('image_url')
            if 'brand' not in item and 'brand' in commercial:
                item['brand'] = commercial['brand']
            if 'category' not in item and 'category' in commercial:
                item['category'] = commercial.get('category')
            if 'specs' not in item and 'specs' in commercial:
                item['specs'] = commercial.get('specs', {})

        # 1. Normalize Brand
        brand = self._normalize_brand(item.get('brand'))

        # 2. Calculate Tier
        price = self._parse_price(item.get('price', 0))
        tier = self._determine_tier(price)

        # 3. Generate Search Tokens
        tags_raw = item.get('tags', [])
        tags_list = []
        if isinstance(tags_raw, str):
            tags_list = tags_raw.split(' ') if ' ' in tags_raw else [tags_raw]
        elif isinstance(tags_raw, list):
            tags_list = [str(t) for t in tags_raw]

        search_text = self._generate_search_tokens(item, brand, tags_list)

        # Normalize category/subcategory
        # Try multiple field names for flexibility
        category = item.get('category') or item.get('cat') or 'Uncategorized'

        # For subcategory: try subCategory, subcategories (take first), or default to General
        sub_category = item.get('subCategory')
        if not sub_category:
            subcats = item.get('subcategories')
            if isinstance(subcats, list) and len(subcats) > 0:
                sub_category = subcats[0]
            else:
                sub_category = 'General'

        # FLATTEN SPECS LOGIC
        raw_specs = item.get('specs', {})
        final_specs = {}

        if isinstance(raw_specs, dict):
            # Check for "Specifications" list wrapper
            if 'Specifications' in raw_specs and isinstance(raw_specs['Specifications'], list):
                for s in raw_specs['Specifications']:
                    k = s.get('key') or s.get('name')
                    v = s.get('value')
                    if k:
                        final_specs[str(k)] = v
            else:
                # Assume strictly flat kv pairs or clean dictionary
                final_specs = raw_specs
        elif isinstance(raw_specs, list):
            # Handle list of {key, value} objects
            for s in raw_specs:
                if isinstance(s, dict):
                    k = s.get('key') or s.get('name')
                    v = s.get('value')
                    if k:
                        final_specs[str(k)] = v

        # Resolve description from multiple possible fields
        description = item.get('description', '')
        if not description:
            description = item.get('description_full', '')
        if not description:
            description = item.get('description_short', '')

        return {
            "id": str(item.get('uuid') or item.get('id', f"generated-{uuid.uuid4()}")),
            "name": item.get('name', 'Untitled Product').strip(),
            "description": description,
            "brand": brand,
            "category": category,
            "subCategory": sub_category,
            "tier": tier,
            "images": {
                "main": item.get('image_url') or "/assets/placeholders/no-image.png",
                "thumbnail": item.get('thumbnail_url') or item.get('image_url') or "/assets/placeholders/no-image.png",
                "gallery": item.get('gallery', [])
            },
            "price": price,
            "stockStatus": item.get('stock_status', 'in_stock'),
            "aiTags": tags_list + [tier],  # Enrich tags
            "specs": final_specs,
            "searchTokens": search_text
        }

    def _validate_item(self, item: Dict) -> bool:
        """
        QUALITY GATE: Rejects items that don't meet the standard.
        """
        is_valid = True

        if not item['name'] or len(str(item['name'])) < 2:
            self.validation_errors.append(f"Missing/Short Name: {item['id']}")
            is_valid = False

        if not item['brand']:
            self.validation_errors.append(f"Missing Brand: {item['id']}")
            is_valid = False

        if item['price'] == 0 and item['stockStatus'] == 'in_stock':
            # Soft warning
            self.validation_warnings.append(f"Zero price: {item['name']}")
            logger.warning(f"Zero price detected for {item['name']}")

        return is_valid

    def export_golden_json(self, output_path: str):
        """
        Outputs the 'Super Solid' single source of truth.
        """
        if not self.products:
            logger.warning("Attempted to export empty golden JSON. Aborting.")
            return False

        payload = {
            "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "version": "5.2.3",
            "stats": {
                "totalProducts": len(self.products),
                "brandsCount": len(set(p['brand'] for p in self.products))
            },
            "products": self.products,
            "categories": self._extract_category_tree()
        }

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)

        logger.info(
            f"✅ SUCCESS: Exported {len(self.products)} products to {output_path}")
        return True

    def _extract_category_tree(self):
        tree = {}
        for p in self.products:
            if p['category'] not in tree:
                tree[p['category']] = []
            if p['subCategory'] not in tree[p['category']]:
                tree[p['category']].append(p['subCategory'])
        # Sort subcategories for consistency
        for cat in tree:
            tree[cat] = sorted(list(set(tree[cat])))
        return tree

# --- Usage Example ---
if __name__ == "__main__":
    # In a real run, this would load from your database or multiple JSON dumps
    refinery = DataRefinery()

    # Sources to check:
    # 1. backend/data/brands/*/products.json (The NEW Single Source of Truth)
    # 2. backend/data/5_golden/*.json (Legacy fallback)

    base_dir = os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))  # backend/
    workspace_root = os.path.dirname(base_dir)

    sources = [
        os.path.join(base_dir, 'data', 'brands', '*', 'products.json'),
        os.path.join(base_dir, 'data', '5_golden', '*.json'),
        os.path.join(workspace_root, 'frontend', 'public',
                     'data', 'ingestion', '*.json')
    ]

    files_found = 0
    for source_pattern in sources:
        for file_path in glob.glob(source_pattern):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    logger.info(f"Ingesting {file_path}...")
                    raw_data = json.load(f)

                    # Handle "Brand/Products" wrapper format
                    items_to_process = []
                    parent_brand = None
                    if isinstance(raw_data, dict):
                        parent_brand = raw_data.get(
                            'brand_name') or raw_data.get('brand')
                        if 'products' in raw_data and isinstance(raw_data['products'], list):
                            items_to_process = raw_data['products']
                        else:
                            items_to_process = [raw_data]
                    elif isinstance(raw_data, list):
                        items_to_process = raw_data

                    # Inject parent brand if missing in items
                    if parent_brand:
                        for item in items_to_process:
                            if isinstance(item, dict) and not item.get('brand'):
                                item['brand'] = parent_brand

                    refinery.ingest_raw_data(items_to_process)
                    files_found += 1
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")

    if files_found == 0:
        logger.warning("No source files found. Checked: " + ", ".join(sources))

    output_path = os.path.join(
        workspace_root, 'frontend', 'public', 'data', 'galaxy_db.json')
    refinery.export_golden_json(output_path)
