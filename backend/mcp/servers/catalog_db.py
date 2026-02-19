"""MCP Server: Catalog DB — exposes product catalog queries via MCP protocol.

Run standalone:
    PYTHONPATH=. python3 backend/mcp/servers/catalog_db.py

Listens on http://localhost:8102/mcp (SSE transport).
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

logger = logging.getLogger("mcp.server.catalog_db")


@asynccontextmanager
async def _lifespan(app: FastAPI):
    _load_catalog()
    yield


app = FastAPI(title="Halilit Catalog DB MCP Server", lifespan=_lifespan)

# Load catalog data at startup
_catalog: list[dict[str, Any]] = []
_DATA_DIR = Path(__file__).parent.parent.parent / "data"
_FRONTEND_DATA_DIR = Path(
    __file__).parent.parent.parent.parent / "frontend" / "public" / "data"


def _load_catalog() -> list[dict[str, Any]]:
    """Load catalog from frontend golden list or backend data."""
    global _catalog
    _catalog = []

    # Primary: load from frontend golden list JSON files
    if _FRONTEND_DATA_DIR.exists():
        for json_file in sorted(_FRONTEND_DATA_DIR.glob("*.json")):
            if json_file.stem in ("index", "search_index", "search_index_min"):
                continue
            try:
                with open(json_file) as f:
                    data = json.load(f)
                if isinstance(data, list):
                    _catalog.extend(data)
                elif isinstance(data, dict) and "products" in data:
                    _catalog.extend(data["products"])
            except Exception as exc:
                logger.warning("Failed to load %s: %s", json_file, exc)

    # Fallback: backend enriched catalog
    if not _catalog:
        catalog_path = _DATA_DIR / "enriched_catalog.json"
        if catalog_path.exists():
            with open(catalog_path) as f:
                _catalog = json.load(f)

    # Fallback: backend brand shards
    if not _catalog:
        brands_dir = _DATA_DIR / "brands"
        if brands_dir.exists():
            for shard in brands_dir.glob("*.json"):
                try:
                    with open(shard) as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        _catalog.extend(data)
                    elif isinstance(data, dict) and "products" in data:
                        _catalog.extend(data["products"])
                except Exception:
                    pass

    logger.info("Loaded %d products into catalog", len(_catalog))
    return _catalog


# --- MCP Tool Implementations ---


def _tool_search_products(arguments: dict[str, Any]) -> Any:
    """Search products by name, category, or brand."""
    query = arguments.get("query", "").lower()
    limit = min(arguments.get("limit", 10), 50)

    if not query:
        return {"products": [], "total": 0}

    results = []
    for product in _catalog:
        name = str(product.get("name", "")).lower()
        brand = str(product.get("brand", "")).lower()
        category = str(product.get("category", "")).lower()
        description = str(product.get("description", "")).lower()

        if query in name or query in brand or query in category or query in description:
            results.append({
                "name": product.get("name"),
                "brand": product.get("brand"),
                "category": product.get("category"),
                "sku": product.get("sku"),
                "description": str(product.get("description", ""))[:200],
            })
            if len(results) >= limit:
                break

    return {"products": results, "total": len(results)}


def _tool_get_product(arguments: dict[str, Any]) -> Any:
    """Get full product details by SKU or name."""
    sku = arguments.get("sku", "")
    name = arguments.get("name", "").lower()

    for product in _catalog:
        if sku and product.get("sku") == sku:
            return {"product": product, "found": True}
        if name and name in str(product.get("name", "")).lower():
            return {"product": product, "found": True}

    return {"product": None, "found": False}


def _tool_list_brands(arguments: dict[str, Any]) -> Any:
    """List all brands in the catalog."""
    brands: dict[str, int] = {}
    for product in _catalog:
        brand = product.get("brand", "Unknown")
        brands[brand] = brands.get(brand, 0) + 1
    return {
        "brands": [
            {"name": b, "product_count": c}
            for b, c in sorted(brands.items())
        ]
    }


def _tool_list_categories(arguments: dict[str, Any]) -> Any:
    """List all categories in the catalog."""
    categories: dict[str, int] = {}
    for product in _catalog:
        cat = product.get("category", "Uncategorized")
        categories[cat] = categories.get(cat, 0) + 1
    return {
        "categories": [
            {"name": c, "product_count": n}
            for c, n in sorted(categories.items())
        ]
    }


def _tool_catalog_stats(arguments: dict[str, Any]) -> Any:
    """Get catalog statistics."""
    brands = set()
    categories = set()
    with_images = 0
    with_descriptions = 0
    for product in _catalog:
        brands.add(product.get("brand", ""))
        categories.add(product.get("category", ""))
        if product.get("images") or product.get("hero_image"):
            with_images += 1
        if product.get("description"):
            with_descriptions += 1

    return {
        "total_products": len(_catalog),
        "total_brands": len(brands),
        "total_categories": len(categories),
        "with_images": with_images,
        "with_descriptions": with_descriptions,
    }


# --- MCP Tool Registry ---

TOOLS = {
    "search_products": {
        "name": "search_products",
        "description": "Search the Halilit product catalog by name, brand, category, or keyword",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 10, max 50)",
                },
            },
            "required": ["query"],
        },
        "handler": _tool_search_products,
    },
    "get_product": {
        "name": "get_product",
        "description": "Get full product details by SKU or name",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sku": {"type": "string", "description": "Product SKU"},
                "name": {
                    "type": "string",
                    "description": "Product name (partial match)",
                },
            },
        },
        "handler": _tool_get_product,
    },
    "list_brands": {
        "name": "list_brands",
        "description": "List all brands and their product counts",
        "inputSchema": {"type": "object", "properties": {}},
        "handler": _tool_list_brands,
    },
    "list_categories": {
        "name": "list_categories",
        "description": "List all product categories and counts",
        "inputSchema": {"type": "object", "properties": {}},
        "handler": _tool_list_categories,
    },
    "catalog_stats": {
        "name": "catalog_stats",
        "description": "Get overall catalog statistics (products, brands, categories, coverage)",
        "inputSchema": {"type": "object", "properties": {}},
        "handler": _tool_catalog_stats,
    },
}


# --- MCP JSON-RPC Handler ---


@app.post("/mcp")
async def mcp_endpoint(request: Request) -> JSONResponse:
    """Handle MCP JSON-RPC 2.0 requests."""
    body = await request.json()
    method = body.get("method", "")
    req_id = body.get("id", 0)
    params = body.get("params", {})

    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "halilit-catalog-db",
                    "version": "1.0.0",
                },
                "capabilities": {
                    "tools": {"listChanged": False},
                },
            },
        })

    if method == "tools/list":
        tool_list = [
            {
                "name": t["name"],
                "description": t["description"],
                "inputSchema": t["inputSchema"],
            }
            for t in TOOLS.values()
        ]
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": tool_list},
        })

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        tool = TOOLS.get(tool_name)
        if not tool:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Tool '{tool_name}' not found",
                },
            })

        try:
            result = tool["handler"](arguments)
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result,
            })
        except Exception as exc:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32000,
                    "message": str(exc),
                },
            })

    return JSONResponse({
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": -32601,
            "message": f"Method '{method}' not supported",
        },
    })



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = int(os.getenv("MCP_CATALOG_PORT", "8102"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
