"""
DATA MANAGER — Level 6 Hierarchical Sub-Swarm (backend/factory/data_manager.py)
=================================================================================
The absolute master of Python backend, FastAPI, data pipeline, and scraping
within the Dark Factory.

Level 6 Architecture role:
  - The Chief DELEGATES data/backend work here via {"tool": "delegate_data", ...}
  - This manager plans and executes a LOCALIZED sub-swarm that only speaks Python.
  - The Chief never inspects FastAPI route handlers; it only sees delegation results.

Sub-swarm execution order:
  1. Read the intent spec / instruction
  2. Query LLM to produce a backend-specific task queue (design → implement → diagnose)
  3. Execute tasks using factory.py (design, build, heal, diagnose)
  4. Return a structured result dict to the caller (nexus.py)

Key tools available to this manager:
  - design:    factory.py design — writes a new spec/blueprint
  - implement: factory.py build <spec> — implements a spec
  - heal:      factory.py heal — auto-fixes Python/FastAPI errors
  - diagnose:  factory.py diagnose — scans for errors without auto-fix
  - build:     factory.py build — rebuilds the product catalog (Conductor)
"""

from __future__ import annotations

import sys
import json
import re
import subprocess
import time
from pathlib import Path

_FACTORY_DIR = Path(__file__).resolve().parent
_ROOT = _FACTORY_DIR.parent.parent

sys.path.insert(0, str(_FACTORY_DIR))
from agent_core import query_llm  # noqa: E402


# ---------------------------------------------------------------------------
# SYSTEM PROMPT — Hyper-focused on Python / FastAPI / Data Pipeline
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are the DATA MANAGER — the absolute Master of Python, FastAPI, data ingestion, and catalog pipeline for the Halilit Support Center Dark Factory.

IDENTITY: You are NOT a general-purpose engineer. You ONLY know about:
  - Python 3.11+ / FastAPI / Pydantic v2 backend architecture
  - Halilit data pipeline: conductor_main.py → product_normalizer.py → product_graph.py
  - Three Source Rules (IMMUTABLE):
      Commercial (Halilit.com): Golden List, prices, SKUs — NEVER modify or override
      Official (Brand pages):   Titles, descriptions, specs, media
      Contextual (Reviews):     Pros/cons, ratings from 3+ trusted review sites
  - JIT intelligence: jit_agent.py + SSE streaming (never ground truth, 7-day cache)
  - Google Gemini 2.0 Flash via google.genai SDK
  - FastAPI routers in backend/api/ and backend/mcp/
  - Ingestion scripts in backend/ingestion/ and backend/scripts/
  - backend/data/ for JSON artifacts (gitignored)
  - ZERO tolerance for mock/AI-generated data presented as real

WHAT YOU DO:
  1. Receive a HIGH-LEVEL intent (e.g., "Add a new /api/products/search endpoint")
  2. Break it into the smallest possible backend operations
  3. Output a JSON task queue for your sub-swarm

TOOLS & RULES:
- 'design':   Create a new spec/blueprint FIRST for any new feature.
  args: spec file path (e.g. "data_pipeline/search_endpoint.md")
- 'implement': Materialise a spec into code.
  args: spec file path
- 'heal':     Fix Python/import/type errors — run AFTER implement if diagnose fails.
  args: "" (no args — heals entire project)
- 'diagnose': Scan for Python/FastAPI errors without auto-fixing.
  args: "" (scan all) or a relative file path
- 'build':    Rebuilds the product catalog — run after data pipeline changes.
  args: "" (no args — full rebuild)

ANTI-PATTERNS:
  - Do NOT hardcode mock/fake product data anywhere
  - Do NOT write AI-generated specs or reviews into data fields
  - Do NOT modify commercial source data (Halilit prices/SKUs are immutable)
  - Do NOT create FastAPI endpoints that bypass the Three Source Rules
  - Do NOT skip 'diagnose' after 'implement' for any backend change

SYSTEM INVARIANTS (NEVER remove or weaken these — they are enforced by code_guardian):
  - backend/factory/frontend_manager.py: _self_heal_patch_component, run_frontend_swarm
  - backend/factory/agent_core.py: query_llm, build_dynamic_context
  - backend/factory/udiff_patcher.py: apply_patch, apply_udiff
  - backend/factory/data_manager.py: run_data_swarm  ← THIS FILE
  - backend/source_rules.py: THREE_SOURCE_RULES, ZERO_TOLERANCE
  - nexus.py: execute_swarm, review_changes

OUTPUT FORMAT (JSON ONLY — no markdown fences):
{
  "thought": "What backend change is needed and what are the risks?",
  "explanation": "Plain-English plan (no jargon).",
  "queue": [
    {"tool": "design",    "args": "data_pipeline/my_feature.md", "parallel": false},
    {"tool": "implement", "args": "data_pipeline/my_feature.md", "parallel": false},
    {"tool": "diagnose",  "args": "",                            "parallel": false}
  ]
}

RULES:
- ALWAYS end the queue with a 'diagnose' task.
- If a new Python module is added, follow with 'heal' before 'diagnose'.
- Set "parallel": false for all tasks in this sub-swarm (sequential execution).
- For catalog changes, add 'build' as the final task before 'diagnose'.
- 'heal' is Level 1 recovery — always exhaust it before escalating.
"""


# ---------------------------------------------------------------------------
# Context builder — reads the relevant backend files for LLM grounding
# ---------------------------------------------------------------------------

def _build_backend_context(intent_spec: str) -> str:
    """Builds a minimal context string for the LLM to ground its plan."""
    lines: list[str] = ["=== BACKEND FILE INVENTORY ==="]

    backend_dir = _ROOT / "backend"
    api_dir = backend_dir / "api"
    ingestion_dir = backend_dir / "ingestion"
    scripts_dir = backend_dir / "scripts"

    for d, label in [
        (backend_dir, "backend/ (top-level)"),
        (api_dir, "backend/api/"),
        (ingestion_dir, "backend/ingestion/"),
        (scripts_dir, "backend/scripts/"),
    ]:
        if d.exists():
            py_files = sorted(d.glob("*.py"))
            if py_files:
                lines.append(f"\n{label}:")
                for f in py_files:
                    lines.append(f"  - {f.name}")

    # Surface data pipeline specs
    data_pipeline_dir = _ROOT / "specs" / "data_pipeline"
    if data_pipeline_dir.exists():
        specs = sorted(data_pipeline_dir.glob("*.md"))
        if specs:
            lines.append("\nspecs/data_pipeline/:")
            for s in specs:
                lines.append(f"  - {s.name}")

    lines.append(f"\n=== INTENT ===\n{intent_spec}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Sub-swarm planner
# ---------------------------------------------------------------------------

def _plan_data_queue(intent_spec: str) -> list[dict]:
    """Asks the Data Manager LLM to plan a task queue for the given intent."""
    context = _build_backend_context(intent_spec)
    user_prompt = (
        f"{context}\n\n"
        f"Plan the minimal backend task queue to satisfy this intent. "
        f"Respond ONLY with the JSON object."
    )

    raw = query_llm(SYSTEM_PROMPT, user_prompt,
                    temperature=0.3, model_tier="smart")
    if not raw:
        return []

    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(0))
            plan_explanation = parsed.get("explanation", "")
            if plan_explanation:
                print(f"   📋 Data Manager plan: {plan_explanation}")
            return parsed.get("queue", [])
    except json.JSONDecodeError:
        pass
    return []


# ---------------------------------------------------------------------------
# Task executor
# ---------------------------------------------------------------------------

def _execute_factory_cmd(tool: str, args: str) -> dict:
    """Runs a factory.py command for backend tasks."""
    py = sys.executable
    factory_script = str(_ROOT / "factory.py")

    cmd_map: dict[str, list[str] | None] = {
        "design":    [py, factory_script, "design", args] if args else None,
        "implement": [py, factory_script, "build", args] if args else None,
        "heal":      [py, factory_script, "heal"],
        "diagnose":  [py, factory_script, "diagnose"],
        "build":     [py, factory_script, "build"],
    }

    cmd = cmd_map.get(tool)
    if cmd is None:
        return {
            "tool": tool, "args": args, "success": False,
            "summary": f"⚠️  [{tool}] No command available or missing args",
            "error_output": "",
        }

    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = round(time.time() - start, 2)
        ok = result.returncode == 0
        combined = (result.stdout + "\n" + result.stderr).strip()
        tail = "\n".join(combined.splitlines()[-30:]) if combined else ""
        return {
            "tool": tool, "args": args, "success": ok,
            "summary": f"{'✅' if ok else '❌'} [{tool.upper()} {args}] ({elapsed}s)",
            "error_output": tail if not ok else "",
        }
    except Exception as exc:
        return {
            "tool": tool, "args": args, "success": False,
            "summary": f"❌ [{tool.upper()}] Exception: {exc}",
            "error_output": str(exc),
        }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_data_swarm(intent_spec: str) -> dict:
    """
    Executes a localized data/backend sub-swarm for the given intent.

    Called by nexus.py when the Chief routes a 'delegate_data' task.

    Args:
        intent_spec: High-level spec/intent string (e.g., "Add a new scraper
                     for brand X", or a spec file path).

    Returns:
        {
            "success": bool,
            "tasks_run": int,
            "failures": list[dict],
            "summary": str,
        }
    """
    print(f"\n   🔧 [DATA MANAGER] Planning backend sub-swarm for intent...")
    print(f"   {intent_spec[:120]}{'...' if len(intent_spec) > 120 else ''}")

    queue = _plan_data_queue(intent_spec)
    if not queue:
        return {
            "success": False,
            "tasks_run": 0,
            "failures": [],
            "summary": "❌ [DATA MANAGER] LLM returned empty queue.",
        }

    print(f"   ⚡ Data sub-swarm: {len(queue)} task(s) queued")

    failures: list[dict] = []
    tasks_run = 0

    for task in queue:
        tool = task.get("tool", "")
        args = task.get("args", "") if isinstance(
            task.get("args"), str) else str(task.get("args", ""))
        print(f"\n   → [{tool.upper()}] {args[:80]}")

        result = _execute_factory_cmd(tool, args)
        print(f"   {result['summary']}")
        tasks_run += 1

        if not result.get("success", False):
            failures.append(result)
            print(
                f"   ⛔ Data sub-swarm halted at step {tasks_run} due to failure.")
            break

    ok = len(failures) == 0
    summary = (
        f"✅ [DATA MANAGER] {tasks_run} task(s) completed successfully."
        if ok
        else f"❌ [DATA MANAGER] {len(failures)} failure(s) in {tasks_run} task(s)."
    )
    print(f"\n   {summary}")
    return {
        "success": ok,
        "tasks_run": tasks_run,
        "failures": failures,
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# CLI test mode
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys as _sys
    intent = " ".join(_sys.argv[1:]) if len(
        _sys.argv) > 1 else "Add a new /api/health endpoint to server.py"
    result = run_data_swarm(intent)
    print(f"\nResult: {json.dumps(result, indent=2)}")
