"""Tests for MCP integration — schemas, registry, client, skill, servers, router.

Run with:
    PYTHONPATH=. python3 -m pytest backend/tests/test_mcp.py -v
"""

from __future__ import annotations
from backend.mcp.registry import MCPRegistry
from backend.mcp.client import MCPClient
from backend.mcp.schemas import (
    MCPError,
    MCPRequest,
    MCPResponse,
    MCPServerConfig,
    MCPTool,
    MCPToolCallResult,
    MCPTransport,
)

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


logging.basicConfig(level=logging.DEBUG)


# ═══════════════════════════ SCHEMA TESTS ═══════════════════════════


class TestMCPSchemas:
    """Test Pydantic v2 MCP message models."""

    def test_server_config_defaults(self):
        config = MCPServerConfig(name="test-server")
        assert config.name == "test-server"
        assert config.transport == MCPTransport.SSE
        assert config.enabled is True
        assert config.timeout_seconds == 10.0
        assert config.url is None
        assert config.command is None

    def test_server_config_full(self):
        config = MCPServerConfig(
            name="catalog",
            transport=MCPTransport.SSE,
            url="http://localhost:8102/mcp",
            timeout_seconds=5.0,
            enabled=False,
        )
        assert config.url == "http://localhost:8102/mcp"
        assert config.enabled is False

    def test_server_config_stdio(self):
        config = MCPServerConfig(
            name="local-tool",
            transport=MCPTransport.STDIO,
            command=["python3", "tool.py"],
        )
        assert config.transport == MCPTransport.STDIO
        assert config.command == ["python3", "tool.py"]

    def test_mcp_request(self):
        req = MCPRequest(id=1, method="tools/list")
        assert req.jsonrpc == "2.0"
        assert req.id == 1
        assert req.method == "tools/list"
        assert req.params == {}

    def test_mcp_request_with_params(self):
        req = MCPRequest(
            id=42,
            method="tools/call",
            params={"name": "search", "arguments": {"query": "test"}},
        )
        dumped = req.model_dump()
        assert dumped["params"]["name"] == "search"
        assert dumped["params"]["arguments"]["query"] == "test"

    def test_mcp_response_success(self):
        resp = MCPResponse(id=1, result={"tools": []})
        assert resp.error is None
        assert resp.result == {"tools": []}

    def test_mcp_response_error(self):
        resp = MCPResponse(
            id=1,
            error=MCPError(code=-32601, message="Method not found"),
        )
        assert resp.result is None
        assert resp.error.code == -32601

    def test_mcp_tool(self):
        tool = MCPTool(
            name="search_products",
            description="Search catalog",
            server_name="catalog-db",
        )
        assert tool.name == "search_products"
        assert tool.server_name == "catalog-db"

    def test_tool_call_result_success(self):
        result = MCPToolCallResult(
            tool_name="search",
            server_name="web-search",
            success=True,
            data={"results": [1, 2, 3]},
            latency_ms=42.5,
        )
        assert result.success is True
        assert result.latency_ms == 42.5
        assert result.error is None

    def test_tool_call_result_failure(self):
        result = MCPToolCallResult(
            tool_name="search",
            server_name="web-search",
            success=False,
            error="Connection refused",
            latency_ms=150.0,
        )
        assert result.success is False
        assert "Connection refused" in result.error


# ═══════════════════════════ REGISTRY TESTS ═══════════════════════════


class TestMCPRegistry:
    """Test the MCP server registry."""

    def test_empty_registry(self):
        registry = MCPRegistry()
        assert len(registry.servers) == 0
        assert len(registry.tools) == 0
        assert registry._initialized is False

    def test_load_config_from_file(self, tmp_path):
        config = {
            "servers": [
                {
                    "name": "test-server",
                    "transport": "sse",
                    "url": "http://localhost:9999/mcp",
                    "enabled": True,
                    "timeout_seconds": 3.0,
                }
            ]
        }
        config_file = tmp_path / "mcp_config.json"
        config_file.write_text(json.dumps(config))

        registry = MCPRegistry()
        registry.load_config(config_file)

        assert "test-server" in registry.servers
        assert registry.servers["test-server"].url == "http://localhost:9999/mcp"
        assert registry.servers["test-server"].timeout_seconds == 3.0

    def test_load_config_missing_file(self):
        registry = MCPRegistry()
        registry.load_config("/nonexistent/path.json")
        assert len(registry.servers) == 0  # Should not error

    def test_load_config_from_env(self):
        registry = MCPRegistry()
        with patch.dict("os.environ", {"MCP_SERVERS": "test:http://localhost:1234"}):
            registry.load_config("/nonexistent/path.json")
        assert "test" in registry.servers
        assert registry.servers["test"].url == "http://localhost:1234"

    def test_get_server(self):
        registry = MCPRegistry()
        registry.servers["s1"] = MCPServerConfig(name="s1", url="http://x")
        assert registry.get_server("s1") is not None
        assert registry.get_server("missing") is None

    def test_get_tool_server(self):
        registry = MCPRegistry()
        registry.servers["s1"] = MCPServerConfig(name="s1", url="http://x")
        registry.tools["my_tool"] = MCPTool(
            name="my_tool", description="test", server_name="s1"
        )
        server = registry.get_tool_server("my_tool")
        assert server is not None
        assert server.name == "s1"

    def test_get_tool_server_missing(self):
        registry = MCPRegistry()
        assert registry.get_tool_server("nonexistent") is None

    def test_list_available_tools(self):
        registry = MCPRegistry()
        registry.tools["t1"] = MCPTool(
            name="t1", description="d1", server_name="s1")
        registry.tools["t2"] = MCPTool(
            name="t2", description="d2", server_name="s1")
        tools = registry.list_available_tools()
        assert len(tools) == 2
        assert tools[0]["name"] == "t1"

    def test_load_actual_config(self):
        """Test loading the real mcp_servers.json config file."""
        config_path = Path(__file__).parent.parent / \
            "config" / "mcp_servers.json"
        if config_path.exists():
            registry = MCPRegistry()
            registry.load_config(config_path)
            assert len(registry.servers) == 3
            assert "catalog-db" in registry.servers
            assert "web-search" in registry.servers
            assert "image-tools" in registry.servers
            # All disabled by default
            for s in registry.servers.values():
                assert s.enabled is False


# ═══════════════════════════ CLIENT TESTS ═══════════════════════════


class TestMCPClient:
    """Test the MCP client with mocked HTTP."""

    @pytest.mark.asyncio
    async def test_call_tool_success(self):
        client = MCPClient()
        server = MCPServerConfig(
            name="test",
            transport=MCPTransport.SSE,
            url="http://localhost:9999/mcp",
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"products": [{"name": "Test Product"}]},
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(client, "_get_http_client") as mock_get:
            mock_http = AsyncMock()
            mock_http.post.return_value = mock_response
            mock_get.return_value = mock_http

            result = await client.call_tool(server, "search_products", {"query": "test"})

        assert result.success is True
        assert result.tool_name == "search_products"
        assert result.server_name == "test"
        assert result.data["products"][0]["name"] == "Test Product"
        assert result.latency_ms > 0

    @pytest.mark.asyncio
    async def test_call_tool_error_response(self):
        client = MCPClient()
        server = MCPServerConfig(
            name="test",
            transport=MCPTransport.SSE,
            url="http://localhost:9999/mcp",
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32601, "message": "Tool not found"},
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(client, "_get_http_client") as mock_get:
            mock_http = AsyncMock()
            mock_http.post.return_value = mock_response
            mock_get.return_value = mock_http

            result = await client.call_tool(server, "nonexistent")

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_call_tool_connection_error(self):
        client = MCPClient()
        server = MCPServerConfig(
            name="test",
            transport=MCPTransport.SSE,
            url="http://localhost:9999/mcp",
        )

        with patch.object(client, "_get_http_client") as mock_get:
            mock_http = AsyncMock()
            mock_http.post.side_effect = ConnectionError("refused")
            mock_get.return_value = mock_http

            result = await client.call_tool(server, "search")

        assert result.success is False
        assert "refused" in result.error.lower()

    @pytest.mark.asyncio
    async def test_call_tool_no_url(self):
        client = MCPClient()
        server = MCPServerConfig(name="test", transport=MCPTransport.SSE)

        result = await client.call_tool(server, "search")
        assert result.success is False
        assert "no URL" in result.error

    @pytest.mark.asyncio
    async def test_health_check_unreachable(self):
        client = MCPClient()
        server = MCPServerConfig(
            name="test",
            transport=MCPTransport.SSE,
            url="http://localhost:59999/mcp",
        )
        healthy = await client.health_check(server)
        assert healthy is False

    @pytest.mark.asyncio
    async def test_list_tools_success(self):
        client = MCPClient()
        server = MCPServerConfig(
            name="test",
            transport=MCPTransport.SSE,
            url="http://localhost:9999/mcp",
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": [
                    {"name": "search_products", "description": "Search"},
                    {"name": "list_brands", "description": "Brands"},
                ]
            },
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(client, "_get_http_client") as mock_get:
            mock_http = AsyncMock()
            mock_http.post.return_value = mock_response
            mock_get.return_value = mock_http

            tools = await client.list_tools(server)

        assert len(tools) == 2
        assert tools[0]["name"] == "search_products"

    @pytest.mark.asyncio
    async def test_close(self):
        client = MCPClient()
        # Should not error even when no connection
        await client.close()


# ═══════════════════════════ STARTUP TESTS ═══════════════════════════


class TestMCPStartup:
    """Test MCP lifecycle hooks."""

    @pytest.mark.asyncio
    async def test_init_no_servers(self):
        """init_mcp should not error when no servers are configured."""
        from backend.mcp.startup import init_mcp, shutdown_mcp

        with patch("backend.mcp.startup.get_registry") as mock_get:
            mock_registry = MagicMock()
            mock_registry.servers = {}
            mock_get.return_value = mock_registry

            # Should not raise
            await init_mcp()

    @pytest.mark.asyncio
    async def test_init_disabled_servers(self):
        """init_mcp should handle all-disabled servers gracefully."""
        from backend.mcp.startup import init_mcp

        with patch("backend.mcp.startup.get_registry") as mock_get:
            mock_registry = MagicMock()
            mock_registry.servers = {
                "s1": MCPServerConfig(name="s1", enabled=False)
            }
            mock_get.return_value = mock_registry

            await init_mcp()

    @pytest.mark.asyncio
    async def test_shutdown(self):
        from backend.mcp.startup import shutdown_mcp

        with patch("backend.mcp.startup.get_registry") as mock_get:
            mock_registry = MagicMock()
            mock_registry.close = AsyncMock()
            mock_get.return_value = mock_registry

            await shutdown_mcp()
            mock_registry.close.assert_awaited_once()


# ═══════════════════════════ CATALOG SERVER TESTS ═══════════════════════════


class TestCatalogDBServer:
    """Test the catalog MCP server endpoints using TestClient."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from backend.mcp.servers.catalog_db import app, _catalog

        # Inject test data
        _catalog.clear()
        _catalog.extend([
            {
                "name": "Baby Maracas MP34",
                "brand": "Halilit",
                "category": "Percussion",
                "sku": "MP34",
                "description": "Colorful baby maracas for early music education",
                "images": ["https://example.com/mp34.jpg"],
            },
            {
                "name": "Rain Wheel RW200",
                "brand": "Halilit",
                "category": "Percussion",
                "sku": "RW200",
                "description": "Mesmerizing rain sound wheel",
            },
            {
                "name": "Roland TD-27KV",
                "brand": "Roland",
                "category": "Drums",
                "sku": "TD27KV",
                "description": "Electronic drum kit",
            },
        ])
        return TestClient(app)

    def test_initialize(self, client):
        resp = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "test", "version": "1.0"},
                "capabilities": {},
            },
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"]["serverInfo"]["name"] == "halilit-catalog-db"

    def test_tools_list(self, client):
        resp = client.post("/mcp", json={
            "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}
        })
        assert resp.status_code == 200
        tools = resp.json()["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        assert "search_products" in tool_names
        assert "get_product" in tool_names
        assert "list_brands" in tool_names
        assert "list_categories" in tool_names
        assert "catalog_stats" in tool_names

    def test_search_products(self, client):
        resp = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_products",
                "arguments": {"query": "maracas"},
            },
        })
        assert resp.status_code == 200
        result = resp.json()["result"]
        assert result["total"] == 1
        assert result["products"][0]["name"] == "Baby Maracas MP34"

    def test_search_by_brand(self, client):
        resp = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "search_products",
                "arguments": {"query": "halilit"},
            },
        })
        result = resp.json()["result"]
        assert result["total"] == 2  # Two Halilit products

    def test_search_empty_query(self, client):
        resp = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "search_products",
                "arguments": {"query": ""},
            },
        })
        result = resp.json()["result"]
        assert result["total"] == 0

    def test_get_product_by_sku(self, client):
        resp = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "get_product",
                "arguments": {"sku": "MP34"},
            },
        })
        result = resp.json()["result"]
        assert result["found"] is True
        assert result["product"]["name"] == "Baby Maracas MP34"

    def test_get_product_by_name(self, client):
        resp = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "get_product",
                "arguments": {"name": "rain wheel"},
            },
        })
        result = resp.json()["result"]
        assert result["found"] is True
        assert "Rain Wheel" in result["product"]["name"]

    def test_get_product_not_found(self, client):
        resp = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "get_product",
                "arguments": {"sku": "NONEXISTENT"},
            },
        })
        result = resp.json()["result"]
        assert result["found"] is False

    def test_list_brands(self, client):
        resp = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {"name": "list_brands", "arguments": {}},
        })
        result = resp.json()["result"]
        brand_names = [b["name"] for b in result["brands"]]
        assert "Halilit" in brand_names
        assert "Roland" in brand_names

    def test_list_categories(self, client):
        resp = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {"name": "list_categories", "arguments": {}},
        })
        result = resp.json()["result"]
        cat_names = [c["name"] for c in result["categories"]]
        assert "Percussion" in cat_names
        assert "Drums" in cat_names

    def test_catalog_stats(self, client):
        resp = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {"name": "catalog_stats", "arguments": {}},
        })
        result = resp.json()["result"]
        assert result["total_products"] == 3
        assert result["total_brands"] == 2
        assert result["with_images"] == 1

    def test_unknown_tool(self, client):
        resp = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 12,
            "method": "tools/call",
            "params": {"name": "nonexistent_tool", "arguments": {}},
        })
        data = resp.json()
        assert data["error"]["code"] == -32601

    def test_unknown_method(self, client):
        resp = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 13,
            "method": "resources/list",
            "params": {},
        })
        data = resp.json()
        assert data["error"]["code"] == -32601


# ═══════════════════════════ MCP ROUTER TESTS ═══════════════════════════


class TestMCPRouter:
    """Test the FastAPI MCP management router."""

    @pytest.fixture
    def client(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from backend.api.mcp_router import router

        test_app = FastAPI()
        test_app.include_router(router)
        return TestClient(test_app)

    def test_list_servers(self, client):
        resp = client.get("/api/mcp/servers")
        assert resp.status_code == 200
        data = resp.json()
        assert "servers" in data

    def test_health_check(self, client):
        resp = client.get("/api/mcp/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "servers" in data

    def test_toggle_missing_server(self, client):
        resp = client.post("/api/mcp/servers/nonexistent/toggle?enabled=true")
        assert resp.status_code == 404


# ═══════════════════════════ INTEGRATION SMOKE TEST ═══════════════════════════


class TestIntegrationSmoke:
    """High-level integration: registry → client → catalog server."""

    def test_full_flow_with_catalog_server(self):
        """Register, discover tools, call a tool — full MCP flow."""
        from fastapi.testclient import TestClient
        from backend.mcp.servers.catalog_db import app as catalog_app, _catalog

        # Inject test data
        _catalog.clear()
        _catalog.extend([
            {"name": "Test Drum", "brand": "TestBrand",
                "category": "Drums", "sku": "TD1"},
        ])

        tc = TestClient(catalog_app, raise_server_exceptions=False)

        # 1. Initialize
        init_resp = tc.post("/mcp", json={
            "jsonrpc": "2.0", "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "clientInfo": {"name": "test"}, "capabilities": {}},
        })
        assert init_resp.status_code == 200

        # 2. Discover tools
        list_resp = tc.post("/mcp", json={
            "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}
        })
        tools = list_resp.json()["result"]["tools"]
        assert len(tools) == 5

        # 3. Call a tool
        call_resp = tc.post("/mcp", json={
            "jsonrpc": "2.0", "id": 3,
            "method": "tools/call",
            "params": {"name": "search_products", "arguments": {"query": "drum"}},
        })
        result = call_resp.json()["result"]
        assert result["total"] == 1
        assert result["products"][0]["sku"] == "TD1"
