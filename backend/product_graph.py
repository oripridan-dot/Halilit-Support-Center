"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              CANONICAL PRODUCT GRAPH — Single Source of Truth               ║
║                                                                             ║
║  This module defines the Canonical Product Graph (CPG), replacing the       ║
║  dual-normalization paths (unified_data_service.py's nested shape and       ║
║  product_normalizer.py's flat shape) with ONE canonical model.              ║
║                                                                             ║
║  Products are no longer isolated atoms — they form a graph of families,     ║
║  variants, accessories, and compatibility relationships.                    ║
║                                                                             ║
║  VERSION: 1.0                                                               ║
║  DEPENDS ON: source_rules.py — Three Source Rules remain THE LAW            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

logger = logging.getLogger("ProductGraph")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: RELATIONSHIP TYPES
# ═══════════════════════════════════════════════════════════════════════════

class RelationshipType(str, Enum):
    """Types of relationships between products in the graph."""
    VARIANT_OF = "variant_of"           # Same product, different size/config (Stage 4 88 vs 73)
    # Designed for a specific product (Soft Case for Stage 4)
    ACCESSORY_FOR = "accessory_for"
    # Works with but not exclusive (generic stand)
    COMPATIBLE_WITH = "compatible_with"
    SUCCESSOR_OF = "successor_of"       # Next generation (Stage 4 → Stage 3)
    BUNDLE_WITH = "bundle_with"         # Sold together as a kit
    ALTERNATIVE_TO = "alternative_to"   # Competing product in same category


class RelationshipDirection(str, Enum):
    """Whether a relationship is one-way or bidirectional."""
    UNIDIRECTIONAL = "unidirectional"   # A → B only (accessory → product)
    BIDIRECTIONAL = "bidirectional"     # A ↔ B (variants, alternatives)


# Default directionality per relationship type
RELATIONSHIP_DEFAULTS: Dict[RelationshipType, RelationshipDirection] = {
    RelationshipType.VARIANT_OF: RelationshipDirection.BIDIRECTIONAL,
    RelationshipType.ACCESSORY_FOR: RelationshipDirection.UNIDIRECTIONAL,
    RelationshipType.COMPATIBLE_WITH: RelationshipDirection.BIDIRECTIONAL,
    RelationshipType.SUCCESSOR_OF: RelationshipDirection.UNIDIRECTIONAL,
    RelationshipType.BUNDLE_WITH: RelationshipDirection.BIDIRECTIONAL,
    RelationshipType.ALTERNATIVE_TO: RelationshipDirection.BIDIRECTIONAL,
}


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: RELATIONSHIP MODEL
# ═══════════════════════════════════════════════════════════════════════════

class ProductRelationship(BaseModel):
    """
    An edge in the product graph connecting two products.

    Multi-parent capable: one accessory can have ACCESSORY_FOR edges
    to multiple products (e.g., a case that fits Stage 4 88 AND Piano 5).
    """
    source_id: str = Field(description="Product ID of the source node")
    target_id: str = Field(description="Product ID of the target node")
    relationship_type: RelationshipType
    direction: RelationshipDirection = RelationshipDirection.UNIDIRECTIONAL

    # Confidence & provenance
    confidence: float = Field(default=0.0, ge=0.0, le=1.0,
                              description="How confident the system is in this relationship")
    ai_discovered: bool = Field(default=True,
                                description="True if AI proposed this relationship")
    manually_curated: bool = Field(default=False,
                                   description="True if a human confirmed/created this")

    # Context
    compatibility_notes: str = Field(default="",
                                     description="Why these products are related")
    discovered_from: str = Field(default="",
                                 description="Which source/page revealed this relationship")
    # Triple-check: which sources verified this relationship (commercial, official, contextual, pattern/heuristic)
    sources_verified: List[str] = Field(default_factory=list,
                                       description="Sources that support this edge for cross-validation")

    # Timestamps
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def is_triple_checked(self) -> bool:
        """True when at least two sources have verified this relationship."""
        return len(self.sources_verified) >= 2

    @property
    def is_confirmed(self) -> bool:
        """A relationship is confirmed if manually curated OR high-confidence AI."""
        return self.manually_curated or self.confidence >= 0.9

    @property
    def needs_review(self) -> bool:
        """Between 0.5 and 0.9 confidence and not yet curated."""
        return not self.manually_curated and 0.5 <= self.confidence < 0.9


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: PRODUCT VARIANT
# ═══════════════════════════════════════════════════════════════════════════

class ProductVariant(BaseModel):
    """
    Describes how a product differs from its family siblings.

    Example: Nord Stage 4 "88" → variant_key="88", differentiator="88 weighted keys"
    """
    variant_key: str = Field(
        description="Short key: '88', '73', 'Compact', 'HP'")
    differentiator: str = Field(default="",
                                description="Human-readable difference description")
    sort_order: int = Field(default=0,
                            description="Display order within the family (0 = default)")
    is_default: bool = Field(default=False,
                             description="True if this is the 'main' variant")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: PRODUCT FAMILY
# ═══════════════════════════════════════════════════════════════════════════

class ProductFamily(BaseModel):
    """
    A group of related product variants sharing a common identity.

    Example: "Nord Stage 4" family contains Stage 4 88, Stage 4 73, Stage 4 Compact.
    Families can also have associated accessories.
    """
    id: str = Field(description="Unique family ID, e.g., 'nord-stage-4'")
    brand: str
    family_name: str = Field(description="Display name: 'Nord Stage 4'")
    series: str = Field(default="",
                        description="Product line: 'Stage'")
    generation: Optional[int] = Field(default=None,
                                      description="Generation number: 4")
    product_line: str = Field(default="",
                              description="Full line name: 'Nord Stage'")

    # Member tracking
    variant_ids: List[str] = Field(default_factory=list,
                                   description="Product IDs of variants in this family")
    accessory_ids: List[str] = Field(default_factory=list,
                                     description="Product IDs of accessories for this family")

    # Metadata
    official_family_url: str = Field(default="",
                                     description="URL to the brand's family/series page")
    description: str = Field(default="",
                             description="Family-level description")
    hero_image: str = Field(default="",
                            description="Representative image for the family")

    # Timestamps
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def variant_count(self) -> int:
        return len(self.variant_ids)

    @property
    def has_accessories(self) -> bool:
        return len(self.accessory_ids) > 0


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: CANONICAL PRODUCT
# ═══════════════════════════════════════════════════════════════════════════

class CanonicalProduct(BaseModel):
    """
    The single source of truth for a product's data.

    Replaces both:
    - unified_data_service.DataNormalizer's nested shape (pipeline-internal)
    - product_normalizer.normalize_product()'s flat shape (frontend-facing)

    Maintains full Three Source Rules compliance.
    """

    # ── Identity (Commercial Scout — immutable) ──
    id: str
    name: str
    brand: str
    brand_logo: str = ""
    sku: str = ""
    halilit_url: str = ""

    # ── Classification ──
    galaxy_id: str = ""
    spectrum_id: str = ""
    category: str = ""
    subcategory: str = ""

    # ── Pricing (Commercial Scout only) ──
    price: float = 0.0
    price_eilat: float = 0.0
    currency: str = "ILS"
    tier: str = "mid"

    # ── Media (Official Scout) ──
    image_url: str = ""
    image_gallery: List[str] = Field(default_factory=list)

    # ── Content (Official Scout) ──
    description: str = ""
    description_short: str = ""
    official_url: str = ""
    specs: Dict[str, Any] = Field(default_factory=dict)
    features: List[str] = Field(default_factory=list)
    faq: List[Dict[str, str]] = Field(default_factory=list)
    audiences: List[str] = Field(default_factory=list)

    # ── Reviews (Contextual Scout — 3+ sources) ──
    rating: float = 0.0
    review_count: int = 0
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    contextual_data: Dict[str, Any] = Field(default_factory=dict)

    # ── Data Quality ──
    quality_score: float = 0.0
    data_status: str = "MINIMAL"
    data_missing: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    data_trust: Dict[str, str] = Field(default_factory=lambda: {
        "price_source": "none",
        "specs_source": "none",
        "description_source": "none",
        "image_source": "none",
        "review_source": "none",
    })

    # ── Search (pre-computed) ──
    search_text: str = ""

    # ════════════════════════════════════════════════════════════════
    # NEW: Product Graph Fields — Family & Relationship Awareness
    # ════════════════════════════════════════════════════════════════

    family_id: Optional[str] = Field(default=None,
                                     description="ID of the ProductFamily this belongs to")
    variant: Optional[ProductVariant] = Field(default=None,
                                              description="Variant info if part of a family")
    relationship_ids: List[str] = Field(default_factory=list,
                                        description="IDs of related products (quick lookup)")

    def to_flat(self) -> Dict[str, Any]:
        """
        Convert to the flat ConductorProduct shape for backward-compatible
        frontend serving. Adds family/variant fields as additive extensions.
        """
        flat = {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "brand_logo": self.brand_logo,
            "galaxy_id": self.galaxy_id,
            "spectrum_id": self.spectrum_id,
            "category": self.category,
            "subcategory": self.subcategory,
            "price": self.price,
            "price_eilat": self.price_eilat,
            "currency": self.currency,
            "tier": self.tier,
            "image_url": self.image_url,
            "image_gallery": self.image_gallery,
            "description": self.description,
            "description_short": self.description_short,
            "specs": self.specs,
            "features": self.features,
            "faq": self.faq,
            "audiences": self.audiences,
            "rating": self.rating,
            "review_count": self.review_count,
            "pros": self.pros,
            "cons": self.cons,
            "contextual_data": self.contextual_data,
            "quality_score": self.quality_score,
            "data_status": self.data_status,
            "data_missing": self.data_missing,
            "halilit_url": self.halilit_url,
            "official_url": self.official_url,
            "sources": self.sources,
            "data_trust": self.data_trust,
            "search_text": self.search_text,
            # ── New graph fields (additive — won't break existing frontend) ──
            "family_id": self.family_id,
            "variant_key": self.variant.variant_key if self.variant else None,
            "variant_is_default": self.variant.is_default if self.variant else None,
        }
        return flat

    @classmethod
    def from_flat(cls, flat: Dict[str, Any]) -> "CanonicalProduct":
        """
        Create a CanonicalProduct from a flat ConductorProduct dict.
        Used during migration from the old normalization path.
        """
        variant = None
        if flat.get("variant_key"):
            variant = ProductVariant(
                variant_key=flat["variant_key"],
                is_default=flat.get("variant_is_default", False),
            )

        return cls(
            id=flat.get("id", ""),
            name=flat.get("name", ""),
            brand=flat.get("brand", ""),
            brand_logo=flat.get("brand_logo", ""),
            sku=flat.get("sku", ""),
            halilit_url=flat.get("halilit_url", ""),
            galaxy_id=flat.get("galaxy_id", ""),
            spectrum_id=flat.get("spectrum_id", ""),
            category=flat.get("category", ""),
            subcategory=flat.get("subcategory", ""),
            price=flat.get("price", 0.0),
            price_eilat=flat.get("price_eilat", 0.0),
            currency=flat.get("currency", "ILS"),
            tier=flat.get("tier", "mid"),
            image_url=flat.get("image_url", ""),
            image_gallery=flat.get("image_gallery", []),
            description=flat.get("description", ""),
            description_short=flat.get("description_short", ""),
            official_url=flat.get("official_url", ""),
            specs=flat.get("specs", {}),
            features=flat.get("features", []),
            faq=flat.get("faq", []),
            audiences=flat.get("audiences", []),
            rating=flat.get("rating", 0.0),
            review_count=flat.get("review_count", 0),
            pros=flat.get("pros", []),
            cons=flat.get("cons", []),
            contextual_data=flat.get("contextual_data", {}),
            quality_score=flat.get("quality_score", 0.0),
            data_status=flat.get("data_status", "MINIMAL"),
            data_missing=flat.get("data_missing", []),
            sources=flat.get("sources", []),
            data_trust=flat.get("data_trust", {}),
            search_text=flat.get("search_text", ""),
            family_id=flat.get("family_id"),
            variant=variant,
        )


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: THE PRODUCT GRAPH (Top-Level Container)
# ═══════════════════════════════════════════════════════════════════════════

class ProductGraph(BaseModel):
    """
    The Canonical Product Graph — the single source of truth for all
    product data, relationships, and family structures.

    Replaces the dual-normalization pipeline with one coherent graph.
    """
    version: int = Field(default=1, description="Graph schema version")

    # Core data stores
    families: Dict[str, ProductFamily] = Field(default_factory=dict)
    products: Dict[str, CanonicalProduct] = Field(default_factory=dict)
    relationships: List[ProductRelationship] = Field(default_factory=list)

    # Computed indexes (rebuilt on mutation)
    _rel_by_source: Dict[str, List[int]] = {}
    _rel_by_target: Dict[str, List[int]] = {}
    _rel_by_type: Dict[str, List[int]] = {}

    class Config:
        arbitrary_types_allowed = True

    # ── Index Management ──

    def rebuild_indexes(self) -> None:
        """Rebuild all relationship indexes after mutations."""
        self._rel_by_source = {}
        self._rel_by_target = {}
        self._rel_by_type = {}

        for idx, rel in enumerate(self.relationships):
            self._rel_by_source.setdefault(rel.source_id, []).append(idx)
            self._rel_by_target.setdefault(rel.target_id, []).append(idx)
            self._rel_by_type.setdefault(
                rel.relationship_type.value, []).append(idx)

            # For bidirectional relationships, index the reverse direction too
            if rel.direction == RelationshipDirection.BIDIRECTIONAL:
                self._rel_by_source.setdefault(rel.target_id, []).append(idx)
                self._rel_by_target.setdefault(rel.source_id, []).append(idx)

    # ── Query Methods ──

    def get_relationships_for(self, product_id: str) -> List[ProductRelationship]:
        """Get all relationships involving a product (as source or target)."""
        if not self._rel_by_source and self.relationships:
            self.rebuild_indexes()

        indices: Set[int] = set()
        indices.update(self._rel_by_source.get(product_id, []))
        indices.update(self._rel_by_target.get(product_id, []))
        return [self.relationships[i] for i in sorted(indices)]

    def get_relationships_by_type(self, product_id: str,
                                  rel_type: RelationshipType) -> List[ProductRelationship]:
        """Get relationships of a specific type involving a product."""
        all_rels = self.get_relationships_for(product_id)
        return [r for r in all_rels if r.relationship_type == rel_type]

    def get_family_members(self, family_id: str) -> List[CanonicalProduct]:
        """Get all products in a family."""
        family = self.families.get(family_id)
        if not family:
            return []
        return [self.products[vid] for vid in family.variant_ids
                if vid in self.products]

    def get_accessories(self, product_id: str) -> List[CanonicalProduct]:
        """Get all accessories for a product."""
        rels = self.get_relationships_by_type(
            product_id, RelationshipType.ACCESSORY_FOR)
        accessory_ids = set()
        for r in rels:
            # Accessory → Product: source is the accessory
            if r.target_id == product_id:
                accessory_ids.add(r.source_id)
            # Bidirectional check
            if r.source_id == product_id and r.direction == RelationshipDirection.BIDIRECTIONAL:
                accessory_ids.add(r.target_id)
        return [self.products[aid] for aid in accessory_ids if aid in self.products]

    def get_compatible(self, product_id: str) -> List[CanonicalProduct]:
        """Get all compatible products."""
        rels = self.get_relationships_by_type(
            product_id, RelationshipType.COMPATIBLE_WITH)
        ids = set()
        for r in rels:
            other = r.target_id if r.source_id == product_id else r.source_id
            ids.add(other)
        return [self.products[pid] for pid in ids if pid in self.products]

    def get_alternatives(self, product_id: str) -> List[CanonicalProduct]:
        """Get alternative products."""
        rels = self.get_relationships_by_type(
            product_id, RelationshipType.ALTERNATIVE_TO)
        ids = set()
        for r in rels:
            other = r.target_id if r.source_id == product_id else r.source_id
            ids.add(other)
        return [self.products[pid] for pid in ids if pid in self.products]

    def get_variants(self, product_id: str) -> List[CanonicalProduct]:
        """Get all variants in the same family as this product."""
        product = self.products.get(product_id)
        if not product or not product.family_id:
            return []
        members = self.get_family_members(product.family_id)
        return [m for m in members if m.id != product_id]

    # ── Mutation Methods ──

    def add_product(self, product: CanonicalProduct) -> None:
        """Add or update a product in the graph."""
        self.products[product.id] = product

    def add_family(self, family: ProductFamily) -> None:
        """Add or update a family."""
        self.families[family.id] = family

    def add_relationship(self, relationship: ProductRelationship) -> None:
        """Add a relationship, auto-setting direction from defaults.
        Deduplicates by (source_id, target_id, relationship_type)."""
        if relationship.direction == RelationshipDirection.UNIDIRECTIONAL:
            default_dir = RELATIONSHIP_DEFAULTS.get(
                relationship.relationship_type,
                RelationshipDirection.UNIDIRECTIONAL
            )
            relationship.direction = default_dir

        # Deduplicate: merge if same source+target+type already exists
        for existing in self.relationships:
            if (existing.source_id == relationship.source_id
                    and existing.target_id == relationship.target_id
                    and existing.relationship_type == relationship.relationship_type):
                # Merge sources_verified (union) and bump confidence
                for src in relationship.sources_verified:
                    if src not in existing.sources_verified:
                        existing.sources_verified.append(src)
                existing.confidence = max(
                    existing.confidence,
                    relationship.confidence,
                    min(1.0, 0.5 + 0.2 * len(existing.sources_verified)),
                )
                existing.updated_at = datetime.utcnow().isoformat()
                return

        self.relationships.append(relationship)
        # Invalidate indexes
        self._rel_by_source = {}
        self._rel_by_target = {}
        self._rel_by_type = {}

    def remove_relationship(self, source_id: str, target_id: str,
                            rel_type: RelationshipType) -> bool:
        """Remove a specific relationship. Returns True if found and removed."""
        for i, r in enumerate(self.relationships):
            if (r.source_id == source_id and r.target_id == target_id
                    and r.relationship_type == rel_type):
                self.relationships.pop(i)
                self._rel_by_source = {}
                self._rel_by_target = {}
                self._rel_by_type = {}
                return True
        return False

    # ── Serialization for Catalog API ──

    def to_catalog_indexes(self, product_indices: Dict[str, int]) -> Dict:
        """
        Build family and relationship indexes compatible with the catalog API.
        product_indices maps product_id → position in the products array.
        """
        by_family: Dict[str, List[int]] = {}
        relationships_map: Dict[str, List[Dict]] = {}

        # Family index
        for fam_id, family in self.families.items():
            indices = []
            for vid in family.variant_ids:
                if vid in product_indices:
                    indices.append(product_indices[vid])
            if indices:
                by_family[fam_id] = indices

        # Relationship index (per product)
        # Index under BOTH source and target so either side can look up the rel
        for rel in self.relationships:
            rel_dict = {**rel.model_dump(), "is_triple_checked": rel.is_triple_checked}
            relationships_map.setdefault(rel.source_id, []).append(rel_dict)
            # Always index the target side too — product pages need to find
            # e.g., what accessories exist for them (target of accessory_for)
            if rel.target_id != rel.source_id:
                relationships_map.setdefault(
                    rel.target_id, []).append(rel_dict)

        return {
            "by_family": by_family,
            "relationships": relationships_map,
        }

    def get_graph_stats(self) -> Dict[str, Any]:
        """Summary statistics for metadata."""
        confirmed = sum(1 for r in self.relationships if r.is_confirmed)
        pending = sum(1 for r in self.relationships if r.needs_review)
        triple_checked = sum(1 for r in self.relationships if r.is_triple_checked)
        type_counts = {}
        for r in self.relationships:
            type_counts[r.relationship_type.value] = type_counts.get(
                r.relationship_type.value, 0) + 1

        products_in_families = sum(
            1 for p in self.products.values() if p.family_id
        )

        return {
            "total_families": len(self.families),
            "total_relationships": len(self.relationships),
            "confirmed_relationships": confirmed,
            "pending_review": pending,
            "triple_checked_relationships": triple_checked,
            "products_in_families": products_in_families,
            "products_without_family": len(self.products) - products_in_families,
            "relationship_type_counts": type_counts,
        }

    # ── Factory Method ──

    @classmethod
    def from_flat_products(cls, flat_products: List[Dict[str, Any]]) -> "ProductGraph":
        """
        Create a ProductGraph from a list of flat product dicts
        (the current normalize_product() output).
        """
        graph = cls()
        for flat in flat_products:
            product = CanonicalProduct.from_flat(flat)
            graph.add_product(product)
        return graph
