"""
Halilit Support Center — JIT Architecture API Server

Lightweight FastAPI server that serves:
  1. Skeleton inventory (pre-built catalog from frontend/public/data/)
  2. JIT Intelligence endpoint (streams live product research via Gemini)
  3. Static frontend assets
"""

from fastapi.responses import Response, FileResponse, JSONResponse
from backend import __version__
from backend.unified_data_service import get_conductor_data_service
from backend.product_normalizer import build_catalog
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
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.project_config import FRONTEND_PUBLIC_DATA, FRONTEND_DIR, DATA_DIR

# Disk cache: load pre-built catalog to avoid slow first build on restart
CATALOG_CACHE_PATH = DATA_DIR / "catalog_cache.json.gz"
CATALOG_CACHE_MAX_AGE_SEC = 86400  # 24 hours; rebuild if older

# ── Server-side catalog cache ──
_catalog_cache_json: bytes | None = None
_catalog_cache_gzip: bytes | None = None
_catalog_cache_dict: dict | None = None
_catalog_cache_time: float = 0
_catalog_build_lock = threading.Lock()
CATALOG_CACHE_TTL = 300  # 5 minutes

# Fields to strip from products in the catalog response (keep contextual_data so UI can show review_synthesis, real_world_insights, review_sources)
STRIP_FIELDS = {"search_text", "subcategory", "currency"}

# Ensure parent directory is in path
_parent_dir = str(Path(__file__).parent.parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════════════════

app = FastAPI(title="Halilit Support Center API", version=__version__)

_origins = os.environ.get("CORS_ORIGINS", "*").strip()
_cors_origins = _origins.split(",") if _origins else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MCP Integration ──
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

    logger.info("MCP endpoints registered at /api/mcp")
except Exception as e:
    logger.warning(f"Failed to register MCP: {e}")

# ── Product Graph Curation API ──
try:
    from backend.api.curation_router import router as curation_router
    app.include_router(curation_router, tags=["Product Graph Curation"])
    logger.info("Curation endpoints registered at /api/curation")
except Exception as e:
    logger.warning(f"Failed to register curation router: {e}")

# Paths
FRONTEND_DIST = str(FRONTEND_DIR / "dist")


# ═══════════════════════════════════════════════════════════════════════════
# CATALOG CACHE
# ═══════════════════════════════════════════════════════════════════════════

def _invalidate_catalog_cache():
    """Force next request to rebuild catalog (used after sync)."""
    global _catalog_cache_json, _catalog_cache_gzip, _catalog_cache_dict, _catalog_cache_time
    with _catalog_build_lock:
        _catalog_cache_json = None
        _catalog_cache_gzip = None
        _catalog_cache_dict = None
        _catalog_cache_time = 0
        try:
            if CATALOG_CACHE_PATH.exists():
                CATALOG_CACHE_PATH.unlink()
        except OSError:
            pass


def _load_catalog_from_disk() -> bool:
    """Load pre-built catalog from disk. Returns True if loaded successfully."""
    global _catalog_cache_json, _catalog_cache_gzip, _catalog_cache_dict, _catalog_cache_time
    if not CATALOG_CACHE_PATH.exists():
        return False
    try:
        age = time.time() - CATALOG_CACHE_PATH.stat().st_mtime
        if age > CATALOG_CACHE_MAX_AGE_SEC:
            return False
        with gzip.open(CATALOG_CACHE_PATH, "rb") as f:
            json_bytes = f.read()
        catalog = json.loads(json_bytes.decode("utf-8"))
        gzip_bytes = gzip.compress(json_bytes, compresslevel=6)
        _catalog_cache_json = json_bytes
        _catalog_cache_gzip = gzip_bytes
        _catalog_cache_dict = catalog
        _catalog_cache_time = time.time()
        n = catalog.get("metadata", {}).get("total_products", 0)
        logger.info(f"Catalog: loaded from disk ({n} products, {len(json_bytes)//1024}KB)")
        return True
    except Exception as e:
        logger.warning(f"Catalog disk cache load failed: {e}")
        return False


def _build_catalog_cache():
    """Build catalog and cache. Uses disk cache if fresh, else builds from scratch."""
    global _catalog_cache_json, _catalog_cache_gzip, _catalog_cache_dict, _catalog_cache_time
    with _catalog_build_lock:
        if _catalog_cache_json is not None and (time.time() - _catalog_cache_time) < CATALOG_CACHE_TTL:
            return
        # Fast path: load from disk cache
        if _load_catalog_from_disk():
            return
        # Slow path: full build
        t0 = time.time()
        catalog = build_catalog(str(FRONTEND_PUBLIC_DATA), resolve=False)

        for p in catalog["products"]:
            for field in STRIP_FIELDS:
                p.pop(field, None)

        catalog["metadata"]["timestamp"] = datetime.now().isoformat()

        json_bytes = json.dumps(catalog, ensure_ascii=False).encode("utf-8")
        gzip_bytes = gzip.compress(json_bytes, compresslevel=6)

        _catalog_cache_json = json_bytes
        _catalog_cache_gzip = gzip_bytes
        _catalog_cache_dict = catalog
        _catalog_cache_time = time.time()
        build_ms = int((time.time() - t0) * 1000)

        # Persist for fast restarts
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with gzip.open(CATALOG_CACHE_PATH, "wb", compresslevel=6) as f:
                f.write(json_bytes)
        except OSError as e:
            logger.warning(f"Could not write catalog cache: {e}")

        logger.info(
            f"Catalog: {catalog['metadata']['total_products']} products, "
            f"{len(catalog['metadata']['brands'])} brands "
            f"(built in {build_ms}ms, {len(json_bytes)//1024}KB)")


def _startup_catalog_build():
    try:
        _build_catalog_cache()
    except Exception as e:
        logger.error(f"Startup catalog build failed: {e}")


_startup_thread = threading.Thread(target=_startup_catalog_build, daemon=True)
_startup_thread.start()


# ═══════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": __version__,
        "service": "Halilit Support Center",
        "architecture": "JIT",
    }


@app.get("/api/conductor/catalog")
async def get_conductor_catalog(request: Request):
    """Single source of truth — pre-indexed catalog from skeleton inventory."""
    global _catalog_cache_json, _catalog_cache_gzip, _catalog_cache_time
    try:
        now = time.time()
        if _catalog_cache_json is None or (now - _catalog_cache_time) > CATALOG_CACHE_TTL:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _build_catalog_cache)

        if _catalog_cache_json is None:
            _startup_thread.join(timeout=60)

        if _catalog_cache_json is None:
            return JSONResponse(status_code=503, content={"error": "Catalog still building"})

        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" in accept_encoding and _catalog_cache_gzip is not None:
            return Response(
                content=_catalog_cache_gzip,
                media_type="application/json",
                headers={"Content-Encoding": "gzip"},
            )

        return Response(content=_catalog_cache_json, media_type="application/json")

    except Exception as e:
        logger.error(f"Failed to generate catalog: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# Legacy endpoints — redirect to conductor catalog
@app.get("/api/galaxy-view")
async def galaxy_view(request: Request):
    return await get_conductor_catalog(request)


@app.get("/api/catalog")
async def get_catalog(request: Request):
    return await get_conductor_catalog(request)


@app.get("/api/spectrum/{spectrum_id}")
async def get_spectrum_star_view(spectrum_id: str):
    """
    Spectrum Module neuron view: ModelGroups (nucleus + inner variations)
    and ProductRelationship (outer connections) for a given spectrum.

    - Nucleus: ModelGroup (e.g. Nord Stage 4)
    - Inner electrons: ModelVariation (88, 73, Compact)
    - Outer connections: ProductRelationship[] for accessories/alternatives

    Use ZoomLevel (galaxy → constellation → cluster → star) to show
    inner connections at 'star' and outer at 'cluster'.
    """
    global _catalog_cache_dict, _catalog_cache_time
    now = time.time()
    if _catalog_cache_dict is None or (now - _catalog_cache_time) > CATALOG_CACHE_TTL:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _build_catalog_cache)
    if _catalog_cache_dict is None:
        return JSONResponse(status_code=503, content={"error": "Catalog still building"})

    catalog = _catalog_cache_dict
    products = catalog.get("products", [])
    indexes = catalog.get("indexes", {})
    by_spectrum = indexes.get("by_spectrum", {})
    inds = by_spectrum.get(spectrum_id, [])
    spectrum_products = [products[i] for i in inds if 0 <= i < len(products)]
    families_meta = catalog.get("families", {})

    try:
        from backend.model_grouper import (
            group_products_by_model,
            group_products_by_model_from_cpg,
        )
        cpg_groups, orphans = group_products_by_model_from_cpg(
            spectrum_products, families_meta
        )
        orphan_groups = group_products_by_model(orphans) if orphans else []
        model_groups = cpg_groups + orphan_groups
        model_groups.sort(key=lambda g: (g["brand"].lower(), g["priceRange"]["min"]))
    except Exception as e:
        logger.warning(f"model_grouper failed for spectrum {spectrum_id}: {e}")
        model_groups = []

    # Relationships keyed by product id (for frontend to "hop" from neuron to neuron)
    relationships_by_product = dict(indexes.get("relationships", {}))

    return {
        "spectrum_id": spectrum_id,
        "model_groups": model_groups,
        "relationships": relationships_by_product,
        "zoom_levels": ["galaxy", "constellation", "cluster", "star"],
        "product_count": len(spectrum_products),
    }


@app.get("/api/catalog/health")
async def get_catalog_health():
    """Catalog health metrics."""
    try:
        from backend.catalog_validator import validate_catalog

        global _catalog_cache_dict, _catalog_cache_time
        now = time.time()
        if _catalog_cache_dict is not None and (now - _catalog_cache_time) <= CATALOG_CACHE_TTL:
            catalog = _catalog_cache_dict
        else:
            loop = asyncio.get_event_loop()
            catalog = await loop.run_in_executor(
                None, build_catalog, str(FRONTEND_PUBLIC_DATA))
        health = validate_catalog(catalog["products"])
        return health
    except Exception as e:
        logger.error(f"Failed to get catalog health: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/conductor/taxonomy")
async def get_conductor_taxonomy():
    """Get the taxonomy schema."""
    try:
        service = get_conductor_data_service()
        return service.get_taxonomy_schema()
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/conductor/filter")
async def filter_conductor_products(filters: dict):
    """Filter products by brand, category, price, etc."""
    try:
        service = get_conductor_data_service()
        return service.filter_products(filters)
    except Exception as e:
        return {"error": str(e), "products": []}


@app.get("/api/conductor/categories")
async def get_conductor_categories():
    """Category summary for navigation."""
    try:
        service = get_conductor_data_service()
        return service.get_category_summary()
    except Exception as e:
        return {"error": str(e), "categories": []}


@app.get("/api/conductor/refresh")
async def refresh_conductor_catalog():
    """Force refresh of all catalog caches."""
    try:
        _invalidate_catalog_cache()
        service = get_conductor_data_service()
        service._catalog_cache = None
        service._cache_timestamp = None

        _build_catalog_cache()
        meta = _catalog_cache_dict.get("metadata", {}) if _catalog_cache_dict else {}
        return {
            "status": "refreshed",
            "product_count": meta.get("total_products", 0),
            "brands": len(meta.get("brands", [])),
            "timestamp": meta.get("timestamp", datetime.now().isoformat()),
        }
    except Exception as e:
        logger.error(f"Refresh failed: {e}")
        return {"error": str(e), "status": "failed"}


# ═══════════════════════════════════════════════════════════════════════════
# BATCH IMAGE LOOKUP — lightweight endpoint for focus-zone enrichment
# Checks JIT cache for images without triggering full JIT pipeline.
# ═══════════════════════════════════════════════════════════════════════════


@app.post("/api/batch-image-lookup")
async def batch_image_lookup(request: Request):
    """
    Look up cached images for a batch of product IDs.
    Returns {product_id: image_url} for any products that have images
    in the JIT cache. Does NOT trigger new scraping — purely cache lookup.

    This endpoint supports the zoom-lens focus-zone enrichment:
    when the user zooms into a price range, the frontend can request
    images for visible products that lack them.
    """
    try:
        body = await request.json()
        product_ids = body.get("product_ids", [])
        if not isinstance(product_ids, list) or len(product_ids) > 200:
            return JSONResponse(
                status_code=400,
                content={"error": "product_ids must be a list of max 200 IDs"},
            )

        from backend.jit_agent import _read_cache

        results: dict[str, str] = {}
        for pid in product_ids:
            cached = _read_cache(pid)
            if cached:
                # Check for images in the cached JIT data
                snap = cached.get("snap", {})
                official = cached.get("official_specs", {})
                thumbnail = snap.get("thumbnail", "")
                official_images = official.get("images", [])

                if official_images:
                    results[pid] = official_images[0]
                elif thumbnail and thumbnail.startswith("http"):
                    results[pid] = thumbnail

        return {"images": results, "found": len(results), "requested": len(product_ids)}

    except Exception as e:
        logger.error(f"Batch image lookup failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ═══════════════════════════════════════════════════════════════════════════
# JIT INTELLIGENCE ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════

from fastapi.responses import StreamingResponse


@app.post("/api/jit/product/{product_id}")
async def jit_product_intelligence(product_id: str):
    """
    Stream live JIT intelligence for a product via SSE.
    First request ~5s (live Gemini research), subsequent instant (7-day cache).

    Events: status, snap, official_specs, verdict, field_notes, exploration, complete
    """
    try:
        from backend.jit_agent import stream_product_intelligence

        return StreamingResponse(
            stream_product_intelligence(product_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        logger.error(f"JIT stream failed for {product_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"JIT intelligence failed: {str(e)}"},
        )


# ═══════════════════════════════════════════════════════════════════════════
# STATIC FILES & FRONTEND
# ═══════════════════════════════════════════════════════════════════════════

if os.path.exists(str(FRONTEND_PUBLIC_DATA)):
    app.mount("/data", StaticFiles(directory=str(FRONTEND_PUBLIC_DATA)), name="data")
    logger.info(f"Serving /data from {FRONTEND_PUBLIC_DATA}")

if os.path.exists(FRONTEND_DIST):
    app.mount(
        "/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{catchall:path}")
    async def serve_react_app(catchall: str):
        file_path = os.path.join(FRONTEND_DIST, catchall)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
else:
    logger.warning(f"Frontend build not found at {FRONTEND_DIST}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
