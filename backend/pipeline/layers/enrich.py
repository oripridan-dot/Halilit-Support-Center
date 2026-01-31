"""
Layer 2: Enrich - Add taxonomy mapping and tier assignment.

This layer is responsible for:
- Mapping raw categories to standardized taxonomy
- Computing data quality tier (Diamond/Gold/Silver/Bronze)
- Selecting hero/thumbnail images
- Generating short descriptions
- Outputting EnrichedProduct records
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

from ..config import config
from ..models import (
    NormalizedProduct,
    EnrichedProduct,
    ImageAsset,
    SpecItem,
    TierLevel,
    StockStatus,
)

logger = logging.getLogger(__name__)


# Standard taxonomy for audio equipment
TAXONOMY = {
    "Studio Monitors": [
        "studio monitor", "powered monitor", "active monitor",
        "nearfield", "midfield", "speaker", "5-inch", "8-inch",
        "reference monitor", "monitor speaker"
    ],
    "Subwoofers": [
        "subwoofer", "sub", "bass", "low frequency"
    ],
    "Headphones": [
        "headphone", "headphones", "earphone", "closed-back",
        "open-back", "studio headphones", "reference headphones"
    ],
    "Microphones": [
        "microphone", "mic", "condenser", "dynamic mic",
        "xlr microphone", "usb microphone", "ribbon mic"
    ],
    "Audio Interfaces": [
        "audio interface", "sound card", "usb interface",
        "daw controller", "i/o", "preamp"
    ],
    "Cables & Connectors": [
        "cable", "xlr cable", "jack", "rca", "connector",
        "patch cable", "instrument cable", "adapter"
    ],
    "Accessories": [
        "stand", "mount", "shock mount", "pop filter",
        "boom arm", "clip", "holder", "isolation pad"
    ],
}


class EnrichLayer:
    """
    Layer 2: Taxonomy mapping and tier assignment.
    """

    def __init__(self):
        self.output_dir = config.VALIDATED_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tier_thresholds = config.TIER_THRESHOLDS

    def process_products(
        self,
        brand_id: str,
        products: List[NormalizedProduct]
    ) -> List[EnrichedProduct]:
        """
        Enrich normalized products with taxonomy and tiers.

        Args:
            brand_id: Brand identifier
            products: List of normalized products

        Returns:
            List of enriched products
        """
        logger.info(f"🎯 Enriching {len(products)} products for {brand_id}")

        enriched = []

        for product in products:
            try:
                result = self._enrich_product(product)
                enriched.append(result)
            except Exception as e:
                logger.error(f"Error enriching {product.id}: {e}")

        # Save results
        self._save_results(brand_id, enriched)

        logger.info(f"✅ Enriched {len(enriched)} products")
        return enriched

    def _enrich_product(
        self,
        product: NormalizedProduct
    ) -> EnrichedProduct:
        """Enrich a single product."""

        # Taxonomy mapping
        category, confidence, subcategories = self._map_taxonomy(
            product.category,
            product.description,
            product.name
        )

        # Tier assignment
        tier, tier_score, tier_reasons = self._assign_tier(product)

        # Image selection
        image_hero, image_thumbnail, image_gallery = self._select_images(
            product.images)

        # Short description
        description_short = self._generate_short_description(
            product.description, product.name)

        # Convert specs to SpecItem format
        specs = {}
        for cat, items in product.specifications.items():
            specs[cat] = items if isinstance(items, list) else [
                SpecItem(key=k, value=v) if isinstance(v, str) else v
                for k, v in (items.items() if isinstance(items, dict) else [])
            ]

        return EnrichedProduct(
            id=product.id,
            brand_id=product.brand_id,
            sku=product.sku,
            name=product.name,
            name_he=product.name_he,
            category=category,
            subcategories=subcategories,
            taxonomy_confidence=confidence,
            tier=tier,
            tier_score=tier_score,
            tier_reasons=tier_reasons,
            description=product.description,
            description_short=description_short,
            price=product.price,
            currency=product.currency,
            stock_status=product.stock_status,
            image_hero=image_hero,
            image_thumbnail=image_thumbnail,
            image_gallery=image_gallery,
            color_primary=product.color_primary,
            specs=specs,
            pros=product.pros,
            cons=product.cons,
            expert_tips=product.expert_tips,
            official_url=product.official_url,
            purchase_url=product.purchase_url,
        )

    def _map_taxonomy(
        self,
        raw_category: str,
        description: str,
        name: str
    ) -> Tuple[str, float, List[str]]:
        """Map to standardized taxonomy."""

        search_text = f"{raw_category} {description} {name}".lower()
        matches = []

        for primary, keywords in TAXONOMY.items():
            for keyword in keywords:
                if keyword in search_text:
                    # Exact category match = higher confidence
                    is_exact = raw_category.lower() == primary.lower()
                    score = 0.95 if is_exact else (
                        0.85 if keyword in raw_category.lower() else 0.70)
                    matches.append((primary, keyword, score))

        if not matches:
            return (raw_category or "Other", 0.5, [])

        # Best match
        best = max(matches, key=lambda x: x[2])
        best_primary = best[0]
        best_score = best[2]

        # Collect subcategories
        subcats = list(set(
            m[1] for m in matches if m[0] == best_primary
        ))

        return (best_primary, min(best_score, 1.0), subcats)

    def _assign_tier(
        self,
        product: NormalizedProduct
    ) -> Tuple[TierLevel, int, List[str]]:
        """Calculate tier based on data quality."""

        score = 0
        reasons = []

        # Name quality (20 points)
        if product.name and len(product.name) >= 10:
            score += 20
            reasons.append("Complete product name")
        elif product.name:
            score += 10

        # Images (25 points)
        if product.images:
            hero_count = sum(1 for img in product.images if img.role == "hero")
            if hero_count > 0:
                score += 15
                reasons.append("Hero image present")
            if len(product.images) >= 3:
                score += 10
                reasons.append("Multiple product images")

        # Price (10 points)
        if product.price and product.price > 0:
            score += 10
            reasons.append("Price available")

        # Description (15 points)
        if product.description:
            if len(product.description) >= 100:
                score += 15
                reasons.append("Detailed description")
            elif len(product.description) >= 30:
                score += 8

        # Specifications (20 points)
        spec_count = sum(len(items)
                         for items in product.specifications.values())
        if spec_count >= 5:
            score += 20
            reasons.append("Comprehensive specifications")
        elif spec_count >= 2:
            score += 10

        # Context data (10 points)
        if product.pros or product.cons:
            score += 5
            reasons.append("Review insights available")
        if product.expert_tips:
            score += 5
            reasons.append("Expert tips available")

        # Determine tier
        tier = TierLevel.BRONZE
        for level, threshold in self.tier_thresholds.items():
            if score >= threshold:
                tier = TierLevel(level)
                break

        return (tier, score, reasons)

    def _select_images(
        self,
        images: List[ImageAsset]
    ) -> Tuple[ImageAsset, ImageAsset, List[ImageAsset]]:
        """Select hero, thumbnail, and gallery images."""

        if not images:
            return (None, None, [])

        # Find hero
        hero = None
        for img in images:
            if img.role == "hero":
                hero = img
                break
        if not hero:
            hero = images[0]

        # Thumbnail (could be separate or derived from hero)
        thumbnail = None
        for img in images:
            if img.role == "thumbnail":
                thumbnail = img
                break
        if not thumbnail and hero:
            # Create thumbnail from hero
            thumbnail = ImageAsset(
                url=hero.url,
                alt=hero.alt,
                role="thumbnail",
                width=200 if hero.width else None,
                height=150 if hero.height else None,
            )

        # Gallery (all non-hero images)
        gallery = [img for img in images if img != hero]

        return (hero, thumbnail, gallery)

    def _generate_short_description(
        self,
        description: str,
        name: str
    ) -> str:
        """Generate a short description (max 100 chars)."""

        if not description:
            return name[:100] if name else ""

        # Take first sentence or first 100 chars
        sentences = description.split('.')
        if sentences:
            first = sentences[0].strip()
            if len(first) <= 100:
                return first

        # Truncate at word boundary
        if len(description) <= 100:
            return description

        truncated = description[:97]
        last_space = truncated.rfind(' ')
        if last_space > 50:
            truncated = truncated[:last_space]

        return truncated + "..."

    def _save_results(
        self,
        brand_id: str,
        products: List[EnrichedProduct]
    ) -> None:
        """Save enriched products to JSON."""
        output_file = self.output_dir / f"{brand_id}-enriched.json"
        data = {
            "brand_id": brand_id,
            "enriched_at": datetime.utcnow().isoformat(),
            "product_count": len(products),
            "tier_summary": self._tier_summary(products),
            "products": [p.model_dump(mode='json') for p in products],
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.debug(f"Saved enriched data to {output_file}")

    def _tier_summary(
        self,
        products: List[EnrichedProduct]
    ) -> Dict[str, int]:
        """Count products by tier."""
        summary = {tier.value: 0 for tier in TierLevel}
        for p in products:
            summary[p.tier.value] += 1
        return summary
