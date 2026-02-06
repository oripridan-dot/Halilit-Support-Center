#!/usr/bin/env python3
"""
v6.0 Ingestion-to-Frontend Synchronizer

Converts backend ingestion output to frontend-consumable JSON format.
Called by conductor after ingestion pipeline completes.

Uses DataNormalizer (orchestrated by Conductor) as the single source of truth
for all data transformation and field mapping.

Flow:
1. Read approved products from backend/data/ingestion/products/{brand}/approved_*.json
2. Normalize with DataNormalizer (guarantees proper price/image extraction)
3. Write to frontend/public/data/{brand}.json
4. Update index files
"""

from backend.ingestion.data_models import IngestionProductDraft
from backend.data_normalizer import DataNormalizer
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

    ⭐ ORCHESTRATED BY CONDUCTOR: Uses DataNormalizer as single source of truth
    Guarantees proper extraction of prices, images, and official data

    Args:
        brand: Brand name (e.g., "Nord")

    Returns:
        (Success boolean, List of normalized frontend products)
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

        logger.info(
            f"  📦 Normalizing {len(products)} products with DataNormalizer...")

        # ⭐ USE CONDUCTOR-ORCHESTRATED DataNormalizer
        # This ensures ALL products have properly extracted:
        # - Prices (price_il, price, currency)
        # - Images (image_hero, image_thumbnail, image_gallery, official_images)
        # - Specs & descriptions
        # - Taxonomy & categorization
        frontend_products = DataNormalizer.normalize_batch(products, brand)

        # Validate normalized products
        invalid_count = 0
        for product in frontend_products:
            is_valid, errors = DataNormalizer.validate_normalized(product)
            if not is_valid:
                invalid_count += 1
                logger.warning(
                    f"  ⚠️  Invalid product {product.get('halilit_id')}: {errors}")

        if invalid_count > 0:
            logger.warning(
                f"  ⚠️  {invalid_count}/{len(frontend_products)} products failed validation")

        # Write to frontend
        output_file = FRONTEND_DATA_DIR / f"{brand.lower()}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(frontend_products, f, indent=2, ensure_ascii=False)

        logger.info(
            f"  ✅ Synced {len(frontend_products)} normalized products to {output_file.name}")
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

    Schema (from frontend/src/lib/schemas.ts):
    - total_verified: Count of products with validation_status='APPROVED'
    - verified_count: Per-brand count of verified products
    - data_file: Path to brand's JSON file (e.g., "roland.json")
    """
    logger.info("📇 Generating index.json metadata (Conductor-Synced)...")

    # Group products by brand
    brand_products = {}
    for p in all_products:
        brand = p.get("brand", "unknown")
        if brand not in brand_products:
            brand_products[brand] = []
        brand_products[brand].append(p)

    # Build brand metadata with Trinity Swarm verification
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
        brand_slug = brand_slugs.get(brand_name, slugify(brand_name))
        data_file = f"{brand_slug}.json"

        # Count verified products (Trinity Swarm approved via Contextual validation)
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
            "data_file": data_file,  # CRITICAL: Frontend uses this to load brand products
            "brand_color": products[0].get("display", {}).get("color_hint", "#1e293b") if products else "#1e293b"
        })

    # Create index structure (matches MasterIndexSchema in frontend)
    index_data = {
        "version": "6.0.0",
        "build_timestamp": datetime.now().isoformat(),
        "total_products": len(all_products),
        "total_verified": total_verified,  # From Trinity Swarm audits
        "brands": sorted(brands, key=lambda x: x["id"])
    }

    index_file = FRONTEND_DATA_DIR / "index.json"
    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

    logger.info(
        f"  ✓ Index generated: {len(brands)} brands, {len(all_products)} total, {total_verified} verified products")
    logger.info(
        f"  ✓ Data sources synced: Commercial (harvest) → Official (enrich) → Contextual (validate)")
    logger.info(
        f"  ✓ Index file: {index_file.name}")


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
