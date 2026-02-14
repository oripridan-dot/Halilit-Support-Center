"""MCP client with SSE and stdio transport support.

Designed for low-latency tool calls from Trinity Swarm agents.
Falls back gracefully if an MCP server is unavailable.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

import httpx

from backend import __version__
from backend.mcp.schemas import (
    MCPError,
    MCPRequest,
    MCPResponse,
    MCPServerConfig,
    MCPToolCallResult,
    MCPTransport,
)

logger = logging.getLogger("mcp.client")


class MCPClient:
    """Async client for communicating with MCP servers."""

    def __init__(self) -> None:
        self._http_client: httpx.AsyncClient | None = None
        self._request_counter: int = 0

    async def _get_http_client(self) -> httpx.AsyncClient:
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    def _next_id(self) -> int:
        self._request_counter += 1
        return self._request_counter

    async def call_tool(
        self,
        server: MCPServerConfig,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> MCPToolCallResult:
        """Call a tool on an MCP server. Returns normalized result."""
        start = time.monotonic()
        try:
            request = MCPRequest(
                id=self._next_id(),
                method="tools/call",
                params={
                    "name": tool_name,
                    "arguments": arguments or {},
                },
            )

            if server.transport == MCPTransport.SSE:
                response = await self._call_sse(server, request)
            elif server.transport == MCPTransport.STDIO:
                response = await self._call_stdio(server, request)
            else:
                raise ValueError(f"Unknown transport: {server.transport}")

            latency = (time.monotonic() - start) * 1000

            if response.error:
                return MCPToolCallResult(
                    tool_name=tool_name,
                    server_name=server.name,
                    success=False,
                    error=response.error.message,
                    latency_ms=latency,
                )

            return MCPToolCallResult(
                tool_name=tool_name,
                server_name=server.name,
                success=True,
                data=response.result,
                latency_ms=latency,
            )

        except Exception as exc:
            latency = (time.monotonic() - start) * 1000
            logger.warning(
                "MCP call failed: server=%s tool=%s error=%s",
                server.name,
                tool_name,
                str(exc),
            )
            return MCPToolCallResult(
                tool_name=tool_name,
                server_name=server.name,
                success=False,
                error=str(exc),
                latency_ms=latency,
            )

    async def _call_sse(
        self, server: MCPServerConfig, request: MCPRequest
    ) -> MCPResponse:
        """Send request to an SSE-based MCP server via HTTP POST."""
        if not server.url:
            raise ValueError(
                f"SSE server '{server.name}' has no URL configured")

        client = await self._get_http_client()
        resp = await client.post(
            server.url,
            json=request.model_dump(),
            timeout=server.timeout_seconds,
        )
        resp.raise_for_status()
        return MCPResponse.model_validate(resp.json())

    async def _call_stdio(
        self, server: MCPServerConfig, request: MCPRequest
    ) -> MCPResponse:
        """Send request to a stdio-based MCP server via subprocess."""
        if not server.command:
            raise ValueError(
                f"Stdio server '{server.name}' has no command configured")

        proc = await asyncio.create_subprocess_exec(
            *server.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**server.env} if server.env else None,
        )

        payload = json.dumps(request.model_dump()) + "\n"
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=payload.encode()),
            timeout=server.timeout_seconds,
        )

        if proc.returncode != 0:
            return MCPResponse(
                id=request.id,
                error=MCPError(
                    code=-1,
                    message=f"Process exited {proc.returncode}: {stderr.decode()[:500]}",
                ),
            )

        # Parse last JSON line from stdout
        lines = stdout.decode().strip().splitlines()
        for line in reversed(lines):
            line = line.strip()
            if line.startswith("{"):
                return MCPResponse.model_validate(json.loads(line))

        return MCPResponse(
            id=request.id,
            error=MCPError(
                code=-2, message="No JSON response from stdio server"),
        )

    async def list_tools(self, server: MCPServerConfig) -> list[dict[str, Any]]:
        """Discover tools available on an MCP server."""
        request = MCPRequest(
            id=self._next_id(),
            method="tools/list",
            params={},
        )

        if server.transport == MCPTransport.SSE:
            response = await self._call_sse(server, request)
        else:
            response = await self._call_stdio(server, request)

        if response.error or not response.result:
            return []

        tools = response.result
        if isinstance(tools, dict) and "tools" in tools:
            return tools["tools"]
        if isinstance(tools, list):
            return tools
        return []

    async def health_check(self, server: MCPServerConfig) -> bool:
        """Check if an MCP server is reachable."""
        try:
            request = MCPRequest(
                id=self._next_id(),
                method="initialize",
                params={
                    "protocolVersion": "2024-11-05",
                    "clientInfo": {"name": "halilit-support-center", "version": __version__},
                    "capabilities": {},
                },
            )
            if server.transport == MCPTransport.SSE and server.url:
                client = await self._get_http_client()
                resp = await client.post(
                    server.url,
                    json=request.model_dump(),
                    timeout=5.0,
                )
                return resp.status_code == 200
            return False
        except Exception:
            return False

    async def close(self) -> None:
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
