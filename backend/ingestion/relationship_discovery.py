"""
Relationship Discovery Engine
==============================

Pattern-based discovery of product relationships:
  - Variants: same brand + base model, different color/size/config
  - Accessories: bags, cases, stands, strings, cables for instruments
  - Compatible: same brand products that work together
  - Alternatives: similar products from different brands in same spectrum

No AI required — pure heuristic matching on product names, categories, and specs.
"""

import logging
import re
import unicodedata
from typing import Dict, List, Optional, Set, Tuple

from backend.product_graph import (
    ProductGraph,
    ProductFamily,
    ProductRelationship,
    ProductVariant,
    RelationshipType,
    RelationshipDirection,
    CanonicalProduct,
)

logger = logging.getLogger("RelationshipDiscovery")

# ═══════════════════════════════════════════════════════════════════════════
# PATTERNS
# ═══════════════════════════════════════════════════════════════════════════

# Color/finish suffixes that indicate variants
COLOR_PATTERN = re.compile(
    r'\s*[-–]\s*'
    r'(Black|White|Red|Blue|Silver|Gold|Gray|Grey|Green|Natural|Sunburst|'
    r'Vintage|Matte|Satin|Gloss|Chrome|Walnut|Cherry|Ebony|Ivory|Maple|'
    r'Ash|Mahogany|Pink|Purple|Orange|Yellow|Tobacco|Burst|Sparkle|'
    r'Metallic|Transparent|Trans|Brown|Cream|Clear|Sand|Light|Dark|'
    r'Seafoam|Surf|Fiesta|Olympic|Candy|Shell|Polar|Midnight|'
    r'Arctic|Sonic|Daphne|Lake Placid|Sherwood|Pelham|TV Yellow|'
    r'Firemist|Wine|Aged|Relic|Road Worn|Faded)\s*$',
    re.IGNORECASE
)

# Size/config suffixes for keyboard/piano variants
SIZE_PATTERN = re.compile(
    r'\s*[-–]?\s*'
    r'(88|73|61|49|37|25|Compact|Stage|Studio|'
    r'HP|AW|HA|EX|DX|LX|SE|LE|Plus|Pro|Standard|'
    r'Mark\s*\d|MK\s*\d|MK\s*I+V?|Gen\s*\d|'
    r'4-String|5-String|6-String|7-String|8-String|'
    r'Left Hand|Left Handed|Lefty|LH)\s*$',
    re.IGNORECASE
)

# Accessory indicators
ACCESSORY_PATTERNS = re.compile(
    r'\b(bag|gig bag|case|hardcase|hard case|soft case|cover|strap|'
    r'string|strings|pick|picks|plectrum|stand|mount|bracket|clamp|'
    r'adapter|cable|cord|lead|tuner|capo|pedal|footswitch|foot switch|'
    r'power supply|charger|battery|replacement|spare|pad set|head set|'
    r'mute|dampener|polish|cleaner|wax|oil|lube|cloth|toolkit|wrench|'
    r'key|allen|screw|bolt|felt|washer|sleeve|bushing|grommet|wing nut|'
    r'cymbal felt|hi hat clutch|drum key|practice pad|dust cover|'
    r'music stand|sheet music|book|method|tutorial|lesson|'
    r'headphones|earbuds|ear tips|ear pads|'
    r'mic clip|mic stand|pop filter|windscreen|shock mount)\b',
    re.IGNORECASE
)

# Hebrew character detection
HEBREW_PATTERN = re.compile(r'[\u0590-\u05FF]')


def _strip_hebrew(text: str) -> str:
    """Remove Hebrew characters and clean up."""
    return HEBREW_PATTERN.sub('', text).strip()


def _normalize_model_name(name: str, brand: str) -> str:
    """
    Normalize a product name to a base model identifier.
    Strips brand prefix, Hebrew, color/size suffixes.
    """
    clean = name.strip()
    # Strip brand prefix
    if brand and clean.lower().startswith(brand.lower()):
        clean = clean[len(brand):].strip()
    # Strip Hebrew
    clean = _strip_hebrew(clean)
    # Strip color suffix
    clean = COLOR_PATTERN.sub('', clean)
    # Strip size suffix
    clean = SIZE_PATTERN.sub('', clean)
    # Normalize whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean.lower()


def _extract_variant_key(name: str, base_model: str, brand: str) -> str:
    """Extract what makes this variant different from the base model."""
    clean = name.strip()
    if brand and clean.lower().startswith(brand.lower()):
        clean = clean[len(brand):].strip()
    clean = _strip_hebrew(clean)
    
    # Find the color/size suffix
    color_match = COLOR_PATTERN.search(clean)
    size_match = SIZE_PATTERN.search(clean)
    
    parts = []
    if size_match:
        parts.append(size_match.group(1).strip())
    if color_match:
        parts.append(color_match.group(1).strip())
    
    if parts:
        return " ".join(parts)
    
    # Fallback: last meaningful word
    words = clean.split()
    if len(words) > 1:
        return words[-1]
    return clean


def _is_accessory(product: CanonicalProduct) -> bool:
    """Check if a product is an accessory."""
    name_lower = (product.name or "").lower()
    return bool(ACCESSORY_PATTERNS.search(name_lower))


def _same_spectrum(a: CanonicalProduct, b: CanonicalProduct) -> bool:
    """Check if two products are in the same spectrum."""
    return a.spectrum_id == b.spectrum_id and a.spectrum_id != ""


def _price_similar(a: CanonicalProduct, b: CanonicalProduct, 
                   tolerance: float = 0.5) -> bool:
    """Check if prices are within tolerance ratio of each other."""
    pa = a.price if a.price > 0 else 0
    pb = b.price if b.price > 0 else 0
    if pa == 0 or pb == 0:
        return True  # Can't compare, assume possible
    ratio = min(pa, pb) / max(pa, pb)
    return ratio >= (1 - tolerance)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN DISCOVERY ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class RelationshipDiscovery:
    """
    Discovers product relationships using pattern matching.
    No AI calls — pure heuristic matching.
    """

    def __init__(self, use_ai: bool = False):
        self.use_ai = use_ai  # Reserved for future AI-assisted discovery

    def discover_all(self, graph: ProductGraph) -> ProductGraph:
        """Run all discovery passes on the graph."""
        logger.info(f"Starting relationship discovery for {len(graph.products)} products")
        
        # Pass 1: Discover variant families
        graph = self._discover_variant_families(graph)
        
        # Pass 2: Discover accessory relationships
        graph = self._discover_accessories(graph)
        
        # Pass 3: Discover alternatives (same spectrum, different brand, similar price)
        graph = self._discover_alternatives(graph)
        
        # Rebuild indexes after all mutations
        graph.rebuild_indexes()
        
        stats = graph.get_graph_stats()
        logger.info(
            f"Discovery complete: {stats['total_families']} families, "
            f"{stats['total_relationships']} relationships, "
            f"{stats['products_in_families']} products in families"
        )
        
        return graph

    def discover_commercial(self, graph: ProductGraph) -> ProductGraph:
        """
        Phase 2 in relationship priority: commercial (catalog/Halilit data).
        Variant families + accessory links from same brand. Sources tagged "commercial".
        """
        logger.info("Relationship discovery (commercial): variants + accessories")
        graph = self._discover_variant_families(graph)
        graph = self._discover_accessories(graph)
        graph.rebuild_indexes()
        return graph

    def discover_spectrum_relations(self, graph: ProductGraph) -> ProductGraph:
        """
        Phase 4 in relationship priority: spectrum module relations.
        Alternatives (same spectrum, tier, cross-brand). Sources tagged "spectrum".
        """
        logger.info("Relationship discovery (spectrum): alternatives by spectrum/tier")
        graph = self._discover_alternatives(graph)
        graph.rebuild_indexes()
        return graph

    def _discover_variant_families(self, graph: ProductGraph) -> ProductGraph:
        """
        Group products into families based on base model name matching.
        Products with same brand + base model name → same family.
        """
        # Skip products already in families
        orphans = [p for p in graph.products.values() if not p.family_id]
        if not orphans:
            return graph

        # Group by brand + normalized model name
        model_groups: Dict[str, List[CanonicalProduct]] = {}
        for p in orphans:
            if _is_accessory(p):
                continue
            base = _normalize_model_name(p.name, p.brand)
            if not base or len(base) < 3:
                continue
            key = f"{p.brand.lower()}::{base}"
            model_groups.setdefault(key, []).append(p)

        families_created = 0
        for key, members in model_groups.items():
            if len(members) < 2:
                continue

            # Create a family
            brand = members[0].brand
            base_name = _normalize_model_name(members[0].name, brand)
            family_id = f"fam_{brand.lower().replace(' ', '-')}_{base_name.replace(' ', '-')[:40]}"

            # Find the best representative (has image, highest quality)
            members.sort(key=lambda p: (
                -(1 if p.image_url else 0),
                -p.quality_score,
                -(p.price if p.price > 0 else 0),
            ))
            hero = members[0]

            family = ProductFamily(
                id=family_id,
                brand=brand,
                family_name=f"{brand} {base_name}".title(),
                series=_detect_series(hero.name, brand),
                hero_image=hero.image_url,
                variant_ids=[m.id for m in members],
                accessory_ids=[],
                description=hero.description_short or hero.description,
            )
            graph.add_family(family)

            # Update products with family info
            for i, m in enumerate(members):
                m.family_id = family_id
                vkey = _extract_variant_key(m.name, base_name, brand)
                m.variant = ProductVariant(
                    variant_key=vkey,
                    is_default=(i == 0),
                    sort_order=i,
                )
                graph.products[m.id] = m

            families_created += 1

        logger.info(f"Variant discovery: created {families_created} new families")
        return graph

    def _discover_accessories(self, graph: ProductGraph) -> ProductGraph:
        """
        Find accessory relationships.
        An accessory is linked to products from the same brand that it could serve.
        """
        accessories = [p for p in graph.products.values() if _is_accessory(p)]
        non_accessories = [p for p in graph.products.values() if not _is_accessory(p)]

        relationships_created = 0
        for acc in accessories:
            acc_name = acc.name.lower()
            acc_brand = acc.brand.lower()

            # Find products from the same brand that this could be an accessory for
            for product in non_accessories:
                if product.brand.lower() != acc_brand:
                    continue
                if not _same_spectrum(acc, product):
                    # Accessories might be in a different spectrum (e.g., "accessories" vs "guitars")
                    # Check if the accessory name mentions the product's spectrum
                    pass  # Allow cross-spectrum accessories within same brand

                # Check if the accessory name references the product or its series
                product_words = set(product.name.lower().split())
                acc_words = set(acc_name.split())
                
                # Must share at least one significant word beyond brand
                shared = product_words & acc_words - {acc_brand}
                if len(shared) >= 1:
                    rel = ProductRelationship(
                        source_id=acc.id,
                        target_id=product.id,
                        relationship_type=RelationshipType.ACCESSORY_FOR,
                        direction=RelationshipDirection.UNIDIRECTIONAL,
                        confidence=0.6,
                        ai_discovered=False,
                        discovered_from="commercial_catalog",
                        compatibility_notes=f"Name overlap: {', '.join(shared)}",
                        sources_verified=["commercial"],
                    )
                    graph.add_relationship(rel)
                    relationships_created += 1

        logger.info(f"Accessory discovery: created {relationships_created} relationships")
        return graph

    def _discover_alternatives(self, graph: ProductGraph) -> ProductGraph:
        """
        Find alternative products: same spectrum, different brand, similar tier.
        Only connect products that are clearly comparable.
        """
        # Group products by spectrum
        by_spectrum: Dict[str, List[CanonicalProduct]] = {}
        for p in graph.products.values():
            if _is_accessory(p) or not p.spectrum_id:
                continue
            by_spectrum.setdefault(p.spectrum_id, []).append(p)

        relationships_created = 0
        for spectrum_id, products in by_spectrum.items():
            if len(products) < 2:
                continue

            # Group by tier within the spectrum
            by_tier: Dict[str, List[CanonicalProduct]] = {}
            for p in products:
                by_tier.setdefault(p.tier, []).append(p)

            for tier, tier_products in by_tier.items():
                if len(tier_products) < 2:
                    continue

                # Find cross-brand pairs with similar prices
                brands_seen: Dict[str, List[CanonicalProduct]] = {}
                for p in tier_products:
                    brands_seen.setdefault(p.brand, []).append(p)

                brand_list = list(brands_seen.keys())
                for i in range(len(brand_list)):
                    for j in range(i + 1, len(brand_list)):
                        brand_a = brand_list[i]
                        brand_b = brand_list[j]
                        # Connect the best product from each brand as alternatives
                        products_a = sorted(brands_seen[brand_a], 
                                          key=lambda p: -p.quality_score)[:2]
                        products_b = sorted(brands_seen[brand_b],
                                          key=lambda p: -p.quality_score)[:2]

                        for pa in products_a:
                            for pb in products_b:
                                if _price_similar(pa, pb, tolerance=0.6):
                                    rel = ProductRelationship(
                                        source_id=pa.id,
                                        target_id=pb.id,
                                        relationship_type=RelationshipType.ALTERNATIVE_TO,
                                        direction=RelationshipDirection.BIDIRECTIONAL,
                                        confidence=0.5,
                                        ai_discovered=False,
                                        discovered_from="spectrum_tier_matching",
                                        compatibility_notes=f"Same spectrum ({spectrum_id}), same tier ({tier})",
                                        sources_verified=["spectrum"],
                                    )
                                    graph.add_relationship(rel)
                                    relationships_created += 1

        logger.info(f"Alternative discovery: created {relationships_created} relationships")
        return graph


def _detect_series(name: str, brand: str) -> str:
    """Detect product series from name."""
    clean = name.strip()
    if brand and clean.lower().startswith(brand.lower()):
        clean = clean[len(brand):].strip()
    clean = _strip_hebrew(clean)
    # Match first series identifier: 2+ uppercase alphanumeric characters
    match = re.match(r'^([A-Z][A-Z0-9\-]{1,12})', clean)
    if match and len(match.group(1)) >= 2:
        return match.group(1)
    return ""


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════

_instance: Optional[RelationshipDiscovery] = None


def get_relationship_discovery(use_ai: bool = False) -> RelationshipDiscovery:
    """Get or create the singleton RelationshipDiscovery instance."""
    global _instance
    if _instance is None:
        _instance = RelationshipDiscovery(use_ai=use_ai)
    return _instance
