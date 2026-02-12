"""MCP server registry — discovers, registers, and manages MCP servers.

Loads config from environment or mcp_config.json.
Provides tool routing: given a tool name, find which server owns it.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from backend.mcp.client import MCPClient
from backend.mcp.schemas import MCPServerConfig, MCPTool, MCPTransport

logger = logging.getLogger("mcp.registry")

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "mcp_servers.json"


class MCPRegistry:
    """Central registry for all MCP servers and their tools."""

    def __init__(self) -> None:
        self.servers: dict[str, MCPServerConfig] = {}
        self.tools: dict[str, MCPTool] = {}  # tool_name → MCPTool
        self.client = MCPClient()
        self._initialized = False

    def load_config(self, config_path: str | Path | None = None) -> None:
        """Load server configs from JSON file or environment."""
        path = Path(config_path) if config_path else _CONFIG_PATH

        if path.exists():
            with open(path) as f:
                data = json.load(f)
            for entry in data.get("servers", []):
                config = MCPServerConfig.model_validate(entry)
                self.servers[config.name] = config
            logger.info("Loaded %d MCP servers from %s",
                        len(self.servers), path)
        else:
            logger.info(
                "No MCP config at %s — loading from environment only", path)

        # Environment override: MCP_SERVERS=name1:url1,name2:url2
        env_servers = os.getenv("MCP_SERVERS", "")
        if env_servers:
            for pair in env_servers.split(","):
                pair = pair.strip()
                if not pair:
                    continue
                parts = pair.split(":", 1)
                if len(parts) == 2:
                    name, url = parts[0].strip(), parts[1].strip()
                    self.servers[name] = MCPServerConfig(
                        name=name,
                        transport=MCPTransport.SSE,
                        url=url,
                    )

    async def discover_tools(self) -> dict[str, MCPTool]:
        """Query all enabled servers for their available tools."""
        self.tools.clear()

        for name, server in self.servers.items():
            if not server.enabled:
                continue
            try:
                raw_tools = await self.client.list_tools(server)
                for t in raw_tools:
                    tool = MCPTool(
                        name=t.get("name", ""),
                        description=t.get("description", ""),
                        server_name=name,
                    )
                    self.tools[tool.name] = tool
                logger.info(
                    "Discovered %d tools from server '%s'", len(
                        raw_tools), name
                )
            except Exception as exc:
                logger.warning("Tool discovery failed for '%s': %s", name, exc)

        self._initialized = True
        return self.tools

    def get_tool_server(self, tool_name: str) -> MCPServerConfig | None:
        """Find which server owns a given tool."""
        tool = self.tools.get(tool_name)
        if not tool:
            return None
        return self.servers.get(tool.server_name)

    def get_server(self, server_name: str) -> MCPServerConfig | None:
        return self.servers.get(server_name)

    async def health(self) -> dict[str, bool]:
        """Check all servers health."""
        results = {}
        for name, server in self.servers.items():
            results[name] = await self.client.health_check(server)
        return results

    def list_available_tools(self) -> list[dict[str, Any]]:
        """Return tool manifest for agent prompt injection."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "server": t.server_name,
            }
            for t in self.tools.values()
        ]

    async def close(self) -> None:
        await self.client.close()


# Module-level singleton
_registry: MCPRegistry | None = None


def get_registry() -> MCPRegistry:
    """Get or create the global MCP registry singleton."""
    global _registry
    if _registry is None:
        _registry = MCPRegistry()
        _registry.load_config()
    return _registry
