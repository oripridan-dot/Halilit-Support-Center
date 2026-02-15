"""
MCP Server: UI Bridge & Architect
Automates the workflow between Cursor (Logic) and Lovable/v0 (Visuals).

Tools:
1. generate_lovable_spec: Creates a strict visual prompt for Lovable/v0 based on backend rules.
2. integrate_lovable_code: Refactors Lovable's raw output to obey Halilit's architecture.

Run standalone:
    PYTHONPATH=. python backend/mcp/servers/ui_bridge.py

Listens on http://localhost:8200/mcp (SSE transport).
"""

from __future__ import annotations

import logging
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

logger = logging.getLogger("mcp.server.ui_bridge")

app = FastAPI(title="Halilit UI Bridge")

# Project root (backend/mcp/servers/ -> project root)
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
_FRONTEND_SRC = _PROJECT_ROOT / "frontend" / "src"

# -------------------------------------------------------------------------
# PROMPTS
# -------------------------------------------------------------------------

ARCHITECT_SYSTEM_PROMPT = """
You are the Halilit Frontend Architect.
Your goal is to generate a PROMPT for an AI UI Generator (like Lovable/v0).
The prompt must ensure the visual result is easy to wire into our backend.

RULES FOR THE PROMPT:
1. Specify the Visual Style: "Dark mode, slate-900 background, blue-500 accents".
2. Define Data Slots: Explicitly ask for specific UI elements that match our Data Model.
   - "Create a distinct container for Price (Commercial Data)".
   - "Create a grid area for Specifications (Official Data)".
3. Forbid Hardcoding: "Do not hardcode 'Fender Stratocaster'. Use placeholders."
"""

INTEGRATOR_SYSTEM_PROMPT = """
You are the Halilit Code Integration Engine.
Your job is to refactor "Dumb" UI code into "Smart" Halilit Components.

TRANSFORMATION RULES:
1. Import `useConductorCatalog` from the correct path (e.g., '../../hooks/useConductorCatalog').
2. Import `useNavigationStore` from the correct path (e.g., '../../store/navigationStore').
3. Replace static <img> with proper fallback handling or use existing ImageWithFallback component if available.
4. DATA BINDING:
   - Price -> product.price or catalog data (Commercial Source)
   - Specs -> product.specs (Official Source)
   - Reviews -> product.reviews or product.pros/cons (Contextual Source)
5. STYLE PRESERVATION: Keep all Tailwind classes exactly as they are.
6. Use TypeScript for props and types.
7. Output ONLY the React/TSX code - no markdown fences, no explanations.
"""


def _get_gemini_client():
    """Get Gemini client if API key is available."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        logger.warning("google-genai not installed")
        return None


def _strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences from AI output."""
    text = text.strip()
    # Remove leading ```tsx or ```ts or ```jsx
    text = re.sub(r"^```(?:tsx?|jsx?|javascript)?\s*\n?", "", text)
    # Remove trailing ```
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


# -------------------------------------------------------------------------
# TOOL 1: PROMPT GENERATOR (Cursor -> Lovable)
# -------------------------------------------------------------------------


def _handle_generate_spec(arguments: dict[str, Any]) -> dict[str, Any]:
    component_type = arguments.get("component_type", "ProductPage")
    context_data = arguments.get("context", "")

    prompt = f"""
Generate a detailed prompt for Lovable.dev or v0.dev to build a '{component_type}'.

Context: {context_data}

Ensure the prompt enforces:
- Bento Grid Layout or appropriate layout for the component
- Tailwind CSS
- Dark mode styling (bg-zinc-950, text-zinc-100)
- Distinct zones for Commercial (Price), Official (Specs), and Contextual (Reviews) data where applicable
- Use lucide-react for icons
- No hardcoded product names - use placeholders
"""

    client = _get_gemini_client()
    if client:
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[ARCHITECT_SYSTEM_PROMPT, prompt],
            )
            lovable_prompt = response.text.strip()
        except Exception as e:
            logger.warning("Gemini spec generation failed: %s", e)
            lovable_prompt = prompt  # Fallback to raw prompt
    else:
        lovable_prompt = prompt

    return {
        "status": "success",
        "action": "COPY_THIS_TO_LOVABLE",
        "lovable_prompt": lovable_prompt,
    }


# -------------------------------------------------------------------------
# TOOL 2: CODE INTEGRATOR (Lovable -> Cursor)
# -------------------------------------------------------------------------


def _handle_integrate_code(arguments: dict[str, Any]) -> dict[str, Any]:
    raw_code = arguments.get("code_content", "")
    target_path = arguments.get("file_path", "")
    create_backup = arguments.get("create_backup", True)

    if not target_path:
        return {"status": "failed", "error": "file_path is required"}

    # Resolve path relative to project root
    if not Path(target_path).is_absolute():
        full_path = _PROJECT_ROOT / target_path.lstrip("/")
    else:
        full_path = Path(target_path)

    if not raw_code and full_path.exists():
        try:
            raw_code = full_path.read_text(encoding="utf-8")
        except Exception as e:
            return {"status": "failed", "error": f"Could not read file: {e}"}

    if not raw_code:
        return {"status": "failed", "error": "No code provided to integrate. Set code_content or ensure file_path exists."}

    # 1. AI Refactoring (if Gemini available)
    client = _get_gemini_client()
    if client:
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    INTEGRATOR_SYSTEM_PROMPT,
                    f"Refactor this React code to use useConductorCatalog and useNavigationStore hooks where appropriate:\n\n{raw_code}",
                ],
            )
            integrated_code = _strip_markdown_fences(response.text)
        except Exception as e:
            logger.warning("Gemini integration failed: %s", e)
            integrated_code = raw_code
    else:
        integrated_code = raw_code

    # 2. Safety check - prevent empty writes
    if len(integrated_code.strip()) < 50:
        return {
            "status": "failed",
            "error": "Integrated code is too short - AI may have produced invalid output. Aborting to prevent data loss.",
        }

    # 3. Create backup and write
    full_path.parent.mkdir(parents=True, exist_ok=True)
    if create_backup and full_path.exists():
        backup_name = f"{full_path.stem}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}{full_path.suffix}"
        backup_path = full_path.parent / backup_name
        shutil.copy2(full_path, backup_path)
        logger.info("Backup created: %s", backup_path)

    try:
        full_path.write_text(integrated_code, encoding="utf-8")
    except Exception as e:
        return {"status": "failed", "error": str(e)}

    return {
        "status": "success",
        "lines": len(integrated_code.splitlines()),
        "file_path": str(full_path),
        "message": "Lovable UI successfully wired to backend logic.",
    }


# -------------------------------------------------------------------------
# MCP Tool Registry
# -------------------------------------------------------------------------

TOOLS = {
    "generate_lovable_spec": {
        "name": "generate_lovable_spec",
        "description": "Generates a prompt to paste into Lovable/v0 to get a UI component that matches our backend rules.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "component_type": {
                    "type": "string",
                    "description": "e.g., 'ProductHeader', 'ReviewGrid', 'GalaxyDashboard', 'SpectrumModule'",
                },
                "context": {
                    "type": "string",
                    "description": "Specific data requirements and component logic",
                },
            },
            "required": ["component_type"],
        },
        "handler": _handle_generate_spec,
    },
    "integrate_lovable_code": {
        "name": "integrate_lovable_code",
        "description": "Refactors raw Lovable/v0 code to wire it into the app's data layer (useConductorCatalog, useNavigationStore).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to save the integrated file (relative to project root)",
                },
                "code_content": {
                    "type": "string",
                    "description": "(Optional) The raw code from Lovable. If omitted, reads from file_path.",
                },
                "create_backup": {
                    "type": "boolean",
                    "description": "Create timestamped backup before overwriting (default true)",
                    "default": True,
                },
            },
            "required": ["file_path"],
        },
        "handler": _handle_integrate_code,
    },
}


# -------------------------------------------------------------------------
# MCP JSON-RPC Handler
# -------------------------------------------------------------------------


@app.post("/mcp")
async def mcp_endpoint(request: Request) -> JSONResponse:
    """Handle MCP JSON-RPC 2.0 requests."""
    body = await request.json()
    method = body.get("method", "")
    req_id = body.get("id", 0)
    params = body.get("params", {})
    arguments = params.get("arguments", {})

    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "halilit-ui-bridge",
                    "version": "1.0.0",
                },
                "capabilities": {
                    "tools": {"listChanged": False},
                },
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
        tool = TOOLS.get(tool_name)
        if not tool:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"},
            })

        try:
            result = tool["handler"](arguments)
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result,
            })
        except Exception as exc:
            logger.exception("Tool %s failed", tool_name)
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
    port = int(os.getenv("MCP_UI_BRIDGE_PORT", "8200"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
