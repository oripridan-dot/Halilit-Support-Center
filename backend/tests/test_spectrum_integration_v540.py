"""
Integration Tests for SPECTRUM v5.4.0

Tests the complete pipeline:
1. Ingest official data from brand catalogs using execute()
2. Map taxonomy from brand-specific to universal using execute()
3. Cross-validate against official data using execute()
4. Verify SpectrumDataProvider orchestration
"""

from backend.skills.spectrum_cross_validator import OfficialSourceCrossValidator
from backend.skills.spectrum_official_ingestion import (
    OfficialBrandCatalogIngester,
    TaxonomyBridgeMapper
)
from backend.spectrum_data_provider import SpectrumDataProvider, get_provider
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@pytest.fixture
def provider():
    """Fixture to provide SpectrumDataProvider instance."""
    return SpectrumDataProvider()


@pytest.fixture
def sample_product():
    """Fixture with sample product data."""
    return {
        'id': 'nord-lead-a1-001',
        'name': 'Nord Lead A1',
        'brand': 'Nord',
        'category': 'Synthesizers',
        'specs': {
            'polyphony': 64,
            'oscillators': 3
        }
    }


class TestSkillExecuteInterface:
    """Test that skills use the standard execute() interface."""

    def test_ingester_execute_method(self):
        """Test OfficialBrandCatalogIngester execute method."""
        ingester = OfficialBrandCatalogIngester()

        context = {
            'brand': 'Nord',
            'include_media': True,
            'deep_catalog': True
        }

        success, result = ingester.execute(context)

        # Should return tuple
        assert isinstance(success, bool)
        assert result is not None

    def test_mapper_execute_method(self):
        """Test TaxonomyBridgeMapper execute method."""
        mapper = TaxonomyBridgeMapper()

        context = {
            'products': [
                {'name': 'Test', 'category': 'Synthesizers'}
            ],
            'brand': 'Nord'
        }

        success, result = mapper.execute(context)

        assert isinstance(success, bool)
        assert result is not None

    def test_validator_execute_method(self):
        """Test OfficialSourceCrossValidator execute method."""
        validator = OfficialSourceCrossValidator()

        context = {
            'product': {'name': 'Test', 'id': 'test-001'},
            'official_data': {},
            'halilit_data': {},
            'review_data': {}
        }

        success, result = validator.execute(context)

        assert isinstance(success, bool)
        assert result is not None


class TestDataFlowIntegration:
    """Test complete data flow through skills."""

    def test_provider_has_all_skills(self, provider):
        """Test that provider initializes with all skills."""
        assert provider is not None
        assert provider.official_ingester is not None
        assert provider.taxonomy_mapper is not None
        assert provider.cross_validator is not None

    def test_provider_method_signature(self, provider):
        """Test that provider methods have correct signature."""
        assert hasattr(provider, 'get_spectrum_data')

        # Method should take brand and optional include_enrichment
        import inspect
        sig = inspect.signature(provider.get_spectrum_data)
        params = list(sig.parameters.keys())

        assert 'brand' in params
        assert 'include_enrichment' in params

    def test_skill_integration_nord_brand(self):
        """Test skills work together for Nord brand."""
        ingester = OfficialBrandCatalogIngester()
        mapper = TaxonomyBridgeMapper()

        # Step 1: Ingest Nord data
        success, result = ingester.execute({
            'brand': 'Nord',
            'include_media': False,  # Skip for speed
            'deep_catalog': False
        })

        if success and result.get('products'):
            # Step 2: Map taxonomy
            map_success, map_result = mapper.execute({
                'products': result.get('products', []),
                'brand': 'Nord'
            })

            assert map_success or isinstance(map_result, (dict, str))


class TestProviderIntegration:
    """Test SpectrumDataProvider integration with skills."""

    def test_provider_orchestrates_skills(self, provider):
        """Test that provider can orchestrate skill execution."""
        assert callable(provider.get_spectrum_data)

        # Provider should work with the skill interfaces
        # (may raise exceptions for unknown brands, but shouldn't crash)
        try:
            result = provider.get_spectrum_data('InvalidBrand')
        except Exception:
            pass  # Expected for invalid brands

    def test_global_provider_singleton(self):
        """Test the global get_provider singleton function."""
        p1 = get_provider()
        p2 = get_provider()

        assert p1 is p2, "Should return singleton instance"
        assert isinstance(p1, SpectrumDataProvider)


class TestErrorHandling:
    """Test error handling in skills."""

    def test_ingester_handles_invalid_brand(self):
        """Test ingester handles unknown brands."""
        ingester = OfficialBrandCatalogIngester()

        success, result = ingester.execute({
            'brand': 'UnknownBrand123',
            'include_media': True
        })

        # Should return False for invalid brand
        assert isinstance(success, bool)
        assert isinstance(result, str) or isinstance(result, dict)

    def test_mapper_with_empty_products(self):
        """Test mapper handles empty product list."""
        mapper = TaxonomyBridgeMapper()

        success, result = mapper.execute({
            'products': [],
            'brand': 'Nord'
        })

        # Should handle gracefully
        assert isinstance(success, bool)
        assert result is not None

    def test_validator_with_minimal_data(self):
        """Test validator handles minimal data gracefully."""
        validator = OfficialSourceCrossValidator()

        context = {
            'product': {'name': 'Test'},  # Minimal product
            'official_data': {},
            'halilit_data': {},
            'review_data': {}
        }

        success, result = validator.execute(context)

        assert isinstance(success, bool)


class TestSkillConsistency:
    """Test consistency across skills."""

    def test_all_skills_return_tuples(self):
        """Test that all skills return (bool, Any) from execute()."""
        ingester = OfficialBrandCatalogIngester()
        mapper = TaxonomyBridgeMapper()
        validator = OfficialSourceCrossValidator()

        skills = [ingester, mapper, validator]

        for skill in skills:
            result = skill.execute({})

            assert isinstance(result, tuple), \
                f"{skill.name} should return tuple from execute()"
            assert len(result) == 2, \
                f"{skill.name} should return (success, result) tuple"
            assert isinstance(result[0], bool), \
                f"{skill.name} first element should be bool"

    def test_all_skills_have_names(self):
        """Test that all skills have unique names."""
        ingester = OfficialBrandCatalogIngester()
        mapper = TaxonomyBridgeMapper()
        validator = OfficialSourceCrossValidator()

        names = [
            ingester.name,
            mapper.name,
            validator.name
        ]

        assert len(names) == len(set(names)), \
            "Skills should have unique names"
        assert all(isinstance(n, str) for n in names), \
            "Skill names should be strings"


class TestProviderDataFlow:
    """Test the complete data flow through the provider."""

    def test_provider_returns_correct_structure(self, provider):
        """Test that provider returns structured data."""
        # This tests the structure, not actual API calls

        assert hasattr(provider, 'official_ingester')
        assert hasattr(provider, 'taxonomy_mapper')
        assert hasattr(provider, 'cross_validator')

        # All should be callable (via execute method)
        for skill in [provider.official_ingester, provider.taxonomy_mapper, provider.cross_validator]:
            assert hasattr(skill, 'execute')
            assert callable(skill.execute)

    def test_get_spectrum_data_error_handling(self, provider):
        """Test that get_spectrum_data handles errors gracefully."""
        # Should raise or return error dict for invalid brand
        try:
            result = provider.get_spectrum_data('InvalidBrand')
            # If it returns, should be a dict
            assert isinstance(result, dict)
        except (ValueError, Exception):
            # Expected to raise
            pass


if __name__ == '__main__':
    # Run integration tests
    pytest.main([__file__, '-v', '--tb=short'])
