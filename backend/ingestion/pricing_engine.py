"""
PRICING STRATEGY ENGINE v8.5

Handles all pricing logic:
- Automatic tier determination
- Price validation
- Regional pricing strategies
- Price history tracking
- Discount calculations

This is where pricing expertise lives.
"""

import logging
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from datetime import datetime, timedelta

from backend.ingestion.data_models import PricingTier, PricingData

logger = logging.getLogger("PricingStrategyEngine")


@dataclass
class PricingRule:
    """A single pricing rule"""
    name: str
    description: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    tier: Optional[PricingTier] = None
    violation_severity: str = "warning"  # "warning" or "error"


class PricingStrategyEngine:
    """
    Master pricing logic engine.

    Determines:
    - Price tiers based on absolute price
    - Pricing validity and consistency
    - Regional pricing strategies (IL vs Eilat)
    - Suggested pricing corrections
    """

    def __init__(self):
        self.logger = logger

        # TIER DEFINITIONS: Map price ranges to tiers
        self.tier_boundaries = {
            PricingTier.ENTRY: (0, 500),        # Entry: < 500 NIS
            PricingTier.MID: (500, 1500),       # Mid: 500-1500 NIS
            PricingTier.PRO: (1500, 4000),      # Pro: 1500-4000 NIS
            PricingTier.FLAGSHIP: (4000, float('inf')),  # Flagship: > 4000 NIS
        }

        # EILAT DISCOUNT EXPECTATIONS
        self.eilat_discount_expected_percent = 15.0  # Default: 15% discount
        self.eilat_discount_tolerance_percent = 5.0  # +/- 5% is acceptable
        self.eilat_discount_min = 10.0  # Never more than 10% is suspicious
        self.eilat_discount_max = 25.0  # More than 25% is definitely wrong

        # PRICING RULES: Enforce business logic
        self.pricing_rules = self._define_pricing_rules()

    # ============================================================================
    # TIER DETERMINATION
    # ============================================================================

    def determine_tier_by_price(self, price: float) -> PricingTier:
        """
        Determine pricing tier based on absolute price (Israel price).
        """
        for tier, (min_price, max_price) in self.tier_boundaries.items():
            if min_price <= price < max_price:
                return tier

        return PricingTier.MID  # Default fallback

    def suggest_tier(self, price_il: float, category: str) -> PricingTier:
        """
        Suggest a tier based on price and category context.

        This is more sophisticated than simple price binning.
        Considers category expectations.
        """
        base_tier = self.determine_tier_by_price(price_il)

        # Category-specific adjustments
        # (In a production system, you'd fetch from db)
        category_tier_factors = {
            "Keyboards & Synthesizers": 1.2,  # Usually more expensive
            "Cables & Connectors": 0.5,  # Usually cheaper
            "Headphones & Earphones": 0.8,
        }

        factor = category_tier_factors.get(category, 1.0)
        adjusted_price = price_il * factor

        suggested = self.determine_tier_by_price(adjusted_price)

        if suggested != base_tier:
            self.logger.debug(f"Price {price_il} NIS in {category} → "
                              f"Base tier: {base_tier}, Adjusted: {suggested} (factor={factor})")

        return suggested

    # ============================================================================
    # PRICING VALIDITY & CONSISTENCY
    # ============================================================================

    def validate_pricing(self, pricing: PricingData) -> Tuple[bool, List[str]]:
        """
        Validate pricing data for errors and inconsistencies.

        Returns: (is_valid, list_of_errors)
        """
        errors = []

        # Check: Prices must be positive
        if pricing.price_il <= 0:
            errors.append(
                "⚠ price_il must be positive (got {pricing.price_il})")

        if pricing.price_eilat <= 0:
            errors.append(
                "⚠ price_eilat must be positive (got {pricing.price_eilat})")

        # Check: Eilat price cannot exceed IL price
        if pricing.price_eilat > pricing.price_il:
            errors.append(f"❌ CRITICAL: Eilat price ({pricing.price_eilat}) "
                          f"exceeds Israel price ({pricing.price_il})")

        # Check: Discount percent is reasonable
        if pricing.price_il > 0:
            discount = ((pricing.price_il - pricing.price_eilat) /
                        pricing.price_il) * 100

            if discount < self.eilat_discount_min:
                errors.append(
                    f"⚠ Eilat discount is suspiciously low ({discount:.1f}%)")

            if discount > self.eilat_discount_max:
                errors.append(f"❌ Eilat discount is suspiciously high ({discount:.1f}%) - "
                              f"probably data error")

        # Apply pricing rules
        rule_violations = self._check_pricing_rules(pricing)
        errors.extend(rule_violations)

        is_valid = len([e for e in errors if e.startswith("❌")]) == 0
        return is_valid, errors

    def _define_pricing_rules(self) -> List[PricingRule]:
        """Define business logic pricing rules"""
        return [
            PricingRule(
                name="entry_floor",
                description="Entry tier products should cost at least 50 NIS",
                min_price=50,
                tier=PricingTier.ENTRY,
                violation_severity="warning",
            ),
            PricingRule(
                name="flagship_minimum",
                description="Flagship tier products should cost at least 4000 NIS",
                min_price=4000,
                tier=PricingTier.FLAGSHIP,
                violation_severity="error",
            ),
        ]

    def _check_pricing_rules(self, pricing: PricingData) -> List[str]:
        """Check if pricing violates any rules"""
        violations = []

        for rule in self.pricing_rules:
            if rule.tier != pricing.tier:
                continue  # Rule doesn't apply to this tier

            if rule.min_price and pricing.price_il < rule.min_price:
                severity = "⚠" if rule.violation_severity == "warning" else "❌"
                violations.append(
                    f"{severity} {rule.name}: {rule.description}")

            if rule.max_price and pricing.price_il > rule.max_price:
                severity = "⚠" if rule.violation_severity == "warning" else "❌"
                violations.append(
                    f"{severity} {rule.name}: {rule.description}")

        return violations

    # ============================================================================
    # REGIONAL PRICING CALCULATIONS
    # ============================================================================

    def compute_eilat_discount_percent(self, price_il: float, price_eilat: float) -> float:
        """
        Compute the actual Eilat discount percentage.

        Formula: (IL - Eilat) / IL * 100
        """
        if price_il <= 0:
            return 0.0

        return ((price_il - price_eilat) / price_il) * 100

    def validate_eilat_price(self, price_il: float, price_eilat: float) -> Tuple[bool, Optional[str]]:
        """
        Validate Eilat price in context of IL price.

        Returns: (is_valid, explanation)
        """
        if price_il <= 0:
            return True, None  # Can't validate without IL price

        actual_discount = self.compute_eilat_discount_percent(
            price_il, price_eilat)
        expected_range = (
            self.eilat_discount_expected_percent - self.eilat_discount_tolerance_percent,
            self.eilat_discount_expected_percent + self.eilat_discount_tolerance_percent,
        )

        if actual_discount < self.eilat_discount_min:
            return False, f"Discount {actual_discount:.1f}% is below minimum {self.eilat_discount_min}%"

        if actual_discount > self.eilat_discount_max:
            return False, f"Discount {actual_discount:.1f}% is above maximum {self.eilat_discount_max}%"

        if actual_discount < expected_range[0]:
            return False, (f"Discount {actual_discount:.1f}% is below expected "
                           f"{expected_range[0]:.1f}%-{expected_range[1]:.1f}% range")

        return True, None

    def suggest_eilat_price(self, price_il: float, discount_percent: Optional[float] = None) -> float:
        """
        Suggest an appropriate Eilat price given an IL price.

        If discount_percent not specified, uses expected default.
        """
        if discount_percent is None:
            discount_percent = self.eilat_discount_expected_percent

        return price_il * (1 - discount_percent / 100)

    # ============================================================================
    # PRICE COMPARISONS & ANOMALY DETECTION
    # ============================================================================

    def detect_price_anomalies(
        self,
        product_name: str,
        price_il: float,
        category: str,
        price_history: List[Tuple[datetime, float]] = None,
    ) -> List[str]:
        """
        Detect unusual prices within a category.

        Returns list of anomalies found.
        """
        anomalies = []

        if price_history and len(price_history) > 1:
            prices = [p[1] for p in price_history]
            latest_price = prices[-1]
            previous_price = prices[-2]

            change_percent = ((latest_price - previous_price) /
                              previous_price) * 100 if previous_price > 0 else 0

            if abs(change_percent) > 50:
                anomalies.append(
                    f"⚠ Price changed {change_percent:+.1f}% from {previous_price} to {latest_price} NIS"
                )

        if price_il > 50000:
            anomalies.append(
                f"⚠ Price {price_il} NIS seems very high - verify")

        return anomalies

    # ============================================================================
    # TIER ORDERING & DISPLAY
    # ============================================================================

    def get_tier_order(self) -> List[PricingTier]:
        """Get pricing tiers in display order (entry → flagship)"""
        return [
            PricingTier.ENTRY,
            PricingTier.MID,
            PricingTier.PRO,
            PricingTier.FLAGSHIP,
        ]

    def get_tier_label(self, tier: PricingTier) -> str:
        """Get human-readable tier name"""
        labels = {
            PricingTier.ENTRY: "Entry Level",
            PricingTier.MID: "Mid-Range",
            PricingTier.PRO: "Professional",
            PricingTier.FLAGSHIP: "Flagship",
            PricingTier.LEGACY: "Legacy",
        }
        return labels.get(tier, str(tier))

    def get_tier_emoji(self, tier: PricingTier) -> str:
        """Get emoji representation of tier"""
        emojis = {
            PricingTier.ENTRY: "🎯",
            PricingTier.MID: "⭐",
            PricingTier.PRO: "💎",
            PricingTier.FLAGSHIP: "👑",
            PricingTier.LEGACY: "📦",
        }
        return emojis.get(tier, "")

    def get_tier_color(self, tier: PricingTier) -> str:
        """Get suggested color for tier (Tailwind)"""
        colors = {
            PricingTier.ENTRY: "bg-blue-100",
            PricingTier.MID: "bg-green-100",
            PricingTier.PRO: "bg-purple-100",
            PricingTier.FLAGSHIP: "bg-yellow-100",
            PricingTier.LEGACY: "bg-gray-100",
        }
        return colors.get(tier, "bg-gray-100")

    # ============================================================================
    # REPORTING & ANALYSIS
    # ============================================================================

    def generate_pricing_report(self, products: List[Tuple[str, PricingData]]) -> Dict:
        """
        Generate a pricing analysis report for a list of products.

        Args:
            products: List of (product_name, pricing_data) tuples
        """
        by_tier = {}
        for tier in self.get_tier_order():
            by_tier[tier] = {
                'count': 0,
                'min_price': float('inf'),
                'max_price': 0,
                'avg_price': 0,
                'total_price': 0,
            }

        for product_name, pricing in products:
            tier = pricing.tier
            by_tier[tier]['count'] += 1
            by_tier[tier]['min_price'] = min(
                by_tier[tier]['min_price'], pricing.price_il)
            by_tier[tier]['max_price'] = max(
                by_tier[tier]['max_price'], pricing.price_il)
            by_tier[tier]['total_price'] += pricing.price_il

        # Compute averages
        for tier in by_tier:
            if by_tier[tier]['count'] > 0:
                by_tier[tier]['avg_price'] = (
                    by_tier[tier]['total_price'] / by_tier[tier]['count']
                )
            else:
                by_tier[tier]['min_price'] = 0

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_products': len(products),
            'by_tier': {tier.value: data for tier, data in by_tier.items()},
        }

    def export_tier_boundaries(self) -> Dict:
        """Export tier boundary information for frontend"""
        return {
            tier.value: {
                'min': boundaries[0],
                'max': boundaries[1],
                'label': self.get_tier_label(tier),
                'emoji': self.get_tier_emoji(tier),
                'color': self.get_tier_color(tier),
            }
            for tier, boundaries in self.tier_boundaries.items()
        }


# Global singleton
_pricing_engine = None


def get_pricing_engine() -> PricingStrategyEngine:
    """Get or create the global pricing engine"""
    global _pricing_engine
    if _pricing_engine is None:
        _pricing_engine = PricingStrategyEngine()
        logger.info("✅ Pricing Strategy Engine initialized")
    return _pricing_engine
