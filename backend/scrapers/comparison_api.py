"""
API Integration for Full-Scale Comparison

Provides endpoints for:
- Comprehensive product comparison (all products)
- Paginated results
- CSV export
- Brand-specific comparisons
- Match quality filtering
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path
import json
import sqlite3

from backend.scrapers.ingestion_orchestrator import ProductDatabase
from backend.scrapers.full_scale_comparison import FullScaleComparison

logger = logging.getLogger(__name__)

# Cache for comparison results to avoid recalculating
COMPARISON_CACHE = {
    "results": None,
    "timestamp": None,
}


class ComparisonAPI:
    """High-level API for comparison operations"""

    def __init__(self):
        self.db = ProductDatabase()

    def get_comprehensive_comparison(self, force_recalculate: bool = False) -> Dict:
        """
        Get comprehensive comparison across ALL products.

        Returns pageable results with full statistics.
        """
        # Check cache
        if COMPARISON_CACHE["results"] and not force_recalculate:
            return COMPARISON_CACHE["results"]

        # Load products from database
        halilit_products = self.db.get_all_halilit_products()
        thomann_products = self.db.get_all_thomann_products()

        logger.info(
            f"Running comparison on {len(halilit_products)} Halilit vs {len(thomann_products)} Thomann products")

        # Run comparison
        comparison_engine = FullScaleComparison(
            halilit_products, thomann_products)
        results = comparison_engine.run_comprehensive_comparison()

        # Format response
        response = {
            "meta": {
                "total_comparisons": len(results["comparisons"]),
                "total_unmatched": len(results["unmatched"]),
                "statistics": results["statistics"],
            },
            "comparisons": [self._format_comparison(c) for c in results["comparisons"]],
            "unmatched_products": results["unmatched"],
        }

        # Cache results
        COMPARISON_CACHE["results"] = response
        import datetime
        COMPARISON_CACHE["timestamp"] = datetime.datetime.utcnow().isoformat()

        return response

    def get_paginated_comparisons(
        self, page: int = 1, page_size: int = 50, min_confidence: float = 0.0
    ) -> Dict:
        """
        Get paginated comparison results.

        Args:
            page: Page number (1-indexed)
            page_size: Results per page
            min_confidence: Minimum match confidence (0-100)

        Returns:
            Paginated results with metadata
        """
        comparison_data = self.get_comprehensive_comparison()

        # Filter by confidence if needed
        filtered = comparison_data["comparisons"]
        if min_confidence > 0:
            filtered = [
                c for c in filtered if c["match_confidence"] >= min_confidence]

        # Calculate pagination
        total = len(filtered)
        total_pages = (total + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total)

        return {
            "page": page,
            "page_size": page_size,
            "total_results": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "results": filtered[start_idx:end_idx],
        }

    def get_brand_comparison_all(self, brand: str) -> Dict:
        """Compare all products of a specific brand"""
        comparison_data = self.get_comprehensive_comparison()

        brand_comparisons = [
            c for c in comparison_data["comparisons"]
            if c["halilit_brand"].lower() == brand.lower()
        ]

        if not brand_comparisons:
            return {
                "brand": brand,
                "total": 0,
                "results": [],
                "message": f"No products found for brand {brand}",
            }

        # Calculate brand-specific statistics
        halilit_cheaper = [
            c for c in brand_comparisons if c["cheaper_at"] == "halilit"]
        thomann_cheaper = [
            c for c in brand_comparisons if c["cheaper_at"] == "thomann"]

        avg_diff = sum(c["price_difference_percent"]
                       for c in brand_comparisons) / len(brand_comparisons)

        return {
            "brand": brand,
            "total": len(brand_comparisons),
            "halilit_cheaper": len(halilit_cheaper),
            "thomann_cheaper": len(thomann_cheaper),
            "average_price_difference_percent": round(avg_diff, 2),
            "results": brand_comparisons,
        }

    def export_full_comparison_csv(self, filepath: Optional[str] = None) -> str:
        """Export all comparisons to CSV"""
        if filepath is None:
            filepath = str(
                Path(__file__).parent.parent /
                "exports" / "full_comparison.csv"
            )

        # Ensure export directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        comparison_data = self.get_comprehensive_comparison()

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

            # Data rows
            for comp in comparison_data["comparisons"]:
                writer.writerow([
                    comp["halilit_brand"],
                    comp["halilit_product_name"],
                    f"{comp['halilit_price_ils']:.2f}",
                    comp["thomann_product_name"],
                    f"{comp['thomann_price_eur']:.2f}",
                    f"{comp['thomann_shipping_eur']:.2f}",
                    f"{comp['thomann_total_ils']:.2f}",
                    f"{comp['price_difference_ils']:.2f}",
                    f"{comp['price_difference_percent']:.2f}",
                    comp["cheaper_at"].upper(),
                    f"{comp['match_confidence']:.1f}",
                ])

        logger.info(
            f"✅ Exported {len(comparison_data['comparisons'])} comparisons to {filepath}")
        return filepath

    def get_database_stats(self) -> Dict:
        """Get current database statistics"""
        return self.db.get_stats()

    def clear_cache(self):
        """Clear comparison cache (e.g., after new data ingestion)"""
        COMPARISON_CACHE["results"] = None
        COMPARISON_CACHE["timestamp"] = None
        logger.info("🔄 Comparison cache cleared")

    @staticmethod
    def _format_comparison(comparison) -> Dict:
        """Format comparison dataclass as dict"""
        return {
            "halilit_product_id": comparison.halilit_product_id,
            "halilit_product_name": comparison.halilit_product_name,
            "halilit_brand": comparison.halilit_brand,
            "halilit_price_ils": comparison.halilit_price_ils,
            "thomann_product_id": comparison.thomann_product_id,
            "thomann_product_name": comparison.thomann_product_name,
            "thomann_price_eur": comparison.thomann_price_eur,
            "thomann_price_ils": comparison.thomann_price_ils,
            "thomann_shipping_eur": comparison.thomann_shipping_eur,
            "halilit_total_ils": comparison.halilit_total_ils,
            "thomann_total_ils": comparison.thomann_total_ils,
            "price_difference_ils": comparison.price_difference_ils,
            "price_difference_percent": comparison.price_difference_percent,
            "cheaper_at": comparison.cheaper_at,
            "match_confidence": comparison.match_confidence,
        }


# Singleton instance
_comparison_api = None


def get_comparison_api() -> ComparisonAPI:
    """Get singleton ComparisonAPI instance"""
    global _comparison_api
    if _comparison_api is None:
        _comparison_api = ComparisonAPI()
    return _comparison_api
