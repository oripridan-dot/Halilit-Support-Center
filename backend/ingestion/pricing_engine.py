"""Pricing Strategy Engine — JIT Architecture stub.

Provides pricing-tier classification and strategy selection for products.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("PricingStrategyEngine")

_pricing_engine: PricingStrategyEngine | None = None


class PricingStrategyEngine:
    """Classifies products into pricing tiers and resolves pricing strategies."""

    def classify(self, product: dict[str, Any]) -> str:
        """Return pricing tier for a product."""
        price = product.get("price_il") or product.get("price")
        if price is None:
            return "call_for_price"
        try:
            p = float(price)
        except (TypeError, ValueError):
            return "call_for_price"
        if p <= 0:
            return "call_for_price"
        if p < 500:
            return "entry"
        if p < 2000:
            return "mid"
        return "premium"

    def resolve(self, product: dict[str, Any]) -> dict[str, Any]:
        """Return resolved pricing data for a product."""
        tier = self.classify(product)
        return {
            "tier": tier,
            "price_il": product.get("price_il"),
            "price_eilat": product.get("price_eilat"),
        }


def get_pricing_engine() -> PricingStrategyEngine:
    """Return the global PricingStrategyEngine singleton."""
    global _pricing_engine
    if _pricing_engine is None:
        _pricing_engine = PricingStrategyEngine()
    return _pricing_engine
