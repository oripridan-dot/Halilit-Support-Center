"""
Layer 3: Optimize - Generate UI-ready JSON with component constraints.

This layer is responsible for:
- Validating against UI component requirements
- Generating URL slugs and search text
- Flattening specs for frontend consumption
- Creating filter tags
- Outputting OptimizedProduct records (final format)
"""

import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from ..config import config
from ..models import (
    EnrichedProduct,
    OptimizedProduct,
    ImageAsset,
    TierLevel,
)

logger = logging.getLogger(__name__)


# UI Component constraints
COMPONENT_CONSTRAINTS = {
    "galaxy_grid": {
        "max_title": 40,
        "max_description": 80,
        "required_fields": ["name", "category", "image_hero"],
    },
    "tier_scatter": {
        "max_title": 50,
        "max_description": 120,
        "required_fields": ["name", "price", "tier", "image_hero"],
    },
    "product_modal": {
        "max_title": 100,
        "max_description": 500,
        "required_fields": ["name", "description_full", "specs"],
    },
    "detail_panel": {
        "max_title": 60,
        "max_description": 300,
        "required_fields": ["name", "specs", "image_hero"],
    },
}


class OptimizeLayer:
    """
    Layer 3: UI optimization and final output generation.
    """

    def __init__(self):
        self.output_dir = config.GOLDEN_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_products(
        self,
        brand_id: str,
        products: List[EnrichedProduct]
    ) -> List[OptimizedProduct]:
        """
        Optimize enriched products for UI consumption.

        Args:
            brand_id: Brand identifier
            products: List of enriched products

        Returns:
            List of UI-optimized products
        """
        logger.info(f"⚡ Optimizing {len(products)} products for {brand_id}")

        optimized = []

        for product in products:
            try:
                result = self._optimize_product(product)
                optimized.append(result)
            except Exception as e:
                logger.error(f"Error optimizing {product.id}: {e}")

        # Save results
        self._save_results(brand_id, optimized)

        logger.info(f"✅ Optimized {len(optimized)} products")
        return optimized

    def _optimize_product(
        self,
        product: EnrichedProduct
    ) -> OptimizedProduct:
        """Optimize a single product for UI."""

        # Generate slug
        slug = self._generate_slug(product.brand_id, product.name)

        # Prepare images for JSON
        image_hero = self._image_to_dict(product.image_hero)
        image_thumbnail = self._image_to_dict(product.image_thumbnail)
        image_gallery = [self._image_to_dict(
            img) for img in product.image_gallery]

        # Flatten specs for UI
        specs = self._flatten_specs(product.specs)

        # Generate search text
        search_text = self._generate_search_text(product)

        # Generate filter tags
        filter_tags = self._generate_filter_tags(product)

        # Generate render hints
        render_hints = self._generate_render_hints(product)

        return OptimizedProduct(
            id=product.id,
            name=product.name,
            slug=slug,
            brand_id=product.brand_id,
            category=product.category,
            subcategories=product.subcategories,
            tier=product.tier.value,
            tier_score=product.tier_score,
            description_short=product.description_short[:100],
            description_full=product.description,
            price=product.price,
            currency=product.currency,
            stock_status=product.stock_status.value if hasattr(
                product.stock_status, 'value') else str(product.stock_status),
            image_hero=image_hero,
            image_thumbnail=image_thumbnail,
            image_gallery=image_gallery,
            color_primary=product.color_primary,
            specs=specs,
            pros=product.pros,
            cons=product.cons,
            expert_tips=product.expert_tips,
            search_text=search_text,
            filter_tags=filter_tags,
            render_hints=render_hints,
            source_url=product.official_url,
            purchase_url=product.purchase_url,
            synced_at=datetime.utcnow().isoformat(),
        )

    def _generate_slug(self, brand_id: str, name: str) -> str:
        """Generate URL-safe slug."""
        # Remove non-ASCII
        name_ascii = ''.join(c for c in name if ord(c) < 128)
        # Lowercase and replace spaces
        slug = name_ascii.lower().strip()
        # Remove special chars
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        # Replace spaces with hyphens
        slug = re.sub(r'\s+', '-', slug)
        # Remove multiple hyphens
        slug = re.sub(r'-+', '-', slug).strip('-')

        return f"/{brand_id}/{slug}"

    def _image_to_dict(self, image: ImageAsset) -> Dict[str, Any]:
        """Convert ImageAsset to dict for JSON."""
        if not image:
            return None
        return {
            "url": image.url,
            "alt": image.alt,
            "width": image.width,
            "height": image.height,
        }

    def _flatten_specs(
        self,
        specs: Dict[str, List[Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Flatten specs for frontend consumption."""
        result = {}

        for category, items in specs.items():
            result[category] = []
            for item in items:
                if hasattr(item, 'model_dump'):
                    spec_dict = item.model_dump()
                elif isinstance(item, dict):
                    spec_dict = item
                else:
                    continue

                # Build spec entry, excluding None values
                spec_entry: Dict[str, str] = {
                    "key": spec_dict.get('key', ''),
                    "value": spec_dict.get('value', ''),
                }
                # Only include unit if it's not None
                unit = spec_dict.get('unit')
                if unit is not None:
                    spec_entry["unit"] = str(unit)

                result[category].append(spec_entry)

        return result

    def _generate_search_text(self, product: EnrichedProduct) -> str:
        """Generate searchable text combining all relevant fields."""
        parts = [
            product.name,
            product.category,
            ' '.join(product.subcategories),
            product.description_short,
            product.brand_id.replace('-', ' '),
        ]

        # Add spec values
        for category, items in product.specs.items():
            for item in items:
                if hasattr(item, 'value'):
                    parts.append(item.value)
                elif isinstance(item, dict):
                    parts.append(item.get('value', ''))

        return ' '.join(filter(None, parts)).lower()

    def _generate_filter_tags(self, product: EnrichedProduct) -> List[str]:
        """Generate tags for filtering/faceting."""
        tags = [
            product.category.lower(),
            product.tier.value,
            product.brand_id,
        ]

        # Add subcategories
        tags.extend([s.lower() for s in product.subcategories])

        # Price range tags
        if product.price:
            if product.price < 100:
                tags.append("budget")
            elif product.price < 500:
                tags.append("mid-range")
            elif product.price < 1000:
                tags.append("professional")
            else:
                tags.append("premium")

        # Stock status
        if hasattr(product.stock_status, 'value'):
            tags.append(product.stock_status.value)

        return list(set(tags))

    def _generate_render_hints(self, product: EnrichedProduct) -> Dict[str, bool]:
        """Generate hints for UI rendering."""
        return {
            "has_hero_image": product.image_hero is not None,
            "has_gallery": len(product.image_gallery) > 0,
            "has_specs": len(product.specs) > 0,
            "has_price": product.price is not None and product.price > 0,
            "has_reviews": len(product.pros) > 0 or len(product.cons) > 0,
            "has_tips": len(product.expert_tips) > 0,
            "is_verified": product.tier in [TierLevel.DIAMOND, TierLevel.GOLD],
            "show_badge": product.tier == TierLevel.DIAMOND,
        }

    def validate_for_components(
        self,
        product: OptimizedProduct,
        components: List[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Validate product against component constraints."""

        if components is None:
            components = COMPONENT_CONSTRAINTS.keys()

        results = {}

        for component in components:
            constraints = COMPONENT_CONSTRAINTS.get(component)
            if not constraints:
                continue

            issues = []

            # Check title length
            if len(product.name) > constraints["max_title"]:
                issues.append(
                    f"Title exceeds {constraints['max_title']} chars")

            # Check description length
            desc_len = len(product.description_short)
            if desc_len > constraints["max_description"]:
                issues.append(
                    f"Description exceeds {constraints['max_description']} chars")

            # Check required fields
            for field in constraints["required_fields"]:
                value = getattr(product, field, None)
                if value is None or value == "" or value == []:
                    issues.append(f"Missing required field: {field}")

            results[component] = {
                "valid": len(issues) == 0,
                "issues": issues,
            }

        return results

    def _save_results(
        self,
        brand_id: str,
        products: List[OptimizedProduct]
    ) -> None:
        """Save optimized products to JSON."""
        output_file = self.output_dir / f"{brand_id}.json"
        data = {
            "brand": brand_id,
            "brand_name": brand_id.replace('-', ' ').title(),
            "product_count": len(products),
            "generated_at": datetime.utcnow().isoformat(),
            "products": [p.model_dump(mode='json') for p in products],
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved optimized catalog to {output_file}")
