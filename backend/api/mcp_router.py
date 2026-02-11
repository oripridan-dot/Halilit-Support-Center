"""API routes for MCP server management and monitoring."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.mcp.registry import get_registry

router = APIRouter(prefix="/api/mcp", tags=["MCP"])


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
    """List all discovered MCP tools across servers."""
    registry = get_registry()
    if not registry.tools:
        await registry.discover_tools()
    return {"tools": registry.list_available_tools()}


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
