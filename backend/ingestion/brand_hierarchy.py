"""
Brand Hierarchy Engine — Strict Backbone (Fashion Schema)
=========================================================

Enforces manufacturer-defined hierarchy: Brand → Type/Category → Series → Model → Variant.
Runs before relationship_discovery so the graph has a clean foundation.

No fuzzy matching: we extract the manufacturer's logic using known series
definitions and regex for generation/model numbers.
"""

import logging
import re
from typing import Dict, List, Optional

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

logger = logging.getLogger("BrandHierarchy")

# ═══════════════════════════════════════════════════════════════════════════
# KNOWN SERIES (manufacturer product lines) — can be moved to config/DB later
# ═══════════════════════════════════════════════════════════════════════════

KNOWN_SERIES: Dict[str, List[str]] = {
    "Nord": ["Stage", "Electro", "Piano", "Grand", "Lead", "Wave"],
    "Roland": ["Fantom", "Jupiter", "Juno", "RD", "FP", "Go", "LX", "HP", "V-Drums", "TD", "SPD"],
    "Allen & Heath": ["dLive", "Avantis", "SQ", "Qu", "ZED", "Xone", "AHM"],
    "Yamaha": ["Montage", "ModX", "CP", "YC", "P-Series", "P", "DGX", "PSR", "Arius", "Clavinova"],
    "Korg": ["Nautilus", "Kronos", "Krome", "B2", "LP", "SV", "D1", "Liano"],
    "Kawai": ["ES", "MP", "CN", "CA", "Novus", "DG"],
    "Casio": ["Privia", "Celviano", "CDP", "PX", "CT", "CGP"],
    "Kurzweil": ["Forte", "SP", "PC", "Artis"],
    "Dexibell": ["Vivo", "Combo", "Classico"],
    "Studiologic": ["Numa", "SL", "Grand"],
    "Arturia": ["KeyLab", "MicroFreak", "MiniLab", "MatrixBrute"],
    "Moog": ["Sub", "Little Phatty", "Subsequent", "Matriarch", "Grandmother"],
    "Dave Smith": ["Prophet", "OB", "Mopho", "Rev2"],
    "Native Instruments": ["Komplete Kontrol", "Maschine", "Traktor"],
    "Novation": ["Launchkey", "Launchpad", "Bass Station", "Peak", "Summit"],
    "M-Audio": ["Keystation", "Oxygen", "Hammer"],
    "Alesis": ["Recital", "Vortex", "Nitrogen", "Coda"],
    "Nektar": ["Impact", "Panorama", "GX"],
    "ESI": ["Key", "Midi"],
}


def _bucket_by_attribute(
    items: List[CanonicalProduct], attr: str
) -> Dict[str, List[CanonicalProduct]]:
    bucket: Dict[str, List[CanonicalProduct]] = {}
    for item in items:
        key = getattr(item, attr, None) or "Unknown"
        key = (key or "Unknown").strip() or "Unknown"
        bucket.setdefault(key, []).append(item)
    return bucket


def _derive_family_name(full_name: str, series: Optional[str], brand: str) -> str:
    """
    Reduces e.g. 'Nord Stage 4 88-Key Stage Keyboard' -> 'Stage 4'.
    If series is None, use first 2–3 words as a guess.
    """
    if not full_name or not full_name.strip():
        return full_name or "Unknown"
    clean = full_name.strip()
    if brand and clean.lower().startswith(brand.lower()):
        clean = clean[len(brand) :].strip()

    if series:
        # Match "Series + Generation" (e.g. Stage 4, Piano 5, P-145)
        pattern = re.compile(
            rf"({re.escape(series)})\s+([0-9]+|[A-Z]+|mk\s*[IV]+|EX|DX|SE|LE)",
            re.IGNORECASE,
        )
        match = pattern.search(clean)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        # Series only (e.g. "Stage", "Electro")
        if series.lower() in clean.lower():
            return series
    # Fallback: first 2–3 significant words (skip "88", "Keys", etc.)
    words = [w for w in clean.split() if w and not w.isdigit()][:3]
    return " ".join(words) if words else clean


def _extract_variant_label(product: CanonicalProduct, family_name: str) -> str:
    """e.g. '88 Keys', '73 Keys', 'Compact', 'Black'."""
    name = (product.name or "").strip()
    if not name:
        return "Standard"
    name_lower = name.lower()
    if product.brand and name_lower.startswith(product.brand.lower()):
        name = name[len(product.brand) :].strip()
    # Strip family name to leave variant part
    fn_lower = family_name.lower()
    if fn_lower in name_lower:
        name = name_lower.replace(fn_lower, "").strip()
    else:
        # Take last token(s) that look like variant (number, Compact, color)
        parts = name.split()
        for i in range(len(parts) - 1, -1, -1):
            tail = " ".join(parts[i:])
            if any(
                x in tail.lower()
                for x in ("88", "73", "61", "49", "compact", "hp", "black", "white")
            ):
                return tail or "Standard"
        if parts:
            return parts[-1]
    return name.strip() or "Standard"


class BrandHierarchyEngine:
    """
    Enforces strict manufacturer hierarchy: Brand -> Series -> Model -> Variant.
    Call before relationship_discovery so families and variant edges exist first.
    """

    def __init__(self, known_series: Optional[Dict[str, List[str]]] = None):
        self.known_series = known_series or KNOWN_SERIES

    def organize_catalog(self, graph: ProductGraph) -> None:
        """
        Group products by Brand → Category → Series/Model, create ProductFamily
        entries, assign family_id and variant on each product, and add VARIANT_OF
        edges between siblings. Mutates graph in place.
        """
        products = list(graph.products.values())
        if not products:
            return

        # 1) Only process products that don't already have a family (e.g. from overlay)
        orphans = [p for p in products if not p.family_id]
        if not orphans:
            logger.debug("BrandHierarchy: no orphans to group")
            return

        # 2) Group by Brand (root)
        by_brand = _bucket_by_attribute(orphans, "brand")
        families_created = 0
        edges_created = 0

        for brand, brand_products in by_brand.items():
            if brand == "Unknown":
                continue
            # 3) Group by Category/Type (branch) so we don't mix e.g. Yamaha P-45 piano with Yamaha outboard
            by_category = _bucket_by_attribute(brand_products, "category")
            for category, type_products in by_category.items():
                type_families = self._extract_series_families(brand, type_products)
                for family in type_families:
                    if len(family.products) < 1:
                        continue
                    family_id = family.id
                    graph.add_family(
                        ProductFamily(
                            id=family_id,
                            brand=family.brand,
                            family_name=family.family_name,
                            series=family.series,
                            variant_ids=[p.id for p in family.products],
                            accessory_ids=[],
                            description=family.description,
                            hero_image=family.hero_image or "",
                        )
                    )
                    families_created += 1
                    # Assign family_id and variant to each product
                    for i, p in enumerate(family.products):
                        p.family_id = family_id
                        vkey = _extract_variant_label(p, family.family_name)
                        p.variant = ProductVariant(
                            variant_key=vkey or "Standard",
                            is_default=(i == 0),
                            sort_order=i,
                        )
                        graph.products[p.id] = p
                    # VARIANT_OF edges between siblings (confidence from official/commercial)
                    conf = CONFIDENCE_BY_SOURCE.get("official", 1.0)
                    for i, a in enumerate(family.products):
                        for b in family.products[i + 1 :]:
                            rel = ProductRelationship(
                                source_id=a.id,
                                target_id=b.id,
                                relationship_type=RelationshipType.VARIANT_OF,
                                direction=RelationshipDirection.BIDIRECTIONAL,
                                confidence=conf,
                                ai_discovered=False,
                                discovered_from="brand_hierarchy",
                                compatibility_notes=f"Same family: {family.family_name}",
                                sources_verified=["official"],
                            )
                            graph.add_relationship(rel)
                            edges_created += 1

        logger.info(
            f"BrandHierarchy: created {families_created} families, "
            f"{edges_created} VARIANT_OF edges"
        )

    def _extract_series_families(
        self, brand: str, products: List[CanonicalProduct]
    ) -> List[ProductFamily]:
        """
        Group products by Series+Model (e.g. "Nord Stage 4", "Yamaha P-145").
        Returns list of ProductFamily-like objects (we use a simple namespace here).
        """
        families: Dict[str, _FamilyAccum] = {}
        known_series_list = self.known_series.get(brand, [])

        for product in products:
            name = (product.name or "").strip()
            if not name:
                continue
            # Detect series from name
            detected_series: Optional[str] = None
            for series in known_series_list:
                if series.lower() in name.lower():
                    detected_series = series
                    break
            family_name = _derive_family_name(name, detected_series, brand)
            # Normalize key for grouping (e.g. "Stage 4" and "stage 4" same)
            key = f"{brand}::{family_name}".lower()
            if key not in families:
                hero = product
                families[key] = _FamilyAccum(
                    id=f"fam_{brand.lower().replace(' ', '_')}_{family_name.replace(' ', '_')[:40]}",
                    brand=brand,
                    family_name=f"{brand} {family_name}".strip(),
                    series=detected_series or "",
                    products=[],
                    hero_image=hero.image_url or "",
                    description=hero.description_short or hero.description or "",
                )
            acc = families[key]
            acc.products.append(product)

        # Sort each family's products (with image/price first as hero)
        for acc in families.values():
            acc.products.sort(
                key=lambda p: (
                    -(1 if (p.image_url) else 0),
                    -p.quality_score,
                    -(p.price if p.price > 0 else 0),
                )
            )

        return list(families.values())


class _FamilyAccum:
    """Interim container for family data before creating ProductFamily."""

    __slots__ = (
        "id",
        "brand",
        "family_name",
        "series",
        "products",
        "hero_image",
        "description",
    )

    def __init__(
        self,
        id: str,
        brand: str,
        family_name: str,
        series: str,
        products: List[CanonicalProduct],
        hero_image: str = "",
        description: str = "",
    ):
        self.id = id
        self.brand = brand
        self.family_name = family_name
        self.series = series
        self.products = products
        self.hero_image = hero_image
        self.description = description
