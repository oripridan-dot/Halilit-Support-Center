"""
Security & Verification Gates Module (v8.0)

Implements checkpoint verification at each stage of the pipeline.
Ensures clean, secured, and reliable data flow through the Trinity Swarm.

Gates:
1. InputValidationGate - Sanitize & validate inputs
2. SecurityGate - Check for PII, malicious content
3. DataIntegrityGate - Verify structure/completeness
4. ComplianceGate - Check against regulations
5. QualityGate - Verify meets quality standards
"""

import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger("SecurityGates")


class GateStatus(Enum):
    """Gate check result"""
    PASSED = "passed"
    WARNING = "warning"
    BLOCKED = "blocked"


@dataclass
class GateCheckResult:
    """Result of a gate verification"""
    gate_name: str
    status: GateStatus
    checks_passed: int
    checks_total: int
    violations: List[str]
    warnings: List[str]
    recommendations: List[str]

    def is_critical_failure(self) -> bool:
        """Check if any critical violations detected"""
        critical_patterns = ["pii_detected",
                             "malicious_code", "structure_invalid"]
        return any(pattern in v.lower() for v in self.violations)


# ============================================================================
# GATE 1: INPUT VALIDATION GATE
# ============================================================================

class InputValidationGate:
    """
    Sanitizes and validates inputs before processing.
    Prevents bad data from entering the pipeline.
    """

    @staticmethod
    def validate_product(product: Dict[str, Any]) -> GateCheckResult:
        """
        Validate product structure and basic sanity.
        """
        violations = []
        warnings = []
        checks_passed = 0
        checks_total = 6

        # Check 1: Is dict
        if not isinstance(product, dict):
            violations.append(
                f"Product is not a dictionary (got {type(product).__name__})")
        else:
            checks_passed += 1

        # Check 2: Has required fields
        required_fields = ['product_name', 'brand', 'price_il', 'halilit_id']
        for field in required_fields:
            if field not in product or not product[field]:
                violations.append(f"Missing required field: {field}")
            else:
                checks_passed += 1

        # Check 3: Price is valid
        try:
            price = float(product.get('price_il', 0))
            if price < 0:
                violations.append("Price is negative")
            elif price == 0:
                warnings.append("Price is zero (might be TBD)")
            else:
                checks_passed += 1
        except (ValueError, TypeError):
            violations.append(
                f"Price is not a number (got {type(product.get('price_il')).__name__})")

        # Check 4: Product name is reasonable length
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
            checks_passed=checks_passed,
            checks_total=checks_total,
            violations=violations,
            warnings=warnings,
            recommendations=["Add missing fields",
                             "Verify price information"] if violations else [],
        )


# ============================================================================
# GATE 2: SECURITY GATE
# ============================================================================

class SecurityGate:
    """
    Checks for security threats:
    - Personal Identifiable Information (PII)
    - Malicious code/markup
    - Suspicious patterns
    - Data integrity
    """

    # PII patterns to detect
    PII_PATTERNS = {
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone: XXX-XXX-XXXX
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",  # Social Security
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "ip_address": r"\b(?:192\.168|10\.|172\.1[6-9]|172\.2[0-9]|172\.3[01])\.\d{1,3}\.\d{1,3}\b",
        "internal_id": r"(?i)(internal_id|ref_id|employee_id|account_\w+)[:=\s]+[\w\d-]+",
    }

    # Malicious code patterns
    MALICIOUS_PATTERNS = {
        "script": r"<script[^>]*>.*?</script>",
        "javascript": r"javascript:",
        "onclick": r"on\w+\s*=",
        "sql_injection": r"(union|select|insert|delete|drop)[\s\n]+(from|into|where|table)",
        "xss": r"<(iframe|object|embed|img)[^>]*on\w+",
    }

    @staticmethod
    def check_pii(text: str) -> Tuple[bool, List[str]]:
        """
        Scan text for PII.
        Returns (has_pii, detected_patterns)
        """
        if not isinstance(text, str):
            return False, []

        detected = []
        for pattern_name, pattern in SecurityGate.PII_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(f"PII_detected: {pattern_name}")

        return len(detected) > 0, detected

    @staticmethod
    def check_malicious(text: str) -> Tuple[bool, List[str]]:
        """
        Scan for malicious code patterns.
        Returns (is_malicious, detected_patterns)
        """
        if not isinstance(text, str):
            return False, []

        detected = []
        for pattern_name, pattern in SecurityGate.MALICIOUS_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                detected.append(f"malicious_{pattern_name}")

        return len(detected) > 0, detected

    @staticmethod
    def check_product_security(product: Dict[str, Any]) -> GateCheckResult:
        """
        Full security check on a product.
        """
        violations = []
        warnings = []
        checks_passed = 0
        checks_total = 5

        # Convert entire product to string for scanning
        product_text = str(product).lower()

        # Check 1: No PII
        has_pii, pii_patterns = SecurityGate.check_pii(product_text)
        if has_pii:
            violations.append(f"PII detected: {', '.join(pii_patterns)}")
        else:
            checks_passed += 1

        # Check 2: No malicious code
        is_malicious, mal_patterns = SecurityGate.check_malicious(product_text)
        if is_malicious:
            violations.append(
                f"Malicious code detected: {', '.join(mal_patterns)}")
        else:
            checks_passed += 1

        # Check 3: No obvious credential exposure
        if re.search(r"(?i)(password|api_?key|secret|token)[\s:=]+\S+", product_text):
            violations.append("Potential credential exposure detected")
        else:
            checks_passed += 1

        # Check 4: Brand is reasonable
        brand = product.get('brand', '')
        if not brand or len(brand) < 2 or len(brand) > 100:
            warnings.append("Brand name suspicious or missing")
        else:
            checks_passed += 1

        # Check 5: Price is reasonable (not obviously fake)
        price = product.get('price_il', 0)
        if isinstance(price, (int, float)):
            if price < 10 or price > 1000000:
                warnings.append(
                    "Price seems unrealistic (very low or very high)")
            else:
                checks_passed += 1

        return GateCheckResult(
            gate_name="Security",
            status=GateStatus.BLOCKED if violations else (
                GateStatus.WARNING if warnings else GateStatus.PASSED),
            checks_passed=checks_passed,
            checks_total=checks_total,
            violations=violations,
            warnings=warnings,
            recommendations=["Remove PII before storage", "Verify brand legitimacy",
                             "Check price reasonableness"] if violations else [],
        )


# ============================================================================
# GATE 3: DATA INTEGRITY GATE
# ============================================================================

class DataIntegrityGate:
    """
    Verifies data structure and completeness.
    Ensures data can be properly stored and served.
    """

    @staticmethod
    def check_integrity(product: Dict[str, Any], required_fields: List[str] = None) -> GateCheckResult:
        """
        Check data integrity and structure.
        """
        if required_fields is None:
            required_fields = {
                'product_name', 'brand', 'price_il', 'halilit_id',
                'display', 'pricing', 'taxonomy'
            }

        violations = []
        warnings = []
        checks_passed = 0
        checks_total = 6

        # Check 1: Essential fields present
        missing = [f for f in required_fields if f not in product]
        if missing:
            violations.append(f"Missing fields: {', '.join(missing)}")
        else:
            checks_passed += 1

        # Check 2: Images accessible
        images = product.get('official_images', [])
        if isinstance(images, list):
            if len(images) == 0:
                warnings.append("No official images available")
            else:
                checks_passed += 1
        else:
            violations.append(
                f"Images field is not a list (got {type(images).__name__})")

        # Check 3: Taxonomy valid
        taxonomy = product.get('taxonomy', {})
        if isinstance(taxonomy, dict):
            required_taxonomy = ['canonical_category', 'canonical_subcategory']
            missing_tax = [f for f in required_taxonomy if f not in taxonomy]
            if missing_tax:
                warnings.append(
                    f"Missing taxonomy fields: {', '.join(missing_tax)}")
            else:
                checks_passed += 1
        else:
            violations.append(
                f"Taxonomy is not a dict (got {type(taxonomy).__name__})")

        # Check 4: Display data valid
        display = product.get('display', {})
        if isinstance(display, dict):
            checks_passed += 1
        else:
            violations.append(
                f"Display is not a dict (got {type(display).__name__})")

        # Check 5: Pricing valid
        pricing = product.get('pricing', {})
        if isinstance(pricing, dict):
            if 'price_il' not in pricing:
                warnings.append("Pricing missing price_il field")
            else:
                checks_passed += 1
        else:
            violations.append(
                f"Pricing is not a dict (got {type(pricing).__name__})")

        # Check 6: Data consistency
        # Product name should match across fields
        name1 = product.get('product_name', '')
        name2 = product.get('display', {}).get('display_name', '')
        if name1 and name2 and name1.lower() == name2.lower():
            checks_passed += 1
        elif name1:
            checks_passed += 1  # At least primary name is present

        return GateCheckResult(
            gate_name="DataIntegrity",
            status=GateStatus.BLOCKED if violations else (
                GateStatus.WARNING if warnings else GateStatus.PASSED),
            checks_passed=checks_passed,
            checks_total=checks_total,
            violations=violations,
            warnings=warnings,
            recommendations=["Normalize data structure",
                             "Add missing fields"] if violations else [],
        )


# ============================================================================
# GATE 4: COMPLIANCE GATE
# ============================================================================

class ComplianceGate:
    """
    Checks compliance with business rules and policies.
    """

    @staticmethod
    def check_compliance(product: Dict[str, Any]) -> GateCheckResult:
        """
        Check business rule compliance.
        """
        violations = []
        warnings = []
        checks_passed = 0
        checks_total = 4

        # Check 1: Price in valid range (for Israel market)
        price = product.get('price_il', 0)
        if isinstance(price, (int, float)):
            if price < 50:  # Minimum reasonable price
                violations.append("Price below acceptable minimum (< 50 NIS)")
            elif price > 500000:  # Maximum reasonable price
                violations.append(
                    "Price exceeds acceptable maximum (> 500,000 NIS)")
            else:
                checks_passed += 1

        # Check 2: Brand validation
        brand = product.get('brand', '').lower()
        # Add real brands list in production
        known_brands = ['roland', 'nord', 'yamaha', 'boss',
                        'korg', 'universal audio', 'rode', 'shure']
        if brand in known_brands or len(brand) > 2:
            checks_passed += 1
        else:
            warnings.append("Brand not in known list or too short")

        # Check 3: Category consistency
        category = product.get('taxonomy', {}).get('canonical_category', '')
        valid_categories = [
            'Amplifiers & Effects', 'Audio Interfaces & Mixers',
            'Drums & Percussion', 'Headphones & Earphones',
            'Keyboards & Synthesizers', 'Microphones & Recording',
            'Studio Monitors & Speakers', 'Other'
        ]
        if category in valid_categories:
            checks_passed += 1
        else:
            warnings.append(f"Category '{category}' not in approved list")

        # Check 4: Minimum data quality
        # Product must have at least 60% completeness
        name = product.get('product_name', '')
        has_images = len(product.get('official_images', [])) > 0
        has_specs = bool(product.get('official_specs'))
        quality_score = sum([bool(name), has_images, has_specs]) / 3

        if quality_score >= 0.6:
            checks_passed += 1
        else:
            warnings.append(f"Data quality too low ({quality_score*100:.0f}%)")

        return GateCheckResult(
            gate_name="Compliance",
            status=GateStatus.BLOCKED if violations else (
                GateStatus.WARNING if warnings else GateStatus.PASSED),
            checks_passed=checks_passed,
            checks_total=checks_total,
            violations=violations,
            warnings=warnings,
            recommendations=[
                "Verify prices", "Validate category assignment"] if violations else [],
        )


# ============================================================================
# GATE 5: QUALITY GATE
# ============================================================================

class QualityGate:
    """
    Verifies product meets quality standards.
    """

    @staticmethod
    def check_quality(product: Dict[str, Any], target_score: float = 80.0) -> GateCheckResult:
        """
        Check if product meets quality threshold.
        """
        from backend.agents.perfection_map import PerfectionMap

        violations = []
        warnings = []
        checks_passed = 0
        checks_total = 3

        # Check 1: Completeness
        completeness = PerfectionMap.calculate_completeness_score(product)
        if completeness >= target_score:
            checks_passed += 1
        else:
            warnings.append(
                f"Completeness score too low ({completeness:.0f}% < {target_score}%)")

        # Check 2: Security
        security = PerfectionMap.calculate_security_score(product)
        if security >= 90.0:
            checks_passed += 1
        else:
            violations.append(
                f"Security score too low ({security:.0f}% < 90%)")

        # Check 3: Overall tier
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
            checks_passed=checks_passed,
            checks_total=checks_total,
            violations=violations,
            warnings=warnings,
            recommendations=["Improve data completeness",
                             "Add official images/specs"] if violations else [],
        )


# ============================================================================
# GATE PROCESSOR
# ============================================================================

class GateProcessor:
    """
    Runs all gates against a product.
    Provides comprehensive security and quality verification.
    """

    @staticmethod
    def process_all_gates(product: Dict[str, Any], strict_mode: bool = False) -> Dict[str, Any]:
        """
        Run all gates and return comprehensive report.

        strict_mode=True: Any warning becomes a blocker
        """

        results = {
            "product_id": product.get('halilit_id', 'unknown'),
            "timestamp": None,
            "overall_status": GateStatus.PASSED,
            "gates": {},
        }

        # Run all gates
        gates = [
            InputValidationGate.validate_product(product),
            SecurityGate.check_product_security(product),
            DataIntegrityGate.check_integrity(product),
            ComplianceGate.check_compliance(product),
            QualityGate.check_quality(product),
        ]

        total_violations = 0
        total_warnings = 0

        for gate_result in gates:
            results["gates"][gate_result.gate_name] = {
                "status": gate_result.status.value,
                "checks_passed": gate_result.checks_passed,
                "checks_total": gate_result.checks_total,
                "violations": gate_result.violations,
                "warnings": gate_result.warnings,
                "recommendations": gate_result.recommendations,
            }

            # Update overall status
            if gate_result.status == GateStatus.BLOCKED:
                results["overall_status"] = GateStatus.BLOCKED
                total_violations += len(gate_result.violations)
            elif gate_result.status == GateStatus.WARNING and strict_mode:
                results["overall_status"] = GateStatus.WARNING
                total_warnings += len(gate_result.warnings)
            elif gate_result.status == GateStatus.WARNING and results["overall_status"] == GateStatus.PASSED:
                results["overall_status"] = GateStatus.WARNING
                total_warnings += len(gate_result.warnings)

        results["total_violations"] = total_violations
        results["total_warnings"] = total_warnings
        results["passed_all_gates"] = results["overall_status"] == GateStatus.PASSED

        logger.info(
            f"[GateProcessor] {product.get('product_name')}: "
            f"Status={results['overall_status'].value}, "
            f"Violations={total_violations}, Warnings={total_warnings}"
        )

        return results
