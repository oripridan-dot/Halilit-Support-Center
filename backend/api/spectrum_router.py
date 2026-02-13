"""
Spectrum API Router — serves model-grouped, family-classified product data
for the redesigned Spectrum view's track/subtrack system.

Endpoints:
  GET /api/spectrum/families  — instrument family tree for sidebar navigation
  GET /api/spectrum/models    — model groups at configurable zoom levels
"""

import logging
import time
from collections import Counter, defaultdict
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from backend.model_grouper import (
    get_family_tree,
    group_products_by_model,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/spectrum", tags=["Spectrum"])

# ── In-memory cache for model groups (expensive to compute) ──
_model_groups_cache: list[dict] | None = None
_model_groups_cache_time: float = 0
_MODEL_GROUPS_CACHE_TTL = 300  # 5 minutes, matches catalog cache


def _get_catalog_products() -> list[dict]:
    """
    Get the current catalog products from the pre-built cache.
    Uses the same data source as /api/conductor/catalog.
    """
    from backend.product_normalizer import build_catalog
    import os

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "../../frontend/public/data")

    catalog = build_catalog(data_dir)
    return catalog.get("products", [])


def _get_model_groups() -> list[dict]:
    """Get model groups with caching. Rebuilds when TTL expires."""
    global _model_groups_cache, _model_groups_cache_time

    now = time.time()
    if _model_groups_cache is not None and (now - _model_groups_cache_time) < _MODEL_GROUPS_CACHE_TTL:
        return _model_groups_cache

    products = _get_catalog_products()
    _model_groups_cache = group_products_by_model(products)
    _model_groups_cache_time = time.time()
    logger.info(f"Spectrum cache rebuilt: {len(_model_groups_cache)} model groups from {len(products)} products in {int((time.time() - now) * 1000)}ms")
    return _model_groups_cache


@router.get("/families")
async def get_instrument_families():
    """
    Returns the domain-driven instrument family tree for sidebar navigation.
    This is a static structure that rarely changes.
    """
    return {"families": get_family_tree()}


@router.get("/models")
async def get_model_groups(
    family: Optional[str] = Query(
        None, description="Filter by instrument family slug"),
    sub_category: Optional[str] = Query(
        None, description="Filter by sub-category slug"),
    body_type: Optional[str] = Query(
        None, description="Filter by body type slug"),
    brand: Optional[str] = Query(None, description="Filter by brand name"),
    zoom: str = Query(
        "cluster", description="Zoom level: galaxy|constellation|cluster|star"),
    min_price: Optional[float] = Query(
        None, description="Minimum price filter"),
    max_price: Optional[float] = Query(
        None, description="Maximum price filter"),
    tier: Optional[str] = Query(
        None, description="Filter by tier: entry|mid|pro|flagship"),
    search: Optional[str] = Query(
        None, description="Search within model names"),
):
    """
    Returns products grouped by model, filtered and shaped by zoom level.

    Zoom levels control response granularity:
    - galaxy: just family counts and summaries
    - constellation: brands within family with model counts
    - cluster: model groups with variation counts (default)
    - star: model groups with full variation details
    """
    try:
        t0 = time.time()
        groups = list(_get_model_groups())  # shallow copy for filtering

        # ── Apply filters ──
        if family:
            groups = [g for g in groups if g["family"] == family]
        if sub_category:
            groups = [g for g in groups if g["subCategory"] == sub_category]
        if body_type:
            groups = [g for g in groups if g["bodyType"] == body_type]
        if brand:
            groups = [g for g in groups if g["brand"].lower() == brand.lower()]
        if tier:
            groups = [
                g for g in groups
                if any(v["tier"] == tier for v in g["variations"])
            ]
        if min_price is not None:
            groups = [g for g in groups if g["priceRange"]["max"] >= min_price]
        if max_price is not None:
            groups = [g for g in groups if g["priceRange"]["min"]
                      <= max_price or g["priceRange"]["min"] == 0]
        if search:
            search_lower = search.lower()
            groups = [g for g in groups if search_lower in g["modelName"].lower()]

        elapsed_ms = int((time.time() - t0) * 1000)

        # ── Shape response by zoom level ──
        if zoom == "galaxy":
            family_counts = Counter(g["family"] for g in groups)
            family_data = []
            for f, count in sorted(family_counts.items()):
                family_groups = [g for g in groups if g["family"] == f]
                total_products = sum(g["variationCount"]
                                     for g in family_groups)
                brands_in_family = len(set(g["brand"] for g in family_groups))
                prices = [g["priceRange"]["min"]
                          for g in family_groups if g["priceRange"]["min"] > 0]
                family_data.append({
                    "family": f,
                    "label": _family_label(f),
                    "modelCount": count,
                    "productCount": total_products,
                    "brandCount": brands_in_family,
                    "priceMin": min(prices) if prices else 0,
                    "priceMax": max(g["priceRange"]["max"] for g in family_groups) if family_groups else 0,
                })

            return {
                "zoom": "galaxy",
                "families": family_data,
                "totalModels": len(groups),
                "totalProducts": sum(g["variationCount"] for g in groups),
                "elapsed_ms": elapsed_ms,
            }

        elif zoom == "constellation":
            brand_map: dict[str, dict] = defaultdict(lambda: {
                "models": 0, "products": 0,
                "priceMin": float("inf"), "priceMax": 0,
                "families": set(), "topModels": [],
            })
            for g in groups:
                b = brand_map[g["brand"]]
                b["models"] += 1
                b["products"] += g["variationCount"]
                if g["priceRange"]["min"] > 0:
                    b["priceMin"] = min(b["priceMin"], g["priceRange"]["min"])
                b["priceMax"] = max(b["priceMax"], g["priceRange"]["max"])
                b["families"].add(g["family"])
                if len(b["topModels"]) < 3:
                    b["topModels"].append({
                        "modelName": g["modelName"],
                        "heroImage": g["heroImage"],
                        "variationCount": g["variationCount"],
                    })

            brands = [
                {
                    "brand": brand_name,
                    "models": stats["models"],
                    "products": stats["products"],
                    "priceMin": stats["priceMin"] if stats["priceMin"] != float("inf") else 0,
                    "priceMax": stats["priceMax"],
                    "families": list(stats["families"]),
                    "topModels": stats["topModels"],
                }
                for brand_name, stats in sorted(brand_map.items())
            ]

            return {
                "zoom": "constellation",
                "brands": brands,
                "totalModels": len(groups),
                "totalProducts": sum(g["variationCount"] for g in groups),
                "elapsed_ms": elapsed_ms,
            }

        elif zoom == "cluster":
            # Model groups without full variation details
            model_groups_slim = [
                {
                    "modelName": g["modelName"],
                    "modelKey": g["modelKey"],
                    "brand": g["brand"],
                    "family": g["family"],
                    "subCategory": g["subCategory"],
                    "bodyType": g["bodyType"],
                    "variationCount": g["variationCount"],
                    "priceRange": g["priceRange"],
                    "heroImage": g["heroImage"],
                    "avgConfidence": g["avgConfidence"],
                    # Include first variation's tier for filtering
                    "primaryTier": g["variations"][0]["tier"] if g["variations"] else "",
                }
                for g in groups
            ]

            return {
                "zoom": "cluster",
                "modelGroups": model_groups_slim,
                "totalModels": len(model_groups_slim),
                "totalProducts": sum(g["variationCount"] for g in groups),
                "elapsed_ms": elapsed_ms,
            }

        else:  # star — full detail
            return {
                "zoom": "star",
                "modelGroups": groups,
                "totalModels": len(groups),
                "totalProducts": sum(g["variationCount"] for g in groups),
                "elapsed_ms": elapsed_ms,
            }

    except Exception as e:
        logger.error(f"Error in spectrum models endpoint: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


def _family_label(family_slug: str) -> str:
    """Get human-readable label for a family slug."""
    from backend.model_grouper import INSTRUMENT_FAMILIES
    fam = INSTRUMENT_FAMILIES.get(family_slug)
    if fam:
        return fam.get("label", family_slug.replace("_", " ").title())
    return family_slug.replace("_", " ").title()
