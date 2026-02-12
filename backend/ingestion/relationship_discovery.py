"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           RELATIONSHIP DISCOVERY — AI-Powered Product Graph Builder         ║
║                                                                             ║
║  Uses pattern matching + official-page hints + Gemini AI to discover        ║
║  product families, variants, accessories, and compatibility relationships.  ║
║                                                                             ║
║  Discovery pipeline:                                                        ║
║    1. Official-page relationship hints (highest confidence — from source)   ║
║    2. Pattern-based family detection (fast, high confidence)                ║
║    3. Breadcrumb-based hierarchy detection (series/family from nav)         ║
║    4. AI-powered relationship discovery (Gemini, per-brand)                 ║
║    5. Confidence scoring + merge with curated relationships                 ║
║                                                                             ║
║  RULE: Relationships are OFFICIAL_SEED — AI proposes, humans confirm.       ║
║  RULE: NO synthesized relationships — must be evidenced from real data.     ║
║                                                                             ║
║  VERSION: 8.4                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import logging
import os
import re
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

from backend.product_graph import (
    CanonicalProduct,
    ProductFamily,
    ProductGraph,
    ProductRelationship,
    ProductVariant,
    RelationshipDirection,
    RelationshipType,
)

logger = logging.getLogger("RelationshipDiscovery")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: PATTERN-BASED FAMILY DETECTION
# ═══════════════════════════════════════════════════════════════════════════

# Known variant suffixes that indicate size/configuration variants
VARIANT_PATTERNS = [
    # Keyboard sizes
    r"\b(88|73|76|61|49|37|25)\s*(?:keys?|key)?\b",
    # Compact/HP/etc variants
    r"\b(compact|hp|ha|stage|studio|mk\s*\d+|mkii|mkiii)\b",
    # Size variants
    r"\b(mini|micro|nano|xl|xxl)\b",
    # Roman numeral generations embedded in name
    r"\b(ii|iii|iv|v|vi)\b",
]

# Accessory keywords
ACCESSORY_KEYWORDS = {
    "case", "bag", "cover", "stand", "pedal", "adapter", "cable",
    "mount", "bracket", "rack", "sleeve", "gig bag", "soft case",
    "hard case", "flight case", "dust cover", "bench", "stool",
    "sustain pedal", "expression pedal", "footswitch", "power supply",
    "music stand", "keyboard stand", "monitor stand", "mic stand",
}

# Brand-specific product line patterns
BRAND_SERIES_PATTERNS: Dict[str, List[Dict[str, Any]]] = {
    "nord": [
        {"series": "Stage", "pattern": r"nord\s+stage\s*(\d+)"},
        {"series": "Electro", "pattern": r"nord\s+electro\s*(\d+\w*)"},
        {"series": "Piano", "pattern": r"nord\s+piano\s*(\d+)"},
        {"series": "Wave", "pattern": r"nord\s+wave\s*(\d*)"},
        {"series": "Lead", "pattern": r"nord\s+lead\s*(\d*)"},
        {"series": "Drum", "pattern": r"nord\s+drum\s*(\d*)"},
    ],
    "roland": [
        {"series": "Fantom", "pattern": r"(?:roland\s+)?fantom[- ]?(\d*)"},
        {"series": "Jupiter", "pattern": r"(?:roland\s+)?jupiter[- ]?x?m?"},
        {"series": "Juno", "pattern": r"(?:roland\s+)?juno[- ]?(\d*)"},
        {"series": "RD", "pattern": r"(?:roland\s+)?rd[- ]?(\d+)"},
        {"series": "FP", "pattern": r"(?:roland\s+)?fp[- ]?(\d+)"},
        {"series": "TD", "pattern": r"(?:roland\s+)?td[- ]?(\d+)"},
        {"series": "V-Drums", "pattern": r"(?:roland\s+)?v-?drums?"},
    ],
    "moog": [
        {"series": "Subsequent", "pattern": r"subsequent\s+(\d+)"},
        {"series": "Matriarch", "pattern": r"matriarch"},
        {"series": "Grandmother", "pattern": r"grandmother"},
        {"series": "Sub", "pattern": r"moog\s+sub\s*(\d+)"},
    ],
    "arturia": [
        {"series": "KeyLab", "pattern": r"keylab\s*(essential\s*)?(\d+)"},
        {"series": "MiniLab", "pattern": r"minilab\s*(\d*)"},
        {"series": "MiniFuse", "pattern": r"minifuse\s*(\d*)"},
        {"series": "AudioFuse", "pattern": r"audiofuse\s*(\d*)"},
    ],
    "adam audio": [
        {"series": "A", "pattern": r"adam\s+a(\d+)x?"},
        {"series": "T", "pattern": r"adam\s+t(\d+)v?"},
        {"series": "S", "pattern": r"adam\s+s(\d+)v?"},
    ],
    "rode": [
        {"series": "NT", "pattern": r"rode\s+nt(\d+)"},
        {"series": "PodMic", "pattern": r"podmic"},
        {"series": "VideoMic", "pattern": r"videomic"},
    ],
    "shure": [
        {"series": "SM", "pattern": r"shure\s+sm(\d+)"},
        {"series": "Beta", "pattern": r"shure\s+beta\s*(\d+)"},
        {"series": "MV", "pattern": r"shure\s+mv(\d+)"},
    ],
    "focusrite": [
        {"series": "Scarlett", "pattern": r"scarlett\s*(solo|\di\d|\d+)"},
        {"series": "Clarett", "pattern": r"clarett"},
    ],
    "universal audio": [
        {"series": "Apollo Twin", "pattern": r"apollo\s+twin\s*(\w*)"},
        {"series": "Apollo", "pattern": r"apollo\s+(x\d+\w*|solo)"},
        {"series": "Volt", "pattern": r"volt\s*(\d+)"},
    ],
    "presonus": [
        {"series": "StudioLive", "pattern": r"studiolive\s*(\d+\w*)"},
        {"series": "Eris", "pattern": r"eris\s*(e?\d+)"},
        {"series": "FaderPort", "pattern": r"faderport\s*(\d*)"},
        {"series": "AudioBox", "pattern": r"audiobox\s*(\w*)"},
    ],
    "mackie": [
        {"series": "CR", "pattern": r"mackie\s+cr(\d+)"},
        {"series": "MR", "pattern": r"mackie\s+mr(\d+)"},
        {"series": "ProFX", "pattern": r"profx(\d+)"},
        {"series": "SRM", "pattern": r"srm(\d+)"},
        {"series": "Thump", "pattern": r"thump(\d+)"},
    ],
    "rcf": [
        {"series": "ART", "pattern": r"rcf\s+art\s*(\d+\w*)"},
        {"series": "SUB", "pattern": r"rcf\s+sub\s*(\d+\w*)"},
        {"series": "NX", "pattern": r"rcf\s+nx\s*(\d+\w*)"},
        {"series": "HD", "pattern": r"rcf\s+hd\s*(\d+\w*)"},
        {"series": "TT", "pattern": r"rcf\s+tt\s*(\d+\w*)"},
    ],
    "pearl": [
        {"series": "Export", "pattern": r"pearl\s+export\s*(\w*)"},
        {"series": "Masters", "pattern": r"pearl\s+masters?\s*(\w*)"},
        {"series": "Decade", "pattern": r"pearl\s+decade\s*(\w*)"},
        {"series": "Session Studio",
            "pattern": r"pearl\s+session\s+studio\s*(\w*)"},
    ],
    "dynaudio": [
        {"series": "LYD", "pattern": r"dynaudio\s+lyd\s*(\d+)"},
        {"series": "Core", "pattern": r"dynaudio\s+core\s*(\d+)"},
        {"series": "BM", "pattern": r"dynaudio\s+bm(\d+)"},
    ],
    "krk": [
        {"series": "ROKIT", "pattern": r"krk\s+rokit\s*(\d+)"},
        {"series": "Classic", "pattern": r"krk\s+classic\s*(\d+)"},
        {"series": "V Series", "pattern": r"krk\s+v(\d+)"},
    ],
    "allen & heath": [
        {"series": "Xone", "pattern": r"xone[:\s]*(\d+\w*)"},
        {"series": "SQ", "pattern": r"(?:allen\s+&?\s*heath\s+)?sq[- ]?(\d+)"},
        {"series": "dLive", "pattern": r"dlive\s*(\w*)"},
        {"series": "AHM", "pattern": r"ahm[- ]?(\d+)"},
        {"series": "ZED", "pattern": r"zed[- ]?(\d+\w*)"},
    ],
    "boss": [
        {"series": "Katana", "pattern": r"boss\s+katana\s*(\w*)"},
        {"series": "ME", "pattern": r"boss\s+me[- ]?(\d+)"},
        {"series": "GT", "pattern": r"boss\s+gt[- ]?(\d+)"},
        {"series": "RC", "pattern": r"boss\s+rc[- ]?(\d+\w*)"},
    ],
    "esp": [
        {"series": "LTD EC", "pattern": r"ltd\s+ec[- ]?(\d+\w*)"},
        {"series": "LTD MH", "pattern": r"ltd\s+mh[- ]?(\d+\w*)"},
        {"series": "LTD TE", "pattern": r"ltd\s+te[- ]?(\d+\w*)"},
        {"series": "LTD KH", "pattern": r"ltd\s+kh[- ]?(\d+\w*)"},
    ],
    "m-audio": [
        {"series": "Keystation", "pattern": r"keystation\s*(\d+\w*)"},
        {"series": "Oxygen", "pattern": r"oxygen\s*(\d+\w*)"},
        {"series": "BX", "pattern": r"m-?audio\s+bx(\d+)"},
        {"series": "Hammer", "pattern": r"hammer\s*(\d+\w*)"},
    ],
    "teenage engineering": [
        {"series": "OP", "pattern": r"op[- ]?(\d+)"},
        {"series": "TP", "pattern": r"tp[- ]?(\d+)"},
    ],
    "warm audio": [
        {"series": "WA", "pattern": r"wa[- ]?(\d+\w*)"},
    ],
}


def _normalize_name(name: str) -> str:
    """Lowercase and strip extra whitespace."""
    return re.sub(r"\s+", " ", name.lower().strip())


def _extract_base_name(name: str, brand: str) -> str:
    """
    Extract the base product name by removing variant suffixes.
    e.g., "Nord Stage 4 88" → "Nord Stage 4"
    e.g., "Nord Stage 4 73-Key" → "Nord Stage 4"
    e.g., "Nord Stage 4 Compact" → "Nord Stage 4"
    """
    normalized = _normalize_name(name)

    # Strip Hebrew/RTL category prefixes for consistent base extraction
    stripped = re.sub(r"^[\u0590-\u05FF\s]+", "", normalized).strip()
    # Use stripped version if it still contains the brand
    if brand.lower() in stripped:
        normalized = stripped

    # Remove common variant suffixes
    # Remove trailing key counts: "88", "73-key", "73 keys", etc.
    base = re.sub(r"\s+\d{2,3}[-\s]*(?:keys?)?$", "", normalized)
    # Remove "compact", "hp", etc. at end
    base = re.sub(r"\s+(?:compact|hp|ha|studio)$", "", base)
    # Remove trailing parenthetical
    base = re.sub(r"\s*\(.*\)\s*$", "", base)

    return base.strip()


def _extract_variant_key(name: str, base_name: str) -> str:
    """
    Extract the variant identifier from a product name.
    e.g., name="Nord Stage 4 88", base="nord stage 4" → "88-Key"
    e.g., name="Nord Stage 4 Compact", base="nord stage 4" → "Compact"
    Returns a clean, title-cased variant key.
    """
    normalized = _normalize_name(name)
    if not base_name:
        return ""

    # What remains after removing the base name
    remainder = normalized.replace(base_name, "").strip()
    # Clean up leading/trailing dashes and spaces
    remainder = re.sub(r"^[- ]+", "", remainder)
    remainder = re.sub(r"[- ]+$", "", remainder)

    # Strip Hebrew/RTL category prefixes (e.g., "סינתיסייזר", "מוניטור אולפני")
    remainder = re.sub(r"^[\u0590-\u05FF\s]+", "", remainder).strip()

    if not remainder:
        return ""

    # Standard keyboard key counts — only these get the "-Key" suffix
    KEYBOARD_SIZES = {"37", "49", "61", "73", "76", "88"}

    # Check if it's a standard key count
    if remainder in KEYBOARD_SIZES:
        return f"{remainder}-Key"

    # Check for "73-key" format already in remainder
    key_match = re.match(r"^(\d{2,3})[-\s]*keys?$", remainder, re.IGNORECASE)
    if key_match and key_match.group(1) in KEYBOARD_SIZES:
        return f"{key_match.group(1)}-Key"

    # Title case the remainder for display
    return remainder.title()


def _is_accessory(name: str, description: str = "") -> bool:
    """Check if a product NAME suggests it's an accessory.
    Only uses the name — descriptions often mention accessory words in context
    (e.g., 'compatible with stand', 'includes mounting bracket')."""
    text = _normalize_name(name)
    return any(kw in text for kw in ACCESSORY_KEYWORDS)


def _detect_accessory_compatibility(accessory_name: str,
                                    all_products: List[CanonicalProduct]
                                    ) -> List[Tuple[str, float]]:
    """
    Find which products an accessory is compatible with based on name matching.
    Returns list of (product_id, confidence) tuples.
    """
    acc_lower = _normalize_name(accessory_name)
    matches = []

    for product in all_products:
        if _is_accessory(product.name):
            continue  # Skip other accessories

        prod_lower = _normalize_name(product.name)

        # Check if the accessory name contains the product/brand name
        confidence = 0.0

        # Direct product name match in accessory name (strongest signal)
        if prod_lower in acc_lower:
            confidence = 0.85

        # Series name match: look for known series identifiers (>3 chars)
        # e.g., "Stage 4" in "Nord Stage 4 Soft Case"
        if confidence == 0:
            # Extract meaningful phrases (brand + series) from product name
            words = product.name.split()
            # Try 2-word and 3-word series combos (skip single short words)
            for length in [3, 2]:
                for i in range(len(words) - length + 1):
                    phrase = " ".join(words[i:i + length]).lower()
                    if len(phrase) > 5 and phrase in acc_lower:
                        confidence = max(confidence, 0.75)
                        break

        if confidence >= 0.5:
            matches.append((product.id, confidence))

    return sorted(matches, key=lambda x: -x[1])


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: MAIN DISCOVERY ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class RelationshipDiscovery:
    """
    Discovers product families and relationships using pattern matching
    and optional AI enhancement.
    """

    def __init__(self, use_ai: bool = False):
        """
        Args:
            use_ai: Whether to use Gemini AI for enhanced discovery.
                    Defaults to False (pattern-only mode for fast/free operation).
        """
        self.use_ai = use_ai and bool(os.getenv("GEMINI_API_KEY"))

    def discover_all(self, graph: ProductGraph,
                     relationship_hints: Optional[List[Dict[str, Any]]] = None
                     ) -> ProductGraph:
        """
        Run full discovery pipeline on the graph:
        0. Official-page relationship hints (if provided — highest confidence)
        1. Pattern-based family detection
        2. Accessory relationship detection
        3. AI-enhanced discovery (if enabled)

        Args:
            graph: ProductGraph with products loaded
            relationship_hints: Optional list of hint dicts from
                OfficialBrandScraper (each has related_name, hint_type, etc.)

        Returns the mutated graph with families and relationships added.
        """
        products = list(graph.products.values())
        if not products:
            logger.info("No products in graph — skipping discovery")
            return graph

        # Group by brand for per-brand analysis
        by_brand: Dict[str, List[CanonicalProduct]] = defaultdict(list)
        for p in products:
            by_brand[p.brand.lower()].append(p)

        logger.info(
            f"Running relationship discovery on {len(products)} products "
            f"across {len(by_brand)} brands (AI={'ON' if self.use_ai else 'OFF'})"
        )

        total_families = 0
        total_relationships = 0

        # Phase 0: Process official-page relationship hints
        if relationship_hints:
            hint_rels = self._process_relationship_hints(
                relationship_hints, graph)
            for rel in hint_rels:
                graph.add_relationship(rel)
                total_relationships += 1
            logger.info(
                f"  Phase 0: {len(hint_rels)} relationships from official page hints"
            )

        for brand, brand_products in by_brand.items():
            # Phase 1: Discover families
            families = self._discover_brand_families(brand, brand_products)
            for family in families:
                graph.add_family(family)
                # Tag products with family_id and variant info
                for vid in family.variant_ids:
                    if vid in graph.products:
                        graph.products[vid].family_id = family.id
                total_families += 1

            # Phase 2: Discover accessory relationships
            rels = self._discover_brand_accessories(brand, brand_products)
            for rel in rels:
                graph.add_relationship(rel)
                total_relationships += 1

        # Phase 3: AI-enhanced discovery (cross-brand relationships)
        if self.use_ai:
            ai_rels = self._ai_discover_relationships(graph)
            for rel in ai_rels:
                graph.add_relationship(rel)
                total_relationships += 1

        graph.rebuild_indexes()
        logger.info(
            f"Discovery complete: {total_families} families, "
            f"{total_relationships} relationships discovered"
        )
        return graph

    def _discover_brand_families(self, brand: str,
                                 products: List[CanonicalProduct]
                                 ) -> List[ProductFamily]:
        """
        Discover product families within a brand using pattern matching.
        Groups products that share a base name but differ by variant suffix.
        """
        families: List[ProductFamily] = []

        # Strategy 1: Use brand-specific series patterns
        brand_patterns = BRAND_SERIES_PATTERNS.get(brand, [])
        assigned_ids: Set[str] = set()

        for sp in brand_patterns:
            series_members: Dict[str,
                                 List[CanonicalProduct]] = defaultdict(list)

            for product in products:
                if product.id in assigned_ids:
                    continue
                if _is_accessory(product.name, product.description):
                    continue

                match = re.search(sp["pattern"], _normalize_name(product.name),
                                  re.IGNORECASE)
                if match:
                    # Group by series+generation
                    gen = match.group(
                        1) if match.lastindex and match.group(1) else ""
                    group_key = f"{sp['series']}{' ' + gen if gen else ''}"
                    series_members[group_key].append(product)

            for group_key, members in series_members.items():
                if len(members) < 1:
                    continue

                family_id = f"{brand}-{group_key.lower().replace(' ', '-')}"
                # Determine generation
                gen_match = re.search(r"(\d+)", group_key)
                generation = int(gen_match.group(1)) if gen_match else None

                family = ProductFamily(
                    id=family_id,
                    brand=brand.title(),
                    family_name=f"{brand.title()} {group_key}",
                    series=sp["series"],
                    generation=generation,
                    product_line=f"{brand.title()} {sp['series']}",
                    variant_ids=[m.id for m in members],
                    hero_image=members[0].image_url if members else "",
                )
                families.append(family)

                # Assign variant info to each product
                # For brand-specific patterns, use the family name as the base
                # e.g., "Nord Stage 4" → base for extracting "88", "Compact"
                family_base = _normalize_name(family.family_name)

                # Also try generic base extraction and pick the shortest
                base_candidates = [family_base] + [
                    _extract_base_name(m.name, brand) for m in members
                ]
                base_name = min(base_candidates,
                                key=len) if base_candidates else ""

                for i, member in enumerate(members):
                    variant_key = _extract_variant_key(member.name, base_name)
                    member.variant = ProductVariant(
                        variant_key=variant_key or member.name.split()[-1],
                        sort_order=i,
                        is_default=(i == 0),
                    )
                    assigned_ids.add(member.id)

        # Strategy 2: Generic base-name grouping for unassigned products
        unassigned = [p for p in products
                      if p.id not in assigned_ids
                      and not _is_accessory(p.name, p.description)]

        base_groups: Dict[str, List[CanonicalProduct]] = defaultdict(list)
        for product in unassigned:
            base = _extract_base_name(product.name, brand)
            if base and len(base) > 3:
                base_groups[base].append(product)

        for base_name, members in base_groups.items():
            if len(members) < 2:
                continue  # Need at least 2 to form a family

            # Remove brand prefix from base_name to avoid "dynaudio-dynaudio-core"
            # Strip Hebrew prefix first, then brand
            base_for_id = re.sub(
                r"^[\u0590-\u05FF\s]+", "", base_name
            ).strip()
            base_for_id = re.sub(
                r"^" + re.escape(brand) + r"\s*", "", base_for_id
            ).strip()
            # Normalize to slug
            slug = re.sub(r"[^a-z0-9]+", "-", base_for_id or base_name)
            slug = re.sub(r"^-+|-+$", "", slug)
            family_id = f"{brand}-{slug}" if slug else brand
            # Clean up any remaining double hyphens
            family_id = re.sub(r"-{2,}", "-", family_id)
            gen_match = re.search(r"(\d+)", base_name)
            generation = int(gen_match.group(1)) if gen_match else None

            family = ProductFamily(
                id=family_id,
                brand=brand.title(),
                family_name=base_name.title(),
                generation=generation,
                variant_ids=[m.id for m in members],
                hero_image=members[0].image_url if members else "",
            )
            families.append(family)

            for i, member in enumerate(members):
                variant_key = _extract_variant_key(member.name, base_name)
                member.variant = ProductVariant(
                    variant_key=variant_key or str(i + 1),
                    sort_order=i,
                    is_default=(i == 0),
                )

        return families

    def _discover_brand_accessories(self, brand: str,
                                    products: List[CanonicalProduct]
                                    ) -> List[ProductRelationship]:
        """
        Find which products are accessories and what they're compatible with.
        """
        relationships: List[ProductRelationship] = []
        non_accessories = [p for p in products
                           if not _is_accessory(p.name, p.description)]

        for product in products:
            if not _is_accessory(product.name, product.description):
                continue

            # Find what this accessory is for
            matches = _detect_accessory_compatibility(
                product.name, non_accessories)

            # Max 5 matches per accessory
            for target_id, confidence in matches[:5]:
                rel = ProductRelationship(
                    source_id=product.id,
                    target_id=target_id,
                    relationship_type=RelationshipType.ACCESSORY_FOR,
                    direction=RelationshipDirection.UNIDIRECTIONAL,
                    confidence=confidence,
                    ai_discovered=True,
                    compatibility_notes=f"Pattern-matched from product name: {product.name}",
                    discovered_from="pattern_matching",
                )
                relationships.append(rel)

        return relationships

    def _ai_discover_relationships(self, graph: ProductGraph
                                   ) -> List[ProductRelationship]:
        """
        Use Gemini AI to discover relationships that pattern matching missed.
        Runs per-brand batch analysis.
        """
        if not self.use_ai:
            return []

        relationships: List[ProductRelationship] = []

        try:
            from google import genai

            client = genai.Client()

            # Group unrelated products by brand for AI analysis
            by_brand: Dict[str, List[CanonicalProduct]] = defaultdict(list)
            for p in graph.products.values():
                if not p.family_id:  # Only analyze products not already in families
                    by_brand[p.brand.lower()].append(p)

            for brand, products in by_brand.items():
                if len(products) < 2:
                    continue

                product_list = "\n".join([
                    f"- ID: {p.id}, Name: {p.name}, Category: {p.category}"
                    for p in products[:50]  # Cap at 50 per brand
                ])

                prompt = f"""Analyze these products from {brand.title()} and identify relationships.

Products:
{product_list}

For each relationship found, return a JSON array of objects with:
- "source_id": product ID of source
- "target_id": product ID of target
- "type": one of "variant_of", "accessory_for", "compatible_with", "successor_of", "alternative_to"
- "confidence": float 0.0-1.0
- "notes": why these are related

Rules:
- Only identify relationships you are CONFIDENT about from the product names
- Do NOT guess or synthesize — if unsure, skip it
- Accessories should point FROM the accessory TO the main product
- Variants share the same base product (different sizes/configs)

Return ONLY the JSON array, no markdown or explanation."""

                try:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt,
                        config={
                            "response_mime_type": "application/json",
                            "temperature": 0.1,
                        },
                    )

                    import json
                    results = json.loads(response.text)
                    if not isinstance(results, list):
                        continue

                    for item in results:
                        try:
                            rel_type = RelationshipType(item.get("type", ""))
                            rel = ProductRelationship(
                                source_id=item["source_id"],
                                target_id=item["target_id"],
                                relationship_type=rel_type,
                                confidence=min(
                                    float(item.get("confidence", 0.5)), 0.85),
                                ai_discovered=True,
                                compatibility_notes=item.get("notes", ""),
                                discovered_from="gemini_ai",
                            )
                            # Only keep if both products exist
                            if (rel.source_id in graph.products
                                    and rel.target_id in graph.products):
                                relationships.append(rel)
                        except (ValueError, KeyError) as e:
                            logger.debug(
                                f"Skipping invalid AI relationship: {e}")

                except Exception as e:
                    logger.warning(f"AI discovery failed for {brand}: {e}")

        except ImportError:
            logger.info("google-genai not installed — skipping AI discovery")

        logger.info(
            f"AI discovered {len(relationships)} additional relationships")
        return relationships

    def _process_relationship_hints(
        self,
        hints: List[Dict[str, Any]],
        graph: ProductGraph,
    ) -> List[ProductRelationship]:
        """
        Convert official-page relationship hints into ProductRelationships.

        Matches hint product names against graph products using fuzzy matching.
        Only creates relationships where both source and target exist in the graph.
        """
        relationships: List[ProductRelationship] = []
        products_by_name: Dict[str, str] = {}  # normalized_name → product_id

        # Build a name→id lookup for matching
        for p in graph.products.values():
            key = _normalize_name(p.name)
            products_by_name[key] = p.id
            # Also index by model name (without brand prefix / Hebrew)
            english = re.sub(r"^[\u0590-\u05FF\s]+", "", p.name).strip()
            if english:
                products_by_name[_normalize_name(english)] = p.id

        hint_type_to_rel = {
            "accessory": RelationshipType.ACCESSORY_FOR,
            "compatible": RelationshipType.COMPATIBLE_WITH,
            "series": RelationshipType.VARIANT_OF,
            "related": RelationshipType.COMPATIBLE_WITH,
        }

        for hint in hints:
            related_name = hint.get("related_name", "")
            if not related_name:
                continue

            hint_type = hint.get("hint_type", "related")
            confidence = float(hint.get("confidence", 0.75))

            # Try to match the related product name to a product in the graph
            target_id = self._fuzzy_match_product(
                related_name, products_by_name)
            if not target_id:
                continue

            rel_type = hint_type_to_rel.get(
                hint_type, RelationshipType.COMPATIBLE_WITH)

            # We don't know the source product from the hint alone,
            # but the hint was extracted from a specific product's page.
            # The caller should set source_product_id on hints.
            source_id = hint.get("source_product_id", "")
            if not source_id or source_id not in graph.products:
                continue
            if source_id == target_id:
                continue

            rel = ProductRelationship(
                source_id=source_id,
                target_id=target_id,
                relationship_type=rel_type,
                confidence=confidence,
                ai_discovered=False,
                compatibility_notes=(
                    f"Discovered from official brand page: {hint.get('related_url', '')}"
                ),
                discovered_from="official_page_hint",
            )
            relationships.append(rel)

        return relationships

    def _fuzzy_match_product(
        self,
        name: str,
        products_by_name: Dict[str, str],
    ) -> Optional[str]:
        """
        Match a product name from a hint to a product in the graph.
        Tries exact match first, then progressively looser matching.
        """
        normalized = _normalize_name(name)

        # Exact match
        if normalized in products_by_name:
            return products_by_name[normalized]

        # Check if any product name contains this name or vice versa
        for key, pid in products_by_name.items():
            if normalized in key or key in normalized:
                return pid

        # Word overlap matching — require 60%+ overlap
        name_words = set(normalized.split())
        if len(name_words) < 2:
            return None

        best_match = None
        best_overlap = 0.0
        for key, pid in products_by_name.items():
            key_words = set(key.split())
            if not key_words:
                continue
            overlap = len(name_words & key_words) / \
                max(len(name_words), len(key_words))
            if overlap > best_overlap and overlap >= 0.6:
                best_overlap = overlap
                best_match = pid

        return best_match


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON & CONVENIENCE
# ═══════════════════════════════════════════════════════════════════════════

_discovery_instance: Optional[RelationshipDiscovery] = None


def get_relationship_discovery(use_ai: bool = False) -> RelationshipDiscovery:
    """Get the singleton RelationshipDiscovery instance."""
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = RelationshipDiscovery(use_ai=use_ai)
    return _discovery_instance


def discover_product_graph(flat_products: List[Dict[str, Any]],
                           use_ai: bool = False,
                           relationship_hints: Optional[List[Dict[str, Any]]] = None
                           ) -> ProductGraph:
    """
    Convenience function: take flat products from build_catalog(),
    run discovery, return enriched graph.

    Args:
        flat_products: Product dicts from the catalog
        use_ai: Whether to use Gemini AI for enhanced discovery
        relationship_hints: Optional hints from official page scraping
    """
    graph = ProductGraph.from_flat_products(flat_products)
    discovery = get_relationship_discovery(use_ai=use_ai)
    graph = discovery.discover_all(
        graph, relationship_hints=relationship_hints)
    return graph
