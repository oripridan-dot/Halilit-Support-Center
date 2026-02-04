"""
Unit Tests for SPECTRUM v5.4.0 Integration

Tests the three core skills:
1. OfficialBrandCatalogIngester - Official source ingestion
2. TaxonomyBridgeMapper - Category mapping
3. OfficialSourceCrossValidator - Data validation
"""

from backend.skills.spectrum_cross_validator import OfficialSourceCrossValidator
from backend.skills.spectrum_official_ingestion import (
    OfficialBrandCatalogIngester,
    TaxonomyBridgeMapper
)
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestOfficialBrandCatalogIngester:
    """Test suite for OfficialBrandCatalogIngester skill."""

    def test_initialization(self):
        """Test that OfficialBrandCatalogIngester initializes properly."""
        ingester = OfficialBrandCatalogIngester()
        assert ingester is not None
        assert ingester.name == "OfficialBrandCatalogIngester"
        assert hasattr(ingester, 'brand_catalogs')

    def test_brand_catalogs_not_empty(self):
        """Test that brand catalogs are populated."""
        ingester = OfficialBrandCatalogIngester()
        assert len(ingester.brand_catalogs) > 0

    def test_some_major_brands_supported(self):
        """Test that major brands are in the catalog."""
        ingester = OfficialBrandCatalogIngester()
        brands = list(ingester.brand_catalogs.keys())

        # At least some major brands should be present
        major_brands_present = any(brand in brands for brand in [
                                   'Nord', 'Moog', 'Roland'])
        assert major_brands_present, "No major synthesizer brands found in catalogs"

    def test_brand_catalog_has_endpoints(self):
        """Test that brand catalogs have API endpoints defined."""
        ingester = OfficialBrandCatalogIngester()

        for brand, catalog in list(ingester.brand_catalogs.items())[:3]:
            assert isinstance(
                catalog, dict), f"{brand} catalog should be a dict"
            assert len(catalog) > 0, f"{brand} catalog should have properties"


class TestTaxonomyBridgeMapper:
    """Test suite for TaxonomyBridgeMapper skill."""

    def test_initialization(self):
        """Test that TaxonomyBridgeMapper initializes properly."""
        mapper = TaxonomyBridgeMapper()
        assert mapper is not None
        assert mapper.name == "TaxonomyBridgeMapper"
        assert hasattr(mapper, 'execute')

    def test_mapper_has_methods(self):
        """Test that mapper has expected methods."""
        mapper = TaxonomyBridgeMapper()

        # Should have at least the execute method from BaseSkill
        assert callable(mapper.execute)

    def test_mapper_can_process_context(self):
        """Test that mapper can process context."""
        mapper = TaxonomyBridgeMapper()

        # Should be able to handle a context dict
        context = {
            'category': 'Synthesizers',
            'brand': 'Nord'
        }

        success, result = mapper.execute(context)
        # Should return a tuple of (success, result)
        assert isinstance(success, bool)
        assert result is not None


class TestOfficialSourceCrossValidator:
    """Test suite for OfficialSourceCrossValidator skill."""

    def test_initialization(self):
        """Test that OfficialSourceCrossValidator initializes properly."""
        validator = OfficialSourceCrossValidator()
        assert validator is not None
        assert validator.name == "OfficialSourceCrossValidator"
        assert hasattr(validator, 'validation_rules')

    def test_validation_rules_exist(self):
        """Test that validation rules are defined."""
        validator = OfficialSourceCrossValidator()

        # Should have multiple validation rules
        rules = validator.validation_rules
        assert len(rules) > 0, "No validation rules defined"

    def test_rule_structure_valid(self):
        """Test that validation rules have expected structure."""
        validator = OfficialSourceCrossValidator()

        for rule_name, rule in list(validator.validation_rules.items())[:5]:
            # Each rule should be a dict with severity
            assert isinstance(rule, dict), f"Rule {rule_name} should be a dict"
            assert 'severity' in rule, f"Rule {rule_name} missing severity"

            valid_severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
            assert rule['severity'] in valid_severities, \
                f"Invalid severity in rule {rule_name}: {rule['severity']}"

    def test_has_critical_rules(self):
        """Test that there are CRITICAL validation rules."""
        validator = OfficialSourceCrossValidator()

        critical_rules = [
            rule for rule in validator.validation_rules.values()
            if rule.get('severity') == 'CRITICAL'
        ]

        assert len(critical_rules) > 0, "No CRITICAL rules found"


class TestIntegrationAcrossSkills:
    """Test integration and data flow between skills."""

    def test_all_skills_importable(self):
        """Test that all three skills can be imported together."""
        from backend.skills.spectrum_official_ingestion import (
            OfficialBrandCatalogIngester,
            TaxonomyBridgeMapper
        )
        from backend.skills.spectrum_cross_validator import OfficialSourceCrossValidator

        ingester = OfficialBrandCatalogIngester()
        mapper = TaxonomyBridgeMapper()
        validator = OfficialSourceCrossValidator()

        assert all([ingester, mapper, validator])

    def test_skill_names_are_unique(self):
        """Test that each skill has a unique name."""
        ingester = OfficialBrandCatalogIngester()
        mapper = TaxonomyBridgeMapper()
        validator = OfficialSourceCrossValidator()

        skill_names = [ingester.name, mapper.name, validator.name]
        assert len(skill_names) == len(set(skill_names)), \
            "Skills must have unique names"

    def test_all_skills_have_execute_method(self):
        """Test that all skills implement the execute method."""
        ingester = OfficialBrandCatalogIngester()
        mapper = TaxonomyBridgeMapper()
        validator = OfficialSourceCrossValidator()

        for skill in [ingester, mapper, validator]:
            assert hasattr(
                skill, 'execute'), f"{skill.name} missing execute method"
            assert callable(
                skill.execute), f"{skill.name}.execute is not callable"

    def test_provider_initialization(self):
        """Test that SpectrumDataProvider can initialize with v5.4.0 skills."""
        from backend.spectrum_data_provider import SpectrumDataProvider

        provider = SpectrumDataProvider()

        assert provider is not None
        assert hasattr(provider, 'official_ingester')
        assert hasattr(provider, 'taxonomy_mapper')
        assert hasattr(provider, 'cross_validator')

        assert isinstance(provider.official_ingester,
                          OfficialBrandCatalogIngester)
        assert isinstance(provider.taxonomy_mapper, TaxonomyBridgeMapper)
        assert isinstance(provider.cross_validator,
                          OfficialSourceCrossValidator)


class TestProviderMethods:
    """Test SpectrumDataProvider methods."""

    def test_provider_has_get_spectrum_data_method(self):
        """Test that provider has the get_spectrum_data method."""
        from backend.spectrum_data_provider import SpectrumDataProvider

        provider = SpectrumDataProvider()
        assert hasattr(provider, 'get_spectrum_data')
        assert callable(provider.get_spectrum_data)

    def test_get_provider_singleton(self):
        """Test the get_provider singleton function."""
        from backend.spectrum_data_provider import get_provider, SpectrumDataProvider

        provider1 = get_provider()
        provider2 = get_provider()

        assert isinstance(provider1, SpectrumDataProvider)
        assert provider1 is provider2, "get_provider should return singleton"


if __name__ == '__main__':
    # Run all tests
    pytest.main([__file__, '-v', '--tb=short'])
