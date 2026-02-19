#!/usr/bin/env python3
"""
Run vision AI on product family hero images to classify type and suggest merges.

Useful when many visually similar items (e.g. guitar bags) are split across
multiple series; the script suggests grouping them under one item.

Requires: catalog_cache.json.gz (run prebuild_catalog_cache.py if missing),
          GEMINI_API_KEY in .env (see .env.example).

Usage:
  PYTHONPATH=. python backend/scripts/visual_grouping_suggest.py [--brand BESPECO] [--limit 10] [--json out.json]
  PYTHONPATH=. python backend/scripts/visual_grouping_suggest.py --brand BESPECO --apply   # verify and apply overrides
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

# .env is loaded by backend.env_secrets when the API key is first needed


def load_catalog(data_dir: Path) -> dict:
    """Load catalog from cache or build (slow)."""
    cache_path = data_dir / "catalog_cache.json.gz"
    if cache_path.exists():
        with gzip.open(cache_path, "rb") as f:
            return json.loads(f.read().decode("utf-8"))
    from backend.product_normalizer import build_catalog
    from backend.project_config import FRONTEND_PUBLIC_DATA
    return build_catalog(str(FRONTEND_PUBLIC_DATA), resolve=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Visual grouping: classify families and suggest merges")
    parser.add_argument("--brand", type=str, help="Only run for this brand (e.g. Bespeco)")
    parser.add_argument("--limit", type=int, default=0, help="Max families to classify (0 = all)")
    parser.add_argument("--json", type=str, metavar="PATH", help="Write full report to JSON file")
    parser.add_argument("--apply", action="store_true", help="Verify and apply suggested merges (write overrides)")
    parser.add_argument("--min-confidence", type=float, default=0.7, help="Min confidence to apply a merge (default 0.7)")
    parser.add_argument("--data-dir", type=str, default=None, help="Backend data dir (default: backend/data)")
    args = parser.parse_args()

    from backend.project_config import DATA_DIR
    from backend.visual_grouping import run_visual_grouping_suggest, verify_and_apply

    data_dir = Path(args.data_dir) if args.data_dir else DATA_DIR

    print("Loading catalog...")
    catalog = load_catalog(data_dir)
    if not catalog.get("products"):
        print("No products in catalog. Run prebuild_catalog_cache.py first.", file=sys.stderr)
        return 1

    limit = args.limit if args.limit > 0 else 9999
    print("Classifying families with vision AI...")
    report = run_visual_grouping_suggest(catalog, brand=args.brand, limit=limit)

    results = report["results"]
    suggested_merges = report["suggested_merges"]
    for i, r in enumerate(results):
        label = r.get("visual_type") or r.get("error") or "?"
        match = "✓" if (r.get("visual_type_normalized") == r.get("series_key")) else "→ suggest"
        print(f"  [{i+1}/{len(results)}] {r.get('family_name') or (r.get('family_id') or '')[:20]} — {label} {match}")

    if args.json:
        out_path = Path(args.json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\nWrote report to {out_path}")

    if suggested_merges:
        print("\n--- Suggested merges ---")
        for m in suggested_merges:
            print(f"  {m['brand_key']} / {m['visual_type_normalized']}: merge {m['current_series_keys']}")
        if args.apply:
            apply_result = verify_and_apply(report, min_confidence=args.min_confidence)
            print(f"\nApplied: {apply_result['applied']} family overrides written to {apply_result['path']}")
            if apply_result.get("skipped_low_confidence"):
                print(f"Skipped (low confidence): {len(apply_result['skipped_low_confidence'])}")
    else:
        print("\nNo merge suggestions (all visual types match current series).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
