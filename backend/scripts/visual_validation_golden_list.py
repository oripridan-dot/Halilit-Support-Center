#!/usr/bin/env python3
"""
Visual validation over the full Golden List
============================================
The Golden List is the union of all brand JSON files in frontend/public/data/*.json.
This script runs visual validation (commercial vs official image match, optional hero quality)
across that list and writes back confidence/coherency fields so data stays consistent.

Use this to:
- Persist visual_match_status and visual_match_confidence for every product that has both
  commercial and official images (improves coherency; mismatches are cleared).
- Optionally score hero image quality and store hero_quality_score / hero_validation_status.

Usage:
  PYTHONPATH=. python backend/scripts/visual_validation_golden_list.py
  PYTHONPATH=. python backend/scripts/visual_validation_golden_list.py --brand bespeco
  PYTHONPATH=. python backend/scripts/visual_validation_golden_list.py --dry-run --limit 50
  PYTHONPATH=. python backend/scripts/visual_validation_golden_list.py --hero-quality   # also validate hero image quality (slower)
  PYTHONPATH=. python backend/scripts/visual_validation_golden_list.py --refine        # only validate products missing visual_match_status (fast reruns)

Set INGESTION_SKIP_VISUAL_VALIDATION=1 to skip all validation (no-op).
Run from project root.
"""

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

DATA_DIR = _ROOT / "frontend" / "public" / "data"
EXCLUDED = {"index", "search_index", "search_index_min", "galaxy_db", "package"}


def load_brand_file(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data, "list"
    if isinstance(data, dict) and "products" in data:
        return data["products"], "dict"
    return [], "unknown"


def save_brand_file(path: Path, products: list, format_type: str):
    if format_type == "list":
        data = products
    elif format_type == "dict":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["products"] = products
    else:
        data = products
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    import argparse
    from backend.ingestion.visual_validator import (
        INGESTION_SKIP_VISUAL_VALIDATION,
        reject_official_if_mismatch,
        get_visual_validator,
    )

    parser = argparse.ArgumentParser(
        description="Run visual validation over the full Golden List; persist coherency/confidence."
    )
    parser.add_argument("--brand", type=str, help="Only process brand file(s) matching this stem")
    parser.add_argument("--dry-run", action="store_true", help="Do not write back to files")
    parser.add_argument("--limit", type=int, default=0, help="Max products per file to process (0 = all)")
    parser.add_argument(
        "--hero-quality",
        action="store_true",
        help="Also validate hero image quality and store hero_quality_score (one HTTP per product, slower)",
    )
    parser.add_argument(
        "--export",
        type=str,
        metavar="PATH",
        help="Export full golden list (all products) to a single JSON file, e.g. backend/data/golden_list.json",
    )
    parser.add_argument(
        "--refine",
        action="store_true",
        help="Only validate products that do not already have visual_match_status (matched/mismatch); skip rest for fast reruns",
    )
    args = parser.parse_args()

    if INGESTION_SKIP_VISUAL_VALIDATION:
        print("INGESTION_SKIP_VISUAL_VALIDATION is set; skipping validation.")
        return 0

    if not DATA_DIR.exists():
        print(f"Data directory not found: {DATA_DIR}")
        return 1

    files = [
        f for f in sorted(DATA_DIR.glob("*.json"))
        if f.suffix == ".json" and f.stem not in EXCLUDED
    ]
    if args.brand:
        brand_lower = args.brand.lower().replace(" ", "-")
        files = [f for f in files if brand_lower in f.stem.lower().replace(" ", "-")]
        if not files:
            print(f"No brand files matching '{args.brand}'.")
            return 1

    validator = get_visual_validator() if args.hero_quality else None
    stats = {"products": 0, "matched": 0, "mismatch": 0, "no_official": 0, "hero_fail": 0, "hero_pass": 0, "skipped_validated": 0}
    all_products_export = [] if args.export else None

    for path in files:
        products, fmt = load_brand_file(path)
        if not products:
            continue
        to_process = products[: args.limit] if args.limit else products
        print(f"  Processing {path.name} ({len(to_process)} products)...", flush=True)
        file_updated = False
        for p in to_process:
            stats["products"] += 1
            commercial = (p.get("image_url") or "").strip()
            official_list = p.get("official_images") or []
            official_hero = None
            if official_list:
                first = official_list[0]
                official_hero = (first.get("url") if isinstance(first, dict) else first) or ""
            if not commercial or not official_hero:
                stats["no_official"] += 1
                if args.hero_quality and commercial:
                    img_bytes, _ = validator.fetch_image_sync(commercial)
                    if img_bytes:
                        q = validator.validate_quality(img_bytes, purpose="hero")
                        p["hero_quality_score"] = q.get("score", 0)
                        p["hero_validation_status"] = q.get("status", "unknown")
                        if q.get("status") == "pass":
                            stats["hero_pass"] += 1
                        else:
                            stats["hero_fail"] += 1
                continue
            # --refine: skip products already validated (no HTTP, fast reruns)
            if args.refine and p.get("visual_match_status") in ("matched", "mismatch"):
                stats["skipped_validated"] += 1
                if p.get("visual_match_status") == "matched":
                    stats["matched"] += 1
                else:
                    stats["mismatch"] += 1
                continue
            # Run commercial vs official match (updates p in place: visual_match_*, clears official_* on mismatch)
            reject_official_if_mismatch(p)
            file_updated = True
            if p.get("visual_match_status") == "matched":
                stats["matched"] += 1
            elif p.get("visual_match_status") == "mismatch":
                stats["mismatch"] += 1
            if args.hero_quality and commercial:
                img_bytes, _ = validator.fetch_image_sync(commercial)
                if img_bytes:
                    q = validator.validate_quality(img_bytes, purpose="hero")
                    p["hero_quality_score"] = q.get("score", 0)
                    p["hero_validation_status"] = q.get("status", "unknown")
                    if q.get("status") == "pass":
                        stats["hero_pass"] += 1
                    else:
                        stats["hero_fail"] += 1
        if not args.dry_run and to_process and (file_updated or not args.refine):
            save_brand_file(path, products, fmt)
            print(f"  Updated {path.name} ({len(to_process)} products)")
        if all_products_export is not None:
            for p in products:
                out = dict(p)
                out["_brand_file"] = path.stem
                all_products_export.append(out)

    if all_products_export is not None and args.export:
        export_path = Path(args.export)
        if not export_path.is_absolute():
            export_path = _ROOT / export_path
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(all_products_export, f, indent=2, ensure_ascii=False)
        print(f"\nExported {len(all_products_export)} products to {export_path}")

    print("\n" + "=" * 60)
    print("GOLDEN LIST VISUAL VALIDATION SUMMARY")
    print("=" * 60)
    print(f"  Products processed:   {stats['products']}")
    print(f"  Commercial+official: matched {stats['matched']}, mismatch (cleared) {stats['mismatch']}")
    print(f"  No official image:     {stats['no_official']}")
    if args.refine and stats.get("skipped_validated", 0):
        print(f"  Skipped (already validated): {stats['skipped_validated']}")
    if args.hero_quality:
        print(f"  Hero quality:          pass {stats['hero_pass']}, fail {stats['hero_fail']}")
    print(f"  Dry run:              {args.dry_run} (no files written)" if args.dry_run else "  Files written.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
