"""
UDIFF Patcher — Level 8 Liquid MCP Core  (backend/factory/udiff_patcher.py)
============================================================================
Replaces the brittle string-matching ast_patcher.py with two human-grade
patching formats that LLMs generate reliably:

  1. SEARCH/REPLACE BLOCKS (Aider format) — preferred for surgical edits:

        <<<<<<< SEARCH
        const DEBOUNCE_MS = 0;
        =======
        const DEBOUNCE_MS = 300;
        >>>>>>> REPLACE

  2. UNIFIED DIFF (standard git diff format):

        --- a/frontend/src/components/GlobalSearch.tsx
        +++ b/frontend/src/components/GlobalSearch.tsx
        @@ -40,3 +40,4 @@
          const handleChange = (e) => {
        -   dispatch(e.target.value);
        +   debounce(() => dispatch(e.target.value), DEBOUNCE_MS)();
          };

Why this beats ast_patcher:
  - LLMs output these formats natively; no string-matching drift possible.
  - A 20-line parser handles what took 270 lines of fragile regex + LLM fallback.
  - Unified Diff is invertible (git apply --reverse) — rollback is free.
  - Compatible with the Level 8 execute_bash_command MCP tool: the LLM can
    pipe output straight to `git apply` if it prefers the native path.

Public API (backward-compatible with ast_patcher):
    apply_patch(file, search, replace)        → bool
    apply_patch_batch(file, patches)          → dict
    insert_before(file, anchor, code)         → bool
    insert_after(file, anchor, code)          → bool

New Level-8 API:
    apply_search_replace_blocks(file, text)   → dict
    apply_unified_diff(udiff_text)            → dict
    apply_udiff(file, text, fmt="auto")       → dict   ← MCP tool entry point

Usage:
    from backend.factory.udiff_patcher import apply_udiff, apply_patch

    # Auto-detect format
    result = apply_udiff("frontend/src/components/GlobalSearch.tsx", patch_text)

    # Explicit Search/Replace block string
    result = apply_search_replace_blocks(
        "frontend/src/components/GlobalSearch.tsx",
        \"\"\"<<<<<<< SEARCH
const DEBOUNCE_MS = 0;
=======
const DEBOUNCE_MS = 300;
>>>>>>> REPLACE\"\"\"
    )
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Workspace root (two dirs up from this file: factory/ → backend/ → root)
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent.parent
_FRONTEND_DIR = _ROOT / "frontend"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve(file_path: str | Path) -> Path:
    """Resolve a workspace-relative or absolute path to an absolute Path."""
    p = Path(file_path)
    if not p.is_absolute():
        p = _ROOT / p
    return p.resolve()


def _normalise(text: str) -> str:
    """Normalise line endings."""
    return text.replace("\r\n", "\n")


# ---------------------------------------------------------------------------
# Format 1: Search/Replace Blocks  (<<<<<<< SEARCH … ======= … >>>>>>> REPLACE)
# ---------------------------------------------------------------------------
# Matches one or more contiguous SEARCH/REPLACE pairs in a text blob.
_SR_PATTERN = re.compile(
    r"<<<<<<< SEARCH\n(.*?)=======\n(.*?)>>>>>>> REPLACE",
    re.DOTALL,
)


def apply_search_replace_blocks(
    file_path: str | Path,
    text: str,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Parse all SEARCH/REPLACE blocks in *text* and apply them sequentially
    to *file_path*.

    Returns:
        {
            "success": bool,
            "applied":  int,   # blocks successfully applied
            "failed":   list,  # search snippets that were not found
            "message":  str,
        }
    """
    path = _resolve(file_path)
    blocks = _SR_PATTERN.findall(_normalise(text))

    if not blocks:
        return {
            "success": False,
            "applied": 0,
            "failed": [],
            "message": "No SEARCH/REPLACE blocks found in input.",
        }

    if not path.exists():
        return {
            "success": False,
            "applied": 0,
            "failed": [],
            "message": f"File not found: {path}",
        }

    content = _normalise(path.read_text(encoding="utf-8"))
    failed: list[str] = []
    applied = 0

    for raw_search, raw_replace in blocks:
        search = raw_search.strip()
        replace = raw_replace.strip()

        if search not in content:
            # Fuzzy fallback: strip trailing whitespace on every line
            search_stripped = "\n".join(l.rstrip()
                                        for l in search.splitlines())
            content_stripped_lines = "\n".join(
                l.rstrip() for l in content.splitlines())
            if search_stripped in content_stripped_lines:
                # Re-locate the actual span via stripped comparison
                idx = content_stripped_lines.index(search_stripped)
                # Count newlines to find end of matched region
                end_idx = idx + len(search_stripped)
                # Replace in original content using character-aligned splice
                content = content[:idx] + replace + content[end_idx:]
                applied += 1
                print(
                    f"   ⚙️  UDIFF: fuzzy-matched and applied block ({applied})")
            else:
                failed.append(search[:80])
                print(f"   ✗  UDIFF: anchor not found — '{search[:60]}...'")
        else:
            if not dry_run:
                content = content.replace(search, replace, 1)
            applied += 1
            print(f"   ✅ UDIFF: block {applied} applied → {path.name}")

    if not dry_run and applied > 0:
        path.write_text(content, encoding="utf-8")
        print(
            f"⚡ UDIFF Patcher: {applied}/{applied + len(failed)} blocks written to {path.name}")

    success = len(failed) == 0
    msg = (
        f"All {applied} block(s) applied to {path.name}."
        if success
        else f"{applied} applied, {len(failed)} failed in {path.name}."
    )
    return {"success": success, "applied": applied, "failed": failed, "message": msg}


# ---------------------------------------------------------------------------
# Format 2: Unified Diff  (--- a/file … +++ b/file … @@ … )
# ---------------------------------------------------------------------------

def apply_unified_diff(udiff_text: str, *, dry_run: bool = False) -> dict[str, Any]:
    """
    Apply a standard unified diff string using `git apply`.

    The diff must contain valid `--- a/…` / `+++ b/…` headers.
    Paths are resolved relative to the project root.

    Returns:
        {
            "success": bool,
            "files_patched": list[str],
            "message": str,
            "stderr": str,
        }
    """
    udiff_text = _normalise(udiff_text).strip()
    if not udiff_text:
        return {"success": False, "files_patched": [], "message": "Empty diff.", "stderr": ""}

    # Extract file names from diff header for reporting
    files_patched = re.findall(r"^\+\+\+ b/(.+)$", udiff_text, re.MULTILINE)

    # Write diff to a temp file and hand it to git apply
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".patch", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(udiff_text + "\n")
        tmp_path = tmp.name

    try:
        cmd = ["git", "apply", "--whitespace=fix"]
        if dry_run:
            cmd.append("--check")
        cmd.append(tmp_path)

        result = subprocess.run(
            cmd,
            cwd=str(_ROOT),
            capture_output=True,
            text=True,
        )
        success = result.returncode == 0
        msg = (
            f"Patch applied to: {', '.join(files_patched)}"
            if success
            else f"git apply failed: {result.stderr.strip()[:300]}"
        )
        if success:
            print(f"⚡ UDIFF Patcher (git apply): patched {files_patched}")
        else:
            print(
                f"❌ UDIFF Patcher (git apply): {result.stderr.strip()[:200]}")

        return {
            "success": success,
            "files_patched": files_patched,
            "message": msg,
            "stderr": result.stderr.strip(),
        }
    finally:
        Path(tmp_path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Unified entry point: auto-detect format
# ---------------------------------------------------------------------------

def apply_udiff(
    file_path: str | Path | None,
    text: str,
    *,
    fmt: str = "auto",
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Top-level dispatcher — auto-detects which format *text* uses and applies it.

    Formats:
        "search_replace" — Aider-style SEARCH/REPLACE blocks (file_path required)
        "unified"        — Standard unified diff (file_path optional — taken from diff header)
        "auto"           — Detect by inspecting the input (default)

    Args:
        file_path:  Target file (required for search_replace, optional for unified).
        text:       The patch text (SEARCH/REPLACE blocks or unified diff).
        fmt:        Format hint ("auto", "search_replace", "unified").
        dry_run:    Validate only; do not write.

    Returns a dict with at minimum {"success": bool, "message": str}.
    """
    text = _normalise(text).strip()

    if fmt == "auto":
        if "<<<<<<< SEARCH" in text and ">>>>>>> REPLACE" in text:
            fmt = "search_replace"
        elif re.search(r"^---\s+", text, re.MULTILINE) and re.search(r"^\+\+\+\s+", text, re.MULTILINE):
            fmt = "unified"
        else:
            # Treat as search_replace and let the parser emit a helpful error
            fmt = "search_replace"

    if fmt == "search_replace":
        if file_path is None:
            return {"success": False, "message": "file_path is required for search_replace format."}
        return apply_search_replace_blocks(file_path, text, dry_run=dry_run)

    if fmt == "unified":
        return apply_unified_diff(text, dry_run=dry_run)

    return {"success": False, "message": f"Unknown format: {fmt}"}


# ---------------------------------------------------------------------------
# Backward-compatible shim (drop-in replacement for ast_patcher)
# ---------------------------------------------------------------------------

def apply_patch(
    file_path: str | Path,
    search_block: str,
    replace_block: str,
    *,
    dry_run: bool = False,
) -> bool:
    """
    Drop-in replacement for ast_patcher.apply_patch.

    Builds a SEARCH/REPLACE block string from the arguments and delegates to
    apply_search_replace_blocks — no regex, no Wolverine LLM overhead.
    """
    block = (
        "<<<<<<< SEARCH\n"
        + search_block.strip()
        + "\n=======\n"
        + replace_block.strip()
        + "\n>>>>>>> REPLACE"
    )
    result = apply_search_replace_blocks(file_path, block, dry_run=dry_run)
    return result["success"]


def apply_patch_batch(
    file_path: str | Path,
    patches: list[dict],
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Drop-in replacement for ast_patcher.apply_patch_batch.

    Converts the list of {"search": …, "replace": …} dicts into a sequence of
    SEARCH/REPLACE blocks and applies them in a single pass.
    """
    blocks = ""
    for p in patches:
        blocks += (
            "<<<<<<< SEARCH\n"
            + p.get("search", "").strip()
            + "\n=======\n"
            + p.get("replace", "").strip()
            + "\n>>>>>>> REPLACE\n\n"
        )
    return apply_search_replace_blocks(file_path, blocks.strip(), dry_run=dry_run)


def insert_before(
    file_path: str | Path,
    anchor_line: str,
    code_to_insert: str,
    *,
    dry_run: bool = False,
) -> bool:
    """Insert code_to_insert immediately before the first occurrence of anchor_line."""
    search = anchor_line.strip()
    replace = code_to_insert.rstrip() + "\n" + anchor_line.strip()
    return apply_patch(file_path, search, replace, dry_run=dry_run)


def insert_after(
    file_path: str | Path,
    anchor_line: str,
    code_to_insert: str,
    *,
    dry_run: bool = False,
) -> bool:
    """Insert code_to_insert immediately after the first occurrence of anchor_line."""
    search = anchor_line.strip()
    replace = anchor_line.strip() + "\n" + code_to_insert.lstrip()
    return apply_patch(file_path, search, replace, dry_run=dry_run)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    print("UDIFF Patcher — Level 8 Liquid MCP Core")
    print("Usage: python udiff_patcher.py <file> <patch_text_or_file>")
    if len(sys.argv) >= 3:
        target = sys.argv[1]
        raw = sys.argv[2]
        # If arg looks like a path, read it; otherwise treat as inline text
        p = Path(raw)
        patch_text = p.read_text(encoding="utf-8") if p.exists() else raw
        result = apply_udiff(target, patch_text)
        print(result)
        sys.exit(0 if result["success"] else 1)
    else:
        print("  Provide file_path and patch text (or path to .patch file).")
