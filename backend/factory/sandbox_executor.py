"""
SANDBOX EXECUTOR — backend/factory/sandbox_executor.py
=======================================================
Parses "## Verification Commands" from a Steerer-written spec and runs each
command, capturing stdout/stderr.  Feeds results back into the Builder's
self-healing loop via the ImprovementCycleService.

Architecture: Pillar 3 — The Autonomous Execution Sandbox (The "Inner Loop")

Public API
----------
    parse_verification_commands(spec_text) -> list[VerificationCommand]
    run_verification_suite(commands, cwd=None) -> VerificationResult
    inner_loop(spec_file, cycle_service, cycle_id, builder_fn, max_rounds) -> bool
"""

from __future__ import annotations

import re
import shlex
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable

# Oracle import — optional; degrades gracefully if unavailable
try:
    from oracle_agent import consult_external_oracle as _oracle_call
except ImportError:
    try:
        from .oracle_agent import consult_external_oracle as _oracle_call  # type: ignore
    except ImportError:
        _oracle_call = None  # type: ignore

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_FRONTEND_DIR = _PROJECT_ROOT / "frontend"
_BACKEND_DIR = _PROJECT_ROOT / "backend"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

class CommandStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"      # command not found / not applicable to env
    TIMEOUT = "TIMEOUT"


@dataclass
class VerificationCommand:
    raw: str              # original line from the spec
    label: str            # human-readable label
    cmd: list[str]        # parsed argv
    cwd: Path             # working directory
    timeout: int = 120    # seconds


@dataclass
class CommandResult:
    command: VerificationCommand
    status: CommandStatus
    stdout: str = ""
    stderr: str = ""
    duration: float = 0.0

    @property
    def combined_output(self) -> str:
        return (self.stdout + "\n" + self.stderr).strip()

    @property
    def error_summary(self) -> str:
        """Returns first 3000 chars of error output suitable for LLM prompting."""
        out = self.combined_output
        return out[:3000] if out else ""


@dataclass
class VerificationResult:
    commands: list[CommandResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.status in (CommandStatus.PASS, CommandStatus.SKIP) for r in self.commands)

    @property
    def first_failure(self) -> CommandResult | None:
        for r in self.commands:
            if r.status == CommandStatus.FAIL:
                return r
        return None

    def summary_text(self) -> str:
        lines = []
        for r in self.commands:
            icon = {"PASS": "✅", "FAIL": "❌",
                    "SKIP": "⏭️", "TIMEOUT": "⏰"}[r.status]
            lines.append(
                f"{icon} [{r.status}] {r.command.label} ({r.duration:.1f}s)")
            if r.status == CommandStatus.FAIL:
                lines.append(f"   Error output:\n{r.error_summary}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Spec parser
# ---------------------------------------------------------------------------

_KNOWN_CMDS = {
    # Frontend
    "pnpm tsc --noemiit": None,  # typo variant — handled below
    "tsc --noemit": ["pnpm", "exec", "tsc", "--noEmit"],
    "npm run lint": ["pnpm", "run", "lint"],
    "pnpm run lint": ["pnpm", "run", "lint"],
    "pnpm lint": ["pnpm", "run", "lint"],
    "eslint": ["pnpm", "exec", "eslint", "src", "--ext", ".ts,.tsx", "--max-warnings", "0"],
    # Backend
    "pytest": ["python", "-m", "pytest"],
    "python -m pytest": ["python", "-m", "pytest"],
    "python -m py_compile": None,  # handled below
    "flake8": ["python", "-m", "flake8", "--max-line-length", "120"],
}


def _resolve_cmd(raw_line: str) -> tuple[list[str], Path] | None:
    """
    Given a raw command string from the spec, return (argv, cwd) or None if
    we cannot safely run it.
    """
    stripped = raw_line.strip().lstrip("$").strip()
    lower = stripped.lower()

    # TypeScript check
    if re.search(r"tsc\b.*--noemit", lower):
        return ["pnpm", "exec", "tsc", "--noEmit"], _FRONTEND_DIR

    # Vite production build (catches runtime import resolution that tsc misses)
    if re.search(r"pnpm\s+build|npm\s+run\s+build|vite\s+build", lower):
        return ["pnpm", "build", "--mode", "production"], _FRONTEND_DIR

    # pnpm / npm lint
    if re.search(r"(pnpm|npm)\s+run\s+lint", lower) or re.search(r"pnpm\s+lint\b", lower):
        return ["pnpm", "run", "lint"], _FRONTEND_DIR

    # ESLint standalone
    if lower.startswith("eslint"):
        return ["pnpm", "exec", "eslint", "src", "--ext", ".ts,.tsx", "--max-warnings", "0"], _FRONTEND_DIR

    # pytest
    if re.search(r"pytest\b", lower):
        # Extract optional path argument
        args = shlex.split(stripped)
        return ["python", "-m"] + args, _PROJECT_ROOT

    # py_compile syntax check
    if re.search(r"py_compile|python.*-m\s+py_compile", lower):
        args = shlex.split(stripped)
        return args, _PROJECT_ROOT

    # Generic python -m commands (safe subset only)
    if re.match(r"python\s+-m\s+(pytest|flake8|mypy|pylint)", lower):
        return shlex.split(stripped), _PROJECT_ROOT

    return None


def parse_verification_commands(spec_text: str) -> list[VerificationCommand]:
    """
    Extracts commands from the '## Verification Commands' section of a spec.

    Accepted line formats:
        ```
        pnpm tsc --noEmit
        pytest backend/tests/test_jit.py
        ```
    or bare lines:
        - `pnpm tsc --noEmit`
        - pnpm run lint
    """
    section_match = re.search(
        r"##\s+Verification Commands?\s*\n(.*?)(?=\n##|\Z)",
        spec_text,
        re.DOTALL | re.IGNORECASE,
    )
    if not section_match:
        return []

    section_body = section_match.group(1)

    # Extract lines that look like commands (ignore pure markdown prose)
    cmd_pattern = re.compile(
        r"(?:^\s*```[a-z]*\s*$.*?^\s*```\s*$|^\s*[-*]?\s*`([^`]+)`\s*$|^\s*(\$?\s*[\w./][\w./ \-\-=]+))",
        re.MULTILINE | re.DOTALL,
    )

    raw_lines: list[str] = []
    # Simple line-by-line extraction
    for line in section_body.splitlines():
        stripped = line.strip()
        # Remove list markers and inline backticks
        stripped = re.sub(r"^[-*]\s+", "", stripped)
        stripped = stripped.strip("`")
        stripped = stripped.lstrip("$").strip()
        if len(stripped) < 4:
            continue
        # Must look like a command (starts with a word or tool name)
        if re.match(r"^[\w./]", stripped):
            raw_lines.append(stripped)

    commands: list[VerificationCommand] = []
    for raw in raw_lines:
        resolved = _resolve_cmd(raw)
        if resolved is None:
            continue
        argv, cwd = resolved
        commands.append(
            VerificationCommand(raw=raw, label=raw[:80], cmd=argv, cwd=cwd)
        )

    return commands


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_verification_suite(
    commands: list[VerificationCommand],
    verbose: bool = True,
) -> VerificationResult:
    """
    Runs each VerificationCommand in sequence.
    Short-circuits on the first FAIL (remaining commands are marked SKIP).
    """
    result = VerificationResult()
    failed = False

    for vc in commands:
        if failed:
            result.commands.append(
                CommandResult(command=vc, status=CommandStatus.SKIP)
            )
            continue

        if verbose:
            print(f"   🧪  Running: {vc.label}")

        t0 = time.monotonic()
        try:
            proc = subprocess.run(
                vc.cmd,
                cwd=str(vc.cwd),
                capture_output=True,
                text=True,
                timeout=vc.timeout,
            )
            duration = time.monotonic() - t0
            if proc.returncode == 0:
                cr = CommandResult(
                    command=vc,
                    status=CommandStatus.PASS,
                    stdout=proc.stdout,
                    duration=duration,
                )
            else:
                cr = CommandResult(
                    command=vc,
                    status=CommandStatus.FAIL,
                    stdout=proc.stdout,
                    stderr=proc.stderr,
                    duration=duration,
                )
                failed = True
        except subprocess.TimeoutExpired as exc:
            duration = time.monotonic() - t0
            cr = CommandResult(
                command=vc,
                status=CommandStatus.TIMEOUT,
                stderr=f"Command timed out after {vc.timeout}s",
                duration=duration,
            )
            failed = True
        except FileNotFoundError:
            cr = CommandResult(
                command=vc,
                status=CommandStatus.SKIP,
                stderr=f"Command not found: {vc.cmd[0]}",
                duration=0.0,
            )

        result.commands.append(cr)
        icon = {"PASS": "✅", "FAIL": "❌",
                "SKIP": "⏭️", "TIMEOUT": "⏰"}[cr.status]
        if verbose:
            print(f"      {icon} {cr.status} ({cr.duration:.1f}s)")

    return result


# ---------------------------------------------------------------------------
# Inner Loop (Pillar 3)
# ---------------------------------------------------------------------------

def inner_loop(
    spec_text: str,
    builder_fn: Callable[[str, str | None], bool],
    max_rounds: int = 5,
    verbose: bool = True,
    intent: str = "",
    target_file: Path | None = None,
    oracle_trigger_round: int = 2,
) -> bool:
    """
    Autonomous self-healing execution loop.

    Flow:
        1. Parse Verification Commands from spec.
        2. Call builder_fn(spec_text, error_context) → writes code to disk.
        3. Run Verification Suite.
        4. If all pass → return True.
        5. If failure → package error, call builder_fn(spec_text, error) again.
        6. After oracle_trigger_round consecutive failures, call JIT Oracle
           Lifeline and inject Rescue Protocol into the next error_feedback.
        7. Repeat up to max_rounds.

    Args:
        spec_text:            The full spec markdown text.
        builder_fn:           A callable(spec_text, error_feedback) -> bool.
                              MUST write the generated code to disk and return
                              True on success (or False if the LLM returned
                              nothing useful).
        max_rounds:           Maximum self-healing iterations before giving up.
        verbose:              Print progress.
        intent:               Human-readable goal; passed to Oracle on escalation.
        target_file:          Path to the output file; Oracle reads it for context.
        oracle_trigger_round: Escalate to Oracle after this many consecutive
                              failures (default: 2).  Set to 0 to disable.

    Returns:
        True if the suite passed before max_rounds, False otherwise.
    """
    commands = parse_verification_commands(spec_text)

    if not commands:
        if verbose:
            print("⚠️  No Verification Commands found in spec — running builder once.")
        return builder_fn(spec_text, None)

    if verbose:
        print(f"🔬  Found {len(commands)} verification command(s).")

    error_feedback: str | None = None
    _consecutive_failures = 0
    _oracle_fired = False  # only call Oracle once per inner_loop run

    for round_num in range(1, max_rounds + 1):
        if verbose:
            if error_feedback:
                print(
                    f"\n🔄  Inner-Loop round {round_num}/{max_rounds} (error feedback active)...")
            else:
                print(
                    f"\n⚡  Inner-Loop round {round_num}/{max_rounds} — generating code...")

        ok = builder_fn(spec_text, error_feedback)
        if not ok:
            if verbose:
                print("❌  builder_fn returned failure — aborting inner loop.")
            return False

        if verbose:
            print("🧪  Running Verification Suite...")
        vr = run_verification_suite(commands, verbose=verbose)

        if vr.passed:
            if verbose:
                print(f"\n🎉  All checks PASSED on round {round_num}!")
            return True

        _consecutive_failures += 1
        failure = vr.first_failure
        raw_error = (
            f"Your code failed the automated verification check.\n"
            f"Command: `{failure.command.label}`\n"
            f"Error output:\n{failure.error_summary}\n\n"
            f"Fix ALL issues listed above before resubmitting. "
            f"Do NOT repeat the same mistake. Study every line of the error carefully."
        ) if failure else (error_feedback or "Unknown verification failure.")

        # ── JIT Oracle Lifeline ──────────────────────────────────────────
        # After oracle_trigger_round consecutive failures, phone the Oracle
        # for an unpolluted, outside-the-box Rescue Protocol.
        if (
            oracle_trigger_round > 0
            and _consecutive_failures >= oracle_trigger_round
            and not _oracle_fired
            and _oracle_call is not None
        ):
            _oracle_fired = True
            _oracle_intent = intent or "(see spec below)\n" + spec_text[:800]
            _current_code = ""
            if target_file and target_file.exists():
                try:
                    _current_code = target_file.read_text(encoding="utf-8")
                except OSError:
                    pass
            if verbose:
                print(
                    f"\n⚠️  Swarm detecting high uncertainty/failure loop ({_consecutive_failures} failures).")
            rescue_protocol = _oracle_call(
                intent=_oracle_intent,
                current_code=_current_code,
                error_logs=raw_error,
            )
            if verbose:
                print("🔄  Chief adopting Oracle Rescue Protocol...")
            raw_error = (
                f"🚨 ORACLE RESCUE PROTOCOL (adopt this strategy immediately) 🚨\n"
                f"{rescue_protocol}\n\n"
                f"--- ORIGINAL VERIFICATION ERROR ---\n{raw_error}"
            )

        error_feedback = raw_error
        if verbose:
            print(
                f"\n⚠️  Verification FAILED — feeding error back to Builder (round {round_num+1})...")

    # ── Strike 3: Burn & Replace ─────────────────────────────────────────────
    # Inner loop exhausted AND the Oracle has already weighed in — the file is
    # beyond patching.  Wipe it, force a clean rewrite from scratch.
    if _oracle_fired and target_file is not None and target_file.exists():
        if verbose:
            print(f"\n{'🔥' * 10}")
            print(f"🔥  STRIKE 3 — BURN & REPLACE")
            print(f"   File deemed corrupt after {max_rounds} rounds + Oracle: {target_file.name}")
            print(f"   Wiping target file and rewriting from spec from scratch...")
            print(f"{'🔥' * 10}\n")
        # Overwrite with empty file to guarantee a clean AST state
        target_file.write_text("", encoding="utf-8")
        burn_feedback = (
            "🔥 BURN & REPLACE DIRECTIVE 🔥\n"
            "The previous implementation is corrupted beyond repair.\n"
            "The target file has been WIPED EMPTY. This is a clean-sheet rebuild.\n"
            "DO NOT reference or patch any previous code. Start from first principles.\n"
            "Read the spec from the top and write a COMPLETE, correct file.\n"
            "Every import, type, and component must be freshly derived from the spec.\n"
            f"\n--- LAST KNOWN ERRORS (do not repeat these) ---\n{error_feedback or '(unknown)'}"
        )
        ok = builder_fn(spec_text, burn_feedback)
        if ok:
            if verbose:
                print("🧪  Running final Burn & Replace verification...")
            vr_final = run_verification_suite(commands, verbose=verbose)
            if vr_final.passed:
                if verbose:
                    print(f"\n🎉  BURN & REPLACE PASSED — clean rebuild verified!")
                return True
            if verbose:
                print(f"❌  Burn & Replace also failed — manual intervention required.")
                print(f"    Last error: {vr_final.first_failure.error_summary[:300] if vr_final.first_failure else 'unknown'}")
        else:
            if verbose:
                print("❌  Burn & Replace builder_fn returned failure.")
        return False
    # ─────────────────────────────────────────────────────────────────────────

    if verbose:
        print(
            f"\n❌  Inner-Loop exhausted {max_rounds} rounds without passing. Last error saved.")
    return False


# ---------------------------------------------------------------------------
# CLI smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys as _sys

    sample_spec = """
# Spec: Test Feature

**Component:** `frontend/src/components/views/TestView.tsx`

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
"""
    cmds = parse_verification_commands(sample_spec)
    print(f"Parsed {len(cmds)} commands:")
    for c in cmds:
        print(f"  [{c.label}]  argv={c.cmd}  cwd={c.cwd}")
