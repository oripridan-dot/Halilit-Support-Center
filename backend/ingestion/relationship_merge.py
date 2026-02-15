"""
Merge relationship candidates from multiple sources (official, contextual)
into the product graph. Deduplicates by (source_id, target_id, relationship_type)
and merges sources_verified so triple-checked edges are promoted.

Relationship priority: 1=official, 2=commercial, 3=contextual, 4=spectrum.
Commercial and spectrum relationships are added by relationship_discovery
(discover_commercial / discover_spectrum_relations), not via this merge.
"""

import logging
from typing import List

from backend.product_graph import ProductGraph, ProductRelationship

logger = logging.getLogger("RelationshipMerge")


def merge_relationship_candidates(
    graph: ProductGraph,
    official_candidates: List[ProductRelationship],
    contextual_candidates: List[ProductRelationship],
) -> None:
    """
    Merge official and contextual relationship candidates into the graph.
    Only adds candidates where both source_id and target_id exist in graph.products.
    When an edge already exists (e.g. from pattern discovery), add_relationship
    will merge sources_verified and bump confidence.
    """
    def ensure_source(rel: ProductRelationship, tag: str) -> ProductRelationship:
        if not rel.sources_verified or tag not in rel.sources_verified:
            rel.sources_verified = list(rel.sources_verified) if rel.sources_verified else []
            if tag not in rel.sources_verified:
                rel.sources_verified.append(tag)
        return rel

    added = 0
    skipped = 0
    for rel in official_candidates:
        if rel.source_id not in graph.products or rel.target_id not in graph.products:
            skipped += 1
            continue
        ensure_source(rel, "official")
        graph.add_relationship(rel)
        added += 1

    for rel in contextual_candidates:
        if rel.source_id not in graph.products or rel.target_id not in graph.products:
            skipped += 1
            continue
        ensure_source(rel, "contextual")
        graph.add_relationship(rel)
        added += 1

    if official_candidates or contextual_candidates:
        graph.rebuild_indexes()
        logger.info(
            f"Relationship merge: applied {added} candidates, skipped {skipped} (missing products)"
        )
