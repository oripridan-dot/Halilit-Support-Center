"""MCP Server: Web Search — product research via external search APIs.

Run standalone:
    PYTHONPATH=. python3 backend/mcp/servers/web_search.py

Listens on http://localhost:8100/mcp (SSE transport).
Requires: BRAVE_API_KEY or SERPER_API_KEY env var.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

logger = logging.getLogger("mcp.server.web_search")

app = FastAPI(title="Halilit Web Search MCP Server")

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")


async def _brave_search(query: str, count: int = 5) -> list[dict[str, Any]]:
    """Search via Brave Search API."""
    if not BRAVE_API_KEY:
        return [{"error": "BRAVE_API_KEY not configured"}]

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": BRAVE_API_KEY},
            params={"q": query, "count": count},
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("web", {}).get("results", [])[:count]:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "description": item.get("description", ""),
        })
    return results


async def _serper_search(query: str, count: int = 5) -> list[dict[str, Any]]:
    """Search via Serper.dev Google Search API."""
    if not SERPER_API_KEY:
        return [{"error": "SERPER_API_KEY not configured"}]

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY},
            json={"q": query, "num": count},
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("organic", [])[:count]:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "description": item.get("snippet", ""),
        })
    return results


async def _search(query: str, count: int = 5) -> list[dict[str, Any]]:
    """Route to available search provider."""
    if BRAVE_API_KEY:
        return await _brave_search(query, count)
    if SERPER_API_KEY:
        return await _serper_search(query, count)
    return [{"error": "No search API key configured (set BRAVE_API_KEY or SERPER_API_KEY)"}]


TOOLS = {
    "web_search": {
        "name": "web_search",
        "description": "Search the web for product information, specifications, reviews, and pricing",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'Halilit baby maracas MP34')",
                },
                "count": {
                    "type": "integer",
                    "description": "Number of results (default 5, max 10)",
                },
            },
            "required": ["query"],
        },
    },
    "product_research": {
        "name": "product_research",
        "description": "Research a specific product across multiple sources (manufacturer, retailers, reviews)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string", "description": "Product name"},
                "brand": {"type": "string", "description": "Brand name"},
                "include_pricing": {
                    "type": "boolean",
                    "description": "Include price comparison",
                },
            },
            "required": ["product_name"],
        },
    },
}


async def _handle_web_search(arguments: dict[str, Any]) -> Any:
    query = arguments.get("query", "")
    count = min(arguments.get("count", 5), 10)
    if not query:
        return {"results": [], "error": "Missing query"}
    results = await _search(query, count)
    return {"results": results, "query": query}


async def _handle_product_research(arguments: dict[str, Any]) -> Any:
    product_name = arguments.get("product_name", "")
    brand = arguments.get("brand", "")
    include_pricing = arguments.get("include_pricing", False)

    if not product_name:
        return {"error": "Missing product_name"}

    queries = [
        f"{brand} {product_name} specifications",
        f"{brand} {product_name} official product page",
    ]
    if include_pricing:
        queries.append(f"{brand} {product_name} price buy")

    all_results: dict[str, Any] = {}
    for query in queries:
        all_results[query] = await _search(query, 3)

    return {"product": product_name, "brand": brand, "research": all_results}


HANDLERS = {
    "web_search": _handle_web_search,
    "product_research": _handle_product_research,
}


@app.post("/mcp")
async def mcp_endpoint(request: Request) -> JSONResponse:
    """Handle MCP JSON-RPC 2.0 requests."""
    body = await request.json()
    method = body.get("method", "")
    req_id = body.get("id", 0)
    params = body.get("params", {})

    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "halilit-web-search", "version": "1.0.0"},
                "capabilities": {"tools": {"listChanged": False}},
            },
        })

    if method == "tools/list":
        tool_list = [
            {
                "name": t["name"],
                "description": t["description"],
                "inputSchema": t["inputSchema"],
            }
            for t in TOOLS.values()
        ]
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": tool_list},
        })

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        handler = HANDLERS.get(tool_name)
        if not handler:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"},
            })
        try:
            result = await handler(arguments)
            return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": result})
        except Exception as exc:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(exc)},
            })

    return JSONResponse({
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method '{method}' not supported"},
    })


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = int(os.getenv("MCP_SEARCH_PORT", "8100"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
