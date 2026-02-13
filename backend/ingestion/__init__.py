"""
INGESTION PIPELINE v8.5

High-level imports for the complete refactored ingestion system.

Usage:
    from backend.ingestion import get_ingestion_orchestrator
    
    orchestrator = get_ingestion_orchestrator()
    report = orchestrator.ingest_batch('Nord', raw_products)
"""

from backend.ingestion.data_models import (
    # Enums
    PricingTier,
    DisplayRole,
    IngestionStatus,
    DataSourceConfidence,

    # Models
    SourceProvenance,
    TaxonomyMapping,
    PricingData,
    MediaAsset,
    DisplayProperties,
    ProductSpecifications,
    IngestionProductDraft,
    IngestionBatch,
    IngestionReport,

    # Legacy compatibility
    ProductDraft,

    # Helpers
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

from backend.ingestion.orchestrator import (
    IngestionOrchestrator,
    get_ingestion_orchestrator,
)

from backend.ingestion.spectrum_adapter import (
    SpectrumAdapter,
    SpecProduct,
    PriceTrack,
    SpectrumPayload,
    QualityReport,
    get_spectrum_adapter,
)

from backend.ingestion.ingestion_database import (
    IngestionDatabase,
    get_ingestion_database,
)

# Enhanced pipeline components (v2.0)
from backend.ingestion.enhanced_harvester import (
    EnhancedHarvester,
    FingerprintStore,
    RateLimiter,
    RetryConfig,
    HarvestResult,
    get_enhanced_harvester,
)

from backend.ingestion.cross_validator import (
    CrossValidator,
    CrossValidationResult,
    ValidationIssue,
    get_cross_validator,
)

from backend.ingestion.image_processor import (
    ImageProcessor,
    ImageVariant,
    ImageProcessingResult,
    get_image_processor,
)

from backend.ingestion.diff_publisher import (
    DiffPublisher,
    PublishDiff,
    PublishResult,
    get_diff_publisher,
)

from backend.ingestion.pipeline_telemetry import (
    PipelineTelemetry,
    PhaseMetrics,
    PipelineRun,
    get_pipeline_telemetry,
)

from backend.ingestion.ai_cache import (
    AIResponseCache,
    get_ai_cache,
)

from backend.ingestion.enhanced_pipeline import (
    EnhancedPipeline,
    get_enhanced_pipeline,
)

__all__ = [
    # Data Models
    'PricingTier',
    'DisplayRole',
    'IngestionStatus',
    'DataSourceConfidence',
    'SourceProvenance',
    'TaxonomyMapping',
    'PricingData',
    'MediaAsset',
    'DisplayProperties',
    'ProductSpecifications',
    'IngestionProductDraft',
    'IngestionBatch',
    'IngestionReport',
    'ProductDraft',

    # Taxonomy
    'TaxonomyManager',
    'get_taxonomy_manager',

    # Pricing
    'PricingStrategyEngine',
    'get_pricing_engine',

    # Display
    'DisplayPreparationEngine',
    'get_display_engine',

    # Orchestration
    'IngestionOrchestrator',
    'get_ingestion_orchestrator',

    # Spectrum Adapter
    'SpectrumAdapter',
    'SpecProduct',
    'PriceTrack',
    'SpectrumPayload',
    'QualityReport',
    'get_spectrum_adapter',

    # Database
    'IngestionDatabase',
    'get_ingestion_database',

    # Enhanced Harvester
    'EnhancedHarvester',
    'FingerprintStore',
    'RateLimiter',
    'RetryConfig',
    'HarvestResult',
    'get_enhanced_harvester',

    # Cross-Validator
    'CrossValidator',
    'CrossValidationResult',
    'ValidationIssue',
    'get_cross_validator',

    # Image Processor
    'ImageProcessor',
    'ImageVariant',
    'ImageProcessingResult',
    'get_image_processor',

    # Diff Publisher
    'DiffPublisher',
    'PublishDiff',
    'PublishResult',
    'get_diff_publisher',

    # Pipeline Telemetry
    'PipelineTelemetry',
    'PhaseMetrics',
    'PipelineRun',
    'get_pipeline_telemetry',

    # AI Cache
    'AIResponseCache',
    'get_ai_cache',

    # Enhanced Pipeline
    'EnhancedPipeline',
    'get_enhanced_pipeline',

    # Helpers
    'validate_pricing_consistency',
    'compute_data_completeness',
]
