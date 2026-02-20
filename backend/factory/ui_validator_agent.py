"""
UI VALIDATOR AGENT — backend/factory/ui_validator_agent.py
===========================================================
Catches frontend runtime errors that TypeScript compilation and ESLint
silently miss — specifically:

  1. **Vite import resolution failures** (wrong path, wrong folder name,
     missing file): discovered by running `pnpm build` which uses Vite's
     resolver, not tsc's resolver.

  2. **Static import map scan**: walks every .ts/.tsx file and verifies
     each relative import resolves to a real file on disk. Catches cases
     like `../../stores/foo` when the folder is actually `../../store/foo`.

  3. **Missing hook files**: any import of `../../hooks/foo` where
     `foo.ts` | `foo.tsx` does not exist.

Why a separate agent from diagnose / watchdog?
-----------------------------------------------
`diagnose` (watchdog) runs `tsc --noEmit` + `eslint`.  TypeScript's path
resolution uses tsconfig `paths` and `baseUrl` which may resolve imports
that Vite cannot find at runtime.  This agent uses Vite's own build step
as the ground-truth resolver, plus an ast-free static scan that is fast
and always-on.

Output contract (stdout):
  Exit 0  → HEALTHY  (prints "✅ UI Validation PASSED")
  Exit 1  → FAILURES (prints structured error list)

The Chief / Watchdog picks up exit code 1 and queues a 'heal' cycle.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

try:
    from smart_import_fixer import fix_imports as _smart_fix
except ImportError:
    _smart_fix = None  # type: ignore[assignment]

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
SRC_DIR = FRONTEND_DIR / "src"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Extensions to try when resolving a bare import (no extension)
_EXTENSIONS = [".ts", ".tsx", ".js", ".jsx", "/index.ts", "/index.tsx"]


class ImportError_(NamedTuple):
    source_file: Path
    import_path: str
    reason: str


def _resolve_import(source_file: Path, import_path: str) -> Path | None:
    """
    Attempt to resolve a relative import path to an absolute file.
    Returns the resolved Path if found, None otherwise.
    """
    base = source_file.parent / import_path
    # Exact match (already has extension)
    if base.exists() and base.is_file():
        return base
    # Try adding extensions
    for ext in _EXTENSIONS:
        candidate = Path(
            str(base) + ext) if not ext.startswith("/") else base / ext.lstrip("/")
        if candidate.exists():
            return candidate
    return None


def scan_imports(src_dir: Path = SRC_DIR) -> list[ImportError_]:
    """
    Walk all .ts/.tsx files under src_dir and check every relative import.
    Returns a list of ImportError_ for any import that cannot be resolved.
    """
    errors: list[ImportError_] = []
    # Match:  from '../../some/path'   or   import('../../some/path')
    pattern = re.compile(r"""(?:from|import)\s+['"](\.[^'"]+)['"]""")

    for fpath in sorted(src_dir.rglob("*.ts")) + sorted(src_dir.rglob("*.tsx")):
        # Skip declaration files and node_modules
        if "node_modules" in fpath.parts or fpath.name.endswith(".d.ts"):
            continue
        try:
            text = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in pattern.finditer(text):
            imp = match.group(1)
            if not imp.startswith("."):
                continue  # absolute / aliased — skip
            # Skip imports that appear inside comments (// or * lines)
            line_start = text.rfind('\n', 0, match.start()) + 1
            line_text = text[line_start:match.start()].lstrip()
            if line_text.startswith('//') or line_text.startswith('*'):
                continue  # comment line — skip
            resolved = _resolve_import(fpath, imp)
            if resolved is None:
                errors.append(ImportError_(
                    source_file=fpath,
                    import_path=imp,
                    reason=f"Cannot resolve '{imp}' from {fpath.relative_to(ROOT_DIR)}"
                ))
    return errors


def run_vite_build() -> tuple[bool, str]:
    """
    Run `pnpm build` (Vite production build) to catch runtime import failures.
    Returns (success: bool, output: str).
    """
    try:
        result = subprocess.run(
            ["pnpm", "build"],
            cwd=str(FRONTEND_DIR),
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = (result.stdout + "\n" + result.stderr).strip()
        return result.returncode == 0, output
    except FileNotFoundError:
        return False, "pnpm not found — is it installed?"
    except subprocess.TimeoutExpired:
        return False, "pnpm build timed out after 120 s"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def validate_ui(run_build: bool = True) -> dict:
    """
    Run the full UI validation suite.

    Returns a dict:
      {
        "passed": bool,
        "import_errors": list[str],   # human-readable
        "build_errors":  list[str],   # Vite output lines that indicate errors
        "summary":       str,
      }
    """
    sep = "─" * 52

    print(sep)
    print("🖥️  UI VALIDATOR — import scan + Vite build check")
    print(sep)

    # 1. Static import map scan (fast — no subprocess)
    print("🔍  Scanning imports in frontend/src …")
    raw_errors = scan_imports(SRC_DIR)
    import_error_msgs = [e.reason for e in raw_errors]

    if import_error_msgs:
        print(f"  ❌ {len(import_error_msgs)} broken import(s) found:")
        for msg in import_error_msgs:
            print(f"     • {msg}")

        # ── Auto-fix pass: deterministic mechanical repair ────────────────
        if _smart_fix is not None:
            print("  🔧  SmartImportFixer: attempting deterministic repair...")
            fix_report = _smart_fix()  # scans & patches entire frontend/src
            if fix_report.fixes:
                print(
                    f"     Applied {len(fix_report.fixes)} fix(es) — re-scanning...")
                raw_errors = scan_imports(SRC_DIR)  # re-scan after fixes
                import_error_msgs = [e.reason for e in raw_errors]
                if import_error_msgs:
                    print(
                        f"  ❌ {len(import_error_msgs)} import(s) remain after auto-fix:")
                    for msg in import_error_msgs:
                        print(f"     • {msg}")
                else:
                    print("  ✅ SmartImportFixer resolved all import errors.")
            else:
                print("     No deterministic fixes found — LLM heal required.")
    else:
        print("  ✅ All relative imports resolve to real files.")

    # 2. Vite production build (authoritative — catches aliased / dynamic imports)
    build_error_lines: list[str] = []
    build_passed = True

    if run_build:
        print("🏗️   Running pnpm build (Vite) …")
        build_passed, build_output = run_vite_build()

        if not build_passed:
            # Extract meaningful errors: include lines after "error during build:"
            # and lines containing known error keywords
            lines = build_output.splitlines()
            error_lines = []
            capture_next = 0
            for ln in lines:
                stripped = ln.strip()
                if not stripped:
                    continue
                if "error during build" in stripped.lower():
                    error_lines.append(stripped)
                    capture_next = 3  # capture the next 3 lines for context
                    continue
                if capture_next > 0:
                    error_lines.append(stripped)
                    capture_next -= 1
                    continue
                if any(kw in ln for kw in (
                    "Failed to resolve", "Cannot find",
                    "does not provide an export", "Module not found",
                    "[vite]", "[rollup]",
                )):
                    error_lines.append(stripped)
            build_error_lines = error_lines[:20]
            print(
                f"  ❌ Vite build FAILED — {len(build_error_lines)} error line(s):")
            for ln in build_error_lines:
                print(f"     • {ln}")
        else:
            print("  ✅ Vite build passed — no runtime import errors.")
    else:
        print("  ⏭️   Vite build skipped (run_build=False).")

    passed = not import_error_msgs and build_passed

    summary_parts = []
    if import_error_msgs:
        summary_parts.append(f"{len(import_error_msgs)} broken import(s)")
    if build_error_lines:
        summary_parts.append(
            f"Vite build errors: {build_error_lines[0][:120]}")
    if not summary_parts:
        summary_parts.append("All checks passed")

    summary = " | ".join(summary_parts)

    print(sep)
    if passed:
        print("✅ UI Validation PASSED")
    else:
        print(f"❌ UI Validation FAILED — {summary}")
    print(sep)

    return {
        "passed": passed,
        "import_errors": import_error_msgs,
        "build_errors": build_error_lines,
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    skip_build = "--no-build" in sys.argv
    result = validate_ui(run_build=not skip_build)
    sys.exit(0 if result["passed"] else 1)
