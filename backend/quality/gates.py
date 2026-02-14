"""
Security & Quality Gates — All gate classes.
Split from unified_quality_gates.py Section 3.
"""

import re
import logging
from typing import Dict, List, Tuple, Any

from backend.quality.models import GateStatus, GateCheckResult

logger = logging.getLogger(__name__)


class InputValidationGate:
    """Sanitizes and validates inputs before processing."""

    @staticmethod
    def validate_product(product: Dict[str, Any]) -> GateCheckResult:
        violations, warnings = [], []
        checks_passed, checks_total = 0, 6

        if not isinstance(product, dict):
            violations.append(
                f"Product is not a dictionary (got {type(product).__name__})")
        else:
            checks_passed += 1

        for field in ['product_name', 'brand', 'price_il', 'halilit_id']:
            if field not in product or not product[field]:
                violations.append(f"Missing required field: {field}")
            else:
                checks_passed += 1

        try:
            price = float(product.get('price_il', 0))
            if price < 0:
                violations.append("Price is negative")
            elif price == 0:
                warnings.append("Price is zero (might be TBD)")
            else:
                checks_passed += 1
        except (ValueError, TypeError):
            violations.append(f"Price is not a number")

        name = product.get('product_name', '')
        if len(name) < 3:
            violations.append("Product name too short (< 3 chars)")
        elif len(name) > 500:
            violations.append("Product name too long (> 500 chars)")
        else:
            checks_passed += 1

        return GateCheckResult(
            gate_name="InputValidation",
            status=GateStatus.BLOCKED if violations else GateStatus.PASSED,
            checks_passed=checks_passed, checks_total=checks_total,
            violations=violations, warnings=warnings,
            recommendations=["Add missing fields",
                             "Verify price information"] if violations else [],
        )


class SecurityGate:
    """Checks for PII, malicious code, and suspicious patterns."""

    PII_PATTERNS = {
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "ip_address": r"\b(?:192\.168|10\.|172\.1[6-9]|172\.2[0-9]|172\.3[01])\.\d{1,3}\.\d{1,3}\b",
        "internal_id": r"(?i)(internal_id|ref_id|employee_id|account_\w+)[:=\s]+[\w\d-]+",
    }

    MALICIOUS_PATTERNS = {
        "script": r"<script[^>]*>.*?</script>",
        "javascript": r"javascript:",
        "onclick": r"on\w+\s*=",
        "sql_injection": r"(union|select|insert|delete|drop)[\s\n]+(from|into|where|table)",
        "xss": r"<(iframe|object|embed|img)[^>]*on\w+",
    }

    @staticmethod
    def check_pii(text: str) -> Tuple[bool, List[str]]:
        if not isinstance(text, str):
            return False, []
        detected = []
        for name, pattern in SecurityGate.PII_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(f"PII_detected: {name}")
        return len(detected) > 0, detected

    @staticmethod
    def check_malicious(text: str) -> Tuple[bool, List[str]]:
        if not isinstance(text, str):
            return False, []
        detected = []
        for name, pattern in SecurityGate.MALICIOUS_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                detected.append(f"malicious_{name}")
        return len(detected) > 0, detected

    @staticmethod
    def check_product_security(product: Dict[str, Any]) -> GateCheckResult:
        violations, warnings = [], []
        checks_passed, checks_total = 0, 5
        product_text = str(product).lower()

        has_pii, pii = SecurityGate.check_pii(product_text)
        if has_pii:
            violations.append(f"PII detected: {', '.join(pii)}")
        else:
            checks_passed += 1

        is_mal, mal = SecurityGate.check_malicious(product_text)
        if is_mal:
            violations.append(f"Malicious code detected: {', '.join(mal)}")
        else:
            checks_passed += 1

        if re.search(r"(?i)(password|api_?key|secret|token)[\s:=]+\S+", product_text):
            violations.append("Potential credential exposure detected")
        else:
            checks_passed += 1

        brand = product.get('brand', '')
        if not brand or len(brand) < 2 or len(brand) > 100:
            warnings.append("Brand name suspicious or missing")
        else:
            checks_passed += 1

        price = product.get('price_il', 0)
        if isinstance(price, (int, float)):
            if price < 10 or price > 1000000:
                warnings.append("Price seems unrealistic")
            else:
                checks_passed += 1

        return GateCheckResult(
            gate_name="Security",
            status=GateStatus.BLOCKED if violations else (
                GateStatus.WARNING if warnings else GateStatus.PASSED),
            checks_passed=checks_passed, checks_total=checks_total,
            violations=violations, warnings=warnings,
            recommendations=["Remove PII",
                             "Verify brand"] if violations else [],
        )


class DataIntegrityGate:
    """Verifies data structure and completeness."""

    @staticmethod
    def check_integrity(product: Dict[str, Any],
                        required_fields: List[str] = None) -> GateCheckResult:
        if required_fields is None:
            required_fields = {'product_name', 'brand', 'price_il',
                               'halilit_id', 'display', 'pricing', 'taxonomy'}

        violations, warnings = [], []
        checks_passed, checks_total = 0, 6

        missing = [f for f in required_fields if f not in product]
        if missing:
            violations.append(f"Missing fields: {', '.join(missing)}")
        else:
            checks_passed += 1

        images = product.get('official_images', [])
        if isinstance(images, list):
            if not images:
                warnings.append("No official images available")
            else:
                checks_passed += 1
        else:
            violations.append(f"Images field is not a list")

        taxonomy = product.get('taxonomy') or {}
        if isinstance(taxonomy, dict):
            checks_passed += 1
        else:
            violations.append(f"Taxonomy is not a dict")

        display = product.get('display', {})
        if isinstance(display, dict):
            checks_passed += 1
        else:
            violations.append(f"Display is not a dict")

        pricing = product.get('pricing', {})
        if isinstance(pricing, dict):
            if 'price_il' not in pricing:
                warnings.append("Pricing missing price_il field")
            else:
                checks_passed += 1
        else:
            violations.append(f"Pricing is not a dict")

        name1 = product.get('product_name', '')
        if name1:
            checks_passed += 1

        return GateCheckResult(
            gate_name="DataIntegrity",
            status=GateStatus.BLOCKED if violations else (
                GateStatus.WARNING if warnings else GateStatus.PASSED),
            checks_passed=checks_passed, checks_total=checks_total,
            violations=violations, warnings=warnings,
            recommendations=["Normalize data structure"] if violations else [],
        )


class ComplianceGate:
    """Checks compliance with business rules."""

    @staticmethod
    def check_compliance(product: Dict[str, Any]) -> GateCheckResult:
        violations, warnings = [], []
        checks_passed, checks_total = 0, 4

        price = product.get('price_il', 0)
        if isinstance(price, (int, float)):
            if price < 50:
                violations.append("Price below minimum (< 50 NIS)")
            elif price > 500000:
                violations.append("Price exceeds maximum (> 500,000 NIS)")
            else:
                checks_passed += 1

        brand = product.get('brand', '').lower()
        if len(brand) > 2:
            checks_passed += 1
        else:
            warnings.append("Brand too short")

        category = product.get('taxonomy', {}).get('canonical_category', '')
        valid_categories = [
            'Amplifiers & Effects', 'Audio Interfaces & Mixers',
            'Drums & Percussion', 'Headphones & Earphones',
            'Keyboards & Synthesizers', 'Microphones & Recording',
            'Studio Monitors & Speakers', 'Other',
        ]
        if category in valid_categories:
            checks_passed += 1
        else:
            warnings.append(f"Category '{category}' not in approved list")

        name = product.get('product_name', '')
        has_images = len(product.get('official_images', [])) > 0
        has_specs = bool(product.get('official_specs'))
        quality_score = sum([bool(name), has_images, has_specs]) / 3
        if quality_score >= 0.6:
            checks_passed += 1
        else:
            warnings.append(
                f"Data quality too low ({quality_score * 100:.0f}%)")

        return GateCheckResult(
            gate_name="Compliance",
            status=GateStatus.BLOCKED if violations else (
                GateStatus.WARNING if warnings else GateStatus.PASSED),
            checks_passed=checks_passed, checks_total=checks_total,
            violations=violations, warnings=warnings,
            recommendations=["Verify prices"] if violations else [],
        )


class SourceRulesGate:
    """
    CORE GATE: Enforces the Three-Source Rules.
    This is the MOST IMPORTANT quality gate; without it the app has no value.
    """

    @staticmethod
    def check_source_rules(product: Dict[str, Any]) -> GateCheckResult:
        from backend.source_rules import (
            validate_no_synthetic_data, MIN_REVIEW_SOURCES,
        )

        violations, warnings = [], []
        checks_passed, checks_total = 0, 5

        # Check 1: NO SYNTHETIC DATA
        synthetic_violations = validate_no_synthetic_data(product)
        if synthetic_violations:
            for sv in synthetic_violations:
                violations.append(f"SYNTHETIC DATA: {sv.message}")
        else:
            checks_passed += 1

        # Check 2: Commercial source present
        if product.get("source_coverage_commercial") or (
            product.get("halilit_id") and product.get("price_il") is not None
        ):
            checks_passed += 1
        else:
            violations.append("MISSING SOURCE: No Commercial data")

        # Check 3: Official source present
        if product.get("source_coverage_official") or (
            product.get("official_specs") and product.get(
                "official_description")
        ):
            checks_passed += 1
        else:
            warnings.append(
                "INCOMPLETE: Official brand data not yet collected")

        # Check 4: Contextual source present (3+ reviews)
        source_count = product.get("contextual_source_count", 0)
        review_sources = product.get("review_sources", [])
        actual_count = max(source_count, len(review_sources))
        if actual_count >= MIN_REVIEW_SOURCES:
            checks_passed += 1
        else:
            warnings.append(
                f"INCOMPLETE: Only {actual_count}/{MIN_REVIEW_SOURCES} review sources")

        # Check 5: No AI-generated source markers
        source_field = product.get("_source", "")
        if isinstance(source_field, str) and "ai_enrichment" in source_field.lower():
            violations.append(
                "FORBIDDEN: AI-enriched data masquerading as real")
        else:
            checks_passed += 1

        return GateCheckResult(
            gate_name="SourceRules",
            status=GateStatus.BLOCKED if violations else (
                GateStatus.WARNING if warnings else GateStatus.PASSED),
            checks_passed=checks_passed, checks_total=checks_total,
            violations=violations, warnings=warnings,
            recommendations=["Re-scrape from authorized sources",
                             "Remove synthetic data"] if violations else [],
        )


class QualityGate:
    """Verifies product meets quality standards."""

    @staticmethod
    def check_quality(product: Dict[str, Any],
                      target_score: float = 80.0) -> GateCheckResult:
        violations, warnings = [], []
        checks_passed, checks_total = 0, 3

        from backend.agents.perfection_map import PerfectionMap

        completeness = PerfectionMap.calculate_completeness_score(product)
        if completeness >= target_score:
            checks_passed += 1
        else:
            warnings.append(
                f"Completeness too low ({completeness:.0f}% < {target_score}%)")

        security = PerfectionMap.calculate_security_score(product)
        if security >= 90.0:
            checks_passed += 1
        else:
            violations.append(
                f"Security score too low ({security:.0f}% < 90%)")

        tier = PerfectionMap.get_quality_tier(completeness)
        if tier in ['GOLD', 'SILVER']:
            checks_passed += 1
        else:
            warnings.append(
                f"Product is tier '{tier}' (target: GOLD or SILVER)")

        return GateCheckResult(
            gate_name="Quality",
            status=GateStatus.BLOCKED if violations else (
                GateStatus.WARNING if warnings else GateStatus.PASSED),
            checks_passed=checks_passed, checks_total=checks_total,
            violations=violations, warnings=warnings,
            recommendations=["Improve completeness"] if violations else [],
        )


class ContentQualityGate:
    """Ensures no placeholder text, empty fields, or excessive repetition."""

    PLACEHOLDERS = [
        "lorem ipsum", "tbd", "pending", "coming soon",
        "no description", "n/a", "undefined", "null", "[insert",
    ]

    @staticmethod
    def check_content(product: Dict[str, Any]) -> GateCheckResult:
        violations, warnings = [], []
        checks_passed, checks_total = 0, 4

        def is_placeholder(text: str) -> bool:
            if not text:
                return False
            t = text.lower()
            return any(p in t for p in ContentQualityGate.PLACEHOLDERS)

        name = product.get('product_name', '')
        if is_placeholder(name):
            violations.append(f"Product name contains placeholder: {name}")
        elif name.lower() in ["unknown", "product", "test"]:
            violations.append(f"Product name is generic: {name}")
        else:
            checks_passed += 1

        desc = product.get('description_long') or product.get(
            'description_short') or ""
        if desc and is_placeholder(desc):
            violations.append("Description contains placeholder text")
        else:
            checks_passed += 1

        if desc and name and desc.lower().strip() == name.lower().strip():
            warnings.append("Description is identical to product name")
        else:
            checks_passed += 1

        if ('official_specs' in product
                and isinstance(product['official_specs'], dict)
                and not product['official_specs']):
            warnings.append("Official specs present but empty")
        else:
            checks_passed += 1

        return GateCheckResult(
            gate_name="ContentQuality",
            status=GateStatus.BLOCKED if violations else (
                GateStatus.WARNING if warnings else GateStatus.PASSED),
            checks_passed=checks_passed, checks_total=checks_total,
            violations=violations, warnings=warnings,
            recommendations=["Remove placeholder text"] if violations else [],
        )


class GateProcessor:
    """Runs all gates against a product."""

    @staticmethod
    def process_all_gates(product: Dict[str, Any],
                          strict_mode: bool = False) -> Dict[str, Any]:
        results = {
            "product_id": product.get('halilit_id', 'unknown'),
            "timestamp": None,
            "overall_status": GateStatus.PASSED,
            "gates": {},
        }

        gates = [
            SourceRulesGate.check_source_rules(product),
            InputValidationGate.validate_product(product),
            SecurityGate.check_product_security(product),
            DataIntegrityGate.check_integrity(product),
            ComplianceGate.check_compliance(product),
            QualityGate.check_quality(product),
            ContentQualityGate.check_content(product),
        ]

        total_violations = total_warnings = 0

        for gate_result in gates:
            results["gates"][gate_result.gate_name] = {
                "status": gate_result.status.value,
                "checks_passed": gate_result.checks_passed,
                "checks_total": gate_result.checks_total,
                "violations": gate_result.violations,
                "warnings": gate_result.warnings,
                "recommendations": gate_result.recommendations,
            }

            if gate_result.status == GateStatus.BLOCKED:
                results["overall_status"] = GateStatus.BLOCKED
                total_violations += len(gate_result.violations)
            elif gate_result.status == GateStatus.WARNING:
                if strict_mode or results["overall_status"] == GateStatus.PASSED:
                    results["overall_status"] = GateStatus.WARNING
                total_warnings += len(gate_result.warnings)

        results["total_violations"] = total_violations
        results["total_warnings"] = total_warnings
        results["passed_all_gates"] = results["overall_status"] == GateStatus.PASSED

        logger.info(
            f"[GateProcessor] {product.get('product_name')}: "
            f"Status={results['overall_status'].value}, "
            f"Violations={total_violations}, Warnings={total_warnings}")

        return results
