"""
Extract relationship candidates from contextual sources (reviews, trusted sites).
Phrases like "compared to the Yamaha P-45", "alternative to the Roland FP-30",
"works with the Nord Stage 4" become relationship candidates with discovered_from="contextual".
"""

import logging
import re
from typing import List, Optional, Tuple

from backend.product_graph import (
    ProductGraph,
    ProductRelationship,
    RelationshipDirection,
    RelationshipType,
)

logger = logging.getLogger("RelationshipEnrichmentContextual")

# Review-style phrases that indicate a relationship
CONTEXTUAL_PATTERNS = [
    (r"compared\s+to\s+(?:the\s+)?([^.,;:\n]+)", RelationshipType.ALTERNATIVE_TO),
    (r"alternative\s+to\s+(?:the\s+)?([^.,;:\n]+)", RelationshipType.ALTERNATIVE_TO),
    (r"vs\.?\s+(?:the\s+)?([^.,;:\n]+)", RelationshipType.ALTERNATIVE_TO),
    (r"versus\s+(?:the\s+)?([^.,;:\n]+)", RelationshipType.ALTERNATIVE_TO),
    (r"similar\s+to\s+(?:the\s+)?([^.,;:\n]+)", RelationshipType.ALTERNATIVE_TO),
    (r"like\s+the\s+([^.,;:\n]+)", RelationshipType.ALTERNATIVE_TO),
    (r"works\s+with\s+(?:the\s+)?([^.,;:\n]+)", RelationshipType.COMPATIBLE_WITH),
    (r"paired\s+with\s+(?:the\s+)?([^.,;:\n]+)", RelationshipType.COMPATIBLE_WITH),
    (r"often\s+used\s+with\s+(?:the\s+)?([^.,;:\n]+)", RelationshipType.COMPATIBLE_WITH),
    (r"better\s+than\s+(?:the\s+)?([^.,;:\n]+)", RelationshipType.ALTERNATIVE_TO),
    (r"replacement\s+for\s+(?:the\s+)?([^.,;:\n]+)", RelationshipType.ALTERNATIVE_TO),
]


def _normalize_mention(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _resolve_product_mention(
    mention: str,
    brand_hint: Optional[str],
    graph: ProductGraph,
    exclude_id: Optional[str] = None,
) -> Optional[str]:
    mention_n = _normalize_mention(mention)
    if len(mention_n) < 2:
        return None
    mention_words = set(mention_n.split())
    best_id: Optional[str] = None
    best_score = 0

    for candidate_id, p in graph.products.items():
        if candidate_id == exclude_id:
            continue
        name_n = _normalize_mention(p.name)
        if not name_n:
            continue
        name_words = set(name_n.split())
        overlap = len(mention_words & name_words)
        if overlap == 0:
            continue
        score = overlap + (
            2 if (brand_hint and _normalize_mention(p.brand) == _normalize_mention(brand_hint)) else 0
        )
        if len(name_n) >= len(mention_n) and mention_n in name_n:
            score += 3
        if score > best_score:
            best_score = score
            best_id = candidate_id

    return best_id


def _extract_mentions_from_text(text: str) -> List[Tuple[str, RelationshipType]]:
    if not text:
        return []
    results: List[Tuple[str, RelationshipType]] = []
    text_lower = text.lower()
    for pattern, rel_type in CONTEXTUAL_PATTERNS:
        for m in re.finditer(pattern, text_lower, re.IGNORECASE):
            mention = (m.group(1) or "").strip()
            if 2 <= len(mention) <= 200:
                results.append((mention, rel_type))
    return results


def extract_contextual_relationship_candidates(graph: ProductGraph) -> List[ProductRelationship]:
    """
    For products with review_synthesis or reviews in contextual_data, extract
    product mentions and relationship type; resolve to catalog product IDs.
    Returns candidates with sources_verified including "contextual".
    """
    candidates: List[ProductRelationship] = []

    for pid, product in graph.products.items():
        review_text = ""
        if product.contextual_data and isinstance(product.contextual_data, dict):
            review_text = (product.contextual_data.get("review_synthesis") or "") + " " + (
                " ".join(
                    str(r.get("text", r) if isinstance(r, dict) else r)
                    for r in product.contextual_data.get("reviews", [])
                )
            )
        if not review_text and product.search_text:
            review_text = product.search_text
        if not review_text:
            continue

        seen_edges: set = set()
        for mention, rel_type in _extract_mentions_from_text(review_text):
            target_id = _resolve_product_mention(
                mention, product.brand, graph, exclude_id=pid
            )
            if not target_id:
                continue
            edge_key = (pid, target_id, rel_type)
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)

            direction = (
                RelationshipDirection.BIDIRECTIONAL
                if rel_type
                in (RelationshipType.ALTERNATIVE_TO, RelationshipType.COMPATIBLE_WITH)
                else RelationshipDirection.UNIDIRECTIONAL
            )

            rel = ProductRelationship(
                source_id=pid,
                target_id=target_id,
                relationship_type=rel_type,
                direction=direction,
                confidence=0.75,
                ai_discovered=True,
                discovered_from="contextual",
                compatibility_notes=f"From reviews: '{mention[:80]}'",
                sources_verified=["contextual"],
            )
            candidates.append(rel)

    if candidates:
        logger.info(f"Contextual enrichment: {len(candidates)} relationship candidates")
    return candidates
