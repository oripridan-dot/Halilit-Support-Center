"""MCP startup hooks — integrate with FastAPI lifecycle.

Call init_mcp() in server.py startup event.
Call shutdown_mcp() in server.py shutdown event.
"""

from __future__ import annotations

import logging

from backend.mcp.registry import get_registry

logger = logging.getLogger("mcp.startup")


async def init_mcp() -> None:
    """Initialize MCP registry and discover tools (non-blocking).

    Safe to call even if no MCP servers are configured — will simply
    log that no servers are available and continue.
    """
    registry = get_registry()

    if not registry.servers:
        logger.info("No MCP servers configured — MCP features inactive")
        return

    enabled = [s for s in registry.servers.values() if s.enabled]
    if not enabled:
        logger.info(
            "MCP: %d servers configured but none enabled", len(
                registry.servers)
        )
        return

    logger.info(
        "MCP: Discovering tools from %d enabled servers...", len(enabled))
    try:
        tools = await registry.discover_tools()
        logger.info(
            "MCP: Ready — %d tools available across %d servers",
            len(tools),
            len(enabled),
        )
    except Exception as exc:
        logger.warning("MCP: Tool discovery failed (non-fatal): %s", exc)


async def shutdown_mcp() -> None:
    """Clean up MCP resources."""
    registry = get_registry()
    await registry.close()
    logger.info("MCP: Shutdown complete")
