#!/usr/bin/env python3
"""
Apply taxonomy fixes: reclassify products with "Other" (or missing) category
using the Active Classifier and write taxonomy back to frontend/public/data/*.json.

Run after upgrading TaxonomyManager. Then run sync + rebuild-catalog to refresh the app.

Usage:
    PYTHONPATH=. python backend/scripts/apply_taxonomy_fix.py
    PYTHONPATH=. python backend/scripts/apply_taxonomy_fix.py --dry-run
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "frontend" / "public" / "data"
EXCLUDED = {"index.json", "search_index.json", "search_index_min.json", "galaxy_db.json", "package.json"}


def get_category(p):
    """Get canonical category from product."""
    tax = p.get("taxonomy") or {}
    return (tax.get("canonical_category") or p.get("category") or "").strip()


def needs_fix(p):
    """True if product has Other or no category."""
    cat = get_category(p)
    return cat.lower() in ("other", "uncategorized", "none", "") or not cat


def apply_fix(dry_run: bool = False):
    print("🔧 Applying Taxonomy Fixes (Active Classifier)...")
    if not DATA_DIR.exists():
        print(f"❌ Data directory not found: {DATA_DIR}")
        return 1

    from backend.ingestion.taxonomy_manager import get_taxonomy_manager
    manager = get_taxonomy_manager()

    fixed_count = 0
    files_updated = 0

    for path in sorted(DATA_DIR.glob("*.json")):
        if path.name in EXCLUDED:
            continue
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"  Skip {path.name}: {e}")
            continue

        products = data if isinstance(data, list) else data.get("products", [])
        if not products:
            continue

        changed = False
        for p in products:
            if not needs_fix(p):
                continue
            name = p.get("product_name") or p.get("name") or "?"
            brand = (p.get("brand") or path.stem or "?").strip()
            desc = (p.get("description") or p.get("page_description") or "")[:500]
            specs = p.get("specifications") or p.get("official_specs") or {}
            price = p.get("price_il") or p.get("price") or 0
            try:
                price = float(price)
            except (TypeError, ValueError):
                price = 0
            cat, subcat, _ = manager.classify_product(name, brand, desc, specs, price=price)
            if cat.lower() in ("other", "uncategorized", ""):
                continue
            if "taxonomy" not in p or not isinstance(p["taxonomy"], dict):
                p["taxonomy"] = {}
            p["taxonomy"]["canonical_category"] = cat
            p["taxonomy"]["canonical_subcategory"] = subcat
            if p.get("category") in ("Other", "Uncategorized", "", None):
                p["category"] = cat
            fixed_count += 1
            changed = True

        if changed and not dry_run:
            with open(path, "w", encoding="utf-8") as f:
                if isinstance(data, list):
                    json.dump(products, f, indent=2, ensure_ascii=False)
                else:
                    data["products"] = products
                    json.dump(data, f, indent=2, ensure_ascii=False)
            files_updated += 1
            print(f"  ✅ {path.name}: taxonomy updated")

    if dry_run:
        print(f"✅ [DRY RUN] Would recategorize {fixed_count} products")
    else:
        print(f"✅ Successfully recategorized {fixed_count} products in {files_updated} files")
    print("👉 Run sync + rebuild-catalog to refresh the app catalog.")
    return 0


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    sys.exit(apply_fix(dry_run=dry_run))
