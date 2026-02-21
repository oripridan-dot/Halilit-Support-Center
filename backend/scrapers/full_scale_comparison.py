"""
Full-Scale Product Comparison Engine

Compares ALL Halilit products to Thomann products with:
- Advanced fuzzy matching for product equivalences
- Complete pricing analysis with VAT/shipping
- Scalable performance for 1000s of products
- Detailed match confidence scoring
"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher
import math
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PriceComparison:
    """Result of comparing a single product pair"""
    halilit_product_id: str
    halilit_product_name: str
    halilit_brand: str
    halilit_price_ils: float

    thomann_product_id: str
    thomann_product_name: str
    thomann_price_eur: float
    thomann_price_ils: float
    thomann_shipping_eur: float

    halilit_total_ils: float
    thomann_total_ils: float
    price_difference_ils: float
    price_difference_percent: float
    cheaper_at: str  # "halilit" or "thomann"
    match_confidence: float  # 0-100


class FullScaleComparison:
    """Enterprise comparison engine for thousands of products"""

    # VAT and currency constants
    VAT_RATE = 0.17  # 17% Israeli VAT
    EUR_TO_ILS = 4.2  # Exchange rate

    # Shipping estimation by weight (kg)
    SHIPPING_BRACKETS = [
        (5, 15),      # < 5kg: €15
        (20, 25),     # 5-20kg: €25
        (50, 45),     # 20-50kg: €45
        (float('inf'), 85),  # > 50kg: €85
    ]

    def __init__(self, halilit_products: List[Dict], thomann_products: List[Dict]):
        """
        Initialize comparison engine.

        Args:
            halilit_products: List of dicts from Halilit database
            thomann_products: List of dicts from Thomann database
        """
        self.halilit_products = halilit_products
        self.thomann_products = thomann_products

        # Build brand indices for faster filtering
        self.thomann_by_brand = self._group_by_brand(thomann_products)

        self.comparisons: List[PriceComparison] = []
        self.unmatched_products = []

    def run_comprehensive_comparison(self) -> Dict:
        """
        Run comparison across all Halilit products.

        Returns:
            Comprehensive statistics and results
        """
        logger.info(
            f"Starting comparison: {len(self.halilit_products)} Halilit products vs {len(self.thomann_products)} Thomann products")

        for i, halilit_product in enumerate(self.halilit_products):
            if i % 100 == 0:
                logger.info(
                    f"  Processed {i}/{len(self.halilit_products)} products")

            # Find best match in Thomann
            best_match = self._find_best_match(halilit_product)

            if best_match:
                # Create comparison
                comparison = self._create_comparison(
                    halilit_product, best_match)
                self.comparisons.append(comparison)
            else:
                self.unmatched_products.append(halilit_product)

        # Generate statistics
        stats = self._generate_statistics()
        logger.info(
            f"✅ Comparison complete: {len(self.comparisons)} products matched")

        return {
            "comparisons": self.comparisons,
            "unmatched": self.unmatched_products,
            "statistics": stats,
        }

    def _find_best_match(self, halilit_product: Dict) -> Optional[Dict]:
        """
        Find best matching Thomann product for a Halilit product.

        Uses brand filtering + fuzzy name matching for efficiency.
        """
        brand = halilit_product.get("brand", "").lower()
        product_name = halilit_product.get("product_name", "").lower()

        # First, search within same brand at Thomann
        brand_candidates = self.thomann_by_brand.get(brand, [])

        if not brand_candidates:
            # Fallback: search all Thomann products
            brand_candidates = self.thomann_products

        # Find best match by name similarity
        best_match = None
        best_score = 0.5  # Minimum confidence threshold

        for thomann_product in brand_candidates:
            thomann_name = thomann_product.get("product_name", "").lower()

            # Calculate similarity
            score = self._similarity_score(product_name, thomann_name)

            if score > best_score:
                best_score = score
                best_match = thomann_product

        return best_match if best_score >= 0.5 else None

    def _similarity_score(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings (0-1).

        Uses SequenceMatcher for fuzzy matching.
        """
        # Remove common words
        stop_words = {'active', 'professional',
                      'studio', 'speaker', 'loudspeaker', 'box'}

        tokens1 = set(word for word in str1.split() if word not in stop_words)
        tokens2 = set(word for word in str2.split() if word not in stop_words)

        # Calculate token overlap
        if not tokens1 or not tokens2:
            return 0

        overlap = len(tokens1 & tokens2) / len(tokens1 | tokens2)

        # Also use sequence matching
        sequence_ratio = SequenceMatcher(None, str1, str2).ratio()

        # Weighted combination
        return 0.4 * overlap + 0.6 * sequence_ratio

    def _create_comparison(self, halilit_product: Dict, thomann_product: Dict) -> PriceComparison:
        """Create a price comparison between two products"""
        # Extract prices
        halilit_price = float(halilit_product.get("price_ils", 0))
        thomann_price_eur = float(thomann_product.get("price_eur", 0))

        # Thomann total calculation
        thomann_shipping = self._estimate_shipping(
            thomann_product.get("weight_kg")
        )
        thomann_subtotal_ils = thomann_price_eur * self.EUR_TO_ILS
        thomann_with_vat = (
            thomann_subtotal_ils + thomann_shipping * self.EUR_TO_ILS) * (1 + self.VAT_RATE)

        # Price difference
        price_diff = thomann_with_vat - halilit_price
        diff_percent = (price_diff / halilit_price *
                        100) if halilit_price > 0 else 0

        return PriceComparison(
            halilit_product_id=halilit_product.get("id", ""),
            halilit_product_name=halilit_product.get("product_name", ""),
            halilit_brand=halilit_product.get("brand", ""),
            halilit_price_ils=halilit_price,
            thomann_product_id=thomann_product.get("id", ""),
            thomann_product_name=thomann_product.get("product_name", ""),
            thomann_price_eur=thomann_price_eur,
            thomann_price_ils=thomann_subtotal_ils,
            thomann_shipping_eur=thomann_shipping,
            halilit_total_ils=halilit_price,
            thomann_total_ils=thomann_with_vat,
            price_difference_ils=price_diff,
            price_difference_percent=diff_percent,
            cheaper_at="halilit" if price_diff < 0 else "thomann",
            match_confidence=self._calculate_confidence(
                halilit_product, thomann_product),
        )

    def _estimate_shipping(self, weight_kg: Optional[float]) -> float:
        """Estimate Thomann shipping cost in EUR based on weight"""
        weight = weight_kg or 10  # Default to 10kg if unknown

        for max_weight, cost in self.SHIPPING_BRACKETS:
            if weight <= max_weight:
                return cost

        return 85  # Maximum

    def _calculate_confidence(self, halilit_product: Dict, thomann_product: Dict) -> float:
        """
        Calculate match confidence (0-100).

        Factors:
        - Brand match (25%)
        - Category match (25%)
        - Price similarity (25%)
        - Name similarity (25%)
        """
        brand_match = 100 if halilit_product.get(
            "brand") == thomann_product.get("brand") else 50

        category_match = 100 if halilit_product.get(
            "category") == thomann_product.get("category") else 50

        # Price similarity (products within 50% price range are similar)
        h_price = float(halilit_product.get("price_ils", 0))
        t_price_ils = float(thomann_product.get(
            "price_eur", 0)) * self.EUR_TO_ILS

        if h_price > 0:
            price_ratio = min(t_price_ils / h_price, h_price / t_price_ils)
            price_match = max(0, 100 * (2 * price_ratio - 1)
                              )  # 0-100 for ratio 0.5-1.0
        else:
            price_match = 50

        # Name similarity
        h_name = halilit_product.get("product_name", "").lower()
        t_name = thomann_product.get("product_name", "").lower()
        name_match = 100 * self._similarity_score(h_name, t_name)

        # Weighted average
        confidence = 0.25 * brand_match + 0.25 * \
            category_match + 0.25 * price_match + 0.25 * name_match

        return round(confidence, 1)

    def _generate_statistics(self) -> Dict:
        """Generate comprehensive comparison statistics"""
        if not self.comparisons:
            return {}

        halilit_cheaper = [
            c for c in self.comparisons if c.cheaper_at == "halilit"]
        thomann_cheaper = [
            c for c in self.comparisons if c.cheaper_at == "thomann"]

        avg_diff = sum(
            c.price_difference_percent for c in self.comparisons) / len(self.comparisons)

        halilit_savings = [
            c.price_difference_percent for c in halilit_cheaper if c.price_difference_percent < 0]
        thomann_premiums = [
            c.price_difference_percent for c in thomann_cheaper if c.price_difference_percent > 0]

        return {
            "total_matched": len(self.comparisons),
            "total_unmatched": len(self.unmatched_products),
            "match_rate_percent": round(100 * len(self.comparisons) / (len(self.comparisons) + len(self.unmatched_products)), 1),
            "halilit_cheaper_count": len(halilit_cheaper),
            "thomann_cheaper_count": len(thomann_cheaper),
            "avg_halilit_savings_percent": round(sum(halilit_savings) / len(halilit_savings), 2) if halilit_savings else 0,
            "avg_thomann_premium_percent": round(sum(thomann_premiums) / len(thomann_premiums), 2) if thomann_premiums else 0,
            "average_price_difference_percent": round(avg_diff, 2),
            "median_confidence": self._median([c.match_confidence for c in self.comparisons]),
        }

    def _group_by_brand(self, products: List[Dict]) -> Dict[str, List[Dict]]:
        """Group products by brand for faster lookup"""
        grouped = {}
        for product in products:
            brand = product.get("brand", "").lower()
            if brand not in grouped:
                grouped[brand] = []
            grouped[brand].append(product)
        return grouped

    def _median(self, values: List[float]) -> float:
        """Calculate median of a list"""
        if not values:
            return 0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        return sorted_values[n // 2]

    def export_comparisons_csv(self, filepath: str):
        """Export comparisons to CSV"""
        import csv

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Brand',
                'Halilit Product',
                'Halilit Price (ILS)',
                'Thomann Product',
                'Thomann Price (EUR)',
                'Thomann Shipping (EUR)',
                'Thomann Total (ILS)',
                'Price Difference (ILS)',
                'Price Difference %',
                'Cheaper At',
                'Match Confidence %',
            ])

            # Rows
            for comp in self.comparisons:
                writer.writerow([
                    comp.halilit_brand,
                    comp.halilit_product_name,
                    f"{comp.halilit_price_ils:.2f}",
                    comp.thomann_product_name,
                    f"{comp.thomann_price_eur:.2f}",
                    f"{comp.thomann_shipping_eur:.2f}",
                    f"{comp.thomann_total_ils:.2f}",
                    f"{comp.price_difference_ils:.2f}",
                    f"{comp.price_difference_percent:.2f}",
                    comp.cheaper_at.upper(),
                    f"{comp.match_confidence:.1f}",
                ])

        logger.info(
            f"✅ Exported {len(self.comparisons)} comparisons to {filepath}")

    def filter_by_confidence(self, min_confidence: float = 70.0) -> List[PriceComparison]:
        """Get only high-confidence matches"""
        return [c for c in self.comparisons if c.match_confidence >= min_confidence]

    def filter_by_brand(self, brand: str) -> List[PriceComparison]:
        """Get comparisons for a specific brand"""
        return [c for c in self.comparisons if c.halilit_brand.lower() == brand.lower()]
