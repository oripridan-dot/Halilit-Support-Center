"""
INGESTION — JIT Architecture

Lightweight ingestion utilities retained from the original pipeline:
  - data_models: Product data structures
  - taxonomy_manager: Category taxonomy
  - pricing_engine: Pricing logic
  - display_engine: Display preparation
  - halilit_page_scraper: Halilit.com scraper (used by skeleton_sync & JIT agent)
  - ingestion_database: Data persistence
  - guardrails: Data quality rules
"""

from backend.ingestion.data_models import (
    PricingTier,
    DisplayRole,
    IngestionStatus,
    DataSourceConfidence,
    SourceProvenance,
    TaxonomyMapping,
    PricingData,
    MediaAsset,
    DisplayProperties,
    ProductSpecifications,
    IngestionProductDraft,
    IngestionBatch,
    IngestionReport,
    ProductDraft,
    validate_pricing_consistency,
    compute_data_completeness,
)

from backend.ingestion.taxonomy_manager import (
    TaxonomyManager,
    get_taxonomy_manager,
)

from backend.ingestion.pricing_engine import (
    PricingStrategyEngine,
    get_pricing_engine,
)

from backend.ingestion.display_engine import (
    DisplayPreparationEngine,
    get_display_engine,
)

from backend.ingestion.ingestion_database import (
    IngestionDatabase,
    get_ingestion_database,
)

__all__ = [
    'PricingTier', 'DisplayRole', 'IngestionStatus', 'DataSourceConfidence',
    'SourceProvenance', 'TaxonomyMapping', 'PricingData', 'MediaAsset',
    'DisplayProperties', 'ProductSpecifications', 'IngestionProductDraft',
    'IngestionBatch', 'IngestionReport', 'ProductDraft',
    'TaxonomyManager', 'get_taxonomy_manager',
    'PricingStrategyEngine', 'get_pricing_engine',
    'DisplayPreparationEngine', 'get_display_engine',
    'IngestionDatabase', 'get_ingestion_database',
    'validate_pricing_consistency', 'compute_data_completeness',
]
