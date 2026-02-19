"""
Relationship Discovery Engine (High Confidence Edition)
========================================================
1. Variants: Grouped by strict Family ID or Official URL match.
2. Accessories: Linked ONLY if:
    a) Explicitly named in the parent's Official Description/Specs (Confidence 1.0)
    b) Strong "Designed For" name match (Confidence 0.9)
3. Alternatives: Same Spectrum + Same Tier (Confidence 0.5 - purely navigational)

No "Compatible With" guessing. No weak regex links.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Set

from backend.product_graph import (
    ProductGraph,
    ProductFamily,
    ProductRelationship,
    ProductVariant,
    RelationshipType,
    RelationshipDirection,
    CanonicalProduct,
    CONFIDENCE_BY_SOURCE,
)

logger = logging.getLogger("RelationshipDiscovery")

# ═══════════════════════════════════════════════════════════════════════════
# PATTERNS (Strict Helpers)
# ═══════════════════════════════════════════════════════════════════════════

# Suffixes that indicate a Variant (Color/Size)
COLOR_PATTERN = re.compile(
    r'\s*[-–]\s*(Black|White|Red|Blue|Silver|Gold|Gray|Grey|Green|Natural|Sunburst|'
    r'Vintage|Matte|Satin|Gloss|Chrome|Walnut|Cherry|Ebony|Ivory|Maple|Ash|Mahogany|'
    r'Pink|Purple|Orange|Yellow|Tobacco|Burst|Sparkle|Metallic|Transparent|Trans|'
    r'Brown|Cream|Clear|Sand|Light|Dark|Seafoam|Surf|Fiesta|Olympic|Candy|Shell|'
    r'Polar|Midnight|Arctic|Sonic|Daphne|Lake Placid|Sherwood|Pelham|TV Yellow|'
    r'Firemist|Wine|Aged|Relic|Road Worn|Faded)\s*$',
    re.IGNORECASE
)

SIZE_PATTERN = re.compile(
    r'\s*[-–]?\s*(88|73|61|49|37|25|Compact|Stage|Studio|HP|AW|HA|EX|DX|LX|SE|LE|'
    r'Plus|Pro|Standard|Mark\s*\d|MK\s*\d|Gen\s*\d|4-String|5-String|6-String|'
    r'7-String|8-String|Left Hand|Left Handed|Lefty|LH)\s*$',
    re.IGNORECASE
)

# Accessories keywords
ACCESSORY_KEYWORDS = {
    "bag", "case", "cover", "stand", "pedal", "bench", "adapter", "cable",
    "mount", "holder", "clamp", "kit", "pack", "bundle", "footswitch"
}

HEBREW_PATTERN = re.compile(r'[\u0590-\u05FF]')


def _strip_hebrew(text: str) -> str:
    return HEBREW_PATTERN.sub('', text).strip()


def _normalize_model_name(name: str, brand: str) -> str:
    clean = name.strip()
    if brand and clean.lower().startswith(brand.lower()):
        clean = clean[len(brand):].strip()
    clean = _strip_hebrew(clean)
    clean = COLOR_PATTERN.sub('', clean)
    clean = SIZE_PATTERN.sub('', clean)
    return re.sub(r'\s+', ' ', clean).strip().lower()


def _extract_variant_key(name: str, base_model: str, brand: str) -> str:
    clean = name.strip()
    if brand and clean.lower().startswith(brand.lower()):
        clean = clean[len(brand):].strip()
    clean = _strip_hebrew(clean)

    color_match = COLOR_PATTERN.search(clean)
    size_match = SIZE_PATTERN.search(clean)

    parts = []
    if size_match:
        parts.append(size_match.group(1).strip())
    if color_match:
        parts.append(color_match.group(1).strip())

    return " ".join(parts) if parts else (clean.split()[-1] if " " in clean else clean)


def _official_family_key(product: CanonicalProduct) -> Optional[Tuple[str, str]]:
    url = (product.official_url or "").strip()
    if not url or not url.startswith("http"):
        return None
    try:
        path = url.split("?")[0].rstrip("/").split("/")[-1]
        base = COLOR_PATTERN.sub("", path).strip("- ")
        base = SIZE_PATTERN.sub("", base).strip("- ")
        base = re.sub(r"\s+", "-", base).lower().strip("-")
        if len(base) < 2:
            return None
        return ((product.brand or "").lower().replace(" ", "-"), base)
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# VERIFICATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════


def verify_against_official_text(parent: CanonicalProduct, accessory: CanonicalProduct) -> bool:
    """
    CHECK 1: Does Parent's official text explicitly name the Accessory?
    Sources checked: description (official/commercial), specs, features list.
    """
    # Prepare text corpus from parent (description holds merged official/commercial content)
    corpus = (parent.description or "") + " "
    if parent.specs:
        corpus += " " + " ".join(str(v) for v in parent.specs.values())
    if parent.features:
        corpus += " " + " ".join(parent.features)

    corpus = corpus.lower()

    # Check for Accessory Model Number (High Precision)
    # e.g. "KSC-70" inside FP-30X description
    acc_name_parts = _strip_hebrew(accessory.name or "").split()

    # Heuristic: If accessory name is short (e.g. "Bag"), ignore.
    # We need a specific model code (e.g. "SC-88", "CB-B88", "KSC-70")
    relevant_model_codes = [
        w for w in acc_name_parts
        if any(c.isdigit() for c in w) and len(w) > 3
    ]

    for code in relevant_model_codes:
        if code.lower() in corpus:
            return True

    # CHECK 2: Does Accessory's name contain the Parent's exact model name?
    # e.g. Accessory: "Roland KSC-70 Stand for FP-30" -> Parent: "Roland FP-30"
    parent_model = _normalize_model_name(parent.name, parent.brand)
    if len(parent_model) > 3 and parent_model in (accessory.name or "").lower():
        return True

    return False


# ═══════════════════════════════════════════════════════════════════════════
# DISCOVERY CLASS
# ═══════════════════════════════════════════════════════════════════════════


class RelationshipDiscovery:
    def __init__(self, use_ai: bool = False):
        self.use_ai = use_ai

    def discover_all(self, graph: ProductGraph) -> ProductGraph:
        logger.info(f"Starting High-Confidence Discovery for {len(graph.products)} products")

        # 1. Families (Structure)
        graph = self._discover_variant_families(graph)

        # 2. Accessories (Strict Verified Links)
        graph = self._discover_accessories(graph)

        # 3. Alternatives (Navigation Peers)
        graph = self._discover_alternatives(graph)

        graph.rebuild_indexes()
        return graph

    def _discover_variant_families(self, graph: ProductGraph) -> ProductGraph:
        """
        Group products into families.
        Priority 1: Official URL overlap (Confidence 1.0)
        Priority 2: Strict Name Matching (Confidence 0.9)
        """
        orphans = [p for p in graph.products.values() if not p.family_id]
        if not orphans:
            return graph

        # Pass 1: Official URL Grouping
        official_groups: Dict[str, List[CanonicalProduct]] = {}
        for p in orphans:
            key_tuple = _official_family_key(p)
            if key_tuple:
                key_str = f"{key_tuple[0]}::{key_tuple[1]}"
                official_groups.setdefault(key_str, []).append(p)

        families_created = 0
        for key, members in official_groups.items():
            if len(members) < 2:
                continue
            self._create_family(graph, members, "official_url_match", 1.0)
            families_created += 1

        # Pass 2: Name-Based Grouping (Fallback)
        still_orphans = [p for p in orphans if not p.family_id]
        name_groups: Dict[str, List[CanonicalProduct]] = {}
        for p in still_orphans:
            # Skip accessories from being family roots
            if any(k in (p.name or "").lower() for k in ACCESSORY_KEYWORDS):
                continue

            base = _normalize_model_name(p.name, p.brand)
            if len(base) < 3:
                continue
            name_groups.setdefault(f"{p.brand}::{base}", []).append(p)

        for key, members in name_groups.items():
            if len(members) < 2:
                continue
            # Extra check: Variants must share category
            cat = members[0].category
            if not all(m.category == cat for m in members):
                continue

            self._create_family(graph, members, "commercial_name_match", 0.9)
            families_created += 1

        logger.info(f"Family Discovery: Created {families_created} families")
        return graph

    def _create_family(
        self,
        graph: ProductGraph,
        members: List[CanonicalProduct],
        method: str,
        confidence: float,
    ) -> None:
        brand = members[0].brand
        base_name = _normalize_model_name(members[0].name, brand)
        fid = f"fam_{brand.lower().replace(' ', '-')}_{base_name.replace(' ', '-')[:30]}"

        members.sort(key=lambda p: (-(1 if p.image_url else 0), -p.price))
        hero = members[0]

        fam = ProductFamily(
            id=fid,
            brand=brand,
            family_name=f"{brand} {base_name}".title(),
            hero_image=hero.image_url or "",
            variant_ids=[m.id for m in members],
            official_family_url=hero.official_url or "",
        )
        graph.add_family(fam)

        for i, m in enumerate(members):
            m.family_id = fid
            vkey = _extract_variant_key(m.name, base_name, brand)
            m.variant = ProductVariant(variant_key=vkey, is_default=(i == 0))
            graph.products[m.id] = m

        # Link siblings
        for i, a in enumerate(members):
            for b in members[i + 1 :]:
                rel = ProductRelationship(
                    source_id=a.id,
                    target_id=b.id,
                    relationship_type=RelationshipType.VARIANT_OF,
                    direction=RelationshipDirection.BIDIRECTIONAL,
                    confidence=confidence,
                    discovered_from=method,
                    sources_verified=["official"] if confidence == 1.0 else ["commercial"],
                )
                graph.add_relationship(rel)

    def _discover_accessories(self, graph: ProductGraph) -> ProductGraph:
        """
        Find accessories with strict verification.
        ONLY create link if:
        1. Same Brand.
        2. Verified by Official Text OR Strong Name Match.
        """
        accessories = [
            p
            for p in graph.products.values()
            if any(k in (p.name or "").lower() for k in ACCESSORY_KEYWORDS)
        ]
        main_units = [p for p in graph.products.values() if p not in accessories]

        # Index main units by Brand for speed
        by_brand: Dict[str, List[CanonicalProduct]] = {}
        for p in main_units:
            by_brand.setdefault((p.brand or "").lower(), []).append(p)

        count = 0
        for acc in accessories:
            candidates = by_brand.get((acc.brand or "").lower(), [])
            if not candidates:
                continue

            for parent in candidates:
                is_verified = verify_against_official_text(parent, acc)

                if is_verified:
                    rel = ProductRelationship(
                        source_id=acc.id,
                        target_id=parent.id,
                        relationship_type=RelationshipType.ACCESSORY_FOR,
                        direction=RelationshipDirection.UNIDIRECTIONAL,
                        confidence=1.0,
                        discovered_from="official_text_verification",
                        compatibility_notes="Explicitly mentioned in official product text",
                        sources_verified=["official_text_match"],
                    )
                    graph.add_relationship(rel)
                    count += 1

        logger.info(f"Accessory Discovery: Found {count} VERIFIED accessory links")
        return graph

    def _discover_alternatives(self, graph: ProductGraph) -> ProductGraph:
        """
        Alternatives = Navigation Peers.
        Same Spectrum, Same Tier, Different Brand.
        Confidence capped at 0.5 because it's an opinion, not a fact.
        """
        by_spectrum_tier: Dict[str, List[CanonicalProduct]] = {}
        for p in graph.products.values():
            if not p.spectrum_id or not p.tier:
                continue
            key = f"{p.spectrum_id}::{p.tier}"
            by_spectrum_tier.setdefault(key, []).append(p)

        count = 0
        for key, group in by_spectrum_tier.items():
            if len(group) < 2:
                continue

            # Sort by quality, take top 5 representative products per group
            group.sort(key=lambda x: -x.quality_score)
            top_group = group[:5]

            for i, a in enumerate(top_group):
                for b in top_group[i + 1 :]:
                    if a.brand == b.brand:
                        continue  # Skip same brand (that's what families/series are for)

                    rel = ProductRelationship(
                        source_id=a.id,
                        target_id=b.id,
                        relationship_type=RelationshipType.ALTERNATIVE_TO,
                        direction=RelationshipDirection.BIDIRECTIONAL,
                        confidence=0.5,
                        discovered_from="spectrum_peer_logic",
                        compatibility_notes="Similar category and price tier",
                        sources_verified=["spectrum_logic"],
                    )
                    graph.add_relationship(rel)
                    count += 1

        logger.info(f"Alternative Discovery: Created {count} navigation links")
        return graph


_instance: Optional[RelationshipDiscovery] = None


def get_relationship_discovery(use_ai: bool = False) -> RelationshipDiscovery:
    global _instance
    if _instance is None:
        _instance = RelationshipDiscovery(use_ai=use_ai)
    return _instance
