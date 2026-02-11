"""Pydantic v2 models for MCP JSON-RPC 2.0 messages."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MCPTransport(str, Enum):
    STDIO = "stdio"
    SSE = "sse"


class MCPServerConfig(BaseModel):
    """Configuration for a registered MCP server."""

    name: str
    transport: MCPTransport = MCPTransport.SSE
    url: str | None = None  # For SSE transport
    command: list[str] | None = None  # For stdio transport
    env: dict[str, str] = Field(default_factory=dict)
    timeout_seconds: float = 10.0
    enabled: bool = True


class MCPToolParam(BaseModel):
    name: str
    type: str = "string"
    description: str = ""
    required: bool = True


class MCPTool(BaseModel):
    """A tool exposed by an MCP server."""

    name: str
    description: str
    server_name: str
    parameters: list[MCPToolParam] = Field(default_factory=list)


class MCPRequest(BaseModel):
    """JSON-RPC 2.0 request to an MCP server."""

    jsonrpc: str = "2.0"
    id: int | str = 0
    method: str
    params: dict[str, Any] = Field(default_factory=dict)


class MCPError(BaseModel):
    code: int
    message: str
    data: Any | None = None


class MCPResponse(BaseModel):
    """JSON-RPC 2.0 response from an MCP server."""

    jsonrpc: str = "2.0"
    id: int | str = 0
    result: Any | None = None
    error: MCPError | None = None


class MCPToolCallResult(BaseModel):
    """Normalized result returned to Trinity Swarm agents."""

    tool_name: str
    server_name: str
    success: bool
    data: Any | None = None
    error: str | None = None
    latency_ms: float = 0.0
