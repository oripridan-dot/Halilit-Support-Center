"""
Halilit Support Center — Lean FastAPI Server (JIT Architecture v9)

Endpoints:
  GET  /api/health                         — Health check
  GET  /api/conductor/catalog              — Lightweight inventory catalog
  GET  /api/conductor/taxonomy             — Category hierarchy
  GET  /api/conductor/categories           — Category stats
  POST /api/conductor/filter               — Filter products
  GET  /api/conductor/refresh              — Force catalog rebuild
  GET  /api/product/{id}/intelligence      — JIT product enrichment
  GET  /api/product/{id}/compare/{other}   — JIT product comparison
  POST /api/sync/inventory                 — Trigger skeleton sync
  GET  /api/catalog/health                 — Catalog quality metrics
  GET  /api/search                         — Text search
  +    /api/spectrum/*                     — Spectrum model grouping
  +    /api/curation/*                     — Product graph curation
"""

import json
import gzip
import time
import logging
import asyncio
import threading
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.product_normalizer import build_catalog, GALAXIES

# ── Logging ──
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Paths ──
BASE_DIR = Path(__file__).parent
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"
FRONTEND_PUBLIC_DATA = BASE_DIR.parent / "frontend" / "public" / "data"

# ── Server-side catalog cache ──
_catalog_cache_json: bytes | None = None
_catalog_cache_gzip: bytes | None = None
_catalog_cache_dict: dict | None = None
_catalog_cache_time: float = 0
_catalog_build_lock = threading.Lock()
CATALOG_CACHE_TTL = 300  # 5 minutes

# Fields to strip from catalog response (never rendered by frontend)
STRIP_FIELDS = {"contextual_data", "search_text", "subcategory", "currency"}

# ── App ──
app = FastAPI(title="Halilit Support Center", version="9.0-jit")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Sub-routers ──
try:
    from backend.api.spectrum_router import router as spectrum_router
    app.include_router(spectrum_router, tags=["Spectrum"])
    logger.info("✅ Spectrum endpoints registered")
except Exception as e:
    logger.warning(f"⚠️ Spectrum router: {e}")

try:
    from backend.api.curation_router import router as curation_router
    app.include_router(curation_router, tags=["Product Graph Curation"])
    logger.info("✅ Curation endpoints registered")
except Exception as e:
    logger.warning(f"⚠️ Curation router: {e}")

try:
    from backend.api.jit_router import router as jit_router
    app.include_router(jit_router, tags=["JIT Intelligence"])
    logger.info("✅ JIT Intelligence endpoints registered")
except Exception as e:
    logger.warning(f"⚠️ JIT router: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# CATALOG CACHE
# ═══════════════════════════════════════════════════════════════════════════

def _build_catalog_cache():
    """Build catalog and cache pre-serialized JSON + gzip. Thread-safe."""
    global _catalog_cache_json, _catalog_cache_gzip, _catalog_cache_dict, _catalog_cache_time
    with _catalog_build_lock:
        if _catalog_cache_json is not None and (time.time() - _catalog_cache_time) < CATALOG_CACHE_TTL:
            return
        t0 = time.time()
        catalog = build_catalog(str(FRONTEND_PUBLIC_DATA))
        _catalog_cache_dict = catalog

        for p in catalog["products"]:
            for field in STRIP_FIELDS:
                p.pop(field, None)

        catalog["metadata"]["timestamp"] = datetime.now().isoformat()

        json_bytes = json.dumps(catalog, ensure_ascii=False).encode("utf-8")
        gzip_bytes = gzip.compress(json_bytes, compresslevel=6)

        _catalog_cache_json = json_bytes
        _catalog_cache_gzip = gzip_bytes
        _catalog_cache_time = time.time()
        ms = int((time.time() - t0) * 1000)

        meta = catalog["metadata"]
        logger.info(
            f"✅ Catalog: {meta['total_products']} products, "
            f"{len(meta['brands'])} brands, "
            f"health: {meta.get('health_score', '?')}/100 "
            f"({ms}ms, {len(json_bytes)//1024}KB → {len(gzip_bytes)//1024}KB gzip)"
        )


def _startup_catalog_build():
    try:
        _build_catalog_cache()
    except Exception as e:
        logger.error(f"Startup catalog build failed: {e}")


_startup_thread = threading.Thread(target=_startup_catalog_build, daemon=True)
_startup_thread.start()


def _get_catalog() -> dict:
    """Get cached catalog dict, rebuilding if expired."""
    global _catalog_cache_dict, _catalog_cache_time
    if _catalog_cache_dict is None or (time.time() - _catalog_cache_time) > CATALOG_CACHE_TTL:
        _build_catalog_cache()
    if _catalog_cache_dict is None:
        _startup_thread.join(timeout=60)
    return _catalog_cache_dict or {"products": [], "metadata": {}, "indexes": {}}


# ═══════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "9.0-jit", "service": "Halilit Support Center"}


@app.get("/api/conductor/catalog")
async def get_conductor_catalog(request: Request):
    """Primary data endpoint — pre-indexed inventory catalog with gzip support."""
    global _catalog_cache_json, _catalog_cache_gzip, _catalog_cache_time
    try:
        if _catalog_cache_json is None or (time.time() - _catalog_cache_time) > CATALOG_CACHE_TTL:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _build_catalog_cache)

        if _catalog_cache_json is None:
            _startup_thread.join(timeout=60)

        if _catalog_cache_json is None:
            return JSONResponse(status_code=503, content={"error": "Catalog still building"})

        accept = request.headers.get("accept-encoding", "")
        if "gzip" in accept and _catalog_cache_gzip:
            return Response(content=_catalog_cache_gzip, media_type="application/json",
                            headers={"Content-Encoding": "gzip"})

        return Response(content=_catalog_cache_json, media_type="application/json")
    except Exception as e:
        logger.error(f"Catalog error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/conductor/taxonomy")
async def get_taxonomy():
    """Category hierarchy from GALAXIES taxonomy."""
    catalog = _get_catalog()
    brands = sorted(catalog.get("metadata", {}).get("brands", []))

    categories = []
    for galaxy in GALAXIES:
        categories.append({
            "id": galaxy["id"],
            "name": galaxy["label"],
            "subcategories": [{"id": s["id"], "name": s["label"]} for s in galaxy.get("spectrums", [])],
        })

    return {
        "universal_categories": categories,
        "all_brands": brands,
        "pricing_tiers": ["entry", "mid", "pro", "flagship", "legacy"],
        "total_products": len(catalog.get("products", [])),
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/conductor/filter")
async def filter_products(filters: dict):
    """Filter products by brand, category, price range, tier, search query."""
    catalog = _get_catalog()
    products = catalog.get("products", [])
    applied = {}

    if "brand" in filters:
        vals = [filters["brand"]] if isinstance(
            filters["brand"], str) else filters["brand"]
        lower = [v.lower() for v in vals]
        products = [p for p in products if p.get("brand", "").lower() in lower]
        applied["brand"] = filters["brand"]

    if "category" in filters:
        vals = [filters["category"]] if isinstance(
            filters["category"], str) else filters["category"]
        lower = [v.lower() for v in vals]
        products = [p for p in products if p.get("galaxy_id", "").lower() in lower
                    or p.get("spectrum_id", "").lower() in lower]
        applied["category"] = filters["category"]

    if "search_query" in filters:
        q = filters["search_query"].lower()
        products = [p for p in products if q in (p.get("search_text") or
                    f"{p.get('name','')} {p.get('brand','')}").lower()]
        applied["search_query"] = filters["search_query"]

    if "pricing_tier" in filters:
        tiers = [filters["pricing_tier"]] if isinstance(
            filters["pricing_tier"], str) else filters["pricing_tier"]
        products = [p for p in products if p.get("tier") in tiers]
        applied["pricing_tier"] = filters["pricing_tier"]

    if "min_price" in filters:
        mp = float(filters["min_price"])
        products = [p for p in products if (p.get("price") or 0) >= mp]
        applied["min_price"] = mp

    if "max_price" in filters:
        mp = float(filters["max_price"])
        products = [p for p in products if 0 < (p.get("price") or 0) <= mp]
        applied["max_price"] = mp

    return {"products": products, "filters_applied": applied, "total_results": len(products)}


@app.get("/api/conductor/categories")
async def get_categories():
    """Category summary with product counts, brands, avg prices."""
    catalog = _get_catalog()
    cats: dict = {}
    for p in catalog.get("products", []):
        cat = p.get("galaxy_id") or "uncategorized"
        if cat not in cats:
            cats[cat] = {"name": cat, "count": 0,
                         "brands": set(), "prices": []}
        cats[cat]["count"] += 1
        cats[cat]["brands"].add(p.get("brand", "Unknown"))
        price = p.get("price") or 0
        if price > 0:
            cats[cat]["prices"].append(price)

    result = []
    for c in cats.values():
        prices = c["prices"]
        result.append({
            "name": c["name"],
            "product_count": c["count"],
            "brands": sorted(c["brands"]),
            "avg_price": round(sum(prices) / len(prices), 2) if prices else 0,
        })
    return {"categories": sorted(result, key=lambda x: x["product_count"], reverse=True)}


@app.get("/api/conductor/refresh")
async def refresh_catalog():
    """Force rebuild of catalog cache."""
    global _catalog_cache_json, _catalog_cache_gzip, _catalog_cache_dict, _catalog_cache_time
    _catalog_cache_json = None
    _catalog_cache_gzip = None
    _catalog_cache_dict = None
    _catalog_cache_time = 0
    _build_catalog_cache()
    meta = (_catalog_cache_dict or {}).get("metadata", {})
    return {
        "status": "refreshed",
        "product_count": meta.get("total_products", 0),
        "brands": len(meta.get("brands", [])),
        "health_score": meta.get("health_score"),
    }


@app.get("/api/catalog/health")
async def catalog_health():
    """Catalog quality metrics."""
    try:
        from backend.catalog_validator import validate_catalog
        loop = asyncio.get_event_loop()
        catalog = await loop.run_in_executor(None, build_catalog, str(FRONTEND_PUBLIC_DATA))
        return validate_catalog(catalog["products"])
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/search")
async def search_products(q: str = ""):
    """Search across catalog products."""
    if not q or len(q) < 2:
        return {"query": q, "results": [], "total_results": 0}

    catalog = _get_catalog()
    q_lower = q.lower()
    results = []
    for p in catalog.get("products", []):
        text = (p.get("search_text")
                or f"{p.get('name','')} {p.get('brand','')} {p.get('description','')}").lower()
        if q_lower in text:
            results.append(p)
            if len(results) >= 50:
                break

    return {"query": q, "total_results": len(results), "results": results}


# ═══════════════════════════════════════════════════════════════════════════
# JIT INTELLIGENCE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/product/{product_id}/intelligence")
async def get_product_intelligence(product_id: str):
    """
    JIT product enrichment — fetches live data from brand sites,
    trusted review sources, and returns a fully enriched product.
    Cached for 7 days server-side.
    """
    try:
        from backend.jit_cache import get_cached_intelligence, cache_intelligence
        from backend.jit_agent import ProductSynthesizer

        # Check cache first
        cached = get_cached_intelligence(product_id)
        if cached:
            return cached

        # Find product in catalog
        catalog = _get_catalog()
        product = None
        for p in catalog.get("products", []):
            if p.get("id") == product_id:
                product = p
                break

        if not product:
            return JSONResponse(status_code=404, content={"error": f"Product '{product_id}' not found"})

        # Run JIT synthesis
        synthesizer = ProductSynthesizer()
        enriched = await synthesizer.synthesize(product)

        # Cache result
        cache_intelligence(product_id, enriched)

        return enriched

    except ImportError:
        return JSONResponse(status_code=501, content={"error": "JIT agent not yet configured"})
    except Exception as e:
        logger.error(f"JIT intelligence error for {product_id}: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/product/{product_id}/compare/{other_id}")
async def compare_products(product_id: str, other_id: str):
    """JIT comparison of two products — specs, pricing, reviews side by side."""
    try:
        from backend.jit_agent import ProductSynthesizer

        catalog = _get_catalog()
        products_map = {p["id"]: p for p in catalog.get("products", [])}

        if product_id not in products_map:
            return JSONResponse(status_code=404, content={"error": f"Product '{product_id}' not found"})
        if other_id not in products_map:
            return JSONResponse(status_code=404, content={"error": f"Product '{other_id}' not found"})

        synthesizer = ProductSynthesizer()
        comparison = await synthesizer.compare(products_map[product_id], products_map[other_id])
        return comparison

    except ImportError:
        return JSONResponse(status_code=501, content={"error": "JIT agent not yet configured"})
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/sync/inventory")
async def sync_inventory():
    """Trigger skeleton inventory sync from Halilit.com."""
    try:
        from backend.skeleton_sync import run_skeleton_sync
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_skeleton_sync)

        # Refresh catalog cache after sync
        global _catalog_cache_json, _catalog_cache_gzip, _catalog_cache_dict, _catalog_cache_time
        _catalog_cache_json = None
        _catalog_cache_gzip = None
        _catalog_cache_dict = None
        _catalog_cache_time = 0

        return {"status": "synced", **result}
    except ImportError:
        return JSONResponse(status_code=501, content={"error": "Skeleton sync not yet configured"})
    except Exception as e:
        logger.error(f"Inventory sync error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ═══════════════════════════════════════════════════════════════════════════
# FRONTEND ROUTING (SPA)
# ═══════════════════════════════════════════════════════════════════════════

if FRONTEND_DIST.exists():
    app.mount(
        "/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    if FRONTEND_PUBLIC_DATA.exists():
        app.mount(
            "/data", StaticFiles(directory=str(FRONTEND_PUBLIC_DATA)), name="data")

    @app.get("/{catchall:path}")
    async def serve_spa(catchall: str):
        file_path = FRONTEND_DIST / catchall
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    logger.warning(f"Frontend build not found at {FRONTEND_DIST}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
