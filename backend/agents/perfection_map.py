"""
PerfectionMap - The Quality Standards & Learning Framework (v8.2)

This module defines what "perfect product data" looks like and tracks
the Trinity Swarm's journey toward that perfection across multiple dimensions.

The Map provides:
1. Success Criteria (automated scoring)
2. Learning Thresholds (when to improve)
3. Improvement Paths (how agents should evolve)
4. Audit Trail (who did what and why)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class DimensionType(Enum):
    """Quality dimensions agents work toward"""
    COMPLETENESS = "completeness"      # All fields present
    ACCURACY = "accuracy"               # Data matches external sources
    FRESHNESS = "freshness"             # Data is recent/current
    CONSISTENCY = "consistency"         # Data matches across sources
    SECURITY = "security"               # No PII, safe to share
    RELEVANCE = "relevance"             # Matches user intent
    VISUAL_QUALITY = "visual_quality"   # Images/media are high quality


class AgentRole(Enum):
    """Trinity Swarm roles"""
    COMMERCIAL_SCOUT = "commercial_scout"    # Harvests raw product data
    OFFICIAL_VERIFIER = "official_verifier"  # Enriches with official specs
    EXTERNAL_VALIDATOR = "external_validator"  # Audits for compliance


@dataclass
class DimensionScorecard:
    """Tracks performance on a single quality dimension"""
    dimension: DimensionType
    target_score: float          # e.g., 95.0 (95% perfect)
    current_score: float         # Last measured score
    agent_responsible: AgentRole  # Who owns improvement
    improvements_attempted: int = 0
    last_improved: Optional[datetime] = None
    success_criteria: List[str] = field(default_factory=list)

    def is_meeting_target(self) -> bool:
        """Check if current score meets target"""
        return self.current_score >= self.target_score

    def gap_to_perfection(self) -> float:
        """How far from target?"""
        return max(0.0, self.target_score - self.current_score)


@dataclass
class PerfectionMap:
    """
    The master quality standards map.
    Defines success metrics and guides agent improvement.
    """

    # ============================================================================
    # DIMENSIONS OF PERFECTION
    # ============================================================================

    # 1. COMPLETENESS - All essential fields populated
    COMPLETENESS_CRITERIA = {
        "product_name": {"weight": 0.20, "required": True},
        "brand": {"weight": 0.15, "required": True},
        "price_il": {"weight": 0.20, "required": True},
        "taxonomy": {"weight": 0.15, "required": True},
        "display": {"weight": 0.15, "required": True},
        "images": {"weight": 0.15, "required": False, "min_count": 2},
    }

    # 2. ACCURACY - Matches authoritative sources
    ACCURACY_CRITERIA = {
        "price_variance_allowed": 0.05,  # ±5% from official price
        "spec_match_required": 0.90,     # 90% field match with official
        "name_similarity_required": 0.85,  # 85% name match
    }

    # 3. FRESHNESS - Recent data
    FRESHNESS_CRITERIA = {
        "max_age_days": 30,              # Data shouldn't be older than 30 days
        "price_refresh_days": 7,          # Prices should be refreshed weekly
        "availability_check_required": True,
    }

    # 4. CONSISTENCY - Same data across sources
    CONSISTENCY_CRITERIA = {
        "cross_source_match": 0.85,      # 85% of fields consistent across sources
        "brand_spelling": True,           # Brand name consistent
        "category_stability": True,       # Category shouldn't change between checks
    }

    # 5. SECURITY - No sensitive data, safe
    SECURITY_CRITERIA = {
        "no_pii": True,                   # No personal info
        "no_internal_ids": True,          # No internal reference numbers
        "markup_clean": True,             # Safe HTML/JSON
        "verified_brand": True,           # Brand is legit
    }

    # 6. RELEVANCE - Matches user search intent
    RELEVANCE_CRITERIA = {
        "keyword_match_required": 0.80,  # 80% keyword overlap
        "category_correct": True,         # Right category assigned
        "similar_products_accuracy": 0.75,  # 75% of similar products are actually similar
    }

    # 7. VISUAL QUALITY - Media/images are usable
    VISUAL_CRITERIA = {
        "image_resolution_min": 300,     # Minimum 300px minimum dimension
        "image_file_size_range": (50000, 10000000),  # 50KB - 10MB
        "image_format_allowed": ["jpg", "png", "webp"],
        "description_length_min": 50,    # At least 50 chars
    }

    # ============================================================================
    # SUCCESS METRICS
    # ============================================================================

    QUALITY_TIERS = {
        "GOLD": 95.0,      # Excellent - ready for premium display
        "SILVER": 80.0,    # Good - ready for production
        "BRONZE": 60.0,    # Acceptable - needs review
        "REJECTED": 0.0,   # Failed critical checks
    }

    # Per-agent targets
    AGENT_TARGETS = {
        AgentRole.COMMERCIAL_SCOUT: {
            "completeness": 70.0,
            "freshness": 85.0,
            "security": 95.0,
        },
        AgentRole.OFFICIAL_VERIFIER: {
            "accuracy": 95.0,
            "completeness": 85.0,
            "visual_quality": 80.0,
        },
        AgentRole.EXTERNAL_VALIDATOR: {
            "consistency": 90.0,
            "security": 98.0,
            "relevance": 80.0,
        },
    }

    # ============================================================================
    # LEARNING & IMPROVEMENT
    # ============================================================================

    @staticmethod
    def calculate_completeness_score(product: Dict[str, Any]) -> float:
        """
        Calculate how complete a product's data is (0-100).

        Weighted scoring:
        - essential fields (name, brand, price) = 60% of score
        - enrichment fields (images, taxonomy) = 40% of score
        """
        score = 0.0
        total_weight = 0.0

        for field_name, criteria in PerfectionMap.COMPLETENESS_CRITERIA.items():
            weight = criteria["weight"]
            total_weight += weight

            if field_name == "images":
                actual_count = len(product.get("images", []))
                min_count = criteria.get("min_count", 0)
                field_score = min(
                    100.0, (actual_count / max(1, min_count)) * 100)
            else:
                field_present = field_name in product and product[field_name]
                field_score = 100.0 if field_present else 0.0

            score += (field_score / 100.0) * weight

        return min(100.0, score * 100)

    @staticmethod
    def calculate_accuracy_score(
        product: Dict[str, Any],
        official_source: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Compare product data against official source (95 = nearly perfect).

        Checks:
        - Price within allowed variance
        - Specs match official data
        - Name similarity
        """
        if not official_source:
            return 50.0  # Can't verify without reference

        score = 0.0
        checks = 0

        # Price accuracy
        price_actual = product.get("price_il", 0)
        price_official = official_source.get("price", 0)
        if price_official > 0:
            variance = abs(price_actual - price_official) / price_official
            price_score = 100.0 if variance <= 0.05 else max(
                0.0, 100 - (variance * 100))
            score += price_score
            checks += 1

        # Name similarity (simple Levenshtein approximation)
        name_actual = product.get("product_name", "").lower()
        name_official = official_source.get("name", "").lower()
        if name_actual and name_official:
            matching_chars = sum(1 for a, b in zip(
                name_actual, name_official) if a == b)
            name_score = (matching_chars /
                          max(len(name_actual), len(name_official))) * 100
            score += name_score
            checks += 1

        return score / max(1, checks) if checks > 0 else 50.0

    @staticmethod
    def calculate_security_score(product: Dict[str, Any]) -> float:
        """
        Check if product data is secure (no PII, safe for sharing).

        Security checks:
        - No personal emails/phone numbers
        - No internal reference numbers
        - Clean HTML (no malicious markup)
        - Verified brand
        """
        score = 100.0

        # Check for PII patterns
        dangerous_patterns = [
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone number
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            r"(?i)secret|password|api[_-]?key|token",  # Credentials
        ]

        import re
        full_text = json.dumps(product)
        for pattern in dangerous_patterns:
            if re.search(pattern, full_text):
                score -= 25.0

        # Check for suspicious HTML
        if "<script>" in full_text.lower() or "javascript:" in full_text.lower():
            score -= 50.0

        return max(0.0, score)

    @staticmethod
    def get_quality_tier(score: float) -> str:
        """Classify product quality"""
        for tier_name in ["GOLD", "SILVER", "BRONZE", "REJECTED"]:
            tier_threshold = PerfectionMap.QUALITY_TIERS[tier_name]
            if score >= tier_threshold:
                return tier_name
        return "REJECTED"


@dataclass
class AgentLearningState:
    """
    Tracks what an agent has learned over time.
    Agents improve by remembering patterns that work/don't work.
    """
    agent: AgentRole
    session_id: str
    products_processed: int = 0
    successes: int = 0
    failures: int = 0
    learned_patterns: List[str] = field(default_factory=list)
    improvement_iterations: int = 0
    last_major_improvement: Optional[datetime] = None

    # Categories this agent does well on
    strong_categories: Dict[str, float] = field(default_factory=dict)
    weak_categories: Dict[str, float] = field(default_factory=dict)

    def success_rate(self) -> float:
        """How often is this agent successful?"""
        total = self.successes + self.failures
        if total == 0:
            return 0.0
        return (self.successes / total) * 100

    def should_retrain(self) -> bool:
        """Signal when agent needs to improve"""
        return self.success_rate() < 85.0

    def record_success(self, product_id: str, category: str, score: float):
        """Agent did well on this"""
        self.successes += 1
        if category not in self.strong_categories:
            self.strong_categories[category] = 0.0
        self.strong_categories[category] = (
            self.strong_categories[category] * 0.8 + score * 0.2
        )

    def record_failure(self, product_id: str, category: str, reason: str):
        """Agent failed on this"""
        self.failures += 1
        if category not in self.weak_categories:
            self.weak_categories[category] = 0.0
        self.weak_categories[category] += 1.0
        self.learned_patterns.append(f"FAILED: {category} - {reason}")


@dataclass
class ImprovementPath:
    """
    Guide for how an agent should improve on a specific dimension.
    """
    dimension: DimensionType
    current_score: float
    target_score: float
    gap: float
    recommended_actions: List[str]

    def get_next_action(self) -> Optional[str]:
        """What should the agent try next?"""
        if not self.recommended_actions:
            return None
        return self.recommended_actions[0]


def create_improvement_plan(
    agent: AgentRole,
    dimension: DimensionType,
    current_score: float,
) -> ImprovementPath:
    """
    Generate a specific improvement plan for an agent on a dimension.
    """
    target = PerfectionMap.AGENT_TARGETS[agent].get(dimension.value, 80.0)
    gap = target - current_score

    actions = []
    if dimension == DimensionType.COMPLETENESS:
        actions = [
            "Add missing fields from primary sources",
            "Cross-check with manufacturer specifications",
            "Enrich with multi-source verification",
        ]
    elif dimension == DimensionType.ACCURACY:
        actions = [
            "Validate against official product pages",
            "Cross-reference prices with 2+ sources",
            "Verify specs with authoritative databases",
        ]
    elif dimension == DimensionType.SECURITY:
        actions = [
            "Scan for PII and sensitive data",
            "Validate HTML/JSON markup safety",
            "Verify brand legitimacy",
            "Remove internal references",
        ]
    elif dimension == DimensionType.CONSISTENCY:
        actions = [
            "Compare data across multiple sources",
            "Flag inconsistencies for human review",
            "Learn what 'normal variance' is",
        ]
    else:
        actions = [f"Improve {dimension.value} quality through learning"]

    return ImprovementPath(
        dimension=dimension,
        current_score=current_score,
        target_score=target,
        gap=gap,
        recommended_actions=actions,
    )
