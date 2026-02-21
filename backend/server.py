"""
Halilit Support Center — JIT Architecture API Server

Lightweight FastAPI server that serves:
  1. Skeleton inventory (pre-built catalog from frontend/public/data/)
  2. JIT Intelligence endpoint (streams live product research via Gemini)
  3. Static frontend assets
"""

from fastapi.responses import StreamingResponse
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
import logging
import asyncio
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request, Query, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.project_config import FRONTEND_PUBLIC_DATA, FRONTEND_DIR, DATA_DIR
from backend.hierarchy import api as hierarchy_api
from backend.memory_utils import (
    start_memory_tracking,
    log_memory_snapshot,
    check_memory_limit,
    cleanup_large_caches,
)

# Disk cache: load pre-built catalog to avoid slow first build on restart
CATALOG_CACHE_PATH = DATA_DIR / "catalog_cache.json.gz"
CATALOG_CACHE_MAX_AGE_SEC = 86400  # 24 hours; rebuild if older

# ── Server-side catalog cache ──
_catalog_cache_json: bytes | None = None
_catalog_cache_gzip: bytes | None = None
_catalog_cache_dict: dict | None = None  # Only keep dict when actively needed
_catalog_cache_time: float = 0
# mtime of catalog_cache.json.gz when we last loaded/wrote it
_catalog_disk_mtime: float = 0
_catalog_build_lock = threading.Lock()
# In dev, use short TTL so rebuild-catalog + refresh shows new data quickly
_DEV = os.environ.get("HALILIT_DEV", "").lower() in ("1", "true", "yes")
CATALOG_CACHE_TTL = 30 if _DEV else 300  # 30s dev, 5 min prod

# Fields to strip from products in the catalog response (keep contextual_data so UI can show review_synthesis, real_world_insights, review_sources)
STRIP_FIELDS = {"search_text", "subcategory", "currency"}

# Async refresh state (thread-safe) — non-blocking catalog rebuild
_refresh_state: dict = {
    "status": "idle",  # idle | running | complete | failed
    "started_at": None,
    "finished_at": None,
    "product_count": None,
    "brands_count": None,
    "error": None,
}
_refresh_state_lock = threading.Lock()

# Catalog build progress (thread-safe) — for first-load monitoring
_build_progress: dict = {"status": "idle", "step": "",
                         "pct": 0.0, "message": "", "elapsed_s": 0}
_build_progress_lock = threading.Lock()

# ── App ──
app = FastAPI(title="Halilit Support Center", version="9.0-jit")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# LIFESPAN (startup / shutdown)
# ═══════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    # Pyroscope performance profiling (no-op when env-vars absent)
    try:
        from backend.pyroscope_integration import init_pyroscope
        init_pyroscope()
    except Exception as _pex:
        logger.debug("Pyroscope init skipped: %s", _pex)

    # Start memory tracking
    start_memory_tracking()
    log_memory_snapshot("startup")

    try:
        from backend.mcp.startup import init_mcp
        await init_mcp()
        logger.info("MCP: Ready")
    except Exception as e:
        logger.warning(f"MCP init failed: {e}")

    log_memory_snapshot("after_mcp_init")

    # Periodic memory check and cleanup
    async def periodic_memory_check():
        while True:
            await asyncio.sleep(60)  # Check every minute
            check_memory_limit()
            cleanup_large_caches()

    asyncio.create_task(periodic_memory_check())

    yield

    try:
        from backend.mcp.startup import shutdown_mcp
        await shutdown_mcp()
        logger.info("MCP: Shutdown complete")
    except Exception as e:
        logger.warning(f"MCP shutdown: {e}")

    log_memory_snapshot("shutdown")


# ═══════════════════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════════════════

app = FastAPI(title="Halilit Support Center API",
              version=__version__, lifespan=lifespan)

_origins = os.environ.get("CORS_ORIGINS", "*").strip()
_cors_origins = _origins.split(",") if _origins else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MCP Router ──
try:
    from backend.api.mcp_router import router as mcp_router
    app.include_router(mcp_router)
    logger.info("MCP endpoints registered at /api/mcp")

    # Include hierarchy API router
    app.include_router(hierarchy_api.router)
    logger.info("Hierarchy endpoints registered at /api/hierarchy")
except Exception as e:
    logger.warning(f"Failed to register MCP: {e}")

# Paths
FRONTEND_DIST = FRONTEND_DIR / "dist"


# ═══════════════════════════════════════════════════════════════════════════
# CATALOG CACHE
# ═══════════════════════════════════════════════════════════════════════════

def _invalidate_catalog_cache():
    """Force next request to rebuild catalog (used after sync)."""
    global _catalog_cache_json, _catalog_cache_gzip, _catalog_cache_dict, _catalog_cache_time, _catalog_disk_mtime
    with _catalog_build_lock:
        _catalog_cache_json = None
        _catalog_cache_gzip = None
        _catalog_cache_dict = None
        _catalog_cache_time = 0
        _catalog_disk_mtime = 0
        try:
            if CATALOG_CACHE_PATH.exists():
                CATALOG_CACHE_PATH.unlink()
        except OSError:
            pass


def _load_catalog_from_disk() -> bool:
    """Load pre-built catalog from disk. Returns True if loaded successfully.
    Invalidates cache if it lacks relationship data (required for structured-items
    accessory hierarchy: flybars/covers only under parent, not top-level cards).
    """
    global _catalog_cache_json, _catalog_cache_gzip, _catalog_cache_dict, _catalog_cache_time, _catalog_disk_mtime
    if not CATALOG_CACHE_PATH.exists():
        return False
    try:
        age = time.time() - CATALOG_CACHE_PATH.stat().st_mtime
        if age > CATALOG_CACHE_MAX_AGE_SEC:
            return False
        with gzip.open(CATALOG_CACHE_PATH, "rb") as f:
            json_bytes = f.read()
        catalog = json.loads(json_bytes.decode("utf-8"))
        rels = catalog.get("indexes", {}).get("relationships", {})
        if not rels or not isinstance(rels, dict):
            logger.info(
                "Catalog disk cache has no relationship index — invalidating so "
                "structured-items hierarchy (accessory-only families) can apply."
            )
            try:
                CATALOG_CACHE_PATH.unlink()
            except OSError:
                pass
            return False
        gzip_bytes = gzip.compress(json_bytes, compresslevel=6)
        _catalog_cache_json = json_bytes
        _catalog_cache_gzip = gzip_bytes
        _catalog_cache_dict = catalog
        _catalog_cache_time = time.time()
        _catalog_disk_mtime = CATALOG_CACHE_PATH.stat().st_mtime
        n = catalog.get("metadata", {}).get("total_products", 0)
        logger.info(
            f"Catalog: loaded from disk ({n} products, {len(json_bytes)//1024}KB)")
        return True
    except Exception as e:
        logger.warning(f"Catalog disk cache load failed: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════════
# CATALOG CACHE
# ═══════════════════════════════════════════════════════════════════════════


def _build_catalog_cache():
    """Build catalog and cache. Uses disk cache if fresh, else builds from scratch.
    If catalog_cache.json.gz was updated on disk (e.g. by conductor rebuild-catalog),
    we reload it so the UI sees new data without restarting the server.
    """
    global _catalog_cache_json, _catalog_cache_gzip, _catalog_cache_dict, _catalog_cache_time, _catalog_disk_mtime
    with _catalog_build_lock:
        now = time.time()
        if _catalog_cache_json is not None and (now - _catalog_cache_time) < CATALOG_CACHE_TTL:
            # In-memory cache valid — but if disk file was updated (e.g. rebuild-catalog), reload
            if CATALOG_CACHE_PATH.exists():
                disk_mtime = CATALOG_CACHE_PATH.stat().st_mtime
                if disk_mtime > _catalog_disk_mtime:
                    _catalog_cache_json = None
                    _catalog_cache_gzip = None
                    _catalog_cache_dict = None
                    _catalog_cache_time = 0
                    _catalog_disk_mtime = 0
                    logger.info(
                        "Catalog disk file updated — will reload on next use")
            if _catalog_cache_json is not None:
                return
        # Fast path: load from disk cache
        if _load_catalog_from_disk():
            return
        # Slow path: full build with progress reporting
        t0 = time.time()

        def on_progress(step: str, pct: float, msg: str) -> None:
            with _build_progress_lock:
                _build_progress["status"] = "building"
                _build_progress["step"] = step
                _build_progress["pct"] = pct
                _build_progress["message"] = msg
                _build_progress["elapsed_s"] = int(time.time() - t0)

        with _build_progress_lock:
            _build_progress["status"] = "building"
            _build_progress["step"] = "start"
            _build_progress["pct"] = 0.0
            _build_progress["message"] = "Building catalog..."
            _build_progress["elapsed_s"] = 0

        catalog = build_catalog(
            str(FRONTEND_PUBLIC_DATA),
            resolve=False,
            on_progress=on_progress,
        )

        with _build_progress_lock:
            _build_progress["status"] = "idle"
            _build_progress["pct"] = 1.0

        for p in catalog["products"]:
            for field in STRIP_FIELDS:
                p.pop(field, None)

        catalog["metadata"]["timestamp"] = datetime.now().isoformat()

        json_bytes = json.dumps(catalog, ensure_ascii=False).encode("utf-8")
        gzip_bytes = gzip.compress(json_bytes, compresslevel=6)

        _catalog_cache_json = json_bytes
        _catalog_cache_gzip = gzip_bytes
        # Only keep dict in memory if memory is available (will rebuild from JSON when needed)
        mem_check = check_memory_limit()
        if mem_check:
            _catalog_cache_dict = catalog
        else:
            _catalog_cache_dict = None  # Free memory, will rebuild from JSON when needed
            logger.info(
                "Memory limit high — keeping catalog dict out of memory")
        _catalog_cache_time = time.time()
        ms = int((time.time() - t0) * 1000)

        log_memory_snapshot("after_catalog_build")

        # Persist for fast restarts
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with gzip.open(CATALOG_CACHE_PATH, "wb", compresslevel=6) as f:
                f.write(json_bytes)
            _catalog_disk_mtime = CATALOG_CACHE_PATH.stat().st_mtime
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


def _run_refresh_background():
    """Run catalog refresh in background thread. Updates _refresh_state when done."""
    global _refresh_state
    with _refresh_state_lock:
        _refresh_state["status"] = "running"
        _refresh_state["started_at"] = datetime.now().isoformat()
        _refresh_state["finished_at"] = None
        _refresh_state["product_count"] = None
        _refresh_state["brands_count"] = None
        _refresh_state["error"] = None
    try:
        _invalidate_catalog_cache()
        service = get_conductor_data_service()
        service._catalog_cache = None
        service._cache_timestamp = None
        _build_catalog_cache()
        meta = _catalog_cache_dict.get(
            "metadata", {}) if _catalog_cache_dict else {}
        with _refresh_state_lock:
            _refresh_state["status"] = "complete"
            _refresh_state["finished_at"] = datetime.now().isoformat()
            _refresh_state["product_count"] = meta.get("total_products", 0)
            _refresh_state["brands_count"] = len(meta.get("brands", []))
        logger.info(
            f"Background refresh complete: {_refresh_state['product_count']} products")
    except Exception as e:
        logger.error(f"Background refresh failed: {e}")
        with _refresh_state_lock:
            _refresh_state["status"] = "failed"
            _refresh_state["finished_at"] = datetime.now().isoformat()
            _refresh_state["error"] = str(e)


_startup_thread = threading.Thread(target=_startup_catalog_build, daemon=True)
_startup_thread.start()


# ═══════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

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


@app.get("/api/health/deep")
async def deep_health_check():
    """Active Sonar deep-check — validates internal organs, not just process liveness."""
    import psutil

    # ── Check 1: Catalog accessibility ──────────────────────────────────────
    catalog_status = "OK"
    catalog_product_count = 0
    try:
        data_service = get_conductor_data_service()
        catalog = data_service.get_catalog()
        catalog_product_count = len(catalog.get("products", []))
        if catalog_product_count == 0:
            catalog_status = "EMPTY"
    except Exception as exc:
        catalog_status = f"ERROR: {exc}"

    # ── Check 2: JIT cache directory ─────────────────────────────────────────
    jit_cache_dir = DATA_DIR / "jit_cache"
    jit_cache_status = "OK" if jit_cache_dir.exists() else "MISSING"

    # ── Check 3: Memory ──────────────────────────────────────────────────────
    proc = psutil.Process(os.getpid())
    memory_mb = proc.memory_info().rss / 1024 / 1024

    overall = "operational" if catalog_status == "OK" else "degraded"

    return {
        "status": overall,
        "timestamp": time.time(),
        "version": __version__,
        "core": {
            "catalog": catalog_status,
            "catalog_product_count": catalog_product_count,
            "jit_cache": jit_cache_status,
        },
        "memory_usage_mb": round(memory_mb, 2),
    }


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Operator Dashboard key metrics: total products, calls-for-price count,
    last ingestion run status, distinct brands count."""
    global _catalog_cache_json, _catalog_cache_dict, _catalog_cache_time
    try:
        now = time.time()
        # Use cached dict if available; otherwise parse from JSON bytes
        if _catalog_cache_dict is not None and (now - _catalog_cache_time) <= CATALOG_CACHE_TTL:
            catalog = _catalog_cache_dict
        elif _catalog_cache_json is not None:
            catalog = json.loads(_catalog_cache_json.decode("utf-8"))
        else:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _build_catalog_cache)
            if _catalog_cache_json is None:
                return JSONResponse(status_code=503, content={"error": "Catalog still building"})
            catalog = json.loads(_catalog_cache_json.decode("utf-8"))

        products = catalog.get("products", [])
        total = len(products)
        cfp = sum(1 for p in products if not p.get("price"))
        brands = len({p.get("brand", "") for p in products if p.get("brand")})

        with _refresh_state_lock:
            refresh = dict(_refresh_state)

        last_run: dict = {"status": "never",
                          "finished_at": None, "product_count": None}
        if refresh.get("finished_at"):
            last_run = {
                "status": refresh.get("status", "unknown"),
                "finished_at": refresh["finished_at"],
                "product_count": refresh.get("product_count"),
            }
        elif refresh.get("status") == "running":
            last_run = {"status": "running",
                        "finished_at": None, "product_count": None}

        return {
            "total_products": total,
            "calls_for_price": cfp,
            "top_brands_count": brands,
            "last_ingestion_run": last_run,
        }
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


def _get_catalog_dict() -> dict | None:
    """Return catalog as dict. Uses in-memory cache or rebuilds from JSON bytes."""
    global _catalog_cache_dict
    if _catalog_cache_dict is not None:
        return _catalog_cache_dict
    if _catalog_cache_json is not None:
        try:
            catalog = json.loads(_catalog_cache_json.decode("utf-8"))
            _catalog_cache_dict = catalog
            return catalog
        except Exception:
            pass
    return None


@app.get("/api/conductor/catalog")
async def get_conductor_catalog(
    request: Request,
    page: int = Query(
        default=0, ge=0, description="Page (1-based). 0 = legacy full blob."),
    page_size: int = Query(default=25, ge=1, le=200, alias="pageSize"),
    search: str = Query(default=""),
    sort_by: str = Query(default="", alias="sortBy"),
    category: str = Query(default=""),
    brand: str = Query(default=""),
):
    """Single source of truth — pre-indexed catalog from skeleton inventory.

    When pagination parameters are supplied (page ≥ 1, or search/category/brand),
    returns a PaginatedCatalogResponse JSON object with server-side filtering.
    When called with no params, returns the full catalog blob (legacy behaviour).
    """
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

        # ── Paginated / filtered path ───────────────────────────────────────
        is_paginated = page >= 1 or bool(search) or bool(
            category) or bool(brand) or bool(sort_by)
        if is_paginated:
            catalog = _get_catalog_dict()
            if catalog is None:
                return JSONResponse(status_code=503, content={"error": "Catalog unavailable"})

            products: list[dict] = list(catalog.get("products", []))

            # Search filter — name, sku, brand, description
            if search:
                q = search.lower()
                products = [
                    p for p in products
                    if q in (p.get("name") or "").lower()
                    or q in (p.get("sku") or "").lower()
                    or q in (p.get("brand") or "").lower()
                    or q in (p.get("description") or "").lower()
                    or q in (p.get("description_short") or "").lower()
                ]

            # Category filter
            if category:
                cat_lower = category.lower()
                products = [p for p in products if (
                    p.get("category") or "").lower() == cat_lower]

            # Brand filter
            if brand:
                brand_lower = brand.lower()
                products = [p for p in products if (
                    p.get("brand") or "").lower() == brand_lower]

            # Sort
            if sort_by == "price_asc":
                products = sorted(products, key=lambda p: (
                    p.get("price") is None, p.get("price") or 0))
            elif sort_by == "price_desc":
                products = sorted(products, key=lambda p: (
                    p.get("price") is None, -(p.get("price") or 0)))
            elif sort_by == "name_asc":
                products = sorted(products, key=lambda p: (
                    p.get("name") or "").lower())
            # Default: in-stock items first, then CfP
            else:
                products = sorted(products, key=lambda p: (
                    p.get("price") is None, (p.get("name") or "").lower()))

            # Paginate
            effective_page = max(1, page)
            total_items = len(products)
            total_pages = max(1, (total_items + page_size - 1) // page_size)
            start = (effective_page - 1) * page_size
            page_products = products[start: start + page_size]

            return JSONResponse({
                "products": page_products,
                "totalItems": total_items,
                "totalPages": total_pages,
                "currentPage": effective_page,
                "pageSize": page_size,
            })

        # ── Legacy full-blob path ───────────────────────────────────────────
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


# ── Removed endpoints (Out of Scope per OPERATOR_CONSOLE_SPEC.md) ─────────────
# Galaxy, Spectrum, Arena, VisualGrouping views have been frozen and removed.
# These stubs return 410 Gone so callers get a clear signal instead of a 404.

@app.get("/api/spectrum/{spectrum_id}")
async def get_spectrum_star_view(spectrum_id: str):
    """Removed — Spectrum views are out of scope per OPERATOR_CONSOLE_SPEC.md."""
    return JSONResponse(status_code=410, content={"error": "Spectrum views removed. Use /api/conductor/catalog."})


@app.get("/api/structured-items")
async def get_structured_items():
    """Removed — Structured items endpoint is out of scope per OPERATOR_CONSOLE_SPEC.md."""
    return JSONResponse(status_code=410, content={"error": "Structured-items removed. Use /api/conductor/catalog."})


@app.post("/api/visual-grouping/suggest")
async def post_visual_grouping_suggest(request: Request):
    """Removed — Visual grouping is out of scope per OPERATOR_CONSOLE_SPEC.md."""
    return JSONResponse(status_code=410, content={"error": "Visual-grouping removed. Use /api/conductor/catalog."})


@app.get("/api/catalog/health")
async def get_catalog_health():
    """Catalog health metrics."""
    try:
        from backend.catalog_validator import validate_catalog

        global _catalog_cache_dict, _catalog_cache_time, _catalog_cache_json
        now = time.time()
        if _catalog_cache_dict is not None and (now - _catalog_cache_time) <= CATALOG_CACHE_TTL:
            catalog = _catalog_cache_dict
        elif _catalog_cache_json is not None:
            # Rebuild from JSON if dict not in memory
            catalog = json.loads(_catalog_cache_json.decode("utf-8"))
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


@app.get("/api/conductor/build/status")
async def get_catalog_build_status():
    """Poll catalog build progress during first load. Returns status, pct (0-1), message, elapsed_s."""
    with _build_progress_lock:
        return dict(_build_progress)


@app.get("/api/conductor/categories")
async def get_conductor_categories():
    """Category summary for navigation."""
    try:
        service = get_conductor_data_service()
        return service.get_category_summary()
    except Exception as e:
        return {"error": str(e), "categories": []}


@app.get("/api/conductor/subcategories")
async def get_conductor_subcategories(include_brands: bool = False):
    """
    Subcategory summary:
    - product_count per subcategory
    - brand_count (distinct brands) per subcategory
    - optionally include explicit brand list (include_brands=true)
    """
    try:
        service = get_conductor_data_service()
        return service.get_subcategory_summary(include_brands=include_brands)
    except Exception as e:
        return {"error": str(e), "subcategories": []}


@app.get("/api/conductor/refresh")
async def refresh_conductor_catalog(block: bool = False):
    """
    Trigger catalog refresh. By default returns immediately (async).
    - block=true: Wait for completion (legacy behavior; can freeze API for 30s+).
    - block=false: Start background refresh, return immediately. Poll /api/conductor/refresh/status.
    """
    with _refresh_state_lock:
        is_running = _refresh_state["status"] == "running"

    if is_running:
        return {
            "status": "running",
            "message": "Refresh already in progress. Poll /api/conductor/refresh/status",
        }

    if block:
        try:
            _invalidate_catalog_cache()
            service = get_conductor_data_service()
            service._catalog_cache = None
            service._cache_timestamp = None
            _build_catalog_cache()
            meta = _catalog_cache_dict.get(
                "metadata", {}) if _catalog_cache_dict else {}
            return {
                "status": "refreshed",
                "product_count": meta.get("total_products", 0),
                "brands": len(meta.get("brands", [])),
                "timestamp": meta.get("timestamp", datetime.now().isoformat()),
            }
        except Exception as e:
            logger.error(f"Refresh failed: {e}")
            return {"error": str(e), "status": "failed"}

    # Non-blocking: start background thread and return immediately
    thread = threading.Thread(target=_run_refresh_background, daemon=True)
    thread.start()
    return {
        "status": "started",
        "message": "Refresh in progress. Poll GET /api/conductor/refresh/status for progress.",
    }


@app.get("/api/conductor/refresh/status")
async def refresh_conductor_status():
    """Poll refresh progress. Returns status (idle|running|complete|failed) and result when done."""
    with _refresh_state_lock:
        state = dict(_refresh_state)
    result = {"status": state["status"]}
    if state["status"] == "complete":
        result["product_count"] = state["product_count"]
        result["brands"] = state["brands_count"]
        result["finished_at"] = state["finished_at"]
    elif state["status"] == "failed":
        result["error"] = state["error"]
        result["finished_at"] = state["finished_at"]
    elif state["status"] == "running":
        result["started_at"] = state["started_at"]
    return result


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
# PRODUCT SEARCH (OpenClaw / Employee Concierge)
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/products/search")
async def products_search(q: str = ""):
    """
    Search products by name, brand, or model. Used by OpenClaw skills and
    employee concierge (WhatsApp/Telegram) to look up price, stock, and specs.
    """
    if not q or len(q.strip()) < 2:
        return {"products": [], "total": 0}
    try:
        service = get_conductor_data_service()
        result = service.filter_products({"search_query": q.strip()})
        products = result.get("products", [])[:20]
        # Minimal payload for chat/OpenClaw: id, name, brand, price
        out = [
            {
                "id": p.get("halilit_id"),
                "product_name": p.get("product_name"),
                "brand": p.get("brand"),
                "price_il": p.get("price_il"),
            }
            for p in products
        ]
        return {"products": out, "total": result.get("total_results", len(out))}
    except Exception as e:
        logger.warning("products/search failed: %s", e)
        return {"products": [], "total": 0, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
# IMAGE VALIDATION  (spec: evolution_clarifai_s_image_moderation_api.md)
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/validate-image", tags=["images"])
async def validate_image(url: str):
    """
    Validate that a hero image URL is reachable and contains a valid image.

    Performs an HTTP HEAD request + optional Content-Type check using the
    ImageValidator service.  No external AI service is required — validation
    is structural (HTTP status + MIME type), not semantic.

    Query param:
        url (str): The image URL to validate.

    Returns:
        {valid, status_code, content_type, reason, url}
    """
    if not url:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="url parameter is required")
    try:
        from backend.image_validator import validate_image_url
        result = validate_image_url(url, verify_bytes=False)
        return result
    except Exception as exc:
        logger.warning("validate-image error: %s", exc)
        return {"url": url, "valid": False, "status_code": None,
                "content_type": None, "reason": f"error:{exc}"}


@app.post("/api/validate-catalog-images", tags=["images"])
async def validate_catalog_images_endpoint():
    """
    Validate hero image URLs for all products in the catalog.
    Returns {product_id: {valid, reason, ...}} for every product that has a hero URL.
    Heavy operation — run rarely (e.g. nightly via the heartbeat daemon).
    """
    try:
        from backend.image_validator import validate_catalog_images
        service = get_conductor_data_service()
        catalog = service.get_unified_catalog()
        results = validate_catalog_images(catalog.get("products", []))
        invalid = {pid: r for pid, r in results.items() if not r["valid"]}
        return {
            "total_checked": len(results),
            "invalid_count": len(invalid),
            "invalid": invalid,
        }
    except Exception as exc:
        logger.error("validate-catalog-images error: %s", exc)
        return {"error": str(exc)}


# ═══════════════════════════════════════════════════════════════════════════
# JIT INTELLIGENCE ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════


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

# ═══════════════════════════════════════════════════════════════════════════
# TELEMETRY NERVE — Sentry Reflex Arc
# ═══════════════════════════════════════════════════════════════════════════


@app.post("/api/webhooks/sentry", status_code=200, tags=["webhooks"])
async def sentry_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Receive Sentry error webhooks and dispatch the Telemetry Agent.

    Returns 200 immediately so Sentry doesn't retry, then processes the
    payload asynchronously via BackgroundTasks.
    """
    try:
        payload = await request.json()
    except Exception:
        payload = {"message": "(unparseable payload)", "event": {}}

    try:
        from backend.factory.telemetry_agent import process_production_error  # type: ignore
        background_tasks.add_task(process_production_error, payload)
    except Exception as exc:
        logger.error("Telemetry Agent import failed: %s", exc)

    return {"status": "received", "message": "Telemetry Nerve activated."}


# Mount images directory if it exists (for locally cached product images)
IMAGES_DIR = DATA_DIR / "images"
if IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")
    logger.info(f"Serving /images from {IMAGES_DIR}")

# Mount frontend public assets (for placeholder images, etc.)
# Only mount if dist doesn't exist (dist takes precedence)
if not os.path.exists(FRONTEND_DIST):
    FRONTEND_ASSETS = FRONTEND_DIR / "public" / "assets"
    if FRONTEND_ASSETS.exists():
        app.mount(
            "/assets", StaticFiles(directory=str(FRONTEND_ASSETS)), name="assets")
        logger.info(f"Serving /assets from {FRONTEND_ASSETS}")

if os.path.exists(FRONTEND_DIST):
    app.mount(
        "/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

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
