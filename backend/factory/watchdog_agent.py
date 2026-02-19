"""
FACTORY WATCHDOG AGENT — Halilit Support Center Dark Factory
Runs diagnostics (TypeScript compilation, linting) and generates Fix Directives
for the Builder Agent to act on.

Usage (via factory.py):
  python factory.py diagnose    — single scan
  python factory.py heal        — scan → fix → re-scan loop
"""
import sys
import subprocess
import re
from pathlib import Path

# agent_core lives in the same package; this file is executed with cwd=FACTORY
from agent_core import query_llm, save_artifact

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
REPAIRS_DIR = ROOT_DIR / "specs" / "repairs"
FIX_SPEC_PATH = REPAIRS_DIR / "current_fix.md"

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are the FACTORY WATCHDOG.
Your job is to analyze error logs and generate a concise "Fix Specification".
You do NOT write code. You write structured instructions for the Builder Agent.
Be concrete: name the exact file, interface, or function that must change.
"""


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def _run_tsc() -> dict:
    """Run `pnpm tsc --noEmit` in the frontend directory."""
    result = subprocess.run(
        ["pnpm", "exec", "tsc", "--noEmit"],
        cwd=str(FRONTEND_DIR),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {
            "status": "FAIL",
            "source": "Frontend TypeScript Compiler (tsc)",
            "log": (result.stdout + "\n" + result.stderr).strip(),
        }
    return {"status": "PASS", "source": "tsc", "log": ""}


def _run_eslint() -> dict:
    """Run ESLint on JS/JSX files only (TSC handles TypeScript).
    Treats exit-code 2 with 'no files' / 'all ignored' as a clean pass."""
    result = subprocess.run(
        ["pnpm", "exec", "eslint", "src/**/*.{js,jsx}", "--max-warnings", "0"],
        cwd=str(FRONTEND_DIR),
        capture_output=True,
        text=True,
    )
    combined = (result.stdout + "\n" + result.stderr).strip()
    # Exit code 2 with no lintable files is not a real failure
    if result.returncode != 0:
        no_files = any(phrase in combined for phrase in [
            "all of the files matching", "No files matching",
            "no files", "file patterns",
        ])
        if no_files:
            return {"status": "PASS", "source": "eslint", "log": ""}
        return {
            "status": "FAIL",
            "source": "Frontend ESLint",
            "log": combined,
        }
    return {"status": "PASS", "source": "eslint", "log": ""}


def run_diagnostics() -> dict:
    """Run all checks; return the first failure found, or a PASS record."""
    print("🩺 Watchdog scanning system health...")

    for checker in [_run_tsc, _run_eslint]:
        result = checker()
        tool = result["source"]
        if result["status"] == "FAIL":
            print(f"   ❌ {tool} — issues detected")
            return result
        print(f"   ✅ {tool} — OK")

    return {"status": "PASS", "source": "all", "log": "System Nominal"}


# ---------------------------------------------------------------------------
# Prescription
# ---------------------------------------------------------------------------

def diagnose_and_prescribe(error_report: dict) -> str | None:
    """Ask the LLM to convert a raw error log into a structured Fix Spec."""
    print(f"🚨 Error detected in: {error_report['source']}. Analyzing...")

    log_excerpt = error_report["log"][:4000]  # stay within context window

    prompt = f"""
DIAGNOSTIC REPORT
=================
Source : {error_report['source']}

Raw Log:
{log_excerpt}

TASK
====
1. Identify every file causing the error.
2. For each file write a "Repair Spec" section that tells the Builder Agent
   EXACTLY what type, interface, function, or import to change/add/remove.
3. Be specific (e.g. "Add `stock_status: StockStatus` to the `Product`
   interface in `frontend/src/types/index.ts`").

OUTPUT FORMAT (Markdown)
========================
# Fix: [Short descriptive title]

## Affected Files
- `path/to/file.ts` — one-line reason

## Repair Instructions
### `path/to/file.ts`
- [ ] Bullet describing the exact change needed
- [ ] …

(Repeat per file if multiple files are broken)
"""

    # Diagnosing errors is structured and specific — fast tier handles it well
    return query_llm(SYSTEM_PROMPT, prompt, model_tier="fast")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def run_watchdog() -> bool:
    """
    Execute a full watchdog cycle.
    Returns True if the system is healthy, False if a fix spec was written.
    """
    REPAIRS_DIR.mkdir(parents=True, exist_ok=True)

    report = run_diagnostics()

    if report["status"] == "PASS":
        # Remove stale fix spec if it exists from a previous run
        if FIX_SPEC_PATH.exists():
            FIX_SPEC_PATH.unlink()
        print("✅ System is Healthy. No improvements needed.")
        return True

    prescription = diagnose_and_prescribe(report)

    if prescription:
        save_artifact(str(FIX_SPEC_PATH), prescription)
        print(f"🩹 Fix Prescribed → {FIX_SPEC_PATH.relative_to(ROOT_DIR)}")
        print("   Run `python factory.py heal` to apply.")
        return False
    else:
        print("❌ Watchdog failed to analyse the error — check API key and logs.")
        return False


if __name__ == "__main__":
    healthy = run_watchdog()
    sys.exit(0 if healthy else 1)
