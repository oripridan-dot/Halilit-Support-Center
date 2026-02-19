"""MCP lifecycle hooks — init and shutdown for FastAPI lifespan."""

from __future__ import annotations

import logging

from backend.mcp.registry import MCPRegistry, get_registry

logger = logging.getLogger("mcp.startup")


async def init_mcp() -> None:
    """Initialize MCP registry and discover tools from enabled servers."""
    registry = get_registry()
    enabled = [s for s in registry.servers.values() if s.enabled]
    if not enabled:
        logger.info("MCP: no enabled servers configured, skipping discovery")
        return
    try:
        tools = await registry.discover_tools()
        logger.info("MCP: discovered %d tools across %d servers", len(tools), len(enabled))
    except Exception as exc:
        logger.warning("MCP: tool discovery failed: %s", exc)


async def shutdown_mcp() -> None:
    """Cleanly close MCP connections."""
    registry = get_registry()
    try:
        await registry.close()
        logger.info("MCP: connections closed")
    except Exception as exc:
        logger.warning("MCP: error during shutdown: %s", exc)


__all__ = ["init_mcp", "shutdown_mcp", "get_registry"]
