#!/usr/bin/env python
"""
Inspect product graph vs OpenClaw hints for a single brand.

Usage (from project root):
  PYTHONPATH=. .venv/bin/python backend/scripts/inspect_brand_graph.py --brand roland

Shows:
  - Product count for the brand
  - Family counts, split by source (graph vs openclaw)
  - Relationship counts, including how many edges are tagged as coming from OpenClaw
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from typing import Dict, List

from backend.product_normalizer import build_catalog
from backend.project_config import FRONTEND_PUBLIC_DATA


def inspect_brand(brand_query: str | None = None) -> None:
    catalog = build_catalog(str(FRONTEND_PUBLIC_DATA), resolve=False)
    products = catalog.get("products", []) or []
    families_meta: Dict[str, dict] = catalog.get("families", {}) or {}
    indexes = catalog.get("indexes", {}) or {}
    rels: Dict[str, List[dict]] = indexes.get("relationships", {}) or {}

    # Normalize brand filter
    brand_filter = (brand_query or "").strip().lower()

    # Map product_id -> brand (normalized)
    pid_to_brand: Dict[str, str] = {}
    for p in products:
        pid = p.get("id")
        brand = (p.get("brand") or "").strip()
        if not pid or not brand:
            continue
        pid_to_brand[pid] = brand

    # Determine which brands we actually have
    all_brands = sorted({b for b in pid_to_brand.values()})

    if not brand_filter:
        print("Available brands (sample):", ", ".join(all_brands[:20]))
        print("Use --brand to focus on one (case-insensitive).")
        return

    # Resolve brand filter to canonical name
    target_brands = {b for b in all_brands if b.lower() == brand_filter}
    if not target_brands:
        # Fallback: substring match
        target_brands = {b for b in all_brands if brand_filter in b.lower()}
    if not target_brands:
        print(f"No products found for brand filter: {brand_query!r}")
        return

    print(f"Inspecting brand(s): {', '.join(sorted(target_brands))}")

    # Filter products for this brand set
    brand_pids = {pid for pid, b in pid_to_brand.items() if b in target_brands}
    print(f"PRODUCTS_FOR_BRAND {len(brand_pids)}")

    # Families for this brand
    family_counts_by_source: Counter[str] = Counter()
    brand_families = []
    for fid, meta in families_meta.items():
        b = (meta.get("brand") or "").strip()
        if b not in target_brands:
            continue
        src = meta.get("source") or "graph"
        family_counts_by_source[src] += 1
        brand_families.append((fid, meta))

    total_families = sum(family_counts_by_source.values())
    print(f"FAMILIES_TOTAL {total_families}")
    for src, cnt in family_counts_by_source.most_common():
        print(f"  FAMILIES_SOURCE {src}: {cnt}")

    # Relationships touching this brand's products
    rel_edge_total = 0
    rel_edge_by_source: Counter[str] = Counter()
    rel_nodes_set = set()

    for pid, edges in rels.items():
        # Only count edges if this node is in the brand product set
        if pid not in brand_pids:
            continue
        for r in edges:
            src = r.get("source") or "graph"
            rel_edge_total += 1
            rel_edge_by_source[src] += 1
            rel_nodes_set.add(pid)

    print(f"REL_NODES_FOR_BRAND {len(rel_nodes_set)}")
    print(f"REL_EDGES_FOR_BRAND {rel_edge_total}")
    for src, cnt in rel_edge_by_source.most_common():
        print(f"  REL_EDGES_SOURCE {src}: {cnt}")

    # Small samples
    print("\nSAMPLE_FAMILIES_FOR_BRAND (up to 5)")
    for fid, meta in brand_families[:5]:
        print(
            fid,
            "->",
            {
                "family_name": meta.get("family_name"),
                "brand": meta.get("brand"),
                "series": meta.get("series"),
                "variant_count": meta.get("variant_count"),
                "source": meta.get("source", "graph"),
            },
        )

    print("\nSAMPLE_RELATIONSHIPS_FOR_BRAND (up to 5 nodes)")
    shown = 0
    for pid, edges in rels.items():
        if shown >= 5:
            break
        if pid not in brand_pids:
            continue
        # Show a trimmed view of each edge
        trimmed = []
        for r in edges[:5]:
            trimmed.append(
                {
                    "source_id": r.get("source_id"),
                    "target_id": r.get("target_id"),
                    "type": r.get("relationship_type"),
                    "source": r.get("source", "graph"),
                }
            )
        print(pid, "->", trimmed)
        shown += 1


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Inspect product graph vs OpenClaw hints for a brand"
    )
    ap.add_argument(
        "--brand",
        type=str,
        help="Brand name (case-insensitive, e.g. 'Roland'). If omitted, prints available brands.",
    )
    args = ap.parse_args()
    inspect_brand(args.brand)


if __name__ == "__main__":
    main()

