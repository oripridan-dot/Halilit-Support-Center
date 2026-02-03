"""
ExternalValidator Agent Skills

Capabilities:
- Compliance auditing against rules
- Risk assessment and scoring
- Data consistency validation
- Audit report generation
"""

from typing import Dict, Any, Tuple
from .base_skill import BaseSkill

class ComplianceAuditorSkill(BaseSkill):
    """
    Audits product data against strict compliance rules.
    Returns APPROVED or REJECTED status with detailed violations.
    """

    def __init__(self):
        super().__init__()
        # Compliance rules engine
        self.rules = {
            'price_ratio': {
                'name': 'Price Consistency (Eilat vs IL)',
                'description': 'Eilat price must be ~17% lower than IL price',
                'min_ratio': 0.75,
                'max_ratio': 0.95,
                'severity': 'HIGH',
                'weight': 0.3
            },
            'brand_in_taxonomy': {
                'name': 'Brand Validity',
                'description': 'Brand must be in official taxonomy',
                'severity': 'CRITICAL',
                'weight': 0.4
            },
            'required_fields': {
                'name': 'Data Completeness',
                'description': 'ID, Name, and Image are mandatory',
                'required': ['name', 'brand', 'price_il', 'image_url'],
                'severity': 'CRITICAL',
                'weight': 0.3
            }
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Audit product compliance.

        Context requires:
        - product_data: dict - Product to audit
        - taxonomy: List[str] - Brand taxonomy
        - audit_level: str (optional) - 'strict' or 'standard' (default: 'standard')
        """
        valid, error = self.validate_context(
            context, ['product_data', 'taxonomy'])
        if not valid:
            return False, error

        product_data = context['product_data']
        taxonomy = context['taxonomy']
        audit_level = context.get('audit_level', 'standard')

        self.logger.info(
            f"⚖️  Auditing: {product_data.get('name')} (Level: {audit_level})")

        try:
            violations = []
            risk_score = 0
            audit_results = {}

            # Rule 1: Price Consistency
            price_rule = self.rules['price_ratio']
            price_valid, price_violation = self._check_price_ratio(
                product_data,
                price_rule['min_ratio'],
                price_rule['max_ratio']
            )
            audit_results['price_ratio'] = price_valid
            if not price_valid:
                violations.append(price_violation)
                risk_score += price_rule['weight'] * 100

            # Rule 2: Brand Validity
            brand_rule = self.rules['brand_in_taxonomy']
            brand = product_data.get('brand', '')
            if brand not in taxonomy:
                violations.append(
                    f"Brand '{brand}' not in taxonomy")
                risk_score += brand_rule['weight'] * 100
                audit_results['brand_valid'] = False
            else:
                audit_results['brand_valid'] = True

            # Rule 3: Required Fields
            field_rule = self.rules['required_fields']
            missing_fields = [
                field for field in field_rule['required']
                if field not in product_data or not product_data[field]
            ]
            if missing_fields:
                violations.append(
                    f"Missing required fields: {', '.join(missing_fields)}")
                risk_score += field_rule['weight'] * 100
                audit_results['fields_complete'] = False
            else:
                audit_results['fields_complete'] = True

            # Determine status
            status = 'REJECTED' if violations else 'APPROVED'
            risk_score = min(int(risk_score), 100)

            self.logger.info(
                f"  Status: {status} | Risk: {risk_score}/100 | Violations: {len(violations)}")

            return True, {
                'product_id': product_data.get('id'),
                'product_name': product_data.get('name'),
                'status': status,
                'risk_score': risk_score,
                'violations': violations,
                'audit_results': audit_results,
                'auditor_notes': f"Compliance audit completed at {audit_level} level",
                'is_approvable': status == 'APPROVED'
            }

        except Exception as e:
            error_msg = f"Compliance audit failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def _check_price_ratio(self, product_data: Dict, min_ratio: float, max_ratio: float) -> Tuple[bool, str]:
        """Check if price ratio is within acceptable range"""
        il_price = product_data.get('price_il')
        eilat_price = product_data.get('price_eilat')

        if not il_price or not eilat_price:
            return False, "Missing price data (IL and/or Eilat)"

        if il_price <= 0:
            return False, "Invalid IL price (must be > 0)"

        ratio = eilat_price / il_price
        if not (min_ratio <= ratio <= max_ratio):
            discount = (1 - ratio) * 100
            return False, f"Price ratio out of range: Eilat is {discount:.1f}% cheaper (expected ~17%)"

        return True, ""

class RiskAssessorSkill(BaseSkill):
    """
    Performs comprehensive risk assessment on products.
    Scores products on multiple risk dimensions.
    """

    def __init__(self):
        super().__init__()
        self.risk_dimensions = {
            'data_quality': {
                'weight': 0.25,
                'description': 'Completeness and accuracy of data',
                'factors': ['missing_fields', 'field_consistency', 'data_freshness']
            },
            'source_reliability': {
                'weight': 0.25,
                'description': 'Reliability of data source',
                'factors': ['source_verification', 'historical_accuracy', 'brand_authorization']
            },
            'price_anomalies': {
                'weight': 0.25,
                'description': 'Price consistency checks',
                'factors': ['ratio_consistency', 'market_comparison', 'outlier_detection']
            },
            'compliance_risk': {
                'weight': 0.25,
                'description': 'Regulatory and policy compliance',
                'factors': ['brand_validity', 'territory_restrictions', 'warranty_claims']
            }
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Assess multi-dimensional risk for product.

        Context requires:
        - product_data: dict - Product to assess
        - historical_data: dict (optional) - Historical context for comparison
        """
        valid, error = self.validate_context(context, ['product_data'])
        if not valid:
            return False, error

        product_data = context['product_data']
        historical_data = context.get('historical_data', {})

        self.logger.info(
            f"📊 Assessing risk for: {product_data.get('name')}")

        try:
            risk_scores = {}
            weighted_total = 0

            # Assess each dimension
            for dimension, config in self.risk_dimensions.items():
                dim_score = self._assess_dimension(
                    dimension, product_data, historical_data)
                risk_scores[dimension] = {
                    'score': dim_score,
                    'weight': config['weight'],
                    'weighted_score': dim_score * config['weight']
                }
                weighted_total += risk_scores[dimension]['weighted_score']

            overall_risk = int(weighted_total)
            risk_level = self._classify_risk(overall_risk)

            self.logger.info(
                f"  Overall Risk: {overall_risk}/100 ({risk_level})")

            return True, {
                'overall_risk_score': overall_risk,
                'risk_level': risk_level,
                'dimension_scores': risk_scores,
                'is_approvable': overall_risk <= 40,
                'requires_review': 40 < overall_risk <= 70,
                'is_rejected': overall_risk > 70,
                'risk_summary': f"Product has {risk_level} risk profile"
            }

        except Exception as e:
            error_msg = f"Risk assessment failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def _assess_dimension(self, dimension: str, product_data: Dict, historical_data: Dict) -> int:
        """Score individual risk dimension (0-100)"""
        if dimension == 'data_quality':
            # Higher score = higher risk
            missing_count = sum(1 for field in ['name', 'brand', 'price_il', 'image_url']
                                if field not in product_data or not product_data[field])
            return missing_count * 25
        elif dimension == 'source_reliability':
            # If source URL exists, lower risk
            if 'source_url' in product_data:
                return 20
            else:
                return 60
        elif dimension == 'price_anomalies':
            # Check price consistency
            il = product_data.get('price_il', 0)
            eilat = product_data.get('price_eilat', 0)
            if il > 0 and 0.75 < eilat/il < 0.95:
                return 10
            else:
                return 70
        elif dimension == 'compliance_risk':
            # Basic compliance score
            return 20
        else:
            return 50

    def _classify_risk(self, risk_score: int) -> str:
        """Classify risk level"""
        if risk_score <= 30:
            return 'LOW'
        elif risk_score <= 60:
            return 'MEDIUM'
        else:
            return 'HIGH'

class ConsistencyValidatorSkill(BaseSkill):
    """
    Validates internal data consistency within a product record.
    Detects contradictions or suspicious patterns.
    """

    def __init__(self):
        super().__init__()
        self.consistency_rules = {
            'price_logic': 'eilat_price < il_price',
            'image_format': 'url_starts_with_http and has_image_extension',
            'name_brand_match': 'brand_name_appears_in_product_name_or_related',
            'date_logic': 'harvest_date <= today',
            'numeric_ranges': 'price >= 100 and price <= 500000'
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Validate internal consistency of product data.

        Context requires:
        - product_data: dict - Product to validate
        """
        valid, error = self.validate_context(context, ['product_data'])
        if not valid:
            return False, error

        product_data = context['product_data']

        self.logger.info(
            f"🔍 Validating consistency for: {product_data.get('name')}")

        try:
            inconsistencies = []

            # Check price logic
            il = product_data.get('price_il')
            eilat = product_data.get('price_eilat')
            if il and eilat and il <= eilat:
                inconsistencies.append(
                    f"Price inconsistency: IL price ({il}) should be > Eilat price ({eilat})")

            # Check image URL format
            image_url = product_data.get('image_url', '')
            if image_url and not (image_url.startswith('http') and any(ext in image_url.lower() for ext in ['.jpg', '.png', '.webp'])):
                inconsistencies.append(
                    "Image URL appears invalid (not http/https or no image extension)")

            # Check brand appears in name
            brand = product_data.get('brand', '').lower()
            name = product_data.get('name', '').lower()
            if brand and brand not in name:
                # This is a warning, not necessarily an error
                pass

            # Check numeric ranges
            if il and (il < 100 or il > 500000):
                inconsistencies.append(
                    f"IL price {il} outside reasonable range")

            is_consistent = len(inconsistencies) == 0
            consistency_score = max(0, 100 - len(inconsistencies) * 15)

            self.logger.info(
                f"  Consistency: {'✅ Valid' if is_consistent else '⚠️  Issues found'}")

            return True, {
                'is_consistent': is_consistent,
                'consistency_score': consistency_score,
                'inconsistency_count': len(inconsistencies),
                'inconsistencies': inconsistencies,
                'can_publish': is_consistent
            }

        except Exception as e:
            error_msg = f"Consistency validation failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

class AuditReportGeneratorSkill(BaseSkill):
    """
    Generates comprehensive audit reports from audit results.
    Combines compliance, risk, and consistency findings.
    """

    def __init__(self):
        super().__init__()

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Generate comprehensive audit report.

        Context requires:
        - compliance_result: dict - From ComplianceAuditorSkill
        - risk_result: dict - From RiskAssessorSkill
        - consistency_result: dict - From ConsistencyValidatorSkill
        - product_data: dict - The product being audited
        """
        required = ['compliance_result', 'risk_result',
                    'consistency_result', 'product_data']
        valid, error = self.validate_context(context, required)
        if not valid:
            return False, error

        compliance = context['compliance_result']
        risk = context['risk_result']
        consistency = context['consistency_result']
        product = context['product_data']

        self.logger.info(
            f"📋 Generating audit report for: {product.get('name')}")

        try:
            # Determine final status
            final_status = self._determine_final_status(
                compliance, risk, consistency)

            # Compile all issues
            all_violations = (
                compliance.get('violations', []) +
                consistency.get('inconsistencies', [])
            )

            report = {
                'product_id': product.get('id'),
                'product_name': product.get('name'),
                'final_status': final_status,
                'overall_risk_score': risk.get('overall_risk_score', 0),
                'risk_level': risk.get('risk_level', 'UNKNOWN'),
                'compliance_status': compliance.get('status'),
                'consistency_score': consistency.get('consistency_score', 0),
                'total_violations': len(all_violations),
                'violations': all_violations,
                'critical_issues': [v for v in all_violations if self._is_critical(v)],
                'warnings': [v for v in all_violations if not self._is_critical(v)],
                'recommendation': self._get_recommendation(final_status, risk),
                'audit_timestamp': 'now',
                'auditor_id': 'ExternalValidator',
                'report_summary': {
                    'compliance': compliance.get('status'),
                    'risk': risk.get('risk_level'),
                    'consistency': 'VALID' if consistency.get('is_consistent') else 'INVALID',
                    'final_action': final_status
                }
            }

            self.logger.info(f"  Report: {final_status}")
            return True, report

        except Exception as e:
            error_msg = f"Report generation failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def _determine_final_status(self, compliance: Dict, risk: Dict, consistency: Dict) -> str:
        """Determine final audit decision"""
        if not compliance.get('is_approvable'):
            return 'REJECTED'
        if risk.get('is_rejected'):
            return 'REJECTED'
        if not consistency.get('is_consistent'):
            return 'NEEDS_REVIEW'
        if risk.get('requires_review'):
            return 'NEEDS_REVIEW'
        if compliance.get('is_approvable') and consistency.get('can_publish') and risk.get('is_approvable'):
            return 'APPROVED'
        return 'NEEDS_REVIEW'

    def _is_critical(self, violation: str) -> bool:
        """Determine if violation is critical"""
        critical_keywords = ['missing', 'invalid',
                             'not in taxonomy', 'inconsistency']
        return any(keyword in violation.lower() for keyword in critical_keywords)

    def _get_recommendation(self, status: str, risk: Dict) -> str:
        """Get action recommendation"""
        if status == 'APPROVED':
            return '✅ APPROVE - Product meets all requirements'
        elif status == 'REJECTED':
            return '🛑 REJECT - Critical issues must be resolved'
        else:
            return f"⚠️  REVIEW REQUIRED - Risk level: {risk.get('risk_level')}"
