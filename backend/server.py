from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from backend.auto_sync_engine import get_auto_sync_engine
from backend.product_normalizer import build_catalog, GALAXIES
import os
import sys
import logging
import json
import gzip
import time
import asyncio
import threading
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.api.streams import router as streams_router

# ── Server-side catalog cache ──
_catalog_cache_json: bytes | None = None   # Pre-serialized JSON bytes
_catalog_cache_gzip: bytes | None = None   # Pre-compressed gzip bytes
_catalog_cache_dict: dict | None = None    # Pre-built catalog dict
_catalog_cache_time: float = 0
_catalog_build_lock = threading.Lock()
CATALOG_CACHE_TTL = 300  # 5 minutes

# Fields to strip from products in the catalog response (never rendered by frontend)
STRIP_FIELDS = {"contextual_data", "search_text", "subcategory", "currency"}

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


app = FastAPI(title="Halilit Support Center API", version="8.3")

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
    from backend.unified_learning_system import router as learning_router
    app.include_router(learning_router)
    logger.info("✅ Learning endpoints registered")
except Exception as e:
    logger.warning(f"⚠️ Failed to load learning endpoints: {e}")

# Async Task Queue API
try:
    from backend.api.task_router import router as task_router
    app.include_router(task_router, tags=["Task Queue"])
    logger.info("✅ Task queue endpoints registered at /api/v8/tasks")
except Exception as e:
    logger.warning(f"⚠️ Failed to register task router: {e}")

# MCP (Model Context Protocol) Integration
try:
    from backend.api.mcp_router import router as mcp_router
    from backend.mcp.startup import init_mcp, shutdown_mcp
    app.include_router(mcp_router)

    @app.on_event("startup")
    async def _mcp_startup():
        await init_mcp()

    @app.on_event("shutdown")
    async def _mcp_shutdown():
        await shutdown_mcp()

    logger.info("✅ MCP endpoints registered at /api/mcp")
except Exception as e:
    logger.warning(f"⚠️ Failed to register MCP: {e}")

# Enhanced Pipeline API
try:
    from backend.api.pipeline_router import router as pipeline_router
    app.include_router(pipeline_router, tags=["Pipeline"])
    logger.info("✅ Pipeline endpoints registered at /api/pipeline")
except Exception as e:
    logger.warning(f"⚠️ Failed to register pipeline router: {e}")

# Spectrum Redesign API (model grouping, instrument families, zoom levels)
try:
    from backend.api.spectrum_router import router as spectrum_router
    app.include_router(spectrum_router, tags=["Spectrum"])
    logger.info("✅ Spectrum endpoints registered at /api/spectrum")
except Exception as e:
    logger.warning(f"⚠️ Failed to register spectrum router: {e}")

# Product Graph Curation API
try:
    from backend.api.curation_router import router as curation_router
    app.include_router(curation_router, tags=["Product Graph Curation"])
    logger.info("✅ Curation endpoints registered at /api/curation")
except Exception as e:
    logger.warning(f"⚠️ Failed to register curation router: {e}")

# WebSocket real-time task updates
try:
    from backend.api.websocket_manager import create_websocket_route

    @app.on_event("startup")
    async def _register_websocket():
        await create_websocket_route(app)

    logger.info("✅ WebSocket endpoint will register at /ws/tasks/{{task_id}}")
except Exception as e:
    logger.warning(f"⚠️ Failed to register WebSocket: {e}")

# Robust path handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "../frontend/dist")
FRONTEND_PUBLIC_DATA = os.path.join(BASE_DIR, "../frontend/public/data")
INGESTION_DATA = os.path.join(
    BASE_DIR, "./data/ingestion")  # Real ingested data


def _build_catalog_cache():
    """Build catalog and cache the pre-serialized JSON response.
    Thread-safe, called at startup and on cache expiry."""
    global _catalog_cache_json, _catalog_cache_gzip, _catalog_cache_dict, _catalog_cache_time
    with _catalog_build_lock:
        # Double-check after acquiring lock
        if _catalog_cache_json is not None and (time.time() - _catalog_cache_time) < CATALOG_CACHE_TTL:
            return
        t0 = time.time()
        catalog = build_catalog(FRONTEND_PUBLIC_DATA)
        _catalog_cache_dict = catalog  # Store dict for secondary endpoints

        # Strip fields the frontend never renders
        for p in catalog["products"]:
            for field in STRIP_FIELDS:
                p.pop(field, None)

        catalog["metadata"]["timestamp"] = datetime.now().isoformat()

        json_bytes = json.dumps(catalog, ensure_ascii=False).encode("utf-8")
        gzip_bytes = gzip.compress(json_bytes, compresslevel=6)

        _catalog_cache_json = json_bytes
        _catalog_cache_gzip = gzip_bytes
        _catalog_cache_time = time.time()
        build_ms = int((time.time() - t0) * 1000)

        logger.info(
            f"✅ Catalog v10: {catalog['metadata']['total_products']} products, "
            f"{len(catalog['metadata']['brands'])} brands, "
            f"{len(catalog['metadata']['galaxy_counts'])} galaxies, "
            f"health: {catalog['metadata'].get('health_score', '?')}/100 "
            f"(built in {build_ms}ms, {len(json_bytes)//1024}KB → {len(gzip_bytes)//1024}KB gzip)")


# Eagerly build catalog at import time in a background thread
# so the first request is instant instead of blocking for 14s
def _startup_catalog_build():
    try:
        _build_catalog_cache()
    except Exception as e:
        logger.error(f"Startup catalog build failed: {e}")


_startup_thread = threading.Thread(target=_startup_catalog_build, daemon=True)
_startup_thread.start()


def _get_catalog() -> dict:
    """Get the cached catalog dict, building if needed. Used by secondary endpoints."""
    global _catalog_cache_dict, _catalog_cache_time
    now = time.time()
    if _catalog_cache_dict is None or (now - _catalog_cache_time) > CATALOG_CACHE_TTL:
        _build_catalog_cache()
    if _catalog_cache_dict is None:
        _startup_thread.join(timeout=60)
    return _catalog_cache_dict or {"products": [], "metadata": {}, "indexes": {}}


# --- API ENDPOINTS (must be before frontend catch-all) ---

# Health check endpoint


@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": "8.3",
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
    """Legacy endpoint — redirects to conductor catalog."""
    return await get_conductor_catalog()


@app.get("/api/catalog")
async def get_catalog():
    """Legacy endpoint — redirects to conductor catalog."""
    return await get_conductor_catalog()


@app.get("/api/conductor/catalog")
async def get_conductor_catalog(request: Request):
    """
    Single source of truth for the frontend — v10 pre-indexed catalog.
    Returns { products, indexes, metadata } where indexes contain
    by_galaxy, by_spectrum, by_brand mappings for instant frontend lookup.

    Optimizations:
    - Pre-built at server startup in background thread
    - Pre-serialized JSON + pre-compressed gzip cached server-side (5 min TTL)
    - Strips unused fields (contextual_data, search_text, subcategory, currency)
    - Cached response served in <50ms
    """
    global _catalog_cache_json, _catalog_cache_gzip, _catalog_cache_time
    try:
        now = time.time()
        if _catalog_cache_json is None or (now - _catalog_cache_time) > CATALOG_CACHE_TTL:
            # Build in thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _build_catalog_cache)

        # Wait for startup build if still in progress
        if _catalog_cache_json is None:
            _startup_thread.join(timeout=60)

        if _catalog_cache_json is None:
            return JSONResponse(status_code=503, content={"error": "Catalog still building"})

        # Serve pre-compressed gzip if client accepts it, otherwise raw JSON
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" in accept_encoding and _catalog_cache_gzip is not None:
            return Response(
                content=_catalog_cache_gzip,
                media_type="application/json",
                headers={"Content-Encoding": "gzip"},
            )

        return Response(
            content=_catalog_cache_json,
            media_type="application/json",
        )

    except Exception as e:
        logger.error(f"Failed to generate conductor catalog: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate catalog", "details": str(e)}
        )


@app.get("/api/catalog/health")
async def get_catalog_health():
    """
    Catalog health dashboard — real-time data quality metrics.
    Returns health_score, status_counts, field_coverage, top_issues,
    brand_health, and resolution_queue.
    """
    try:
        from backend.catalog_validator import validate_catalog

        # Use cached catalog build (run in executor to avoid blocking)
        loop = asyncio.get_event_loop()
        catalog = await loop.run_in_executor(
            None, build_catalog, FRONTEND_PUBLIC_DATA)
        health = validate_catalog(catalog["products"])

        logger.info(
            f"📊 Catalog health: {health['health_score']}/100 "
            f"({health['status_counts']})")

        return health

    except Exception as e:
        logger.error(f"Failed to get catalog health: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to compute health", "details": str(e)}
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


# ========== COPILOTKIT SKILL ENDPOINTS ==========
# Skill execution is handled via the Celery task queue (see tasks.py)
# and the CopilotKit chat router (see api/copilot_router.py).
# The task API is served by api/task_router.py.


# ========== CONDUCTOR UNIFIED DATA ENDPOINTS ==========
# These are the PRIMARY endpoints for frontend data loading
# All data is Conductor-verified and taxonomy-compliant


@app.get("/api/conductor/taxonomy")
async def get_conductor_taxonomy():
    """
    Get the taxonomy schema derived from the live catalog + GALAXIES.
    Used by frontend for category/subcategory hierarchies and filter controls.
    """
    try:
        catalog = _get_catalog()
        products = catalog.get("products", [])
        brands = sorted(catalog.get("metadata", {}).get("brands", []))

        # Build universal categories from GALAXIES (canonical source)
        universal_categories = []
        for galaxy in GALAXIES:
            universal_categories.append({
                "id": galaxy["id"],
                "name": galaxy["label"],
                "subcategories": [
                    {"id": s["id"], "name": s["label"]}
                    for s in galaxy.get("spectrums", [])
                ],
            })

        return {
            "universal_categories": universal_categories,
            "all_brands": brands,
            "pricing_tiers": ["entry", "mid", "pro", "flagship", "legacy"],
            "display_roles": ["hero", "cornerstone", "specialist", "entry", "hidden"],
            "statuses": ["harvested", "enriched", "validated", "approved", "rejected", "archived"],
            "confidence_levels": ["official", "trusted", "commercial", "user", "inferred"],
            "total_products": len(products),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to get taxonomy: {e}")
        return {"error": str(e)}


@app.post("/api/conductor/filter")
async def filter_conductor_products(filters: dict):
    """
    Apply flexible filtering to the pre-built catalog.

    Supported filters: brand, category, pricing_tier, min_price, max_price,
    display_role, search_query.
    """
    try:
        catalog = _get_catalog()
        products = catalog.get("products", [])
        filters_applied = {}

        if "brand" in filters:
            vals = [filters["brand"]] if isinstance(
                filters["brand"], str) else filters["brand"]
            vals_lower = [v.lower() for v in vals]
            products = [p for p in products if p.get(
                "brand", "").lower() in vals_lower]
            filters_applied["brand"] = filters["brand"]

        if "category" in filters:
            vals = [filters["category"]] if isinstance(
                filters["category"], str) else filters["category"]
            vals_lower = [v.lower() for v in vals]
            products = [p for p in products if p.get("galaxy_id", "").lower() in vals_lower
                        or p.get("spectrum_id", "").lower() in vals_lower]
            filters_applied["category"] = filters["category"]

        if "search_query" in filters:
            q = filters["search_query"].lower()
            products = [p for p in products if q in (p.get("search_text") or
                        f"{p.get('name','')} {p.get('brand','')}").lower()]
            filters_applied["search_query"] = filters["search_query"]

        if "pricing_tier" in filters:
            tiers = [filters["pricing_tier"]] if isinstance(
                filters["pricing_tier"], str) else filters["pricing_tier"]
            products = [p for p in products if p.get("tier") in tiers]
            filters_applied["pricing_tier"] = filters["pricing_tier"]

        if "min_price" in filters:
            mp = float(filters["min_price"])
            products = [p for p in products if (p.get("price") or 0) >= mp]
            filters_applied["min_price"] = mp

        if "max_price" in filters:
            mp = float(filters["max_price"])
            products = [p for p in products if 0 < (p.get("price") or 0) <= mp]
            filters_applied["max_price"] = mp

        return {
            "products": products,
            "filters_applied": filters_applied,
            "total_results": len(products),
            "source": "conductor_verified",
        }
    except Exception as e:
        logger.error(f"Filter failed: {e}")
        return {"error": str(e), "products": []}


@app.get("/api/conductor/categories")
async def get_conductor_categories():
    """
    Get category summary from the pre-built catalog for navigation UI.
    Returns category stats: product count, brands, avg price.
    """
    try:
        catalog = _get_catalog()
        products = catalog.get("products", [])

        categories: dict = {}
        for p in products:
            cat = p.get("galaxy_id") or "uncategorized"
            brand = p.get("brand", "Unknown")
            price = p.get("price") or 0

            if cat not in categories:
                categories[cat] = {"name": cat, "count": 0,
                                   "brands": set(), "prices": []}
            categories[cat]["count"] += 1
            categories[cat]["brands"].add(brand)
            if price > 0:
                categories[cat]["prices"].append(price)

        result = []
        for cat_data in categories.values():
            prices = cat_data["prices"]
            result.append({
                "name": cat_data["name"],
                "product_count": cat_data["count"],
                "brands": sorted(cat_data["brands"]),
                "avg_price": round(sum(prices) / len(prices), 2) if prices else 0,
            })

        return {
            "categories": sorted(result, key=lambda x: x["product_count"], reverse=True)
        }
    except Exception as e:
        logger.error(f"Failed to get categories: {e}")
        return {"error": str(e), "categories": []}


@app.get("/api/conductor/refresh")
async def refresh_conductor_catalog():
    """
    Force rebuild of the catalog cache.
    Use after running a pipeline stage to update frontend with new data.
    """
    try:
        global _catalog_cache_json, _catalog_cache_gzip, _catalog_cache_dict, _catalog_cache_time
        _catalog_cache_json = None
        _catalog_cache_gzip = None
        _catalog_cache_dict = None
        _catalog_cache_time = 0
        _build_catalog_cache()

        catalog = _catalog_cache_dict or {}
        meta = catalog.get("metadata", {})
        return {
            "status": "refreshed",
            "product_count": meta.get("total_products", 0),
            "brands": len(meta.get("brands", [])),
            "health_score": meta.get("health_score"),
            "timestamp": meta.get("timestamp"),
        }
    except Exception as e:
        logger.error(f"Refresh failed: {e}")
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
