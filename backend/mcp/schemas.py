"""MCP Pydantic v2 data models — requests, responses, tool configs, server configs."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MCPTransport(str, Enum):
    SSE = "sse"
    STDIO = "stdio"


class MCPServerConfig(BaseModel):
    name: str
    transport: MCPTransport = MCPTransport.SSE
    url: str | None = None
    command: list[str] | None = None
    timeout_seconds: float = 10.0
    enabled: bool = True
    env: dict[str, str] | None = None


class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: int | str
    method: str
    params: dict[str, Any] = Field(default_factory=dict)


class MCPError(BaseModel):
    code: int
    message: str
    data: Any = None


class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int | str | None = None
    result: Any = None
    error: MCPError | None = None


class MCPTool(BaseModel):
    name: str
    description: str
    server_name: str
    input_schema: dict[str, Any] = Field(default_factory=dict)


class MCPToolCallResult(BaseModel):
    tool_name: str
    server_name: str
    success: bool
    data: Any = None
    error: str | None = None
    latency_ms: float = 0.0
