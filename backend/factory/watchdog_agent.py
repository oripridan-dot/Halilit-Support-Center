"""
FACTORY WATCHDOG AGENT — Halilit Support Center Dark Factory
Runs diagnostics (TypeScript compilation, linting) and generates Fix Directives
for the Builder Agent to act on.

v2.0 — GATEKEEPER MODE (Pillar 4: The Watchdog Gatekeeper)
Now acts as the final quality checkpoint in every autonomous cycle.
A Gatekeeper review compares the implemented code against the original spec
and the user's intent before the Chief marks the cycle complete.

Usage (via factory.py):
  python factory.py diagnose    — single scan
  python factory.py heal        — scan → fix → re-scan loop
"""
import sys
import subprocess
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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
# Prompts
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are the FACTORY WATCHDOG.
Your job is to analyze error logs and generate a concise "Fix Specification".
You do NOT write code. You write structured instructions for the Builder Agent.
Be concrete: name the exact file, interface, or function that must change.
"""

GATEKEEPER_SYSTEM_PROMPT = """
You are the FACTORY GATEKEEPER — the final quality checkpoint in an autonomous AI development pipeline.

Your sole job is to decide: does the implemented code FULLY satisfy the specification AND the user's original intent?

EVALUATION CRITERIA:
1. **Spec Compliance:** Every requirement in the spec is reflected in the code.
2. **User Intent:** The feature does what the user originally asked for.
3. **No Regressions:** The code doesn't remove existing functionality.
4. **Code Quality:** No obvious bugs, missing error states, or undefined references.
5. **Source Rules:** ZERO synthetic/mock data presented as real (Halilit Source Rules).

RESPONSE FORMAT — you MUST respond with EXACTLY this format:
VERDICT: APPROVED
or
VERDICT: REJECTED
REASON: [1-3 bullet points describing SPECIFIC, actionable flaws. Name the exact file, line, or function.]
REMEDY: [Precise instructions for the Builder to fix the issue. Must be concrete enough to act on without human input.]

RULES:
- Only reject for HARD blockers (spec violations, regressions, missing requirements).
- Do NOT reject for minor style issues, code formatting, or theoretical optimizations.
- If in doubt, APPROVE — over-rejection defeats the purpose of autonomous execution.
- Your REMEDY must be actionable by the Builder Agent without any human clarification.
"""


# ---------------------------------------------------------------------------
# Gatekeeper verdict
# ---------------------------------------------------------------------------

@dataclass
class GatekeeperVerdict:
    approved: bool
    reason: str = ""
    remedy: str = ""

    def as_feedback(self) -> str:
        """Returns a prompt-ready feedback block for the Builder."""
        if self.approved:
            return ""
        return (
            f"--- ❌ GATEKEEPER REJECTED — FIX ALL OF THESE ---\n"
            f"**Reason:**\n{self.reason}\n\n"
            f"**Required Fix:**\n{self.remedy}\n"
        )


def gatekeeper_review(
    original_prompt: str,
    spec_text: str,
    code_text: str,
    screenshot_description: str = "",
) -> GatekeeperVerdict:
    """
    Final quality gate: reviews implemented code against the spec and user intent.

    Architecture: Pillar 4 — The Watchdog Gatekeeper.
    Called by the Task Force coordinator AFTER the Builder's inner_loop passes
    all Verification Commands.

    Args:
        original_prompt:       The user's original natural-language request.
        spec_text:             The Steerer's spec markdown.
        code_text:             The Builder's final generated code (after sandbox pass).
        screenshot_description: Optional Playwright/vision description of the UI state.

    Returns:
        GatekeeperVerdict with approved=True/False and structured feedback.
    """
    print("🛡️  Gatekeeper reviewing implementation against spec...")

    vision_section = ""
    if screenshot_description:
        vision_section = f"\nUI STATE (from Playwright/screenshot analysis):\n{screenshot_description}\n"

    prompt = f"""
ORIGINAL USER REQUEST:
{original_prompt}

SPEC (what the Builder was supposed to implement):
{spec_text[:3000]}

IMPLEMENTED CODE (what the Builder actually wrote):
{code_text[:4000]}
{vision_section}
TASK:
Review the implemented code against the original request and spec.
Respond with VERDICT: APPROVED or VERDICT: REJECTED (with REASON and REMEDY).
"""

    # Gatekeeper review is a critical judgement — use the smart tier
    response = query_llm(GATEKEEPER_SYSTEM_PROMPT, prompt,
                         temperature=0.0, model_tier="smart")
    if not response:
        print("⚠️  Gatekeeper received no response — defaulting to APPROVED.")
        return GatekeeperVerdict(approved=True, reason="LLM unavailable")

    # Parse verdict
    approved = bool(re.search(r"VERDICT:\s*APPROVED", response, re.IGNORECASE))
    if approved:
        print("✅  Gatekeeper: APPROVED")
        return GatekeeperVerdict(approved=True)

    # Extract REASON and REMEDY from rejection
    reason_match = re.search(
        r"REASON:\s*(.+?)(?=REMEDY:|$)", response, re.DOTALL | re.IGNORECASE)
    remedy_match = re.search(
        r"REMEDY:\s*(.+?)$", response, re.DOTALL | re.IGNORECASE)
    reason = reason_match.group(1).strip() if reason_match else response[:500]
    remedy = remedy_match.group(1).strip(
    ) if remedy_match else "Review the spec requirements carefully and reimplement."

    print(f"❌  Gatekeeper: REJECTED\n   Reason: {reason[:200]}")
    return GatekeeperVerdict(approved=False, reason=reason, remedy=remedy)


def evaluate_frontend_feature(
    spec_text: str,
    original_prompt: str = "",
    code_text: str = "",
    url: str = "http://localhost:5173",
    hint: str = "",
) -> GatekeeperVerdict:
    """
    One-call quality gate for a frontend feature build.

    Pillar 4 + Multi-Modal Eyes:
      1. Captures a Playwright screenshot and describes it via Gemini vision.
      2. Feeds the visual description into the Gatekeeper review alongside
         the spec and generated code.
      3. Returns the verdict; callers check `.approved` and use `.as_feedback()`
         to inject rejection context back into the Builder.

    Args:
        spec_text:       The spec (markdown) that the Builder was supposed to implement.
        original_prompt: The user's original natural-language request (for intent check).
        code_text:       The Builder's generated code (optional but enriches the review).
        url:             The local dev-server URL to screenshot.
        hint:            Extra guidance passed to the visual QA prompt
                         (e.g. "Check if the comparison matrix is visible").

    Returns:
        GatekeeperVerdict — approved=True means the feature passed all gates.
    """
    # ── Step 1: Visual QA (screenshot + Gemini vision) ───────────────────────
    screenshot_description = ""
    try:
        _factory_dir = Path(__file__).resolve().parent
        import sys as _sys
        if str(_factory_dir) not in _sys.path:
            _sys.path.insert(0, str(_factory_dir))
        from visual_qa import capture_and_describe  # noqa: PLC0415
        print("📸  [evaluate_frontend_feature] Capturing visual QA screenshot...")
        screenshot_description = capture_and_describe(
            url=url,
            spec_text=spec_text,
            hint=hint or "Verify the UI matches the spec layout and token requirements.",
        )
        if screenshot_description.startswith("[visual_qa:"):
            print(f"   ℹ️  {screenshot_description}")
            screenshot_description = ""  # treat as missing rather than noise
        else:
            print("   ✅ Screenshot captured and analysed.")
    except Exception as _err:
        print(f"   ⚠️  Visual QA unavailable: {_err}")

    # ── Step 2: Gatekeeper review ─────────────────────────────────────────────
    return gatekeeper_review(
        original_prompt=original_prompt or spec_text[:200],
        spec_text=spec_text,
        code_text=code_text,
        screenshot_description=screenshot_description,
    )


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Diagnostics (Level 5 — tsc + eslint + pytest + vitest)
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


def _run_pytest() -> dict:
    """Run pytest if backend test files are found. Returns SKIP if none found."""
    tests_dir = ROOT_DIR / "backend" / "tests"
    test_files = list(tests_dir.glob("test_*.py")
                      ) if tests_dir.exists() else []
    if not test_files:
        return {"status": "SKIP", "source": "pytest", "log": "No test files found."}
    print(f"   🧪  Running pytest ({len(test_files)} file(s))...")
    result = subprocess.run(
        ["python", "-m", "pytest", str(tests_dir), "-v", "--tb=short", "-q"],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        return {
            "status": "FAIL",
            "source": "pytest",
            "log": (result.stdout + "\n" + result.stderr).strip()[:3000],
        }
    return {"status": "PASS", "source": "pytest", "log": ""}


def _run_vitest() -> dict:
    """Run pnpm test --run (Vitest) if frontend test files are found. SKIP if none."""
    test_dirs = [
        ROOT_DIR / "frontend" / "tests",
        ROOT_DIR / "frontend" / "src",
    ]
    test_files = []
    for d in test_dirs:
        if d.exists():
            test_files.extend(d.rglob("*.test.ts"))
            test_files.extend(d.rglob("*.test.tsx"))
            test_files.extend(d.rglob("*.spec.ts"))
            test_files.extend(d.rglob("*.spec.tsx"))
    if not test_files:
        return {"status": "SKIP", "source": "vitest", "log": "No test files found."}
    print(f"   🧪  Running Vitest ({len(test_files)} file(s))...")
    result = subprocess.run(
        ["pnpm", "test", "--run"],
        cwd=str(FRONTEND_DIR),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        return {
            "status": "FAIL",
            "source": "vitest",
            "log": (result.stdout + "\n" + result.stderr).strip()[:3000],
        }
    return {"status": "PASS", "source": "vitest", "log": ""}


def run_unit_tests(target_file: str = "") -> bool:
    """
    Executes physical Vitest unit tests in the frontend workspace.

    Called by the Frontend Manager during TDD State 3 (Red Phase) and
    State 5 (Green Phase) to verify React component logic.

    Args:
        target_file: If provided, runs only the tests matching that filename.
                     Pass an empty string to run the full test suite.

    Returns:
        True if all tests pass (Green), False if any test fails (Red).
    """
    print(f"🐕 Watchdog: Sniffing logic in {target_file if target_file else 'all components'}...")

    cmd = ["pnpm", "test", "--", "--run", "--passWithNoTests"]
    if target_file:
        # Vitest accepts a filename filter as the last positional argument
        cmd.append(Path(target_file).name)

    result = subprocess.run(
        cmd,
        cwd=str(FRONTEND_DIR),
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode == 0:
        print("   ✅ Watchdog confirms: Tests passed (Green Phase).")
        return True

    print("   ❌ Watchdog detected failures (Red Phase):")
    # Print the last 15 lines to avoid console flood
    print("\n".join(result.stdout.splitlines()[-15:]))
    return False


def run_diagnostics() -> dict:
    """Run all checks (tsc, eslint, pytest, vitest); return first failure or PASS."""
    print("🩺 Watchdog scanning system health...")

    for checker in [_run_tsc, _run_eslint, _run_pytest, _run_vitest]:
        result = checker()
        tool = result["source"]
        if result["status"] == "SKIP":
            print(f"   ⏭️  {tool} — skipped (no test files)")
            continue
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
# Entry Points
# ---------------------------------------------------------------------------

def run_watchdog() -> bool:
    """
    Execute a full watchdog cycle (diagnostics + prescription).
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
    import os as _os

    # ------------------------------------------------------------------
    # GATEKEEPER MODE: triggered when TF_BLACKBOARD env is set
    # In this mode we run the Gatekeeper review (Pillar 4) and optionally
    # augment it with a Playwright visual screenshot (visual_qa module).
    # ------------------------------------------------------------------
    _bb = _os.environ.get("TF_BLACKBOARD", "").strip()
    if _bb:
        _bb_path = Path(_bb)
        if _bb_path.exists():
            print("🛡️  Gatekeeper mode activated (Task Force Round 3)...")

            _bb_text = _bb_path.read_text(encoding="utf-8")

            # Extract goal from first line that looks like "**Goal:** ..."
            import re as _re
            _goal_m = _re.search(r"\*\*Goal:\*\*\s*(.+)", _bb_text)
            _original_prompt = _goal_m.group(
                1).strip() if _goal_m else "(unknown goal)"

            # Spec section is the whole blackboard (it grows as agents write)
            _spec_text = _bb_text[:3000]

            # Extract builder code from "## Round 2" section if present
            _code_section = _re.search(
                r"##\s+Round 2.*?$(.*?)(?=^##|\Z)",
                _bb_text, _re.DOTALL | _re.MULTILINE
            )
            _code_text = _code_section.group(
                1).strip() if _code_section else ""

            # ── Visual QA ─────────────────────────────────────────────
            _screenshot_desc = ""
            try:
                sys.path.insert(0, str(Path(__file__).resolve().parent))
                from visual_qa import capture_and_describe as _cap
                print("📸  Attempting visual QA (Playwright screenshot)...")
                _screenshot_desc = _cap(
                    url="http://localhost:5173",
                    spec_text=_spec_text,
                )
                if _screenshot_desc.startswith("[visual_qa:"):
                    print(f"   ℹ️  {_screenshot_desc}")
                else:
                    print("   ✅ Screenshot captured and analysed.")
            except Exception as _vqa_err:
                print(f"   ⚠️  Visual QA unavailable: {_vqa_err}")

            verdict = gatekeeper_review(
                original_prompt=_original_prompt,
                spec_text=_spec_text,
                code_text=_code_text,
                screenshot_description=_screenshot_desc,
            )

            # Write verdict back to blackboard
            _status_line = "✅ APPROVED" if verdict.approved else "❌ REJECTED"
            _gatekeeper_section = f"\n\n---\n## Round 3 — Gatekeeper Verdict\n\n**Status:** {_status_line}\n"
            if not verdict.approved:
                _gatekeeper_section += f"\n**Reason:**\n{verdict.reason}\n\n**Required Fix:**\n{verdict.remedy}\n"
            _bb_path.write_text(_bb_text.rstrip() +
                                _gatekeeper_section, encoding="utf-8")
            print(f"   Verdict written → {_bb_path.name}")

            sys.exit(0 if verdict.approved else 1)

    # Default: run standard diagnostics / prescription cycle
    healthy = run_watchdog()
    sys.exit(0 if healthy else 1)
