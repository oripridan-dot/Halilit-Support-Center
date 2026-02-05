"""
Spectrum Adapter - Convert IngestionProductDraft to Spectrum Format

Bridges between the ingestion pipeline and the Spectrum display system.
Converts validated IngestionProductDraft objects into SpecProduct objects
organized into PriceTracks for optimal display and discovery.

Key Responsibilities:
- Convert ingestion output to Spectrum format
- Organize products by pricing tier
- Extract display properties
- Maintain data provenance
- Generate quality reports
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from enum import Enum

from backend.ingestion.data_models import (
    IngestionProductDraft, IngestionReport, PricingTier, DisplayRole
)

logger = logging.getLogger("SpectrumAdapter")


class SpecProduct:
    """Product in Spectrum Track format"""

    def __init__(
        self,
        halilit_id: str,
        name: str,
        brand: str,
        category: str,
        subcategory: str,
        price_il: float,
        price_eilat: float,
        display_role: str,
        display_tier_level: int,
        hero_image_url: Optional[str] = None,
        media_assets: Optional[List[Dict[str, Any]]] = None,
        description_short: Optional[str] = None,
        description_long: Optional[str] = None,
        official_specs: Optional[Dict[str, Any]] = None,
        quality_score: float = 100.0,
        data_completeness: float = 0.0,
        color_hint: Optional[str] = None,
        feature_list: Optional[List[str]] = None,
    ):
        self.halilit_id = halilit_id
        self.name = name
        self.brand = brand
        self.category = category
        self.subcategory = subcategory
        self.price_il = price_il
        self.price_eilat = price_eilat
        self.display_role = display_role
        self.display_tier_level = display_tier_level
        self.hero_image_url = hero_image_url
        self.media_assets = media_assets or []
        self.description_short = description_short
        self.description_long = description_long
        self.official_specs = official_specs or {}
        self.quality_score = quality_score
        self.data_completeness = data_completeness
        self.color_hint = color_hint
        self.feature_list = feature_list or []
        self.validation_status = "APPROVED"
        self.data_provenance = {
            "source": "ingestion_pipeline",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "halilit_id": self.halilit_id,
            "name": self.name,
            "brand": self.brand,
            "category": self.category,
            "subcategory": self.subcategory,
            "price_il": self.price_il,
            "price_eilat": self.price_eilat,
            "display_role": self.display_role,
            "display_tier_level": self.display_tier_level,
            "hero_image_url": self.hero_image_url,
            "media_assets": self.media_assets,
            "description_short": self.description_short,
            "description_long": self.description_long,
            "official_specs": self.official_specs,
            "quality_score": self.quality_score,
            "data_completeness": self.data_completeness,
            "color_hint": self.color_hint,
            "feature_list": self.feature_list,
            "validation_status": self.validation_status,
            "data_provenance": self.data_provenance,
        }


class PriceTrack:
    """Price tier track for Spectrum display"""

    def __init__(
        self,
        tier: str,
        tier_label: str,
        price_range: tuple,
        tier_level: int = 3,
        description: str = "",
    ):
        self.tier = tier
        self.tier_label = tier_label
        self.price_range = price_range
        self.tier_level = tier_level
        self.description = description
        self.products: List[SpecProduct] = []

    def add_product(self, product: SpecProduct) -> None:
        """Add product to track"""
        self.products.append(product)

    def get_product_count(self) -> int:
        """Get number of products in track"""
        return len(self.products)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "tier": self.tier,
            "tier_label": self.tier_label,
            "price_range": self.price_range,
            "tier_level": self.tier_level,
            "description": self.description,
            "products": [p.to_dict() for p in self.products],
            "product_count": self.get_product_count(),
        }


class SpectrumPayload:
    """Complete Spectrum data payload"""

    def __init__(self, brand: str):
        self.brand = brand
        self.timestamp = datetime.utcnow().isoformat()
        self.tracks: Dict[str, PriceTrack] = {}
        self.total_products = 0

    def add_track(self, tier_key: str, track: PriceTrack) -> None:
        """Add price track"""
        self.tracks[tier_key] = track

    def get_track(self, tier_key: str) -> Optional[PriceTrack]:
        """Get track by tier key"""
        return self.tracks.get(tier_key)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "brand": self.brand,
            "timestamp": self.timestamp,
            "total_products": self.total_products,
            "tracks": {k: v.to_dict() for k, v in self.tracks.items()},
            "metadata": {
                "version": "v5.4",
                "schema": "spectrum-ingestion-v1",
                "created_at": self.timestamp,
            },
        }


class QualityReport:
    """Data quality report for Spectrum products"""

    def __init__(self, brand: str):
        self.brand = brand
        self.generated_at = datetime.utcnow().isoformat()
        self.total_products = 0
        self.approved_products = 0
        self.rejected_products = 0
        self.critical_errors: List[str] = []
        self.warnings: List[str] = []
        self.recommendations: List[str] = []
        self.average_quality_score = 0.0
        self.average_completeness = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "brand": self.brand,
            "generated_at": self.generated_at,
            "total_products": self.total_products,
            "approved_products": self.approved_products,
            "rejected_products": self.rejected_products,
            "overall_quality_score": self.average_quality_score,
            "average_completeness": self.average_completeness,
            "critical_errors": self.critical_errors,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }


class SpectrumAdapter:
    """Adapts ingestion output to Spectrum format"""

    def __init__(self):
        self.price_tier_mapping = {
            PricingTier.ENTRY: ("entry", "Entry Level", (0, 500), 1),
            PricingTier.MID: ("mid", "Mid-Range", (500, 1500), 2),
            PricingTier.PRO: ("pro", "Professional", (1500, 4000), 3),
            PricingTier.FLAGSHIP: ("flagship", "Flagship", (4000, 100000), 5),
            PricingTier.LEGACY: ("legacy", "Legacy", (0, 100000), 0),
        }

    def convert_ingestion_report(
        self, report: IngestionReport
    ) -> tuple[SpectrumPayload, QualityReport]:
        """
        Convert complete IngestionReport to Spectrum format

        Args:
            report: IngestionReport from orchestrator

        Returns:
            Tuple of (SpectrumPayload, QualityReport)
        """
        logger.info(f"Converting ingestion report for brand: {report.brand}")

        payload = SpectrumPayload(report.brand)
        quality = QualityReport(report.brand)

        # Initialize price tracks
        for tier, (key, label, range_, level) in self.price_tier_mapping.items():
            track = PriceTrack(key, label, range_, level)
            payload.add_track(key, track)

        # Process approved products
        for product in report.approved_products:
            spec_product = self._convert_product(product)
            tier_key = self._get_tier_key(product.pricing.tier)

            track = payload.get_track(tier_key)
            if track:
                track.add_product(spec_product)
                payload.total_products += 1
                quality.approved_products += 1

        # Track rejected products in quality report
        quality.rejected_products = len(report.rejected_products)
        quality.total_products = (
            quality.approved_products + quality.rejected_products
        )

        # Calculate quality metrics
        if report.approved_products:
            avg_quality = sum(
                p.quality_score for p in report.approved_products
            ) / len(report.approved_products)
            avg_completeness = sum(
                p.data_completeness for p in report.approved_products
            ) / len(report.approved_products)
            quality.average_quality_score = round(avg_quality, 2)
            quality.average_completeness = round(avg_completeness, 2)

        # Add recommendations from report
        quality.recommendations = report.recommendations

        logger.info(
            f"✅ Converted {payload.total_products} products "
            f"({quality.approved_products} approved, {quality.rejected_products} rejected)"
        )

        return payload, quality

    def _convert_product(self, product: IngestionProductDraft) -> SpecProduct:
        """Convert single IngestionProductDraft to SpecProduct"""

        # Extract display properties
        display_role = product.display.display_role
        # Handle both Enum and string values due to Pydantic use_enum_values config
        display_role_str = display_role if isinstance(display_role, str) else (
            display_role.value if display_role else "SPECIALIST")
        display_tier = product.display.display_tier_level or 3

        # Extract hero image
        hero_image = None
        if product.display.hero_image:
            hero_image = product.display.hero_image
        elif product.display.media_assets and len(product.display.media_assets) > 0:
            hero_image = product.display.media_assets[0].url if hasattr(
                product.display.media_assets[0], 'url') else None

        # Build media assets
        media_assets = []
        if product.display.media_assets:
            for asset in product.display.media_assets:
                if hasattr(asset, '__dict__'):
                    # Asset is a Pydantic model
                    media_assets.append(
                        {
                            "url": asset.url,
                            "type": asset.type if hasattr(asset, 'type') else "image",
                            "alt": asset.alt_text if hasattr(asset, 'alt_text') else product.product_name,
                            "priority": asset.priority if hasattr(asset, 'priority') else 0,
                        }
                    )
                else:
                    # Asset is a dict
                    media_assets.append(
                        {
                            "url": asset.get("url", ""),
                            "type": asset.get("type", "image"),
                            "alt": asset.get("alt", product.product_name),
                            "priority": asset.get("priority", 0),
                        }
                    )

        # Build feature list
        features = product.feature_list or []

        # Create SpecProduct
        return SpecProduct(
            halilit_id=product.halilit_id,
            name=product.product_name,
            brand=product.brand,
            category=product.taxonomy.canonical_category,
            subcategory=product.taxonomy.canonical_subcategory,
            price_il=product.pricing.price_il,
            price_eilat=product.pricing.price_eilat,
            display_role=display_role_str,
            display_tier_level=display_tier,
            hero_image_url=hero_image,
            media_assets=media_assets,
            description_short=product.description_short,
            description_long=product.description_long,
            official_specs=product.specifications.specs_dict or {},
            quality_score=round(product.quality_score * 100, 1),
            data_completeness=round(
                product.data_completeness * 100, 1),
            color_hint=product.display.color_hint,
            feature_list=features,
        )

    def _get_tier_key(self, tier: PricingTier) -> str:
        """Get tier key from PricingTier enum"""
        if tier in self.price_tier_mapping:
            return self.price_tier_mapping[tier][0]
        return "mid"  # Default to mid

    def organize_by_role(
        self, products: List[IngestionProductDraft]
    ) -> Dict[str, List[SpecProduct]]:
        """
        Organize products by display role

        Returns:
            Dict mapping display role to list of SpecProducts
        """
        organized = {
            "HERO": [],
            "CORNERSTONE": [],
            "SPECIALIST": [],
            "ENTRY": [],
            "HIDDEN": [],
        }

        for product in products:
            display_role = product.display.display_role
            role = display_role if isinstance(display_role, str) else (
                display_role.value if display_role else "SPECIALIST")
            spec_product = self._convert_product(product)
            if role in organized:
                organized[role].append(spec_product)
            else:
                organized["SPECIALIST"].append(spec_product)

        return organized

    def generate_display_metrics(
        self, payload: SpectrumPayload
    ) -> Dict[str, Any]:
        """
        Generate metrics for display optimization

        Returns:
            Dict with display metrics
        """
        metrics = {
            "total_products": payload.total_products,
            "products_by_tier": {},
            "products_by_role": {},
            "average_quality": 0.0,
            "hero_count": 0,
            "recommendations": [],
        }

        quality_scores = []
        role_counts = {"HERO": 0, "CORNERSTONE": 0,
                       "SPECIALIST": 0, "ENTRY": 0, "HIDDEN": 0}

        for track in payload.tracks.values():
            metrics["products_by_tier"][track.tier] = track.get_product_count()
            for product in track.products:
                quality_scores.append(product.quality_score)
                role_counts[product.display_role] = (
                    role_counts.get(product.display_role, 0) + 1
                )

        metrics["products_by_role"] = role_counts
        if quality_scores:
            metrics["average_quality"] = round(
                sum(quality_scores) / len(quality_scores), 2
            )

        metrics["hero_count"] = role_counts.get("HERO", 0)

        # Recommendations
        if role_counts["HERO"] == 0:
            metrics["recommendations"].append(
                "Consider promoting products to HERO role for better visibility"
            )
        if metrics["average_quality"] < 80:
            metrics["recommendations"].append(
                "Improve product data completeness to increase quality scores"
            )

        return metrics


# Singleton pattern
_adapter = None


def get_spectrum_adapter() -> SpectrumAdapter:
    """Get singleton SpectrumAdapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = SpectrumAdapter()
    return _adapter
