"""
Per-brand catalog organizer: unified structure for easy search and handling.

Produces a single schema per brand: brand_identity, categories, products, search_index.
Uses OpenClaw when available (skill: organize_brand_catalog), otherwise Python fallback.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.catalog_organizer_schema import (
    build_categories_from_products,
    build_search_index,
)
from backend.project_config import FRONTEND_PUBLIC_DATA

logger = logging.getLogger("CatalogOrganizer")

OPENCLAW_URL = os.getenv("OPENCLAW_URL", "").rstrip("/")
OPENCLAW_KEY = os.getenv("OPENCLAW_KEY", "")
# Support both env var names for compatibility
OPENCLAW_ORGANIZER_PATH = os.getenv("OPENCLAW_ORGANIZER_PATH") or os.getenv("OPENCLAW_EXECUTE_PATH", "/api/execute")
OPENCLAW_ORGANIZER_TIMEOUT = float(os.getenv("OPENCLAW_ORGANIZER_TIMEOUT") or os.getenv("OPENCLAW_TIMEOUT", "120.0"))
# Cap payload size: don't send huge brands to OpenClaw in one shot (fallback for large)
ORGANIZER_MAX_PRODUCTS_OPENCLAW = int(os.getenv("ORGANIZER_MAX_PRODUCTS_OPENCLAW", "500"))


def _slug(s: str) -> str:
    if not s:
        return "unknown"
    return "".join(c if c.isalnum() or c in " -" else " " for c in s).strip().replace(" ", "-").lower().strip("-")


def _fallback_organize(brand_slug: str, brand_name: str, products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build consolidated catalog in Python (no OpenClaw)."""
    slug = _slug(brand_slug) or brand_slug.lower().replace(" ", "-")
    categories = build_categories_from_products(products)
    search_index = build_search_index(products, slug)
    now = datetime.now(timezone.utc).isoformat()
    return {
        "brand_identity": {
            "id": slug,
            "name": brand_name or slug,
            "slug": slug,
            "logo_url": None,
            "website": None,
            "description": None,
        },
        "categories": categories,
        "products": products,
        "search_index": search_index,
        "meta": {
            "total_products": len(products),
            "total_categories": len(categories),
            "organized_at": now,
            "source": "python_fallback",
        },
    }


async def _organize_via_openclaw(brand_slug: str, brand_name: str, products: List[Dict[str, Any]]) -> Dict[str, Any] | None:
    """Call OpenClaw skill organize_brand_catalog. Returns consolidated dict or None on failure."""
    if not OPENCLAW_URL or len(products) > ORGANIZER_MAX_PRODUCTS_OPENCLAW:
        return None
    try:
        import httpx
    except ImportError:
        return None
    payload = {
        "skill": "organize_brand_catalog",
        "params": {
            "brand_slug": _slug(brand_slug) or brand_slug,
            "brand_name": brand_name or brand_slug,
            "products": products[:ORGANIZER_MAX_PRODUCTS_OPENCLAW],
        },
    }
    url = f"{OPENCLAW_URL}{OPENCLAW_ORGANIZER_PATH}"
    headers: Dict[str, str] = {}
    if OPENCLAW_KEY:
        headers["Authorization"] = f"Bearer {OPENCLAW_KEY}"
        headers["X-API-Key"] = OPENCLAW_KEY
    try:
        async with httpx.AsyncClient(timeout=OPENCLAW_ORGANIZER_TIMEOUT) as client:
            resp = await client.post(url, json=payload, headers=headers or None)
            resp.raise_for_status()
            data = resp.json()
    except httpx.TimeoutException as e:
        logger.warning("OpenClaw organize_brand_catalog timeout after %ss: %s", OPENCLAW_ORGANIZER_TIMEOUT, e)
        return None
    except httpx.HTTPStatusError as e:
        logger.warning("OpenClaw organize_brand_catalog HTTP %s: %s | Response: %s", e.response.status_code, e, e.response.text[:200])
        return None
    except httpx.ConnectError as e:
        logger.warning("OpenClaw organize_brand_catalog connection failed (is container running?): %s | URL: %s", e, url)
        return None
    except Exception as e:
        logger.warning("OpenClaw organize_brand_catalog failed: %s | URL: %s", e, url)
        return None
    result = data.get("result", data)
    if isinstance(result, dict) and "products" in result and "brand_identity" in result:
        if "meta" not in result:
            result["meta"] = {
                "total_products": len(result.get("products", [])),
                "total_categories": len(result.get("categories", [])),
                "organized_at": datetime.now(timezone.utc).isoformat(),
                "source": "openclaw",
            }
        return result
    return None


def organize_brand_sync(brand_slug: str, brand_name: str, products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build consolidated catalog for one brand. Uses OpenClaw when configured and payload size OK,
    otherwise Python fallback. Synchronous wrapper for scripts.
    """
    import asyncio
    return asyncio.run(organize_brand(brand_slug, brand_name, products))


async def organize_brand(brand_slug: str, brand_name: str, products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build consolidated catalog for one brand. Prefer OpenClaw; fallback to Python.
    """
    if not products:
        return _fallback_organize(brand_slug, brand_name, [])
    consolidated = await _organize_via_openclaw(brand_slug, brand_name, products)
    if consolidated:
        logger.info("Organized %s via OpenClaw (%s products)", brand_slug, len(products))
        return consolidated
    return _fallback_organize(brand_slug, brand_name, products)


def write_consolidated_catalog(brand_slug: str, consolidated: Dict[str, Any], out_dir: Path | None = None) -> Path:
    """Write consolidated catalog to frontend data dir. Returns path written."""
    out_dir = out_dir or FRONTEND_PUBLIC_DATA
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = (consolidated.get("brand_identity") or {}).get("id") or _slug(brand_slug)
    path = out_dir / f"{slug}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(consolidated, f, indent=2, ensure_ascii=False)
    logger.info("Wrote consolidated catalog: %s (%s products)", path.name, len(consolidated.get("products", [])))
    return path


def load_brand_products(path: Path) -> tuple[str, str, list]:
    """Load products from a brand JSON file. Returns (brand_slug, brand_name, products)."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        products = data
        slug = path.stem
        name = slug.replace("-", " ").title()
        return slug, name, products
    products = data.get("products", [])
    identity = data.get("brand_identity", {})
    slug = identity.get("id") or path.stem
    name = identity.get("name") or slug.replace("-", " ").title()
    return slug, name, products
