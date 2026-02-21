#!/usr/bin/env python3
"""
THE CHIEF: PROJECT NEXUS â nexus.py  (v4.2 â Level 6 Edition)
============================================================
Massively Parallel AI Engineering Console for the Dark Factory.

v4.2 changes:
  â¢ mentor_insight from Chief is now displayed after every briefing.
  â¢ fitness tool added to action map with proper icon.
  â¢ Version aligned with project v9.7.6.

Features:
  â¢ Chief now outputs a TASK QUEUE instead of a single action.
  â¢ Independent tasks run in PARALLEL via ThreadPoolExecutor.
  â¢ Sequential barriers (commit, heal, build) wait for all parallel
    tasks before executing.

Start with:
    python nexus.py
"""

import sys
import subprocess
import os
import time
import textwrap
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Bio-Swarm: record session start time so Mutation Engine only analyses
# logs from the current session (not all historical logs).
_SESSION_START_TS: float = time.time()

# Anti-Loop Circuit Breaker — stores the last Senior Architect mandate.
# Set by the escalate_to_senior handler; injected into the next Chief consult.
_last_senior_mandate: str = ""

# Level 8 — ReAct mode flag (set by --react CLI flag in main())
_REACT_MODE: bool = False

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass  # dotenv optional; set env vars manually if needed

# ---------------------------------------------------------------------------
# ANSI colours & styling
# ---------------------------------------------------------------------------
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

ROOT = Path(__file__).resolve().parent
_FACTORY_DIR = ROOT / "backend" / "factory"


# ---------------------------------------------------------------------------
# Janitor — lazy import so nexus.py loads even without the factory package
# ---------------------------------------------------------------------------

def _metabolic_flush() -> None:
    """Call janitor_agent.metabolic_flush() if the module is available."""
    try:
        if str(_FACTORY_DIR) not in sys.path:
            sys.path.insert(0, str(_FACTORY_DIR))
        from janitor_agent import metabolic_flush  # noqa: PLC0415
        metabolic_flush(silent=False)
    except Exception as exc:  # noqa: BLE001
        print(f"{DIM}⚠️  Metabolic flush skipped: {exc}{RESET}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_box(text: str, color: str = CYAN) -> None:
    """Prints text wrapped inside a Unicode box."""
    lines = textwrap.wrap(text, width=70)
    print(color + "â" + "â" * 72 + "â")
    for line in lines:
        print(f"â {line:<70} â")
    print("â" + "â" * 72 + "â" + RESET)


def type_writer(text: str, speed: float = 0.006) -> None:
    """Character-by-character print for an 'AI thinking' effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()


def hr() -> None:
    print(f"{DIM}{'â' * 52}{RESET}")


def print_header() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{CYAN}{BOLD}")
    print("ââââââââââââââââââââââââââââââââââââââââââââââââ")
    print("â   THE CHIEF â PROJECT NEXUS  v4.2            â")
    print("â   Chief Edition Â· Dark Factory Â· v9.7.4     â")
    print("ââââââââââââââââââââââââââââââââââââââââââââââââ")
    print(RESET)


# ---------------------------------------------------------------------------
# Senior Tech Lead helpers
# ---------------------------------------------------------------------------

def _get_senior_insight() -> str:
    """
    Calls the Tech Lead Agent's fast heuristics scan and returns a compact
    findings string to inject into the Chief's planning context.

    Never raises — returns an empty string on failure so we degrade gracefully.
    """
    try:
        sys.path.insert(0, str(ROOT / "backend" / "factory"))
        from tech_lead_agent import get_insights_for_chief  # noqa: PLC0415
        return get_insights_for_chief(include_stubs=True)
    except Exception as exc:
        return f"(Senior scan unavailable: {exc})"


def _call_death_loop_diagnosis(failed_intent: str, attempts: int) -> str:
    """
    🚨 ANTI-LOOP CIRCUIT BREAKER — calls the On-Call Senior Architect.

    Reads crash logs + kanban, asks the LLM for a different strategy,
    prints the mandate in bright red/yellow, and returns it for injection
    into the Chief's context as a SYSTEM_OVERRIDE.

    Never raises — falls back to a hard-coded rebuild mandate.
    """
    print(
        f"\n{RED}{BOLD}"
        f"🚨 DEATH LOOP DETECTED ({attempts} consecutive failures)"
        f"{RESET}"
    )
    print(
        f"{YELLOW}   Summoning On-Call Senior Architect to break the loop..."
        f"{RESET}"
    )
    try:
        sys.path.insert(0, str(ROOT / "backend" / "factory"))
        from tech_lead_agent import diagnose_death_loop  # noqa: PLC0415
        mandate = diagnose_death_loop(
            failed_intent, previous_attempts=attempts)
    except Exception as exc:
        mandate = (
            f"SYSTEM OVERRIDE MANDATE: Senior diagnosis failed ({exc}). "
            f"Force-escalate: use 'sandbox' to REBUILD the blocked component "
            f"from scratch. Do NOT use patch_component. Intent: {failed_intent}"
        )

    print(f"\n{RED}{BOLD}{'=' * 62}{RESET}")
    print(f"{RED}{BOLD}🧠 SENIOR ARCHITECT OVERRIDE{RESET}")
    print(f"{RED}{BOLD}{'=' * 62}{RESET}")
    for line in mandate.splitlines():
        if "SYSTEM OVERRIDE MANDATE" in line:
            print(f"{YELLOW}{BOLD}  → {line}{RESET}")
        else:
            print(f"{MAGENTA}  {line}{RESET}")
    print(f"{RED}{BOLD}{'=' * 62}{RESET}\n")
    return mandate


def _detect_placeholder_files() -> list[str]:
    """
    Lightweight post-swarm stub detector.  Scans recently modified TS/TSX/PY
    files (last 5 minutes) for placeholder patterns and returns a list of
    plain-text issue strings.

    This catches cases where the Builder quietly returns stub code without
    raising a compile error — e.g. `export {};` or `<p>Placeholder…</p>`.
    """
    import time as _time
    import re as _re

    stub_patterns = [
        _re.compile(r'Placeholder for .* [Ii]mplementation'),
        _re.compile(r'<p>Placeholder'),
        _re.compile(r'// Implement .* here'),
    ]
    # A file that is ONLY `export {};` (possibly with whitespace/comments)
    only_export_empty = _re.compile(
        r"^\s*(//[^\n]*)?\s*export\s*\{\s*\}\s*;?\s*$", _re.DOTALL
    )

    cutoff = _time.time() - 300  # 5 minutes
    ignore_dirs = {".venv", "node_modules", "__pycache__", ".git"}
    search_roots = [ROOT / "frontend" / "src", ROOT / "backend"]
    issues: list[str] = []

    for root in search_roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if any(part in ignore_dirs for part in path.parts):
                continue
            if path.suffix not in (".ts", ".tsx", ".py") or not path.is_file():
                continue
            try:
                if path.stat().st_mtime < cutoff:
                    continue
                size = path.stat().st_size
            except OSError:
                continue

            rel = str(path.relative_to(ROOT))

            # Critically small (skip __init__ and d.ts)
            if size < 120 and path.name not in ("__init__.py", "vite-env.d.ts"):
                issues.append(
                    f"STUB_DETECTED: {rel} is only {size} bytes — likely an empty "
                    f"stub written by the Builder.\n"
                    f"  Fix: queue 'implement' for the spec that owns this file."
                )
                continue

            # Skip factory infrastructure files — they embed stub pattern strings
            # in their own source (e.g. tech_lead_agent defines stub regexes).
            _factory_skip = {
                "tech_lead_agent.py", "evolution_manager.py",
                "repair_service.py", "nexus.py",
            }
            if path.name in _factory_skip:
                continue

            # Content patterns
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            if only_export_empty.match(content):
                issues.append(
                    f"STUB_DETECTED: {rel} contains only `export {{}}` — "
                    f"the Builder generated an empty module.\n"
                    f"  Fix: queue 'implement' for the spec that owns this file."
                )
                continue

            for pat in stub_patterns:
                if pat.search(content):
                    issues.append(
                        f"STUB_DETECTED: placeholder pattern in {rel}.\n"
                        f"  Fix: queue 'implement' for the spec that owns this file."
                    )
                    break

    return issues


# ---------------------------------------------------------------------------
# Single-task factory executor (used by both sequential and parallel paths)
# ---------------------------------------------------------------------------

_ACTION_MAP = {
    "design":     ("build",      "ðï¸  ARCHITECT",      "Drafting new blueprints..."),
    "implement":  ("build",      "ð¨ BUILDER",         "Translating specs to code..."),
    "build":      ("build",      "âï¸  CONDUCTOR",      "Rebuilding the product catalog..."),
    "heal":       ("heal",       "ð WATCHDOG",        "Diagnosing and auto-repairing (up to 3 cycles)..."),
    "ui_validate": ("ui_validate", "ð¥ï¸  UI VALIDATOR",   "Scanning imports + Vite build check..."),
    "diagnose":   ("diagnose",   "ð WATCHDOG SCAN",   "Scanning for errors â no auto-fix..."),
    "sandbox":    ("sandbox",    "ðï¸  SANDBOX",        "Inner-loop: generate â tsc/lint/vite â self-heal (5 rounds)..."),
    "steer":      ("steer",      "ð§­ STRATEGIST",      "Analysing master plan..."),
    "doc":        ("doc",        "ð SCRIBE",          "Regenerating ARCHITECTURE.md..."),
    "optimize":   ("optimize",   "â¨ OPTIMIZER",        "Refactoring file..."),
    "commit":     ("commit",     "ð® REPO AGENT",      "Staging and committing progress..."),
    "reflect":    ("reflect",    "ð§  MENTOR",          "Extracting lesson â updating LEARNED_GUIDELINES.md..."),
    "task_force": ("task_force", "âï¸  TASK FORCE",     "Assembling multi-agent Task Force (SteererâBuilderâWatchdog)..."),
    "v0_design":  ("v0_design",  "ð¨ V0 DESIGNER",    "Generating v0.dev prompt or integrating v0 output..."),
    "scout":      ("scout",      "ð­ SCOUT",           "Scanning for new tools â writing Evolution Proposals..."),
    "synthesize": ("synthesize", "ð§¬ RIBOSOME",       "Translating Genome â Synthesis Directive (protein folding)..."),
    "mutate":     ("mutate",     "ð§« MUTATION ENGINE", "Analysing fitness logs â evolving agent DNA..."),
    "fitness":    ("fitness",    "ð FITNESS LEDGER",  "Printing per-agent fitness scores and generation counts..."),
    "repair":     ("repair",     "🛠️  REPAIR SERVICE", "Running immune-response pipeline: import fixer → tsc → lint → vite → janitor..."),    "audit":      ("audit",     "🔍 TECH LEAD AUDIT", "Summoning Principal Engineer — running fresh heuristic scan → DAILY_BRIEFING.md..."),
    "delegate_frontend": ("delegate_frontend", "🎨 FRONTEND MANAGER", "Routing to React/Tailwind/Vite sub-swarm..."),
    "delegate_data":     ("delegate_data",     "🔧 DATA MANAGER",    "Routing to Python/FastAPI/pipeline sub-swarm..."),
    "escalate_to_senior": ("escalate_to_senior", "🚨 SENIOR ARCHITECT", "Circuit-breaker: On-Call Senior diagnoses death loop → prescribes new strategy..."),
    # Level 8 — Liquid MCP Core (can be scheduled directly by the Chief or used inside react_loop)
    "run_frontend_tests":    ("run_frontend_tests",    "🧪 VITEST",           "Running Vitest suite — returning raw terminal output..."),
    "git_isolate_workspace": ("git_isolate_workspace", "🌿 GIT ISOLATE",      "Creating AI feature branch before any edit..."),
    "git_merge_workspace":   ("git_merge_workspace",   "🔀 GIT MERGE",        "Merging or rolling back feature branch..."),
    "execute_bash":          ("execute_bash",          "💻 BASH",             "Executing shell command and returning stdout + stderr..."),
    "apply_patch":           ("apply_patch",           "🩹 UDIFF PATCHER",    "Applying SEARCH/REPLACE or unified diff patch to file..."),
}


def _build_cmd(tool: str, args: str) -> list[str] | None:
    """Return the factory.py command list, or None if not dispatchable."""
    py = sys.executable
    factory = [py, str(ROOT / "factory.py")]

    if tool == "design":
        return factory + ["design", args] if args else None
    if tool == "implement":
        return factory + ["build", args] if args else None
    if tool == "sandbox":
        # Sandbox makeover: autonomous inner_loop build with full verification
        # Same as 'implement' but signals the Chief's intent to force clean builds
        return factory + ["build", args] if args else None
    if tool in ("build",):
        return factory + ["build"]
    if tool == "heal":
        return factory + ["heal"]
    if tool == "ui_validate":
        return factory + ["ui_validate"] + (["--no-build"] if args == "--no-build" else [])
    if tool == "diagnose":
        return factory + ["diagnose"]
    if tool == "steer":
        return factory + ["steer"]
    if tool == "doc":
        return factory + ["doc"]
    if tool == "optimize":
        return factory + ["optimize", args] if args else None
    if tool == "commit":
        return factory + ["commit"]
    if tool == "reflect":
        return factory + ["reflect", args] if args else factory + ["reflect", "(no context provided)"]
    if tool == "task_force":
        # task has extra keys: id, goal, agents
        # args carries the goal; use tool-level dict keys if available
        return None  # handled by execute_task_force() below
    if tool == "v0_design":
        return factory + ["v0_design", args] if args else None
    if tool == "scout":
        return factory + ["scout"]
    if tool == "synthesize":
        return factory + ["synthesize", args] if args else None
    if tool == "mutate":
        return factory + ["mutate"] + (["--force"] if args == "--force" else [])
    if tool == "audit":
        return None  # handled inline in execute_sequential / run_process
    if tool == "fitness":
        return factory + ["fitness"]
    if tool == "repair":
        cmd = factory + ["repair"]
        if args:
            if args.startswith("--"):
                cmd.append(args)
            else:
                cmd += ["--target", args]
        return cmd
    return None  # 'explain' or unknown


def _build_task_force_cmd(task: dict) -> list[str] | None:
    """Build a factory.py task_force command from a task-force queue item."""
    py = sys.executable
    factory = [py, str(ROOT / "factory.py")]
    tf_id = task.get("id", "")
    goal = task.get("goal", task.get("args", ""))
    agents = ",".join(task.get("agents", ["steerer", "builder", "watchdog"]))
    if not tf_id or not goal:
        return None
    return factory + ["task_force", tf_id, goal, agents]


def run_process(task: dict) -> dict:
    """
    Executes a single factory command in a subprocess.
    Captures output to avoid terminal interleaving (used in parallel batches).
    Returns a result dict: {tool, args, success, summary, error_output}
    """
    tool = task["tool"]
    args = task.get("args", "")
    # --- Inline audit handler (parallel/batch path) ---
    if tool == "audit":
        sys.path.insert(0, str(ROOT / "backend" / "factory"))
        try:
            from tech_lead_agent import generate_morning_briefing  # noqa: PLC0415
            generate_morning_briefing()
            return {"tool": tool, "args": args, "success": True,
                    "summary": "✅ [AUDIT] DAILY_BRIEFING.md refreshed by Tech Lead.",
                    "error_output": ""}
        except Exception as exc:
            return {"tool": tool, "args": args, "success": False,
                    "summary": f"❌ [AUDIT] Tech Lead Agent failed: {exc}",
                    "error_output": str(exc)}

    # --- Anti-Loop Circuit Breaker: escalate_to_senior (parallel/batch path) ---
    if tool == "escalate_to_senior":
        global _last_senior_mandate
        mandate = _call_death_loop_diagnosis(
            str(args) or "unknown intent", attempts=1)
        _last_senior_mandate = mandate
        return {"tool": tool, "args": args, "success": True,
                "summary": "✅ [SENIOR ARCHITECT] Mandate issued — Chief will receive SYSTEM_OVERRIDE.",
                "error_output": ""}

    # --- Level 8 direct MCP tool dispatch (parallel/batch path) ---
    if tool in ("run_frontend_tests", "execute_bash", "apply_patch",
                "git_isolate_workspace", "git_merge_workspace"):
        _mcp = _load_mcp_handlers()
        _mcp_name = {
            "run_frontend_tests":    "run_frontend_tests",
            "execute_bash":          "execute_bash_command",
            "apply_patch":           "apply_udiff_patch",
            "git_isolate_workspace": "git_isolate_workspace",
            "git_merge_workspace":   "git_merge_workspace",
        }[tool]
        _handler = _mcp.get(_mcp_name)
        if _handler is None:
            return {"tool": tool, "args": args, "success": False,
                    "summary": f"❌ [{tool.upper()}] MCP handler not found.",
                    "error_output": "MCP server could not be loaded."}
        try:
            import json as _j
            # args is a plain string from the queue — parse as JSON dict if possible
            _tool_args = _j.loads(args) if isinstance(args, str) and args.startswith("{") else {
                "command": args} if tool == "execute_bash" else {"task_name": args} if tool == "git_isolate_workspace" else {}
            out = _handler(_tool_args)
            success = True
            if isinstance(out, str):
                try:
                    _parsed = _j.loads(out)
                    success = _parsed.get("success", True) if isinstance(
                        _parsed, dict) else True
                    if "exit_code" in _parsed:
                        success = _parsed["exit_code"] == 0
                except Exception:
                    pass
            return {"tool": tool, "args": args, "success": success,
                    "summary": f"[{tool.upper()}] {chr(0x2705) if success else chr(0x274c)} {str(out)[:200]}",
                    "error_output": str(out) if not success else ""}
        except Exception as exc:
            return {"tool": tool, "args": args, "success": False,
                    "summary": f"\u274c [{tool.upper()}] {exc}", "error_output": str(exc)}

    # --- Hierarchical Sub-Swarm delegation (parallel/batch path) ---
    if tool == "delegate_frontend":
        if _REACT_MODE:
            result = react_loop(args)
            return {
                "tool": tool, "args": args,
                "success": result["success"],
                "summary": result["summary"],
                "error_output": "" if result["success"] else result["summary"],
            }
        sys.path.insert(0, str(ROOT / "backend" / "factory"))
        try:
            from frontend_manager import run_frontend_swarm  # noqa: PLC0415
            import re as _re
            task_slug = _re.sub(
                r"[^\w]+", "-", args[:40].lower()).strip("-") or "frontend-task"
            result = run_frontend_swarm(args, task_name=task_slug)
            return {
                "tool": tool, "args": args,
                "success": result.get("success", False),
                "summary": result.get("summary", ""),
                "error_output": str(result.get("failures", [])) if result.get("failures") else "",
            }
        except Exception as exc:
            return {"tool": tool, "args": args, "success": False,
                    "summary": f"❌ [DELEGATE_FRONTEND] Frontend Manager crashed: {exc}",
                    "error_output": str(exc)}

    # ── Evolution Proposal intercept ──────────────────────────────────────────
    # Code-level guard: if the LLM queues ANY tool on a proposal file path,
    # silently route it to the deterministic evolution_manager instead.
    import re as _evo_re
    if tool in ("delegate_data", "delegate_frontend", "implement") and isinstance(args, str):
        _evo_m = _evo_re.search(
            r"(\d{4}-\d{2}-\d{2}_proposal_[\w\-]+\.md)", args)
        if _evo_m:
            _prop_rel = "specs/strategy/evolution/" + _evo_m.group(1)
            print("\n" + YELLOW + "\U0001f500 [ROUTER] Intercepted '" + tool + "' on evolution proposal "
                  "-> redirecting to evolution_manager" + RESET)
            sys.path.insert(0, str(ROOT))
            try:
                from backend.factory.evolution_manager import process_proposal  # noqa: PLC0415
                _er = process_proposal(_prop_rel)
                _v = _er.get("verdict", "?")
                _rs = _er.get("reason", "")
                return {
                    "tool": "process_evolution_proposal", "args": _prop_rel,
                    "success": True,
                    "summary": "[EVOLUTION MANAGER] " + _v + ": " + _rs,
                    "error_output": "", "evolution_result": _er,
                }
            except Exception as _eex:
                return {"tool": tool, "args": args, "success": False,
                        "summary": "[EVOLUTION MANAGER] intercept failed: " + str(_eex),
                        "error_output": str(_eex)}

    if tool == "delegate_data":
        if _REACT_MODE:
            result = react_loop(args)
            return {
                "tool": tool, "args": args,
                "success": result["success"],
                "summary": result["summary"],
                "error_output": "" if result["success"] else result["summary"],
            }
        sys.path.insert(0, str(ROOT / "backend" / "factory"))
        try:
            from data_manager import run_data_swarm  # noqa: PLC0415
            result = run_data_swarm(args)
            return {
                "tool": tool, "args": args,
                "success": result.get("success", False),
                "summary": result.get("summary", ""),
                "error_output": str(result.get("failures", [])) if result.get("failures") else "",
            }
        except Exception as exc:
            return {"tool": tool, "args": args, "success": False,
                    "summary": f"❌ [DELEGATE_DATA] Data Manager crashed: {exc}",
                    "error_output": str(exc)}
    # Pre-flight: verify the file exists before dispatching optimize
    if tool == "optimize" and args:
        target_path = ROOT / args
        if not target_path.exists():
            msg = (f"â [OPTIMIZE] Skipped â file does not exist: {args}\n"
                   f"   The Chief hallucinated this path. Only optimize real files.")
            return {"tool": tool, "args": args, "success": False,
                    "summary": f"â [OPTIMIZE {args}] File not found â skipped",
                    "error_output": msg}

    # task_force uses a special command builder
    if tool == "task_force":
        cmd = _build_task_force_cmd(task)
    else:
        cmd = _build_cmd(tool, args)
    if cmd is None:
        return {"tool": tool, "args": args, "success": True,
                "summary": f"{DIM}[{tool.upper()}] No command dispatched (explain/none).{RESET}",
                "error_output": ""}

    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = round(time.time() - start_time, 2)
        success = result.returncode == 0
        label = f"{tool.upper()} {args}".strip()
        status = "â" if success else "â"
        # Combine stdout+stderr for failure context (last 40 lines avoids noise)
        combined = (result.stdout + "\n" + result.stderr).strip()
        tail = "\n".join(combined.splitlines()[-40:]) if combined else ""
        return {
            "tool": tool,
            "args": args,
            "success": success,
            "summary": f"{status} [{label}] ({duration}s)",
            "error_output": tail if not success else "",
        }
    except Exception as e:
        return {"tool": tool, "args": args, "success": False,
                "summary": f"â [{tool.upper()}] Exception: {e}",
                "error_output": str(e)}


def execute_sequential(task: dict) -> dict:
    """Run a single task interactively (output streams to terminal).
    Returns a result dict: {tool, args, success, summary, error_output}
    """
    tool = task["tool"]
    args = task.get("args", "")

    info = _ACTION_MAP.get(tool)
    if info:
        _, icon, label = info
        print(f"\n{MAGENTA}{BOLD}{icon} AGENT ACTIVATED{RESET}")
        print(f"   {label}")
        if args and tool not in ("task_force",):
            print(f"   Target: {args}")
        if tool == "task_force":
            goal = task.get("goal", args)
            tf_agents = task.get("agents", ["steerer", "builder", "watchdog"])
            print(f"   ID     : {task.get('id', 'auto')}")
            print(f"   Goal   : {goal}")
            print(f"   Agents : {', '.join(tf_agents)}")

    # Pre-flight: verify the file exists before dispatching optimize
    if tool == "optimize" and args:
        target_path = ROOT / args
        if not target_path.exists():
            print(f"\nâ [OPTIMIZE] File not found â skipped: {args}")
            print(f"   The Chief hallucinated this path. Only optimize real files.")
            return {"tool": tool, "args": args, "success": False,
                    "summary": f"â [OPTIMIZE {args}] File not found â skipped",
                    "error_output": f"File does not exist: {args}"}
    # --- Inline audit handler: summon Tech Lead, regenerate DAILY_BRIEFING.md ---
    if tool == "audit":
        sys.path.insert(0, str(ROOT / "backend" / "factory"))
        try:
            from tech_lead_agent import generate_morning_briefing  # noqa: PLC0415
            generate_morning_briefing()
            print(
                f"\n{GREEN}✅ [AUDIT] DAILY_BRIEFING.md regenerated — Chief will re-read priorities on next turn.{RESET}")
            return {"tool": tool, "args": args, "success": True,
                    "summary": "✅ [AUDIT] Tech Lead briefing updated — DAILY_BRIEFING.md refreshed.",
                    "error_output": ""}
        except Exception as exc:
            msg = f"❌ [AUDIT] Tech Lead Agent failed: {exc}"
            print(f"\n{RED}{msg}{RESET}")
            return {"tool": tool, "args": args, "success": False,
                    "summary": msg, "error_output": str(exc)}

    # --- Anti-Loop Circuit Breaker: escalate_to_senior (interactive path) ---
    if tool == "escalate_to_senior":
        global _last_senior_mandate
        mandate = _call_death_loop_diagnosis(
            str(args) or "unknown intent", attempts=1)
        _last_senior_mandate = mandate
        print(
            f"\n{GREEN}✅ [SENIOR ARCHITECT] Mandate stored — injecting into Chief on next turn.{RESET}")
        return {"tool": tool, "args": args, "success": True,
                "summary": "✅ [SENIOR ARCHITECT] Mandate issued — Chief receives SYSTEM_OVERRIDE next turn.",
                "error_output": ""}

    # --- Hierarchical Sub-Swarm delegation handlers ---
    if tool == "delegate_frontend":
        sys.path.insert(0, str(ROOT / "backend" / "factory"))
        try:
            from frontend_manager import run_frontend_swarm  # noqa: PLC0415
            import re as _re
            task_slug = _re.sub(
                r"[^\w]+", "-", args[:40].lower()).strip("-") or "frontend-task"
            result = run_frontend_swarm(args, task_name=task_slug)
            return {
                "tool": tool, "args": args,
                "success": result.get("success", False),
                "summary": result.get("summary", ""),
                "error_output": str(result.get("failures", [])) if result.get("failures") else "",
            }
        except Exception as exc:
            msg = f"❌ [DELEGATE_FRONTEND] Frontend Manager crashed: {exc}"
            print(f"\n{RED}{msg}{RESET}")
            return {"tool": tool, "args": args, "success": False,
                    "summary": msg, "error_output": str(exc)}

    # Code-level guard: if the LLM queues ANY tool on a proposal file path,
    # silently route it to the deterministic evolution_manager instead.
    import re as _evo_re
    if tool in ("delegate_data", "delegate_frontend", "implement") and isinstance(args, str):
        _evo_m = _evo_re.search(
            r"(\d{4}-\d{2}-\d{2}_proposal_[\w\-]+\.md)", args)
        if _evo_m:
            _prop_rel = "specs/strategy/evolution/" + _evo_m.group(1)
            print("\n" + YELLOW + "\U0001f500 [ROUTER] Intercepted '" + tool + "' on evolution proposal "
                  "-> redirecting to evolution_manager" + RESET)
            sys.path.insert(0, str(ROOT))
            try:
                from backend.factory.evolution_manager import process_proposal  # noqa: PLC0415
                _er = process_proposal(_prop_rel)
                _v = _er.get("verdict", "?")
                _rs = _er.get("reason", "")
                return {
                    "tool": "process_evolution_proposal", "args": _prop_rel,
                    "success": True,
                    "summary": "[EVOLUTION MANAGER] " + _v + ": " + _rs,
                    "error_output": "", "evolution_result": _er,
                }
            except Exception as _eex:
                return {"tool": tool, "args": args, "success": False,
                        "summary": "[EVOLUTION MANAGER] intercept failed: " + str(_eex),
                        "error_output": str(_eex)}

    if tool == "delegate_data":
        if _REACT_MODE:
            res = react_loop(args)
            return {
                "tool": tool, "args": args,
                "success": res["success"],
                "summary": res["summary"],
                "error_output": "" if res["success"] else res["summary"],
            }
        sys.path.insert(0, str(ROOT / "backend" / "factory"))
        try:
            from data_manager import run_data_swarm  # noqa: PLC0415
            result = run_data_swarm(args)
            return {
                "tool": tool, "args": args,
                "success": result.get("success", False),
                "summary": result.get("summary", ""),
                "error_output": str(result.get("failures", [])) if result.get("failures") else "",
            }
        except Exception as exc:
            msg = f"❌ [DELEGATE_DATA] Data Manager crashed: {exc}"
            print(f"\n{RED}{msg}{RESET}")
            return {"tool": tool, "args": args, "success": False,
                    "summary": msg, "error_output": str(exc)}

    # --- Level 8 direct MCP tool dispatch (interactive path) ---
    if tool in ("run_frontend_tests", "execute_bash", "apply_patch",
                "git_isolate_workspace", "git_merge_workspace"):
        import json as _ji
        _mcp2 = _load_mcp_handlers()
        _mcp_name2 = {
            "run_frontend_tests":    "run_frontend_tests",
            "execute_bash":          "execute_bash_command",
            "apply_patch":           "apply_udiff_patch",
            "git_isolate_workspace": "git_isolate_workspace",
            "git_merge_workspace":   "git_merge_workspace",
        }[tool]
        _handler2 = _mcp2.get(_mcp_name2)
        if _handler2 is None:
            print(
                f"\n{RED}\u274c [{tool.upper()}] MCP handler not found.{RESET}")
            return {"tool": tool, "args": args, "success": False,
                    "summary": f"\u274c [{tool.upper()}] MCP handler not found.",
                    "error_output": "MCP server could not be loaded."}
        try:
            _tool_args2 = (_ji.loads(args) if isinstance(args, str) and args.startswith("{")
                           else {"command": args} if tool == "execute_bash"
                           else {"task_name": args} if tool == "git_isolate_workspace"
                           else {})
            out2 = _handler2(_tool_args2)
            print(f"   {str(out2)[:400]}")
            success2 = True
            if isinstance(out2, str):
                try:
                    _p2 = _ji.loads(out2)
                    success2 = _p2.get("success", True) if isinstance(
                        _p2, dict) else True
                    if "exit_code" in _p2:
                        success2 = _p2["exit_code"] == 0
                except Exception:
                    pass
            _icon2 = "\u2705" if success2 else "\u274c"
            return {"tool": tool, "args": args, "success": success2,
                    "summary": f"[{tool.upper()}] {_icon2} {str(out2)[:200]}",
                    "error_output": str(out2) if not success2 else ""}
        except Exception as exc2:
            print(f"\n{RED}\u274c [{tool.upper()}] {exc2}{RESET}")
            return {"tool": tool, "args": args, "success": False,
                    "summary": f"\u274c [{tool.upper()}] {exc2}", "error_output": str(exc2)}

    cmd = _build_task_force_cmd(
        task) if tool == "task_force" else _build_cmd(tool, args)
    if cmd:
        # Stream stdout to terminal; capture stderr to detect failures
        proc = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
        if proc.stderr:
            # Print stderr so operator sees it
            sys.stderr.write(proc.stderr)
        success = proc.returncode == 0
        label = f"{tool.upper()} {args}".strip()
        return {
            "tool": tool, "args": args, "success": success,
            "summary": f"{'â' if success else 'â'} [{label}]",
            "error_output": "\n".join(proc.stderr.splitlines()[-40:]) if proc.stderr and not success else "",
        }
    else:
        print(f"  {DIM}(No factory dispatch for tool '{tool}'){RESET}")
        return {"tool": tool, "args": args, "success": True, "summary": f"[{tool}] skipped", "error_output": ""}


# ---------------------------------------------------------------------------
# Swarm execution engine
# ---------------------------------------------------------------------------
# HOTL Steering Gate
# ---------------------------------------------------------------------------

def review_changes(auto_mode: bool = False) -> bool:
    """
    Human-on-the-Loop gate: display modified files, let the Operator
    approve, inspect, or reject before the next task batch runs.

    Returns True  â changes accetd (and committed).
    Returns False â changes reverted via git restore.
    """
    # Quick-exit: no tracked changes means nothing to review
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True
    )
    if not status.stdout.strip():
        print(f"\n{DIM}â No working-tree changes detected â gate passed.{RESET}")
        return True

    print(f"\n{BOLD}{YELLOW}{'â' * 52}")
    print("ð  STEERING GATE â REVIEW MODIFICATIONS")
    print(f"{'â' * 52}{RESET}")
    subprocess.run(["git", "status", "-s"])

    if auto_mode:
        print(f"\n{CYAN}⚡ [AUTO] Changes auto-approved and committed.{RESET}")
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "config", "--local", "commit.gpgsign", "false"])
        r = subprocess.run([
            "git", "-c", "commit.gpgsign=false",
            "commit", "--no-gpg-sign", "-m", "chore: automated batch execution approved"
        ], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{RED}❌ Commit failed: {(r.stdout + r.stderr).strip()}{RESET}")
            return False
        _metabolic_flush()
        return True

    while True:
        try:
            decision = input(
                f"\n{BOLD}Approve changes? [{GREEN}Y{RESET}{BOLD}/n/diff/reject]{RESET}: "
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            decision = "n"

        if decision in ("", "y", "yes"):
            subprocess.run(["git", "add", "."])
            subprocess.run(["git", "config", "--local",
                           "commit.gpgsign", "false"])
            r = subprocess.run([
                "git", "-c", "commit.gpgsign=false",
                "commit", "--no-gpg-sign", "-m", "chore: automated batch execution approved"
            ], capture_output=True, text=True)
            if r.returncode != 0:
                err = (r.stdout + r.stderr).strip()
                print(f"{RED}❌ Commit failed:\n   {err}{RESET}")
                print(f"{YELLOW}↩  Reverting to avoid stuck state...{RESET}")
                subprocess.run(["git", "restore", "."])
                return False
            print(f"{GREEN}✅ Changes committed.{RESET}")
            _metabolic_flush()
            return True

        elif decision == "diff":
            subprocess.run(["git", "diff"])
            # Loop back to let the operator decide after reviewing the diff
            continue

        elif decision in ("n", "no", "reject"):
            print(f"{YELLOW}â©  Reverting all uncommitted changes...{RESET}")
            subprocess.run(["git", "restore", "."])
            subprocess.run(["git", "clean", "-fd"])
            print(f"{RED}â Changes rejected and reverted.{RESET}")
            return False

        else:
            print(f"{DIM}  Options: Y Â· n Â· diff Â· reject{RESET}")


# ---------------------------------------------------------------------------

def execute_swarm(queue: list[dict], auto_mode: bool = False) -> list[dict]:
    """
    Parallel Execution Engine.

    Strategy:
      â¢ Accumulate consecutive parallel=True tasks into a batch.
      â¢ When a parallel=False task appears (or queue ends), flush the batch
        via ThreadPoolExecutor, then run the sequential task interactively.
      â¢ After EVERY batch (parallel or sequential) the HOTL Steering Gate fires:
        the Operator can approve, inspect diff, or reject+revert before the
        next batch starts.

    Returns a list of failed task result dicts (empty if all succeeded).
    """
    print(f"\n{BOLD}ð MOBILIZING FACTORY SWARM...{RESET}")

    batch: list[dict] = []
    failures: list[dict] = []
    halted: list[bool] = [False]  # mutable flag accessible from closure

    def flush_batch() -> None:
        if halted[0] or not batch:
            return
        count = len(batch)
        print(
            f"\n{CYAN}â¡ Executing parallel batch ({count} agent{'s' if count > 1 else ''})...{RESET}")
        with ThreadPoolExecutor(max_workers=min(count, 8)) as executor:
            futures = {executor.submit(run_process, t): t for t in batch}
            for future in as_completed(futures):
                res = future.result()
                print(f"   {res['summary']}")
                if not res["success"]:
                    failures.append(res)
        batch.clear()
        # ââ HOTL STEERING GATE â fires after every parallel batch ââ
        if not auto_mode:
            approved = review_changes(auto_mode=False)
            if not approved:
                print(f"{RED}â Batch rejected by Operator. Halting queue.{RESET}")
                halted[0] = True

    for task in queue:
        if halted[0]:
            break
        if task.get("parallel", False):
            batch.append(task)
        else:
            flush_batch()
            if halted[0]:
                break
            print(
                f"\n{YELLOW}ð Sequential task: {task['tool']} {task.get('args', '')}...{RESET}")
            res = execute_sequential(task)
            if not res.get("success", True):
                failures.append(res)
            # ââ HOTL STEERING GATE â fires after every sequential task ââ
            if not auto_mode:
                approved = review_changes(auto_mode=False)
                if not approved:
                    print(
                        f"{RED}â Sequential task rejected by Operator. Halting queue.{RESET}")
                    halted[0] = True

    flush_batch()
    if halted[0]:
        print(f"\n{YELLOW}â¹  Swarm halted at Operator's Steering Gate.{RESET}")
    else:
        print(f"\n{GREEN}ð All objectives complete.{RESET}")
    return failures


# ---------------------------------------------------------------------------
# OODA Mutation Cycle â called automatically after every successful batch
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Level 8 — MCP handler loader (shared by react_loop and direct handlers)
# ---------------------------------------------------------------------------

def _load_mcp_handlers() -> dict:
    """
    Import the Level 8 MCP tool handlers from factory_mcp_server directly.
    Returns the _TOOL_HANDLERS dict, or {} if unavailable.
    """
    try:
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location(
            "factory_mcp_server",
            ROOT / "backend" / "mcp" / "servers" / "factory_mcp_server.py",
        )
        _mod = _ilu.module_from_spec(_spec)  # type: ignore[arg-type]
        _spec.loader.exec_module(_mod)  # type: ignore[union-attr]
        return _mod._TOOL_HANDLERS
    except Exception as exc:
        print(f"{DIM}⚠️  MCP handlers unavailable: {exc}{RESET}")
        return {}


# ---------------------------------------------------------------------------
# Level 8 — ReAct Core Runtime
# ---------------------------------------------------------------------------

_REACT_SYSTEM = """You are the LEVEL 8 CORE — a free-thinking engineering agent operating in a
ReAct (Reason → Act → Observe) loop. You have direct access to OS-level tools.
You work like a senior human developer: read the terminal, fix what's broken, verify, commit.

AVAILABLE TOOLS (call one per turn):
  run_frontend_tests    {"target_file": "<optional filename filter>"}
      → Runs Vitest and returns [PASS/FAIL] + raw terminal output.
  execute_bash_command  {"command": "<shell command>", "working_directory": "<optional path>"}
      → Executes any shell command. Returns {exit_code, stdout, stderr}.
  apply_udiff_patch     {"file_path": "<workspace-relative path>", "patch_text": "<SEARCH/REPLACE or unified diff>"}
      → Applies a surgical code patch. PREFERRED for all file edits.
  git_isolate_workspace {"task_name": "<slug>"}
      → Creates and checks out an AI feature branch. Returns branch name.
  git_merge_workspace   {"branch_name": "<branch>", "success_status": true|false}
      → Merges branch on success, rolls back on failure.
  read_file             {"path": "<workspace-relative path>"}
      → Reads a file from disk. Not a registered MCP tool — handled inline.

RULES:
- NEVER guess file contents — use read_file to read before patching.
- NEVER skip run_frontend_tests after every code change.
- Fix ONE issue per turn, then re-run tests to confirm before moving on.
- When tests are GREEN, call git_merge_workspace with success_status=true.
- If you exhaust max turns without green tests, call git_merge_workspace with success_status=false.

RESPONSE FORMAT (JSON only, no markdown — one action per response):
{
  "thought": "<your reasoning>",
  "action": "<tool_name or DONE>",
  "args": {<tool arguments as object>},
  "status": "WORKING | DONE | FAILED"
}
When status=DONE or status=FAILED, set action="DONE" and include "result" key with summary.
"""


def react_loop(goal: str, max_turns: int = 14) -> dict:
    """
    Level 8 Core Runtime: Reason → Act → Observe loop.

    The Chief LLM picks MCP tools turn-by-turn, reads real terminal output,
    and self-corrects — no middle-manager Python state machine required.

    Args:
        goal:      Plain-English task description (from the Operator).
        max_turns: Hard cap on iterations (default 14).

    Returns:
        {"success": bool, "summary": str, "turns": int}
    """
    import json as _json
    import re as _re

    # ── Load handlers ────────────────────────────────────────────────────────
    handlers = _load_mcp_handlers()
    if not handlers:
        return {
            "success": False,
            "summary": "❌ [REACT] MCP handlers could not be loaded. Falling back to manager.",
            "turns": 0,
        }

    # Inline read_file handler (not an MCP tool, but needed by the LLM)
    def _read_file(args: dict) -> str:
        p = ROOT / args.get("path", "")
        if not p.exists():
            return f"File not found: {args.get('path')}"
        try:
            return p.read_text(encoding="utf-8", errors="replace")[:8000]
        except Exception as exc:
            return f"Error reading file: {exc}"

    all_handlers = {**handlers, "read_file": _read_file}

    # ── Load LLM ─────────────────────────────────────────────────────────────
    try:
        sys.path.insert(0, str(ROOT / "backend" / "factory"))
        from agent_core import query_llm  # type: ignore
    except ImportError as exc:
        return {"success": False, "summary": f"❌ [REACT] agent_core unavailable: {exc}", "turns": 0}

    # ── ReAct loop ───────────────────────────────────────────────────────────
    history: list[str] = []
    branch: str = ""

    print(f"\n{CYAN}{BOLD}⚛️  REACT CORE ACTIVATED{RESET}")
    print(f"   Goal: {goal}")
    print(f"   Max turns: {max_turns}\n")

    for turn in range(1, max_turns + 1):
        history_block = "\n".join(history[-20:])  # cap context window
        user_prompt = (
            f"GOAL: {goal}\n\n"
            f"TURN: {turn}/{max_turns}\n\n"
            f"HISTORY (most recent last):\n{history_block or '(none yet)'}\n\n"
            "What is your next action? Respond with JSON only."
        )

        raw = query_llm(_REACT_SYSTEM, user_prompt,
                        temperature=0.2, model_tier="smart")
        if not raw:
            history.append(f"[T{turn}] LLM returned empty response.")
            continue

        # Strip any accidental markdown fence
        raw = raw.strip()
        raw = _re.sub(r"^```(?:json)?\s*", "", raw)
        raw = _re.sub(r"\s*```\s*$", "", raw)

        try:
            step = _json.loads(raw)
        except _json.JSONDecodeError:
            # Try to extract JSON from the raw output
            m = _re.search(r"\{.*\}", raw, _re.DOTALL)
            if m:
                try:
                    step = _json.loads(m.group(0))
                except Exception:
                    history.append(
                        f"[T{turn}] Could not parse JSON: {raw[:200]}")
                    continue
            else:
                history.append(f"[T{turn}] No JSON in response: {raw[:200]}")
                continue

        thought = step.get("thought", "")
        action = step.get("action", "")
        step_args = step.get("args", {})
        status = step.get("status", "WORKING")

        print(
            f"{DIM}[T{turn}] {BOLD}{action}{RESET}{DIM}  →  {thought[:100]}{RESET}")

        # ── Terminal condition ───────────────────────────────────────────────
        if action == "DONE" or status in ("DONE", "FAILED"):
            result_msg = step.get("result", thought)
            success = status != "FAILED"
            if branch and success:
                handlers.get("git_merge_workspace", lambda _: None)(
                    {"branch_name": branch, "success_status": True}
                )
            elif branch and not success:
                handlers.get("git_merge_workspace", lambda _: None)(
                    {"branch_name": branch, "success_status": False}
                )
            icon = "✅" if success else "❌"
            print(
                f"\n{GREEN if success else RED}{icon} [REACT] {result_msg}{RESET}")
            return {"success": success, "summary": f"{icon} [REACT] {result_msg}", "turns": turn}

        # ── Execute tool ─────────────────────────────────────────────────────
        handler = all_handlers.get(action)
        if handler is None:
            obs = f"Unknown tool: {action}. Available: {list(all_handlers.keys())}"
            print(f"   {YELLOW}⚠️  {obs}{RESET}")
        else:
            try:
                obs = handler(step_args)
                # Track branch name for auto-merge
                if action == "git_isolate_workspace":
                    try:
                        _br = _json.loads(obs).get("branch", "")
                        if _br:
                            branch = _br
                    except Exception:
                        pass
            except Exception as exc:
                obs = f"Tool error: {exc}"

        # Truncate very long observations to prevent context explosion
        obs_str = str(obs)
        if len(obs_str) > 3000:
            obs_str = obs_str[:1500] + \
                "\n... [truncated] ...\n" + obs_str[-600:]

        history.append(
            f"[T{turn}] ACTION={action} ARGS={step_args}\nOBSERVATION={obs_str}\n")

    # Max turns exceeded
    if branch:
        handlers.get("git_merge_workspace", lambda _: None)(
            {"branch_name": branch, "success_status": False}
        )
    summary = f"❌ [REACT] Goal not completed after {max_turns} turns: {goal[:80]}"
    print(f"\n{RED}{summary}{RESET}")
    return {"success": False, "summary": summary, "turns": max_turns}


def _run_ooda_mutation_cycle() -> None:
    """
    Bio-Swarm OODA hook: silently runs the Mutation Engine after each
    successful Swarm batch so the system evolves before going idle.

    Mutations are only applied when a fitness score drops below the threshold.
    The result is printed in a compact summary block.
    """
    try:
        sys.path.insert(0, str(ROOT / "backend" / "factory"))
        from mutation_engine import run_mutation_cycle  # noqa: PLC0415

        print(
            f"\n{DIM}\u2500 Bio-Swarm \u2500 running post-batch OODA cycle \u2500{RESET}")
        results = run_mutation_cycle(
            since_ts=_SESSION_START_TS,
            force_mutate=False,
            verbose=False,
        )
        if results:
            print(f"{MAGENTA}{BOLD}\ud83e\uddeb MUTATIONS APPLIED THIS BATCH:{RESET}")
            for r in results:
                print(
                    f"   \u2022 {BOLD}{r.agent}{RESET} \u2192 Gen {r.generation}  "
                    f"({r.target})  confidence={r.confidence}"
                )
                print(f"     Heuristic: {DIM}{r.heuristic[:100]}{RESET}")
        else:
            print(
                f"{DIM}   \u2713 All agents above fitness threshold. No mutations needed.{RESET}")
    except Exception as exc:
        # Never crash Nexus due to mutation engine error
        print(f"{DIM}   (OODA mutation cycle skipped: {exc}){RESET}")


# ---------------------------------------------------------------------------
# Main REPL
# ---------------------------------------------------------------------------

def main() -> None:
    # ---- CLI flags (Phase 4 â Auto-Pilot) ----------------------------------
    parser = argparse.ArgumentParser(
        prog="nexus.py",
        description="THE CHIEF: Project Nexus â Massively Parallel AI Engineering Console",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-Pilot: authorize every swarm plan without a Y/n prompt.",
    )
    parser.add_argument(
        "--react",
        action="store_true",
        help="Level 8 ReAct mode: delegate_frontend/data route through the ReAct Core (MCP tools) instead of sub-swarm managers.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Dry Run: show the Chief's plan but do NOT dispatch any tasks.",
    )
    parser.add_argument(
        "--briefing",
        action="store_true",
        help="Tech Lead morning audit: run heuristics scan, write DAILY_BRIEFING.md, and exit.",
    )
    parser.add_argument(
        "instruction",
        nargs="?",
        default="",
        help="Optional: initial instruction passed straight to the Chief.",
    )
    args = parser.parse_args()

    # ---- Tech Lead Briefing intercept (runs before any swarm logic) --------
    if args.briefing:
        sys.path.insert(0, str(ROOT / "backend" / "factory"))
        try:
            from tech_lead_agent import generate_morning_briefing  # noqa: PLC0415
        except ImportError as exc:
            print(f"{RED}Error: Could not load Tech Lead Agent â {exc}{RESET}")
            sys.exit(1)
        generate_morning_briefing()
        sys.exit(0)
    # ------------------------------------------------------------------------

    auto_mode: bool = args.auto
    dry_run: bool = args.dry_run

    # Level 8: engage ReAct Core Runtime if --react flag is set
    global _REACT_MODE, _last_senior_mandate
    _REACT_MODE = args.react
    if _REACT_MODE:
        print(
            f"{CYAN}{BOLD}⚛️  LEVEL 8 REACT MODE ENGAGED — delegates route through ReAct Core.{RESET}")

        print(
            f"{YELLOW}{BOLD}â¡ AUTO-PILOT ENGAGED â plans execute without confirmation.{RESET}")
    if dry_run:
        print(
            f"{CYAN}{BOLD}ð¤ DRY-RUN MODE â tasks will be printed but NOT executed.{RESET}")

    # Kill Switch â abort after this many consecutive failures
    KILL_SWITCH_THRESHOLD = 3
    consecutive_failures: int = 0

    # ---- Verify environment ------------------------------------------------
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print(f"{RED}{BOLD}CRITICAL:{RESET}{RED} Neither GEMINI_API_KEY nor "
              f"GOOGLE_API_KEY is set.{RESET}")
        print("  Export it or add it to your .env file, then run nexus.py again.")
        sys.exit(1)

    # ---- Load Chief Agent --------------------------------------------------
    sys.path.insert(0, str(ROOT / "backend" / "factory"))
    try:
        from chief_agent import consult_chief  # noqa: PLC0415
    except ImportError as exc:
        print(f"{RED}Error: Could not load Chief Agent â {exc}{RESET}")
        print("  Make sure backend/factory/chief_agent.py exists.")
        sys.exit(1)

    # ---- Startup -----------------------------------------------------------
    print_header()
    print(f"{BOLD}ð PROJECT NEXUS: SWARM EDITION ONLINE{RESET}")
    print("---------------------------------------")

    initial_input = args.instruction or ""
    # --- Senior Tech Lead pre-flight scan ---
    print(f"{DIM}\U0001f454  Senior Tech Lead scanning factory floor...{RESET}")
    _senior_context = _get_senior_insight()
    if _senior_context and "unavailable" not in _senior_context:
        print(f"\n{MAGENTA}\U0001f4cb SENIOR SCAN FINDINGS:{RESET}")
        for _line in _senior_context.splitlines():
            if _line.strip():
                print(f"   {DIM}{_line}{RESET}")
    plan = consult_chief(initial_input, is_startup=not bool(initial_input),
                         tech_lead_context=_senior_context)

    print(f"\n{GREEN}{BOLD}CHIEF'S BRIEFING:{RESET}")
    type_writer(plan.get("explanation", "(no explanation)"))
    mentor_insight = plan.get("mentor_insight", "")
    if mentor_insight:
        print(f"\n{MAGENTA}{BOLD}🎓 MENTOR INSIGHT:{RESET}")
        type_writer(mentor_insight, speed=0.004)
    proposal = plan.get("proposal", "")
    if proposal:
        print(f"\n{YELLOW}ð RECOMMENDATION: {proposal}{RESET}")

    hr()

    # ---- REPL loop ---------------------------------------------------------
    while True:
        try:
            # --- Display pending queue from last response ---
            queue = plan.get("queue", [])

            if queue:
                print(f"\n{YELLOW}ð ACTION PLAN:{RESET}")
                for i, task in enumerate(queue, 1):
                    mode = f"{CYAN}â¡ PARALLEL {RESET}" if task.get(
                        "parallel") else f"{YELLOW}ð SEQUENTIAL{RESET}"
                    args_label = task.get("args", "")
                    print(
                        f"   {i}. {mode} | {BOLD}{task['tool'].upper()}{RESET} {args_label}")

                # --- Auto-Pilot or interactive confirm ----------------------
                if dry_run:
                    print(
                        f"\n{CYAN}[DRY-RUN] Plan would execute {len(queue)} task(s). Not dispatching.{RESET}")
                    plan = {"queue": []}
                    hr()
                    # In dry-run, fall through to free-form prompt
                    try:
                        user_input = input(f"\n{BOLD}YOU > {RESET}").strip()
                    except (KeyboardInterrupt, EOFError):
                        break
                    if not user_input or user_input.lower() in ("exit", "quit", "q", ":q"):
                        break
                    print(f"\n{DIM}Chief is planning logistics...{RESET}")
                    _dr_mandate = _last_senior_mandate
                    _last_senior_mandate = ""
                    plan = consult_chief(user_input, is_startup=False,
                                         senior_override=_dr_mandate)
                    hr()
                    print(f"\n{GREEN}{BOLD}CHIEF >{RESET}")
                    type_writer(plan.get("explanation", "(no explanation)"))
                    hr()
                    continue

                if auto_mode:
                    confirm = "y"
                    print(
                        f"\n{CYAN}â¡ [AUTO] Executing {len(queue)} task(s)...{RESET}")
                else:
                    try:
                        confirm = input(
                            f"\n{CYAN}Authorize Swarm? [{BOLD}Y{RESET}{CYAN}/n] "
                            f"or type new instructions: {RESET}"
                        ).strip()
                    except (KeyboardInterrupt, EOFError):
                        break

                if confirm.lower() in ("exit", "quit", "q", ":q"):
                    break

                if confirm.lower() in ("", "y", "yes"):
                    failures = execute_swarm(queue, auto_mode=auto_mode)
                    plan = {"queue": []}
                    hr()

                    # --- Post-swarm: stub/placeholder detection ---
                    _stubs = _detect_placeholder_files()
                    if _stubs:
                        print(
                            f"\n{YELLOW}\u26a0\ufe0f  STUB DETECTOR: {len(_stubs)} placeholder file(s) found after swarm:{RESET}")
                        for _s in _stubs:
                            print(
                                f"   {RED}\u2022 {_s.splitlines()[0]}{RESET}")
                            if len(_s.splitlines()) > 1:
                                print(f"     {DIM}{_s.splitlines()[1]}{RESET}")
                        # Treat stubs as failures so the Chief auto-recovers
                        failures = failures + [
                            {"tool": "implement", "args": _stub_line.split(": ", 1)[1].split(" —")[0] if ": " in _stub_line else "unknown",
                             "success": False, "summary": f"\u26a0\ufe0f [STUB] {_stub_line.splitlines()[0]}", "error_output": _stub_line}
                            for _stub_line in _stubs
                        ]

                    # --- Post-swarm: auto-mode still needs a final gate pass ---
                    if not failures:
                        if auto_mode:
                            # In auto-mode the per-batch gates already auto-approved;
                            # run one final commit to lock the full swarm result.
                            review_changes(auto_mode=True)
                        consecutive_failures = 0
                        # ââ OODA MUTATION CYCLE (runs silently after each successful batch) ââ
                        _run_ooda_mutation_cycle()
                        continue
                    # --- Kill Switch: abort after N consecutive failures ---
                    if failures:
                        consecutive_failures += 1
                        if consecutive_failures >= KILL_SWITCH_THRESHOLD:
                            print(
                                f"\n{RED}{BOLD}ð KILL SWITCH TRIGGERED:{RESET}{RED} "
                                f"{consecutive_failures} consecutive failure batch(es). "
                                f"Halting Auto-Pilot to prevent runaway loops.{RESET}"
                            )
                            print(
                                f"  Last failures:\n"
                                + "\n".join(
                                    f"    â¢ {f['tool']} {f.get('args', '')}"
                                    for f in failures
                                )
                            )
                            # Log halt to file for post-mortem
                            try:
                                log_dir = ROOT / "factory_logs"
                                log_dir.mkdir(exist_ok=True)
                                import datetime as _dt
                                halt_log = log_dir / "autopilot_halt.log"
                                with open(halt_log, "a", encoding="utf-8") as _fh:
                                    _fh.write(
                                        f"\n[{_dt.datetime.now().isoformat()}] KILL SWITCH TRIGGERED\n"
                                        + "\n".join(
                                            f"  FAILED: {f['tool']} {f.get('args','')} â {f.get('error_output','')[:300]}"
                                            for f in failures
                                        ) + "\n"
                                    )
                                print(
                                    f"  {DIM}Halt logged to factory_logs/autopilot_halt.log{RESET}")
                            except Exception:
                                pass
                            if auto_mode:
                                print(
                                    f"  {DIM}Re-run without --auto or fix the errors, "
                                    f"then restart Nexus.{RESET}")
                                break
                            # In interactive mode, warn but allow continuation
                            print(
                                f"  {YELLOW}Manual override: type a new instruction to continue.{RESET}")
                            consecutive_failures = 0  # reset after warning in interactive

                        # --- Auto-recovery: feed failures back to Chief ---
                        failure_report = "\n".join(
                            f"FAILED: {f['tool']} {f.get('args', '')}\n{f.get('error_output', '')}"
                            for f in failures
                        )

                        # --- ANTI-LOOP: auto-escalate to Senior Architect at 2 failures ---
                        if consecutive_failures >= 2 and not _last_senior_mandate:
                            _loop_intent = (
                                str(failures[-1].get("args", "unknown"))
                                if failures else "unknown"
                            )
                            _last_senior_mandate = _call_death_loop_diagnosis(
                                _loop_intent, attempts=consecutive_failures
                            )

                        # Consume mandate — only injected once per loop cycle
                        _pending_override = _last_senior_mandate
                        _last_senior_mandate = ""

                        print(
                            f"\n{YELLOW}\U0001f504 Consulting Chief for recovery plan...{RESET}")
                        plan = consult_chief(
                            "", is_startup=False,
                            failure_context=failure_report,
                            tech_lead_context=_senior_context,
                            senior_override=_pending_override,
                        )
                        print(f"\n{RED}{BOLD}CHIEF RECOVERY PLAN:{RESET}")
                        type_writer(
                            plan.get("explanation", "(no explanation)"))
                        thought = plan.get("thought", "")
                        if thought:
                            print(f"  {DIM}[Reasoning: {thought}]{RESET}")
                        mentor_insight = plan.get("mentor_insight", "")
                        if mentor_insight:
                            print(
                                f"\n{MAGENTA}{BOLD}🎓 RECOVERY INSIGHT:{RESET}")
                            type_writer(mentor_insight, speed=0.004)
                        hr()

                    continue

                elif confirm.lower() in ("n", "no"):
                    print(f"  {DIM}Plan cancelled.{RESET}")
                    plan = {"queue": []}
                    hr()
                    continue

                else:
                    # User typed new instructions instead of Y/N
                    user_input = confirm

            else:
                # No pending queue â free-form input
                if auto_mode:
                    # Auto-Pilot with empty queue: nothing to do, exit gracefully
                    print(
                        f"\n{GREEN}â [AUTO] Queue exhausted. Nexus shutting down.{RESET}")
                    break
                try:
                    user_input = input(f"\n{BOLD}YOU > {RESET}").strip()
                except (KeyboardInterrupt, EOFError):
                    break

            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q", ":q"):
                break

            # ---- 'senior' shortcut: print Tech Lead report on demand ----
            if user_input.lower() in ("senior", "scan", "tech lead", "tl"):
                print(
                    f"\n{MAGENTA}\U0001f454 Requesting Senior Tech Lead Scan...{RESET}")
                _tl_report = _get_senior_insight()
                if _tl_report and "unavailable" not in _tl_report:
                    for _tl_line in _tl_report.splitlines():
                        print(f"   {_tl_line}")
                else:
                    print(
                        f"   {GREEN}\u2705 Factory is clean — no issues detected.{RESET}")
                hr()
                continue

            # ---- 'boardroom' shortcut: Advisory consultation (Boardroom Protocol) ----
            _consult_keywords = (
                "consult", "advise", "advice", "think about", "what do you think",
                "should we", "is this a good idea", "i'm thinking", "im thinking",
                "what do you reckon", "thoughts on", "opinion on",
            )
            _lower_input = user_input.lower()
            _is_advisory = (
                _lower_input in ("boardroom", "/boardroom",
                                 "consult", "/consult")
                or any(kw in _lower_input for kw in _consult_keywords)
            )
            if _is_advisory:
                print(
                    f"\n{MAGENTA}🏛️  BOARDROOM PROTOCOL ACTIVATED — entering consultation mode...{RESET}")
                try:
                    sys.path.insert(0, str(ROOT / "backend" / "factory"))
                    from tech_lead_agent import consult_tech_lead_on_idea  # type: ignore  # noqa: PLC0415
                    _tl_verdict = consult_tech_lead_on_idea(user_input)
                    # Chief adds strategic framing to the Tech Lead's verdict
                    _boardroom_prompt = (
                        f"The Operator has asked for advisory consultation (NOT execution) on:\n"
                        f"{user_input}\n\n"
                        f"The Senior Tech Lead has delivered this architectural verdict:\n"
                        f"{_tl_verdict}\n\n"
                        f"BOARDROOM ADVISORY MODE: Combine your strategic perspective with the Tech Lead's "
                        f"verdict and present a joint 'BOARDROOM ADVISORY REPORT'. "
                        f"DO NOT queue any tasks. DO NOT write code. End with a clear recommendation "
                        f"and ask the Governor whether to proceed or drop the idea."
                    )
                    _advisory_plan = consult_chief(
                        _boardroom_prompt, is_startup=False,
                        tech_lead_context="", senior_override=""  # context already injected above
                    )
                    print(
                        f"\n{BOLD}{MAGENTA}🏛️  BOARDROOM ADVISORY REPORT:{RESET}")
                    type_writer(_advisory_plan.get("explanation", _tl_verdict))
                    _boardroom_insight = _advisory_plan.get(
                        "mentor_insight", "")
                    if _boardroom_insight:
                        print(f"\n{MAGENTA}{BOLD}🎓 ARCHITECT'S NOTE:{RESET}")
                        type_writer(_boardroom_insight, speed=0.004)
                except Exception as _brd_exc:
                    print(f"   {RED}Boardroom unavailable: {_brd_exc}{RESET}")
                hr()
                continue

            # ---- 'pm' shortcut: Product Manager roadmap briefing --------------
            if user_input.lower() in ("pm", "/pm", "roadmap", "what's next", "whats next", "next"):
                print(
                    f"\n{MAGENTA}\U0001f454 Consulting Product Manager...{RESET}")
                try:
                    sys.path.insert(0, str(ROOT / "backend" / "factory"))
                    from product_manager import consult_product_manager  # type: ignore  # noqa: PLC0415
                    _pm_brief = consult_product_manager(user_input)
                    print(f"\n{BOLD}{_pm_brief}{RESET}")
                except Exception as _pm_exc:
                    print(f"   {RED}PM Agent error: {_pm_exc}{RESET}")
                hr()
                continue

            # Inject any pending Senior Architect mandate into context
            _pending_mandate = _last_senior_mandate
            _last_senior_mandate = ""  # consume immediately
            _fresh_senior = _get_senior_insight()
            plan = consult_chief(user_input, is_startup=False,
                                 tech_lead_context=_fresh_senior,
                                 senior_override=_pending_mandate)

            hr()
            print(f"\n{GREEN}{BOLD}CHIEF >{RESET}")
            type_writer(plan.get("explanation", "(no explanation)"))

            thought = plan.get("thought", "")
            if thought:
                print(f"  {DIM}[Reasoning: {thought}]{RESET}")
            mentor_insight = plan.get("mentor_insight", "")
            if mentor_insight:
                print(f"\n{MAGENTA}{BOLD}🎓 MENTOR INSIGHT:{RESET}")
                type_writer(mentor_insight, speed=0.004)
            next_proposal = plan.get("proposal", "")
            if next_proposal:
                print(f"\n{YELLOW}ð PROPOSAL: {next_proposal}{RESET}")

            hr()

        except (KeyboardInterrupt, EOFError):
            break

    print(f"\n{DIM}Nexus shutting down. Goodbye.{RESET}")


if __name__ == "__main__":
    main()
