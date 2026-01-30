from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class VendorData(BaseModel):
    """Path 2: Commercial Data (Source: Halilit)"""
    sku: str
    price: float
    sale_price: Optional[float] = None
    currency: str = "ILS"
    stock_status: str  # "IN_STOCK", "OUT_OF_STOCK", "PRE_ORDER"
    purchase_url: str
    is_sold_locally: bool = True
    local_description: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.now)


class MediaAsset(BaseModel):
    type: str  # "image", "video", "manual", "3d_model"
    url: str
    label: Optional[str] = None
    is_local: bool = False
    local_path: Optional[str] = None


class TechnicalData(BaseModel):
    """Path 1: Technical & Media (Source: Brand/Manufacturer)"""
    manufacturer_sku: Optional[str] = None
    # e.g. {"Weight": "5kg", "Power": "220V"}
    specifications: Dict[str, str] = Field(default_factory=dict)
    official_description: Optional[str] = None
    assets: List[MediaAsset] = Field(default_factory=list)
    manual_url: Optional[str] = None
    source_url: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.now)


class BrandInfo(BaseModel):
    """Brand Level Metadata"""
    id: str
    name: str
    official_website: Optional[str] = None
    logo_url: Optional[str] = None
    logo_local_path: Optional[str] = None
    description: Optional[str] = None
    # e.g. {"facebook": "...", "instagram": "..."}
    social_links: Dict[str, str] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)


class Product(BaseModel):
    """Merged Product Entity"""
    id: str  # Internal normalized ID (e.g., 'adam_audio_t5v')
    brand: str
    name: str

    # The two paths
    commercial: VendorData
    technical: TechnicalData

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
