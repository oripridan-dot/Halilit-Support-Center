"""
Cross-Validation Engine — Phase 6 Implementation

Validates product data consistency across the Three Source Rules:
1. CommercialScout (Halilit) — prices, SKUs, existence
2. OfficialScout (Brand pages) — specs, descriptions, media
3. ContextualScout (3+ review sites) — reviews, pros/cons

Produces a confidence score per product and flags conflicts between sources.

Works alongside the existing source_rules.py enforcement — this module
focuses on CONSISTENCY between sources, while source_rules.py focuses
on OWNERSHIP and IMMUTABILITY.

Usage:
    from backend.ingestion.cross_validator import CrossValidator

    validator = CrossValidator()
    result = validator.validate(product_dict)
    print(result.overall_confidence)   # 0.0 – 1.0
    print(result.confidence_tier)      # HIGH | GOOD | PARTIAL | MINIMAL
    print(result.issues)               # List of ValidationIssues
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict, Set

logger = logging.getLogger("CrossValidator")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ValidationIssue:
    """A single issue found during cross-validation."""
    field: str
    severity: str  # "error" | "warning" | "info"
    message: str
    source_a: Optional[str] = None
    source_b: Optional[str] = None
    value_a: Any = None
    value_b: Any = None


@dataclass
class CrossValidationResult:
    """Complete cross-validation output for a single product."""
    product_id: str
    overall_confidence: float = 0.0  # 0.0 – 1.0
    source_coverage: Dict[str, bool] = field(default_factory=dict)
    issues: List[ValidationIssue] = field(default_factory=list)
    field_scores: Dict[str, float] = field(default_factory=dict)

    @property
    def confidence_tier(self) -> str:
        """Map numeric confidence to a human-readable tier."""
        if self.overall_confidence >= 0.85:
            return "HIGH"
        if self.overall_confidence >= 0.6:
            return "GOOD"
        if self.overall_confidence >= 0.35:
            return "PARTIAL"
        return "MINIMAL"

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    def to_dict(self) -> dict:
        """Serialize for API responses and storage."""
        return {
            "product_id": self.product_id,
            "overall_confidence": round(self.overall_confidence, 4),
            "confidence_tier": self.confidence_tier,
            "source_coverage": self.source_coverage,
            "field_scores": {k: round(v, 4) for k, v in self.field_scores.items()},
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues": [
                {
                    "field": i.field,
                    "severity": i.severity,
                    "message": i.message,
                }
                for i in self.issues
            ],
        }


# ---------------------------------------------------------------------------
# Cross-Validator
# ---------------------------------------------------------------------------

class CrossValidator:
    """
    Validates product data across the Three Source Rules.

    Scoring dimensions (weighted):
    - Source coverage (30%) — are all 3 sources present?
    - Field completeness (25%) — are owned fields actually filled?
    - Cross-consistency (20%) — do shared fields agree across sources?
    - Data integrity (15%) — no synthetic/mock data detected?
    - Review coverage (10%) — are there 3+ review site sources?
    """

    # Field ownership map — mirrors source_rules.py
    FIELD_OWNERSHIP: Dict[str, Set[str]] = {
        "commercial": {
            "prices", "price_il", "price_eilat", "sku", "halilit_url",
            "halilit_id", "availability",
        },
        "official": {
            "title", "brand", "description", "specifications",
            "images", "documentation", "official_url",
            "features", "dimensions", "weight", "materials",
            "model_number",
        },
        "contextual": {
            "reviews", "pros", "cons", "user_rating",
            "review_sources", "real_world_insights", "community_feedback",
        },
    }

    # Known mock/synthetic data markers
    MOCK_INDICATORS = frozenset([
        "lorem ipsum", "test product", "sample data", "placeholder",
        "todo", "fixme", "example.com", "mock data", "dummy",
        "ai_generated", "synthetic", "simulated",
    ])

    # Weights for scoring dimensions
    WEIGHTS = {
        "coverage": 0.30,
        "completeness": 0.25,
        "consistency": 0.20,
        "integrity": 0.15,
        "review_coverage": 0.10,
    }

    def validate(self, product: dict) -> CrossValidationResult:
        """
        Run full cross-validation on a product.

        Args:
            product: Product dict (IngestionProductDraft-shaped or normalized)

        Returns:
            CrossValidationResult with confidence score and issues
        """
        product_id = (
            product.get("id")
            or product.get("sku")
            or product.get("halilit_id")
            or "unknown"
        )
        result = CrossValidationResult(product_id=str(product_id))

        # 1. Source coverage
        result.source_coverage = self._check_source_coverage(product)
        coverage_score = sum(result.source_coverage.values()) / 3.0

        # 2. Field completeness
        completeness_score = self._check_field_completeness(product, result)

        # 3. Cross-consistency of shared fields
        consistency_score = self._check_cross_consistency(product, result)

        # 4. Data integrity (no mock/synthetic data)
        integrity_score = self._check_data_integrity(product, result)

        # 5. Review coverage (3+ sources)
        review_score = self._check_review_coverage(product, result)

        # Weighted overall confidence
        result.overall_confidence = (
            coverage_score * self.WEIGHTS["coverage"]
            + completeness_score * self.WEIGHTS["completeness"]
            + consistency_score * self.WEIGHTS["consistency"]
            + integrity_score * self.WEIGHTS["integrity"]
            + review_score * self.WEIGHTS["review_coverage"]
        )

        result.field_scores = {
            "coverage": round(coverage_score, 4),
            "completeness": round(completeness_score, 4),
            "consistency": round(consistency_score, 4),
            "integrity": round(integrity_score, 4),
            "review_coverage": round(review_score, 4),
        }

        return result

    def validate_batch(self, products: List[dict]) -> List[CrossValidationResult]:
        """Validate a batch of products."""
        return [self.validate(p) for p in products]

    # ------------------------------------------------------------------
    # Scoring dimensions
    # ------------------------------------------------------------------

    def _check_source_coverage(self, product: dict) -> Dict[str, bool]:
        """
        Check which of the 3 authorized sources have contributed data.
        Looks at explicit source markers + presence of owned fields.
        """
        # Check explicit source tracking
        sources = product.get("data_sources", {})
        source_coverage_field = product.get("source_coverage", {})

        if isinstance(sources, list):
            source_set = {s.lower() for s in sources}
            return {
                "commercial": any(
                    k in source_set
                    for k in ("commercial", "halilit", "commercial_scout")
                ),
                "official": any(
                    k in source_set
                    for k in ("official", "brand", "official_scout")
                ),
                "contextual": any(
                    k in source_set
                    for k in ("contextual", "reviews", "contextual_scout")
                ),
            }

        if isinstance(source_coverage_field, dict):
            return {
                "commercial": bool(source_coverage_field.get("commercial")),
                "official": bool(source_coverage_field.get("official")),
                "contextual": bool(source_coverage_field.get("contextual")),
            }

        # Infer from field presence
        return {
            "commercial": bool(
                product.get("price_il")
                or product.get("prices")
                or product.get("halilit_url")
                or product.get("halilit_id")
            ),
            "official": bool(
                product.get("specifications")
                or product.get("official_url")
                or product.get("description")
            ),
            "contextual": bool(
                product.get("reviews")
                or product.get("pros")
                or product.get("review_sources")
            ),
        }

    def _check_field_completeness(
        self, product: dict, result: CrossValidationResult
    ) -> float:
        """Score how complete each source's owned fields are."""
        total_fields = 0
        filled_fields = 0

        for source, fields in self.FIELD_OWNERSHIP.items():
            for f in fields:
                total_fields += 1
                value = self._deep_get(product, f)
                if self._is_nonempty(value):
                    filled_fields += 1
                else:
                    result.issues.append(
                        ValidationIssue(
                            field=f,
                            severity="info",
                            message=f"Missing field '{f}' (owned by {source})",
                            source_a=source,
                        )
                    )

        return filled_fields / max(total_fields, 1)

    def _check_cross_consistency(
        self, product: dict, result: CrossValidationResult
    ) -> float:
        """
        Check that shared fields agree across sources.
        Currently checks: title and brand consistency.
        """
        checks = 0
        agreements = 0

        # --- Title consistency ---
        titles = []
        for key in [
            "title", "name", "product_name", "official_title",
            "commercial_title",
        ]:
            val = product.get(key)
            if val and isinstance(val, str) and len(val.strip()) > 2:
                titles.append(val.strip().lower())

        if len(titles) >= 2:
            checks += 1
            # Token-overlap similarity
            tokens_0 = set(titles[0].split())
            tokens_1 = set(titles[1].split())
            union = tokens_0 | tokens_1
            overlap = len(tokens_0 & tokens_1) / max(len(union), 1)
            if overlap >= 0.5:
                agreements += 1
            else:
                result.issues.append(
                    ValidationIssue(
                        field="title",
                        severity="warning",
                        message="Title mismatch across sources",
                        value_a=titles[0][:80],
                        value_b=titles[1][:80],
                    )
                )

        # --- Brand consistency ---
        brands: set = set()
        for key in ["brand", "manufacturer", "brand_name"]:
            val = product.get(key)
            if val and isinstance(val, str) and len(val.strip()) > 1:
                brands.add(val.strip().lower())

        if len(brands) > 1:
            checks += 1
            result.issues.append(
                ValidationIssue(
                    field="brand",
                    severity="warning",
                    message=f"Brand inconsistency: {brands}",
                )
            )
        elif len(brands) == 1:
            checks += 1
            agreements += 1

        # --- SKU consistency ---
        skus: set = set()
        for key in ["sku", "model_number", "halilit_id"]:
            val = product.get(key)
            if val and isinstance(val, str) and len(val.strip()) > 0:
                skus.add(val.strip().lower())

        if len(skus) >= 2:
            checks += 1
            # SKUs should be different fields — just verify they exist
            agreements += 1

        return agreements / max(checks, 1)

    def _check_data_integrity(
        self, product: dict, result: CrossValidationResult
    ) -> float:
        """
        Detect synthetic/mock/AI-generated data masquerading as real.
        Aligned with source_rules.py's validate_no_synthetic_data().
        """
        score = 1.0
        product_str = json.dumps(product, default=str).lower()

        for indicator in self.MOCK_INDICATORS:
            if indicator in product_str:
                score -= 0.2
                result.issues.append(
                    ValidationIssue(
                        field="*",
                        severity="error",
                        message=f"Synthetic data marker detected: '{indicator}'",
                    )
                )

        # Suspiciously perfect ratings
        for rating_key in ("user_rating", "rating", "average_rating"):
            rating = product.get(rating_key)
            if rating and isinstance(rating, (int, float)):
                if rating == 5.0:
                    score -= 0.1
                    result.issues.append(
                        ValidationIssue(
                            field=rating_key,
                            severity="warning",
                            message="Perfect 5.0 rating is suspicious — may be synthetic",
                        )
                    )
                elif rating < 0 or rating > 5:
                    score -= 0.15
                    result.issues.append(
                        ValidationIssue(
                            field=rating_key,
                            severity="error",
                            message=f"Rating {rating} out of valid range [0, 5]",
                        )
                    )

        # Price sanity checks (negative, absurdly high)
        for price_key in ("price_il", "price_eilat"):
            price = product.get(price_key)
            if price and isinstance(price, (int, float)):
                if price < 0:
                    score -= 0.2
                    result.issues.append(
                        ValidationIssue(
                            field=price_key,
                            severity="error",
                            message=f"Negative price: {price}",
                        )
                    )
                elif price > 500_000:
                    score -= 0.1
                    result.issues.append(
                        ValidationIssue(
                            field=price_key,
                            severity="warning",
                            message=f"Unusually high price: {price}",
                        )
                    )

        return max(score, 0.0)

    def _check_review_coverage(
        self, product: dict, result: CrossValidationResult
    ) -> float:
        """
        Verify contextual data comes from 3+ trusted review sites.
        Aligned with source_rules.MIN_REVIEW_SOURCES = 3.
        """
        review_sources = product.get("review_sources", [])
        if isinstance(review_sources, list):
            count = len(review_sources)
        elif isinstance(review_sources, str):
            count = 1 if review_sources.strip() else 0
        else:
            count = 0

        if count >= 3:
            return 1.0

        if count == 2:
            result.issues.append(
                ValidationIssue(
                    field="review_sources",
                    severity="warning",
                    message=f"Only {count} review sources (need 3+)",
                )
            )
            return 0.6

        if count == 1:
            result.issues.append(
                ValidationIssue(
                    field="review_sources",
                    severity="warning",
                    message=f"Only {count} review source (need 3+)",
                )
            )
            return 0.3

        result.issues.append(
            ValidationIssue(
                field="review_sources",
                severity="error",
                message="No review sources found",
            )
        )
        return 0.0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _deep_get(obj: dict, key: str) -> Any:
        """Get a value from a dict, supporting dot-notation for nesting."""
        if "." in key:
            parts = key.split(".")
            current: Any = obj
            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return None
            return current
        return obj.get(key)

    @staticmethod
    def _is_nonempty(value: Any) -> bool:
        """Check if a value is meaningfully populated."""
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip() not in ("", "N/A", "Unknown", "n/a", "TBD")
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_cross_validator: Optional[CrossValidator] = None


def get_cross_validator() -> CrossValidator:
    """Get or create the singleton CrossValidator."""
    global _cross_validator
    if _cross_validator is None:
        _cross_validator = CrossValidator()
    return _cross_validator
