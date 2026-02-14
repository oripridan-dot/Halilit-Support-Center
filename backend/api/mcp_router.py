"""API routes for MCP server management, monitoring, and catalog validation tools."""

from __future__ import annotations

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException

from backend.mcp.registry import get_registry
from backend.catalog_validator import validate_product, validate_catalog, resolve_catalog
from backend.product_normalizer import build_catalog

router = APIRouter(prefix="/api/mcp", tags=["MCP"])

# Data directory for catalog operations
_DATA_DIR = str(Path(__file__).parent.parent.parent /
                "frontend" / "public" / "data")


@router.get("/servers")
async def list_servers():
    """List all registered MCP servers."""
    registry = get_registry()
    return {
        "servers": [
            {
                "name": s.name,
                "transport": s.transport.value,
                "url": s.url,
                "enabled": s.enabled,
                "timeout_seconds": s.timeout_seconds,
            }
            for s in registry.servers.values()
        ]
    }


@router.get("/tools")
async def list_tools():
    """List all discovered MCP tools + built-in validation tools."""
    registry = get_registry()
    if not registry.tools:
        await registry.discover_tools()

    # External MCP tools
    external_tools = registry.list_available_tools()

    # Built-in validation tools
    builtin_tools = [
        {
            "name": "catalog_health",
            "description": "Get real-time catalog data quality metrics (health score, field coverage, top issues)",
            "server": "builtin",
        },
        {
            "name": "validate_product",
            "description": "Score a single product on UI-relevant completeness (0-100)",
            "server": "builtin",
        },
        {
            "name": "resolve_catalog",
            "description": "Auto-fix missing data across catalog using smart heuristics (price estimation, description synthesis)",
            "server": "builtin",
        },
        {
            "name": "brand_health",
            "description": "Get per-brand data quality breakdown",
            "server": "builtin",
        },
        {
            "name": "resolution_queue",
            "description": "Get products most in need of data improvement, sorted by priority",
            "server": "builtin",
        },
    ]

    return {"tools": external_tools + builtin_tools}


@router.get("/health")
async def health_check():
    """Check connectivity to all MCP servers."""
    registry = get_registry()
    results = await registry.health()
    return {"servers": results}


@router.post("/discover")
async def discover():
    """Trigger tool discovery across all enabled servers."""
    registry = get_registry()
    tools = await registry.discover_tools()
    return {"discovered": len(tools), "tools": list(tools.keys())}


@router.post("/servers/{server_name}/toggle")
async def toggle_server(server_name: str, enabled: bool = True):
    """Enable or disable an MCP server."""
    registry = get_registry()
    server = registry.get_server(server_name)
    if not server:
        raise HTTPException(404, f"Server '{server_name}' not found")
    server.enabled = enabled
    return {"name": server_name, "enabled": enabled}


# ═══════════════════════════════════════════════════════════════════════════
# BUILT-IN VALIDATION TOOLS — Exposed as MCP-style endpoints
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/tools/catalog_health")
async def tool_catalog_health():
    """
    MCP Tool: catalog_health
    Returns complete catalog health metrics including:
    - health_score (0-100)
    - status_counts (COMPLETE/GOOD/PARTIAL/MINIMAL)
    - field_coverage (% per field)
    - top_issues (sorted by impact)
    - brand_health (per-brand breakdown)
    """
    catalog = build_catalog(_DATA_DIR)
    health = validate_catalog(catalog["products"])
    return health


@router.get("/tools/brand_health")
async def tool_brand_health(brand: str = ""):
    """
    MCP Tool: brand_health
    Get per-brand quality breakdown. Optionally filter by brand name.
    """
    catalog = build_catalog(_DATA_DIR)
    health = validate_catalog(catalog["products"])

    if brand:
        brand_key = brand.lower().strip()
        if brand_key in health["brand_health"]:
            return {
                "brand": brand,
                "health": health["brand_health"][brand_key],
                "products": [
                    {
                        "id": p.get("id"),
                        "name": p.get("name"),
                        "score": validate_product(p)["score"],
                        "status": validate_product(p)["status"],
                        "missing": validate_product(p)["missing"],
                    }
                    for p in catalog["products"]
                    if (p.get("brand") or "").lower() == brand_key
                ],
            }
        raise HTTPException(404, f"Brand '{brand}' not found")

    return {"brand_health": health["brand_health"]}


@router.get("/tools/resolution_queue")
async def tool_resolution_queue(limit: int = 50):
    """
    MCP Tool: resolution_queue
    Get products most in need of improvement, sorted by worst first.
    """
    catalog = build_catalog(_DATA_DIR)
    health = validate_catalog(catalog["products"])
    return {
        "total_needing_work": health["resolution_queue_size"],
        "queue": health["resolution_queue"][:limit],
    }


@router.post("/tools/validate_product")
async def tool_validate_product(product: dict):
    """
    MCP Tool: validate_product
    Score a single product dict on UI-relevant completeness.
    """
    return validate_product(product)


@router.post("/tools/resolve_catalog")
async def tool_resolve_catalog():
    """
    MCP Tool: resolve_catalog
    Run smart resolution across the entire catalog.
    Returns before/after health scores and improvement summary.
    """
    catalog = build_catalog(_DATA_DIR, resolve=False)
    products = catalog["products"]

    health_before = validate_catalog(products)
    resolved, summary = resolve_catalog(products)
    health_after = validate_catalog(resolved)

    return {
        "health_before": health_before["health_score"],
        "health_after": health_after["health_score"],
        "improvement": health_after["health_score"] - health_before["health_score"],
        "products_improved": summary["products_improved"],
        "total_changes": summary["total_changes"],
        "status_before": health_before["status_counts"],
        "status_after": health_after["status_counts"],
    }
