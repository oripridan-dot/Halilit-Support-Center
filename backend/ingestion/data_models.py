"""
UNIFIED DATA MODELS FOR INGESTION PIPELINE v6.1

Consolidates taxonomy, pricing, and display considerations into a single
data flow from scraping through verification.

These models are the "language" that all ingestion components speak.

SOURCE RULES (see backend/source_rules.py for the full law):
  1. COMMERCIAL (Halilit.com)  -> Golden List, Prices, SKUs
  2. OFFICIAL (Brand pages)    -> Titles, Descriptions, Specs, Media
  3. CONTEXTUAL (3+ Reviews)   -> Pros/Cons, Real-world insights

NO SYNTHETIC DATA. NO MOCKING. ONLY REAL DATA.
"""

from pydantic import BaseModel, ConfigDict, Field
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
    model_config = ConfigDict(use_enum_values=False)

    source_name: str  # "halilit", "official_nord", "amazon", etc.
    source_url: str
    confidence: DataSourceConfidence = DataSourceConfidence.COMMERCIAL
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    extraction_method: str  # "api", "web_scraper", "manual", "feed"
    extraction_notes: Optional[str] = None


class FieldLineage(BaseModel):
    """Track provenance of specific data fields"""
    field_name: str
    source: str  # e.g., "trinity_agent_v2" or "regex_fallback"
    confidence: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    previous_value: Any = None


class TaxonomyMapping(BaseModel):
    """Product's position in taxonomy hierarchy"""
    model_config = ConfigDict(use_enum_values=False)

    canonical_category: str  # Universal: "Keyboards & Synthesizers"
    canonical_subcategory: str  # Universal: "Synthesizer"
    brand_taxonomy: Optional[str] = None  # Brand-specific if different
    alt_categories: List[str] = []  # Secondary classifications
    keywords: List[str] = []  # For search/discovery


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

    model_config = ConfigDict(use_enum_values=True)


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
    model_config = ConfigDict(use_enum_values=True)

    display_role: DisplayRole = DisplayRole.SPECIALIST
    hero_image: Optional[str] = None  # URL to main hero image
    thumbnail_image: Optional[str] = None
    should_highlight: bool = False  # Featured/trending
    display_tier_level: int = 3  # 1-5, higher = more prominent tier
    color_hint: Optional[str] = None  # Suggested brand color
    media_assets: List[MediaAsset] = []
    visual_issues: List[str] = []  # Issues found by VisualValidator


class ProductSpecifications(BaseModel):
    """Technical specifications with source tracking"""
    specs_dict: Dict[str, Any] = {}  # {key: value}
    specs_source: DataSourceConfidence = DataSourceConfidence.COMMERCIAL
    specs_completeness: float = 0.5  # 0-1, how complete are specs
    specs_markdown: Optional[str] = None  # Formatted specs for display


class IngestionProductDraft(BaseModel):
    """
    UNIFIED PRODUCT MODEL(v6.0 - Strict Separation): Single source of separation.

    This model enforces the "Iron Rules" of source-of-truth:
    1. COMMERCIAL(Halilit) -> Inventory, Price, SKU(The Golden List)
    2. OFFICIAL(Brand) -> Specs, Media, Description(The Knowledge)
    3. CONTEXTUAL(Reviews) -> Ratings, Pros/Cons(The Insight)
    """

    # --- 1. COMMERCIAL DATA (The Golden List - Source: Halilit) ---
    halilit_id: str = Field(..., description="Unique ID from Halilit (SKU)")
    product_name: str = Field(..., description="Name as listed on Halilit")
    brand: str = Field(..., description="Brand as listed on Halilit")
    price_il: float = Field(..., description="Official IL Price from Halilit")
    price_eilat: float = Field(...,
                               description="Official Eilat Price from Halilit")
    halilit_url: str = Field(..., description="Source URL on Halilit")
    sku: Optional[str] = None
    model_number: Optional[str] = None
    official_name: Optional[str] = None

    # --- 2. OFFICIAL DATA (The Knowledge - Source: Brand Site) ---
    official_specs: Dict[str, Any] = Field(
        default_factory=dict, description="Tech specs from brand site")
    official_description: Optional[str] = Field(
        None, description="Marketing copy from brand site")
    official_images: List[MediaAsset] = Field(
        default_factory=list, description="High-res assets from brand")
    official_url: Optional[str] = Field(
        None, description="URL of the official product page")

    # --- 3. CONTEXTUAL DATA (The Insight - Source: 3+ Trusted Review Sites) ---
    # RULE: Must come from AT LEAST 3 well-trusted review websites
    # RULE: Each review must be SPECIFIC to this exact product
    # RULE: NO AI-generated reviews. ONLY real user/critic reviews.
    reviews: List[Dict[str, Any]] = Field(
        default_factory=list, description="Reviews from 3+ trusted sites")
    review_sources: List[str] = Field(
        default_factory=list, description="URLs of review sources (minimum 3 required)")
    review_pros: List[str] = Field(
        default_factory=list, description="Real pros from user reviews")
    review_cons: List[str] = Field(
        default_factory=list, description="Real cons from user reviews")
    review_synthesis: Optional[str] = Field(
        None, description="Summary of real reviews (not AI-generated opinions)")
    user_sentiment: Optional[str] = Field(
        None, description="Overall user sentiment from review aggregation")
    real_world_insights: List[str] = Field(
        default_factory=list, description="Practical insights from real users")
    average_rating: Optional[float] = Field(
        None, description="Normalized 0-5 rating from aggregated reviews")

    # --- PIPELINE METADATA ---
    status: IngestionStatus = IngestionStatus.HARVESTED
    pipeline_phase: str = "harvest"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    # --- LEGACY / COMPUTED (Maintained for compatibility but derived) ---
    # These containers capture the OUTPUT of the pipeline phases
    taxonomy: Optional[TaxonomyMapping] = None
    pricing: Optional[PricingData] = None
    display: Optional[DisplayProperties] = None
    specifications: Optional[ProductSpecifications] = None

    # Description & Content (Derived/Legacy)
    description_short: Optional[str] = None
    description_long: Optional[str] = None
    feature_list: List[str] = []

    # Source Tracking
    sources: List[SourceProvenance] = []
    primary_source: Optional[SourceProvenance] = None
    lineage: Dict[str, FieldLineage] = Field(
        default_factory=dict, description="Per-field data lineage tracking")
    raw_snapshot: Dict[str, Any] = Field(
        default_factory=dict, description="Snapshot of raw input data for verification")

    # Quality & Validation
    data_completeness: float = 0.5
    quality_score: float = 0.5
    validation_status: IngestionStatus = IngestionStatus.HARVESTED
    validation_errors: List[str] = []
    validation_warnings: List[str] = []

    # Visual Matching (New)
    visual_match_confidence: float = Field(
        0.0, description="Confidence that commercial and official images match")
    visual_match_reasoning: Optional[str] = None
    visual_match_status: str = "pending"  # pending, matched, mismatch, skipped

    # --- SOURCE COVERAGE TRACKING ---
    source_coverage_commercial: bool = Field(
        False, description="Whether Commercial Scout has provided its data")
    source_coverage_official: bool = Field(
        False, description="Whether Official Scout has provided its data")
    source_coverage_contextual: bool = Field(
        False, description="Whether Contextual Scout has provided its data")
    contextual_source_count: int = Field(
        0, description="How many review sources contributed (must be >= 3)")
    cross_validation_confidence: float = Field(
        0.0, description="Cross-validation confidence score 0.0-1.0")
    cross_validation_status: str = Field(
        "pending", description="pending, validated, conflicts_found, incomplete")

    model_config = ConfigDict(
        arbitrary_types_allowed=True, use_enum_values=True, extra="allow")


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

    if pricing.price_il < 0:
        errors.append("price_il must be non-negative")

    if pricing.price_eilat < 0:
        errors.append("price_eilat must be non-negative")

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
