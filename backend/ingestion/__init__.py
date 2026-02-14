"""
INGESTION PIPELINE v9.0

Lean package re-exports. Most consumers import directly from sub-modules:
    from backend.ingestion.data_models import IngestionProductDraft
    from backend.ingestion.orchestrator import get_ingestion_orchestrator

Package-level imports kept only for the most common symbols.
"""

# Core data models (frequently referenced)
from backend.ingestion.data_models import (
    IngestionProductDraft,
    IngestionReport,
    IngestionBatch,
    IngestionStatus,
    ProductDraft,  # Legacy compat
)

# Singleton accessors (the primary API)
from backend.ingestion.orchestrator import get_ingestion_orchestrator
from backend.ingestion.spectrum_adapter import get_spectrum_adapter
from backend.ingestion.ingestion_database import get_ingestion_database
from backend.ingestion.taxonomy_manager import get_taxonomy_manager
from backend.ingestion.ai_cache import get_ai_cache
from backend.ingestion.enhanced_pipeline import get_enhanced_pipeline

__all__ = [
    # Models
    "IngestionProductDraft",
    "IngestionReport",
    "IngestionBatch",
    "IngestionStatus",
    "ProductDraft",
    # Accessors
    "get_ingestion_orchestrator",
    "get_spectrum_adapter",
    "get_ingestion_database",
    "get_taxonomy_manager",
    "get_ai_cache",
    "get_enhanced_pipeline",
]
