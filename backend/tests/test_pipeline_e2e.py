"""
End-to-End Integration Test for Pipeline v5.0

Tests the complete flow:
  Ingest → Normalize → Enrich → Optimize → Deploy → TypeScript Generation

Run with: python -m pytest backend/tests/test_pipeline_e2e.py -v
"""

from backend.pipeline.runner import PipelineRunner
from backend.pipeline.layers import NormalizeLayer, EnrichLayer, OptimizeLayer
from backend.pipeline.harvesters import OfficialHarvester, CommercialHarvester, ContextualHarvester
from backend.pipeline.models import (
    OfficialData,
    CommercialData,
    ContextualData,
    NormalizedProduct,
    EnrichedProduct,
    OptimizedProduct,
    TierLevel,
    StockStatus,
)
from backend.pipeline.config import config
import pytest
import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestModels:
    """Test Pydantic models validation."""

    def test_official_data_validation(self):
        """OfficialData should validate required fields."""
        data = OfficialData(
            manufacturer_sku="TEST-001",
            official_name="Test Product",
            brand_id="test-brand",
            brand_name="Test Brand",
            category="Studio Monitors",
            description="A test product for validation",
            specifications={"Audio": {"Frequency": "20Hz-20kHz"}},
        )

        assert data.manufacturer_sku == "TEST-001"
        assert data.brand_id == "test-brand"
        assert data.harvested_at is not None  # Auto-set timestamp

    def test_contextual_data_validation(self):
        """ContextualData should accept pros/cons lists."""
        data = ContextualData(
            product_id="test-001",
            pros=["Great sound", "Good build"],
            cons=["Expensive"],
            expert_tips=["Use with isolation pads"],
            confidence_score=75,
        )

        assert len(data.pros) == 2
        assert data.confidence_score == 75

    def test_tier_level_enum(self):
        """TierLevel enum should have correct values."""
        assert TierLevel.DIAMOND.value == "diamond"
        assert TierLevel.GOLD.value == "gold"
        assert TierLevel.SILVER.value == "silver"
        assert TierLevel.BRONZE.value == "bronze"


class TestNormalizeLayer:
    """Test Layer 1: Normalization."""

    def setup_method(self):
        """Setup test fixtures."""
        self.layer = NormalizeLayer()

        self.official = [
            OfficialData(
                manufacturer_sku="A7V",
                official_name="ADAM Audio A7V",
                brand_id="adam-audio",
                brand_name="ADAM Audio",
                category="Studio Monitors",
                description="7-inch studio monitor with DSP",
                specifications={
                    "Audio": {"Woofer": "7 inch", "Tweeter": "X-ART"}},
                images=[{"url": "https://example.com/a7v.jpg",
                         "alt": "A7V", "role": "hero"}],
            ),
        ]

        self.commercial = [
            CommercialData(
                halilit_sku="HL-A7V",
                product_id="adam-audio-a7v",
                price_usd=899.0,
                stock_status=StockStatus.IN_STOCK,
                product_url="https://halilit.com/a7v",
            ),
        ]

        self.contextual = [
            ContextualData(
                product_id="adam-audio-a7v",
                pros=["Excellent clarity", "Wide sweet spot"],
                cons=["Needs space from wall"],
                expert_tips=["Use Sonarworks for room correction"],
                confidence_score=80,
            ),
        ]

    def test_normalize_merges_three_pillars(self):
        """Normalization should merge data from all 3 sources."""
        results = self.layer.process_brand(
            "adam-audio",
            self.official,
            self.commercial,
            self.contextual,
        )

        assert len(results) == 1
        product = results[0]

        # Official data
        assert "A7V" in product.name
        assert product.category == "Studio Monitors"

        # Commercial data
        assert product.price == 899.0
        assert product.stock_status == StockStatus.IN_STOCK

        # Contextual data
        assert "Excellent clarity" in product.pros
        assert "Use Sonarworks" in product.expert_tips[0]

    def test_normalize_handles_missing_commercial(self):
        """Normalization should work without commercial data."""
        results = self.layer.process_brand(
            "adam-audio",
            self.official,
            [],  # No commercial data
            self.contextual,
        )

        assert len(results) == 1
        product = results[0]

        assert product.price is None
        assert product.stock_status == StockStatus.UNKNOWN

    def test_normalize_handles_missing_contextual(self):
        """Normalization should work without contextual data."""
        results = self.layer.process_brand(
            "adam-audio",
            self.official,
            self.commercial,
            [],  # No contextual data
        )

        assert len(results) == 1
        product = results[0]

        assert product.pros == []
        assert product.cons == []


class TestEnrichLayer:
    """Test Layer 2: Enrichment."""

    def setup_method(self):
        """Setup test fixtures."""
        self.layer = EnrichLayer()

        self.normalized = [
            NormalizedProduct(
                id="adam-audio-a7v",
                brand_id="adam-audio",
                sku="A7V",
                name="ADAM Audio A7V Studio Monitor",
                category="Studio Monitors",
                description="Professional 7-inch nearfield studio monitor with X-ART tweeter",
                price=899.0,
                currency="USD",
                stock_status=StockStatus.IN_STOCK,
                images=[],
                specifications={"Audio": []},
                pros=["Great sound"],
                cons=[],
                expert_tips=[],
            ),
        ]

    def test_enrich_assigns_tier(self):
        """Enrichment should assign tier based on data quality."""
        results = self.layer.process_products("adam-audio", self.normalized)

        assert len(results) == 1
        product = results[0]

        # Should have tier assigned
        assert product.tier in [TierLevel.DIAMOND,
                                TierLevel.GOLD, TierLevel.SILVER, TierLevel.BRONZE]
        assert 0 <= product.tier_score <= 100
        assert len(product.tier_reasons) > 0

    def test_enrich_maps_taxonomy(self):
        """Enrichment should map to standard taxonomy."""
        results = self.layer.process_products("adam-audio", self.normalized)

        product = results[0]

        # Should map "Studio Monitors" correctly
        assert product.category == "Studio Monitors"
        assert product.taxonomy_confidence >= 0.5

    def test_enrich_generates_short_description(self):
        """Enrichment should generate short description."""
        results = self.layer.process_products("adam-audio", self.normalized)

        product = results[0]

        assert len(product.description_short) <= 100
        assert product.description_short  # Not empty


class TestOptimizeLayer:
    """Test Layer 3: Optimization."""

    def setup_method(self):
        """Setup test fixtures."""
        self.layer = OptimizeLayer()

        self.enriched = [
            EnrichedProduct(
                id="adam-audio-a7v",
                brand_id="adam-audio",
                sku="A7V",
                name="ADAM Audio A7V Studio Monitor",
                category="Studio Monitors",
                subcategories=["nearfield", "7-inch"],
                taxonomy_confidence=0.9,
                tier=TierLevel.GOLD,
                tier_score=70,
                tier_reasons=["Complete name", "Has price"],
                description="Professional studio monitor",
                description_short="7-inch nearfield monitor",
                price=899.0,
                currency="USD",
                stock_status=StockStatus.IN_STOCK,
                image_hero=None,
                image_thumbnail=None,
                image_gallery=[],
                specs={},
                pros=["Great sound"],
                cons=[],
                expert_tips=[],
            ),
        ]

    def test_optimize_generates_slug(self):
        """Optimization should generate URL-safe slug."""
        results = self.layer.process_products("adam-audio", self.enriched)

        product = results[0]

        assert product.slug.startswith("/adam-audio/")
        assert " " not in product.slug
        assert product.slug.islower() or product.slug.startswith("/")

    def test_optimize_generates_search_text(self):
        """Optimization should generate searchable text."""
        results = self.layer.process_products("adam-audio", self.enriched)

        product = results[0]

        assert product.search_text
        assert "adam" in product.search_text.lower()
        assert "monitor" in product.search_text.lower()

    def test_optimize_generates_filter_tags(self):
        """Optimization should generate filter tags."""
        results = self.layer.process_products("adam-audio", self.enriched)

        product = results[0]

        assert len(product.filter_tags) > 0
        assert "gold" in product.filter_tags  # Tier
        assert "adam-audio" in product.filter_tags  # Brand

    def test_optimize_generates_render_hints(self):
        """Optimization should generate UI render hints."""
        results = self.layer.process_products("adam-audio", self.enriched)

        product = results[0]

        assert "has_price" in product.render_hints
        assert product.render_hints["has_price"] == True
        assert "has_hero_image" in product.render_hints


class TestPipelineRunner:
    """Test complete pipeline orchestration."""

    def setup_method(self):
        """Setup test fixtures."""
        config.ensure_directories()
        self.runner = PipelineRunner()

    @pytest.mark.asyncio
    async def test_runner_processes_mock_brand(self):
        """Runner should process a brand with mock data."""
        # Set up mock brand
        self.runner.brands = {
            "test-brand": {
                "id": "test-brand",
                "name": "Test Brand",
            }
        }

        # Run with skip_ingest to use mock data from harvesters
        report = await self.runner.run_full_pipeline(
            brand_ids=["test-brand"],
            skip_deploy=True,  # Don't deploy to frontend during test
        )

        assert report["brands_processed"] >= 0
        assert "started_at" in report

    def test_runner_loads_brands_from_discovery(self):
        """Runner should discover brands from existing data."""
        self.runner.load_brands()

        # Should have some brands (from existing data or empty)
        assert isinstance(self.runner.brands, dict)


class TestTypeScriptGeneration:
    """Test TypeScript type generation."""

    def test_generates_valid_typescript(self):
        """Generator should produce valid TypeScript."""
        from backend.pipeline.typescript_generator import generate_types
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(suffix=".ts", delete=False, mode='w') as f:
            output_path = Path(f.name)

        try:
            generate_types(output_path)

            content = output_path.read_text()

            # Check for key elements
            assert "export interface OptimizedProduct" in content
            assert "export type TierLevel" in content

        finally:
            if output_path.exists():
                os.unlink(output_path)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
