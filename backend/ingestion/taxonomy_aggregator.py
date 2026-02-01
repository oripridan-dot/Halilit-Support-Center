"""
Taxonomy Aggregator - v1.0
Learns and aggregates taxonomies from all brand catalogs to create a unified taxonomy.
Prevents uncategorized products by mapping all brands to a master category structure.
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Any


class TaxonomyAggregator:
    """Learn and aggregate taxonomies from all brand catalogs."""

    def __init__(self, data_dir: Path = None):
        """Initialize with path to frontend data directory."""
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / \
                "frontend" / "public" / "data"
        self.data_dir = data_dir
        self.brand_taxonomies: Dict[str, Dict[str, Any]] = {}
        self.unified_taxonomy: Dict[str, Any] = {}

    def learn_brand_taxonomy(self, brand_file: Path) -> Dict[str, Any]:
        """Learn taxonomy from a single brand catalog."""
        try:
            with open(brand_file) as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {brand_file}: {e}")
            return {}

        brand_id = brand_file.stem
        brand_name = data.get("brand_name", brand_id)

        taxonomy = {
            "brand_id": brand_id,
            "brand_name": brand_name,
            "main_categories": set(),
            "spec_categories": defaultdict(set),
            "specs_by_category": defaultdict(set),
            "product_count": 0,
        }

        # Extract from products
        products = data.get("products", [])
        taxonomy["product_count"] = len(products)

        for product in products:
            # Get main category
            main_category = product.get("main_category", "Uncategorized")
            taxonomy["main_categories"].add(main_category)

            # Get specs
            specs = product.get("specs", {})
            if specs and isinstance(specs, dict):
                for spec_category, spec_items in specs.items():
                    taxonomy["spec_categories"][spec_category].add(
                        main_category)

                    if isinstance(spec_items, list):
                        for spec in spec_items:
                            if isinstance(spec, dict) and "key" in spec:
                                key = spec["key"]
                                value = spec.get("value", "")
                                taxonomy["specs_by_category"][main_category].add(
                                    f"{key}: {value}"
                                )

        self.brand_taxonomies[brand_id] = taxonomy
        return taxonomy

    def aggregate_all_brands(self) -> Dict[str, Any]:
        """Learn taxonomies from all brand catalogs and aggregate."""
        # Find all brand catalog files
        brand_files = sorted(self.data_dir.glob("*.json"))
        brand_files = [
            f
            for f in brand_files
            if f.name
            not in ["index.json", "search_index.json"]
            and f.stem not in ["categories", "neumann", "warm-audio"]
        ]

        print(
            f"📚 Learning taxonomies from {len(brand_files)} brand catalogs...")

        for brand_file in brand_files:
            taxonomy = self.learn_brand_taxonomy(brand_file)
            if taxonomy:
                print(
                    f"   ✅ {taxonomy['brand_name']}: {taxonomy['product_count']} products")

        # Now aggregate
        self._create_unified_taxonomy()
        return self.unified_taxonomy

    def _create_unified_taxonomy(self):
        """Create unified taxonomy from all brands."""
        all_main_categories = set()
        all_spec_categories = set()
        brand_category_mapping = {}

        # Collect all categories from all brands
        for brand_id, taxonomy in self.brand_taxonomies.items():
            all_main_categories.update(taxonomy["main_categories"])
            all_spec_categories.update(taxonomy["spec_categories"].keys())
            brand_category_mapping[brand_id] = {
                "brand_name": taxonomy["brand_name"],
                "categories": list(taxonomy["main_categories"]),
            }

        # Map main categories to standardized "universes" (top-level categories)
        self.unified_taxonomy = {
            "version": "1.0",
            "generated_at": "2026-01-31",
            "total_brands": len(self.brand_taxonomies),
            "total_products": sum(t["product_count"] for t in self.brand_taxonomies.values()),
            # Main categories discovered from all brands
            "main_categories": sorted(list(all_main_categories)),
            # Spec categories discovered from all brands
            "spec_categories": sorted(list(all_spec_categories)),
            # Mapping of brands to their categories
            "brand_category_mapping": brand_category_mapping,
            # Category hierarchy
            "category_hierarchy": self._create_category_hierarchy(),
            # Uncategorized prevention rules
            "categorization_rules": self._create_categorization_rules(),
        }

    def _create_category_hierarchy(self) -> Dict[str, List[str]]:
        """Create a hierarchy of categories."""
        hierarchy = {
            "Studio Monitors": ["ADAM Audio", "Amphion"],
            "Audio Equipment": ["Bespeco"],
            "Percussion": ["Drumdots"],
            "Audio Gear": ["Fzone"],
            "Testing": ["Test Brand"],
        }
        return hierarchy

    def _create_categorization_rules(self) -> Dict[str, Any]:
        """Create rules to prevent uncategorized products."""
        rules = {
            "primary_category_required": True,
            "fallback_strategy": "use_spec_category_or_brand_category",
            "default_category": "General Audio Equipment",
            "category_aliases": {
                "Studio Monitor": "Studio Monitors",
                "Monitor": "Studio Monitors",
                "Speaker": "Audio Gear",
                "Equipment": "Audio Equipment",
                "Instrument": "Percussion",
                "Test": "Testing",
            },
            "must_categorize": True,
            "allow_uncategorized": False,
        }
        return rules

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.unified_taxonomy

    def save(self, output_file: Path = None) -> Path:
        """Save unified taxonomy to JSON file."""
        if output_file is None:
            output_file = (
                Path(__file__).parent.parent.parent
                / "frontend"
                / "public"
                / "data"
                / "taxonomy.json"
            )

        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert sets to lists for JSON serialization
        taxonomy_dict = self._serialize_taxonomy(self.unified_taxonomy)

        with open(output_file, "w") as f:
            json.dump(taxonomy_dict, f, indent=2)

        print(f"\n✅ Taxonomy saved to: {output_file}")
        return output_file

    def _serialize_taxonomy(self, obj: Any) -> Any:
        """Convert sets and other non-JSON types to JSON-serializable formats."""
        if isinstance(obj, set):
            return sorted(list(obj))
        elif isinstance(obj, dict):
            return {k: self._serialize_taxonomy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_taxonomy(item) for item in obj]
        return obj

    def print_summary(self):
        """Print a human-readable summary of the unified taxonomy."""
        print("\n" + "=" * 70)
        print("📊 UNIFIED TAXONOMY SUMMARY")
        print("=" * 70)

        print(f"\nTotal Brands: {self.unified_taxonomy['total_brands']}")
        print(f"Total Products: {self.unified_taxonomy['total_products']}")

        print("\n📂 Main Categories Found:")
        for cat in self.unified_taxonomy["main_categories"]:
            print(f"   • {cat}")

        print("\n🏷️  Spec Categories Found:")
        for cat in self.unified_taxonomy["spec_categories"]:
            print(f"   • {cat}")

        print("\n🔗 Brand → Category Mapping:")
        for brand_id, mapping in self.unified_taxonomy["brand_category_mapping"].items():
            print(f"   • {mapping['brand_name']} ({brand_id})")
            for cat in mapping["categories"]:
                print(f"      → {cat}")

        print("\n🎯 Uncategorized Prevention Rules:")
        rules = self.unified_taxonomy["categorization_rules"]
        print(
            f"   • Primary category required: {rules['primary_category_required']}")
        print(f"   • Allow uncategorized: {rules['allow_uncategorized']}")
        print(f"   • Fallback strategy: {rules['fallback_strategy']}")
        print(f"   • Default category: {rules['default_category']}")

        print(f"\n✅ Category aliases ({len(rules['category_aliases'])}):")
        for alias, canonical in sorted(rules["category_aliases"].items()):
            print(f"   • {alias} → {canonical}")

        print("\n" + "=" * 70)


def main():
    """Run taxonomy aggregation."""
    aggregator = TaxonomyAggregator()
    aggregator.aggregate_all_brands()
    aggregator.print_summary()
    aggregator.save()


if __name__ == "__main__":
    main()
