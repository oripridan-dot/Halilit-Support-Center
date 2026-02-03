"""
Data Refinery: Transforms raw product data into Galaxy Standard format.

The strategy: "Refine, Validate, Enforce"
1. Refine: Normalize brands, clean text, generate missing SEO tags.
2. Validate: Fail the build if a product is missing critical fields.
3. Enforce: Output a schema that matches the Frontend's TypeScript interfaces 1:1.
"""

import json
import time
import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DataRefinery")


class DataRefinery:
    """Processes raw product data through refinement and validation gates."""

    def __init__(self):
        self.products: List[Dict[str, Any]] = []
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []

    def ingest_raw_data(self, raw_items: List[Dict]) -> int:
        """
        Takes raw dumps (from scrapers/agents) and attempts to refine them.

        Args:
            raw_items: List of raw product dictionaries

        Returns:
            Number of successfully refined items
        """
        logger.info(f"🔄 Refining {len(raw_items)} raw items...")

        accepted_count = 0
        for idx, item in enumerate(raw_items):
            try:
                refined = self._refine_item(item)
                if self._validate_item(refined):
                    self.products.append(refined)
                    accepted_count += 1
                else:
                    logger.debug(
                        f"Item #{idx} failed validation: {item.get('name', 'Unknown')}")
            except Exception as e:
                logger.warning(
                    f"Skipping item #{idx} ({item.get('name', 'Unknown')}): {e}")

        logger.info(f"✅ Accepted {accepted_count}/{len(raw_items)} items")
        return accepted_count

    def _refine_item(self, item: Dict) -> Dict[str, Any]:
        """
        TRANSFORMATION LAYER: Cleans and standardizes data.

        Handles:
        - Brand normalization (e.g., "Nord Keyboards" → "Nord")
        - Tier calculation based on price
        - Search token generation for frontend search
        - Image URL fallbacks
        """
        # 1. Normalize Brand
        brand_raw = item.get('brand', 'Generic').strip()
        brand = self._normalize_brand(brand_raw)

        # 2. Extract Price
        price = self._parse_price(item.get('price', 0))

        # 3. Calculate Tier (Logic rule: price-based)
        tier = self._determine_tier(price)

        # 4. Extract or Generate Images
        main_image = item.get('image_url') or item.get(
            'image') or "/assets/placeholders/no-image.png"
        gallery = item.get('gallery', []) or [main_image]

        # 5. Generate Search Tokens (For fast frontend search)
        search_text = self._generate_search_tokens(item, brand, tier)

        # 6. Extract Specs (with fallback)
        specs = item.get('specs', {}) or item.get('specifications', {}) or {}
        if isinstance(specs, str):
            specs = {}  # Fallback if specs is malformed

        # 7. Extract or generate AI tags
        ai_tags = item.get('tags', []) or item.get('ai_tags', [])
        if isinstance(ai_tags, str):
            ai_tags = [ai_tags]
        ai_tags = list(set(ai_tags + [tier]))  # Deduplicate

        return {
            "id": str(item.get('uuid') or item.get('id') or item.get('name', 'unknown')),
            "name": item.get('name', 'Untitled Product').strip(),
            "brand": brand,
            "category": item.get('category', 'Uncategorized').strip(),
            "subCategory": item.get('subCategory', 'General').strip(),
            "tier": tier,
            "images": {
                "main": main_image,
                "thumbnail": item.get('thumbnail_url') or main_image,
                "gallery": gallery
            },
            "price": price,
            "stockStatus": item.get('stock_status', 'in_stock'),
            "aiTags": ai_tags,
            "specs": specs,
            "searchTokens": search_text,
            "description": item.get('description', '').strip()
        }

    def _normalize_brand(self, brand: str) -> str:
        """Normalize brand names (remove generic suffixes)."""
        brand = brand.strip().title()
        # Remove common suffixes
        for suffix in [' Keyboards', ' Synths', ' Instruments', ' Inc.', ' Ltd.']:
            if brand.endswith(suffix):
                brand = brand[:-len(suffix)].strip()
        return brand

    def _parse_price(self, price_value: Any) -> float:
        """Safely parse price from various formats."""
        try:
            if isinstance(price_value, str):
                # Remove common currency symbols
                cleaned = price_value.replace(
                    '$', '').replace('€', '').replace('£', '')
                return float(cleaned.split()[0])
            return float(price_value)
        except (ValueError, AttributeError, IndexError):
            return 0.0

    def _determine_tier(self, price: float) -> str:
        """Determine product tier based on price."""
        if price < 500:
            return 'entry'
        elif price < 1500:
            return 'mid'
        elif price < 4000:
            return 'pro'
        else:
            return 'flagship'

    def _generate_search_tokens(self, item: Dict, brand: str, tier: str) -> str:
        """Generate a search string combining multiple fields."""
        components = [
            item.get('name', ''),
            brand,
            item.get('category', ''),
            item.get('subCategory', ''),
            tier,
            ' '.join(item.get('tags', [])) if item.get('tags') else '',
            item.get('description', '')[:100]  # First 100 chars of description
        ]
        search_text = ' '.join(str(c) for c in components if c)
        return search_text.lower()

    def _validate_item(self, item: Dict) -> bool:
        """
        QUALITY GATE: Rejects items that don't meet the standard.
        Soft warnings for non-critical issues.
        """
        is_valid = True
        item_ref = f"{item['id']} ({item['name']})"

        # Critical: Name required
        if not item['name'] or len(item['name'].strip()) < 2:
            self.validation_errors.append(f"Missing/Invalid Name: {item_ref}")
            is_valid = False

        # Critical: Brand required
        if not item['brand'] or item['brand'] == 'Generic':
            self.validation_errors.append(f"Missing Brand: {item_ref}")
            is_valid = False

        # Soft warning: Zero price for in-stock items
        if item['price'] == 0 and item['stockStatus'] == 'in_stock':
            self.validation_warnings.append(
                f"Zero price (in-stock): {item_ref}")

        # Soft warning: Missing main image
        if '/placeholders/' in item['images']['main']:
            self.validation_warnings.append(
                f"Using placeholder image: {item_ref}")

        return is_valid

    def export_golden_json(self, output_path: str) -> bool:
        """
        Outputs the 'Super Solid' single source of truth.

        Returns:
            True if export successful, False otherwise
        """
        if not self.products:
            logger.error("❌ No products to export! Refinery is empty.")
            return False

        # Prepare output directory
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        payload = {
            "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "version": "5.2.0",
            "stats": {
                "totalProducts": len(self.products),
                "brandsCount": len(set(p['brand'] for p in self.products))
            },
            "products": self.products,
            "categories": self._extract_category_tree()
        }

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)

            file_size = os.path.getsize(output_path)
            logger.info(
                f"✅ SUCCESS: Exported {len(self.products)} products to {output_path} ({file_size} bytes)")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to export: {e}")
            return False

    def _extract_category_tree(self) -> Dict[str, List[str]]:
        """Extract unique category → subcategories mapping."""
        tree = {}
        for p in self.products:
            category = p.get('category', 'Uncategorized')
            subcategory = p.get('subCategory', 'General')

            if category not in tree:
                tree[category] = []
            if subcategory not in tree[category]:
                tree[category].append(subcategory)

        return tree

    def print_report(self):
        """Print a human-readable report of the refinement process."""
        logger.info("\n" + "="*60)
        logger.info("📊 REFINERY REPORT")
        logger.info("="*60)
        logger.info(f"Products Accepted: {len(self.products)}")
        logger.info(f"Validation Errors: {len(self.validation_errors)}")
        logger.info(f"Validation Warnings: {len(self.validation_warnings)}")

        if self.validation_errors:
            logger.warning("\n⚠️  Validation Errors:")
            for err in self.validation_errors[:5]:  # Show first 5
                logger.warning(f"  - {err}")
            if len(self.validation_errors) > 5:
                logger.warning(
                    f"  ... and {len(self.validation_errors) - 5} more")

        if self.validation_warnings:
            logger.info("\nℹ️  Validation Warnings:")
            for warn in self.validation_warnings[:5]:  # Show first 5
                logger.info(f"  - {warn}")
            if len(self.validation_warnings) > 5:
                logger.info(
                    f"  ... and {len(self.validation_warnings) - 5} more")

        logger.info(f"\n📁 Categories: {len(self._extract_category_tree())}")
        logger.info(f"🏢 Brands: {len(set(p['brand'] for p in self.products))}")
        logger.info("="*60 + "\n")


# --- Usage Example ---
if __name__ == "__main__":
    """
    Standalone execution: Load existing JSON dumps and refine them.
    """
    import sys

    # Determine base path
    script_dir = Path(__file__).parent.parent
    data_dir = script_dir / "data" / "5_golden"
    output_path = script_dir.parent / "frontend" / \
        "public" / "data" / "galaxy_db.json"

    # Initialize refinery
    refinery = DataRefinery()

    # Load all JSON files from data/5_golden/
    if data_dir.exists():
        json_files = list(data_dir.glob("*.json"))
        logger.info(f"Found {len(json_files)} source files to process")

        for json_file in json_files:
            try:
                logger.info(f"Loading {json_file.name}...")
                with open(json_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)

                # Handle both single object and list of objects
                items = raw_data if isinstance(raw_data, list) else [raw_data]
                refinery.ingest_raw_data(items)
            except Exception as e:
                logger.error(f"Failed to load {json_file.name}: {e}")
    else:
        logger.warning(f"Data directory not found: {data_dir}")
        logger.info("Using empty dataset for testing...")

    # Export the golden JSON
    refinery.print_report()
    success = refinery.export_golden_json(str(output_path))

    sys.exit(0 if success else 1)
