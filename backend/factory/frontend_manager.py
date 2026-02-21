"""
FRONTEND MANAGER — Level 6 Hierarchical Sub-Swarm (backend/factory/frontend_manager.py)
========================================================================================
The absolute master of React, Tailwind, and Vite within the Dark Factory.

Level 6 Architecture role:
  - The Chief DELEGATES frontend work here via {"tool": "delegate_frontend", ...}
  - This manager plans and executes a LOCALIZED sub-swarm that only speaks React.
  - The Chief never sees TypeScript; it only sees the delegation result.

Sub-swarm execution order:
  1. Read the intent spec / instruction
  2. Query LLM to produce a frontend-specific task queue (synthesize → patch/implement → validate)
  3. Execute tasks using ast_patcher (surgical patches) or factory.py build (full impl)
  4. Return a structured result dict to the caller (nexus.py)

Key tools available to this manager:
  - patch_component: ast_patcher.apply_patch() — surgical, no full-file rewrite
  - synthesize:      factory.py synthesize — Ribosome translates Genome → Directive
  - implement:       factory.py build <spec> — full spec-driven implementation
  - ui_validate:     factory.py ui_validate — Vite build + import integrity check
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

KANBAN_PATH = _ROOT / "FACTORY_KANBAN.md"

sys.path.insert(0, str(_FACTORY_DIR))
from agent_core import query_llm  # noqa: E402
from udiff_patcher import apply_patch, apply_patch_batch  # noqa: E402


# ---------------------------------------------------------------------------
# Real-time Kanban board helper
# ---------------------------------------------------------------------------

def update_kanban(branch: str, target: str, state: str) -> None:
    """
    Writes real-time telemetry to the physical Kanban board at FACTORY_KANBAN.md.
    Called at each state transition so the Operator can track execution live.
    """
    content = (
        f"# 🏭 FACTORY KANBAN (LIVE)\n\n"
        f"**Current Branch:** `{branch}`\n"
        f"**Target:** `{target}`\n\n"
        f"### 🔄 Execution State\n\n"
        f"{state}\n\n"
        f"---\n\n"
        f"*Last updated: {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*\n"
    )
    KANBAN_PATH.write_text(content, encoding="utf-8")
    print(f"\n📊 KANBAN → {state}")


# ---------------------------------------------------------------------------
# SYSTEM PROMPT — Hyper-focused on React / Tailwind / Vite
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are the FRONTEND MANAGER — the absolute Master of React, TypeScript, Tailwind CSS, and Vite for the Halilit Support Center Dark Factory.

IDENTITY: You are NOT a general-purpose engineer. You ONLY know about:
  - React 18 + TypeScript 5 component architecture
  - Tailwind CSS 3.4 dark-theme UI (slate-900/800/700 palette, blue-500 accents)
  - Vite 5 build system, ESM imports, fast HMR
  - Zustand 5 (app state) + React Query 5 (server state)
  - Framer Motion animations
  - Halilit component hierarchy: App.tsx → views/ (Dashboard, Inventory, ProductDetail) → cockpit/
  - Three Source Rules: never display synthetic/mock data in UI

WHAT YOU DO:
  1. Receive a HIGH-LEVEL intent (e.g., "Add 300ms debounce to GlobalSearch")
  2. Break it into the smallest possible surgical operations
  3. Output a JSON task queue for your sub-swarm

TOOLS & RULES:
- 'patch_component': PREFERRED for changes < 30 lines. Uses ast_patcher — no full-file rewrite.
  args: {"file": "relative/path.tsx", "search": "exact anchor code", "replace": "new code"}
  ONLY use when you can identify the EXACT anchor block in the target file.
- 'implement': For new components or large rewrites where patch is insufficient.
  args: spec file path (e.g. "specs/interface/02_inventory_grid.md")
- 'synthesize': For Genome-driven phenotype synthesis BEFORE implement.
  args: genome YAML path (e.g. "specs/genomes/search_bar.yaml")
- 'ui_validate': MANDATORY after any patch_component or implement that touches frontend.
  args: "" or "--no-build"

ANTI-PATTERNS (never do these):
  - Do NOT generate full 400-line component rewrites when a 5-line patch works
  - Do NOT invent file paths — only use files you KNOW exist
  - Do NOT skip ui_validate — it catches Vite runtime errors tsc/eslint miss
  - Do NOT import Three.js, GalaxyDashboard, or any 3D libraries
- NEVER remove or weaken the `_self_heal_patch_component` function or its call-site in `run_frontend_swarm`. It is a SYSTEM INVARIANT.

OUTPUT FORMAT (JSON ONLY — no markdown fences):
{
  "thought": "What is the minimal change needed?",
  "explanation": "Plain-English plan — jargon-free.",
  "queue": [
    {"tool": "patch_component", "args": {"file": "frontend/src/components/GlobalSearch.tsx", "search": "const DEBOUNCE_MS = 0;", "replace": "const DEBOUNCE_MS = 300;"}, "parallel": false},
    {"tool": "ui_validate",     "args": "",                                                                                                                                        "parallel": false}
  ]
}

RULES:
- ALWAYS end the queue with a 'ui_validate' task.
- Prefer 'patch_component' over 'implement' whenever the target block is identifiable.
- If the intent requires a NEW spec (no spec file exists), prepend a note in "thought" — but still try to patch_component for simple changes.
- Set "parallel": false for all tasks in this sub-swarm (sub-swarm runs sequentially).
"""


# ---------------------------------------------------------------------------
# Context builder — reads the relevant frontend files to give the LLM ground truth
# ---------------------------------------------------------------------------

def _build_frontend_context(intent_spec: str) -> str:
    """Builds a minimal context string for the LLM to ground its plan."""
    lines: list[str] = []
    lines.append("=== FRONTEND FILE INVENTORY ===")

    views_dir = _ROOT / "frontend" / "src" / "components" / "views"
    cockpit_dir = _ROOT / "frontend" / "src" / "components" / "cockpit"
    hooks_dir = _ROOT / "frontend" / "src" / "hooks"
    components_dir = _ROOT / "frontend" / "src" / "components"

    for d in [views_dir, cockpit_dir, hooks_dir]:
        if d.exists():
            files = sorted(d.glob("*.tsx")) + sorted(d.glob("*.ts"))
            lines.append(f"\n{d.relative_to(_ROOT)}/:")
            for f in files:
                lines.append(f"  - {f.name}")

    # Surface top-level components
    if components_dir.exists():
        top_files = sorted(components_dir.glob("*.tsx"))
        if top_files:
            lines.append(f"\ncomponents/ (top-level):")
            for f in top_files:
                lines.append(f"  - {f.name}")

    lines.append(f"\n=== INTENT ===\n{intent_spec}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Sub-swarm planner
# ---------------------------------------------------------------------------

def _plan_frontend_queue(intent_spec: str) -> list[dict]:
    """Asks the Frontend Manager LLM to plan a task queue for the given intent."""
    context = _build_frontend_context(intent_spec)
    user_prompt = (
        f"{context}\n\n"
        f"Plan the minimal frontend task queue to satisfy this intent. "
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
                print(f"   📋 Frontend Manager plan: {plan_explanation}")
            return parsed.get("queue", [])
    except json.JSONDecodeError:
        pass
    return []


# ---------------------------------------------------------------------------
# Self-healing — reattempt a failed patch_component by re-reading the actual
# file and asking the LLM to produce a corrected search/replace block.
# SYSTEM INVARIANT: do NOT remove this function.
# ---------------------------------------------------------------------------

_HEAL_SYSTEM_PROMPT = """
You are the FRONTEND MANAGER in self-healing mode.
A patch_component operation just failed because the search anchor was not found in the file.
Your job: read the ACTUAL FILE CONTENT provided and produce a corrected patch, OR fall back to an 'implement' task if no surgical patch is possible.

RULES:
- Respond ONLY with valid JSON — no markdown fences.
- Prefer 'patch_component' if you can identify the exact anchor in the file.
- Use 'implement' only if the component needs a full rewrite.
- Do NOT invent file paths.
- Always end queue with 'ui_validate'.

OUTPUT FORMAT:
{
  "thought": "Why did the original anchor miss?",
  "queue": [
    {"tool": "patch_component", "args": {"file": "relative/path.tsx", "search": "exact anchor", "replace": "new code"}, "parallel": false},
    {"tool": "ui_validate", "args": "", "parallel": false}
  ]
}
"""


def _self_heal_patch_component(
    file_path: str,
    intent: str,
    original_search: str,
    original_replace: str,
    max_retries: int = 2,
) -> dict:
    """
    SYSTEM INVARIANT — do NOT remove.
    Called when patch_component fails with "Anchor not found".
    Reads the actual file, re-queries the LLM for a corrected plan, and retries.
    Falls back to 'implement' (full spec build) if all patch retries fail.
    """
    abs_path = _ROOT / file_path
    if not abs_path.exists():
        return {
            "tool": "patch_component", "args": file_path, "success": False,
            "summary": f"❌ [self-heal] File not found: {file_path}",
            "error_output": f"path {file_path} does not exist",
        }

    file_lines = abs_path.read_text(encoding="utf-8").splitlines()
    file_preview = "\n".join(file_lines[:300])
    if len(file_lines) > 300:
        file_preview += f"\n... ({len(file_lines) - 300} more lines truncated)"

    user_prompt = (
        f"Original intent: {intent}\n\n"
        f"Failed anchor (search block that was NOT found in the file):\n```\n{original_search}\n```\n\n"
        f"Intended replacement:\n```\n{original_replace}\n```\n\n"
        f"ACTUAL FILE CONTENT ({file_path}):\n```tsx\n{file_preview}\n```\n\n"
        f"Produce a corrected JSON task queue to apply this change. "
        f"Use the exact code from the file as the search anchor."
    )

    for attempt in range(1, max_retries + 1):
        print(
            f"   🔧 [self-heal] Attempt {attempt}/{max_retries} — querying LLM for corrected patch...")
        raw = query_llm(_HEAL_SYSTEM_PROMPT, user_prompt,
                        temperature=0.2, model_tier="smart")
        if not raw:
            continue
        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        try:
            json_match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not json_match:
                continue
            parsed = json.loads(json_match.group(0))
            thought = parsed.get("thought", "")
            if thought:
                print(f"   💡 [self-heal] {thought}")
            heal_queue = parsed.get("queue", [])
        except (json.JSONDecodeError, ValueError):
            continue

        for task in heal_queue:
            tool = task.get("tool", "")
            args = task.get("args", "")
            if tool == "patch_component":
                patch_args = args if isinstance(args, dict) else {}
                result = _execute_patch_component(patch_args)
                if result.get("success"):
                    print(
                        f"   ✅ [self-heal] Patch applied on attempt {attempt}.")
                    return result
                print(
                    f"   ✗  [self-heal] Attempt {attempt} still failed — {result.get('error_output', '')}")
            elif tool == "implement":
                str_args = args if isinstance(args, str) else str(args)
                print(
                    f"   🏗️  [self-heal] Falling back to implement: {str_args}")
                return _execute_factory_cmd("implement", str_args)

    # All retries exhausted — write a temp spec and implement
    print(
        f"   ⚠️  [self-heal] All {max_retries} patch retries failed. Attempting implement fallback...")
    tmp_spec = _ROOT / "specs" / "temp" / f"_heal_{Path(file_path).stem}.md"
    tmp_spec.parent.mkdir(parents=True, exist_ok=True)
    tmp_spec.write_text(
        f"# Auto-heal spec for {file_path}\n\n## Intent\n{intent}\n\n"
        f"## Target\n`{file_path}`\n\n## Constraint\nPreserve all existing behaviour. "
        f"Only apply the minimal change described in the intent.",
        encoding="utf-8",
    )
    result = _execute_factory_cmd(
        "implement", str(tmp_spec.relative_to(_ROOT)))
    result["self_healed"] = True
    return result


# ---------------------------------------------------------------------------
# Task executor
# ---------------------------------------------------------------------------

def _execute_patch_component(args: dict) -> dict:
    """Executes a patch_component task using ast_patcher."""
    file_path = args.get("file", "")
    search_block = args.get("search", "")
    replace_block = args.get("replace", "")

    if not all([file_path, search_block, replace_block]):
        return {
            "tool": "patch_component",
            "success": False,
            "summary": "❌ [patch_component] Missing required args: file, search, replace",
            "error_output": f"Got: {args}",
        }

    ok = apply_patch(file_path, search_block, replace_block)
    return {
        "tool": "patch_component",
        "args": file_path,
        "success": ok,
        "summary": f"{'✅' if ok else '❌'} [patch_component] {Path(file_path).name}",
        "error_output": "" if ok else f"Anchor not found in {file_path}",
    }


def _execute_factory_cmd(tool: str, args: str) -> dict:
    """Runs a factory.py command (implement, synthesize, ui_validate)."""
    py = sys.executable
    factory = [py, str(_ROOT / "factory.py")]

    cmd_map = {
        "implement":  factory + ["build", args] if args else None,
        "synthesize": factory + ["synthesize", args] if args else None,
        "ui_validate": factory + ["ui_validate"] + (["--no-build"] if args == "--no-build" else []),
    }

    cmd = cmd_map.get(tool)
    if cmd is None:
        return {
            "tool": tool, "args": args, "success": False,
            "summary": f"⚠️  [{tool}] No command available",
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

def run_frontend_swarm(intent_spec: str, task_name: str = "frontend-task") -> dict:
    """
    Executes a localized frontend sub-swarm for the given intent.

    Called by nexus.py when the Chief routes a 'delegate_frontend' task.

    Args:
        intent_spec: High-level spec/intent string (e.g., the content of a spec
                     file, or a plain-English instruction for a surgical patch).
        task_name:   Slug used for the Kanban board branch label.

    Returns:
        {
            "success": bool,
            "tasks_run": int,
            "failures": list[dict],
            "summary": str,
        }
    """
    print(f"\n   🎨 [FRONTEND MANAGER] Planning sub-swarm for intent...")
    print(f"   {intent_spec[:120]}{'...' if len(intent_spec) > 120 else ''}")
    update_kanban(
        task_name, intent_spec[:80], "⏳ State 1: Frontend Manager activated — planning sub-swarm...")

    queue = _plan_frontend_queue(intent_spec)
    if not queue:
        update_kanban(
            task_name, intent_spec[:80], "❌ LLM returned empty queue — sub-swarm aborted.")
        return {
            "success": False,
            "tasks_run": 0,
            "failures": [],
            "summary": "❌ [FRONTEND MANAGER] LLM returned empty queue.",
        }

    print(f"   ⚡ Frontend sub-swarm: {len(queue)} task(s) queued")
    update_kanban(
        task_name, intent_spec[:80], f"🛠️ State 2: Executing {len(queue)} frontend task(s)...")

    failures: list[dict] = []
    tasks_run = 0

    for task in queue:
        tool = task.get("tool", "")
        args = task.get("args", "")
        print(f"\n   → [{tool.upper()}] {str(args)[:80]}")
        update_kanban(task_name, str(args)[
                      :60], f"⚙️  Step {tasks_run + 1}/{len(queue)}: [{tool.upper()}] running...")

        if tool == "patch_component":
            # args can be a dict (from JSON queue) or string
            patch_args = args if isinstance(args, dict) else {}
            result = _execute_patch_component(patch_args)
        else:
            str_args = args if isinstance(args, str) else str(args)
            result = _execute_factory_cmd(tool, str_args)

        print(f"   {result['summary']}")
        tasks_run += 1

        if not result.get("success", False):
            # ── Self-healing: anchor miss → reattempt on the spot ─────────────
            if (tool == "patch_component"
                    and "Anchor not found" in result.get("error_output", "")):
                print(
                    f"   🩹 [self-heal] Anchor miss detected — attempting in-place recovery...")
                update_kanban(task_name, str(args)[:60],
                              f"🩹 Step {tasks_run}: Anchor miss — self-healing patch...")
                patch_args = args if isinstance(args, dict) else {}
                healed = _self_heal_patch_component(
                    file_path=patch_args.get("file", ""),
                    intent=intent_spec,
                    original_search=patch_args.get("search", ""),
                    original_replace=patch_args.get("replace", ""),
                )
                if healed.get("success"):
                    print(
                        f"   ✅ [self-heal] Recovered — continuing sub-swarm.")
                    update_kanban(task_name, str(args)[:60],
                                  f"✅ Step {tasks_run}: Self-heal succeeded — resuming.")
                    result = healed  # swap in the successful result and continue

            if not result.get("success", False):
                failures.append(result)
                update_kanban(task_name, str(args)[
                              :60], f"🚨 Step {tasks_run} FAILED — sub-swarm halted. Operator review required.")
                # Stop on first unrecoverable failure — don't validate broken code
                print(
                    f"   ⛔ Frontend sub-swarm halted at step {tasks_run} due to failure.")
                break

    ok = len(failures) == 0
    summary = (
        f"✅ [FRONTEND MANAGER] {tasks_run} task(s) completed successfully."
        if ok
        else f"❌ [FRONTEND MANAGER] {len(failures)} failure(s) in {tasks_run} task(s)."
    )
    print(f"\n   {summary}")
    if ok:
        update_kanban(
            task_name, intent_spec[:80], f"✅ State 6: All {tasks_run} task(s) complete — awaiting Operator review gate.")
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
        _sys.argv) > 1 else "Add 300ms debounce to GlobalSearch input"
    result = run_frontend_swarm(intent)
    print(f"\nResult: {json.dumps(result, indent=2)}")
