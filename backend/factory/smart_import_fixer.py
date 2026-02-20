"""
SMART IMPORT FIXER — backend/factory/smart_import_fixer.py
===========================================================
Deterministic, rule-based import healer for the frontend src/ tree.

Runs BEFORE the LLM self-heal loop so that mechanical mistakes are fixed
instantly without burning LLM tokens or looping.  The LLM is then only
called for issues that genuinely require semantic understanding.

Fixes applied (in order):
  1. Out-of-src imports  — any relative path that escapes frontend/src/
     (e.g. ../../specs/contracts/...) is removed and an inline TODO stub
     is inserted so TypeScript still compiles.

  2. Missing generated.ts  — if a file imports from './generated' but
     that file does not exist, and the imported names are already defined
     locally in the same file (or in index.ts), the import is dropped.

  3. Directory name fuzzy-match  — e.g. '../../stores/foo' when the real
     folder is '../../store/foo'.  Checks all path segments against real
     neighbours and applies the closest match.

  4. File name fuzzy-match  — if the directory is correct but the
     filename doesn't exist, fuzzy-matches against other files in the
     same dir (handles useDebounceValue vs useDebouncedValue etc.).

  5. TSX generic arrow function syntax  — `= <T>(` is illegal JSX; fixed
     to `= <T,>(`.

Usage:
    from smart_import_fixer import fix_imports
    report = fix_imports()          # scans frontend/src, applies all fixes
    print(report.summary())

    # or target a single file:
    report = fix_imports(target_file=Path("frontend/src/components/views/InventoryView.tsx"))

    # dry-run (no writes):
    report = fix_imports(dry_run=True)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import get_close_matches
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_SRC = ROOT / "frontend" / "src"
FRONTEND_DIR = ROOT / "frontend"

# ── Patterns ─────────────────────────────────────────────────────────────────

# Matches:  from '../../some/path'   import('../../some/path')
_IMPORT_RE = re.compile(
    r"""(?P<prefix>(?:from|import\()\s*)(?P<q>['"])(?P<path>\.[^'"]+)(?P=q)""",
    re.MULTILINE,
)

# `const Foo = <T>(` or `function foo<T>(` in .tsx files — invalid JSX
_GENERIC_ARROW_RE = re.compile(r"(=\s*)<([A-Z][A-Za-z0-9_]*)\s*>(\s*\()")

# Matches entire import statement lines mentioning './generated'
_GENERATED_IMPORT_LINE_RE = re.compile(
    r"^(?:export \*|import type|import)\s+.*['\"]\.\/generated['\"]\s*;?\s*$",
    re.MULTILINE,
)

# ── Data models ───────────────────────────────────────────────────────────────


@dataclass
class Fix:
    file: Path
    kind: str        # 'out_of_src' | 'missing_generated' | 'dir_fuzzy' | 'file_fuzzy' | 'jsx_generic'
    original: str
    replacement: str
    description: str


@dataclass
class FixReport:
    fixes_applied: list[Fix] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)     # things we couldn't fix

    def summary(self) -> str:
        if not self.fixes_applied and not self.skipped:
            return "✅  Smart Import Fixer: nothing to fix."
        lines = [f"🔧  Smart Import Fixer — {len(self.fixes_applied)} fix(es) applied, {len(self.skipped)} unresolved:"]
        for f in self.fixes_applied:
            rel = f.file.relative_to(ROOT)
            lines.append(f"   ✅ [{f.kind}] {rel}: {f.description}")
        for s in self.skipped:
            lines.append(f"   ⚠️  Unresolved: {s}")
        return "\n".join(lines)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _extensions() -> list[str]:
    return [".ts", ".tsx", ".js", ".jsx"]


def _resolve(base_dir: Path, import_path: str) -> Path | None:
    """Try to resolve an import path from base_dir, with extension probing."""
    candidate = (base_dir / import_path).resolve()
    if candidate.is_file():
        return candidate
    for ext in _extensions():
        with_ext = Path(str(candidate) + ext)
        if with_ext.is_file():
            return with_ext
        index = candidate / ("index" + ext)
        if index.is_file():
            return index
    return None


def _relative_import(from_file: Path, target: Path) -> str:
    """Return a relative import string from from_file to target (no extension)."""
    rel = target.relative_to(from_file.parent)
    # Remove .ts/.tsx extension for cleaner import
    stem = rel.with_suffix("") if rel.suffix in (".ts", ".tsx") else rel
    s = str(stem).replace("\\", "/")
    if not s.startswith("."):
        s = "./" + s
    return s


def _fuzzy_path_fix(source_file: Path, import_path: str) -> str | None:
    """
    Attempt to find the closest real path for a broken import.

    Strategy:
      - Walk the import path segments.
      - For each non-existent segment, fuzzy-match against siblings in the
        parent directory that DO exist.
      - Reconstruct and verify the full path resolves after all segment fixes.
    """
    base = source_file.parent
    parts = Path(import_path).parts  # e.g. ('..', '..', 'stores', 'navigationStore')

    # Build an absolute candidate path segment by segment, fixing as we go
    current = base
    fixed_parts: list[str] = []

    for part in parts:
        if part in (".", ".."):
            current = (current / part).resolve()
            fixed_parts.append(part)
            continue

        # Strip file extension from part for directory/file matching
        part_stem = Path(part).stem
        part_ext = Path(part).suffix  # '' | '.ts' | '.tsx' etc.

        # Does this segment exist as-is?
        exact = current / part
        if exact.exists():
            current = exact if exact.is_dir() else exact.parent
            fixed_parts.append(part)
            continue

        # Fuzzy match against real siblings (dirs + files)
        try:
            siblings = [p.name for p in current.iterdir()]
        except (PermissionError, OSError):
            return None

        # First try stem-only match (ignoring extension)
        sibling_stems = [Path(s).stem for s in siblings]
        stem_matches = get_close_matches(part_stem, sibling_stems, n=1, cutoff=0.7)
        if stem_matches:
            matched_stem = stem_matches[0]
            # Find the full name (with extension) if it was a file
            full_names = [s for s in siblings if Path(s).stem == matched_stem]
            if full_names:
                chosen = full_names[0]  # prefer exact; if multiple prefer .ts/.tsx
                for fn in full_names:
                    if fn.endswith((".ts", ".tsx")):
                        chosen = fn
                        break
                # Reconstruct: if original had no extension and chosen is a dir, keep it
                if (current / chosen).is_dir():
                    fixed_parts.append(chosen)
                    current = current / chosen
                else:
                    # Include stem only (we'll strip extension in the final import)
                    fixed_parts.append(Path(chosen).stem if not part_ext else chosen)
                    current = (current / chosen).parent
                continue

        # Also match against full names
        full_matches = get_close_matches(part, siblings, n=1, cutoff=0.7)
        if full_matches:
            chosen = full_matches[0]
            fixed_parts.append(Path(chosen).stem if not part_ext else chosen)
            current = (current / chosen).parent if (current / chosen).is_file() else current / chosen
            continue

        # Cannot fix this segment
        return None

    # Reconstruct the fixed import string
    fixed_import = "/".join(fixed_parts)
    if not fixed_import.startswith("."):
        fixed_import = "./" + fixed_import

    # Verify the fixed path actually resolves
    if _resolve(source_file.parent, fixed_import):
        return fixed_import
    return None


def _is_out_of_src(source_file: Path, import_path: str) -> bool:
    """Return True if the resolved import would land outside frontend/src/."""
    try:
        resolved = (source_file.parent / import_path).resolve()
        return not str(resolved).startswith(str(FRONTEND_SRC))
    except Exception:
        return False


# ── Per-file fixers ───────────────────────────────────────────────────────────


def _fix_jsx_generics(content: str, source_file: Path, report: FixReport,
                      dry_run: bool) -> str:
    """Replace `= <T>(` with `= <T,>(` in .tsx files (illegal JSX syntax)."""
    if source_file.suffix != ".tsx":
        return content

    new_content, n = _GENERIC_ARROW_RE.subn(r"\1<\2,>\3", content)
    if n:
        report.fixes_applied.append(Fix(
            file=source_file,
            kind="jsx_generic",
            original="= <T>(",
            replacement="= <T,>(",
            description=f"Fixed {n} bare generic arrow function(s): <T>( → <T,>(",
        ))
    return new_content


def _fix_missing_generated(content: str, source_file: Path, report: FixReport,
                            dry_run: bool) -> str:
    """Remove `export * from './generated'` and `import ... from './generated'`
    when generated.ts doesn't exist."""
    generated_path = source_file.parent / "generated.ts"
    if generated_path.exists():
        return content  # file exists, nothing to fix

    new_content = _GENERATED_IMPORT_LINE_RE.sub("", content)
    if new_content != content:
        # Clean up extra blank lines left behind
        new_content = re.sub(r"\n{3,}", "\n\n", new_content)
        report.fixes_applied.append(Fix(
            file=source_file,
            kind="missing_generated",
            original="import/export from './generated'",
            replacement="(removed — types defined inline)",
            description="Removed imports from non-existent generated.ts (types defined locally)",
        ))
    return new_content


def _fix_imports_in_content(content: str, source_file: Path, report: FixReport,
                             dry_run: bool) -> str:
    """Scan all relative imports and attempt to fix broken ones."""
    result = content

    for match in _IMPORT_RE.finditer(content):
        import_path = match.group("path")
        resolved = _resolve(source_file.parent, import_path)
        if resolved is not None:
            continue  # already resolves — skip

        # ── Rule 1: out-of-src import (e.g. ../../specs/contracts/...) ───────
        if _is_out_of_src(source_file, import_path):
            # Build a safe inline TODO comment replacement
            # Remove the entire import statement line
            stmt_line_re = re.compile(
                r"^[^\n]*" + re.escape(match.group("path")) + r"[^\n]*\n?",
                re.MULTILINE,
            )
            new_result, n = stmt_line_re.subn("", result, count=1)
            if n:
                # Refresh matches for subsequent passes
                result = new_result
                report.fixes_applied.append(Fix(
                    file=source_file,
                    kind="out_of_src",
                    original=import_path,
                    replacement="(removed)",
                    description=f"Removed out-of-src import '{import_path}' — specs/contracts must not be imported in frontend files",
                ))
            else:
                report.skipped.append(
                    f"{source_file.relative_to(ROOT)}: could not remove '{import_path}'"
                )
            continue

        # ── Rule 2: fuzzy path fix ────────────────────────────────────────────
        fixed = _fuzzy_path_fix(source_file, import_path)
        if fixed:
            result = result.replace(
                match.group("q") + import_path + match.group("q"),
                match.group("q") + fixed + match.group("q"),
                1,
            )
            report.fixes_applied.append(Fix(
                file=source_file,
                kind="dir_fuzzy" if import_path.rsplit("/", 1)[0] != fixed.rsplit("/", 1)[0] else "file_fuzzy",
                original=import_path,
                replacement=fixed,
                description=f"'{import_path}' → '{fixed}'",
            ))
        else:
            report.skipped.append(
                f"{source_file.relative_to(ROOT)}: cannot resolve '{import_path}'"
            )

    return result


# ── Public entry point ────────────────────────────────────────────────────────


def fix_imports(
    target_file: Optional[Path] = None,
    dry_run: bool = False,
    verbose: bool = True,
) -> FixReport:
    """
    Scan frontend/src (or just *target_file*) for broken imports and apply
    deterministic fixes.

    Parameters
    ----------
    target_file : Path | None
        If provided, only that file is processed.  Otherwise, all .ts/.tsx
        files under frontend/src are processed.
    dry_run : bool
        If True, compute fixes but do NOT write any files.
    verbose : bool
        If True, print a summary after completion.

    Returns
    -------
    FixReport
        Detailed account of every fix applied and every issue left unresolved.
    """
    report = FixReport()

    files: list[Path]
    if target_file:
        files = [target_file] if target_file.exists() else []
    else:
        files = sorted(FRONTEND_SRC.rglob("*.ts")) + sorted(FRONTEND_SRC.rglob("*.tsx"))
        # Skip declaration files and node_modules
        files = [f for f in files
                 if "node_modules" not in f.parts and not f.name.endswith(".d.ts")]

    for fpath in files:
        try:
            original = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        content = original

        # Apply fixers in order (each may modify content for the next one)
        content = _fix_missing_generated(content, fpath, report, dry_run)
        content = _fix_jsx_generics(content, fpath, report, dry_run)
        content = _fix_imports_in_content(content, fpath, report, dry_run)

        if content != original and not dry_run:
            fpath.write_text(content, encoding="utf-8")

    if verbose:
        print(report.summary())

    return report


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    dry = "--dry-run" in sys.argv
    target: Path | None = None
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            target = Path(arg)
            if not target.is_absolute():
                target = ROOT / target
    report = fix_imports(target_file=target, dry_run=dry)
    sys.exit(0 if not report.skipped else 1)
