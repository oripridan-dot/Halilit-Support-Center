from pydantic import BaseModel


class ProcessedBadge(BaseModel):
    brand_id: str
    level: str = "DIAMOND"  # Gold, Silver, Diamond
    checks: dict = {
        "commercial_data": True,      # Price/SKU exists
        "official_manual": True,      # PDF exists
        "taxonomy_aligned": True,     # Fits UI structure perfectly
        "context_layer": True,        # Has "Real World" pros/cons
        "media_optimized": True       # Images are WebP
    }
    signature: str  # Hash of the dataset
