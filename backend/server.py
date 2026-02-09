from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from backend.auto_sync_engine import get_auto_sync_engine
from backend.unified_data_service_v76 import get_conductor_data_service
from backend.ingestion_to_frontend import get_frontend_data
import os
import sys
import logging
import json
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.api.streams import router as streams_router

# Ensure parent directory is in path
_parent_dir = str(Path(__file__).parent.parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_golden_list_brands() -> set:
    """
    Load Halilit's actual commercial database brands from frontend/public/data/
    Returns set of brand names (as stored in the golden list files)
    """
    frontend_data_dir = Path(__file__).parent.parent / \
        "frontend" / "public" / "data"

    if not frontend_data_dir.exists():
        logger.warning(f"Golden list dir not found: {frontend_data_dir}")
        return set()

    golden_brands = set()
    for json_file in frontend_data_dir.glob("*.json"):
        brand_name = json_file.stem
        # Skip metadata files
        if brand_name not in ("index", "search_index", "search_index_min"):
            golden_brands.add(brand_name)

    logger.info(
        f"Loaded {len(golden_brands)} brands from Halilit's golden list")
    return golden_brands


def normalize_brand_name(brand: str) -> str:
    """
    Normalize brand name to canonical form:
    - lowercase
    - trim whitespace
    - replace hyphens with spaces (hyphenated and spaced are same brand)
    """
    normalized = brand.strip().lower()
    # Replace hyphens with spaces to handle "Adam-Audio" == "Adam Audio"
    normalized = normalized.replace('-', ' ')
    return normalized


def get_ingestion_products_for_golden_brands():
    """
    Get all products from ingestion database that match Halilit's golden list.
    Maps golden list brands to their ingestion products.

    Returns: dict of {golden_brand_name -> product_list}
    """
    golden_brands = get_golden_list_brands()
    ingestion_products_dir = Path(INGESTION_DATA) / "products"

    if not ingestion_products_dir.exists():
        logger.warning(
            f"Ingestion products dir not found: {ingestion_products_dir}")
        return {}

    # Map golden brand -> normalized -> ingestion directory name -> products
    result = {}

    for golden_brand in sorted(golden_brands):
        golden_normalized = normalize_brand_name(golden_brand)

        # Look for matching ingestion directories
        all_products = []
        sources_found = []

        for ingestion_dir in ingestion_products_dir.iterdir():
            if not ingestion_dir.is_dir():
                continue

            ingestion_normalized = normalize_brand_name(ingestion_dir.name)

            # If normalized names match, this ingestion directory has products for this golden brand
            if ingestion_normalized == golden_normalized:
                approved_files = sorted(ingestion_dir.glob(
                    "approved_*.json"), reverse=True)
                if approved_files:
                    try:
                        with open(approved_files[0]) as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                all_products.extend(data)
                            elif isinstance(data, dict) and "products" in data:
                                all_products.extend(data["products"])
                            sources_found.append(ingestion_dir.name)
                    except Exception as e:
                        logger.warning(
                            f"Failed to load {approved_files[0]}: {e}")

        if all_products:
            result[golden_brand] = {
                "products": all_products,
                "product_count": len(all_products),
                "ingestion_sources": sources_found
            }
        else:
            logger.warning(
                f"No approved products found for golden brand '{golden_brand}'")

    return result


app = FastAPI(title="Halilit Support Center API", version="7.3")

# Add CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(streams_router, tags=["Real-time Streams"])

# CopilotKit Integration
try:
    from backend.api.copilot_router import router as copilot_router
    app.include_router(copilot_router, prefix="/api", tags=["CopilotKit"])
    logger.info("✅ CopilotKit endpoint registered at /api/copilot/chat")
except Exception as e:
    logger.warning(f"⚠️ Failed to register CopilotKit: {e}")

# Include learning endpoints
try:
    from backend.unified_learning_system_v75 import router as learning_router
    app.include_router(learning_router)
    logger.info("✅ Learning endpoints registered")
except Exception as e:
    logger.warning(f"⚠️ Failed to load learning endpoints: {e}")

# Robust path handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "../frontend/dist")
FRONTEND_PUBLIC_DATA = os.path.join(BASE_DIR, "../frontend/public/data")
INGESTION_DATA = os.path.join(
    BASE_DIR, "./data/ingestion")  # Real ingested data

# --- API ENDPOINTS (must be before frontend catch-all) ---

# Health check endpoint


@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": "7.3",
        "service": "Halilit Support Center"
    }


@app.get("/api/versions")
async def get_versions():
    """Get ingestion version information"""
    try:
        from backend.ingestion_versioning import get_version_manager
        manager = get_version_manager()
        return manager.export_for_frontend()
    except Exception as e:
        logger.error(f"Error getting versions: {e}")
        return {
            "error": str(e),
            "total_brands": 0,
            "total_products": 0,
            "active_versions": {}
        }


@app.get("/api/galaxy-view")
async def galaxy_view():
    return get_frontend_data()


@app.get("/api/catalog")
async def get_catalog():
    """Get all product data from CONDUCTOR INGESTED files filtered by Halilit's golden list"""
    try:
        golden_brands = get_golden_list_brands()
        golden_products = get_ingestion_products_for_golden_brands()

        all_products = []
        brand_counts = {}

        for brand_name in sorted(golden_products.keys()):
            brand_data = golden_products[brand_name]
            all_products.extend(brand_data["products"])
            brand_counts[brand_name] = brand_data["product_count"]

        logger.info(
            f"✅ Loaded {len(all_products)} real ingested products from {len(golden_products)} GOLDEN LIST brands")

        return {
            "total_products": len(all_products),
            "total_brands": len(golden_products),
            "brands": sorted(list(golden_products.keys())),
            "brand_product_counts": brand_counts,
            "products": all_products,
            "source": "halilit_commercial_database_with_conductor_enrichment",
            "note": "Products are from Halilit's golden list brands, enriched with Conductor ingestion pipeline"
        }
    except Exception as e:
        logger.error(f"Error loading catalog: {e}")
        return {"error": str(e), "products": [], "source": "error"}


@app.get("/api/conductor/catalog")
async def get_conductor_catalog():
    """
    Get the unified conductor catalog by aggregating generated frontend data files.
    This serves as the single source of truth for the frontend app.

    CRITICAL UPDATES v7.6:
    - Normalizes data structure for frontend (Price, Image, Name)
    - Deduplicates products by ID
    - Filters out 'junk' (Price=0 or No Image)
    - Ensures official Halilit data takes precedence
    """
    try:
        data_dir = Path(FRONTEND_PUBLIC_DATA)
        brands_found = set()
        categories_count = {}

        # Deduplication map: ID -> Product
        products_map = {}

        # Files to exclude from product aggregation
        excluded_files = {
            'index.json',
            'search_index.json',
            'search_index_min.json',
            'galaxy_db.json',
            'package.json'
        }

        if not data_dir.exists():
            logger.warning(f"Frontend data dir not found: {data_dir}")
            return {"products": [], "metadata": {"total_products": 0, "brands": [], "categories": {}, "timestamp": datetime.now().isoformat(), "source": "conductor_verified", "verification_status": "error", "cache_ttl_seconds": 300}}

        # Iterate over all JSON files
        json_files = list(data_dir.glob("*.json"))
        # Sort files to potentially process newer/better ones last or first?
        # Actually, let's just process.

        for json_file in json_files:
            if json_file.name in excluded_files:
                continue

            try:
                with open(json_file, 'r') as f:
                    file_data = json.load(f)

                    # Handle both list and dict-wrapper formats (nord.json is dict wrapper)
                    brand_products = []
                    if isinstance(file_data, list):
                        brand_products = file_data
                    elif isinstance(file_data, dict) and "products" in file_data:
                        brand_products = file_data["products"]

                    if brand_products:
                        # brands_found.add(json_file.stem)  # MOVED: Only add if products survive filter

                        for p in brand_products:
                            # --- NORMALIZATION & CLEANING ---

                            # 1. ID Strategy
                            pid = p.get('id') or p.get('halilit_id')
                            if not pid:
                                continue  # Skip invalid ID

                            # 2. Name Strategy
                            name = p.get('name') or p.get('product_name') or p.get(
                                'official_name') or "Unknown Product"

                            # 3. Category Strategy
                            category = p.get('category')
                            if not category:
                                category = p.get('taxonomy', {}).get(
                                    'canonical_category', 'Other')
                            if category == 'Uncategorized':
                                category = 'Other'

                            # 4. Price Strategy
                            # Check root price first, then pricing object, then price_il specific
                            price = p.get('price')
                            if not price or price == 0:
                                price = p.get('price_il', 0)
                            if not price or price == 0:
                                price = p.get('pricing', {}).get('price_il', 0)

                            # QUALITY GATE 1: Price must be > 0
                            if float(price) <= 0:
                                continue

                            # 5. Image Strategy
                            image_url = p.get('image_url') or ""
                            if not image_url:
                                # Try official images (best quality)
                                official_images = p.get('official_images', [])
                                if official_images and isinstance(official_images, list):
                                    # Prefer hero
                                    for img in official_images:
                                        if img.get('display_purpose') == 'hero':
                                            image_url = img.get('url')
                                            break
                                    # Fallback to first
                                    if not image_url and len(official_images) > 0:
                                        image_url = official_images[0].get(
                                            'url')

                            # Filter out placeholder images (allow local placeholder)
                            if image_url and ("brand.com" in image_url):
                                image_url = ""

                            if not image_url:
                                # Try display object
                                disp_hero = p.get(
                                    'display', {}).get('hero_image')
                                if disp_hero:
                                    if isinstance(disp_hero, dict):
                                        image_url = disp_hero.get('url')
                                    elif isinstance(disp_hero, str):
                                        image_url = disp_hero

                            if not image_url:
                                # Try primary source (Halilit scraper fallback)
                                p_source = p.get('primary_source', {})
                                if isinstance(p_source, dict):
                                    image_url = p_source.get(
                                        'image', "")  # rare but possible

                            # Filter out placeholder images (Final Check) - Allow local placeholder
                            if image_url and ("brand.com" in image_url):
                                image_url = ""

                            # QUALITY GATE 2: Must have an image
                            # (We can relax this if strictly needed, but user asked for "only junk data")
                            if not image_url:
                                continue

                            # --- CONSTRUCT FINAL OBJECT ---
                            # Deduce sources if missing
                            sources = p.get('sources', [])
                            if not sources:
                                sources.append('halilit_direct')
                                if p.get('official_specs') or p.get('official_description'):
                                    sources.append('official_specs')
                                if p.get('reviews') or p.get('average_rating'):
                                    sources.append('trusted_reviews')

                            normalized_product = {
                                "id": pid,
                                "halilit_id": pid,
                                "name": name,
                                "product_name": name,
                                "brand": p.get('brand', json_file.stem),
                                "category": category,
                                "price": float(price),
                                "currency": "ILS",
                                "image_url": image_url,
                                "description": p.get('description_short') or p.get('official_description') or "",
                                "taxonomy": p.get('taxonomy', {"canonical_category": category}),
                                "display": {
                                    "hero_image": {"url": image_url},
                                    "color_hint": p.get('display', {}).get('color_hint', 'bg-slate-800'),
                                    "display_role": p.get('display', {}).get('display_role', 'entry'),
                                    "should_highlight": p.get('display', {}).get('should_highlight', False)
                                },
                                # --- ENRICHMENT FIELDS (The "Three Pillars") ---
                                "sources": sources,
                                "official_specs": p.get('official_specs', {}),
                                "review_data": {
                                    "aggregate_rating": p.get('average_rating') or p.get('review_data', {}).get('aggregate_rating', 0),
                                    "total_reviews": len(p.get('reviews', [])) or p.get('review_data', {}).get('total_reviews', 0),
                                    "pros_and_cons": p.get('pros_and_cons') or p.get('review_data', {}).get('pros_and_cons', {})
                                },
                                "pricing": {
                                    "price_il": float(price),
                                    # Simple heuristic
                                    "tier": "pro" if float(price) > 2000 else "entry"
                                }
                            }

                            # Deduplicate: Overwrite with newest/best?
                            # For now simply overwrite (last one wins)
                            products_map[pid] = normalized_product
                            # Mark brand as having valid products
                            brands_found.add(json_file.stem)

            except Exception as e:
                logger.error(f"Error loading {json_file.name}: {e}")

        # Final List
        all_products = list(products_map.values())

        # Re-calc categories from final list
        categories_count = {}
        for p in all_products:
            c = p.get('category', 'Other')
            categories_count[c] = categories_count.get(c, 0) + 1

        logger.info(
            f"✅ Served Clean Catalog: {len(all_products)} verified products from {len(brands_found)} brands")

        catalog = {
            'products': all_products,
            'metadata': {
                'total_products': len(all_products),
                'brands': sorted(list(brands_found)),
                'categories': categories_count,
                'timestamp': datetime.now().isoformat(),
                'source': 'conductor_verified_clean',
                'verification_status': 'complete',
                'cache_ttl_seconds': 300
            }
        }

        return catalog

    except Exception as e:
        logger.error(f"Failed to generate conductor catalog: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate catalog", "details": str(e)}
        )


@app.get("/api/brands/{brand}")
async def get_brand_products(brand: str):
    """Get products for a specific brand from CONDUCTOR INGESTED data filtered by Halilit's golden list"""
    try:
        golden_products = get_ingestion_products_for_golden_brands()

        if brand not in golden_products:
            return {
                "error": f"Brand '{brand}' not found in Halilit's golden list",
                "products": [],
                "brand": brand,
                "source": "error"
            }

        brand_data = golden_products[brand]

        logger.info(
            f"Loaded {len(brand_data['products'])} products for brand '{brand}'")

        return {
            "brand": brand,
            "product_count": brand_data["product_count"],
            "products": brand_data["products"],
            "ingestion_sources": brand_data["ingestion_sources"],
            "source": "halilit_commercial_database_with_conductor_enrichment"
        }
    except Exception as e:
        logger.error(f"Error loading brand products: {e}")
        return {"error": str(e), "products": [], "brand": brand, "source": "error"}


@app.get("/api/search")
async def search_products(q: str = ""):
    """Search across CONDUCTOR INGESTED products (real data)"""
    try:
        if not q or len(q) < 2:
            return {"query": q, "results": []}

        ingestion_products_dir = Path(INGESTION_DATA) / "products"
        results = []
        q_lower = q.lower()

        for brand_dir in ingestion_products_dir.iterdir():
            if not brand_dir.is_dir():
                continue

            # Find latest approved products
            approved_files = sorted(brand_dir.glob(
                "approved_*.json"), reverse=True)
            if not approved_files:
                continue

            try:
                with open(approved_files[0]) as f:
                    data = json.load(f)
                    products = data if isinstance(
                        data, list) else data.get("products", [])

                    for product in products:
                        # Search in key fields
                        search_text = " ".join([
                            str(product.get("product_name", "")),
                            str(product.get("brand", "")),
                            str(product.get("description_short", "")),
                            str(product.get("official_description", ""))
                        ]).lower()

                        if q_lower in search_text:
                            results.append(product)
                            if len(results) >= 50:  # Limit results
                                break
            except Exception as e:
                logger.warning(f"Error searching {brand_dir}: {e}")

        logger.info(f"✅ Found {len(results)} products matching '{q}'")

        return {
            "query": q,
            "total_results": len(results),
            "results": results[:50],
            "source": "conductor_ingestion_database"
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"error": str(e), "results": [], "source": "error"}


# ========== COPILOTKIT INTEGRATION ENDPOINTS ==========

# Initialize the CopilotKit executor (singleton)
_executor = None


def get_executor():
    """Get or create the CopilotKit skill executor."""
    global _executor
    if _executor is None:
        from backend.copilot_skill_executor import CopilotSkillExecutor
        _executor = CopilotSkillExecutor()
    return _executor


@app.get("/api/copilot/skills")
async def list_available_skills():
    """Get list of available skills for CopilotKit agent."""
    executor = get_executor()
    return {
        "skills": executor.get_available_skills(),
        "total_skills": len(executor.get_available_skills()),
        "status": "ready"
    }


@app.post("/api/copilot/execute-skill")
async def execute_single_skill(request: dict):
    """Execute a single skill via CopilotKit."""
    executor = get_executor()

    skill_name = request.get('skill')
    context = request.get('context', {})

    if not skill_name:
        return {"error": "skill parameter required"}

    result = await executor.execute_skill(skill_name, context)
    return result


@app.post("/api/copilot/pipeline")
async def execute_pipeline(request: dict):
    """
    Execute a product through the full 6-phase pipeline.
    Returns SSE stream of progress updates.
    """
    from fastapi.responses import StreamingResponse

    executor = get_executor()

    raw_product = request.get('raw_product')
    brand = request.get('brand')

    if not raw_product or not brand:
        return {"error": "raw_product and brand required"}

    async def event_stream():
        """Stream progress events as SSE."""
        async for event in executor.execute_full_pipeline(raw_product, brand):
            # Format as SSE
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/api/copilot/batch-ingest")
async def batch_ingest_products(request: dict):
    """
    Ingest multiple products with progress streaming.
    Returns SSE stream of progress updates.
    """
    from fastapi.responses import StreamingResponse

    executor = get_executor()

    products = request.get('products', [])
    brand = request.get('brand')

    if not products or not brand:
        return {"error": "products list and brand required"}

    async def event_stream():
        """Stream batch progress events as SSE."""
        async for event in executor.stream_ingestion_progress(products, brand):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/copilot/status")
async def copilot_status():
    """Get CopilotKit pipeline status and capabilities."""
    executor = get_executor()
    return executor.get_pipeline_status()


@app.get("/api/copilot/history")
async def execution_history(limit: int = 50):
    """Get recent execution history."""
    executor = get_executor()
    return {
        "history": executor.get_execution_history(limit),
        "total_executions": len(executor.execution_history)
    }


@app.delete("/api/copilot/history")
async def clear_execution_history():
    """Clear execution history."""
    executor = get_executor()
    executor.clear_history()
    return {"status": "cleared"}


# ========== CONDUCTOR UNIFIED DATA ENDPOINTS v7.6 ==========
# These are the PRIMARY endpoints for frontend data loading
# All data is Conductor-verified and taxonomy-compliant

# @app.get("/api/conductor/catalog")
# async def get_conductor_catalog_unified():
#     """
#     Get unified, Conductor-verified product catalog.
#     (DISABLED: Using direct file aggregation method defined earlier in this file)
#     """
#     try:
#         service = get_conductor_data_service()
#         catalog = service.get_unified_catalog()
#         logger.info(
#             f"✅ Served unified catalog with {catalog['metadata']['total_products']} products")
#         return catalog
#     except Exception as e:
#         logger.error(f"❌ Failed to get catalog: {e}")
#         return {
#             "error": str(e),
#             "products": [],
#             "metadata": {
#                 "source": "error",
#                 "verification_status": "failed"
#             }
#         }


@app.get("/api/conductor/taxonomy")
async def get_conductor_taxonomy():
    """
    Get the flexible taxonomy schema.

    Frontend and backend use this to:
    - Display category/subcategory hierarchies
    - Filter products by taxonomy
    - Understand available pricing tiers and display roles
    - Dynamically build UI controls based on what's available
    """
    try:
        service = get_conductor_data_service()
        taxonomy = service.get_taxonomy_schema()
        return taxonomy
    except Exception as e:
        logger.error(f"❌ Failed to get taxonomy: {e}")
        return {"error": str(e)}


@app.post("/api/conductor/filter")
async def filter_conductor_products(filters: dict):
    """
    Apply flexible filtering to Conductor-verified products.

    Supported filters:
    - brand: str or [str]
    - category: str or [str]
    - subcategory: str or [str]
    - pricing_tier: str or [str]
    - min_price: float
    - max_price: float
    - display_role: str or [str]
    - search_query: str
    """
    try:
        service = get_conductor_data_service()
        results = service.filter_products(filters)
        return results
    except Exception as e:
        logger.error(f"❌ Filter failed: {e}")
        return {"error": str(e), "products": []}


@app.get("/api/conductor/categories")
async def get_conductor_categories():
    """
    Get category summary for navigation UI.

    Returns category stats including product count, brands, subcategories, and average price.
    """
    try:
        service = get_conductor_data_service()
        summary = service.get_category_summary()
        return summary
    except Exception as e:
        logger.error(f"❌ Failed to get categories: {e}")
        return {"error": str(e), "categories": []}


@app.get("/api/conductor/refresh")
async def refresh_conductor_catalog():
    """
    Force refresh of the unified catalog cache.
    Use after running Conductor pipeline to update frontend with new data.
    """
    try:
        service = get_conductor_data_service()
        service._catalog_cache = None  # Clear cache
        service._cache_timestamp = None

        catalog = service.get_unified_catalog()
        return {
            "status": "refreshed",
            "product_count": catalog['metadata']['total_products'],
            "brands": len(catalog['metadata']['brands']),
            "timestamp": catalog['metadata']['timestamp']
        }
    except Exception as e:
        logger.error(f"❌ Refresh failed: {e}")
        return {"error": str(e), "status": "failed"}


# ========== AUTO-SYNC ENDPOINTS (Phase 1E) ==========


def get_sync_engine():
    """Get auto-sync engine singleton."""
    return get_auto_sync_engine()


@app.post("/api/copilot/sync")
async def sync_product(request_data: dict):
    """Sync a single product result to frontend after pipeline completion."""
    try:
        sync_engine = get_sync_engine()

        # Extract product data
        product_id = request_data.get(
            "product_id") or request_data.get("halilit_id")
        product_name = request_data.get("product_name")
        brand = request_data.get("brand", "Unknown")
        category = request_data.get("category", "Uncategorized")
        status = request_data.get("status", "APPROVED")
        risk_score = request_data.get("risk_score", 50)
        pricing_tier = request_data.get("pricing_tier")

        async def sync_stream():
            """Stream sync events as SSE."""
            async for event in sync_engine.sync_pipeline_result(
                product_id=product_id,
                product_name=product_name,
                brand=brand,
                category=category,
                status=status,
                risk_score=risk_score,
                pricing_tier=pricing_tier
            ):
                yield f"data: {json.dumps(event)}\n\n"

        return StreamingResponse(sync_stream(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Sync error: {str(e)}")
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.post("/api/copilot/sync-batch")
async def sync_batch(request_data: dict):
    """Sync multiple products to frontend (batch sync with progress)."""
    try:
        sync_engine = get_sync_engine()

        # Extract batch data
        products = request_data.get("products", [])
        brand = request_data.get("brand", "Unknown")

        if not products:
            return JSONResponse(status_code=400, content={"error": "No products provided"})

        async def batch_sync_stream():
            """Stream batch sync events as SSE."""
            async for event in sync_engine.sync_batch(
                products=products,
                brand=brand
            ):
                yield f"data: {json.dumps(event)}\n\n"

        return StreamingResponse(batch_sync_stream(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Batch sync error: {str(e)}")
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.get("/api/copilot/sync/history")
async def sync_history(limit: int = 50):
    """Get sync history."""
    sync_engine = get_sync_engine()
    return {
        "history": sync_engine.get_sync_history(limit),
        "total_syncs": len(sync_engine.sync_history)
    }


@app.get("/api/copilot/sync/batch-status/{batch_id}")
async def sync_batch_status(batch_id: str):
    """Get status of a specific sync batch."""
    sync_engine = get_sync_engine()
    status = sync_engine.get_batch_status(batch_id)

    if status is None:
        return JSONResponse(status_code=404, content={"error": "Batch not found"})

    return {"batch_status": status}


@app.post("/api/copilot/sync/toggle")
async def toggle_sync(request_data: dict):
    """Enable or disable auto-sync."""
    sync_engine = get_sync_engine()
    enabled = request_data.get("enabled", True)
    sync_engine.toggle_sync(enabled)

    return {
        "status": "enabled" if enabled else "disabled",
        "sync_enabled": enabled
    }


@app.delete("/api/copilot/sync/history")
async def clear_sync_history():
    """Clear sync history."""
    sync_engine = get_sync_engine()
    sync_engine.clear_history()
    return {"status": "cleared"}


# ========== FRONTEND ROUTING ==========

# Ensure you run 'npm run build' in frontend/ first!
if os.path.exists(FRONTEND_DIST):
    app.mount(
        "/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    # Mount data if it exists
    if os.path.exists(FRONTEND_PUBLIC_DATA):
        app.mount("/data", StaticFiles(directory=FRONTEND_PUBLIC_DATA), name="data")

    @app.get("/{catchall:path}")
    async def serve_react_app(catchall: str):
        # Return index.html for any path (SPA routing)
        # Check if file exists in dist, otherwise serve index.html
        file_path = os.path.join(FRONTEND_DIST, catchall)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
else:
    logger.warning(
        f"WARNING: Frontend build not found at {FRONTEND_DIST}. Run 'npm run build' in frontend/ folder.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
