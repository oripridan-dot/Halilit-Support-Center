#!/usr/bin/env python3
"""
Detective script: analyze the "Other" bucket and suggest missing keywords.

Loads products from frontend/public/data/*.json (and especially the "Other" brand file),
finds unclassified products (category Other or missing), extracts common words,
and runs the Active Classifier on samples to preview fixes.

Usage:
    PYTHONPATH=. python backend/scripts/analyze_and_fix_taxonomy.py
"""

import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "frontend" / "public" / "data"
EXCLUDED = {"index.json", "search_index.json", "search_index_min.json", "galaxy_db.json", "package.json"}
SKIP_WORDS = {"the", "and", "with", "for", "pro", "black", "white", "pair", "set", "new", "deluxe"}


def load_all_products():
    """Load all products from brand JSONs."""
    products = []
    if not DATA_DIR.exists():
        return products
    for f in sorted(DATA_DIR.glob("*.json")):
        if f.name in EXCLUDED:
            continue
        try:
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)
            raw = data if isinstance(data, list) else data.get("products", [])
            for p in raw:
                p["_file"] = f.stem
                products.append(p)
        except Exception as e:
            print(f"  Skip {f.name}: {e}")
    return products


def get_category(p):
    """Get canonical category from product."""
    tax = p.get("taxonomy") or {}
    return (tax.get("canonical_category") or p.get("category") or "").strip()


def run_analysis():
    print("🔍 Loading products from frontend/public/data...")
    all_products = load_all_products()
    if not all_products:
        print("❌ No products found. Run skeleton-sync or ingest first.")
        return

    # 1. Unclassified: category Other or missing
    other_products = [
        p for p in all_products
        if get_category(p).lower() in ("other", "uncategorized", "none", "") or not get_category(p)
    ]
    # Also include products from the "Other" brand file (unmatched from sitemap)
    other_brand_products = [p for p in all_products if (p.get("_file") or "").lower() == "other"]
    # Union: either in Other file or has Other category
    unclassified = list({id(p.get("halilit_id") or p.get("id") or i): p for i, p in enumerate(other_products + other_brand_products)}.values())

    print(f"📊 Total products: {len(all_products)}")
    print(f"📊 Unclassified (Other category or from 'Other' brand): {len(unclassified)}")

    if not unclassified:
        print("✅ No 'Other' / unclassified products to analyze.")
        return

    # 2. Extract common words from unclassified names
    word_counter = Counter()
    for p in unclassified:
        name = (p.get("product_name") or p.get("name") or p.get("official_name") or "").lower()
        name = name.replace("-", " ").replace("/", " ")
        words = [w for w in name.split() if len(w) > 2 and w not in SKIP_WORDS]
        word_counter.update(words)

    print("\n🚨 TOP MISSING KEYWORDS (consider adding to learned_taxonomy or universal taxonomy):")
    for word, count in word_counter.most_common(25):
        print(f"   - {word} ({count} products)")

    # 3. Dry run: preview Active Classifier on samples
    print("\n🧪 Testing Active Classifier on 10 samples:")
    from backend.ingestion.taxonomy_manager import get_taxonomy_manager
    manager = get_taxonomy_manager()
    for p in unclassified[:10]:
        name = p.get("product_name") or p.get("name") or "?"
        brand = (p.get("brand") or p.get("_file") or "?").strip()
        desc = (p.get("description") or p.get("page_description") or "")[:200]
        specs = p.get("specifications") or p.get("official_specs") or {}
        price = p.get("price_il") or p.get("price") or 0
        try:
            price = float(price)
        except (TypeError, ValueError):
            price = 0
        cat, subcat, conf = manager.classify_product(name, brand, desc, specs, price=price)
        print(f"   '{name[:50]}...' (brand={brand})")
        print(f"      → {cat} > {subcat} (conf={conf:.2f})")

    print("\n👉 Run: PYTHONPATH=. python backend/scripts/apply_taxonomy_fix.py")
    print("   to write taxonomy back to brand JSONs and get Other down to zero.")


if __name__ == "__main__":
    run_analysis()
