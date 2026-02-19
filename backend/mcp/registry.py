"""MCP server registry — tracks configured servers and discovered tools."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from backend.mcp.client import MCPClient
from backend.mcp.schemas import MCPServerConfig, MCPTool, MCPTransport

logger = logging.getLogger("mcp.registry")

_registry: MCPRegistry | None = None


class MCPRegistry:
    """Registry of MCP servers and their discovered tools."""

    def __init__(self) -> None:
        self.servers: dict[str, MCPServerConfig] = {}
        self.tools: dict[str, MCPTool] = {}
        self._initialized: bool = False
        self._client = MCPClient()

    def load_config(self, config_path: str | Path) -> None:
        """Load server configs from a JSON file and/or MCP_SERVERS env var."""
        path = Path(config_path)
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                for srv in data.get("servers", []):
                    config = MCPServerConfig(**srv)
                    self.servers[config.name] = config
                logger.info("Loaded %d servers from %s", len(self.servers), path)
            except Exception as exc:
                logger.warning("Failed to load MCP config from %s: %s", path, exc)

        # Override / supplement with MCP_SERVERS env var (format: name:url,name2:url2)
        env_servers = os.environ.get("MCP_SERVERS", "")
        if env_servers:
            for entry in env_servers.split(","):
                entry = entry.strip()
                if ":" in entry:
                    name, _, url = entry.partition(":")
                    name = name.strip()
                    url = url.strip()
                    if name and url:
                        self.servers[name] = MCPServerConfig(
                            name=name,
                            transport=MCPTransport.SSE,
                            url=url,
                        )
                        logger.info("Loaded server '%s' from MCP_SERVERS env", name)

    def get_server(self, name: str) -> MCPServerConfig | None:
        return self.servers.get(name)

    def get_tool_server(self, tool_name: str) -> MCPServerConfig | None:
        tool = self.tools.get(tool_name)
        if tool is None:
            return None
        return self.servers.get(tool.server_name)

    def list_available_tools(self) -> list[dict[str, Any]]:
        return [
            {"name": t.name, "description": t.description, "server": t.server_name}
            for t in self.tools.values()
        ]

    async def discover_tools(self) -> dict[str, MCPTool]:
        """Discover tools from all enabled servers."""
        for server in self.servers.values():
            if not server.enabled:
                continue
            try:
                raw_tools = await self._client.list_tools(server)
                for rt in raw_tools:
                    tool = MCPTool(
                        name=rt.get("name", ""),
                        description=rt.get("description", ""),
                        server_name=server.name,
                        input_schema=rt.get("inputSchema", {}),
                    )
                    self.tools[tool.name] = tool
            except Exception as exc:
                logger.warning("Tool discovery failed for server '%s': %s", server.name, exc)
        self._initialized = True
        return self.tools

    async def health(self) -> dict[str, Any]:
        """Check connectivity to all enabled servers."""
        results: dict[str, Any] = {}
        for name, server in self.servers.items():
            if not server.enabled:
                results[name] = {"healthy": False, "reason": "disabled"}
                continue
            try:
                ok = await self._client.health_check(server)
                results[name] = {"healthy": ok}
            except Exception as exc:
                results[name] = {"healthy": False, "reason": str(exc)}
        return results

    async def close(self) -> None:
        await self._client.close()


def get_registry() -> MCPRegistry:
    """Return the global MCPRegistry singleton, creating it if needed."""
    global _registry
    if _registry is None:
        _registry = MCPRegistry()
        # Auto-load from default config path
        default_config = Path(__file__).parent.parent / "config" / "mcp_servers.json"
        _registry.load_config(default_config)
    return _registry
