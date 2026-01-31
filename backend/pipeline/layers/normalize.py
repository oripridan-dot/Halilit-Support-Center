"""
Layer 1: Normalize - Validate and merge data from 3 source pillars.

This layer is responsible for:
- Validating raw data against Pydantic schemas
- Merging Official + Commercial + Contextual into unified products
- Computing content hashes for change detection
- Outputting NormalizedProduct records
"""

import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..config import config
from ..models import (
    OfficialData,
    CommercialData,
    ContextualData,
    NormalizedProduct,
    ImageAsset,
    SpecItem,
    StockStatus,
)

logger = logging.getLogger(__name__)


class NormalizeLayer:
    """
    Layer 1: Merge and validate data from 3 pillars.

    Priority order (for conflicts):
      1. Official (manufacturer truth)
      2. Commercial (price/availability)
      3. Contextual (reviews/tips)
    """

    def __init__(self):
        self.output_dir = config.VALIDATED_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_brand(
        self,
        brand_id: str,
        official: List[OfficialData],
        commercial: List[CommercialData],
        contextual: List[ContextualData],
    ) -> List[NormalizedProduct]:
        """
        Merge data from 3 pillars into normalized products.

        Args:
            brand_id: Brand identifier
            official: List of official manufacturer data
            commercial: List of commercial/price data
            contextual: List of contextual/review data

        Returns:
            List of merged, validated NormalizedProduct records
        """
        logger.info(
            f"📋 Normalizing {brand_id}: {len(official)} official, {len(commercial)} commercial, {len(contextual)} contextual")

        # Index commercial and contextual by product ID for fast lookup
        commercial_index = self._index_by_product_id(commercial)
        contextual_index = self._index_by_product_id(contextual)

        products = []

        for off in official:
            product_id = self._generate_id(
                brand_id, off.manufacturer_sku, off.official_name)

            # Lookup related data
            comm = commercial_index.get(
                product_id) or commercial_index.get(off.manufacturer_sku)
            ctx = contextual_index.get(product_id)

            # Merge into normalized product
            try:
                normalized = self._merge_product(product_id, off, comm, ctx)
                products.append(normalized)
            except Exception as e:
                logger.error(f"Error normalizing {product_id}: {e}")

        # Save normalized data
        self._save_results(brand_id, products)

        logger.info(f"✅ Normalized {len(products)} products for {brand_id}")
        return products

    def _merge_product(
        self,
        product_id: str,
        official: OfficialData,
        commercial: Optional[CommercialData],
        contextual: Optional[ContextualData],
    ) -> NormalizedProduct:
        """Merge data from 3 pillars into a single product."""

        # Images from official source
        images = [
            ImageAsset(
                url=img.get('url', ''),
                alt=img.get('alt', official.official_name)[:100],
                role=img.get('role', 'detail'),
                width=img.get('width'),
                height=img.get('height'),
            )
            for img in official.images
            if img.get('url')
        ]

        # Specifications from official source
        specs = {}
        for category, items in official.specifications.items():
            specs[category] = [
                SpecItem(key=k, value=v)
                for k, v in items.items()
            ]

        # Commerce data
        price = None
        currency = "USD"
        stock_status = StockStatus.UNKNOWN
        purchase_url = None

        if commercial:
            price = commercial.price_usd or commercial.price_ils
            currency = "USD" if commercial.price_usd else "ILS"
            stock_status = commercial.stock_status
            purchase_url = commercial.product_url

        # Context data
        pros = []
        cons = []
        expert_tips = []
        review_sources = []

        if contextual:
            pros = contextual.pros
            cons = contextual.cons
            expert_tips = contextual.expert_tips
            review_sources = contextual.verified_sources

        return NormalizedProduct(
            id=product_id,
            brand_id=official.brand_id,
            sku=official.manufacturer_sku,
            name=official.official_name,
            category=official.category,
            subcategory=official.subcategory,
            description=official.description,
            price=price,
            currency=currency,
            stock_status=stock_status,
            images=images,
            specifications=specs,
            pros=pros,
            cons=cons,
            expert_tips=expert_tips,
            review_sources=review_sources,
            official_url=official.official_url,
            purchase_url=purchase_url,
        )

    def _index_by_product_id(
        self,
        items: List[Any]
    ) -> Dict[str, Any]:
        """Create lookup index by product_id."""
        index = {}
        for item in items:
            if hasattr(item, 'product_id'):
                index[item.product_id] = item
            elif hasattr(item, 'halilit_sku'):
                index[item.halilit_sku] = item
        return index

    def _generate_id(
        self,
        brand_id: str,
        sku: str,
        name: str
    ) -> str:
        """Generate a consistent product ID."""
        identifier = sku or name
        clean = re.sub(r'[^a-zA-Z0-9]', '-', identifier.lower())
        clean = re.sub(r'-+', '-', clean).strip('-')
        return f"{brand_id}-{clean}"

    def _save_results(
        self,
        brand_id: str,
        products: List[NormalizedProduct]
    ) -> None:
        """Save normalized products to JSON."""
        output_file = self.output_dir / f"{brand_id}-normalized.json"
        data = {
            "brand_id": brand_id,
            "normalized_at": datetime.utcnow().isoformat(),
            "product_count": len(products),
            "products": [p.model_dump(mode='json') for p in products],
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.debug(f"Saved normalized data to {output_file}")

    def load_from_files(
        self,
        brand_id: str,
        official_file: Path,
        commercial_file: Optional[Path] = None,
        contextual_file: Optional[Path] = None,
    ) -> List[NormalizedProduct]:
        """Load and normalize from JSON files."""

        # Load official
        with open(official_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            official = [OfficialData(**p) for p in data.get('products', [])]

        # Load commercial if available
        commercial = []
        if commercial_file and commercial_file.exists():
            with open(commercial_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                commercial = [CommercialData(**p)
                              for p in data.get('products', [])]

        # Load contextual if available
        contextual = []
        if contextual_file and contextual_file.exists():
            with open(contextual_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                contextual = [ContextualData(**p)
                              for p in data.get('products', [])]

        return self.process_brand(brand_id, official, commercial, contextual)
