"""
Halilit Support Center - Unified Data Pipeline v5.0

Single entry point for all data processing:
  python -m backend.pipeline [ingest|process|deploy|run]

Three Data Sources:
  1. OFFICIAL   - Manufacturer specs, names, taxonomy, media (the truth)
  2. COMMERCIAL - Halilit prices, SKUs, stock status (the market)  
  3. CONTEXTUAL - Expert reviews, pros/cons, tips (the wisdom)

Three Processing Layers:
  1. NORMALIZE - Validate & structure raw data (Pydantic schemas)
  2. ENRICH    - Taxonomy mapping, tier assignment, visual metadata
  3. OPTIMIZE  - UI-ready JSON with component constraints

Output: Static JSON files in frontend/public/data/
"""

__version__ = "5.0.0"
__all__ = [
    "run_pipeline",
    "ingest_sources",
    "process_layers",
    "deploy_catalog",
]

from .runner import run_pipeline, ingest_sources, process_layers, deploy_catalog
