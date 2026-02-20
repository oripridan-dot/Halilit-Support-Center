#!/usr/bin/env python3
"""
THE CHIEF: PROJECT NEXUS — nexus.py  (v4.0 — Chief Edition)
============================================================
Massively Parallel AI Engineering Console for the Dark Factory.

Features:
  • Chief now outputs a TASK QUEUE instead of a single action.
  • Independent tasks run in PARALLEL via ThreadPoolExecutor.
  • Sequential barriers (commit, heal, build) wait for all parallel
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_box(text: str, color: str = CYAN) -> None:
    """Prints text wrapped inside a Unicode box."""
    lines = textwrap.wrap(text, width=70)
    print(color + "┌" + "─" * 72 + "┐")
    for line in lines:
        print(f"│ {line:<70} │")
    print("└" + "─" * 72 + "┘" + RESET)


def type_writer(text: str, speed: float = 0.006) -> None:
    """Character-by-character print for an 'AI thinking' effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()


def hr() -> None:
    print(f"{DIM}{'─' * 52}{RESET}")


def print_header() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{CYAN}{BOLD}")
    print("╔══════════════════════════════════════════════╗")
    print("║   THE CHIEF — PROJECT NEXUS  v4.0            ║")
    print("║   Chief Edition · Dark Factory               ║")
    print("╚══════════════════════════════════════════════╝")
    print(RESET)


# ---------------------------------------------------------------------------
# Single-task factory executor (used by both sequential and parallel paths)
# ---------------------------------------------------------------------------

_ACTION_MAP = {
    "design":     ("build",      "🏗️  ARCHITECT",      "Drafting new blueprints..."),
    "implement":  ("build",      "🔨 BUILDER",         "Translating specs to code..."),
    "build":      ("build",      "⚙️  CONDUCTOR",      "Rebuilding the product catalog..."),
    "heal":       ("heal",       "🚑 WATCHDOG",        "Diagnosing and auto-repairing (up to 3 cycles)..."),
    "ui_validate": ("ui_validate", "🖥️  UI VALIDATOR",   "Scanning imports + Vite build check..."),
    "diagnose":   ("diagnose",   "🔍 WATCHDOG SCAN",   "Scanning for errors — no auto-fix..."),
    "steer":      ("steer",      "🧭 STRATEGIST",      "Analysing master plan..."),
    "doc":        ("doc",        "📝 SCRIBE",          "Regenerating ARCHITECTURE.md..."),
    "optimize":   ("optimize",   "✨ OPTIMIZER",        "Refactoring file..."),
    "commit":     ("commit",     "👮 REPO AGENT",      "Staging and committing progress..."),
    "reflect":    ("reflect",    "🧠 MENTOR",          "Extracting lesson → updating LEARNED_GUIDELINES.md..."),
    "task_force": ("task_force", "⚔️  TASK FORCE",     "Assembling multi-agent Task Force (Steerer→Builder→Watchdog)..."),
    "v0_design":  ("v0_design",  "🎨 V0 DESIGNER",    "Generating v0.dev prompt or integrating v0 output..."),
    "scout":      ("scout",      "🔭 SCOUT",           "Scanning for new tools → writing Evolution Proposals..."),
    "synthesize": ("synthesize", "🧬 RIBOSOME",       "Translating Genome → Synthesis Directive (protein folding)..."),
    "mutate":     ("mutate",     "🧫 MUTATION ENGINE", "Analysing fitness logs → evolving agent DNA..."),
    "fitness":    ("fitness",    "📊 FITNESS LEDGER", "Printing per-agent fitness scores and generation counts..."),
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
    if tool == "fitness":
        return factory + ["fitness"]
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

    # Pre-flight: verify the file exists before dispatching optimize
    if tool == "optimize" and args:
        target_path = ROOT / args
        if not target_path.exists():
            msg = (f"❌ [OPTIMIZE] Skipped — file does not exist: {args}\n"
                   f"   The Chief hallucinated this path. Only optimize real files.")
            return {"tool": tool, "args": args, "success": False,
                    "summary": f"❌ [OPTIMIZE {args}] File not found — skipped",
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
        status = "✅" if success else "❌"
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
                "summary": f"❌ [{tool.upper()}] Exception: {e}",
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
            print(f"\n❌ [OPTIMIZE] File not found — skipped: {args}")
            print(f"   The Chief hallucinated this path. Only optimize real files.")
            return {"tool": tool, "args": args, "success": False,
                    "summary": f"❌ [OPTIMIZE {args}] File not found — skipped",
                    "error_output": f"File does not exist: {args}"}

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
            "summary": f"{'✅' if success else '❌'} [{label}]",
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

    Returns True  → changes accepted (and committed).
    Returns False → changes reverted via git restore.
    """
    # Quick-exit: no tracked changes means nothing to review
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True
    )
    if not status.stdout.strip():
        print(f"\n{DIM}✔ No working-tree changes detected — gate passed.{RESET}")
        return True

    print(f"\n{BOLD}{YELLOW}{'─' * 52}")
    print("🛑  STEERING GATE — REVIEW MODIFICATIONS")
    print(f"{'─' * 52}{RESET}")
    subprocess.run(["git", "status", "-s"])

    if auto_mode:
        print(f"\n{CYAN}⚡ [AUTO] Changes auto-approved and committed.{RESET}")
        subprocess.run(["git", "add", "."])
        subprocess.run([
            "git", "commit", "-m",
            "chore: automated batch execution approved"
        ])
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
            subprocess.run([
                "git", "commit", "-m",
                "chore: automated batch execution approved"
            ])
            print(f"{GREEN}✅ Changes committed.{RESET}")
            return True

        elif decision == "diff":
            subprocess.run(["git", "diff"])
            # Loop back to let the operator decide after reviewing the diff
            continue

        elif decision in ("n", "no", "reject"):
            print(f"{YELLOW}↩  Reverting all uncommitted changes...{RESET}")
            subprocess.run(["git", "restore", "."])
            subprocess.run(["git", "clean", "-fd"])
            print(f"{RED}✖ Changes rejected and reverted.{RESET}")
            return False

        else:
            print(f"{DIM}  Options: Y · n · diff · reject{RESET}")


# ---------------------------------------------------------------------------

def execute_swarm(queue: list[dict]) -> list[dict]:
    """
    Parallel Execution Engine.

    Strategy:
      • Accumulate consecutive parallel=True tasks into a batch.
      • When a parallel=False task appears (or queue ends), flush the batch
        via ThreadPoolExecutor, then run the sequential task interactively.

    Returns a list of failed task result dicts (empty if all succeeded).
    """
    print(f"\n{BOLD}🚀 MOBILIZING FACTORY SWARM...{RESET}")

    batch: list[dict] = []
    failures: list[dict] = []

    def flush_batch() -> None:
        if not batch:
            return
        count = len(batch)
        print(
            f"\n{CYAN}⚡ Executing parallel batch ({count} agent{'s' if count > 1 else ''})...{RESET}")
        with ThreadPoolExecutor(max_workers=min(count, 8)) as executor:
            futures = {executor.submit(run_process, t): t for t in batch}
            for future in as_completed(futures):
                res = future.result()
                print(f"   {res['summary']}")
                if not res["success"]:
                    failures.append(res)
        batch.clear()

    for task in queue:
        if task.get("parallel", False):
            batch.append(task)
        else:
            flush_batch()
            print(
                f"\n{YELLOW}🔒 Sequential task: {task['tool']} {task.get('args', '')}...{RESET}")
            res = execute_sequential(task)
            if not res.get("success", True):
                failures.append(res)

    flush_batch()
    print(f"\n{GREEN}🏁 All objectives complete.{RESET}")
    return failures


# ---------------------------------------------------------------------------
# OODA Mutation Cycle — called automatically after every successful batch
# ---------------------------------------------------------------------------

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
    # ---- CLI flags (Phase 4 — Auto-Pilot) ----------------------------------
    parser = argparse.ArgumentParser(
        prog="nexus.py",
        description="THE CHIEF: Project Nexus — Massively Parallel AI Engineering Console",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-Pilot: authorize every swarm plan without a Y/n prompt.",
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
            print(f"{RED}Error: Could not load Tech Lead Agent — {exc}{RESET}")
            sys.exit(1)
        generate_morning_briefing()
        sys.exit(0)
    # ------------------------------------------------------------------------

    auto_mode: bool = args.auto
    dry_run: bool = args.dry_run

    if auto_mode:
        print(
            f"{YELLOW}{BOLD}⚡ AUTO-PILOT ENGAGED — plans execute without confirmation.{RESET}")
    if dry_run:
        print(
            f"{CYAN}{BOLD}💤 DRY-RUN MODE — tasks will be printed but NOT executed.{RESET}")

    # Kill Switch — abort after this many consecutive failures
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
        print(f"{RED}Error: Could not load Chief Agent — {exc}{RESET}")
        print("  Make sure backend/factory/chief_agent.py exists.")
        sys.exit(1)

    # ---- Startup -----------------------------------------------------------
    print_header()
    print(f"{BOLD}🔗 PROJECT NEXUS: SWARM EDITION ONLINE{RESET}")
    print("---------------------------------------")

    print(f"\n{DIM}🧠 Analyzing Project State...{RESET}")
    initial_input = args.instruction or ""
    plan = consult_chief(initial_input, is_startup=not bool(initial_input))

    print(f"\n{GREEN}{BOLD}CHIEF'S BRIEFING:{RESET}")
    type_writer(plan.get("explanation", "(no explanation)"))

    proposal = plan.get("proposal", "")
    if proposal:
        print(f"\n{YELLOW}👉 RECOMMENDATION: {proposal}{RESET}")

    hr()

    # ---- REPL loop ---------------------------------------------------------
    while True:
        try:
            # --- Display pending queue from last response ---
            queue = plan.get("queue", [])

            if queue:
                print(f"\n{YELLOW}📋 ACTION PLAN:{RESET}")
                for i, task in enumerate(queue, 1):
                    mode = f"{CYAN}⚡ PARALLEL {RESET}" if task.get(
                        "parallel") else f"{YELLOW}🔒 SEQUENTIAL{RESET}"
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
                    plan = consult_chief(user_input, is_startup=False)
                    hr()
                    print(f"\n{GREEN}{BOLD}CHIEF >{RESET}")
                    type_writer(plan.get("explanation", "(no explanation)"))
                    hr()
                    continue

                if auto_mode:
                    confirm = "y"
                    print(
                        f"\n{CYAN}⚡ [AUTO] Executing {len(queue)} task(s)...{RESET}")
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
                    failures = execute_swarm(queue)
                    plan = {"queue": []}
                    hr()

                    # --- HOTL Steering Gate (post-swarm review) -----------
                    if not failures:
                        accepted = review_changes(auto_mode=auto_mode)
                        if not accepted:
                            print(
                                f"\n{YELLOW}Changes reverted. Provide a new instruction "
                                f"or adjust your spec and re-run.{RESET}")
                        consecutive_failures = 0
                        # ── OODA MUTATION CYCLE (runs silently after each successful batch) ──
                        _run_ooda_mutation_cycle()
                        continue
                    # --- Kill Switch: abort after N consecutive failures ---
                    if failures:
                        consecutive_failures += 1
                        if consecutive_failures >= KILL_SWITCH_THRESHOLD:
                            print(
                                f"\n{RED}{BOLD}🛑 KILL SWITCH TRIGGERED:{RESET}{RED} "
                                f"{consecutive_failures} consecutive failure batch(es). "
                                f"Halting Auto-Pilot to prevent runaway loops.{RESET}"
                            )
                            print(
                                f"  Last failures:\n"
                                + "\n".join(
                                    f"    • {f['tool']} {f.get('args', '')}"
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
                                            f"  FAILED: {f['tool']} {f.get('args','')} — {f.get('error_output','')[:300]}"
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
                        print(
                            f"\n{YELLOW}🔄 Consulting Chief for recovery plan...{RESET}")
                        plan = consult_chief(
                            "", is_startup=False,
                            failure_context=failure_report
                        )
                        print(f"\n{RED}{BOLD}CHIEF RECOVERY PLAN:{RESET}")
                        type_writer(
                            plan.get("explanation", "(no explanation)"))
                        thought = plan.get("thought", "")
                        if thought:
                            print(f"  {DIM}[Reasoning: {thought}]{RESET}")
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
                # No pending queue — free-form input
                if auto_mode:
                    # Auto-Pilot with empty queue: nothing to do, exit gracefully
                    print(
                        f"\n{GREEN}✅ [AUTO] Queue exhausted. Nexus shutting down.{RESET}")
                    break
                try:
                    user_input = input(f"\n{BOLD}YOU > {RESET}").strip()
                except (KeyboardInterrupt, EOFError):
                    break

            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q", ":q"):
                break

            # ---- Consult Chief with new input ----
            print(f"\n{DIM}Chief is planning logistics...{RESET}")
            plan = consult_chief(user_input, is_startup=False)

            hr()
            print(f"\n{GREEN}{BOLD}CHIEF >{RESET}")
            type_writer(plan.get("explanation", "(no explanation)"))

            thought = plan.get("thought", "")
            if thought:
                print(f"  {DIM}[Reasoning: {thought}]{RESET}")

            next_proposal = plan.get("proposal", "")
            if next_proposal:
                print(f"\n{YELLOW}👉 PROPOSAL: {next_proposal}{RESET}")

            hr()

        except (KeyboardInterrupt, EOFError):
            break

    print(f"\n{DIM}Nexus shutting down. Goodbye.{RESET}")


if __name__ == "__main__":
    main()
