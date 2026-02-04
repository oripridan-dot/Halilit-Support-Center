"""
SpectrumValidator Skill

Comprehensive validation for spectrum data:
- Data quality gates
- Price consistency checks
- Source credibility verification
- Data provenance validation
"""

import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
from .base_skill import BaseSkill

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SpectrumValidator")


class SpectrumValidator(BaseSkill):
    """
    Multi-stage validation pipeline for spectrum screen data.
    Enforces data quality gates and provenance tracking.
    """

    def __init__(self):
        super().__init__()
        self.name = "SpectrumValidator"

        # Validation rules
        self.rules = {
            'halilit_price_required': {
                'description': 'Halilit price is mandatory',
                'severity': 'CRITICAL',
                'weight': 1.0
            },
            'price_consistency': {
                'description': 'Eilat price should be ~15-20% lower than IL price',
                'severity': 'HIGH',
                'weight': 0.8,
                'min_ratio': 0.75,
                'max_ratio': 0.95
            },
            'product_name_quality': {
                'description': 'Product name must be descriptive (>3 chars)',
                'severity': 'CRITICAL',
                'weight': 1.0,
                'min_length': 3
            },
            'brand_consistency': {
                'description': 'Brand must match taxonomy',
                'severity': 'HIGH',
                'weight': 0.8
            },
            'source_credibility': {
                'description': 'At least one credible source must be present',
                'severity': 'MEDIUM',
                'weight': 0.6
            },
            'data_provenance': {
                'description': 'All data must have provenance tracking',
                'severity': 'MEDIUM',
                'weight': 0.5
            }
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Validate spectrum data payload.

        Context requires:
        - payload: Dict - Spectrum data to validate
        - brand_taxonomy: List[str] - Valid brands
        """
        valid, error = self.validate_context(
            context, ['payload', 'brand_taxonomy'])
        if not valid:
            return False, error

        payload = context['payload']
        brand_taxonomy = context['brand_taxonomy']

        logger.info(
            f"🔍 Validating spectrum data for {payload.get('brand')}...")

        try:
            validation_results = {
                'passed': True,
                'errors': [],
                'warnings': [],
                'quality_score': 100,
                'products_validated': 0,
                'products_rejected': 0,
                'details': {}
            }

            # Validate each track
            tracks = payload.get('tracks', [])

            for track_idx, track in enumerate(tracks):
                track_results = self._validate_track(
                    track, brand_taxonomy, payload.get('brand'))

                validation_results['products_validated'] += track_results['products_validated']
                validation_results['products_rejected'] += track_results['products_rejected']
                validation_results['quality_score'] = min(
                    validation_results['quality_score'],
                    track_results['quality_score']
                )

                if track_results['errors']:
                    validation_results['passed'] = False
                    validation_results['errors'].extend(
                        track_results['errors'])

                validation_results['warnings'].extend(
                    track_results['warnings'])
                validation_results['details'][f'track_{track_idx}'] = track_results

            # Calculate final quality score
            validation_results['quality_score'] = max(
                0, validation_results['quality_score'])

            return validation_results['passed'], validation_results

        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return False, {
                'passed': False,
                'errors': [f"Validation exception: {str(e)}"],
                'quality_score': 0
            }

    def _validate_track(self, track: Dict, taxonomy: List[str], brand: str) -> Dict:
        """Validate a single price track."""
        results = {
            'tier': track.get('tier'),
            'products_validated': 0,
            'products_rejected': 0,
            'quality_score': 100,
            'errors': [],
            'warnings': [],
            'product_results': []
        }

        products = track.get('products', [])

        for product in products:
            product_result = self._validate_product(product, taxonomy, brand)
            results['product_results'].append(product_result)

            if product_result['valid']:
                results['products_validated'] += 1
            else:
                results['products_rejected'] += 1
                results['passed'] = False

            if product_result['warnings']:
                results['warnings'].extend(product_result['warnings'])

            # Reduce quality score based on issues
            results['quality_score'] -= product_result.get('penalty', 0)

        results['quality_score'] = max(0, results['quality_score'])
        return results

    def _validate_product(self, product: Dict, taxonomy: List[str], brand: str) -> Dict:
        """Validate a single product."""
        result = {
            'product_id': product.get('halilit_id', 'UNKNOWN'),
            'valid': True,
            'errors': [],
            'warnings': [],
            'penalty': 0,
            'rule_results': {}
        }

        # Rule 1: Halilit Price Required
        if not product.get('price_il'):
            result['valid'] = False
            result['errors'].append('Missing Halilit price (price_il)')
            result['rule_results']['halilit_price_required'] = False
            result['penalty'] += 10
        else:
            result['rule_results']['halilit_price_required'] = True

        # Rule 2: Price Consistency
        price_il = product.get('price_il', 0)
        price_eilat = product.get('price_eilat', 0)

        if price_il > 0 and price_eilat > 0:
            ratio = price_eilat / price_il
            min_ratio = self.rules['price_consistency']['min_ratio']
            max_ratio = self.rules['price_consistency']['max_ratio']

            if not (min_ratio <= ratio <= max_ratio):
                result['warnings'].append(
                    f"Suspicious price ratio: Eilat/IL = {ratio:.2f} "
                    f"(expected {min_ratio}-{max_ratio})"
                )
                result['rule_results']['price_consistency'] = False
                result['penalty'] += 5
            else:
                result['rule_results']['price_consistency'] = True
        else:
            result['rule_results']['price_consistency'] = None  # N/A

        # Rule 3: Product Name Quality
        name = product.get('name', '')
        if len(name) < self.rules['product_name_quality']['min_length']:
            result['valid'] = False
            result['errors'].append(f'Product name too short: "{name}"')
            result['rule_results']['product_name_quality'] = False
            result['penalty'] += 10
        else:
            result['rule_results']['product_name_quality'] = True

        # Rule 4: Brand Consistency
        if brand not in taxonomy:
            result['warnings'].append(f'Brand "{brand}" not in taxonomy')
            result['rule_results']['brand_consistency'] = False
            result['penalty'] += 3
        else:
            result['rule_results']['brand_consistency'] = True

        # Rule 5: Source Credibility
        sources = product.get('sources', [])
        has_credible_source = any(
            s in ['halilit_direct', 'official_specs'] for s in sources
        )

        if not has_credible_source:
            result['warnings'].append('No credible source found')
            result['rule_results']['source_credibility'] = False
            result['penalty'] += 3
        else:
            result['rule_results']['source_credibility'] = True

        # Rule 6: Data Provenance
        provenance = product.get('data_provenance')
        if not provenance:
            result['warnings'].append('Missing data provenance information')
            result['rule_results']['data_provenance'] = False
            result['penalty'] += 2
        else:
            result['rule_results']['data_provenance'] = True

        return result


class DataProvenanceTracker(BaseSkill):
    """
    Tracks data lineage and source attribution.
    Enables users to see exactly where each piece of data came from.
    """

    def __init__(self):
        super().__init__()
        self.name = "DataProvenanceTracker"

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Track provenance for a product.

        Context requires:
        - product: Dict - Product to track
        """
        valid, error = self.validate_context(context, ['product'])
        if not valid:
            return False, error

        product = context['product']

        try:
            provenance = self._build_provenance_record(product)

            return True, {
                'product_id': product.get('halilit_id'),
                'provenance': provenance,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return False, f"Provenance tracking failed: {str(e)}"

    def _build_provenance_record(self, product: Dict) -> Dict:
        """Build comprehensive provenance record."""
        return {
            'halilit': {
                'source': 'Halilit.com Commerce API',
                'field_mapping': {
                    'product_id': 'halilit_id',
                    'name': 'Product name from Halilit',
                    'price_il': 'Israeli mainland price',
                    'price_eilat': 'Eilat zone price',
                    'image_url': 'Halilit product image'
                },
                'confidence': 0.95,
                'last_updated': product.get('halilit_updated_at')
            },
            'official_sources': {
                'sources': product.get('official_specs', {}).get('source'),
                'fields': ['specifications', 'features', 'technical_details'],
                'confidence': 0.90,
                'last_updated': product.get('official_updated_at')
            },
            'trusted_reviews': {
                'sources': product.get('review_data', {}).get('sources', []),
                'fields': ['rating', 'reviews_count', 'pros', 'cons'],
                'confidence': 0.85,
                'last_updated': product.get('reviews_updated_at')
            }
        }


class QualityReportGenerator(BaseSkill):
    """
    Generates data quality reports for the Conductor.
    Provides actionable insights for data improvement.
    """

    def __init__(self):
        super().__init__()
        self.name = "QualityReportGenerator"

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Generate quality report for a spectrum dataset.

        Context requires:
        - validation_results: Dict - From SpectrumValidator
        - brand: str - Brand name
        """
        valid, error = self.validate_context(
            context, ['validation_results', 'brand'])
        if not valid:
            return False, error

        validation_results = context['validation_results']
        brand = context['brand']

        try:
            report = {
                'brand': brand,
                'generated_at': datetime.utcnow().isoformat(),
                'summary': self._generate_summary(validation_results),
                'recommendations': self._generate_recommendations(validation_results),
                'metrics': self._calculate_metrics(validation_results)
            }

            return True, report

        except Exception as e:
            return False, f"Report generation failed: {str(e)}"

    def _generate_summary(self, results: Dict) -> Dict:
        """Generate executive summary."""
        return {
            'overall_quality': results.get('quality_score', 0),
            'total_products_validated': results.get('products_validated', 0),
            'products_rejected': results.get('products_rejected', 0),
            'critical_errors': len([e for e in results.get('errors', [])]),
            'warnings': len(results.get('warnings', []))
        }

    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if results.get('quality_score', 0) < 80:
            recommendations.append(
                "Quality score below 80%. Review and fix critical errors first.")

        if len(results.get('errors', [])) > 0:
            recommendations.append(
                f"{len(results.get('errors', []))} critical errors found. "
                "These products should not be displayed until fixed.")

        if len(results.get('warnings', [])) > 5:
            recommendations.append(
                "Multiple warnings detected. Consider data enrichment strategies.")

        return recommendations

    def _calculate_metrics(self, results: Dict) -> Dict:
        """Calculate key metrics."""
        total = results.get('products_validated', 0) + \
            results.get('products_rejected', 0)

        return {
            'validation_rate': (results.get('products_validated', 0) / total * 100) if total > 0 else 0,
            'approval_percentage': (results.get('products_validated', 0) / total * 100) if total > 0 else 0,
            'error_density': len(results.get('errors', [])) / max(total, 1),
            'quality_trend': 'improving' if results.get('quality_score', 0) > 80 else 'needs_attention'
        }
