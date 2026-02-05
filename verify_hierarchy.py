import json
import re
from pathlib import Path

print("\n" + "="*70)
print("CATEGORIZATION HIERARCHY VERIFICATION")
print("="*70)

# Load all products
all_products = []
brands_data = {}

index_path = Path("frontend/public/data/index.json")
with open(index_path) as f:
    index = json.load(f)

for brand_entry in index["brands"]:
    brand_file = Path(f"frontend/public/data/{brand_entry['data_file']}")
    with open(brand_file) as f:
        products = json.load(f)
    
    all_products.extend(products)
    brands_data[brand_entry["id"]] = {
        "name": brand_entry["name"],
        "products": products
    }

print(f"\nTotal products loaded: {len(all_products)}")

# Analyze categorization by tier
print("\n" + "="*70)
print("TIER 1: HALILIT DATA (canonical_category from ingestion)")
print("="*70)

tier1_categories = {}
tier1_count = 0

for p in all_products:
    category = p.get("category")
    if category and category.lower() != "none" and category.lower() != "uncategorized":
        tier1_categories[category] = tier1_categories.get(category, 0) + 1
        tier1_count += 1

print(f"\nProducts with valid Halilit category: {tier1_count}/{len(all_products)}")
if tier1_categories:
    print("\nCategory breakdown:")
    for cat in sorted(tier1_categories.keys()):
        count = tier1_categories[cat]
        print(f"  • {cat}: {count} products")

# Products still needing Tier 2 or 3
uncategorized = len(all_products) - tier1_count
print(f"\nProducts needing Tier 2/3 validation: {uncategorized}")

print("\n" + "="*70)
print("TIER 2: BRAND WEBSITE VALIDATION")
print("="*70)

# Analyze a sample of uncategorized products by brand
print(f"\nUncategorized products by brand (sample):")

brand_uncategorized = {}
for p in all_products:
    category = p.get("category")
    if category and (category.lower() == "none" or category.lower() == "uncategorized" or not category):
        brand = p.get("brand", "unknown")
        brand_uncategorized[brand] = brand_uncategorized.get(brand, 0) + 1

for brand in sorted(brand_uncategorized.keys(), key=lambda x: brand_uncategorized[x], reverse=True):
    count = brand_uncategorized[brand]
    print(f"  • {brand}: {count} products")

print("\n" + "="*70)
print("SAMPLE PRODUCTS FOR EACH TIER")
print("="*70)

# Show tier 1 examples
print("\nTier 1 examples (with valid Halilit category):")
tier1_examples = [p for p in all_products if p.get("category") and p.get("category").lower() not in ["none", "uncategorized", ""]][:3]
for p in tier1_examples:
    print(f"  • {p.get('brand')}/{p.get('name')}: {p.get('category')}")

# Show tier 2/3 candidates (products without category)
print("\nTier 2/3 candidates (need brand/contextual validation):")
tier2_3_candidates = [p for p in all_products if not p.get("category") or p.get("category").lower() in ["none", "uncategorized", ""]]
if tier2_3_candidates:
    for p in tier2_3_candidates[:5]:
        brand = p.get("brand", "?")
        name = p.get("name", "?")
        print(f"  • {brand}/{name} (specs: {bool(p.get('specifications'))})")

print("\n" + "="*70)
