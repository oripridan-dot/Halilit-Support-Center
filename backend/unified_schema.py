"""
UNIFIED PRODUCT SCHEMA v7.0 - Single Source of Truth
=====================================================

This module defines THE definitive Product structure that ALL screens must use.
It bridges backend (IngestionProductDraft) and frontend (TypeScript Product type).

CRITICAL RULE:
- All 3 screens MUST pull from the same data source
- All fields must be validated against this schema
- Any deviation triggers a validation error
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class ImageAsset(BaseModel):
    """Single image with metadata"""
    url: str = Field(..., description="Image URL")
    alt: Optional[str] = Field(None, description="Alt text")
    purpose: str = Field(
        "display", description="hero|thumbnail|gallery|documentation")
    source: str = Field(
        "halilit", description="Data source: halilit|official|community")

    class Config:
        use_enum_values = True


class PricePoint(BaseModel):
    """Price in a specific currency/region"""
    currency: str = Field(..., description="ILS, USD, EUR")
    amount: float = Field(..., description="Numeric price")
    region: str = Field("israel", description="israel|eilat|usa|eu")
    source: str = Field("halilit", description="Data source")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ProductSpecifications(BaseModel):
    """Unified specifications structure"""
    short_description: Optional[str] = None
    long_description: Optional[str] = None

    # Standardized specs
    specs: Dict[str, Any] = Field(default_factory=dict)
    features: List[str] = Field(default_factory=list)

    # Official metadata
    sku: Optional[str] = None
    model_number: Optional[str] = None
    official_name: Optional[str] = None
    official_url: Optional[str] = None

    # Quality metrics
    completeness_score: float = Field(
        0.0, description="0-100: How complete are specs")
    data_quality_score: float = Field(0.0, description="0-100: Data accuracy")

    class Config:
        use_enum_values = True


class ReviewData(BaseModel):
    """Reviews and ratings"""
    average_rating: Optional[float] = Field(None, ge=0, le=5)
    total_reviews: int = Field(default=0)
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    synthesis: Optional[str] = None
    # ["amazon", "sweetwater", etc]
    sources: List[str] = Field(default_factory=list)


class TaxonomyInfo(BaseModel):
    """Product's position in category hierarchy"""
    canonical_category: str = Field(..., description="6 main galaxies")
    canonical_subcategory: str = Field(...,
                                       description="spectrum tier i.e. synthesizers")
    brand_specific_category: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class DataProvenance(BaseModel):
    """Track data origin and confidence"""
    sources: List[str] = Field(
        default_factory=list)  # ["halilit", "official_brand", ...]
    halilit_confidence: float = Field(1.0, ge=0, le=1)
    official_confidence: float = Field(0.0, ge=0, le=1)
    community_confidence: float = Field(0.0, ge=0, le=1)

    # Lineage tracking
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    last_verified: Optional[datetime] = None
    verification_status: str = Field(
        "approved", description="approved|pending|rejected|archived")


class UnifiedProduct(BaseModel):
    """
    THE DEFINITIVE PRODUCT STRUCTURE - v7.0

    This is what ALL frontend screens MUST receive.
    Backend ingestion must transform everything to this schema.
    Frontend hooks must return this exact structure.
    """

    # ===== IDENTITY =====
    id: str = Field(..., description="Unique product ID (halilit_id)")
    name: str = Field(..., description="Product name")
    brand: str = Field(..., description="Brand name")
    halilit_id: str = Field(..., description="Original Halilit SKU")

    # ===== PRICING (Single Source of Truth: Halilit) =====
    pricing: Dict[str, PricePoint] = Field(default_factory=dict)

    # Convenience fields for quick access
    price_il: float = Field(...,
                            description="Primary Israel price (from pricing)")
    currency: str = Field("ILS", description="Primary currency")
    pricing_tier: str = Field(
        "mid", description="entry|mid|pro|flagship|legacy")

    # ===== IMAGES =====
    images: List[ImageAsset] = Field(default_factory=list)

    # Quick access fields
    image_hero: Optional[str] = None  # Main display image
    image_thumbnail: Optional[str] = None  # Thumbnail for lists

    # ===== SPECIFICATIONS & DETAILS =====
    specifications: ProductSpecifications = Field(
        default_factory=ProductSpecifications)

    # ===== REVIEWS & RATINGS =====
    reviews: ReviewData = Field(default_factory=ReviewData)

    # ===== TAXONOMY & CATEGORIZATION =====
    taxonomy: TaxonomyInfo = Field(...)

    # ===== DATA LINEAGE & PROVENANCE =====
    provenance: DataProvenance = Field(default_factory=DataProvenance)

    # ===== PIPELINE STATUS =====
    status: str = Field(
        "approved", description="harvested|enriched|validated|approved|rejected")
    in_stock: bool = Field(True)

    # ===== ENRICHMENT METADATA =====
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # ===== TIMESTAMPS =====
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat()}

    @validator('pricing')
    def validate_pricing(cls, v):
        """Ensure pricing dict is not empty"""
        if not v:
            raise ValueError("Product must have at least one price point")
        return v

    @validator('price_il')
    def validate_price_positive(cls, v):
        """Ensure price is positive"""
        if v <= 0:
            raise ValueError("Price must be positive")
        return v

    def get_price(self, currency: str = "ILS", region: str = "israel") -> Optional[float]:
        """Get price for specific currency/region"""
        key = f"{currency}_{region}"
        if key in self.pricing:
            return self.pricing[key].amount

        # Fallback: return any matching currency
        matching = [p.amount for p in self.pricing.values()
                    if p.currency == currency]
        return matching[0] if matching else self.price_il

    def to_frontend_dict(self) -> Dict[str, Any]:
        """
        Convert to frontend-compatible dictionary.
        Flattens nested structures for React components.
        """
        hero_img = next(
            (img.url for img in self.images if img.purpose == "hero"), self.image_hero)
        thumb_img = next(
            (img.url for img in self.images if img.purpose == "thumbnail"), self.image_thumbnail)

        return {
            # Identity
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "halilit_id": self.halilit_id,

            # Pricing (flattened for easy access)
            "price_il": self.price_il,
            "currency": self.currency,
            "pricing_tier": self.pricing_tier,
            "pricing": self.pricing,

            # Images (both nested and flat for compatibility)
            "images": {
                "main": hero_img,
                "thumbnail": thumb_img,
                "gallery": [img.url for img in self.images if img.purpose == "gallery"],
                "all": [img.dict() for img in self.images]
            },
            "image_hero": hero_img,
            "image_thumbnail": thumb_img,
            "image_url": hero_img,  # Legacy
            "image": hero_img,  # Legacy

            # Specs
            "specifications": self.specifications.dict(),
            "specs": self.specifications.specs,
            "features": self.specifications.features,
            "sku": self.specifications.sku,

            # Details
            "description_short": self.specifications.short_description,
            "description_long": self.specifications.long_description,

            # Reviews
            "reviews": self.reviews.dict(),
            "average_rating": self.reviews.average_rating,

            # Taxonomy
            "taxonomy": self.taxonomy.dict(),
            "category": self.taxonomy.canonical_category,
            "subcategory": self.taxonomy.canonical_subcategory,

            # Provenance
            "provenance": self.provenance.dict(),
            "sources": self.provenance.sources,

            # Status
            "status": self.status,
            "in_stock": self.in_stock,

            # Timestamps
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# ============================================================================
# BATCH OPERATIONS
# ============================================================================

class ProductBatch(BaseModel):
    """Batch of products with validation metadata"""
    products: List[UnifiedProduct] = Field(...)
    batch_id: str = Field(default_factory=lambda: str(
        datetime.utcnow().timestamp()))
    source: str = Field(..., description="Source system")
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)

    def validate_consistency(self) -> Dict[str, Any]:
        """Validate entire batch for consistency"""
        issues = {
            "errors": [],
            "warnings": [],
            "stats": {
                "total_products": len(self.products),
                "with_images": 0,
                "with_specs": 0,
                "with_reviews": 0,
                "average_price": 0.0,
            }
        }

        total_price = 0
        for product in self.products:
            if product.images:
                issues["stats"]["with_images"] += 1
            if product.specifications.specs:
                issues["stats"]["with_specs"] += 1
            if product.reviews.total_reviews > 0:
                issues["stats"]["with_reviews"] += 1
            total_price += product.price_il

        if self.products:
            issues["stats"]["average_price"] = total_price / len(self.products)

        return issues
