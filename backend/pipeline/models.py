"""
Pipeline Data Models - Single source of truth for all schemas.

These Pydantic models define the contract between:
  - Harvesters (data in)
  - Processing layers (transformation)
  - Frontend (data out)

TypeScript types are auto-generated from these models.
"""

from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import hashlib
import json


# =============================================================================
# ENUMS
# =============================================================================

class TierLevel(str, Enum):
    """Product quality tier based on data completeness."""
    DIAMOND = "diamond"  # 75+ score: Complete data, verified
    GOLD = "gold"        # 60-74: Good data, minor gaps
    SILVER = "silver"    # 40-59: Basic data, needs enrichment
    BRONZE = "bronze"    # 0-39: Minimal data


class StockStatus(str, Enum):
    """Product availability status."""
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    PRE_ORDER = "pre_order"
    DISCONTINUED = "discontinued"
    UNKNOWN = "unknown"


# =============================================================================
# SOURCE MODELS (Input from 3 pillars)
# =============================================================================

class OfficialData(BaseModel):
    """
    PILLAR 1: Official Manufacturer Data
    The authoritative source for product identity and specifications.
    """
    manufacturer_sku: str = Field(...,
                                  description="Official SKU from manufacturer")
    official_name: str = Field(..., min_length=1, max_length=200)
    brand_id: str = Field(..., pattern="^[a-z0-9-]+$")
    brand_name: str

    # Technical specs
    category: str = Field(default="Other")
    subcategory: Optional[str] = None
    description: str = Field(default="", max_length=2000)
    specifications: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Nested specs: {'Audio': {'Frequency': '20Hz-20kHz'}}"
    )

    # Media
    images: List[Dict[str, Any]] = Field(default_factory=list)
    manuals: List[str] = Field(default_factory=list)
    official_url: Optional[str] = None

    # Metadata
    harvested_at: datetime = Field(default_factory=datetime.utcnow)
    source_hash: str = ""

    @field_validator('source_hash', mode='before')
    @classmethod
    def compute_hash(cls, v, info):
        if v:
            return v
        data = {
            'name': info.data.get('official_name'),
            'sku': info.data.get('manufacturer_sku'),
            'specs': info.data.get('specifications', {}),
        }
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()


class CommercialData(BaseModel):
    """
    PILLAR 2: Commercial/Retail Data
    Price and availability from Halilit's e-commerce.
    """
    halilit_sku: str = Field(..., description="Halilit's internal SKU")
    product_id: str = Field(..., description="Reference to official product")

    # Pricing
    price_ils: Optional[float] = Field(None, gt=0, description="Price in ILS")
    price_usd: Optional[float] = Field(
        None, gt=0, description="Converted to USD")
    member_price_ils: Optional[float] = None
    currency: str = "ILS"

    # Availability
    stock_status: StockStatus = StockStatus.UNKNOWN
    stock_quantity: Optional[int] = None
    delivery_estimate: Optional[str] = None

    # URLs
    product_url: Optional[str] = None

    # Metadata
    last_checked: datetime = Field(default_factory=datetime.utcnow)


class ReviewSource(BaseModel):
    """A single verified review source."""
    source_name: str
    url: str
    rating: Optional[float] = Field(None, ge=0, le=100)
    date: Optional[str] = None
    snippet: Optional[str] = None


class ContextualData(BaseModel):
    """
    PILLAR 3: Contextual/Real-World Data
    Synthesized from expert reviews and user feedback.
    """
    product_id: str

    # Verified sources
    verified_sources: List[ReviewSource] = Field(default_factory=list)

    # AI-synthesized insights
    pros: List[str] = Field(
        default_factory=list,
        description="Consensus strengths from multiple sources"
    )
    cons: List[str] = Field(
        default_factory=list,
        description="Consensus weaknesses"
    )
    recurring_issues: List[str] = Field(
        default_factory=list,
        description="Known problems mentioned across reviews"
    )
    expert_tips: List[str] = Field(
        default_factory=list,
        description="Pro tips from professionals"
    )

    # Quality metrics
    confidence_score: int = Field(
        default=0,
        ge=0,
        le=100,
        description="How trustworthy is this data (based on source count/quality)"
    )

    # Metadata
    synthesized_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# MERGED PRODUCT (After Layer 1: Normalize)
# =============================================================================

class ImageAsset(BaseModel):
    """Optimized image with metadata."""
    url: str
    alt: str = "Product image"
    role: str = Field(default="detail",
                      pattern="^(hero|thumbnail|detail|gallery)$")
    width: Optional[int] = None
    height: Optional[int] = None


class SpecItem(BaseModel):
    """A single specification entry."""
    key: str
    value: str
    unit: Optional[str] = None
    icon: Optional[str] = None


class NormalizedProduct(BaseModel):
    """
    Layer 1 Output: Validated, merged product from all 3 sources.
    """
    # Identity
    id: str = Field(..., pattern="^[a-z0-9-]+$")
    brand_id: str = Field(..., pattern="^[a-z0-9-]+$")
    sku: str

    # Naming
    name: str = Field(..., min_length=1, max_length=200)
    name_he: Optional[str] = None  # Hebrew name from Halilit

    # Classification
    category: str
    subcategory: Optional[str] = None

    # Content
    description: str = Field(default="", max_length=2000)

    # Commerce (from Commercial pillar)
    price: Optional[float] = None
    currency: str = "USD"
    stock_status: StockStatus = StockStatus.UNKNOWN

    # Visuals (from Official pillar)
    images: List[ImageAsset] = Field(default_factory=list)
    color_primary: Optional[str] = None

    # Specs (from Official pillar)
    specifications: Dict[str, List[SpecItem]] = Field(default_factory=dict)

    # Context (from Contextual pillar)
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    expert_tips: List[str] = Field(default_factory=list)
    review_sources: List[ReviewSource] = Field(default_factory=list)

    # URLs
    official_url: Optional[str] = None
    purchase_url: Optional[str] = None

    # Audit
    content_hash: str = ""
    normalized_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('content_hash', mode='before')
    @classmethod
    def compute_hash(cls, v, info):
        if v:
            return v
        data = {
            'name': info.data.get('name'),
            'sku': info.data.get('sku'),
            'price': info.data.get('price'),
        }
        return hashlib.md5(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()


# =============================================================================
# ENRICHED PRODUCT (After Layer 2: Enrich)
# =============================================================================

class EnrichedProduct(BaseModel):
    """
    Layer 2 Output: Product with taxonomy and tier assignment.
    """
    # All normalized fields
    id: str
    brand_id: str
    sku: str
    name: str
    name_he: Optional[str] = None

    # Enhanced taxonomy
    category: str
    subcategories: List[str] = Field(default_factory=list)
    taxonomy_confidence: float = Field(default=0.5, ge=0, le=1)

    # Tier assignment
    tier: TierLevel
    tier_score: int = Field(ge=0, le=100)
    tier_reasons: List[str] = Field(default_factory=list)

    # Content
    description: str = ""
    description_short: str = Field(default="", max_length=100)

    # Commerce
    price: Optional[float] = None
    currency: str = "USD"
    stock_status: StockStatus = StockStatus.UNKNOWN

    # Visuals with hero/thumbnail selection
    image_hero: Optional[ImageAsset] = None
    image_thumbnail: Optional[ImageAsset] = None
    image_gallery: List[ImageAsset] = Field(default_factory=list)
    color_primary: Optional[str] = None

    # Specs grouped by category
    specs: Dict[str, List[SpecItem]] = Field(default_factory=dict)

    # Context
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    expert_tips: List[str] = Field(default_factory=list)

    # URLs
    official_url: Optional[str] = None
    purchase_url: Optional[str] = None

    # Metadata
    enriched_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# OPTIMIZED PRODUCT (After Layer 3: Optimize - Final Output)
# =============================================================================

class OptimizedProduct(BaseModel):
    """
    Layer 3 Output: UI-ready product JSON.
    This is the contract between backend and frontend.
    """
    # Identity
    id: str
    name: str
    slug: str
    brand_id: str

    # Taxonomy
    category: str
    subcategories: List[str] = Field(default_factory=list)
    tier: str
    tier_score: int

    # Content
    description_short: str = Field(max_length=100)
    description_full: str

    # Commerce
    price: Optional[float] = None
    currency: str = "USD"
    stock_status: str

    # Visuals
    image_hero: Optional[Dict[str, Any]] = None
    image_thumbnail: Optional[Dict[str, Any]] = None
    image_gallery: List[Dict[str, Any]] = Field(default_factory=list)
    color_primary: Optional[str] = None

    # Specs (flattened for UI)
    specs: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)

    # Context
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    expert_tips: List[str] = Field(default_factory=list)

    # Search & Filter
    search_text: str = ""
    filter_tags: List[str] = Field(default_factory=list)

    # UI Hints
    render_hints: Dict[str, bool] = Field(default_factory=dict)

    # URLs
    source_url: Optional[str] = None
    purchase_url: Optional[str] = None

    # Metadata
    synced_at: str

    @field_validator('slug', mode='before')
    @classmethod
    def generate_slug(cls, v, info):
        if v:
            return v
        name = info.data.get('name', '').lower()
        # Create URL-safe slug
        import re
        slug = re.sub(r'[^a-z0-9\s-]', '', name)
        slug = re.sub(r'\s+', '-', slug).strip('-')
        brand = info.data.get('brand_id', '')
        return f"/{brand}/{slug}"


# =============================================================================
# CATALOG MODELS (Index and Brand files)
# =============================================================================

class BrandSummary(BaseModel):
    """Brand entry in the catalog index."""
    id: str
    name: str
    logo_url: Optional[str] = None
    brand_color: Optional[str] = None
    product_count: int = 0
    verified_count: int = 0
    data_file: str


class CatalogIndex(BaseModel):
    """
    The main index.json that lists all brands.
    Frontend loads this first to discover available data.
    """
    version: str = "5.0.0"
    build_timestamp: str
    total_products: int = 0
    total_verified: int = 0
    brands: List[BrandSummary] = Field(default_factory=list)


class BrandCatalog(BaseModel):
    """
    Per-brand catalog file (e.g., adam-audio.json).
    Contains all products for one brand.
    """
    brand: str
    brand_name: str
    brand_color: Optional[str] = None
    logo_url: Optional[str] = None
    product_count: int = 0
    products: List[OptimizedProduct] = Field(default_factory=list)
    generated_at: str
