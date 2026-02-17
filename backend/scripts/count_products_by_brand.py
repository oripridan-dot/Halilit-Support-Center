#!/usr/bin/env python3
"""
Count canonical items by brand.

CANONICAL ITEM = product series/line for best context: Stage, Lead, Piano, Electro, Grand, Wave, Drum, etc.
  - One canonical item = one SERIES (e.g. Nord Stage = all Stage 3/4 variants; Nord Lead = Lead A1; Nord Piano = Piano 5/6).
  - This gives the right items and products context: Stage, Lead, Piano, Electro, and so on.
  - ACCESSORIES (pedals, stands, covers, cases, bags) are grouped into ONE "Accessories" item per brand.
  - Orphan products (no family_id) count as 1 canonical item each.
  Example: Nord = Stage, Lead, Piano, Electro, Grand, Wave, Drum, … + Accessories.

Uses the same catalog as the app (conductor v10): either the pre-built cache
or a full build from frontend/public/data.

Usage:
    PYTHONPATH=. python backend/scripts/count_products_by_brand.py
    PYTHONPATH=. python backend/scripts/count_products_by_brand.py --csv [path]
    PYTHONPATH=. python backend/scripts/count_products_by_brand.py --scan [path]

  --scan       Verify canonical items for all brands: print each brand and its items (series + Accessories).
  --scan PATH  Same, and write full report JSON to PATH for review.

If backend/data/catalog_cache.json.gz exists, counts are read from there (fast).
Otherwise the catalog is built from scratch (slower).

Why 129 brands vs Halilit's 84?
  Our catalog has one "brand" per distinct brand string that appears on products.
  Halilit's 84 is the number of official brand pages (המותגים שלנו). The gap comes from:
  - Aliases: same brand under different names (e.g. "adam-audio" vs "ADAM Audio")
  - Buckets: "Other", "Sample", "-", "Show", "Halilit Expo" that aren't brand pages
  - Sub-brands or product lines we keep separate
  So "129" = distinct brand labels in our data; "84" = Halilit's official brand count.
"""

import argparse
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

# Brand labels that are buckets/placeholders, not Halilit official brand pages
NON_BRAND_LABELS = frozenset(
    {"other", "sample", "show", "halilit expo", "halilit", "-", ""}
)


# Words in family name that indicate an accessory (pedals, stands, covers, etc.).
# Semantic groups so e.g. all guitar bags/cases group under one item (cases-bags).
ACCESSORY_KEYWORDS = frozenset(
    {"pedal", "stand", "cover", "dust", "case", "bag", "monitor stand"}
)
ACCESSORY_SEMANTIC_GROUPS = [
    ("cases-bags", ("bag", "case", "cover", "dust")),
    ("stands", ("stand", "monitor stand")),
    ("pedals", ("pedal",)),
    ("other-accessories", ()),
]


def _is_accessory_family(family_name: str) -> bool:
    """True if this family is accessory-like (pedal, stand, cover, etc.)."""
    name = (family_name or "").lower()
    return any(kw in name for kw in ACCESSORY_KEYWORDS)


def _accessory_semantic_series(family_name: str) -> str:
    """Group accessory families: cases-bags, stands, pedals, other-accessories."""
    name = (family_name or "").lower()
    for group_key, keywords in ACCESSORY_SEMANTIC_GROUPS:
        if any(kw in name for kw in keywords):
            return group_key
    return "other-accessories"


def _normalize_series_token(token: str) -> str:
    """Collapse model numbers to product line: Vad316 → vad, Td713 → td, V → v."""
    if not token:
        return ""
    s = token.strip().lower()
    # Take leading letters only (strip trailing digits) so VAD307/VAD316 → vad, TD713 → td
    letters = "".join(c for c in s if c.isalpha())
    if letters:
        return letters
    # All digits or mixed: use first run of letters
    for i, c in enumerate(s):
        if c.isalpha():
            end = i + 1
            while end < len(s) and s[end].isalpha():
                end += 1
            return s[i:end]
    return s


def _series_key(brand: str, family_name: str, series: str, family_id: str) -> str:
    """Canonical item key. Accessories get semantic group (cases-bags, stands, pedals)."""
    name = (family_name or "").strip()
    if _is_accessory_family(name):
        return _accessory_semantic_series(name)
    s = (series or "").strip()
    if s:
        return s.lower()
    br = (brand or "").strip()
    if br and name.lower().startswith(br.lower() + " "):
        rest = name[len(br) :].strip()
        if rest:
            first_token = rest.split()[0].strip().lower()
            normalized = _normalize_series_token(first_token)
            if normalized:
                return normalized
            return first_token
    if name:
        first_token = name.split()[0].strip().lower()
        normalized = _normalize_series_token(first_token)
        if normalized:
            return normalized
        return first_token
    return (family_id or "").replace("fam_", "").split("_")[0].lower()


def main() -> int:
    parser = argparse.ArgumentParser(description="Count canonical products by brand")
    parser.add_argument(
        "--csv",
        metavar="PATH",
        nargs="?",
        const="",
        help="Write CSV to PATH (default: stdout). Use --csv to print CSV to stdout.",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Print short note on 129 vs Halilit 84 brands.",
    )
    parser.add_argument(
        "--scan",
        metavar="PATH",
        nargs="?",
        const="",
        help="Scan all brands: print each brand and its canonical items (series + Accessories). Optional PATH to write report JSON.",
    )
    args = parser.parse_args()

    from backend.project_config import DATA_DIR, FRONTEND_PUBLIC_DATA

    cache_path = DATA_DIR / "catalog_cache.json.gz"

    if cache_path.exists():
        with gzip.open(cache_path, "rt", encoding="utf-8") as f:
            catalog = json.load(f)
        source_note = "(from catalog cache)\n"
    else:
        source_note = "No catalog cache found. Building catalog from data (this may take a minute)...\n"
        from backend.product_normalizer import build_catalog

        catalog = build_catalog(str(FRONTEND_PUBLIC_DATA), resolve=False)
        if not catalog.get("products"):
            print("No products in catalog. Ensure frontend/public/data has brand JSON files.")
            return 1

    meta = catalog.get("metadata", {})
    brands_ordered = meta.get("brands", [])
    products = catalog.get("products", [])
    families_meta = catalog.get("families", {})

    # Canonical item = 1 per series (including semantic groups: cases-bags, stands, pedals) + orphans.
    main_series_keys_by_brand: dict[str, set[str]] = {}
    for fid, fam in families_meta.items():
        b = (fam.get("brand") or "").strip().lower()
        if not b:
            continue
        family_name = fam.get("family_name", "") or ""
        sk = _series_key(
            fam.get("brand", ""),
            family_name,
            fam.get("series", ""),
            fid,
        )
        main_series_keys_by_brand.setdefault(b, set()).add(sk)
    canonical_item_count_by_brand: dict[str, int] = {
        b: len(keys) for b, keys in main_series_keys_by_brand.items()
    }
    orphan_count_by_brand: dict[str, int] = {}
    for p in products:
        if (p.get("family_id") or "").strip():
            continue
        b = (p.get("brand") or "").strip().lower()
        if b:
            orphan_count_by_brand[b] = orphan_count_by_brand.get(b, 0) + 1
    all_brand_keys = set(canonical_item_count_by_brand) | set(orphan_count_by_brand)
    brand_counts = {
        b: canonical_item_count_by_brand.get(b, 0) + orphan_count_by_brand.get(b, 0)
        for b in all_brand_keys
    }

    def display_name(key: str) -> str:
        for b in brands_ordered:
            if b.lower() == key:
                return b
        return key.title() if key else key

    rows = [(display_name(k), v) for k, v in brand_counts.items()]
    rows.sort(key=lambda x: (-x[1], x[0].lower()))
    total = sum(c for _, c in rows)

    # Scan/verify: for each brand list its canonical items (series + Accessories + orphans)
    if args.scan is not None:
        print(source_note)
        print("Scan: canonical items per brand (series + Accessories + orphans)\n")
        report = []
        for b in sorted(all_brand_keys, key=lambda x: (-brand_counts.get(x, 0), x)):
            display = display_name(b)
            items = sorted(main_series_keys_by_brand.get(b, set()))
            orphans = orphan_count_by_brand.get(b, 0)
            if orphans:
                items.append(f"+{orphans} orphan(s)")
            count = brand_counts.get(b, 0)
            report.append({
                "brand": display,
                "brand_key": b,
                "canonical_item_count": count,
                "items": items,
                "orphan_count": orphans,
            })
            print(f"  {display} ({count}): {', '.join(items)}")
        if args.scan != "":
            out = Path(args.scan)
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                json.dump({"brands": report, "total_brands": len(report), "total_canonical_items": total}, f, indent=2)
            print(f"\nWrote scan report to {out}")
        else:
            print(f"\nTotal: {len(report)} brands, {total} canonical items")
        return 0

    if args.csv is not None:
        # CSV output: brand, canonical_product_count (with self-describing comment)
        import csv as csv_module
        canonical_comment = (
            "# canonical_item_count = 1 per series (Stage, Lead, Piano, Electro, …) + 1 Accessories per brand (if any) + orphans. "
            "Items = series for best product context."
        )
        if args.csv == "":
            w = csv_module.writer(sys.stdout)
            print(canonical_comment)
            w.writerow(["brand", "canonical_item_count"])
            for name, count in rows:
                w.writerow([name, count])
        else:
            out = Path(args.csv)
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out, "w", newline="", encoding="utf-8") as f:
                f.write(canonical_comment + "\n")
                w = csv_module.writer(f)
                w.writerow(["brand", "canonical_item_count"])
                for name, count in rows:
                    w.writerow([name, count])
            print(f"Wrote {len(rows)} brands to {out}")
        return 0

    if args.explain:
        bucket_brands = [r for r in rows if r[0].lower().strip() in NON_BRAND_LABELS]
        bucket_count = sum(c for _, c in bucket_brands)
        core_count = len(rows) - len(bucket_brands)
        print(
            "Why 129 vs Halilit's 84? Our catalog counts every distinct brand string on products.\n"
            "Halilit's 84 = official brand pages (המותגים שלנו). Extra in ours: aliases (e.g.\n"
            "ADAM Audio vs adam-audio), plus bucket labels like Other, Sample, -, Show, Halilit Expo.\n"
        )
        if bucket_brands:
            print(f"Bucket / non-brand labels in catalog: {len(bucket_brands)} labels, {bucket_count} products")
            for name, count in bucket_brands:
                print(f"  {name!r}: {count}")
            print(f"Core brand labels (excluding above): {core_count} brands\n")

    print(source_note)
    print(
        "Canonical item = series (Stage, Lead, Piano, Electro, …) + 1 Accessories per brand (if any) + orphans. "
        "Items give the right product context.\n"
    )
    width = max(len(str(c)) for _, c in rows) if rows else 0
    name_width = max(len(n) for n, _ in rows) if rows else 0

    print("Canonical items by brand")
    print("=" * (name_width + width + 6))
    for name, count in rows:
        print(f"  {name:<{name_width}}  {count:>{width}}")
    print("=" * (name_width + width + 6))
    print(f"  {'TOTAL':<{name_width}}  {total:>{width}}")
    print(f"\n  {len(rows)} brands, {total} canonical items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
