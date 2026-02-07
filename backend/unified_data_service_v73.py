#!/usr/bin/env python3
"""
UNIFIED DATA SERVICE v7.3

Consolidated data pipeline that handles:
1. Product normalization (raw → IngestionProductDraft)
2. Data aggregation & filtering
3. Frontend synchronization

This file consolidates:
- conductor_data_service.py
- data_normalizer.py
- ingestion_to_frontend.py

Single source of truth for all product data processing in Halilit Support Center.
"""

import json
import logging
import re
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from backend.ingestion.ingestion_database import get_ingestion_database
from backend.ingestion.taxonomy_manager import get_taxonomy_manager

logger = logging.getLogger("UnifiedDataService")

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

INGESTION_DIR = Path(
    "/workspaces/Halilit-Support-Center/backend/data/ingestion")
FRONTEND_DATA_DIR = Path(
    "/workspaces/Halilit-Support-Center/frontend/public/data")

# Cache with 5-minute TTL
CACHE_TTL_SECONDS = 300
_catalog_cache = None
_cache_timestamp = None


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: DATA NORMALIZATION (from data_normalizer.py)
# ═══════════════════════════════════════════════════════════════════════════

class DataNormalizer:
    """
    Transforms raw product data to standardized IngestionProductDraft format.

    Features:
    - Extracts pricing from multiple source formats
    - Normalizes images (hero, thumbnail, gallery)
    - Re-classifies taxonomy using TaxonomyManager
    - Handles descriptions and specifications
    - Applies strict validation gates
    """

    @staticmethod
    def normalize_product(raw_product: Dict[str, Any], brand: str = "") -> Dict[str, Any]:
        """
        Normalize a raw product to IngestionProductDraft + frontend-compatible format

        Args:
            raw_product: Raw product data from any source
            brand: Brand name for context

        Returns:
            Fully normalized product dictionary
        """

        # ════════════════════════════════════════════════════════════════
        # PHASE 1: EXTRACT CORE IDENTIFIERS
        # ════════════════════════════════════════════════════════════════

        halilit_id = (
            raw_product.get("halilit_id")
            or raw_product.get("id")
            or raw_product.get("sku")
            or "unknown"
        )

        product_name = (
            raw_product.get("product_name")
            or raw_product.get("name")
            or raw_product.get("official_name")
            or "Unknown Product"
        )

        brand_name = raw_product.get("brand") or brand or "Generic"

        # ════════════════════════════════════════════════════════════════
        # PHASE 2: EXTRACT PRICING DATA (CRITICAL FOR UI)
        # ════════════════════════════════════════════════════════════════

        pricing_data = DataNormalizer._extract_pricing(raw_product)

        # ════════════════════════════════════════════════════════════════
        # PHASE 3: EXTRACT & NORMALIZE IMAGES (CRITICAL FOR UI)
        # ════════════════════════════════════════════════════════════════

        official_images = DataNormalizer._extract_images(raw_product)
        hero_image = official_images[0] if official_images else None
        thumbnail_image = (
            official_images[1] if len(official_images) > 1 else hero_image
        )

        # ════════════════════════════════════════════════════════════════
        # PHASE 4: EXTRACT DESCRIPTIONS & SPECS
        # ════════════════════════════════════════════════════════════════

        description_long = (
            raw_product.get("description_long")
            or raw_product.get("official_description")
            or raw_product.get("description")
            or ""
        )

        description_short = (
            raw_product.get("description_short")
            or (description_long[:200] + "..." if len(description_long) > 200 else description_long)
            or ""
        )

        official_specs = (
            raw_product.get("official_specs")
            or raw_product.get("specifications")
            or raw_product.get("specs")
            or {}
        )

        # ════════════════════════════════════════════════════════════════
        # PHASE 5: EXTRACT TAXONOMY & CATEGORIZATION
        # ════════════════════════════════════════════════════════════════

        try:
            tm = get_taxonomy_manager()
            cat, subcat, conf = tm.classify_product(
                product_name=product_name,
                brand=brand_name,
                description=description_long,
                specifications=official_specs
            )

            taxonomy = {
                "canonical_category": cat,
                "canonical_subcategory": subcat,
                "brand_taxonomy": raw_product.get("taxonomy", {}).get("brand_taxonomy"),
                "alt_categories": raw_product.get("taxonomy", {}).get("alt_categories", []),
                "keywords": raw_product.get("taxonomy", {}).get("keywords", [])
            }
        except Exception as e:
            logger.warning(f"Re-classification failed for {product_name}: {e}")
            taxonomy = raw_product.get("taxonomy", {})

        display = raw_product.get("display", {})

        # ════════════════════════════════════════════════════════════════
        # PHASE 6: BUILD NORMALIZED PRODUCT (IngestionProductDraft)
        # ════════════════════════════════════════════════════════════════

        normalized = {
            # ===== CORE COMMERCIAL DATA (Halilit) =====
            "halilit_id": str(halilit_id),
            "product_name": product_name,
            "brand": brand_name,
            "price_il": float(pricing_data.get("price_il", 0)),
            "price_eilat": float(pricing_data.get("price_eilat", 0)),
            "halilit_url": raw_product.get("halilit_url", ""),

            # ===== OPTIONAL IDS =====
            "sku": raw_product.get("sku") or raw_product.get("model_number"),
            "model_number": raw_product.get("model_number"),
            "official_name": raw_product.get("official_name"),

            # ===== OFFICIAL SPECS (Brand Source) =====
            "official_specs": official_specs,
            "official_description": raw_product.get("official_description"),
            "official_images": official_images,
            "official_url": raw_product.get("official_url"),

            # ===== REVIEWS & RATINGS =====
            "reviews": raw_product.get("reviews") or [],
            "review_synthesis": raw_product.get("review_synthesis"),
            "average_rating": raw_product.get("average_rating"),

            # ===== WORKFLOW STATUS =====
            "status": raw_product.get("status", "approved"),
            "pipeline_phase": raw_product.get("pipeline_phase", "complete"),
            "created_at": raw_product.get("created_at") or datetime.now().isoformat(),
            "last_updated": raw_product.get("last_updated") or datetime.now().isoformat(),

            # ===== TAXONOMY MAPPING =====
            "taxonomy": taxonomy or {},

            # ===== PRICING DATA (Structured) =====
            "pricing": {
                "price_il": float(pricing_data.get("price_il", 0)),
                "price_eilat": float(pricing_data.get("price_eilat", 0)),
                "price_usd": pricing_data.get("price_usd"),
                "price_eur": pricing_data.get("price_eur"),
                "tier": pricing_data.get("tier", "entry"),
                "eilat_discount_percent": pricing_data.get("eilat_discount_percent", 0),
                "suggested_tier": pricing_data.get("suggested_tier"),
                "price_validity_marker": pricing_data.get("price_validity_marker"),
                "last_price_change": pricing_data.get("last_price_change"),
                "previous_price_il": pricing_data.get("previous_price_il"),
            },

            # ===== DISPLAY PROPERTIES (For UI Rendering) =====
            "display": {
                "display_role": display.get("display_role", "standard"),
                "hero_image": hero_image,
                "thumbnail_image": thumbnail_image,
                "should_highlight": display.get("should_highlight", False),
                "display_tier_level": display.get("display_tier_level", 0),
                "color_hint": display.get("color_hint"),
                "media_assets": official_images,
            },

            # ===== DESCRIPTIONS & FEATURES =====
            "specifications": official_specs,
            "description_short": description_short,
            "description_long": description_long,
            "feature_list": raw_product.get("feature_list") or [],

            # ===== SOURCE TRACKING =====
            "sources": raw_product.get("sources") or [],
            "primary_source": raw_product.get("primary_source"),
            "lineage": raw_product.get("lineage"),
            "raw_snapshot": raw_product.get("raw_snapshot"),

            # ===== QUALITY METRICS =====
            "data_completeness": raw_product.get("data_completeness", 0.7),
            "quality_score": raw_product.get("quality_score", 0.7),
            "validation_status": raw_product.get("validation_status", "approved"),
            "validation_errors": raw_product.get("validation_errors", []),
            "validation_warnings": raw_product.get("validation_warnings", []),

            # ===== FRONTEND-SPECIFIC FIELDS =====
            "price": float(pricing_data.get("price_il", 0)),
            "currency": "ILS",
            "image_hero": hero_image,
            "image_thumbnail": thumbnail_image,
            "image_gallery": official_images,
            "image_url": hero_image.get("url") if hero_image else "",
        }

        return normalized

    @staticmethod
    def _extract_pricing(product: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize pricing from various sources"""

        # Priority 1: pricing object (already structured)
        if isinstance(product.get("pricing"), dict):
            pricing = product["pricing"].copy()
            if pricing.get("price_il") or pricing.get("price_eilat"):
                return pricing

        # Priority 2: top-level price_il / price_eilat (direct fields)
        if product.get("price_il") is not None:
            return {
                "price_il": float(product["price_il"]),
                "price_eilat": float(product.get("price_eilat", 0)),
                "tier": "entry",
            }

        # Priority 3: nested commercial pricing
        if isinstance(product.get("commercial"), dict):
            commercial = product["commercial"]
            if commercial.get("price"):
                return {
                    "price_il": float(commercial["price"]),
                    "price_eilat": float(commercial.get("price_eilat", 0)),
                    "tier": "entry",
                }

        # Priority 4: direct price field
        if product.get("price") is not None:
            return {
                "price_il": float(product["price"]),
                "price_eilat": 0,
                "tier": "entry",
            }

        # Default: no pricing
        logger.warning(
            f"No pricing found for {product.get('product_name', 'unknown')}")
        return {
            "price_il": 0,
            "price_eilat": 0,
            "tier": "entry",
        }

    @staticmethod
    def _extract_images(product: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and normalize images from various sources
        Returns list of image objects with required fields
        """

        images: List[Dict[str, Any]] = []

        # Priority 1: official_images array (already normalized)
        if isinstance(product.get("official_images"), list):
            for img in product["official_images"]:
                if isinstance(img, dict):
                    normalized_img = {
                        "url": img.get("url") or img.get("src") or "",
                        "alt": img.get("alt") or img.get("alt_text", "Product image"),
                        "type": img.get("type", "official"),
                        "display_purpose": img.get("display_purpose", "display"),
                        "priority": img.get("priority", len(images)),
                        "source": img.get("source", "official"),
                    }
                    if normalized_img["url"]:
                        images.append(normalized_img)
                elif isinstance(img, str):
                    images.append({
                        "url": img,
                        "alt": "Product image",
                        "type": "official",
                        "display_purpose": "display",
                        "priority": len(images),
                        "source": "official",
                    })

        # Priority 2: display.hero_image (single hero image)
        if isinstance(product.get("display"), dict):
            display = product["display"]
            if display.get("hero_image"):
                hero = {
                    "url": display["hero_image"],
                    "alt": "Hero image",
                    "type": "hero",
                    "display_purpose": "hero",
                    "priority": 0,
                    "source": "display",
                }
                if not any(img["url"] == hero["url"] for img in images):
                    images.insert(0, hero)

        # Priority 3: media.gallery array
        if isinstance(product.get("media"), dict):
            media = product["media"]
            if isinstance(media.get("gallery"), list):
                for idx, img_url in enumerate(media["gallery"]):
                    if img_url:
                        images.append({
                            "url": img_url,
                            "alt": "Gallery image",
                            "type": "gallery",
                            "display_purpose": "display",
                            "priority": len(images),
                            "source": "media",
                        })

        # Priority 4: direct image_url field
        if product.get("image_url") and not images:
            images.append({
                "url": product["image_url"],
                "alt": "Product image",
                "type": "standard",
                "display_purpose": "display",
                "priority": 0,
                "source": "direct",
            })

        return images

    @staticmethod
    def normalize_batch(
        products: List[Dict[str, Any]], brand: str = ""
    ) -> List[Dict[str, Any]]:
        """Normalize a batch of products"""
        normalized = []
        for product in products:
            try:
                normalized_product = DataNormalizer.normalize_product(
                    product, brand)
                normalized.append(normalized_product)
            except Exception as e:
                logger.error(
                    f"Failed to normalize product {product.get('halilit_id')}: {e}")
                continue
        return normalized

    @staticmethod
    def validate_normalized(product: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate that a normalized product has all required fields
        Returns (is_valid, list_of_errors)
        """
        errors = []

        required = ["halilit_id", "product_name",
                    "brand", "price_il", "official_images"]
        for field in required:
            if not product.get(field):
                errors.append(f"Missing required field: {field}")

        if product.get("price_il") is not None and not isinstance(product["price_il"], (int, float)):
            errors.append(
                f"price_il must be numeric, got {type(product['price_il'])}")

        if not isinstance(product.get("official_images"), list):
            errors.append("official_images must be a list")

        return len(errors) == 0, errors


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: CONDUCTOR DATA SERVICE (from conductor_data_service.py)
# ═══════════════════════════════════════════════════════════════════════════

class ConductorDataService:
    """
    Single source of truth for product data aggregation and filtering.
    All data delivered to frontend goes through Conductor verification.

    Features:
    - Aggregates all verified products
    - Provides flexible filtering
    - Manages cache
    - Returns canonical product structure
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.database = get_ingestion_database()
        self.taxonomy_manager = get_taxonomy_manager()
        self._catalog_cache = None
        self._cache_timestamp = None

    def get_unified_catalog(self) -> Dict[str, Any]:
        """
        Get all Conductor-verified products aggregated from all brands.

        Returns: {
            'products': [List of verified products],
            'metadata': {
                'total_products': count,
                'brands': [list of brands],
                'categories': {category -> count},
                'timestamp': when built,
                'source': 'conductor_verified'
            }
        }
        """
        # Check cache first
        now = datetime.utcnow()
        if self._catalog_cache and self._cache_timestamp:
            if (now - self._cache_timestamp).total_seconds() < CACHE_TTL_SECONDS:
                self.logger.info("✓ Returning cached catalog")
                return self._catalog_cache

        self.logger.info("🔄 Aggregating unified catalog from all brands...")

        all_products = []
        brands_set = set()
        categories_count = {}

        try:
            approved_products_by_brand = self.database.get_all_approved_products()

            for brand, products in approved_products_by_brand.items():
                if not products:
                    continue

                brands_set.add(brand)

                for product in products:
                    normalized = self._normalize_product(product, brand)
                    all_products.append(normalized)

                    category = normalized.get('taxonomy', {}).get(
                        'canonical_category', 'Uncategorized')
                    categories_count[category] = categories_count.get(
                        category, 0) + 1

            self.logger.info(
                f"✅ Aggregated {len(all_products)} products from {len(brands_set)} brands")

        except Exception as e:
            self.logger.error(f"❌ Aggregation failed: {e}")
            return self._empty_catalog()

        # Build response
        catalog = {
            'products': all_products,
            'metadata': {
                'total_products': len(all_products),
                'brands': sorted(list(brands_set)),
                'categories': categories_count,
                'timestamp': now.isoformat(),
                'source': 'conductor_verified',
                'verification_status': 'complete',
                'cache_ttl_seconds': CACHE_TTL_SECONDS
            }
        }

        # Cache it
        self._catalog_cache = catalog
        self._cache_timestamp = now

        return catalog

    def get_taxonomy_schema(self) -> Dict[str, Any]:
        """
        Get the taxonomy system for backend and frontend.

        Returns: {
            'universal_categories': [...],
            'all_brands': [...],
            'pricing_tiers': [...],
            'display_roles': [...]
        }
        """
        try:
            all_categories = self.taxonomy_manager.get_all_categories()

            universal_categories = []
            for category in all_categories:
                subcats = self.taxonomy_manager.get_subcategories(category)
                universal_categories.append({
                    'id': category.lower().replace(' ', '-'),
                    'name': category,
                    'subcategories': [
                        {
                            'id': subcat.lower().replace(' ', '-'),
                            'name': subcat
                        }
                        for subcat in subcats
                    ]
                })

            approved_by_brand = self.database.get_all_approved_products()
            all_brands = sorted(list(approved_by_brand.keys()))

            return {
                'universal_categories': universal_categories,
                'all_brands': all_brands,
                'pricing_tiers': ['entry', 'mid', 'pro', 'flagship', 'legacy'],
                'display_roles': ['hero', 'cornerstone', 'specialist', 'entry', 'hidden'],
                'statuses': ['harvested', 'enriched', 'validated', 'approved', 'rejected', 'archived'],
                'confidence_levels': ['official', 'trusted', 'commercial', 'user', 'inferred'],
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to get taxonomy schema: {e}")
            return {
                'universal_categories': [],
                'all_brands': [],
                'pricing_tiers': ['entry', 'mid', 'pro', 'flagship'],
                'display_roles': ['hero', 'cornerstone', 'specialist', 'entry'],
                'error': str(e)
            }

    def filter_products(
        self,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply flexible filtering to products.

        Supported filters:
        - brand: str or [str]
        - category: str or [str]
        - subcategory: str or [str]
        - pricing_tier: str or [str]
        - min_price / max_price: float
        - display_role: str or [str]
        - search_query: str

        Returns: {
            'products': [filtered],
            'filters_applied': {...},
            'total_results': count
        }
        """
        catalog = self.get_unified_catalog()
        products = catalog['products']
        filters_applied = {}

        # Apply each filter
        if 'brand' in filters:
            brands = filters['brand']
            if isinstance(brands, str):
                brands = [brands]
            brands_lower = [b.lower() for b in brands]
            products = [p for p in products if (
                p.get('brand', '').lower() in brands_lower)]
            filters_applied['brand'] = filters['brand']

        if 'category' in filters:
            categories = filters['category']
            if isinstance(categories, str):
                categories = [categories]
            categories_lower = [c.lower() for c in categories]
            products = [p for p in products if (
                p.get('taxonomy', {}).get('canonical_category',
                                          '').lower() in categories_lower
            )]
            filters_applied['category'] = filters['category']

        if 'search_query' in filters:
            query = filters['search_query'].lower()
            products = [p for p in products if self._matches_search(p, query)]
            filters_applied['search_query'] = filters['search_query']

        if 'pricing_tier' in filters:
            tiers = filters['pricing_tier']
            if isinstance(tiers, str):
                tiers = [tiers]
            products = [p for p in products if (
                p.get('pricing', {}).get('tier') in tiers
            )]
            filters_applied['pricing_tier'] = filters['pricing_tier']

        if 'min_price' in filters:
            min_price = float(filters['min_price'])
            products = [p for p in products if (
                p.get('pricing', {}).get('price_il', 0) >= min_price
            )]
            filters_applied['min_price'] = min_price

        if 'max_price' in filters:
            max_price = float(filters['max_price'])
            products = [p for p in products if (
                p.get('pricing', {}).get('price_il', float('inf')) <= max_price
            )]
            filters_applied['max_price'] = max_price

        if 'display_role' in filters:
            roles = filters['display_role']
            if isinstance(roles, str):
                roles = [roles]
            products = [p for p in products if (
                p.get('display', {}).get('display_role') in roles
            )]
            filters_applied['display_role'] = filters['display_role']

        return {
            'products': products,
            'filters_applied': filters_applied,
            'total_results': len(products),
            'source': 'conductor_verified'
        }

    def get_category_summary(self) -> Dict[str, Any]:
        """
        Get category summary for navigation/filtering UI.

        Returns: {
            'categories': [
                {
                    'name': str,
                    'product_count': int,
                    'brands': [str],
                    'subcategories': [str],
                    'avg_price': float
                }
            ]
        }
        """
        catalog = self.get_unified_catalog()
        products = catalog['products']

        categories = {}

        for product in products:
            cat = product.get('taxonomy', {}).get(
                'canonical_category', 'Uncategorized')
            subcat = product.get('taxonomy', {}).get('canonical_subcategory')
            brand = product.get('brand', 'Unknown')
            price = product.get('pricing', {}).get('price_il', 0)

            if cat not in categories:
                categories[cat] = {
                    'name': cat,
                    'product_count': 0,
                    'brands': set(),
                    'subcategories': set(),
                    'prices': []
                }

            categories[cat]['product_count'] += 1
            if brand:
                categories[cat]['brands'].add(brand)
            if subcat:
                categories[cat]['subcategories'].add(subcat)
            if price > 0:
                categories[cat]['prices'].append(price)

        # Convert to API format
        result = []
        for cat_name, cat_data in categories.items():
            result.append({
                'name': cat_name,
                'product_count': cat_data['product_count'],
                'brands': sorted(list(cat_data['brands'])),
                'subcategories': sorted(list(cat_data['subcategories'])),
                'avg_price': (sum(cat_data['prices']) / len(cat_data['prices']))
                if cat_data['prices'] else 0
            })

        return {
            'categories': sorted(result, key=lambda x: x['product_count'], reverse=True)
        }

    # =========================================================================
    # PRIVATE HELPERS
    # =========================================================================

    def _normalize_product(self, product: Dict[str, Any], brand: str) -> Dict[str, Any]:
        """Ensure product has canonical structure for frontend consumption."""
        return {
            'id': product.get('id') or product.get('halilit_id') or f"{brand}-{product.get('product_name')}",
            'product_name': product.get('product_name', 'Unknown'),
            'brand': product.get('brand', brand),
            'taxonomy': {
                'canonical_category': product.get('taxonomy', {}).get('canonical_category', 'Uncategorized'),
                'canonical_subcategory': product.get('taxonomy', {}).get('canonical_subcategory', ''),
                'keywords': product.get('taxonomy', {}).get('keywords', [])
            },
            'pricing': {
                'price_il': product.get('pricing', {}).get('price_il', 0),
                'price_eilat': product.get('pricing', {}).get('price_eilat', 0),
                'tier': product.get('pricing', {}).get('tier', 'mid'),
                'currency': 'NIS'
            },
            'display': {
                'display_role': product.get('display', {}).get('display_role', 'entry'),
                'hero_image': self._extract_image_url(product, 'hero'),
                'thumbnail_image': self._extract_image_url(product, 'thumbnail'),
                'color_hint': product.get('display', {}).get('color_hint'),
                'should_highlight': product.get('display', {}).get('should_highlight', False)
            },
            'specifications': product.get('specifications', {}) or product.get('specs_dict', {}),
            'description_short': product.get('description_short', ''),
            'description_long': product.get('description_long', ''),
            'validation_status': product.get('validation_status', 'approved'),
            'source': product.get('primary_source', {}).get('source_name', 'unknown'),
            'confidence': product.get('primary_source', {}).get('confidence', 'commercial')
        }

    def _extract_image_url(self, product: Dict[str, Any], purpose: str) -> Optional[str]:
        """Extract image URL from product media assets."""
        if 'display' in product:
            if purpose == 'hero' and product['display'].get('hero_image'):
                return product['display']['hero_image']
            if purpose == 'thumbnail' and product['display'].get('thumbnail_image'):
                return product['display']['thumbnail_image']

        media_assets = product.get('media_assets', []) or product.get(
            'display', {}).get('media_assets', [])
        for asset in media_assets:
            if asset.get('display_purpose') == purpose:
                return asset.get('url')

        return None

    def _matches_search(self, product: Dict[str, Any], query: str) -> bool:
        """Check if product matches search query."""
        searchable = [
            product.get('product_name', '').lower(),
            product.get('brand', '').lower(),
            product.get('taxonomy', {}).get('canonical_category', '').lower(),
            product.get('description_short', '').lower(),
        ]

        search_text = ' '.join(searchable)
        return query in search_text

    def _empty_catalog(self) -> Dict[str, Any]:
        """Return empty but valid catalog structure."""
        return {
            'products': [],
            'metadata': {
                'total_products': 0,
                'brands': [],
                'categories': {},
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'conductor_verified',
                'verification_status': 'error',
                'error': 'Failed to aggregate products'
            }
        }


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: INGESTION-TO-FRONTEND SYNC (from ingestion_to_frontend.py)
# ═══════════════════════════════════════════════════════════════════════════

class IngestToFrontendSyncEngine:
    """
    Converts backend ingestion output to frontend-consumable JSON format.

    Features:
    - Syncs approved products to frontend
    - Generates search artifacts (index, shards, galaxy_db)
    - Generates metadata and index files
    - Applies strict quality gates
    """

    @staticmethod
    def _slugify(text: str) -> str:
        """Convert text to URL-safe slug"""
        if not text:
            return "unknown"
        return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

    @classmethod
    def sync_brand_to_frontend(cls, brand: str) -> tuple[bool, List[Dict[str, Any]]]:
        """
        Sync approved products from ingestion to frontend format.

        Args:
            brand: Brand name (e.g., "Nord")

        Returns:
            (Success boolean, List of normalized frontend products)
        """
        try:
            brand_dir = INGESTION_DIR / "products" / brand

            if not brand_dir.exists():
                logger.warning(f"No product directory for {brand}")
                return False, []

            approved_files = sorted(brand_dir.glob(
                "approved_*.json"), reverse=True)
            if not approved_files:
                logger.warning(f"No approved products file for {brand}")
                return False, []

            approved_file = approved_files[0]

            with open(approved_file) as f:
                approved_data = json.load(f)

            if isinstance(approved_data, dict) and "products" in approved_data:
                products = approved_data["products"]
            else:
                products = approved_data if isinstance(
                    approved_data, list) else []

            logger.info(
                f"  📦 Normalizing {len(products)} products with DataNormalizer...")

            frontend_products = DataNormalizer.normalize_batch(products, brand)

            # Strict validation pass
            valid_products = []
            invalid_count = 0

            for product in frontend_products:
                is_valid, errors = DataNormalizer.validate_normalized(product)

                price_il = float(product.get('price_il', 0))
                official_images = product.get('official_images', [])
                data_completeness = float(product.get('data_completeness', 0))

                frontend_specific_errors = []

                if price_il < 500:
                    frontend_specific_errors.append(
                        f"Price too low ({price_il} NIS) - likely simulated data"
                    )

                if not official_images or len(official_images) == 0:
                    frontend_specific_errors.append(
                        "No images available for frontend display")

                if data_completeness < 0.4:
                    frontend_specific_errors.append(
                        f"Data incomplete ({data_completeness:.0%}) - requires 40% minimum"
                    )

                if is_valid and len(frontend_specific_errors) == 0:
                    valid_products.append(product)
                else:
                    invalid_count += 1
                    all_errors = errors + frontend_specific_errors
                    logger.warning(
                        f"  ⚠️  Invalid product {product.get('halilit_id')}: {all_errors}")

            logger.info(
                f"  ✅ After strict validation: {len(valid_products)}/{len(frontend_products)} products passed")

            output_file = FRONTEND_DATA_DIR / f"{brand.lower()}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w') as f:
                json.dump(valid_products, f, indent=2, ensure_ascii=False)

            logger.info(
                f"  ✅ Synced {len(valid_products)} high-quality products to {output_file.name}")
            return len(valid_products) > 0, valid_products

        except Exception as e:
            logger.error(f"  ✗ Failed to sync {brand}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False, []

    @classmethod
    def generate_smart_artifacts(cls, all_products: List[Dict[str, Any]]):
        """
        Generate optimized artifacts for the frontend data strategy.

        Creates:
        1. search_index_min.json (Lightweight search index)
        2. shards/{category}.json (Category-specific shards)
        3. galaxy_db.json (Full fallback)
        """
        logger.info("🧠 Generating Smart Artifacts (Search Index & Shards)...")

        # 1. Search Index (Minified)
        search_index = []
        for p in all_products:
            search_item = {
                "id": p.get("halilit_id"),
                "t": p.get("product_name"),
                "s": p.get("taxonomy", {}).get("canonical_category") or "Uncategorized",
                "b": p.get("brand")
            }
            search_index.append(search_item)

        search_index_file = FRONTEND_DATA_DIR / "search_index_min.json"
        with open(search_index_file, 'w') as f:
            json.dump(search_index, f, separators=(
                ',', ':'), ensure_ascii=False)
        logger.info(
            f"  ✓ Validated Search Index: {len(search_index)} items -> {search_index_file.name}")

        # 2. Category Shards
        shards_dir = FRONTEND_DATA_DIR / "shards"
        shards_dir.mkdir(parents=True, exist_ok=True)

        shards = {}
        for p in all_products:
            cat = p.get("taxonomy", {}).get("canonical_category") if isinstance(
                p.get("taxonomy"), dict) else None
            if not cat:
                cat = "uncategorized"

            cat_slug = cls._slugify(cat)

            if cat_slug not in shards:
                shards[cat_slug] = []
            shards[cat_slug].append(p)

        for cat_slug, products in shards.items():
            shard_file = shards_dir / f"{cat_slug}.json"
            with open(shard_file, 'w') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)

        logger.info(f"  ✓ Generated {len(shards)} category shards")

        # 3. Full Galaxy DB (Fallback)
        galaxy_file = FRONTEND_DATA_DIR / "galaxy_db.json"
        with open(galaxy_file, 'w') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        logger.info(
            f"  ✓ Full DB Backup: {galaxy_file.name} ({len(all_products)} items)")

    @classmethod
    def generate_index_metadata(cls, all_products: List[Dict[str, Any]]):
        """
        Generate index.json with accurate brand metadata.
        CRITICAL: Prevents catalogLoader from discovering stale data.
        """
        logger.info("📇 Generating index.json metadata (Conductor-Synced)...")

        brand_products = {}
        for p in all_products:
            brand = p.get("brand", "unknown")
            if brand not in brand_products:
                brand_products[brand] = []
            brand_products[brand].append(p)

        brands = []
        total_verified = 0
        brand_slugs = {
            "Drumdots": "drumdots",
            "Moog": "moog",
            "Nord": "nord",
            "Rode": "rode",
            "Roland": "roland",
            "Shure": "shure",
            "Universal Audio": "universal-audio"
        }

        for brand_name, products in brand_products.items():
            brand_slug = brand_slugs.get(brand_name, cls._slugify(brand_name))
            data_file = f"{brand_slug}.json"

            verified_count = sum(
                1 for p in products
                if p.get("validation_status", "").lower() == "approved"
            )
            total_verified += verified_count

            brands.append({
                "id": brand_slug,
                "name": brand_name,
                "product_count": len(products),
                "verified_count": verified_count,
                "primary_category": products[0].get("taxonomy", {}).get("canonical_category", "Unknown") if products else "Unknown",
                "data_file": data_file,
                "brand_color": products[0].get("display", {}).get("color_hint", "#1e293b") if products else "#1e293b"
            })

        index_data = {
            "version": "7.3.0",
            "build_timestamp": datetime.now().isoformat(),
            "total_products": len(all_products),
            "total_verified": total_verified,
            "brands": sorted(brands, key=lambda x: x["id"])
        }

        index_file = FRONTEND_DATA_DIR / "index.json"
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        logger.info(
            f"  ✓ Index generated: {len(brands)} brands, {len(all_products)} total, {total_verified} verified products")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: SINGLETON ACCESSORS
# ═══════════════════════════════════════════════════════════════════════════

_conductor_service = None


def get_conductor_data_service() -> ConductorDataService:
    """Get or create singleton instance of ConductorDataService."""
    global _conductor_service
    if _conductor_service is None:
        _conductor_service = ConductorDataService()
    return _conductor_service


def get_ingest_to_frontend_engine() -> IngestToFrontendSyncEngine:
    """Get IngestToFrontendSyncEngine (stateless utility class)."""
    return IngestToFrontendSyncEngine()
