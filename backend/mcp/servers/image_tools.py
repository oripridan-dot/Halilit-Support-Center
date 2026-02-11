"""MCP Server: Image Tools — image validation, processing, and analysis.

Run standalone:
    PYTHONPATH=. python3 backend/mcp/servers/image_tools.py

Listens on http://localhost:8101/mcp (SSE transport).
"""

from __future__ import annotations

import io
import logging
import os
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

logger = logging.getLogger("mcp.server.image_tools")

app = FastAPI(title="Halilit Image Tools MCP Server")

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    logger.warning("Pillow not installed — image processing limited")


TOOLS = {
    "validate_image_url": {
        "name": "validate_image_url",
        "description": "Check if an image URL is accessible and returns valid image data",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Image URL to validate"},
                "min_width": {
                    "type": "integer",
                    "description": "Minimum acceptable width (default 100)",
                },
                "min_height": {
                    "type": "integer",
                    "description": "Minimum acceptable height (default 100)",
                },
            },
            "required": ["url"],
        },
    },
    "get_image_info": {
        "name": "get_image_info",
        "description": "Get image dimensions, format, and file size from a URL",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Image URL"},
            },
            "required": ["url"],
        },
    },
    "check_image_quality": {
        "name": "check_image_quality",
        "description": "Assess image quality: resolution, aspect ratio, file size, format suitability",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Image URL"},
                "purpose": {
                    "type": "string",
                    "description": "Intended use: 'hero', 'thumbnail', 'gallery'",
                    "enum": ["hero", "thumbnail", "gallery"],
                },
            },
            "required": ["url"],
        },
    },
}


async def _fetch_image(url: str) -> tuple[bytes, str]:
    """Fetch image bytes and content type from URL."""
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url, timeout=15.0)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        return resp.content, content_type


async def _handle_validate_image_url(arguments: dict[str, Any]) -> Any:
    url = arguments.get("url", "")
    min_width = arguments.get("min_width", 100)
    min_height = arguments.get("min_height", 100)

    if not url:
        return {"valid": False, "error": "Missing url"}

    try:
        img_bytes, content_type = await _fetch_image(url)
    except Exception as exc:
        return {"valid": False, "url": url, "error": f"Fetch failed: {exc}"}

    if not content_type.startswith("image/"):
        return {"valid": False, "url": url, "error": f"Not an image: {content_type}"}

    if HAS_PILLOW:
        try:
            img = Image.open(io.BytesIO(img_bytes))
            width, height = img.size
            if width < min_width or height < min_height:
                return {
                    "valid": False,
                    "url": url,
                    "width": width,
                    "height": height,
                    "error": f"Too small: {width}x{height} (min {min_width}x{min_height})",
                }
            return {
                "valid": True,
                "url": url,
                "width": width,
                "height": height,
                "format": img.format,
                "file_size_kb": round(len(img_bytes) / 1024, 1),
            }
        except Exception as exc:
            return {"valid": False, "url": url, "error": f"Image decode failed: {exc}"}

    return {
        "valid": True,
        "url": url,
        "content_type": content_type,
        "file_size_kb": round(len(img_bytes) / 1024, 1),
        "note": "Pillow not available — dimensions not checked",
    }


async def _handle_get_image_info(arguments: dict[str, Any]) -> Any:
    url = arguments.get("url", "")
    if not url:
        return {"error": "Missing url"}

    try:
        img_bytes, content_type = await _fetch_image(url)
    except Exception as exc:
        return {"error": f"Fetch failed: {exc}"}

    info: dict[str, Any] = {
        "url": url,
        "content_type": content_type,
        "file_size_kb": round(len(img_bytes) / 1024, 1),
    }

    if HAS_PILLOW:
        try:
            img = Image.open(io.BytesIO(img_bytes))
            info["width"] = img.size[0]
            info["height"] = img.size[1]
            info["format"] = img.format
            info["mode"] = img.mode
        except Exception:
            info["decode_error"] = True

    return info


async def _handle_check_image_quality(arguments: dict[str, Any]) -> Any:
    url = arguments.get("url", "")
    purpose = arguments.get("purpose", "hero")

    if not url:
        return {"error": "Missing url"}

    # Quality thresholds by purpose
    thresholds = {
        "hero": {"min_width": 800, "min_height": 600, "max_size_kb": 5000},
        "thumbnail": {"min_width": 150, "min_height": 150, "max_size_kb": 500},
        "gallery": {"min_width": 400, "min_height": 300, "max_size_kb": 3000},
    }
    thresh = thresholds.get(purpose, thresholds["hero"])

    try:
        img_bytes, content_type = await _fetch_image(url)
    except Exception as exc:
        return {"quality": "failed", "error": str(exc)}

    file_size_kb = len(img_bytes) / 1024
    issues: list[str] = []
    score = 100

    if not content_type.startswith("image/"):
        return {"quality": "invalid", "error": "Not an image"}

    if file_size_kb > thresh["max_size_kb"]:
        issues.append(
            f"File too large: {file_size_kb:.0f}KB > {thresh['max_size_kb']}KB"
        )
        score -= 20

    if HAS_PILLOW:
        try:
            img = Image.open(io.BytesIO(img_bytes))
            w, h = img.size
            if w < thresh["min_width"]:
                issues.append(f"Width {w} < {thresh['min_width']}")
                score -= 30
            if h < thresh["min_height"]:
                issues.append(f"Height {h} < {thresh['min_height']}")
                score -= 30
            if img.format and img.format.upper() not in ("JPEG", "PNG", "WEBP"):
                issues.append(f"Unusual format: {img.format}")
                score -= 10
        except Exception as exc:
            issues.append(f"Decode error: {exc}")
            score -= 50

    quality = (
        "excellent"
        if score >= 90
        else "good"
        if score >= 70
        else "acceptable"
        if score >= 50
        else "poor"
    )

    return {
        "quality": quality,
        "score": max(0, score),
        "purpose": purpose,
        "file_size_kb": round(file_size_kb, 1),
        "issues": issues,
        "url": url,
    }


HANDLERS = {
    "validate_image_url": _handle_validate_image_url,
    "get_image_info": _handle_get_image_info,
    "check_image_quality": _handle_check_image_quality,
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
                "serverInfo": {"name": "halilit-image-tools", "version": "1.0.0"},
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
                "error": {
                    "code": -32601,
                    "message": f"Tool '{tool_name}' not found",
                },
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
    port = int(os.getenv("MCP_IMAGE_PORT", "8101"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
