#!/usr/bin/env python3
"""
v6.0 Ingestion-to-Frontend Synchronizer

Converts backend ingestion output to frontend-consumable JSON format.
Called by conductor after ingestion pipeline completes.

Flow:
1. Read approved products from backend/data/ingestion/products/{brand}/approved_*.json
2. Extract product data into frontend format
3. Write to frontend/public/data/{brand}.json
4. Update index files
"""

from backend.ingestion.data_models import IngestionProductDraft
import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

import re

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IngestToFrontend")

INGESTION_DIR = Path(
    "/workspaces/Halilit-Support-Center/backend/data/ingestion")
FRONTEND_DATA_DIR = Path(
    "/workspaces/Halilit-Support-Center/frontend/public/data")


def slugify(text: str) -> str:
    if not text:
        return "unknown"
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def sync_brand_to_frontend(brand: str) -> tuple[bool, List[Dict[str, Any]]]:
    """
    Sync approved products from ingestion to frontend format.

    Maps backend schema to IngestionProductDraft (the source of truth for frontend).

    Args:
        brand: Brand name (e.g., "Nord")

    Returns:
        (Success boolean, List of frontend products)
    """
    try:
        brand_dir = INGESTION_DIR / "products" / brand

        # Find the latest approved_*.json file
        if not brand_dir.exists():
            logger.warning(f"No product directory for {brand}")
            return False, []

        approved_files = sorted(brand_dir.glob(
            "approved_*.json"), reverse=True)
        if not approved_files:
            logger.warning(f"No approved products file for {brand}")
            return False, []

        approved_file = approved_files[0]  # Latest file

        # Load approved products
        with open(approved_file) as f:
            approved_data = json.load(f)

        if isinstance(approved_data, dict) and "products" in approved_data:
            products = approved_data["products"]
        else:
            products = approved_data if isinstance(approved_data, list) else []

        # Convert to FRONTEND SCHEMA (IngestionProductDraft)
        frontend_products = []
        for p in products:
            # Extract main fields
            halilit_id = p.get("halilit_id") or p.get("id")
            product_name = p.get("product_name") or p.get(
                "name", "Unknown Product")
            brand_name = p.get("brand", "Generic")

            # Extract pricing data
            pricing = p.get("pricing", {})
            price_il = pricing.get("price_il") or p.get(
                "price_il") or p.get("price", 0)
            price_eilat = pricing.get("price_eilat") or p.get("price_eilat", 0)

            # Extract taxonomy
            taxonomy = p.get("taxonomy", {})

            # Extract display data
            display = p.get("display", {})

            # Properly map to IngestionProductDraft schema
            fp = {
                # ===== CORE COMMERCIAL DATA (Halilit) =====
                "halilit_id": str(halilit_id) if halilit_id else "unknown",
                "product_name": product_name,
                "brand": brand_name,
                "price_il": float(price_il) if price_il else 0,
                "price_eilat": float(price_eilat) if price_eilat else 0,
                "halilit_url": p.get("halilit_url", ""),

                # ===== OPTIONAL IDS =====
                "sku": p.get("sku") or p.get("model_number"),
                "model_number": p.get("model_number"),
                "official_name": p.get("official_name"),

                # ===== OFFICIAL SPECS (Brand Source) =====
                "official_specs": p.get("official_specs") or {},
                "official_description": p.get("official_description"),
                "official_images": p.get("official_images") or [],
                "official_url": p.get("official_url"),

                # ===== REVIEWS & RATINGS =====
                "reviews": p.get("reviews") or [],
                "review_synthesis": p.get("review_synthesis"),
                "average_rating": p.get("average_rating"),

                # ===== WORKFLOW STATUS =====
                "status": p.get("status", "approved"),
                "pipeline_phase": p.get("pipeline_phase"),
                "created_at": p.get("created_at"),
                "last_updated": p.get("last_updated"),

                # ===== TAXONOMY MAPPING =====
                "taxonomy": taxonomy or {},

                # ===== PRICING DATA =====
                "pricing": {
                    "price_il": float(price_il) if price_il else 0,
                    "price_eilat": float(price_eilat) if price_eilat else 0,
                    "price_usd": pricing.get("price_usd"),
                    "price_eur": pricing.get("price_eur"),
                    "tier": pricing.get("tier", "entry"),
                    "eilat_discount_percent": pricing.get("eilat_discount_percent", 0),
                    "suggested_tier": pricing.get("suggested_tier"),
                    "price_validity_marker": pricing.get("price_validity_marker"),
                    "last_price_change": pricing.get("last_price_change"),
                    "previous_price_il": pricing.get("previous_price_il"),
                } or None,

                # ===== DISPLAY PROPERTIES =====
                "display": {
                    "display_role": display.get("display_role", "entry"),
                    "hero_image": display.get("hero_image"),
                    "thumbnail_image": display.get("thumbnail_image"),
                    "should_highlight": display.get("should_highlight", False),
                    "display_tier_level": display.get("display_tier_level", 0),
                    "color_hint": display.get("color_hint"),
                    "media_assets": display.get("media_assets", []),
                } or None,

                # ===== SPECIFICATIONS =====
                "specifications": p.get("specifications") or {},
                "description_short": p.get("description_short"),
                "description_long": p.get("description_long"),
                "feature_list": p.get("feature_list") or [],

                # ===== SOURCE TRACKING =====
                "sources": p.get("sources") or [],
                "primary_source": p.get("primary_source"),
                "lineage": p.get("lineage"),
                "raw_snapshot": p.get("raw_snapshot"),

                # ===== QUALITY METRICS =====
                "data_completeness": p.get("data_completeness", 0.5),
                "quality_score": p.get("quality_score", 0.5),
                "validation_status": p.get("validation_status", "approved"),
                "validation_errors": p.get("validation_errors", []),
                "validation_warnings": p.get("validation_warnings", []),
            }

            frontend_products.append(fp)

        # Write to frontend
        output_file = FRONTEND_DATA_DIR / f"{brand.lower()}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(frontend_products, f, indent=2, ensure_ascii=False)

        logger.info(
            f"  ✓ Synced {len(frontend_products)} products to {output_file.name}")
        return True, frontend_products

    except Exception as e:
        logger.error(f"  ✗ Failed to sync {brand}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False, []


def generate_smart_artifacts(all_products: List[Dict[str, Any]]):
    """
    Generate optimized artifacts for the "Advanced Pre-Processing" strategy.

    1. search_index_min.json (Lightweight search index)
    2. shards/{category}.json (Category-specific shards)
    3. galaxy_db.json (Full fallback)
    """
    logger.info("🧠 Generating Smart Artifacts (Search Index & Shards)...")

    # 1. Search Index (Minified) - using correct field names
    search_index = []
    for p in all_products:
        # Create minimal search object as per strategy (using correct IngestionProductDraft field names)
        search_item = {
            "id": p.get("halilit_id"),           # Correct field name
            "t": p.get("product_name"),          # Title/Name
            # Section/Category
            "s": p.get("taxonomy", {}).get("canonical_category") or "Uncategorized",
            "b": p.get("brand")                  # Brand
        }
        search_index.append(search_item)

    search_index_file = FRONTEND_DATA_DIR / "search_index_min.json"
    with open(search_index_file, 'w') as f:
        json.dump(search_index, f, separators=(',', ':'), ensure_ascii=False)
    logger.info(
        f"  ✓ Validated Search Index: {len(search_index)} items -> {search_index_file.name}")

    # 2. Category Shards
    shards_dir = FRONTEND_DATA_DIR / "shards"
    shards_dir.mkdir(parents=True, exist_ok=True)

    shards = {}
    for p in all_products:
        # Use taxonomy for category (frontend canonical source)
        cat = p.get("taxonomy", {}).get("canonical_category") if isinstance(
            p.get("taxonomy"), dict) else None
        if not cat:
            cat = "uncategorized"

        cat_slug = slugify(cat)

        if cat_slug not in shards:
            shards[cat_slug] = []
        shards[cat_slug].append(p)

    for cat_slug, products in shards.items():
        shard_file = shards_dir / f"{cat_slug}.json"
        with open(shard_file, 'w') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)

    logger.info(f"  ✓ Generated {len(shards)} category shards")

    # 3. Full Galaxy DB (Fallback) - contains full IngestionProductDraft schema
    galaxy_file = FRONTEND_DATA_DIR / "galaxy_db.json"
    with open(galaxy_file, 'w') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    logger.info(
        f"  ✓ Full DB Backup: {galaxy_file.name} ({len(all_products)} items)")


def generate_index_metadata(all_products: List[Dict[str, Any]]):
    """
    Generate index.json with accurate brand metadata.
    CRITICAL: Prevents catalogLoader from discovering stale data.
    """
    logger.info("📇 Generating index.json metadata...")

    # Group products by brand
    brand_products = {}
    for p in all_products:
        brand = p.get("brand", "unknown")
        if brand not in brand_products:
            brand_products[brand] = []
        brand_products[brand].append(p)

    # Build brand metadata
    brands = []
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
        brand_slug = brand_slugs.get(brand_name, slugify(brand_name))
        brands.append({
            "id": brand_slug,
            "name": brand_name,
            "product_count": len(products),
            "primary_category": products[0].get("taxonomy", {}).get("canonical_category", "Unknown") if products else "Unknown"
        })

    # Create index structure
    index_data = {
        "version": "6.0.0",
        "build_timestamp": datetime.now().isoformat(),
        "total_products": len(all_products),
        "brands": sorted(brands, key=lambda x: x["id"])
    }

    index_file = FRONTEND_DATA_DIR / "index.json"
    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

    logger.info(
        f"  ✓ Index generated: {len(brands)} brands, {len(all_products)} products -> index.json")


def sync_all_brands() -> Dict[str, bool]:
    """Sync all brands."""
    logger.info("📊 Syncing ingestion output to frontend...")

    # Find all brands with approved products
    products_dir = INGESTION_DIR / "products"
    if not products_dir.exists():
        logger.warning("No ingestion products directory")
        return {}

    results = {}
    all_products_collected = []

    for brand_dir in products_dir.iterdir():
        if brand_dir.is_dir():
            brand = brand_dir.name
            success, brand_products = sync_brand_to_frontend(brand)
            results[brand] = success
            if success:
                all_products_collected.extend(brand_products)

    success_count = sum(1 for v in results.values() if v)
    logger.info(f"✅ Synced {success_count}/{len(results)} brands")

    # Generate Advanced Artifacts
    if all_products_collected:
        generate_smart_artifacts(all_products_collected)
        generate_index_metadata(all_products_collected)

    # Generate Manifest Report
    generate_manifest_report(results)

    return results


def generate_manifest_report(sync_results: Dict[str, bool]):
    """
    Generate a human-readable Quality Report (HTML).
    Process: A human must click "Approve" (conceptually) on this report before live push.
    """
    logger.info("📝 Generating Manifest Report...")

    report_file = INGESTION_DIR / "reports" / "ingestion_report.html"
    report_file.parent.mkdir(parents=True, exist_ok=True)

    total_products = 0
    warnings_list = []
    missing_images_list = []

    # Iterate all brands
    products_dir = INGESTION_DIR / "products"
    if products_dir.exists():
        for brand_dir in products_dir.iterdir():
            if brand_dir.is_dir():
                brand = brand_dir.name
                # Load latest approved data
                approved_files = sorted(brand_dir.glob(
                    "approved_*.json"), reverse=True)
                if not approved_files:
                    continue

                try:
                    with open(approved_files[0]) as f:
                        data = json.load(f)
                        products = data.get("products", []) if isinstance(
                            data, dict) else data

                        total_products += len(products)

                        for p in products:
                            p_name = p.get("product_name") or p.get(
                                "name", "Unknown")
                            p_id = p.get("halilit_id") or p.get("id", "??")

                            # Check warnings
                            p_warnings = p.get("validation_warnings", [])
                            if p_warnings:
                                warnings_list.append({
                                    "id": p_id,
                                    "name": p_name,
                                    "brand": brand,
                                    "warnings": p_warnings
                                })

                            # Check images (simplified check)
                            images = p.get("official_images") or []
                            if not images:
                                # Also check if media_assets in display
                                display = p.get("display", {})
                                if not display.get("media_assets"):
                                    missing_images_list.append({
                                        "id": p_id,
                                        "name": p_name,
                                        "brand": brand
                                    })
                except Exception as e:
                    logger.error(f"Error reading {brand} for report: {e}")

    # Build HTML
    html = f"""
    <html>
    <head>
        <title>Ingestion Manifest Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
        <style>
            body {{ font-family: sans-serif; padding: 20px; }}
            .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .warning {{ color: #d35400; }}
            .error {{ color: #c0392b; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>Ingestion Quality Report</h1>
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p><strong>Total Products Processed:</strong> {total_products}</p>
            <p><strong>Products with Warnings:</strong> {len(warnings_list)}</p>
            <p><strong>Products Missing Images:</strong> {len(missing_images_list)}</p>
        </div>
        
        <h3>⚠️ Validation Warnings</h3>
        <table>
            <tr><th>ID</th><th>Brand</th><th>Product</th><th>Warnings</th></tr>
            {''.join(f"<tr><td>{w['id']}</td><td>{w['brand']}</td><td>{w['name']}</td><td class='warning'>{'; '.join(w['warnings'])}</td></tr>" for w in warnings_list)}
        </table>
        
        <h3>📷 Missing Images</h3>
        <table>
            <tr><th>ID</th><th>Brand</th><th>Product</th></tr>
            {''.join(f"<tr><td>{m['id']}</td><td>{m['brand']}</td><td>{m['name']}</td></tr>" for m in missing_images_list)}
        </table>
        
        <div style="margin-top: 30px; border-top: 2px solid #ccc; padding-top: 20px;">
            <p><em>Check this report before deploying to production.</em></p>
        </div>
    </body>
    </html>
    """

    with open(report_file, "w") as f:
        f.write(html)

    logger.info(f"📄 Report generated at: {report_file}")


if __name__ == "__main__":
    sync_all_brands()
    logger.info("Done!")
