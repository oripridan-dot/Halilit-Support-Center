"""
Extract relationship candidates from official sources (brand product pages).
Official brand product pages are the FIRST and MOST INFLUENTIAL source for relations:
they typically list accessories, related products, "you may also like", and compatible
products. We fetch official_url when present and parse those sections, then fall back
to text extraction from description/specs.
"""

import json
import logging
import re
import time
from typing import List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from backend.product_graph import (
    ProductGraph,
    ProductRelationship,
    RelationshipDirection,
    RelationshipType,
)

logger = logging.getLogger("RelationshipEnrichmentOfficial")

# Request limits so catalog build doesn't hammer brand sites
OFFICIAL_FETCH_TIMEOUT = 10
OFFICIAL_FETCH_DELAY_SEC = 0.4
OFFICIAL_FETCH_MAX_PER_RUN = 80

# Section headings on brand pages that indicate related products (lowercase for match)
# Brand-specific terms (Allen & Heath, RCF, Pro Audio) ensure strict adherence to manufacturer structure.
RELATED_SECTION_HEADINGS = [
    ("accessories", RelationshipType.ACCESSORY_FOR),
    ("related products", RelationshipType.COMPATIBLE_WITH),
    ("you may also like", RelationshipType.ALTERNATIVE_TO),
    ("compatible with", RelationshipType.COMPATIBLE_WITH),
    ("recommended", RelationshipType.ACCESSORY_FOR),
    ("recommended accessories", RelationshipType.ACCESSORY_FOR),
    ("also in this series", RelationshipType.VARIANT_OF),
    ("complete your setup", RelationshipType.ACCESSORY_FOR),
    ("frequently bought together", RelationshipType.BUNDLE_WITH),
    ("similar products", RelationshipType.ALTERNATIVE_TO),
    ("alternatives", RelationshipType.ALTERNATIVE_TO),
    # Brand-specific (Pro Audio / PA)
    ("compatible accessories", RelationshipType.ACCESSORY_FOR),
    ("works with", RelationshipType.COMPATIBLE_WITH),
    ("optional extras", RelationshipType.ACCESSORY_FOR),
    ("system components", RelationshipType.BUNDLE_WITH),
    ("expansion options", RelationshipType.ACCESSORY_FOR),
]

# Phrases that indicate a relationship, and the relationship type to suggest
# (mention is the product name fragment we extract)
OFFICIAL_PATTERNS = [
    (r"compatible\s+with\s+([^.,;:\n]+)", RelationshipType.COMPATIBLE_WITH),
    (r"works\s+with\s+([^.,;:\n]+)", RelationshipType.COMPATIBLE_WITH),
    (r"designed\s+for\s+([^.,;:\n]+)", RelationshipType.ACCESSORY_FOR),
    (r"for\s+use\s+with\s+([^.,;:\n]+)", RelationshipType.COMPATIBLE_WITH),
    (r"use\s+with\s+([^.,;:\n]+)", RelationshipType.COMPATIBLE_WITH),
    (r"recommended\s+for\s+([^.,;:\n]+)", RelationshipType.ACCESSORY_FOR),
    (r"also\s+in\s+this\s+series[:\s]+([^.,;:\n]+)", RelationshipType.VARIANT_OF),
    (r"replaces\s+([^.,;:\n]+)", RelationshipType.SUCCESSOR_OF),
    (r"successor\s+to\s+([^.,;:\n]+)", RelationshipType.SUCCESSOR_OF),
]


def _normalize_mention(text: str) -> str:
    """Lowercase, collapse whitespace, strip."""
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _resolve_product_mention(
    mention: str,
    brand_hint: Optional[str],
    graph: ProductGraph,
    exclude_id: Optional[str] = None,
) -> Optional[str]:
    """
    Resolve a product mention (e.g. "Nord Stage 4 88") to a product ID in the graph.
    Prefer same brand. Returns None if no good match.
    """
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
        # Prefer same brand
        score = overlap + (2 if (brand_hint and _normalize_mention(p.brand) == _normalize_mention(brand_hint)) else 0)
        # Prefer longer overlap (full name match)
        if len(name_n) >= len(mention_n) and mention_n in name_n:
            score += 3
        if score > best_score:
            best_score = score
            best_id = candidate_id

    return best_id


def _extract_related_mentions_from_text(text: str) -> List[Tuple[str, RelationshipType]]:
    """Extract (product_mention, relationship_type) from description/spec text."""
    if not text:
        return []
    results: List[Tuple[str, RelationshipType]] = []
    text_lower = text.lower()
    for pattern, rel_type in OFFICIAL_PATTERNS:
        for m in re.finditer(pattern, text_lower, re.IGNORECASE):
            mention = (m.group(1) or "").strip()
            if len(mention) >= 2 and len(mention) <= 200:
                results.append((mention, rel_type))
    return results


def fetch_official_page_html(url: str) -> Optional[str]:
    """Fetch HTML from an official product page. Returns None on failure or invalid URL."""
    if not url or not url.startswith("http"):
        return None
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; HalilitSupport/1.0; +product-relations)"},
            timeout=OFFICIAL_FETCH_TIMEOUT,
            allow_redirects=True,
        )
        if resp.status_code == 200 and resp.text:
            return resp.text
    except Exception as e:
        logger.debug("Official page fetch failed %s: %s", url[:60], e)
    return None


def parse_related_from_html(
    html: str,
    brand: str,
) -> List[Tuple[str, RelationshipType]]:
    """
    Parse brand product page HTML for accessories / related products sections.
    Looks for section headings (Accessories, Related Products, etc.) and extracts
    product names from following links or list items.
    Returns (product_mention, relationship_type).
    """
    results: List[Tuple[str, RelationshipType]] = []
    soup = BeautifulSoup(html, "lxml")
    if soup is None:
        return results

    # Find elements that look like section headings
    for tag in soup.find_all(["h2", "h3", "h4", "strong", "span", "div"], limit=500):
        text = (tag.get_text() or "").strip().lower()
        if len(text) < 3 or len(text) > 120:
            continue
        rel_type = None
        for heading, rtype in RELATED_SECTION_HEADINGS:
            if heading in text:
                rel_type = rtype
                break
        if rel_type is None:
            continue

        # Collect product names from this section: next siblings, or parent's next siblings
        container = tag.find_parent(["section", "div", "aside"]) or tag
        # Look for links that look like product links (often have product name as text)
        for a in (container.find_all("a", href=True) if container else [])[:30]:
            name = (a.get_text() or "").strip()
            name = re.sub(r"\s+", " ", name)
            if 2 <= len(name) <= 150 and name.lower() not in ("learn more", "view all", "see more", "buy", "shop"):
                results.append((name, rel_type))
        # List items under this section
        for li in (container.find_all("li") if container else [])[:30]:
            name = (li.get_text() or "").strip()
            name = re.sub(r"\s+", " ", name)
            if 2 <= len(name) <= 150:
                results.append((name, rel_type))
        # Product cards / tiles (common classes)
        for el in (container.select(".product-name, .product-title, .product__name, [data-product-name]") if container else [])[:30]:
            name = el.get("data-product-name") or (el.get_text() or "").strip()
            name = re.sub(r"\s+", " ", name)
            if 2 <= len(name) <= 150:
                results.append((name, rel_type))

    # JSON-LD: isRelatedTo, relatedProduct
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
            if isinstance(data, dict) and data.get("@type") == "Product":
                for ref in data.get("isRelatedTo", []) or []:
                    if isinstance(ref, dict):
                        name = ref.get("name") or ref.get("title")
                        if name and 2 <= len(str(name)) <= 150:
                            results.append((str(name).strip(), RelationshipType.COMPATIBLE_WITH))
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("@type") == "Product":
                        for ref in item.get("isRelatedTo", []) or []:
                            if isinstance(ref, dict):
                                name = ref.get("name") or ref.get("title")
                                if name and 2 <= len(str(name)) <= 150:
                                    results.append((str(name).strip(), RelationshipType.COMPATIBLE_WITH))
        except Exception:
            pass

    return results


def extract_official_relationship_candidates(graph: ProductGraph) -> List[ProductRelationship]:
    """
    Official brand pages are the first and most influential source. We:
    1. Fetch official_url when present and parse accessories/related sections (confidence 0.92).
    2. Fall back to text in description/specs (confidence 0.85).
    """
    candidates: List[ProductRelationship] = []
    seen_edges_global: set = set()

    def add_candidate(
        source_id: str,
        target_id: str,
        rel_type: RelationshipType,
        mention: str,
        confidence: float,
        note: str,
    ) -> None:
        edge_key = (source_id, target_id, rel_type)
        if edge_key in seen_edges_global:
            return
        seen_edges_global.add(edge_key)
        direction = RelationshipDirection.UNIDIRECTIONAL
        if rel_type in (
            RelationshipType.COMPATIBLE_WITH,
            RelationshipType.VARIANT_OF,
            RelationshipType.ALTERNATIVE_TO,
            RelationshipType.BUNDLE_WITH,
        ):
            direction = RelationshipDirection.BIDIRECTIONAL
        candidates.append(
            ProductRelationship(
                source_id=source_id,
                target_id=target_id,
                relationship_type=rel_type,
                direction=direction,
                confidence=confidence,
                ai_discovered=True,
                discovered_from="official",
                compatibility_notes=note,
                sources_verified=["official"],
            )
        )

    # 1) Fetch official brand pages and parse accessories/related sections (primary source)
    products_with_url = [(pid, p) for pid, p in graph.products.items() if p.official_url]
    fetched = 0
    for idx, (pid, product) in enumerate(products_with_url):
        if fetched >= OFFICIAL_FETCH_MAX_PER_RUN:
            break
        if idx > 0:
            time.sleep(OFFICIAL_FETCH_DELAY_SEC)
        html = fetch_official_page_html(product.official_url)
        if not html:
            continue
        fetched += 1
        mentions = parse_related_from_html(html, product.brand)
        for mention, rel_type in mentions:
            target_id = _resolve_product_mention(mention, product.brand, graph, exclude_id=pid)
            if not target_id:
                continue
            if rel_type == RelationshipType.ACCESSORY_FOR:
                # Section "Accessories" on this product's page = these are accessories FOR this product
                source_id, target_id = target_id, pid
            else:
                source_id, target_id = pid, target_id
            add_candidate(
                source_id,
                target_id,
                rel_type,
                mention,
                confidence=0.92,
                note=f"From official page section: '{mention[:60]}'",
            )

    # 2) Text extraction from description/specs (fallback, still official source)
    for pid, product in graph.products.items():
        text_parts = []
        if product.description:
            text_parts.append(product.description)
        if product.description_short:
            text_parts.append(product.description_short)
        if product.specs and isinstance(product.specs, dict):
            for v in product.specs.values():
                if isinstance(v, str):
                    text_parts.append(v)
        if product.features:
            text_parts.extend(f for f in product.features if isinstance(f, str))
        text = " ".join(text_parts)
        if not text:
            continue

        for mention, rel_type in _extract_related_mentions_from_text(text):
            target_id = _resolve_product_mention(mention, product.brand, graph, exclude_id=pid)
            if not target_id:
                continue
            if rel_type == RelationshipType.ACCESSORY_FOR:
                source_id, target_id = pid, target_id
            else:
                source_id, target_id = pid, target_id
            add_candidate(
                source_id,
                target_id,
                rel_type,
                mention,
                confidence=0.85,
                note=f"From official text: '{mention[:60]}'",
            )

    if candidates:
        logger.info(
            f"Official enrichment: {len(candidates)} candidates (fetched {fetched} brand pages)"
        )
    return candidates
