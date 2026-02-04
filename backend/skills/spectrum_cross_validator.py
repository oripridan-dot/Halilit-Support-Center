"""
SpectrumCrossCheckValidator Skill

Advanced validation using official sources as the ground truth.
Cross-validates all data sources against official manufacturer data.
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from .base_skill import BaseSkill

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SpectrumCrossCheckValidator")


class OfficialSourceCrossValidator(BaseSkill):
    """
    Uses official manufacturer data as ground truth to validate and cross-check
    all other data sources (Halilit prices, review sites, community data).
    """

    def __init__(self):
        super().__init__()
        self.name = "OfficialSourceCrossValidator"

        # Validation rules for cross-checking
        self.validation_rules = {
            'product_name': {
                'severity': 'CRITICAL',
                'source': 'official',
                'tolerance': 0.0,
                'rule': 'Must match official name exactly'
            },
            'model_number': {
                'severity': 'CRITICAL',
                'source': 'official',
                'tolerance': 0.0,
                'rule': 'Must match official model number'
            },
            'specifications': {
                'severity': 'HIGH',
                'source': 'official',
                'tolerance': 0.05,  # 5% deviation allowed
                'rule': 'Must match official specs within tolerance'
            },
            'official_price': {
                'severity': 'MEDIUM',
                'source': 'official',
                'tolerance': 0.20,  # 20% deviation allowed
                'rule': 'MSRP should be within 20% of official'
            },
            'halilit_price': {
                'severity': 'MEDIUM',
                'source': 'halilit',
                'tolerance': 0.30,  # 30% deviation allowed
                'rule': 'Actual prices can vary by 30% from MSRP'
            },
            'product_category': {
                'severity': 'HIGH',
                'source': 'official',
                'tolerance': 0.0,
                'rule': 'Must be in official category taxonomy'
            },
            'images': {
                'severity': 'MEDIUM',
                'source': 'official',
                'tolerance': 0.5,
                'rule': 'Should have official images'
            },
            'warranty': {
                'severity': 'HIGH',
                'source': 'official',
                'tolerance': 0.0,
                'rule': 'Must match official warranty terms'
            },
            'availability': {
                'severity': 'MEDIUM',
                'source': 'official',
                'tolerance': 0.1,
                'rule': 'Must match official availability status'
            }
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Cross-validate product data against official sources.

        Context requires:
        - product: Dict - Product to validate
        - official_data: Dict - Official manufacturer data
        - halilit_data: Dict - Halilit price/stock data (optional)
        - review_data: Dict - Review aggregation data (optional)
        """
        product = context.get('product')
        official_data = context.get('official_data')
        halilit_data = context.get('halilit_data', {})
        review_data = context.get('review_data', {})

        if not product or not official_data:
            return False, "Missing required product or official data"

        logger.info(
            f"🔍 Cross-validating {product.get('name')} against official sources...")

        try:
            validation_result = self._perform_cross_check(
                product,
                official_data,
                halilit_data,
                review_data
            )

            return True, validation_result

        except Exception as e:
            logger.error(f"Cross-validation failed: {str(e)}")
            return False, str(e)

    def _perform_cross_check(
        self,
        product: Dict,
        official_data: Dict,
        halilit_data: Dict,
        review_data: Dict
    ) -> Dict:
        """Perform comprehensive cross-validation."""

        checks = {
            'name_check': self._check_product_name(product, official_data),
            'model_check': self._check_model_number(product, official_data),
            'specs_check': self._check_specifications(product, official_data),
            'price_check': self._check_pricing(product, official_data, halilit_data),
            'category_check': self._check_category(product, official_data),
            'images_check': self._check_images(product, official_data),
            'warranty_check': self._check_warranty(product, official_data),
            'availability_check': self._check_availability(product, official_data, halilit_data),
            'review_consistency_check': self._check_review_consistency(product, review_data),
            'data_completeness_check': self._check_completeness(product, official_data)
        }

        # Calculate overall quality score
        quality_score = self._calculate_quality_score(checks)

        # Identify discrepancies
        discrepancies = self._extract_discrepancies(checks)

        # Generate reconciliation recommendations
        recommendations = self._generate_recommendations(
            discrepancies, official_data)

        return {
            'product_id': product.get('id'),
            'validation_timestamp': datetime.utcnow().isoformat(),
            'all_checks': checks,
            'quality_score': quality_score,  # 0-100
            'passed': quality_score >= 70,
            'discrepancies': discrepancies,
            'recommendations': recommendations,
            'source_priority': self._determine_source_priority(checks)
        }

    def _check_product_name(
        self,
        product: Dict,
        official_data: Dict
    ) -> Dict:
        """Check if product name matches official name."""
        product_name = product.get('name', '').strip().lower()
        official_name = official_data.get('official_name', '').strip().lower()

        match = product_name == official_name

        return {
            'rule': 'product_name',
            'passed': match,
            'product_value': product.get('name'),
            'official_value': official_data.get('official_name'),
            'severity': 'CRITICAL',
            'message': f"{'✅' if match else '❌'} Product name {'matches' if match else 'does not match'} official",
            'confidence': 1.0 if match else 0.0
        }

    def _check_model_number(
        self,
        product: Dict,
        official_data: Dict
    ) -> Dict:
        """Check if model number matches official model."""
        product_model = product.get('model_number', '').strip().upper()
        official_model = official_data.get('model_number', '').strip().upper()

        match = product_model == official_model

        return {
            'rule': 'model_number',
            'passed': match,
            'product_value': product.get('model_number'),
            'official_value': official_data.get('model_number'),
            'severity': 'CRITICAL',
            'message': f"{'✅' if match else '❌'} Model number {'matches' if match else 'does not match'} official",
            'confidence': 1.0 if match else 0.0
        }

    def _check_specifications(
        self,
        product: Dict,
        official_data: Dict
    ) -> Dict:
        """Cross-check specifications."""
        product_specs = product.get('specifications', {})
        official_specs = official_data.get('specifications_normalized', {})

        discrepancies = []
        matching_specs = 0
        total_specs = 0

        for key, official_value in official_specs.items():
            product_value = product_specs.get(key)
            total_specs += 1

            if product_value == official_value:
                matching_specs += 1
            else:
                discrepancies.append({
                    'spec': key,
                    'product': product_value,
                    'official': official_value
                })

        match_percentage = (matching_specs / total_specs *
                            100) if total_specs > 0 else 0
        passed = match_percentage >= 80  # 80% specs must match

        return {
            'rule': 'specifications',
            'passed': passed,
            'matching_specs': matching_specs,
            'total_specs': total_specs,
            'match_percentage': match_percentage,
            'severity': 'HIGH',
            'discrepancies': discrepancies,
            'message': f"{'✅' if passed else '⚠️'} Specs match {match_percentage:.1f}%",
            'confidence': min(1.0, match_percentage / 100)
        }

    def _check_pricing(
        self,
        product: Dict,
        official_data: Dict,
        halilit_data: Dict
    ) -> Dict:
        """Cross-check pricing between official and Halilit."""
        official_price = official_data.get('price_official_usd')
        halilit_price = halilit_data.get('price_halilit')
        product_price = product.get('price')

        pricing_checks = {
            'official_price': official_price,
            'halilit_price': halilit_price,
            'product_price': product_price
        }

        # Calculate price variance
        price_variance = 'N/A'
        variance_percentage = 0

        if official_price and halilit_price:
            variance_percentage = abs(
                halilit_price - official_price) / official_price * 100
            price_variance = f"{variance_percentage:.1f}%"

        # Check if variance is within tolerance (30%)
        within_tolerance = variance_percentage <= 30

        return {
            'rule': 'pricing',
            'passed': within_tolerance or not halilit_price,
            'official_price': official_price,
            'halilit_price': halilit_price,
            'product_price': product_price,
            'variance_percentage': variance_percentage,
            'variance_tolerance': 30,
            'severity': 'MEDIUM',
            'message': f"Price variance: {price_variance} {'✅ within' if within_tolerance else '⚠️ exceeds'} tolerance",
            'confidence': 1.0 - min(1.0, variance_percentage / 100)
        }

    def _check_category(
        self,
        product: Dict,
        official_data: Dict
    ) -> Dict:
        """Check if category is in official taxonomy."""
        product_category = product.get('category')
        official_category = official_data.get('category')
        official_taxonomy = official_data.get('subcategories', [])

        # Check if category matches
        category_matches = product_category == official_category

        # Check if in allowed subcategories
        in_taxonomy = product_category in official_taxonomy or category_matches

        return {
            'rule': 'category',
            'passed': in_taxonomy,
            'product_category': product_category,
            'official_category': official_category,
            'allowed_categories': official_taxonomy,
            'severity': 'HIGH',
            'message': f"{'✅' if in_taxonomy else '❌'} Category {'valid' if in_taxonomy else 'invalid'} in official taxonomy",
            'confidence': 1.0 if in_taxonomy else 0.0
        }

    def _check_images(
        self,
        product: Dict,
        official_data: Dict
    ) -> Dict:
        """Check if official images are present."""
        product_images = product.get('media', {}).get('images', [])
        official_images = official_data.get('media', {}).get('images', [])

        has_images = len(product_images) > 0
        has_official_images = len(official_images) > 0

        image_count = len(product_images)
        official_count = len(official_images)

        return {
            'rule': 'images',
            'passed': has_official_images,
            'product_images': image_count,
            'official_images': official_count,
            'severity': 'MEDIUM',
            'message': f"{'✅' if has_official_images else '⚠️'} Official images {'present' if has_official_images else 'missing'}",
            'confidence': 1.0 if has_official_images else 0.5
        }

    def _check_warranty(
        self,
        product: Dict,
        official_data: Dict
    ) -> Dict:
        """Cross-check warranty information."""
        product_warranty = product.get('warranty_years')
        official_warranty = official_data.get('warranty_years')

        match = product_warranty == official_warranty

        return {
            'rule': 'warranty',
            'passed': match,
            'product_warranty': product_warranty,
            'official_warranty': official_warranty,
            'severity': 'HIGH',
            'message': f"{'✅' if match else '⚠️'} Warranty {'matches' if match else 'differs from'} official",
            'confidence': 1.0 if match else 0.5
        }

    def _check_availability(
        self,
        product: Dict,
        official_data: Dict,
        halilit_data: Dict
    ) -> Dict:
        """Check product availability status."""
        official_status = official_data.get('status', 'active')
        halilit_stock = halilit_data.get('stock_status', 'in_stock')

        # Consistency check
        status_consistent = (
            (official_status == 'active' and halilit_stock == 'in_stock') or
            (official_status == 'discontinued' and halilit_stock == 'out_of_stock')
        )

        return {
            'rule': 'availability',
            'passed': status_consistent,
            'official_status': official_status,
            'halilit_stock': halilit_stock,
            'severity': 'MEDIUM',
            'message': f"{'✅' if status_consistent else '⚠️'} Status {'consistent' if status_consistent else 'inconsistent'}",
            'confidence': 1.0 if status_consistent else 0.7
        }

    def _check_review_consistency(
        self,
        product: Dict,
        review_data: Dict
    ) -> Dict:
        """Check review data consistency."""
        if not review_data:
            return {
                'rule': 'review_consistency',
                'passed': True,
                'message': 'No review data to validate',
                'severity': 'LOW'
            }

        aggregate_rating = review_data.get('aggregate_rating', 0)
        review_count = review_data.get('total_reviews', 0)

        # Reviews are consistent if rating is reasonable
        rating_valid = 1.0 <= aggregate_rating <= 5.0

        return {
            'rule': 'review_consistency',
            'passed': rating_valid and review_count > 0,
            'aggregate_rating': aggregate_rating,
            'review_count': review_count,
            'severity': 'LOW',
            'message': f"{'✅' if rating_valid else '⚠️'} Reviews {'valid' if rating_valid else 'invalid'}",
            # More reviews = higher confidence
            'confidence': min(1.0, review_count / 100)
        }

    def _check_completeness(
        self,
        product: Dict,
        official_data: Dict
    ) -> Dict:
        """Check data completeness."""
        required_fields = [
            'name', 'model_number', 'category', 'price_official_usd',
            'specifications', 'warranty_years'
        ]

        official_complete = sum(
            1 for field in required_fields if official_data.get(field))
        product_complete = sum(
            1 for field in required_fields if product.get(field))

        official_percentage = (official_complete / len(required_fields)) * 100
        product_percentage = (product_complete / len(required_fields)) * 100

        return {
            'rule': 'data_completeness',
            'passed': official_percentage >= 90 and product_percentage >= 80,
            'official_completeness': official_percentage,
            'product_completeness': product_percentage,
            'severity': 'MEDIUM',
            'message': f"Official: {official_percentage:.0f}%, Product: {product_percentage:.0f}%",
            'confidence': min(official_percentage / 100, product_percentage / 100)
        }

    def _calculate_quality_score(self, checks: Dict[str, Any]) -> int:
        """Calculate overall quality score 0-100."""
        total_score = 0
        total_weight = 0

        # Weight each check
        weights = {
            'name_check': 15,
            'model_check': 15,
            'specs_check': 20,
            'price_check': 15,
            'category_check': 15,
            'images_check': 5,
            'warranty_check': 10,
            'availability_check': 5,
            'review_consistency_check': 5,
            'data_completeness_check': 10
        }

        for check_name, check_result in checks.items():
            weight = weights.get(check_name, 5)
            confidence = check_result.get('confidence', 0)
            total_score += confidence * weight
            total_weight += weight

        return int((total_score / total_weight * 100) if total_weight > 0 else 0)

    def _extract_discrepancies(self, checks: Dict[str, Any]) -> List[Dict]:
        """Extract all discrepancies from checks."""
        discrepancies = []

        for check_name, check_result in checks.items():
            if not check_result.get('passed'):
                discrepancies.append({
                    'check': check_name,
                    'severity': check_result.get('severity'),
                    'message': check_result.get('message'),
                    'details': {
                        k: v for k, v in check_result.items()
                        if k not in ['rule', 'passed', 'severity', 'message', 'confidence']
                    }
                })

        return discrepancies

    def _generate_recommendations(
        self,
        discrepancies: List[Dict],
        official_data: Dict
    ) -> List[Dict]:
        """Generate recommendations based on discrepancies."""
        recommendations = []

        for discrepancy in discrepancies:
            check = discrepancy['check']

            if check == 'name_check':
                recommendations.append({
                    'priority': 'CRITICAL',
                    'action': 'Use official name',
                    'official_value': official_data.get('official_name')
                })

            elif check == 'category_check':
                recommendations.append({
                    'priority': 'HIGH',
                    'action': 'Recategorize to official category',
                    'official_value': official_data.get('category')
                })

            elif check == 'specs_check':
                recommendations.append({
                    'priority': 'HIGH',
                    'action': 'Sync specifications with official',
                    'note': 'Update mismatched specs from official source'
                })

            elif check == 'price_check':
                recommendations.append({
                    'priority': 'MEDIUM',
                    'action': 'Verify pricing accuracy',
                    'note': f"MSRP: {official_data.get('price_official_usd')}"
                })

            elif check == 'images_check':
                recommendations.append({
                    'priority': 'MEDIUM',
                    'action': 'Add official product images',
                    'note': 'Use high-resolution official images'
                })

        return recommendations

    def _determine_source_priority(self, checks: Dict[str, Any]) -> Dict:
        """Determine priority order for data sources."""
        return {
            'primary': 'official_manufacturer',
            'secondary': 'halilit',
            'tertiary': 'reviews',
            'community': 'gearspace',
            'rationale': 'Official sources are ground truth, validated by other sources'
        }
