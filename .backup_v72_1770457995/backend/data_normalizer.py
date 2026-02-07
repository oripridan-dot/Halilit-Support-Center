#!/usr/bin/env python3
"""
Data Normalizer - Handles all product data transformation
Ensures products conform to IngestionProductDraft spec with proper image/price handling
Used by Conductor as the single source of truth for data normalization
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.ingestion.taxonomy_manager import get_taxonomy_manager

logger = logging.getLogger("DataNormalizer")


class DataNormalizer:
    """
    Orchestrated by Conductor to normalize all product data
    Ensures prices, images, and official specs are properly extracted and formatted
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

        # RE-CLASSIFY using the refined TaxonomyManager
        # This fixes categorization issues (e.g. Roland "Electronic Drums" overflow)
        # by using the solid anchor source of truth.
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
                "media_assets": official_images,  # All images available for UI
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

            # ===== FRONTEND-SPECIFIC FIELDS (for compatibility) =====
            # Top-level price for priceFormatter.ts
            "price": float(pricing_data.get("price_il", 0)),
            "currency": "ILS",
            # Image fields for imageResolver.ts
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
                    # Ensure required fields
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
                    # String URL - wrap in object
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
                # Add if not already present
                if not any(img["url"] == hero["url"] for img in images):
                    images.insert(0, hero)

        # Priority 3: media.gallery array (nested format)
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

        # Priority 4: direct image_url field (legacy)
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

        # Required fields
        required = ["halilit_id", "product_name",
                    "brand", "price_il", "official_images"]
        for field in required:
            if not product.get(field):
                errors.append(f"Missing required field: {field}")

        # Type checks
        if product.get("price_il") is not None and not isinstance(product["price_il"], (int, float)):
            errors.append(
                f"price_il must be numeric, got {type(product['price_il'])}")

        if not isinstance(product.get("official_images"), list):
            errors.append("official_images must be a list")

        return len(errors) == 0, errors
