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
# Scope-violation purger
# ---------------------------------------------------------------------------
# The Builder sometimes hallucinates component code (JSX components, component
# imports) directly into hook/store/util .ts files.  This produces unresolvable
# imports that SmartImportFixer can never fix because the targets simply don't
# exist.  Detect and auto-strip these scope violations BEFORE the import scan
# so the system never gets stuck on them.

_HOOK_DIRS = {"hooks", "store", "stores", "utils", "lib", "services"}
# Marker that the Builder uses when it appends a second file's content
_APPENDED_FILE_COMMENT = re.compile(
    r"^//\s+frontend/src/", re.MULTILINE
)


def purge_scope_violations(src_dir: Path = SRC_DIR) -> list[str]:
    """
    Scan every .ts (non-.tsx) file under hook/store/utils directories.
    Auto-strips three classes of Builder hallucination that cause Vite esbuild
    to die and can never be resolved by SmartImportFixer:

      1. Appended-file block: '// frontend/src/...' comment marker
      2. JSX-in-.ts: any 'className=' in a .ts file → truncate back to the
         nearest export boundary (catches appended React components)
      3. Component imports in hook files: relative imports referencing
         'components/' that don't resolve

    Returns a list of human-readable repair messages.
    """
    repaired: list[str] = []

    for fpath in sorted(src_dir.rglob("*.ts")):
        if fpath.suffix == ".tsx":
            continue
        if not any(part in _HOOK_DIRS for part in fpath.parts):
            continue
        if "node_modules" in fpath.parts or fpath.name.endswith(".d.ts"):
            continue

        try:
            original = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        working = original

        # ── Strategy 1: truncate at appended-file marker ─────────────────
        m = _APPENDED_FILE_COMMENT.search(working)
        if m:
            working = working[: m.start()].rstrip() + "\n"
            repaired.append(
                f"[scope-purge] Truncated appended component block from {fpath.relative_to(ROOT_DIR)}"
            )

        # ── Strategy 2: JSX in .ts — className= is the smoking gun ───────
        #    Prefer: git show HEAD to restore the last clean committed version.
        #    Fallback: walk backwards and truncate at the nearest export/function
        #    boundary (removes the injected JSX block, but may lose hook body).
        jsx_hit = re.search(r'\bclassName=', working)
        if jsx_hit:
            rel_path = fpath.relative_to(ROOT_DIR)
            # ── Attempt 1: git show HEAD (non-destructive, full restore) ──
            import subprocess as _sp
            git_show = _sp.run(
                ["git", "-C", str(ROOT_DIR), "show", f"HEAD:{rel_path}"],
                capture_output=True,
                text=True,
            )
            if git_show.returncode == 0 and git_show.stdout.strip():
                working = git_show.stdout
                repaired.append(
                    f"[scope-purge] Restored {rel_path} from git HEAD (JSX-in-.ts detected)"
                )
            else:
                # ── Attempt 2: truncate at JSX boundary ──────────────────
                pre = working[: jsx_hit.start()]
                boundary = None
                for m2 in re.finditer(
                    r'^(export\s+)?(const|function|class)\s+\w',
                    pre,
                    re.MULTILINE,
                ):
                    boundary = m2  # keep scanning — want LAST match before jsx_hit
                if boundary:
                    working = working[: boundary.start()].rstrip() + "\n"
                else:
                    line_start = working.rfind("\n", 0, jsx_hit.start()) + 1
                    working = working[:line_start].rstrip() + "\n"
                repaired.append(
                    f"[scope-purge] Stripped JSX component block (className detected) from {rel_path}"
                )

        # ── Strategy 3: component imports in hook file ────────────────────
        import_pattern = re.compile(
            r"^import\s+.*?from\s+['\"](\./|\.\./).*?components/[^'\"]+['\"];?\s*$",
            re.MULTILINE,
        )
        fixed = import_pattern.sub("", working)
        if fixed != working:
            fixed = re.sub(r"\n{3,}", "\n\n", fixed).lstrip("\n")
            working = fixed
            repaired.append(
                f"[scope-purge] Stripped hallucinated component import(s) from {fpath.relative_to(ROOT_DIR)}"
            )

        if working != original:
            fpath.write_text(working, encoding="utf-8")

    return repaired

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

    # 0. Scope-violation purge (zero-LLM, deterministic)
    #    Removes hallucinated component code/imports the Builder dumps into
    #    hook/store/util .ts files — these can never be fixed by SmartImportFixer
    #    and would otherwise permanently block the system.
    purge_results = purge_scope_violations(SRC_DIR)
    if purge_results:
        print(
            f"  🧹 Scope-violation purge: {len(purge_results)} file(s) auto-repaired:")
        for r in purge_results:
            print(f"     • {r}")
    else:
        print("  ✅ Scope check: no hook/store file contamination detected.")

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
            if fix_report.fixes_applied:
                print(
                    f"     Applied {len(fix_report.fixes_applied)} fix(es) — re-scanning...")
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
            # Extract meaningful errors: only include lines that represent
            # genuine fatal build failures, not warnings or advisory notices.
            lines = build_output.splitlines()
            error_lines = []
            capture_next = 0
            for ln in lines:
                stripped = ln.strip()
                if not stripped:
                    continue
                # Skip lines that are clearly non-fatal warnings
                if any(warn_kw in stripped.lower() for warn_kw in (
                    "warn ", "warning:", "deprecated", "experimentaldecorators",
                )):
                    continue
                if "error during build" in stripped.lower():
                    error_lines.append(stripped)
                    capture_next = 3  # capture the next 3 lines for context
                    continue
                if capture_next > 0:
                    error_lines.append(stripped)
                    capture_next -= 1
                    continue
                # Only flag hard fatal resolver errors, not warnings
                if any(kw in ln for kw in (
                    "Failed to resolve", "Cannot find module",
                    "does not provide an export", "Module not found",
                    "Rollup failed", "[rollup]",
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
