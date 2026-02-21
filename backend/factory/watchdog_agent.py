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

# JIT Oracle Lifeline — cold-booted external consultant for stuck loops
try:
    from oracle_agent import consult_external_oracle as _oracle_lifeline
except ImportError:
    from .oracle_agent import consult_external_oracle as _oracle_lifeline  # type: ignore

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


# ---------------------------------------------------------------------------
# Wolverine — Compiler Error Feedback Loop
# ---------------------------------------------------------------------------

def extract_import_errors(compiler_log: str) -> list[dict]:
    """
    Parses tsc / Rollup / Vite compiler output and extracts actionable
    import resolution failures.

    Returns a list of dicts:
        {"file": str, "bad_import": str, "line": int, "full_error": str}

    Example patterns caught:
        - "Cannot find module '../stores/navigationStore'"
        - "Rollup failed to resolve import \"@/stores/navigationStore\""
        - "error TS2307: Cannot find module 'src/stores/...'"
    """
    errors: list[dict] = []

    # tsc: error TS2307 or TS2305 — "Cannot find module '...'"
    tsc_pattern = re.compile(
        r"^(?P<file>[^\(]+)\((?P<line>\d+),\d+\):.*?Cannot find module '(?P<imp>[^']+)'",
        re.MULTILINE,
    )
    for m in tsc_pattern.finditer(compiler_log):
        errors.append({
            "file": m.group("file").strip(),
            "bad_import": m.group("imp").strip(),
            "line": int(m.group("line")),
            "full_error": m.group(0).strip(),
        })

    # Rollup/Vite: "failed to resolve import '...' from '...'"
    rollup_pattern = re.compile(
        r"failed to resolve import [\"'](?P<imp>[^\"']+)[\"'] from [\"'](?P<file>[^\"']+)[\"']",
        re.IGNORECASE,
    )
    for m in rollup_pattern.finditer(compiler_log):
        errors.append({
            "file": m.group("file").strip(),
            "bad_import": m.group("imp").strip(),
            "line": 0,
            "full_error": m.group(0).strip(),
        })

    # Deduplicate by (file, bad_import)
    seen: set[tuple[str, str]] = set()
    unique: list[dict] = []
    for e in errors:
        key = (e["file"], e["bad_import"])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    return unique


def targeted_import_heal(compiler_log: str) -> bool:
    """
    Wolverine — Compiler Error Feedback Loop.

    When tsc or Vite reports unresolved imports, this function:
      1. Extracts the exact file + bad import path combination.
      2. Asks the LLM to suggest the correct import path given the project layout.
      3. Applies the fix directly via a string replace in the offending file.

    Returns True if at least one fix was applied, False otherwise.
    Architecture: Wolverine Gap-3 remediation (watchdog_agent.py).
    """
    import_errors = extract_import_errors(compiler_log)
    if not import_errors:
        return False

    print(
        f"🐺 Wolverine: {len(import_errors)} import error(s) detected — triggering targeted heal...")
    fixed_any = False

    for err in import_errors:
        bad_file = err["file"]
        bad_import = err["bad_import"]
        print(f"   🔍  Healing: {bad_file}  ← bad import: '{bad_import}'")

        # Build the absolute path to the file
        candidate = ROOT_DIR / bad_file
        if not candidate.exists():
            candidate = FRONTEND_DIR / bad_file
        if not candidate.exists():
            print(f"      ⚠️  File not found on disk: {bad_file} — skipping.")
            continue

        file_content = candidate.read_text(encoding="utf-8")

        # Ask the LLM to produce the corrected import line
        heal_prompt = f"""A TypeScript/React file has an unresolvable import. Fix ONLY the broken import line.

File: {bad_file}
Bad import path: "{bad_import}"
Compiler error: {err['full_error']}

Project structure hints:
- Navigation store is at: frontend/src/store/navigationStore.ts (singular "store", not "stores")
- Hooks are at: frontend/src/hooks/
- Components are at: frontend/src/components/
- Types are at: frontend/src/types/index.ts

Current file content (first 60 lines):
{chr(10).join(file_content.splitlines()[:60])}

Return ONLY the single corrected import line (e.g. import {{ useNavigationStore }} from '@/store/navigationStore';).
No explanation. No fences. Just the corrected import statement."""

        corrected_line = query_llm(
            "You are a TypeScript import path expert. Return only the corrected import line.",
            heal_prompt,
            temperature=0.0,
            model_tier="fast",
        )

        if not corrected_line:
            print("      ❌ LLM returned no response.")
            continue

        corrected_line = corrected_line.strip().strip("`")

        # Find and replace the bad import line in the file
        bad_line_pattern = re.compile(
            re.escape(bad_import).replace(r"\/", r"[/\\]"),
            re.IGNORECASE,
        )
        # Find the actual import line containing the bad path
        for original_line in file_content.splitlines():
            if bad_import in original_line and original_line.strip().startswith("import"):
                new_content = file_content.replace(
                    original_line, corrected_line, 1)
                candidate.write_text(new_content, encoding="utf-8")
                print(
                    f"      ✅ Fixed: '{original_line.strip()}' → '{corrected_line.strip()}'")
                fixed_any = True
                break
        else:
            print(f"      ⚠️  Could not locate the import line in {bad_file}.")

    return fixed_any


def targeted_jsx_in_ts_heal(compiler_log: str) -> bool:
    """
    JSX-in-TS Healer — fixes the specific esbuild error:
      "Expected '>' but found 'className'" or any JSX syntax in a .ts file.

    Root-cause: a builder agent rewrote a hook/utility .ts file and injected
    React JSX component code. esbuild cannot parse JSX from .ts files.

    Strategy (in order):
      1. Parse affected .ts file path from the esbuild error.
      2. Attempt `git checkout HEAD -- <file>` to restore the last clean version.
      3. If no git version exists, ask the LLM to strip all JSX and rewrite as
         a plain TypeScript hook (no render, no return JSX).

    Returns True if at least one file was fixed.
    """
    # esbuild error pattern: 'Expected ">" but found "XXX"'
    # file reference appears as: file: path/to/file.ts:line:col
    jsx_error_pattern = re.compile(
        r'Expected ["\u201c]>["\u201d] but found',
        re.IGNORECASE,
    )
    if not jsx_error_pattern.search(compiler_log):
        return False

    # Extract the affected .ts file
    file_ref_pattern = re.compile(
        r"(?:file:\s*|Transform failed.*?\n.*?)([\w./\-]+\.ts):\d+:\d+",
        re.IGNORECASE,
    )
    # Also try simpler: look for a .ts path in the error lines
    path_pattern = re.compile(r"([\w/.\-]+\.ts)(?=:\d+:\d+)", re.IGNORECASE)

    affected_files: list[Path] = []
    for m in path_pattern.finditer(compiler_log):
        raw = m.group(1).strip()
        candidate = ROOT_DIR / raw
        if not candidate.exists():
            candidate = FRONTEND_DIR / raw
        if candidate.exists() and candidate.suffix == ".ts":
            if candidate not in affected_files:
                affected_files.append(candidate)

    if not affected_files:
        print("🚨 JSX-in-TS error detected but could not locate the .ts file.")
        return False

    fixed_any = False
    for ts_file in affected_files:
        rel = ts_file.relative_to(ROOT_DIR)
        print(f"🔧 JSX-in-TS Healer: attempting git restore for {rel}")

        # Strategy 1: git checkout HEAD
        git_result = subprocess.run(
            ["git", "-C", str(ROOT_DIR), "checkout", "HEAD", "--", str(rel)],
            capture_output=True,
            text=True,
        )
        if git_result.returncode == 0:
            print(f"   ✅ Restored {rel} from git HEAD.")
            fixed_any = True
            continue

        # Strategy 2: git show HEAD — pipe content directly
        show_result = subprocess.run(
            ["git", "-C", str(ROOT_DIR), "show", f"HEAD:{rel}"],
            capture_output=True,
            text=True,
        )
        if show_result.returncode == 0 and show_result.stdout.strip():
            ts_file.write_text(show_result.stdout, encoding="utf-8")
            print(f"   ✅ Restored {rel} from git HEAD via show.")
            fixed_any = True
            continue

        # Strategy 3: LLM rewrite — strip all JSX, keep the hook logic
        print(f"   ⚠️  No git version for {rel} — asking LLM to strip JSX...")
        current = ts_file.read_text(encoding="utf-8")
        strip_prompt = f"""The following TypeScript file ({rel}) is a .ts file
(not .tsx) but contains JSX/React component code. This causes an esbuild error.

Your job: REWRITE this file as a clean TypeScript hook (.ts).
Rules:
- REMOVE all React component functions (any function returning JSX / <div> etc.)
- REMOVE all JSX markup
- KEEP only the hook function (the function starting with 'use...')
- KEEP all imports needed by the hook
- KEEP the hook's return value intact
- File must have no JSX whatsoever
- Export the hook as both named and default export

Current (broken) file content:
{current[:6000]}

Return ONLY the complete corrected TypeScript file. No fences. No explanation."""
        fixed_content = query_llm(
            "You are a TypeScript refactoring expert. Strip JSX from hooks.",
            strip_prompt,
            temperature=0.0,
            model_tier="fast",
        )
        if fixed_content and "export" in fixed_content:
            ts_file.write_text(fixed_content.strip(), encoding="utf-8")
            print(f"   ✅ LLM stripped JSX from {rel}.")
            fixed_any = True

    return fixed_any


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
    print(
        f"🐕 Watchdog: Sniffing logic in {target_file if target_file else 'all components'}...")

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

def _burn_and_replace(broken_file: Path, spec_file: Path | None, raw_error: str) -> bool:
    """
    Strike 3: Wipe the broken file and trigger a full rebuild from spec.

    Used when Strike 1 (targeted edit) and Strike 2 (Oracle) have both failed.
    Returns True if the rebuild produced a clean build.
    """
    import subprocess as _sp
    print(f"\n{'🔥' * 10}")
    print(f"🔥  STRIKE 3 — BURN & REPLACE: {broken_file.name}")
    print(f"   File deemed corrupt.  Wiping and scheduling full rewrite...")
    print(f"{'🔥' * 10}\n")

    # Wipe the file to guarantee a clean AST state
    broken_file.write_text("", encoding="utf-8")
    print(f"   ✅ {broken_file.name} wiped.")

    if spec_file and spec_file.exists():
        print(
            f"   🏗️  Triggering builder_agent rewrite from spec: {spec_file.name}")
        factory_py = ROOT_DIR / "factory.py"
        result = _sp.run(
            [sys.executable, str(factory_py), "implement", str(spec_file)],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
        )
        combined = (result.stdout + "\n" + result.stderr).strip()
        if result.returncode == 0:
            print(f"   ✅ Burn & Replace rebuild succeeded.")
            return True
        print(f"   ❌ Rebuild failed:\n{combined[:500]}")
    else:
        print(f"   ⚠️  No spec file available — cannot auto-rebuild.")
        print(f"      Manually run: python factory.py implement <spec_path>")
        burn_protocol_path = REPAIRS_DIR / "burn_and_replace_required.md"
        burn_protocol_path.write_text(
            f"# Burn & Replace Required\n\n"
            f"**File:** `{broken_file.relative_to(ROOT_DIR)}`\n\n"
            f"**Status:** Wiped empty after Strike 1 + Strike 2 both failed.\n\n"
            f"**Action:** Run `python factory.py implement <spec_path>` to rebuild.\n\n"
            f"**Last error:**\n```\n{raw_error[:1500]}\n```\n",
            encoding="utf-8",
        )
        print(
            f"   📋 Instructions saved → {burn_protocol_path.relative_to(ROOT_DIR)}")
    return False


def run_watchdog() -> bool:
    """
    3-Strike Healing Protocol — replaces blind retry loops with progressive
    intelligent fallback, exactly like a senior developer would behave.

    STRIKE 1 — Deterministic targeted edit:
      • JSX-in-TS Healer (esbuild 'Expected >' errors)
      • Wolverine targeted import heal (tsc TS2307 errors)
      Raw terminal output (stdout + stderr) is captured and fed directly into
      LLM prompts — the AI reads the compiler, not a summary.

    STRIKE 2 — Oracle Lifeline:
      • LLM prescription via diagnose_and_prescribe (fast tier, structured Fix Spec)
      • If prescription fails or doesn't resolve the error: JIT Oracle Lifeline
        (cold-booted, unpolluted context, first-principles reasoning)

    STRIKE 3 — Burn & Replace:
      • File is deemed corrupted beyond patching.
      • Wiped empty.  builder_agent rewrites from spec from scratch.
      • Guarantees a clean AST state.

    Returns True if the system is healthy after any strike, False otherwise.
    """
    REPAIRS_DIR.mkdir(parents=True, exist_ok=True)

    report = run_diagnostics()

    if report["status"] == "PASS":
        if FIX_SPEC_PATH.exists():
            FIX_SPEC_PATH.unlink()
        print("✅ System is Healthy. No improvements needed.")
        return True

    # Capture the raw terminal output — the AI reads the compiler directly.
    raw_terminal_output = report.get("log", "").strip()
    error_source = report.get("source", "unknown")

    print(f"\n🩺 FAILURE DETECTED — {error_source}")
    print(
        f"   Raw terminal output ({len(raw_terminal_output)} chars captured)")
    if raw_terminal_output:
        # Print first 20 lines to terminal so operator can see what the AI sees
        preview = "\n".join(raw_terminal_output.splitlines()[:20])
        print(f"--- TERMINAL OUTPUT (Strike 1 reads this) ---\n{preview}\n---")

    # ═══════════════════════════════════════════════════════════════════════════
    # STRIKE 1 — Deterministic targeted edit (JSX healer + Wolverine)
    # Feed the EXACT raw terminal output to targeted healers.
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n⚡  STRIKE 1 — Deterministic targeted edit (reading raw compiler output)...")

    strike1_applied = False

    # 1a. JSX-in-TS healer (esbuild 'Expected > but found className')
    if raw_terminal_output:
        jsx_healed = targeted_jsx_in_ts_heal(raw_terminal_output)
        if jsx_healed:
            print("  🔧 Strike 1a: JSX-in-TS fixes applied.")
            strike1_applied = True

    # 1b. Wolverine — LLM-powered surgical import fix driven by raw tsc output
    if raw_terminal_output:
        import_healed = targeted_import_heal(raw_terminal_output)
        if import_healed:
            print("  🐺 Strike 1b: Wolverine import fixes applied.")
            strike1_applied = True

    if strike1_applied:
        print("  🔄 Re-running diagnostics after Strike 1...")
        report = run_diagnostics()
        raw_terminal_output = report.get("log", "").strip()
        if report["status"] == "PASS":
            if FIX_SPEC_PATH.exists():
                FIX_SPEC_PATH.unlink()
            print("  ✅ System healthy after Strike 1.")
            return True
        print(f"  ⚠️  Strike 1 did not fully heal — escalating to Strike 2.")
    else:
        print("  ℹ️  Strike 1: no deterministic fixes applicable — escalating to Strike 2.")

    # ═══════════════════════════════════════════════════════════════════════════
    # STRIKE 2 — Oracle Lifeline (LLM + unpolluted first-principles reasoning)
    # Feed the raw terminal output DIRECTLY into the Oracle prompt.
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n🔮  STRIKE 2 — Oracle Lifeline (cold-booted, reading raw terminal)...")

    # First try: structured LLM prescription (fast, targeted)
    prescription = diagnose_and_prescribe(report)
    if prescription:
        save_artifact(str(FIX_SPEC_PATH), prescription)
        print(
            f"  🩹 Strike 2a: Fix Spec prescribed → {FIX_SPEC_PATH.relative_to(ROOT_DIR)}")
        print(f"  Run `python factory.py heal` to apply the prescription.")
        return False  # caller (heal loop) will pick up the fix spec

    # Second try: JIT Oracle — completely cold-booted, zero memory of failures
    print("  ⚠️  LLM prescription returned nothing — phoning the Oracle...")
    oracle_strategy = _oracle_lifeline(
        intent=(
            f"Fix the following {error_source} errors "
            f"in the Halilit Support Center project.  "
            f"The raw compiler output is below — read every line carefully."
        ),
        current_code=(
            f"# Error source: {error_source}\n"
            f"# Raw terminal output is in error_logs below."
        ),
        error_logs=raw_terminal_output or "(no terminal output captured)",
    )
    if oracle_strategy:
        oracle_fix_path = REPAIRS_DIR / "oracle_rescue_protocol.md"
        save_artifact(str(oracle_fix_path), oracle_strategy)
        print(
            f"  🛸 Oracle Rescue Protocol saved → {oracle_fix_path.relative_to(ROOT_DIR)}")
        print(f"  Run `python factory.py heal` to apply.")
        return False  # caller (heal loop) will pick up the oracle protocol

    # ═══════════════════════════════════════════════════════════════════════════
    # STRIKE 3 — Burn & Replace
    # Both Strike 1 and Strike 2 failed.  File is corrupted beyond patching.
    # Wipe it and trigger a full spec-driven rewrite.
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n🔥  STRIKE 3 — Both targeted edit and Oracle failed.")
    print("    Activating Burn & Replace protocol...")

    # Identify the broken file from the error log
    _file_pattern = re.compile(r"(frontend/src/[\w/\-.]+\.tsx?)")
    _match = _file_pattern.search(raw_terminal_output)
    _broken_file: Optional[Path] = None
    if _match:
        _broken_file = ROOT_DIR / _match.group(1)
        if not _broken_file.exists():
            _broken_file = None

    if _broken_file:
        # Find a spec for this component if one exists
        _spec: Optional[Path] = None
        _comp_stem = _broken_file.stem.lower()
        for _spec_candidate in (ROOT_DIR / "specs" / "interface").glob("*.md"):
            if _comp_stem in _spec_candidate.stem.lower():
                _spec = _spec_candidate
                break
        _burn_and_replace(_broken_file, _spec, raw_terminal_output)
    else:
        print("  ⚠️  Could not identify specific broken file from terminal output.")
        print("      Saving terminal output for manual review...")
        emergency_path = REPAIRS_DIR / "strike3_terminal_output.txt"
        emergency_path.write_text(
            f"# Strike 3 triggered — could not isolate broken file\n\n"
            f"## Raw Terminal Output\n```\n{raw_terminal_output}\n```\n",
            encoding="utf-8",
        )
        print(f"  📋 Saved → {emergency_path.relative_to(ROOT_DIR)}")

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
