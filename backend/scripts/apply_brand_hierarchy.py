#!/usr/bin/env python3
"""
Apply Brand Hierarchy — Group products into families based on manufacturer naming rules.

Runs BrandHierarchyEngine to:
1. Group products by Brand → Category → Series/Model (e.g. Nord Stage 4, Yamaha P-145)
2. Assign family_id and variant labels to each product
3. Create VARIANT_OF edges between siblings in each family
4. Persist families + relationships to product_graph.json

Run after apply_taxonomy_fix.py (so products have correct categories). Then restart backend
or rebuild catalog to see families in the frontend.

Usage:
    PYTHONPATH=. python backend/scripts/apply_brand_hierarchy.py
"""

import logging
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("apply_brand_hierarchy")

DATA_DIR = ROOT / "frontend" / "public" / "data"


def apply_hierarchy() -> int:
    """Apply brand hierarchy rules and persist to product_graph.json."""
    logger.info("👑 Applying Brand Hierarchy Rules...")

    if not DATA_DIR.exists():
        logger.error("❌ Data directory not found: %s", DATA_DIR)
        return 1

    from backend.product_normalizer import build_catalog
    from backend.product_graph import ProductGraph
    from backend.product_graph_store import get_graph_store
    from backend.ingestion.brand_hierarchy import BrandHierarchyEngine

    # 1) Build catalog from frontend/public/data/*.json (normalized products)
    catalog = build_catalog(str(DATA_DIR))
    products = catalog.get("products", [])
    if not products:
        logger.warning("⚠️ No products in catalog — nothing to organize")
        return 0

    logger.info("   Loaded %d products from catalog", len(products))

    # 2) Build graph and load persisted families/relationships
    graph = ProductGraph.from_flat_products(products)
    store = get_graph_store()
    graph = store.load_graph_overlay(graph)

    before_families = len(graph.families)
    before_rels = len(graph.relationships)

    # 3) Run BrandHierarchyEngine (mutates graph in place)
    engine = BrandHierarchyEngine()
    engine.organize_catalog(graph)

    after_families = len(graph.families)
    after_rels = len(graph.relationships)

    # 4) Persist to product_graph.json
    store.export_json_snapshot(graph)

    logger.info(
        "✅ Created %d strict product families (total: %d), "
        "%d relationships (added %d)",
        after_families - before_families,
        after_families,
        after_rels,
        after_rels - before_rels,
    )
    if graph.families:
        sample = next(iter(graph.families.values()))
        logger.info(
            "   e.g. '%s' contains %d variants",
            sample.family_name,
            len(sample.variant_ids),
        )
    logger.info("👉 Restart backend or rebuild catalog to see families in the frontend.")
    return 0


if __name__ == "__main__":
    sys.exit(apply_hierarchy())
