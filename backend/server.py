<<<<<<< Updated upstream
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
=======
from datetime import datetime
from typing import Dict
from backend.thomann_comparison import get_thomann_comparison, TARGET_BRANDS
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from backend.auto_sync_engine import get_auto_sync_engine
from backend.unified_data_service_v73 import get_conductor_data_service
from backend.scrapers.comparison_api import ComparisonAPI
from backend.scrapers.ingestion_orchestrator import IngestionOrchestrator
from backend.scrapers.thomann_scraper import ThomannScraper, ThomannProduct
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
from datetime import datetime
from fastapi import FastAPI, Request, Query, BackgroundTasks
=======
from fastapi import FastAPI, BackgroundTasks
>>>>>>> Stashed changes
=======
from fastapi import FastAPI, BackgroundTasks
>>>>>>> Stashed changes
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

# ── JIT Innovation Pipeline Router ──
try:
    from backend.api.innovation_router import router as innovation_router
    app.include_router(innovation_router)
    logger.info("Innovation pipeline endpoints registered at /api/innovation")
except Exception as e:
    logger.warning(f"Failed to register JIT Innovation router: {e}")

# ── Liquid Route Manager (Level 10 SDUI) ──
try:
    from backend.api.liquid_router import router as liquid_router
    app.include_router(liquid_router)
    logger.info(
        "Liquid Router registered at /api/liquid — in-memory SDUI engine active")
except Exception as e:
    logger.warning(f"Failed to register Liquid Router: {e}")

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

<<<<<<< Updated upstream
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
=======

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


# ========== THOMANN-HALILIT PRICE COMPARISON ENDPOINTS ==========


# Sample Thomann product database (would be fetched from Thomann API in production)
# ⚠️ DEPRECATED: Mock data removed - now using real web scraping via ThomannScraper
# See get_thomann_products_by_brand() function below for real data integration
# Removed - was hardcoded fictional data
THOMANN_PRODUCTS_DATABASE_DEPRECATED = {}


# Cache for Thomann products (avoids re-scraping on every request)
_THOMANN_PRODUCT_CACHE = {
    "products": None,  # List[ThomannProduct]
    # Dict mapping brand→{product_name→{price_eur, weight_kg}}
    "by_brand": None,
    "timestamp": None,
    "source": None  # "live_scraper", "test_data", or "error"
}

# Environment flag: USE_TEST_DATA=1 to always use test dataset
USE_TEST_DATA = os.getenv("USE_TEST_DATA", "0") == "1"


def load_thomann_test_data() -> Dict[str, Dict]:
    """Load test Thomann products from JSON file (for development/fallback)"""
    try:
        test_data_path = Path(__file__).parent / \
            "scrapers" / "thomann_test_data.json"
        if test_data_path.exists():
            with open(test_data_path) as f:
                data = json.load(f)
                # Extract brand data (skip metadata)
                by_brand = {k: v for k, v in data.items() if k != "_metadata"}
                logger.info(
                    f"✅ Loaded test data for {len(by_brand)} brands from {test_data_path.name}")
                return by_brand
        else:
            logger.warning(f"Test data not found at {test_data_path}")
            return {}
    except Exception as e:
        logger.error(f"Failed to load test data: {e}")
        return {}


@app.get("/api/comparison/brands")
async def get_comparison_brands():
    """Get list of brands available for comparison"""
    return {
        "brands": TARGET_BRANDS,
        "count": len(TARGET_BRANDS),
        "description": "Thomann-Halilit price comparison available for these brands"
    }


def get_thomann_products_by_brand() -> Dict[str, Dict]:
    """
    Get Thomann products by brand using REAL web scraping (with test data fallback).

    Returns:
        Dict mapping brand_name → {product_name → {price_eur, weight_kg, product_url, in_stock}}

    Priority:
        1. Return cached data if available (recent)
        2. Try live web scraping (ThomannScraper)
        3. Fall back to test data (thomann_test_data.json)
        4. Return empty dict if all else fails

    Environment:
        - USE_TEST_DATA=1: Skip live scraping, use test data directly
    """
    global _THOMANN_PRODUCT_CACHE

    try:
        # Return cached data if available and fresh (< 1 hour old)
        if _THOMANN_PRODUCT_CACHE["by_brand"] is not None:
            if _THOMANN_PRODUCT_CACHE.get("timestamp"):
                from datetime import timedelta
                cache_time = datetime.fromisoformat(
                    _THOMANN_PRODUCT_CACHE["timestamp"])
                if datetime.now() - cache_time < timedelta(hours=1):
                    logger.info(
                        f"🔄 Using cached Thomann data (source: {_THOMANN_PRODUCT_CACHE.get('source')})")
                    return _THOMANN_PRODUCT_CACHE["by_brand"]

        # Check if test data mode is forced
        if USE_TEST_DATA:
            logger.info("📋 TEST MODE: Using test dataset (USE_TEST_DATA=1)")
            test_data = load_thomann_test_data()
            if test_data:
                _THOMANN_PRODUCT_CACHE["by_brand"] = test_data
                _THOMANN_PRODUCT_CACHE["timestamp"] = datetime.now(
                ).isoformat()
                _THOMANN_PRODUCT_CACHE["source"] = "test_data (forced)"
                return test_data

        # Try live scraping
        logger.info("🌐 Attempting REAL Thomann data from thomannmusic.com...")
        try:
            scraper = ThomannScraper(max_pages_per_category=3)
            products, stats = scraper.scrape_all_categories()

            if stats['total_products'] > 0:
                logger.info(
                    f"✅ Scraped {stats['total_products']} real products from Thomann")

                # Index by brand
                by_brand = {}
                for product in products:
                    brand_lower = product.brand.lower()
                    if brand_lower not in by_brand:
                        by_brand[brand_lower] = {}

                    by_brand[brand_lower][product.product_name] = {
                        "price_eur": product.price_eur,
                        "weight_kg": product.weight_kg or 0,
                        "product_url": product.product_url,
                        "in_stock": product.in_stock,
                    }

                _THOMANN_PRODUCT_CACHE["by_brand"] = by_brand
                _THOMANN_PRODUCT_CACHE["timestamp"] = datetime.now(
                ).isoformat()
                _THOMANN_PRODUCT_CACHE["source"] = "live_scraper"
                logger.info(
                    f"✅ Indexed {len(by_brand)} brands from REAL Thomann data")
                return by_brand
            else:
                logger.warning(
                    f"⚠️  Live scraping returned 0 products. Stats: {stats}")
                raise Exception("Live scraper returned no products")

        except Exception as scrape_error:
            logger.warning(f"🌐 Live scraping failed: {scrape_error}")
            logger.info("🔄 Falling back to test data...")

            # Fall back to test data
            test_data = load_thomann_test_data()
            if test_data:
                logger.info(
                    f"📋 Using fallback test data for {len(test_data)} brands")
                _THOMANN_PRODUCT_CACHE["by_brand"] = test_data
                _THOMANN_PRODUCT_CACHE["timestamp"] = datetime.now(
                ).isoformat()
                _THOMANN_PRODUCT_CACHE["source"] = "test_data (fallback)"
                return test_data
            else:
                logger.error("❌ Both live scraping AND test data failed")
                raise

    except Exception as e:
        logger.error(f"🚨 CRITICAL: Final fallback failed: {e}")
        logger.warning(
            "⚠️  Returning empty dict - comparison will skip Thomann")
        _THOMANN_PRODUCT_CACHE["source"] = "error"
        return {}


@app.get("/api/comparison/all")
async def get_all_brands_comparison():
    """
    Get comparison summary for all target brands.

    Returns high-level metrics without detailed product listings.
    """
    try:
        results = {
            "timestamp": datetime.now().isoformat(),
            "brands": {},
            "overall_summary": {
                "total_brands": len(TARGET_BRANDS),
                "total_products_compared": 0,
                "total_matched": 0,
                "avg_price_diff_percent": 0,
>>>>>>> Stashed changes
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


<<<<<<< Updated upstream
<<<<<<< Updated upstream
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
=======
=======
>>>>>>> Stashed changes
            # 🌐 GET REAL THOMANN DATA (no longer using fake hardcoded database)
            thomann_by_brand = get_thomann_products_by_brand()
            thomann_data = thomann_by_brand.get(brand, {})
            comparison = comparison_service.compare_brand_catalog(
                brand=brand,
                halilit_products=halilit_by_brand[brand],
                thomann_products_map=thomann_data
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
            for p in products
        ]
        return {"products": out, "total": result.get("total_results", len(out))}
=======

        # 🌐 GET REAL THOMANN DATA (no longer using fake hardcoded database)
        thomann_by_brand = get_thomann_products_by_brand()
        thomann_data = thomann_by_brand.get(brand_lower, {})

        # Create comparison
        comparison = comparison_service.compare_brand_catalog(
            brand=brand_lower,
            halilit_products=halilit_by_brand[brand_lower],
            thomann_products_map=thomann_data
        )

        logger.info(
            f"✅ Generated comparison for {brand_lower}: {comparison['summary']['total_products']} products")

        return comparison

>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
    Query param:
        url (str): The image URL to validate.
=======
        if not all([brand, halilit_product_id]):
            return {"error": "brand and halilit_product_id required"}

        # Get Halilit product
        service = get_conductor_data_service()
        catalog = service.get_unified_catalog()

        halilit_product = None
        for p in catalog["products"]:
            if p.get("id") == halilit_product_id:
                halilit_product = p
                break

        if not halilit_product:
            return {"error": f"Product {halilit_product_id} not found"}

        # Create validated comparison
        comparison_service = get_thomann_comparison()
        comparison = comparison_service.create_price_comparison(
            halilit_product=halilit_product,
            thomann_price_eur=thomann_price_eur,
            thomann_weight_kg=thomann_weight_kg,
            matched=bool(thomann_price_eur),
            confidence_score=100 if thomann_model else 0
        )

        logger.info(
            f"✅ Validated comparison for {halilit_product.get('product_name')}")

        return comparison.to_dict()

    except Exception as e:
        logger.error(f"Validation error: {e}")
        return {"error": str(e)}


# ========== FULL-SCALE COMPARISON ENDPOINTS ==========
# These endpoints compare ALL Halilit products to Thomann products


@app.get("/api/v2/comparison/full")
async def get_full_comparison():
    """
    Get comprehensive comparison across ALL products.

    This endpoint:
    - Loads all Halilit products from database
    - Loads all Thomann products from database
    - Compares them using fuzzy matching
    - Returns detailed statistics and results

    Note: May take 10-30 seconds on first call, cached afterward.
    """
    try:
        from backend.scrapers.comparison_api import get_comparison_api

        api = get_comparison_api()
        comparison_data = api.get_comprehensive_comparison()

        return {
            "status": "success",
            "meta": comparison_data["meta"],
            "total_products": len(comparison_data["comparisons"]),
            "note": "Use /api/v2/comparison/full/paginated for paginated results",
        }

    except Exception as e:
        logger.error(f"Full comparison error: {e}")
        return {
            "error": str(e),
            "message": "Make sure to run data ingestion first: python backend/scrapers/ingestion_orchestrator.py",
        }


@app.get("/api/v2/comparison/full/paginated")
async def get_paginated_comparison(page: int = 1, page_size: int = 50, min_confidence: float = 0.0):
    """
    Get paginated comparison results.

    Query parameters:
    - page: Page number (1-indexed)
    - page_size: Results per page (default: 50, max: 500)
    - min_confidence: Minimum match confidence 0-100 (default: 0)
    """
    try:
        from backend.scrapers.comparison_api import get_comparison_api

        # Limit page size
        page_size = min(page_size, 500)

        api = get_comparison_api()
        paginated_results = api.get_paginated_comparisons(
            page=page, page_size=page_size, min_confidence=min_confidence
        )

        return {
            "status": "success",
            "pagination": {
                "page": paginated_results["page"],
                "page_size": paginated_results["page_size"],
                "total_results": paginated_results["total_results"],
                "total_pages": paginated_results["total_pages"],
                "has_next": paginated_results["has_next"],
                "has_prev": paginated_results["has_prev"],
            },
            "results": paginated_results["results"],
        }

    except Exception as e:
        logger.error(f"Paginated comparison error: {e}")
        return {"error": str(e)}


@app.get("/api/v2/comparison/full/brand/{brand}")
async def get_brand_full_comparison(brand: str):
    """
    Get all comparisons for a specific brand.

    Examples: /api/v2/comparison/full/brand/montarbo
    """
    try:
        from backend.scrapers.comparison_api import get_comparison_api

        api = get_comparison_api()
        brand_data = api.get_brand_comparison_all(brand)

        return {
            "status": "success",
            "brand": brand,
            "data": brand_data,
        }

    except Exception as e:
        logger.error(f"Brand comparison error: {e}")
        return {"error": str(e)}


@app.get("/api/v2/comparison/full/export-csv")
async def export_full_comparison_csv():
    """
    Export all comparisons to CSV file.

    Returns downloadable CSV with all products, prices, and differences.
    """
    try:
        from backend.scrapers.comparison_api import get_comparison_api

        api = get_comparison_api()
        filepath = api.export_full_comparison_csv()

        return FileResponse(filepath, filename="halilit_thomann_full_comparison.csv")

    except Exception as e:
        logger.error(f"CSV export error: {e}")
        return {"error": str(e)}


@app.post("/api/v2/comparison/full/run-ingestion")
async def run_full_data_ingestion(skip_halilit: bool = False, skip_thomann: bool = False):
    """
    Trigger complete data ingestion from Halilit and Thomann.

    This endpoint:
    1. Scrapes all categories with pagination
    2. Stores products in SQLite database
    3. Clears comparison cache (triggers recalculation)

    Parameters:
    - skip_halilit: Skip Halilit scraping
    - skip_thomann: Skip Thomann scraping

    ⚠️ WARNING: This may take 30-60 minutes depending on site sizes.
    Run in background: curl -X POST 'http://localhost:8000/api/v2/comparison/full/run-ingestion' &
    """
    try:
        from backend.scrapers.ingestion_orchestrator import IngestionOrchestrator
        from backend.scrapers.comparison_api import get_comparison_api

        logger.info("🚀 Starting full-scale data ingestion...")
        logger.info(
            f"  Skip Halilit: {skip_halilit}, Skip Thomann: {skip_thomann}")

        orchestrator = IngestionOrchestrator()
        stats = orchestrator.run_full_ingestion(
            skip_halilit=skip_halilit, skip_thomann=skip_thomann
        )

        # Clear cache to force recalculation
        api = get_comparison_api()
        api.clear_cache()

        # Export to JSON
        orchestrator.export_database_to_json()

        logger.info("✅ Ingestion complete, cache cleared")

        return {
            "status": "success",
            "message": "Data ingestion complete. Cache cleared for fresh comparison.",
            "stats": stats,
        }

    except Exception as e:
        logger.error(f"Ingestion error: {e}", exc_info=True)
        return {"error": str(e), "details": "Check server logs for details"}


@app.get("/api/v2/comparison/full/database-stats")
async def get_database_statistics():
    """
    Get current database statistics.
>>>>>>> Stashed changes

    Returns:
        {valid, status_code, content_type, reason, url}
    """
    if not url:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400, detail="url parameter is required")
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


<<<<<<< Updated upstream
# ═══════════════════════════════════════════════════════════════════════════
# STATIC FILES & FRONTEND
# ═══════════════════════════════════════════════════════════════════════════
=======
# ========== FULL-SCALE COMPARISON ENDPOINTS (v2) ==========

# Initialize comparison API (singleton)
_comparison_api = None


def get_comparison_api():
    global _comparison_api
    if _comparison_api is None:
        _comparison_api = ComparisonAPI()
    return _comparison_api


@app.post("/api/v2/comparison/full/run-ingestion")
async def run_full_ingestion(background_tasks: BackgroundTasks, skip_halilit: bool = False, skip_thomann: bool = False):
    """
    Start full-scale data ingestion in background.
    Scrapes all products from Halilit.com and Thomannmusic.com with pagination.

    Returns immediately, ingestion runs in background (30-60 minutes).
    """
    try:
        def ingestion_task():
            try:
                orchestrator = IngestionOrchestrator()
                logger.info("🚀 Starting full-scale ingestion...")
                orchestrator.run_full_ingestion(
                    skip_halilit=skip_halilit, skip_thomann=skip_thomann)
                logger.info("✅ Full-scale ingestion complete")
                # Clear API cache after ingestion
                api = get_comparison_api()
                api.clear_cache()
            except Exception as e:
                logger.error(f"❌ Ingestion failed: {e}", exc_info=True)

        background_tasks.add_task(ingestion_task)
        return {
            "status": "ingestion_started",
            "message": "Full-scale ingestion started in background",
            "estimated_duration_minutes": "30-60",
            "skip_halilit": skip_halilit,
            "skip_thomann": skip_thomann
        }
    except Exception as e:
        logger.error(f"Ingestion start error: {e}")
        return {"error": str(e), "status": "failed"}, 500


@app.get("/api/v2/comparison/full")
async def get_full_comparison_overview():
    """Get overview statistics of comparison database."""
    try:
        api = get_comparison_api()
        stats = api.get_database_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Overview error: {e}")
        return {"error": str(e)}, 500


@app.get("/api/v2/comparison/full/paginated")
async def get_paginated_comparisons(page: int = 1, page_size: int = 50, min_confidence: float = 0):
    """Get paginated comparison results with optional filtering."""
    try:
        api = get_comparison_api()
        results = api.get_paginated_comparisons(
            page=page, page_size=page_size, min_confidence=min_confidence)
        return {
            "status": "success",
            "page": page,
            "page_size": page_size,
            "min_confidence": min_confidence,
            "data": results
        }
    except Exception as e:
        logger.error(f"Pagination error: {e}")
        return {"error": str(e)}, 500


@app.get("/api/v2/comparison/full/brand/{brand}")
async def get_brand_comparison_full(brand: str):
    """Get comprehensive comparison for a specific brand."""
    try:
        api = get_comparison_api()
        results = api.get_brand_comparison_all(brand=brand)
        return {
            "status": "success",
            "brand": brand,
            "data": results
        }
    except Exception as e:
        logger.error(f"Brand comparison error: {e}")
        return {"error": str(e)}, 500


@app.get("/api/v2/comparison/full/export-csv")
async def export_full_comparison_csv():
    """Export all comparisons as CSV file."""
    try:
        api = get_comparison_api()
        csv_path = api.export_full_comparison_csv()
        return FileResponse(path=csv_path, media_type="text/csv", filename="comparison_full_export.csv")
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        return {"error": str(e)}, 500


@app.get("/api/v2/comparison/full/database-stats")
async def get_database_statistics():
    """Get raw database statistics."""
    try:
        api = get_comparison_api()
        stats = api.get_database_stats()
        return stats
    except Exception as e:
        logger.error(f"Database stats error: {e}")
        return {"error": str(e)}, 500


# ========== FULL-SCALE COMPARISON ENDPOINTS (v2) ==========

# Initialize comparison API (singleton)
_comparison_api = None


def get_comparison_api():
    global _comparison_api
    if _comparison_api is None:
        _comparison_api = ComparisonAPI()
    return _comparison_api


@app.post("/api/v2/comparison/full/run-ingestion")
async def run_full_ingestion(background_tasks: BackgroundTasks, skip_halilit: bool = False, skip_thomann: bool = False):
    """
    Start full-scale data ingestion in background.
    Scrapes all products from Halilit.com and Thomannmusic.com with pagination.

    Returns immediately, ingestion runs in background (30-60 minutes).
    """
    try:
        def ingestion_task():
            try:
                orchestrator = IngestionOrchestrator()
                logger.info("🚀 Starting full-scale ingestion...")
                orchestrator.run_full_ingestion(
                    skip_halilit=skip_halilit, skip_thomann=skip_thomann)
                logger.info("✅ Full-scale ingestion complete")
                # Clear API cache after ingestion
                api = get_comparison_api()
                api.clear_cache()
            except Exception as e:
                logger.error(f"❌ Ingestion failed: {e}", exc_info=True)

        background_tasks.add_task(ingestion_task)
        return {
            "status": "ingestion_started",
            "message": "Full-scale ingestion started in background",
            "estimated_duration_minutes": "30-60",
            "skip_halilit": skip_halilit,
            "skip_thomann": skip_thomann
        }
    except Exception as e:
        logger.error(f"Ingestion start error: {e}")
        return {"error": str(e), "status": "failed"}, 500


@app.get("/api/v2/comparison/full")
async def get_full_comparison_overview():
    """Get overview statistics of comparison database."""
    try:
        api = get_comparison_api()
        stats = api.get_database_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Overview error: {e}")
        return {"error": str(e)}, 500


@app.get("/api/v2/comparison/full/paginated")
async def get_paginated_comparisons(page: int = 1, page_size: int = 50, min_confidence: float = 0):
    """Get paginated comparison results with optional filtering."""
    try:
        api = get_comparison_api()
        results = api.get_paginated_comparisons(
            page=page, page_size=page_size, min_confidence=min_confidence)
        return {
            "status": "success",
            "page": page,
            "page_size": page_size,
            "min_confidence": min_confidence,
            "data": results
        }
    except Exception as e:
        logger.error(f"Pagination error: {e}")
        return {"error": str(e)}, 500


@app.get("/api/v2/comparison/full/brand/{brand}")
async def get_brand_comparison_full(brand: str):
    """Get comprehensive comparison for a specific brand."""
    try:
        api = get_comparison_api()
        results = api.get_brand_comparison_all(brand=brand)
        return {
            "status": "success",
            "brand": brand,
            "data": results
        }
    except Exception as e:
        logger.error(f"Brand comparison error: {e}")
        return {"error": str(e)}, 500


@app.get("/api/v2/comparison/full/export-csv")
async def export_full_comparison_csv():
    """Export all comparisons as CSV file."""
    try:
        api = get_comparison_api()
        csv_path = api.export_full_comparison_csv()
        return FileResponse(path=csv_path, media_type="text/csv", filename="comparison_full_export.csv")
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        return {"error": str(e)}, 500


@app.get("/api/v2/comparison/full/database-stats")
async def get_database_statistics():
    """Get raw database statistics."""
    try:
        api = get_comparison_api()
        stats = api.get_database_stats()
        return stats
    except Exception as e:
        logger.error(f"Database stats error: {e}")
        return {"error": str(e)}, 500


# ========== FRONTEND ROUTING ==========
>>>>>>> Stashed changes

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


@app.post("/api/telemetry/crash-report", status_code=200, tags=["telemetry"])
async def crash_report(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Sovereign Nerve — receives frontend crash reports (uncaught JS errors / unhandled rejections).

    The payload shape matches what Sovereign Nerve (frontend/src/telemetry.ts) sends:
      { event: {title}, stacktrace, culprit, timestamp, environment, userAgent }
    This is forwarded to process_production_error() in the same way as the Sentry webhook.
    Returns 200 immediately so the browser keepalive request is resolved fast.
    """
    try:
        payload = await request.json()
    except Exception:
        payload = {"message": "(unparseable payload)", "event": {}}

    # Skip agent processing for validation / CI probes to avoid false alarms.
    env = payload.get("environment") or (
        payload.get("event") or {}).get("environment") or ""
    if env in ("test", "validation", "ci"):
        return {"status": "received", "message": "Test probe acknowledged — Sovereign Nerve not triggered."}

    try:
        from backend.factory.telemetry_agent import process_production_error  # type: ignore
        background_tasks.add_task(process_production_error, payload)
    except Exception as exc:
        logger.error("Telemetry Agent import failed: %s", exc)

    return {"status": "received", "message": "Sovereign Nerve ingestor activated."}


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
