# backend/models/product_hierarchy.py
from typing import List, Dict, Optional, Any, Literal, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class ProductStatus(str, Enum):
    IN_STOCK = "in_stock"
    PRE_ORDER = "pre_order"
    DISCONTINUED = "discontinued"
    COMING_SOON = "coming_soon"

class BrandIdentity(BaseModel):
    id: str
    name: str
    website: str
    logo_url: Optional[str] = None

class ProductImage(BaseModel):
    url: str
    type: str = "main"
    alt_text: Optional[str] = None

class ProductSpecification(BaseModel):
    key: str
    value: str

class PriceInfo(BaseModel):
    regular_price: Optional[float] = None
    eilat_price: Optional[float] = None

class SourceType(str, Enum):
    BRAND_OFFICIAL = "official"
    COMMERCIAL = "commercial"
    MANUAL = "manual"
    GENERATED = "generated"
    OFFICIAL = "official"

class RelationshipType(str, Enum):
    ACCESSORY = "accessory"
    RELATED = "related"
    REQUIRED = "necessity"
    COMPATIBLE = "compatible"

class ProductRelationship(BaseModel):
    id: str
    name: str = ""
    type: RelationshipType
    category: Optional[str] = None
    sku: Optional[str] = None

class ProductTier(BaseModel):
    level: str
    grade_factors: List[str] = []
    target_audience: str = "General"

class ConnectivityDNA(BaseModel):
    type: str = "cable"
    connector_a: str = "Unknown"
    connector_b: str = "Unknown"
    signal_type: str = "Unknown"
    length_meters: Optional[float] = None
    
    # Legacy / Additional
    has_midi: bool = False
    has_usb: bool = False

class ProductCore(BaseModel):
    """
    The Master Product Entity.
    """
    id: str
    brand: str
    name: str = "Unknown Product"
    sku: Optional[str] = None
    
    # Classification
    main_category: str = Field(..., alias="category")
    subcategory: Optional[str] = None
    
    # Data
    description: str = ""
    features: List[str] = []
    specifications: List[ProductSpecification] = []
    images: List[ProductImage] = []
    pricing: Optional[PriceInfo] = None
    status: ProductStatus = ProductStatus.IN_STOCK
    
    # Links
    manual_urls: List[str] = []
    support_url: Optional[str] = None
    video_urls: List[str] = []

    # Relationships (Specific)
    accessories: List[ProductRelationship] = []
    related_products: List[ProductRelationship] = []

    # Rich Data
    relationships: List[ProductRelationship] = []
    connectivity: Optional[ConnectivityDNA] = None
    tier: Optional[ProductTier] = None
    source: SourceType = SourceType.OFFICIAL
    data_sources: List[SourceType] = []
    
    # --- NEW: Frontend Normalization Hooks ---
    tribe_assignment: Optional[str] = Field(None, description="Force a specific Tribe ID")

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True

class ProductCatalog(BaseModel):
    brand_identity: Union[BrandIdentity, Dict[str, Any]]
    products: List[ProductCore]
    total_products: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    @validator('total_products', pre=True, always=True)
    def set_total_products(cls, v, values):
        if v is None or v == 0:
            if 'products' in values and values['products']:
                return len(values['products'])
        return v or 0

    @validator('last_updated', pre=True, always=True)
    def set_last_updated(cls, v):
        if v is None:
            return datetime.utcnow()
        return v
