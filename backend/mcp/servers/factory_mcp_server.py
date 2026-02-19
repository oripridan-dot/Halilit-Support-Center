"""
HALILIT FACTORY MCP SERVER  (backend/mcp/servers/factory_mcp_server.py)
=======================================================================
Exposes the Dark Factory agent swarm as a standard MCP server (stdio
JSON-RPC).  VS Code Copilot connects via .vscode/mcp.json and can call
any factory agent as a native tool inside chat.

Tools exposed:
  factory_chief_plan   – Ask the Chief to analyse the project and return
                         a JSON task queue.
  factory_build        – Run the Builder agent on a spec file path.
  factory_heal         – Run Watchdog: diagnose + auto-repair (3 cycles).
  factory_diagnose     – Run the scanner (no auto-fix).
  factory_v0_design    – Generate a v0.dev-ready UI spec + prompt from a
                         plain-English description, then optionally
                         integrate output code into the codebase.
  factory_commit       – Stage all changes and create a semantic commit.
  factory_status       – Return environment health as JSON.

Run standalone (for debugging):
    PYTHONPATH=. python backend/mcp/servers/factory_mcp_server.py

Register in .vscode/mcp.json, then reload VS Code.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Bootstrap: ensure project root is on sys.path & .env is loaded
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
logger = logging.getLogger("factory.mcp")

_PYTHON = sys.executable
_FACTORY_PY = str(_ROOT / "factory.py")

# ---------------------------------------------------------------------------
# MCP protocol constants
# ---------------------------------------------------------------------------
PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "halilit-factory", "version": "4.0.0"}

# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------
TOOLS: list[dict[str, Any]] = [
    {
        "name": "factory_chief_plan",
        "description": (
            "Ask the Dark Factory Chief to analyse the current project state "
            "and return a prioritised task queue. Provide an optional instruction "
            "to steer the plan (e.g. 'focus on ProductDetailView fixes')."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "instruction": {
                    "type": "string",
                    "description": "Optional steering instruction for the Chief.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "factory_build",
        "description": (
            "Run the Builder agent on a spec file to materialise it into code. "
            "Pass the relative path to a spec (e.g. specs/interface/my_spec.md)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "spec_path": {
                    "type": "string",
                    "description": "Relative path to the spec file (from project root).",
                }
            },
            "required": ["spec_path"],
        },
    },
    {
        "name": "factory_heal",
        "description": "Run the Watchdog agent: scan for errors and auto-repair (up to 3 cycles).",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "factory_diagnose",
        "description": "Scan the project for TypeScript / Python errors without making changes.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "factory_v0_design",
        "description": (
            "Generate a ready-to-paste v0.dev prompt for a UI component from a "
            "plain-English description, then optionally integrate v0 output code "
            "into the codebase using the Halilit architecture rules."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Plain-English description of the UI component to design.",
                },
                "component_type": {
                    "type": "string",
                    "description": "Component category hint, e.g. ProductCard, InventoryRow, Dashboard.",
                    "default": "UIComponent",
                },
                "v0_output_code": {
                    "type": "string",
                    "description": "Optional: paste the raw TSX code returned by v0.dev to integrate it.",
                },
                "target_file": {
                    "type": "string",
                    "description": "Optional: relative path where integrated code should be written.",
                },
            },
            "required": ["description"],
        },
    },
    {
        "name": "factory_commit",
        "description": "Stage all current changes and create a semantic git commit.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "factory_status",
        "description": "Return environment health: API key, venv, spec count, agent presence.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
]

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def _run_factory(args: list[str], timeout: int = 120) -> tuple[bool, str]:
    """Run factory.py with given args. Returns (success, output)."""
    cmd = [_PYTHON, _FACTORY_PY] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(_ROOT),
        )
        out = (result.stdout + "\n" + result.stderr).strip()
        return result.returncode == 0, out
    except subprocess.TimeoutExpired:
        return False, f"Timed out after {timeout}s"
    except Exception as e:
        return False, str(e)


def _tool_chief_plan(args: dict[str, Any]) -> str:
    instruction = args.get("instruction", "")
    try:
        sys.path.insert(0, str(_ROOT / "backend" / "factory"))
        from chief_agent import consult_chief  # type: ignore
        plan = consult_chief(instruction, is_startup=not instruction)
        return json.dumps(plan, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _tool_build(args: dict[str, Any]) -> str:
    spec = args.get("spec_path", "").strip()
    if not spec:
        return "Error: spec_path is required."
    ok, out = _run_factory(["build", spec], timeout=180)
    return out


def _tool_heal(args: dict[str, Any]) -> str:
    ok, out = _run_factory(["heal"], timeout=240)
    return out


def _tool_diagnose(args: dict[str, Any]) -> str:
    ok, out = _run_factory(["diagnose"], timeout=120)
    return out


def _tool_v0_design(args: dict[str, Any]) -> str:
    description = args.get("description", "")
    component_type = args.get("component_type", "UIComponent")
    v0_code = args.get("v0_output_code", "").strip()
    target_file = args.get("target_file", "").strip()

    try:
        from backend.factory.v0_agent import generate_v0_prompt, integrate_v0_output  # type: ignore
        if v0_code and target_file:
            result = integrate_v0_output(v0_code, target_file)
            return json.dumps(result, indent=2)
        else:
            result = generate_v0_prompt(description, component_type)
            return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _tool_commit(args: dict[str, Any]) -> str:
    ok, out = _run_factory(["commit"], timeout=90)
    return out


def _tool_status(args: dict[str, Any]) -> str:
    ok, out = _run_factory(["status"], timeout=20)
    return out


_TOOL_HANDLERS = {
    "factory_chief_plan": _tool_chief_plan,
    "factory_build": _tool_build,
    "factory_heal": _tool_heal,
    "factory_diagnose": _tool_diagnose,
    "factory_v0_design": _tool_v0_design,
    "factory_commit": _tool_commit,
    "factory_status": _tool_status,
}

# ---------------------------------------------------------------------------
# MCP JSON-RPC stdio server loop
# ---------------------------------------------------------------------------

def _respond(request_id: Any, result: Any) -> None:
    msg = json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result})
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def _error(request_id: Any, code: int, message: str) -> None:
    msg = json.dumps({"jsonrpc": "2.0", "id": request_id,
                      "error": {"code": code, "message": message}})
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def _handle(raw: str) -> None:
    try:
        req = json.loads(raw)
    except json.JSONDecodeError:
        return  # silently drop malformed lines (ping/keepalive etc.)

    req_id = req.get("id")
    method = req.get("method", "")

    # ----- Lifecycle -----
    if method == "initialize":
        _respond(req_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "serverInfo": SERVER_INFO,
            "capabilities": {"tools": {}},
        })
        return

    if method == "notifications/initialized":
        return  # no response for notifications

    # ----- Tool discovery -----
    if method == "tools/list":
        _respond(req_id, {"tools": TOOLS})
        return

    # ----- Tool execution -----
    if method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        handler = _TOOL_HANDLERS.get(tool_name)
        if handler is None:
            _error(req_id, -32601, f"Unknown tool: {tool_name}")
            return
        try:
            output = handler(tool_args)
        except Exception as exc:
            output = f"Error: {exc}"
        _respond(req_id, {
            "content": [{"type": "text", "text": output}],
            "isError": False,
        })
        return

    # ----- Unknown method -----
    if req_id is not None:
        _error(req_id, -32601, f"Method not found: {method}")


def main() -> None:
    logger.info("Halilit Factory MCP Server starting (stdio)")
    for line in sys.stdin:
        line = line.strip()
        if line:
            _handle(line)


if __name__ == "__main__":
    main()
