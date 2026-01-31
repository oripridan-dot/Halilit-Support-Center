"""
Processing Layers Package - Transform raw data into UI-ready JSON.

Layer 1: Normalize - Validate & merge 3 source pillars
Layer 2: Enrich   - Taxonomy mapping & tier assignment  
Layer 3: Optimize - UI constraints & final output
"""

from .normalize import NormalizeLayer
from .enrich import EnrichLayer
from .optimize import OptimizeLayer

__all__ = ["NormalizeLayer", "EnrichLayer", "OptimizeLayer"]
