"""
MASTER FACTORY CONTROLLER — Halilit Support Center v9.7.0 Chief
Unified CLI for the full development lifecycle.

Commands:
  init                    Create folder structure
  design "description"    Architect: generate a spec from plain text
  build <spec_path>       Builder: materialize code from a spec
  start                   Launch backend + frontend dev servers
  status                  Check environment health
"""
import sys
import os
import subprocess
import time
from pathlib import Path

# --- PATHS ---
ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"
BACKEND = ROOT / "backend"
SPECS = ROOT / "specs"
FACTORY = BACKEND / "factory"


def log(msg: str) -> None:
    print(f"🏭 [FACTORY] {msg}")


def ensure_env() -> None:
    """Abort if the Gemini API key is missing."""
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        log("❌ STOP: GEMINI_API_KEY (or GOOGLE_API_KEY) is not set.")
        log("   Export it or add it to your .env file and try again.")
        sys.exit(1)


def cmd_init() -> None:
    """Create all required directory scaffolding."""
    log("Initializing Factory Floor...")
    dirs = [
        SPECS / "interface",
        SPECS / "data_pipeline",
        SPECS / "behavior",
        SPECS / "01_data",
        SPECS / "strategy",
        FACTORY,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        log(f"  ✓ {d.relative_to(ROOT)}")
    log("✅ Structure ready.")


def cmd_design(prompt: str, category: str = "interface") -> None:
    """Architect: generate a spec from a plain-text feature description."""
    ensure_env()
    log(f"Activating Spec Architect...")
    agent = FACTORY / "spec_writer.py"
    env = {**os.environ, "PYTHONPATH": str(FACTORY)}
    subprocess.run(
        [sys.executable, str(agent), prompt, category],
        cwd=str(FACTORY),
        env=env,
    )


def cmd_build(spec_path: str) -> None:
    """Builder: materialise a spec into production code."""
    ensure_env()

    # Resolve spec path — try several conventions
    candidates = [
        Path(spec_path),                           # absolute or cwd-relative
        ROOT / spec_path,                          # relative to repo root
        SPECS / "interface" / spec_path,           # shorthand: filename only
        SPECS / "data_pipeline" / spec_path,
    ]
    resolved = next((p for p in candidates if p.exists()), None)

    if resolved is None:
        log(f"❌ Spec not found: {spec_path}")
        log("   Try passing the full path, e.g.:  python factory.py build specs/interface/my_spec.md")
        return

    log(f"Activating Builder Agent for {resolved.name}...")
    agent = FACTORY / "builder_agent.py"
    env = {**os.environ, "PYTHONPATH": str(FACTORY)}
    subprocess.run(
        [sys.executable, str(agent), str(resolved.resolve())],
        cwd=str(FACTORY),
        env=env,
    )


def cmd_start() -> None:
    """Launch the FastAPI backend and Vite frontend dev servers."""
    log("🚀 Starting Console...")
    # Backend via uvicorn (non-blocking, spawns in background)
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--reload", "--port", "8000"],
        cwd=str(BACKEND),
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )
    log(f"  Backend PID {backend_proc.pid} → http://localhost:8000")
    # Frontend via pnpm (blocks until Ctrl-C)
    try:
        subprocess.run(["pnpm", "dev"], cwd=str(FRONTEND))
    except KeyboardInterrupt:
        log("Shutting down...")
        backend_proc.terminate()


def cmd_steer() -> None:
    """Steerer: audit strategy vs specs and generate the next improvement."""
    ensure_env()
    log("Activating System Steerer (Level 6)...")
    agent = FACTORY / "steerer_agent.py"
    env = {**os.environ, "PYTHONPATH": str(FACTORY)}
    subprocess.run(
        [sys.executable, str(agent)],
        cwd=str(FACTORY),
        env=env,
    )


def cmd_doc() -> None:
    """Scribe: read codebase and regenerate docs/ARCHITECTURE.md."""
    ensure_env()
    log("Activating Factory Scribe...")
    agent = FACTORY / "scribe_agent.py"
    env = {**os.environ, "PYTHONPATH": str(FACTORY)}
    subprocess.run(
        [sys.executable, str(agent)],
        cwd=str(FACTORY),
        env=env,
    )


# ---------------------------------------------------------------------------
# Level 7 — Self-Improvement
# ---------------------------------------------------------------------------

def cmd_diagnose() -> None:
    """Watchdog: run diagnostics and write a Fix Spec if errors are found."""
    ensure_env()
    (SPECS / "repairs").mkdir(parents=True, exist_ok=True)
    log("Activating Factory Watchdog...")
    agent = FACTORY / "watchdog_agent.py"
    env = {**os.environ, "PYTHONPATH": str(FACTORY)}
    subprocess.run(
        [sys.executable, str(agent)],
        cwd=str(FACTORY),
        env=env,
    )


def cmd_heal(max_cycles: int = 3) -> None:
    """Autonomous fix loop: Watchdog -> Builder -> Watchdog (up to max_cycles)."""
    ensure_env()
    (SPECS / "repairs").mkdir(parents=True, exist_ok=True)
    log(f"🚑 Starting Self-Healing Sequence (max {max_cycles} cycles)...")

    fix_spec = SPECS / "repairs" / "current_fix.md"
    watchdog = FACTORY / "watchdog_agent.py"
    builder = FACTORY / "builder_agent.py"
    env = {**os.environ, "PYTHONPATH": str(FACTORY)}

    for cycle in range(1, max_cycles + 1):
        log(f"Cycle {cycle}/{max_cycles}: Diagnosing...")

        result = subprocess.run(
            [sys.executable, str(watchdog)],
            cwd=str(FACTORY),
            env=env,
        )
        # watchdog exits 0 when healthy
        if result.returncode == 0:
            log("✨ System is clean. Stopping loop.")
            return

        if not fix_spec.exists():
            log("⚠️  Watchdog exited non-zero but wrote no fix spec — manual inspection needed.")
            return

        log("🩹 Fix spec found. Invoking Builder Agent...")
        subprocess.run(
            [sys.executable, str(builder), str(fix_spec.resolve())],
            cwd=str(FACTORY),
            env=env,
        )

        # Remove the spec so the next watchdog run starts fresh
        fix_spec.unlink(missing_ok=True)
        log("✅ Fix applied. Verifying...")
        time.sleep(1)  # let the filesystem settle

    log(f"⚠️  Reached {max_cycles} cycles without a clean bill of health — review manually.")


def cmd_optimize(target_file: str) -> None:
    """Optimizer: refactor a source file in-place (no behaviour changes)."""
    ensure_env()
    full_path = ROOT / target_file
    if not full_path.exists():
        log(f"❌ File not found: {full_path}")
        sys.exit(1)
    log(f"Activating Code Optimizer for {target_file}...")
    agent = FACTORY / "optimizer_agent.py"
    env = {**os.environ, "PYTHONPATH": str(FACTORY)}
    subprocess.run(
        [sys.executable, str(agent), str(full_path.resolve())],
        cwd=str(FACTORY),
        env=env,
    )


def cmd_patch(filename: str, instruction: str) -> None:
    """Patcher: apply a targeted plain-English edit to a single file (FAST model)."""
    ensure_env()
    full_path = ROOT / filename
    if not full_path.exists():
        log(f"❌ File not found: {full_path}")
        sys.exit(1)
    log(f"Activating Code Patcher for {filename}...")
    agent = FACTORY / "patcher_agent.py"
    env = {**os.environ, "PYTHONPATH": str(FACTORY)}
    subprocess.run(
        [sys.executable, str(agent), str(full_path.resolve()), instruction],
        cwd=str(FACTORY),
        env=env,
    )


def cmd_commit(dry_run: bool = False) -> None:
    """Repo Agent: stage, generate semantic commit message, commit, and push."""
    ensure_env()
    log("Activating Repository Manager...")
    agent = FACTORY / "repo_agent.py"
    env = {**os.environ, "PYTHONPATH": str(FACTORY)}
    args = [sys.executable, str(agent)]
    if dry_run:
        args.append("--dry-run")
    subprocess.run(args, cwd=str(FACTORY), env=env)


def cmd_reflect(context: str) -> None:
    """
    Mentor (Reflect Agent): extract a lesson from a failure event and append it
    to docs/LEARNED_GUIDELINES.md so all future agents learn from the mistake.
    """
    ensure_env()
    log("Activating Mentor Agent (Reflect)...")
    agent = FACTORY / "reflect_agent.py"
    env = {**os.environ, "PYTHONPATH": str(FACTORY)}
    subprocess.run(
        [sys.executable, str(agent), context],
        cwd=str(FACTORY),
        env=env,
    )


def cmd_task_force(task_id: str, goal: str, agents: list[str] | None = None) -> None:
    """
    Task-Force Coordinator: spin up a multi-agent improvement cycle with a shared
    Blackboard file, then orchestrate Steerer → Builder → Watchdog rounds.
    """
    ensure_env()
    import uuid as _uuid

    if not agents:
        agents = ["steerer", "builder", "watchdog"]

    # Resolve a short unique id if none provided
    if not task_id:
        task_id = _uuid.uuid4().hex[:8]

    log(f"Assembling Task Force [{task_id}]...")
    log(f"  Goal   : {goal}")
    log(f"  Agents : {', '.join(agents)}")

    # Create Blackboard
    specs_temp = SPECS / "temp"
    specs_temp.mkdir(parents=True, exist_ok=True)
    bb_path = specs_temp / f"task_force_{task_id}.md"
    bb_content = f"""# Task-Force Blackboard: {task_id}

**Goal:** {goal}
**Agents:** {', '.join(agents)}
**Status:** In Progress

---

## Round 1 — Steerer: Architecture Contract
*(pending — Steerer will populate this)*

---

## Round 2 — Builder: Implementation Notes
*(pending — Builder will populate this)*

---

## Round 3 — Watchdog: Review & Feedback
*(pending — Watchdog will populate this)*

---

## API Contracts
*(agents append here)*

## Blockers / Escalations
*(agents append here)*
"""
    bb_path.write_text(bb_content, encoding="utf-8")
    log(f"  Blackboard created: {bb_path.relative_to(ROOT)}")

    # Round 1 — Steerer
    log("Round 1/3: Activating Steerer (Architecture Contract)...")
    env = {**os.environ,
           "PYTHONPATH": str(FACTORY), "TF_BLACKBOARD": str(bb_path)}
    subprocess.run([sys.executable, str(
        FACTORY / "steerer_agent.py")], cwd=str(FACTORY), env=env)

    # Round 2 — Builder (uses spec written to blackboard by steerer if any)
    log("Round 2/3: Activating Builder (Implementation)...")
    subprocess.run([sys.executable, str(FACTORY / "builder_agent.py"),
                   str(bb_path)], cwd=str(FACTORY), env=env)

    # Round 3 — Watchdog / Patcher (reviews builder output)
    log("Round 3/3: Activating Watchdog (Review)...")
    subprocess.run([sys.executable, str(
        FACTORY / "watchdog_agent.py")], cwd=str(FACTORY), env=env)

    log(f"✅ Task Force [{task_id}] complete. See Blackboard: {bb_path.relative_to(ROOT)}")


def cmd_status() -> None:
    """Print environment health information."""
    log("Environment Status")
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    print(f"  GEMINI_API_KEY : {'✅ set' if gemini_key else '❌ missing'}")

    venv = os.getenv("VIRTUAL_ENV")
    print(f"  Virtual env    : {venv if venv else '⚠️  not activated'}")

    specs_count = len(list(SPECS.rglob("*.md")))
    print(f"  Specs found    : {specs_count} markdown files under specs/")

    be_factory = FACTORY / "agent_core.py"
    print(
        f"  Factory agents : {'✅ present' if be_factory.exists() else '❌ missing'}")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
HELP = """
Dark Factory — Master Controller  (v9.7.0 — Chief)

Usage:
  python factory.py <command> [args]

Core Commands:
  init                           Create project folder structure
  design "feature description"   Architect generates a spec from text
  design "feature" <category>    Category defaults to 'interface'
  build <spec_path>              Builder materializes code from spec
  steer                          Steerer audits strategy vs specs → generates next spec
  doc                            Scribe regenerates docs/ARCHITECTURE.md from code
  start                          Run backend + frontend dev servers
  status                         Show environment health

Level 7 — Self-Improvement:
  diagnose                       Watchdog: scan for compiler / lint errors; write fix spec
  heal                           Autonomous loop: diagnose → fix → re-diagnose (×3)
  optimize <file>                Optimizer: refactor a source file in-place
  patch <file> "instruction"     Patcher: surgical fast-model edit to a single file

Level 8 — Professional Standards:
  commit                         Repo Agent: semantic commit message + push to git
  commit --dry-run               Preview commit message without committing

Level 9 — Feedback & Memory Loop:
  reflect "failure context"      Mentor: extract lesson → append to docs/LEARNED_GUIDELINES.md
  task_force <id> "goal"         Coordinator: multi-agent Task Force (Steerer→Builder→Watchdog)

Examples:
  python factory.py init
  python factory.py design "A SystemSettings view that lists scrapers and lets operators toggle them"
  python factory.py build specs/interface/system_settings.md
  python factory.py steer
  python factory.py doc
  python factory.py start
  python factory.py diagnose
  python factory.py heal
  python factory.py optimize frontend/src/components/views/InventoryView.tsx
  python factory.py patch frontend/src/components/views/InventoryView.tsx "Change the header colour to blue"
  python factory.py reflect "TS error: missing product.id field in InventoryView — fixed by adding id to ProductCard type"
  python factory.py task_force accessory_engine "Implement cross-sell accessories on Product Detail"
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(HELP)
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "init":
        cmd_init()

    elif command == "design":
        if len(sys.argv) < 3:
            log(
                "❌ Usage: python factory.py design \"Feature description\" [category]")
            sys.exit(1)
        category_arg = sys.argv[3] if len(sys.argv) > 3 else "interface"
        cmd_design(sys.argv[2], category_arg)

    elif command == "build":
        if len(sys.argv) < 3:
            log("❌ Usage: python factory.py build <spec_path>")
            sys.exit(1)
        cmd_build(sys.argv[2])

    elif command == "doc":
        cmd_doc()

    elif command == "steer":
        cmd_steer()

    elif command == "start":
        cmd_start()

    elif command == "status":
        cmd_status()

    elif command == "diagnose":
        cmd_diagnose()

    elif command == "heal":
        max_c = int(sys.argv[2]) if len(
            sys.argv) > 2 and sys.argv[2].isdigit() else 3
        cmd_heal(max_c)

    elif command == "optimize":
        if len(sys.argv) < 3:
            log("❌ Usage: python factory.py optimize <relative_file_path>")
            sys.exit(1)
        cmd_optimize(sys.argv[2])

    elif command == "patch":
        if len(sys.argv) < 4:
            log('❌ Usage: python factory.py patch <relative_file_path> "instruction"')
            sys.exit(1)
        cmd_patch(sys.argv[2], sys.argv[3])

    elif command == "commit":
        dry = "--dry-run" in sys.argv or "-n" in sys.argv
        cmd_commit(dry_run=dry)

    elif command == "reflect":
        if len(sys.argv) < 3:
            log('❌ Usage: python factory.py reflect "failure context"')
            sys.exit(1)
        cmd_reflect(sys.argv[2])

    elif command == "task_force":
        if len(sys.argv) < 4:
            log('❌ Usage: python factory.py task_force <id> "goal" [agent1,agent2,...]')
            sys.exit(1)
        tf_id = sys.argv[2]
        tf_goal = sys.argv[3]
        tf_agents = sys.argv[4].split(",") if len(sys.argv) > 4 else None
        cmd_task_force(tf_id, tf_goal, tf_agents)

    else:
        log(f"Unknown command: {command}")
        print(HELP)
        sys.exit(1)
