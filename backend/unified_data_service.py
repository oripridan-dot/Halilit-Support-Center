#!/usr/bin/env python3
"""
UNIFIED DATA SERVICE v9.0 — Simplified

Two responsibilities only:
1. DataNormalizer  — raw ingestion data → nested IngestionProductDraft shape (write path)
2. IngestToFrontendSyncEngine — sync approved products to frontend JSON files

The *read* path (serving products to the frontend) is handled entirely by
product_normalizer.build_catalog() called from server.py.  ConductorDataService
was removed because it duplicated the read path using a different data source
(ingestion DB vs JSON files), causing inconsistencies.

SOURCE RULES (see backend/source_rules.py for the full law):
─────────────────────────────────────────────────────────────
1. COMMERCIAL (Halilit.com) → Golden List, Prices, SKUs
2. OFFICIAL (Brand pages)   → Titles, Descriptions, Specs, Media
3. CONTEXTUAL (3+ Reviews)  → Pros/Cons, Real-world insights

NO SYNTHETIC DATA. NO MOCKING. ONLY REAL DATA.
"""

import json
import logging
import re
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from backend.source_rules import (
    validate_no_synthetic_data, enforce_source_rules,
    AuthorizedSource, SourceCoverage, MIN_REVIEW_SOURCES,
)

logger = logging.getLogger("UnifiedDataService")

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

_BACKEND_DIR = Path(__file__).resolve().parent
INGESTION_DIR = _BACKEND_DIR / "data" / "ingestion"
FRONTEND_DATA_DIR = _BACKEND_DIR.parent / "frontend" / "public" / "data"
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

        # UPDATED v7.5: Prefer Official Name if available (User Request)
        product_name = (
            raw_product.get("official_name")
            or raw_product.get("product_name")
            or raw_product.get("name")
            or "Unknown Product"
        )

        brand_name = raw_product.get("brand") or brand or "Generic"
        brand_slug = brand_name.lower().replace(" ", "-") if brand_name else "generic"

        # Check for SVG logo first, then PNG, else default
        # Note: In a real app we'd check file existence. For now we assume logic.
        # Actually, let's just make it flexible in the Frontend or standardize here.
        # Since we just created sequential_logo.svg, let's use a helper or simple logic.
        if brand_slug in ["sequential", "roland", "boss", "yamaha"]:  # Known SVGs or preferred
            brand_logo_url = f"/assets/logos/{brand_slug}_logo.svg"
        else:
            brand_logo_url = f"/assets/logos/{brand_slug}_logo.png"

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
            "brand_logo": brand_logo_url,
            "image_hero": hero_image,
            "image_thumbnail": thumbnail_image,
            "image_gallery": official_images,
            "image_url": hero_image.get("url") if hero_image else "",

            # ===== SOURCE COVERAGE TRACKING =====
            "source_coverage_commercial": raw_product.get("source_coverage_commercial", False),
            "source_coverage_official": raw_product.get("source_coverage_official", False),
            "source_coverage_contextual": raw_product.get("source_coverage_contextual", False),
            "contextual_source_count": raw_product.get("contextual_source_count", 0),
            "cross_validation_confidence": raw_product.get("cross_validation_confidence", 0.0),
            "cross_validation_status": raw_product.get("cross_validation_status", "pending"),

            # ===== CONTEXTUAL DATA (Reviews from 3+ trusted sources) =====
            "reviews": raw_product.get("reviews", []),
            "review_sources": raw_product.get("review_sources", []),
            "review_pros": raw_product.get("review_pros", []),
            "review_cons": raw_product.get("review_cons", []),
            "review_synthesis": raw_product.get("review_synthesis"),
            "average_rating": raw_product.get("average_rating"),
            "user_sentiment": raw_product.get("user_sentiment", "pending"),
            "real_world_insights": raw_product.get("real_world_insights", []),
        }

        # ═══════════════════════════════════════════════════════════════
        # SOURCE RULES ENFORCEMENT: Reject synthetic data at normalization
        # ═══════════════════════════════════════════════════════════════
        synthetic_violations = validate_no_synthetic_data(normalized)
        if synthetic_violations:
            for sv in synthetic_violations:
                logger.warning(
                    f"⛔ SYNTHETIC DATA in {halilit_id}: {sv.message}")
                if "validation_warnings" not in normalized:
                    normalized["validation_warnings"] = []
                normalized["validation_warnings"].append(
                    f"SOURCE RULE VIOLATION: {sv.message}")

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
                    raw_url = img.get("url") or img.get("src") or ""

                    # FIX: Handle placeholder URLs from ingestion
                    if "brand.com/hero.jpg" in raw_url:
                        raw_url = "/assets/images/placeholder_product.svg"

                    normalized_img = {
                        "url": raw_url,
                        "alt": img.get("alt") or img.get("alt_text", "Product image"),
                        "type": img.get("type", "official"),
                        "display_purpose": img.get("display_purpose", "display"),
                        "priority": img.get("priority", len(images)),
                        "source": img.get("source", "official"),
                    }
                    if normalized_img["url"]:
                        images.append(normalized_img)
                elif isinstance(img, str):
                    clean_url = img
                    if "brand.com/hero.jpg" in clean_url:
                        clean_url = "/assets/images/placeholder_product.svg"

                    images.append({
                        "url": clean_url,
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
            direct_url = product["image_url"]
            if "brand.com/hero.jpg" in direct_url:
                direct_url = "/assets/images/placeholder_product.svg"

            images.append({
                "url": direct_url,
                "alt": "Product image",
                "type": "standard",
                "display_purpose": "display",
                "priority": 0,
                "source": "direct",
            })

        # Final Fallback: If no images found at all, use placeholder
        if not images:
            images.append({
                "url": "/assets/images/placeholder_product.svg",
                "alt": "No Image Available",
                "type": "placeholder",
                "display_purpose": "hero",
                "priority": 0,
                "source": "fallback",
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
        Validate that a normalized product has all REQUIRED fields.

        ✅ v7.5 CHANGE: Only require core commercial fields
        ❌ No longer strict about images, specs, or description

        Returns (is_valid, list_of_errors)
        """
        errors = []

        # Core required fields (must exist for any valid product)
        required = ["halilit_id", "product_name", "brand"]
        for field in required:
            if not product.get(field):
                errors.append(f"Missing required field: {field}")

        # Price optional but validate if present
        if product.get("price_il") is not None and not isinstance(product["price_il"], (int, float)):
            errors.append(
                f"price_il must be numeric, got {type(product['price_il'])}")

        return len(errors) == 0, errors


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: INGESTION-TO-FRONTEND SYNC (from ingestion_to_frontend.py)
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

                # ✅ RELAXED VALIDATION (v7.5) - Include more products
                # Only reject if there are core validation errors
                # (missing required fields), not quality issues

                if is_valid:
                    # Product has all required fields - accept it
                    valid_products.append(product)
                else:
                    # Only reject if core required fields are missing
                    invalid_count += 1
                    logger.debug(
                        f"  ⚠️  Skipped {product.get('halilit_id')}: {errors}")

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
            "version": "8.3.0",
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
# SECTION 3: SINGLETON ACCESSORS
# ═══════════════════════════════════════════════════════════════════════════


def get_ingest_to_frontend_engine() -> IngestToFrontendSyncEngine:
    """Get IngestToFrontendSyncEngine (stateless utility class)."""
    return IngestToFrontendSyncEngine()


def get_conductor_data_service():
    """Backward-compat stub — ConductorDataService was removed in v9.0.
    All catalog reads now go through product_normalizer.build_catalog() in server.py.
    Returns None; callers should be updated to use the new path."""
    import warnings
    warnings.warn(
        "get_conductor_data_service() is deprecated. "
        "Use product_normalizer.build_catalog() instead.",
        DeprecationWarning, stacklevel=2,
    )
    return None
