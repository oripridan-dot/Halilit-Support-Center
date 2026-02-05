"""
UNIFIED DATA MODELS FOR INGESTION PIPELINE v6.0

Consolidates taxonomy, pricing, and display considerations into a single
data flow from scraping through verification.

These models are the "language" that all ingestion components speak.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


# ============================================================================
# ENUMS: Taxonomies, Tiers, Statuses
# ============================================================================

class PricingTier(str, Enum):
    """Standard pricing tier categories"""
    ENTRY = "entry"  # Budget: < $500
    MID = "mid"  # Mid-range: $500-$1,500
    PRO = "pro"  # Professional: $1,500-$4,000
    FLAGSHIP = "flagship"  # Premium: > $4,000
    LEGACY = "legacy"  # Discontinued/Archive


class DisplayRole(str, Enum):
    """Primary purpose of product for UI display"""
    HERO = "hero"  # Featured/flagship model
    CORNERSTONE = "cornerstone"  # Key stepping stone
    SPECIALIST = "specialist"  # Niche/specific use case
    ENTRY = "entry"  # Gateway product
    HIDDEN = "hidden"  # Don't display (internal use)


class IngestionStatus(str, Enum):
    """Status throughout the ingestion workflow"""
    HARVESTED = "harvested"  # Raw from scraper
    ENRICHED = "enriched"  # Taxonomy + pricing applied
    VALIDATED = "validated"  # Passed compliance checks
    APPROVED = "approved"  # Ready to display
    REJECTED = "rejected"  # Failed validation
    ARCHIVED = "archived"  # Historical


class DataSourceConfidence(str, Enum):
    """Confidence level in data source"""
    OFFICIAL = "official"  # 1.0 - Direct from manufacturer
    TRUSTED = "trusted"  # 0.95 - Verified third party
    COMMERCIAL = "commercial"  # 0.9 - Retailer (Halilit)
    USER = "user"  # 0.7 - Community/reviews
    INFERRED = "inferred"  # 0.6 - Computed/guessed


# ============================================================================
# DATA MODELS: Core Structures
# ============================================================================

class SourceProvenance(BaseModel):
    """Track where data came from and its quality"""
    source_name: str  # "halilit", "official_nord", "amazon", etc.
    source_url: str
    confidence: DataSourceConfidence = DataSourceConfidence.COMMERCIAL
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    extraction_method: str  # "api", "web_scraper", "manual", "feed"
    extraction_notes: Optional[str] = None

    class Config:
        use_enum_values = False


class TaxonomyMapping(BaseModel):
    """Product's position in taxonomy hierarchy"""
    canonical_category: str  # Universal: "Keyboards & Synthesizers"
    canonical_subcategory: str  # Universal: "Synthesizer"
    brand_taxonomy: Optional[str] = None  # Brand-specific if different
    alt_categories: List[str] = []  # Secondary classifications
    keywords: List[str] = []  # For search/discovery

    class Config:
        use_enum_values = False


class PricingData(BaseModel):
    """All pricing information in one place"""
    price_il: float  # Israel mainland price (NIS)
    price_eilat: float  # Eilat/special region (NIS)
    price_usd: Optional[float] = None  # US price for reference
    price_eur: Optional[float] = None  # EU price for reference

    # Computed properties
    tier: PricingTier = Field(default=PricingTier.MID)
    eilat_discount_percent: float = 0.0  # Computed: (1 - eilat/il) * 100
    suggested_tier: Optional[PricingTier] = None  # AI suggestion
    price_validity_marker: str = "current"  # "current", "outdated", "provisional"

    # Price history
    last_price_change: Optional[datetime] = None
    previous_price_il: Optional[float] = None

    class Config:
        use_enum_values = True


class MediaAsset(BaseModel):
    """Individual media asset with purpose"""
    type: str  # "image", "video", "document"
    url: str
    display_purpose: str  # "hero", "gallery", "thumbnail", "specification"
    resolution: Optional[str] = None  # "1920x1080", "2000x1500"
    source: DataSourceConfidence = DataSourceConfidence.COMMERCIAL
    alt_text: Optional[str] = None
    priority: int = 100  # 0-255, higher = display first


class DisplayProperties(BaseModel):
    """How product should be displayed in UI"""
    display_role: DisplayRole = DisplayRole.SPECIALIST
    hero_image: Optional[str] = None  # URL to main hero image
    thumbnail_image: Optional[str] = None
    should_highlight: bool = False  # Featured/trending
    display_tier_level: int = 3  # 1-5, higher = more prominent tier
    color_hint: Optional[str] = None  # Suggested brand color
    media_assets: List[MediaAsset] = []

    class Config:
        use_enum_values = True


class ProductSpecifications(BaseModel):
    """Technical specifications with source tracking"""
    specs_dict: Dict[str, Any] = {}  # {key: value}
    specs_source: DataSourceConfidence = DataSourceConfidence.COMMERCIAL
    specs_completeness: float = 0.5  # 0-1, how complete are specs
    specs_markdown: Optional[str] = None  # Formatted specs for display


class IngestionProductDraft(BaseModel):
    """
    UNIFIED PRODUCT MODEL: Single source of truth for all ingestion data.

    This is THE model that flows through the entire pipeline:
    Harvest → Enrich (Taxonomy) → Tier (Pricing) → Prepare (Display) → Validate → Approve
    """

    # IDENTITY & NAMING
    halilit_id: str  # Primary unique identifier
    product_name: str  # Display name
    official_name: Optional[str] = None  # Manufacturer's official name
    brand: str  # Normalized brand name
    model_number: Optional[str] = None
    sku: Optional[str] = None

    # TAXONOMY & CLASSIFICATION
    taxonomy: TaxonomyMapping  # Category system

    # PRICING & VALUE
    pricing: PricingData  # All pricing in one place

    # DESCRIPTION & CONTENT
    description_short: Optional[str] = None
    description_long: Optional[str] = None
    feature_list: List[str] = []

    # TECHNICAL SPECIFICATIONS
    specifications: ProductSpecifications

    # DISPLAY & PRESENTATION
    display: DisplayProperties

    # SOURCE & PROVENANCE
    sources: List[SourceProvenance] = []  # Where this data came from
    primary_source: SourceProvenance  # Which source is primary

    # QUALITY & VALIDATION
    data_completeness: float = 0.5  # 0-1, overall data quality
    quality_score: float = 0.5  # 0-1, how complete and accurate
    validation_status: IngestionStatus = IngestionStatus.HARVESTED
    validation_errors: List[str] = []
    validation_warnings: List[str] = []

    # METADATA
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class IngestionBatch(BaseModel):
    """A batch of products being ingested together"""
    batch_id: str
    brand: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    products: List[IngestionProductDraft] = []
    batch_status: IngestionStatus = IngestionStatus.HARVESTED
    batch_notes: Optional[str] = None


class IngestionReport(BaseModel):
    """Final report from ingestion pipeline"""
    batch_id: str
    brand: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_products_processed: int
    approved_count: int
    rejected_count: int
    approved_products: List[IngestionProductDraft] = []
    rejected_products: List[tuple] = []  # (product, reason)
    critical_errors: List[str] = []
    warnings: List[str] = []
    execution_time_seconds: float = 0.0
    recommendations: List[str] = []


# ============================================================================
# COMPATIBILITY MODELS: Bridge to legacy systems
# ============================================================================

class ProductDraft(BaseModel):
    """Legacy ProductDraft for backwards compatibility"""
    id: str
    name: str
    brand: str
    price_il: float
    price_eilat: float
    image_url: Optional[str] = None
    source_url: Optional[str] = None
    official_match: Optional[bool] = False

    @classmethod
    def from_ingestion_draft(cls, draft: IngestionProductDraft) -> 'ProductDraft':
        """Convert new unified model back to legacy format"""
        return cls(
            id=draft.halilit_id,
            name=draft.product_name,
            brand=draft.brand,
            price_il=draft.pricing.price_il,
            price_eilat=draft.pricing.price_eilat,
            image_url=draft.display.hero_image,
            source_url=draft.primary_source.source_url if draft.primary_source else None,
            official_match=draft.primary_source.confidence == DataSourceConfidence.OFFICIAL if draft.primary_source else False,
        )

    def to_ingestion_draft(self, taxonomy: TaxonomyMapping, pricing_tier: PricingTier) -> IngestionProductDraft:
        """Convert legacy format to new unified model"""
        return IngestionProductDraft(
            halilit_id=self.id,
            product_name=self.name,
            brand=self.brand,
            taxonomy=taxonomy,
            pricing=PricingData(
                price_il=self.price_il,
                price_eilat=self.price_eilat,
                tier=pricing_tier,
                eilat_discount_percent=(
                    (self.price_il - self.price_eilat) / self.price_il * 100) if self.price_il > 0 else 0,
            ),
            display=DisplayProperties(
                hero_image=self.image_url,
            ),
            primary_source=SourceProvenance(
                source_name="legacy_import",
                source_url=self.source_url or "unknown",
                confidence=DataSourceConfidence.COMMERCIAL,
            ),
            sources=[SourceProvenance(
                source_name="legacy_import",
                source_url=self.source_url or "unknown",
                confidence=DataSourceConfidence.COMMERCIAL,
            )],
        )


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_pricing_consistency(pricing: PricingData) -> List[str]:
    """Validate pricing rules and return any violations"""
    errors = []

    if pricing.price_il <= 0:
        errors.append("price_il must be positive")

    if pricing.price_eilat <= 0:
        errors.append("price_eilat must be positive")

    if pricing.price_eilat > pricing.price_il:
        errors.append("Eilat price cannot exceed Israel mainland price")

    # Check discount percent is reasonable (0-25%)
    if pricing.eilat_discount_percent > 25:
        errors.append(
            f"Eilat discount {pricing.eilat_discount_percent:.1f}% seems too high")

    if pricing.eilat_discount_percent < 0:
        errors.append("Eilat discount cannot be negative")

    return errors


def compute_data_completeness(draft: IngestionProductDraft) -> float:
    """Compute overall data completeness score 0-1"""
    score = 0.0
    max_score = 0.0

    # Basic information (required)
    if draft.halilit_id:
        score += 0.1
    max_score += 0.1
    if draft.product_name:
        score += 0.1
    max_score += 0.1
    if draft.brand:
        score += 0.1
    max_score += 0.1

    # Pricing (required)
    if draft.pricing.price_il > 0:
        score += 0.1
    max_score += 0.1
    if draft.pricing.price_eilat > 0:
        score += 0.1
    max_score += 0.1

    # Taxonomy (required)
    if draft.taxonomy.canonical_category:
        score += 0.05
    max_score += 0.05
    if draft.taxonomy.canonical_subcategory:
        score += 0.05
    max_score += 0.05

    # Description (recommended)
    if draft.description_short:
        score += 0.05
    max_score += 0.05
    if draft.description_long:
        score += 0.05
    max_score += 0.05

    # Specifications (recommended)
    if draft.specifications.specs_dict:
        score += 0.05
    max_score += 0.05

    # Media (recommended)
    if draft.display.hero_image:
        score += 0.1
    max_score += 0.1
    if draft.display.media_assets:
        score += 0.05
    max_score += 0.05

    # Official source (recommended)
    if draft.primary_source and draft.primary_source.confidence == DataSourceConfidence.OFFICIAL:
        score += 0.05
    max_score += 0.05

    return score / max_score if max_score > 0 else 0.5
