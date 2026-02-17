"""
MCP Server: Image Tools (v2)
Powered by backend.ingestion.visual_validator.

Run standalone:
    PYTHONPATH=. python backend/mcp/servers/image_tools.py

Listens on http://localhost:8101/mcp (POST JSON-RPC).
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

from backend.ingestion.visual_validator import get_visual_validator

logger = logging.getLogger("mcp.server.image_tools")
app = FastAPI(title="Halilit Image Tools MCP")
validator = get_visual_validator()

TOOLS = {
    "validate_image": {
        "name": "validate_image",
        "description": "Deep validation of an image URL (quality, resolution, visual check).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "purpose": {"type": "string", "enum": ["hero", "thumbnail", "gallery"]},
            },
            "required": ["url"],
        },
    },
    "compare_images": {
        "name": "compare_images",
        "description": "Compare two image URLs to check if they are identical or similar.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url_a": {"type": "string"},
                "url_b": {"type": "string"},
            },
            "required": ["url_a", "url_b"],
        },
    },
    "audit_image_ai": {
        "name": "audit_image_ai",
        "description": "AI-powered audit of an image URL: Gemini vision assesses if it is a good product hero (not placeholder, clear, trustworthy).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "product_name": {"type": "string"},
                "brand": {"type": "string"},
            },
            "required": ["url"],
        },
    },
}


async def _handle_validate_image(args: dict) -> Any:
    url = args.get("url")
    if not url:
        return {"error": "Missing URL"}

    img_bytes, mime = await validator.fetch_image(url)
    if not img_bytes:
        return {"valid": False, "error": "Could not fetch image"}

    result = validator.validate_quality(img_bytes, args.get("purpose", "hero"))
    result["url"] = url
    result["content_type"] = mime
    result["valid"] = result.get("status") == "pass"
    return result


async def _handle_compare_images(args: dict) -> Any:
    url_a = args.get("url_a")
    url_b = args.get("url_b")

    if not url_a or not url_b:
        return {"error": "Missing url_a or url_b"}

    bytes_a, _ = await validator.fetch_image(url_a)
    bytes_b, _ = await validator.fetch_image(url_b)

    if not bytes_a or not bytes_b:
        return {"error": "Could not fetch one or both images"}

    result = validator.compare_images(bytes_a, bytes_b)
    result["url_a"] = url_a
    result["url_b"] = url_b
    return result


async def _handle_audit_image_ai(args: dict) -> Any:
    url = args.get("url")
    if not url:
        return {"error": "Missing url"}

    img_bytes, _ = await validator.fetch_image(url)
    if not img_bytes:
        return {"error": "Could not fetch image", "url": url}

    import asyncio
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: validator.audit_quality_ai(
            img_bytes,
            product_name=args.get("product_name"),
            brand=args.get("brand"),
        ),
    )
    result["url"] = url
    return result


HANDLERS = {
    "validate_image": _handle_validate_image,
    "compare_images": _handle_compare_images,
    "audit_image_ai": _handle_audit_image_ai,
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
                "serverInfo": {"name": "halilit-image-tools", "version": "2.0.0"},
                "capabilities": {"tools": {"listChanged": False}},
            },
        })

    if method == "tools/list":
        tool_list = [
            {"name": t["name"], "description": t["description"], "inputSchema": t["inputSchema"]}
            for t in TOOLS.values()
        ]
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": tool_list},
        })

    if method == "tools/call":
        name = params.get("name")
        handler = HANDLERS.get(name)
        if handler:
            try:
                res = await handler(params.get("arguments", {}))
                return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": res})
            except Exception as exc:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32000, "message": str(exc)},
                })
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Tool '{name}' not found"},
        })

    return JSONResponse({
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method '{method}' not supported"},
    })


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = int(os.getenv("MCP_IMAGE_PORT", "8101"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
