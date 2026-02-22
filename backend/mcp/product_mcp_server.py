"""
product_mcp_server.py — TooLoo Umbilical Server for Halilit Support Center
===========================================================================
Exposes Halilit's live state to TooLoo Core via the Model Context Protocol.

Run from anywhere:
    python backend/mcp/product_mcp_server.py

TooLoo connects via:
    python nexus.py halilit --test-mcp          (smoke test)
    python nexus.py halilit "your mandate"      (full mandate)

Port: TOOLOO_MCP_PORT env var (default 7001)
"""

from __future__ import annotations

import ast
import json
import logging
import os
import sqlite3
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # backend/mcp -> backend -> repo root
PORT = int(os.environ.get("TOOLOO_MCP_PORT", 7001))

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("halilit_mcp")

# ── Config ──────────────────────────────────────────────────────────────────

def _load_config() -> dict[str, str]:
    cfg: dict[str, str] = {}
    for f in [REPO_ROOT / ".tooloo.config"]:
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    cfg[k.strip()] = v.strip().strip('"\'')
    return cfg

CONFIG = _load_config()
PROJECT_NAME = CONFIG.get("PROJECT_NAME", "Halilit Support Center")
STACK = "Python FastAPI + React/Vite + SQLite + Gemini"

mcp = FastMCP(f"{PROJECT_NAME} — TooLoo Umbilical", host="localhost", port=PORT)

_IGNORE = {".git", "node_modules", "__pycache__", ".venv", "venv",
           "dist", "build", ".mypy_cache", ".pytest_cache"}


def _walk_tree(path: Path, depth: int, current: int = 0, prefix: str = "") -> list[str]:
    if current >= depth:
        return []
    lines: list[str] = []
    try:
        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
    except PermissionError:
        return []
    for i, entry in enumerate(entries):
        if entry.name in _IGNORE or entry.name.startswith("."):
            continue
        connector = "└── " if i == len(entries) - 1 else "├── "
        lines.append(f"{prefix}{connector}{entry.name}{'/' if entry.is_dir() else ''}")
        if entry.is_dir():
            ext = "    " if i == len(entries) - 1 else "│   "
            lines.extend(_walk_tree(entry, depth, current + 1, prefix + ext))
    return lines


@mcp.tool()
def get_project_identity() -> str:
    """Returns project name, stack, and .tooloo.config contents."""
    config_text = (REPO_ROOT / ".tooloo.config").read_text(encoding="utf-8") \
        if (REPO_ROOT / ".tooloo.config").exists() else "(no .tooloo.config)"
    return json.dumps({
        "project_name": PROJECT_NAME,
        "stack": STACK,
        "repo_root": str(REPO_ROOT),
        "config_summary": config_text[:2000],
    }, indent=2)


@mcp.tool()
def get_directory_structure(depth: int = 3) -> str:
    """Returns the top-level directory tree of the Halilit repository."""
    lines = _walk_tree(REPO_ROOT, depth)
    return f"{REPO_ROOT.name}/\n" + "\n".join(lines)


@mcp.tool()
def get_db_schema() -> str:
    """Returns the live SQLite database schema (tables + columns)."""
    dbs = [d for d in list(REPO_ROOT.rglob("*.db")) + list(REPO_ROOT.rglob("*.sqlite"))
           if not any(p in str(d) for p in ["node_modules", ".venv", "venv"])]
    if not dbs:
        return "(no SQLite database found)"
    results: list[str] = []
    for db_path in dbs[:3]:
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [r[0] for r in cur.fetchall()]
            parts = [f"## {db_path.relative_to(REPO_ROOT)}\nTables: {', '.join(tables)}"]
            for table in tables[:25]:
                cur.execute(f"PRAGMA table_info({table})")
                cols = cur.fetchall()
                col_str = ", ".join(f"{c[1]} {c[2]}" for c in cols)
                parts.append(f"  {table}({col_str})")
            conn.close()
            results.append("\n".join(parts))
        except Exception as exc:
            results.append(f"## {db_path.name}\n(error: {exc})")
    return "\n\n".join(results)


@mcp.tool()
def get_error_logs(lines: int = 100) -> str:
    """Returns the last N lines from the most recent log, or git log as fallback."""
    log_files = [f for d in [REPO_ROOT / "backend" / "logs", REPO_ROOT / "logs"]
                 if d.is_dir() for f in d.glob("*.log")]
    if not log_files:
        try:
            r = subprocess.run(
                ["git", "-C", str(REPO_ROOT), "log", "--oneline", "-20"],
                capture_output=True, text=True, timeout=10,
            )
            return f"(no .log files) Recent git log:\n\n{r.stdout.strip()}"
        except Exception:
            return "(no logs found)"
    latest = max(log_files, key=lambda p: p.stat().st_mtime)
    text = latest.read_text(encoding="utf-8", errors="replace")
    return "\n".join(text.splitlines()[-lines:])


@mcp.tool()
def get_architecture() -> str:
    """Returns docs/ARCHITECTURE.md content."""
    for p in [REPO_ROOT / "docs" / "ARCHITECTURE.md", REPO_ROOT / "ARCHITECTURE.md"]:
        if p.exists():
            return p.read_text(encoding="utf-8")
    return "(ARCHITECTURE.md not found)"


@mcp.tool()
def get_source_rules() -> str:
    """Returns source rules / governance docs."""
    for candidate in ["docs/SOURCE_RULES.md", "backend/source_rules.py", ".tooloo.config"]:
        p = REPO_ROOT / candidate
        if p.exists():
            return p.read_text(encoding="utf-8")
    return "(no source rules found)"


@mcp.tool()
def get_ast_structure(file_path: str) -> str:
    """Returns the AST symbol map (classes + functions) for a given file."""
    full = REPO_ROOT / file_path
    if not full.exists():
        return f"File not found: {file_path}"
    try:
        tree = ast.parse(full.read_text(encoding="utf-8", errors="replace"))
        symbols = [
            f"{'class' if isinstance(n, ast.ClassDef) else 'def'} {n.name} (line {n.lineno})"
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        ]
        return "\n".join(symbols) or "(no symbols found)"
    except SyntaxError as exc:
        return f"AST parse error: {exc}"


@mcp.tool()
def get_health_status() -> str:
    """Quick health check: git status + recent commits."""
    parts: list[str] = []
    for label, cmd in [
        ("git status", ["git", "-C", str(REPO_ROOT), "status", "--short"]),
        ("recent commits", ["git", "-C", str(REPO_ROOT), "log", "--oneline", "-5"]),
    ]:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            parts.append(f"### {label}\n{r.stdout.strip() or '(clean)'}")
        except Exception as exc:
            parts.append(f"### {label}\n(error: {exc})")
    return "\n\n".join(parts)


@mcp.tool()
def read_file(file_path: str, max_chars: int = 8000) -> str:
    """Read any file in the Halilit repo (for context gathering)."""
    full = REPO_ROOT / file_path
    if not full.exists():
        return f"File not found: {file_path}"
    return full.read_text(encoding="utf-8", errors="replace")[:max_chars]


if __name__ == "__main__":
    logger.info("🔌 Halilit MCP Server starting — port %d | root: %s", PORT, REPO_ROOT)
    mcp.run(transport="streamable-http")
