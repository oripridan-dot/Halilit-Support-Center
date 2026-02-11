"""MCP Tool Skill — allows Trinity Swarm agents to call MCP server tools.

This skill is registered like any other skill. Agents request tool calls
via the standard skill interface. The skill routes to the appropriate
MCP server, executes the call, and returns normalized results.

Usage by agents:
    skill: mcp_tool
    params:
        tool: "web_search"
        arguments: {"query": "Halilit baby maracas specs"}

Compatible with both async (FastAPI) and sync (Celery) contexts.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Tuple

from backend.mcp.registry import get_registry
from backend.mcp.schemas import MCPToolCallResult
from backend.skills.base_skill import BaseSkill

logger = logging.getLogger("skills.mcp_tool")


class MCPToolSkill(BaseSkill):
    """Skill that bridges Trinity Swarm agents to MCP servers.

    Integrates with the existing SkillRegistry — agents call it
    like any other skill, no MCP awareness needed.
    """

    def __init__(self, orchestrator=None):
        super().__init__()
        self.orchestrator = orchestrator

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """Execute an MCP tool call synchronously (for SkillRegistry compat).

        Args:
            context: Must contain:
                - tool (str): Name of the MCP tool to call
                - arguments (dict, optional): Arguments to pass to the tool
                - server (str, optional): Direct server routing

        Returns:
            Tuple of (success, result_dict)
        """
        valid, error = self.validate_context(context, ["tool"])
        if not valid:
            return False, error

        # Run async call in a new event loop (safe for Celery workers)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # We're inside an async context (FastAPI) — create a task
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(self._run_sync, context)
                result = future.result(timeout=30)
        else:
            result = self._run_sync(context)

        success = result.get("success", False)
        self.log_execution(success, "MCP Tool Call", f"{context.get('tool')}")
        return success, result

    def _run_sync(self, context: Dict[str, Any]) -> dict[str, Any]:
        """Run the async MCP call in a fresh event loop."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self._execute_async(context))
        finally:
            loop.close()

    async def _execute_async(self, context: Dict[str, Any]) -> dict[str, Any]:
        """Async implementation of the MCP tool call."""
        tool_name = context.get("tool", "")
        arguments = context.get("arguments", {})
        registry = get_registry()

        # Find which server owns this tool
        server = registry.get_tool_server(tool_name)
        if not server:
            # Fallback: try server_name param for direct routing
            server_name = context.get("server")
            if server_name:
                server = registry.get_server(server_name)

        if not server:
            available = [t["name"] for t in registry.list_available_tools()]
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found. Available: {available[:10]}",
                "data": None,
            }

        if not server.enabled:
            return {
                "success": False,
                "error": f"Server '{server.name}' is disabled",
                "data": None,
            }

        # Execute the MCP call
        result: MCPToolCallResult = await registry.client.call_tool(
            server=server,
            tool_name=tool_name,
            arguments=arguments,
        )

        logger.info(
            "MCP tool call: %s on %s → %s (%.1fms)",
            tool_name,
            server.name,
            "OK" if result.success else "FAIL",
            result.latency_ms,
        )

        return {
            "success": result.success,
            "data": result.data,
            "error": result.error,
            "tool": result.tool_name,
            "server": result.server_name,
            "latency_ms": result.latency_ms,
        }


async def list_tools() -> list[dict[str, Any]]:
    """Return all available MCP tools (for agent prompt injection)."""
    registry = get_registry()
    if not registry.tools:
        await registry.discover_tools()
    return registry.list_available_tools()


# Skill metadata (used by skill registry auto-discovery)
SKILL_META = {
    "name": "mcp_tool",
    "description": "Call external tools via MCP (Model Context Protocol) servers",
    "version": "1.0.0",
    "params_schema": {
        "tool": {"type": "string", "required": True},
        "arguments": {"type": "object", "required": False},
        "server": {"type": "string", "required": False},
    },
}
