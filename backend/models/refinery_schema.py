from pydantic import BaseModel, HttpUrl, Field, validator
from typing import List, Optional

# --- PILLAR 1: OFFICIAL DATA (The Manufacturer) ---


class OfficialSource(BaseModel):
    """Immutable technical facts."""
    manufacturer_sku: str
    official_name: str
    official_page: HttpUrl
    specs: dict[str, str]  # e.g. {"Freq Response": "20Hz-20kHz"}
    media_assets: dict[str, str]  # e.g. {"manual": "url", "schematic": "url"}

# --- PILLAR 2: COMMERCIAL DATA (The Retailer) ---


class CommercialSource(BaseModel):
    """Market reality (Price & Stock)."""
    local_sku: str
    price_ilr: float
    member_price_ilr: Optional[float]
    stock_status: str  # "IN_STOCK", "PRE_ORDER", "DISCONTINUED"
    delivery_time: str

# --- PILLAR 3: CONTEXTUAL DATA (The Real World) ---


class ReviewSource(BaseModel):
    source_name: str  # e.g. "Sound On Sound"
    url: str
    rating: float  # Normalized 0-100
    date: str


class ContextualSource(BaseModel):
    """The 'Street Knowledge' - AI Synthesized."""
    verified_sources: List[ReviewSource]

    # The Good & The Bad (Summarized from >3 sources)
    pros: List[str] = Field(description="Consensus strengths")
    cons: List[str] = Field(description="Consensus weaknesses")

    # The "Gotchas"
    recurring_issues: List[str] = Field(
        description="e.g. 'Potentiometer scratch after 1 year'")
    expert_tips: List[str] = Field(description="e.g. 'Needs high gain preamp'")

    # Calculated Trust Score
    data_confidence_score: int = Field(ge=0, le=100)
