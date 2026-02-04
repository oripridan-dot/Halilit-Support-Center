"""
Spectrum Data Provider - Backend routes for enhanced spectrum screen

Serves enriched, validated spectrum data with:
- Price-organized tracks
- Multi-source enrichment (official + reviews)
- Data provenance tracking
- Quality metrics
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import logging

# Import SPECTRUM v5.4.0 skills
from backend.skills.spectrum_official_ingestion import (
    OfficialBrandCatalogIngester,
    TaxonomyBridgeMapper
)
from backend.skills.spectrum_cross_validator import OfficialSourceCrossValidator

logger = logging.getLogger("SpectrumDataProvider")

# ============================================================================
# DATA MODELS
# ============================================================================


class ProvenanceInfo(BaseModel):
    """Data provenance information"""
    halilit: Dict[str, Any]
    official_sources: Optional[Dict[str, Any]] = None
    trusted_reviews: Optional[Dict[str, Any]] = None


class DataSourceInfo(BaseModel):
    """Information about a data source"""
    source_name: str
    confidence: float
    url: str
    last_updated: Optional[str] = None


class SpecProduct(BaseModel):
    """Product in Spectrum Track"""
    halilit_id: str
    name: str
    brand: str
    category: str
    price_il: float
    price_eilat: float

    # Data from various sources
    official_specs: Optional[Dict[str, Any]] = None
    review_data: Optional[Dict[str, Any]] = None
    official_images: Optional[List[Dict]] = None

    # Provenance
    data_provenance: ProvenanceInfo
    sources: List[str]

    # Quality
    quality_score: float = 100.0
    validation_status: str = "APPROVED"  # APPROVED, REVIEW_PENDING, REJECTED


class PriceTrack(BaseModel):
    """Price tier track"""
    tier: str
    tier_label: str
    price_range: tuple  # (min, max)
    products: List[SpecProduct]
    product_count: int


class SpectrumDataPayload(BaseModel):
    """Complete spectrum data response"""
    brand: str
    timestamp: str
    total_products: int
    tracks: List[PriceTrack]
    metadata: Dict[str, Any]


class QualityReport(BaseModel):
    """Data quality report"""
    brand: str
    generated_at: str
    overall_quality_score: float
    total_products: int
    approved_products: int
    rejected_products: int
    critical_errors: List[str]
    warnings: List[str]
    recommendations: List[str]


# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/api/spectrum", tags=["spectrum"])


# ============================================================================
# SPECTRUM DATA PROVIDER CLASS
# ============================================================================

class SpectrumDataProvider:
    """
    Main provider class for SPECTRUM v5.4.0 data operations.
    Orchestrates official ingestion, taxonomy mapping, and validation.
    """

    def __init__(self):
        """Initialize SPECTRUM v5.4.0 skills."""
        logger.info("🚀 Initializing SpectrumDataProvider with v5.4.0 skills...")

        # Initialize v5.4.0 skills
        self.official_ingester = OfficialBrandCatalogIngester()
        self.taxonomy_mapper = TaxonomyBridgeMapper()
        self.cross_validator = OfficialSourceCrossValidator()

        logger.info("✅ SpectrumDataProvider initialized with 3 core skills")

    def get_spectrum_data(self, brand: str, include_enrichment: bool = True) -> Dict[str, Any]:
        """
        Get complete spectrum data with official sources as primary.

        Args:
            brand: Brand name (e.g., 'Nord', 'Moog')
            include_enrichment: Include official specs and reviews

        Returns:
            Dict with official_data, quality_report, and source_priority
        """
        try:
            logger.info(f"📊 Getting spectrum data for {brand}...")

            # Step 1: Ingest official data using the execute method
            ingestion_success, ingestion_result = self.official_ingester.execute({
                'brand': brand,
                'include_media': include_enrichment,
                'deep_catalog': True
            })

            if not ingestion_success:
                raise ValueError(
                    f"Failed to ingest data for {brand}: {ingestion_result}")

            official_data = ingestion_result.get('products', [])

            # Step 2: Apply taxonomy mapping using the execute method
            mapping_success, mapping_result = self.taxonomy_mapper.execute({
                'products': official_data,
                'brand': brand
            })

            if mapping_success:
                mapped_data = mapping_result.get('products', official_data)
            else:
                mapped_data = official_data

            # Step 3: Cross-validate using the execute method
            validation_success, validation_results = self.cross_validator.execute({
                'products': mapped_data,
                'official_data': ingestion_result,
                'brand': brand
            })

            return {
                "brand": brand,
                "official_data": mapped_data,
                "quality_report": validation_results if validation_success else {},
                "source_priority": ["official", "halilit", "reviews"],
                "timestamp": str(__import__('datetime').datetime.utcnow())
            }

        except Exception as e:
            logger.error(f"Error getting spectrum data: {str(e)}")
            raise

# ============================================================================
# GLOBAL PROVIDER INSTANCE
# ============================================================================


_provider: Optional[SpectrumDataProvider] = None


def get_provider() -> SpectrumDataProvider:
    """Get or create the global SpectrumDataProvider instance."""
    global _provider
    if _provider is None:
        _provider = SpectrumDataProvider()
    return _provider


# ============================================================================
# ROUTER ENDPOINTS
# ============================================================================


@router.get("/data/{brand}")
async def get_spectrum_data(
    brand: str,
    include_enrichment: bool = Query(
        True, description="Include official specs and reviews"),
    force_refresh: bool = Query(
        False, description="Skip cache and refresh data")
) -> SpectrumDataPayload:
    """
    Get complete spectrum data for a brand with all enrichments.

    Returns products organized by price tier (entry -> mid -> pro -> flagship)
    with data from Halilit (prices/IDs), official sources (specs/images),
    and trusted reviews (ratings/sentiment).

    SPECTRUM v5.4.0 Integration:
    - Step 1: Ingest official data (OfficialBrandCatalogIngester)
    - Step 2: Map taxonomy (TaxonomyBridgeMapper)
    - Step 3: Cross-validate (OfficialSourceCrossValidator)
    """
    logger.info(f"📊 Fetching spectrum data for {brand}...")

    try:
        # Get provider instance and use new v5.4.0 skills
        provider = get_provider()
        data_result = provider.get_spectrum_data(brand, include_enrichment)

        # For now, return the data as-is (can be enhanced with price tier organization)
        return SpectrumDataPayload(
            brand=data_result['brand'],
            timestamp=data_result['timestamp'],
            total_products=len(data_result['official_data']),
            tracks=[],  # TODO: Organize by price tiers
            metadata={
                "source_priority": data_result['source_priority'],
                "quality_report": data_result['quality_report'],
                "v5_4_0_integration": True
            }
        )

    except Exception as e:
        logger.error(f"Error fetching spectrum data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/product/{product_id}")
async def get_product_details(product_id: str) -> SpecProduct:
    """
    Get detailed information for a specific product.
    Includes all enrichment data and provenance.
    """
    logger.info(f"🔍 Fetching details for product {product_id}...")

    try:
        # In production, load from database
        # For now, return template
        return SpecProduct(
            halilit_id=product_id,
            name="Product Name",
            brand="Brand",
            category="Category",
            price_il=5000.0,
            price_eilat=4250.0,
            official_specs={
                'polyphony': 64,
                'connectivity': ['MIDI', 'USB']
            },
            review_data={
                'average_rating': 4.7,
                'review_count': 45
            },
            data_provenance=ProvenanceInfo(
                halilit={'id': product_id, 'price': 5000.0},
                official_sources={'specs': {}},
                trusted_reviews={'rating': 4.7}
            ),
            sources=['halilit_direct', 'official_specs', 'trusted_reviews'],
            quality_score=95.0,
            validation_status="APPROVED"
        )

    except Exception as e:
        logger.error(f"Error fetching product details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality/{brand}")
async def get_quality_report(brand: str) -> Dict[str, Any]:
    """
    Get quality validation report for all products in a brand.
    SPECTRUM v5.4.0: Uses OfficialSourceCrossValidator with 10 validation checks.
    """
    logger.info(f"📋 Getting quality report for {brand}...")

    try:
        provider = get_provider()

        # Get official data
        official_data = provider.official_ingester.ingest_brand_catalog(brand)
        if not official_data:
            return {
                "error": f"No official data found for {brand}",
                "brand": brand
            }

        # Generate quality report
        quality_report = provider.cross_validator.generate_quality_report(
            official_data)

        return {
            "brand": brand,
            "generated_at": str(__import__('datetime').datetime.utcnow()),
            "total_products": len(official_data),
            "quality_score": quality_report.get('overall_score', 0),
            "checks_passed": quality_report.get('checks_passed', 0),
            "checks_failed": quality_report.get('checks_failed', 0),
            "validation_checks": quality_report.get('validation_checks', []),
            "discrepancies": quality_report.get('discrepancies', []),
            "recommendations": quality_report.get('recommendations', [])
        }

    except Exception as e:
        logger.error(f"Error getting quality report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/taxonomy")
async def get_taxonomy_mapping() -> Dict[str, Any]:
    """
    Get taxonomy mapping across all brands.
    SPECTRUM v5.4.0: Shows universal taxonomy and brand-specific mappings.
    """
    logger.info("🏷️  Getting taxonomy mapping...")

    try:
        provider = get_provider()

        # Get complete mapping
        mapping = provider.taxonomy_mapper.get_complete_mapping()

        return {
            "universal_categories": mapping.get('universal', []),
            "brand_taxonomies": mapping.get('brands', {}),
            "mappings": mapping.get('mappings', {}),
            "generated_at": str(__import__('datetime').datetime.utcnow())
        }

    except Exception as e:
        logger.error(f"Error getting taxonomy mapping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality-report/{brand}")
async def get_quality_report(brand: str) -> QualityReport:
    """
    Get data quality report for a brand.
    Shows validation results and recommendations.
    """
    logger.info(f"📋 Generating quality report for {brand}...")

    try:
        from backend.skills.spectrum_validator import QualityReportGenerator
        from backend.skills.spectrum_data_pipeline import SpectrumDataPipeline

        # Get data first
        pipeline = SpectrumDataPipeline()
        success, payload = pipeline.execute({
            'brand': brand,
            'include_enrichment': True
        })

        if not success:
            raise HTTPException(status_code=400, detail="Failed to fetch data")

        # Validate and generate report
        from backend.skills.spectrum_validator import SpectrumValidator
        validator = SpectrumValidator()
        valid, validation_results = validator.execute({
            'payload': payload,
            'brand_taxonomy': ['Nord', 'Moog', 'Roland', 'Yamaha', 'Korg', 'Universal-Audio']
        })

        generator = QualityReportGenerator()
        report_success, report = generator.execute({
            'validation_results': validation_results,
            'brand': brand
        })

        if not report_success:
            raise HTTPException(
                status_code=500, detail="Report generation failed")

        return QualityReport(
            brand=brand,
            generated_at=report.get('generated_at'),
            overall_quality_score=validation_results.get('quality_score', 0),
            total_products=validation_results.get('products_validated', 0) +
            validation_results.get('products_rejected', 0),
            approved_products=validation_results.get('products_validated', 0),
            rejected_products=validation_results.get('products_rejected', 0),
            critical_errors=validation_results.get('errors', []),
            warnings=validation_results.get('warnings', []),
            recommendations=report.get('recommendations', [])
        )

    except Exception as e:
        logger.error(f"Error generating quality report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources/{brand}")
async def get_data_sources(brand: str) -> Dict[str, List[DataSourceInfo]]:
    """
    Get information about all data sources for a brand's products.
    Shows where each piece of data comes from.
    """
    logger.info(f"🔗 Fetching data sources for {brand}...")

    sources = {
        'halilit': [
            DataSourceInfo(
                source_name='Halilit Commerce API',
                confidence=0.98,
                url='https://halilit.com',
                last_updated=None
            )
        ],
        'official': [
            DataSourceInfo(
                source_name='Manufacturer Official Site',
                confidence=0.95,
                url=f'https://official.{brand.lower()}.com',
                last_updated=None
            )
        ],
        'trusted_reviews': [
            DataSourceInfo(
                source_name='Thomann',
                confidence=0.90,
                url='https://www.thomann.de',
                last_updated=None
            ),
            DataSourceInfo(
                source_name='Sweetwater',
                confidence=0.90,
                url='https://www.sweetwater.com',
                last_updated=None
            ),
            DataSourceInfo(
                source_name='Reverb',
                confidence=0.85,
                url='https://reverb.com',
                last_updated=None
            )
        ]
    }

    return sources


@router.post("/rebuild/{brand}")
async def rebuild_spectrum_data(
    brand: str,
    deep_refresh: bool = Query(
        False, description="Force deep refresh of all sources")
) -> Dict[str, Any]:
    """
    Rebuild and refresh spectrum data for a brand.
    Used by Conductor to update data after changes.
    """
    logger.info(f"🔄 Rebuilding spectrum data for {brand}...")

    try:
        from backend.skills.spectrum_data_pipeline import SpectrumDataPipeline
        from backend.skills.spectrum_validator import SpectrumValidator

        pipeline = SpectrumDataPipeline()
        success, result = pipeline.execute({
            'brand': brand,
            'include_enrichment': True,
            'force_refresh': deep_refresh
        })

        if not success:
            raise HTTPException(
                status_code=400, detail=f"Rebuild failed: {result}")

        # Validate
        validator = SpectrumValidator()
        valid, validation_results = validator.execute({
            'payload': result,
            'brand_taxonomy': ['Nord', 'Moog', 'Roland', 'Yamaha', 'Korg', 'Universal-Audio']
        })

        return {
            'status': 'success',
            'brand': brand,
            'total_products': result.get('total_products'),
            'quality_score': validation_results.get('quality_score'),
            'validation_passed': validation_results.get('passed'),
            'timestamp': result.get('timestamp')
        }

    except Exception as e:
        logger.error(f"Error rebuilding spectrum data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# INTEGRATION HELPER
# ============================================================================

def attach_spectrum_router(app):
    """Attach spectrum router to FastAPI app"""
    app.include_router(router)
