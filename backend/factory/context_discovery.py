"""
CONTEXT DISCOVERY — backend/factory/context_discovery.py
=========================================================
Gives Factory agents "eyes" — dynamic, runtime codebase search instead of
hardcoded file lists.

Public API
----------
    search_codebase(query, max_results=8) -> list[SearchHit]
    read_file_context(path, max_chars=4000) -> str
    build_dynamic_context(queries, paths=[]) -> str

This module is intentionally dependency-light: pure stdlib + pathspec (optional).
"""

from __future__ import annotations

import fnmatch
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

# ---------------------------------------------------------------------------
# Root introspection
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Directories to skip (generated, deps, caches)
_SKIP_DIRS = {
    "node_modules", "__pycache__", ".git", ".venv", "venv", "dist", "build",
    ".next", "coverage", ".pytest_cache", "jit_cache", ".github",
}

# Source extensions worth searching
_SRC_EXTS = {
    ".ts", ".tsx", ".py", ".md", ".json", ".js", ".jsx", ".css", ".html",
}

# Max chars per match snippet
_SNIPPET_CHARS = 300


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class SearchHit:
    path: str          # repo-relative path
    line: int          # 1-based line number of the match
    snippet: str       # surrounding context (~5 lines)
    score: float = 1.0  # relevance signal (higher = more relevant)

    def format(self) -> str:
        return f"  {self.path}:{self.line}\n{self.snippet}"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _iter_source_files(root: Path) -> Iterator[Path]:
    """Recursively yield source files, skipping noise directories."""
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skip-dirs in-place
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fpath.suffix.lower() in _SRC_EXTS:
                yield fpath


def _lines_around(lines: list[str], idx: int, radius: int = 3) -> str:
    """Return a slice of lines surrounding index `idx`."""
    start = max(0, idx - radius)
    end = min(len(lines), idx + radius + 1)
    numbered = [
        f"{start + i + 1:>4}: {lines[start + i]}" for i in range(end - start)]
    return "\n".join(numbered)


def _score_hit(query_tokens: list[str], path: str, snippet: str) -> float:
    """
    Simple heuristic score: how many query tokens appear in path + snippet.
    Component/type definition files score higher.
    """
    combined = (path + " " + snippet).lower()
    token_hits = sum(1 for t in query_tokens if t in combined)
    bonus = 0.5 if any(x in path for x in [
                       "/types/", "/hooks/", "/components/", "models.py"]) else 0
    return float(token_hits) + bonus


# ---------------------------------------------------------------------------
# Core search
# ---------------------------------------------------------------------------

def search_codebase(
    query: str,
    max_results: int = 8,
    root: Path | None = None,
) -> list[SearchHit]:
    """
    Full-text search across the source tree.

    Splits `query` into tokens, searches every source file for lines matching
    ANY token (case-insensitive), ranks by relevance, and returns up to
    `max_results` non-duplicate file hits.

    Example
    -------
        hits = search_codebase("related products carousel")
        for h in hits:
            print(h.format())
    """
    root = root or _PROJECT_ROOT
    tokens = [t.lower() for t in re.split(r"\W+", query) if len(t) >= 3]
    if not tokens:
        return []

    # Build a combined regex for fast OR-match
    pattern = re.compile(
        "|".join(re.escape(t) for t in tokens), re.IGNORECASE
    )

    hits: list[SearchHit] = []
    seen_files: set[str] = set()

    for fpath in _iter_source_files(root):
        try:
            text = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        lines = text.splitlines()
        for idx, line in enumerate(lines):
            if pattern.search(line):
                rel = str(fpath.relative_to(root))
                # One hit per file (best match wins)
                snippet = _lines_around(lines, idx)[:_SNIPPET_CHARS]
                score = _score_hit(tokens, rel, snippet)

                if rel not in seen_files:
                    seen_files.add(rel)
                    hits.append(SearchHit(path=rel, line=idx +
                                1, snippet=snippet, score=score))
                    break  # move to next file once we have the first match

    # Sort by relevance, then trim
    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[:max_results]


def read_file_context(
    path: str | Path,
    max_chars: int = 4000,
    root: Path | None = None,
) -> str:
    """
    Read a file and return its content (up to max_chars), with a header line.
    Accepts repo-relative or absolute paths.
    """
    root = root or _PROJECT_ROOT
    fpath = Path(path)
    if not fpath.is_absolute():
        fpath = root / fpath
    if not fpath.exists():
        return f"# (file not found) {path}"
    content = fpath.read_text(encoding="utf-8", errors="replace")
    truncated = " [truncated]" if len(content) > max_chars else ""
    header = f"### File: {fpath.relative_to(root)}{truncated}\n"
    return header + "```\n" + content[:max_chars] + "\n```\n"


def build_dynamic_context(
    queries: list[str],
    extra_paths: list[str] | None = None,
    max_search_results: int = 6,
    max_file_chars: int = 3000,
) -> str:
    """
    High-level helper used by Steerer and Builder to discover relevant context.

    1. Runs each query through search_codebase.
    2. Reads the top-scoring unique files.
    3. Appends any explicitly requested extra_paths.

    Returns a formatted context block ready to inject into a prompt.
    """
    all_hits: dict[str, SearchHit] = {}  # path → best hit

    for query in queries:
        for hit in search_codebase(query, max_results=max_search_results):
            if hit.path not in all_hits or hit.score > all_hits[hit.path].score:
                all_hits[hit.path] = hit

    # Sort by score descending, take top N unique files
    ranked_paths = [
        h.path for h in sorted(all_hits.values(), key=lambda h: h.score, reverse=True)
    ][:max_search_results]

    # Merge with explicit paths
    explicit = [str(p) for p in (extra_paths or [])]
    all_paths = list(dict.fromkeys(ranked_paths + explicit)
                     )  # dedupe, preserve order

    parts: list[str] = ["--- DYNAMICALLY DISCOVERED CONTEXT ---\n"]
    for p in all_paths:
        parts.append(read_file_context(p, max_chars=max_file_chars))

    parts.append("--- END CONTEXT ---\n")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# CLI smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or "inventory grid product"
    print(f"🔍  Searching for: {query!r}\n")
    results = search_codebase(query)
    if not results:
        print("  (no results)")
    else:
        for h in results:
            print(h.format())
            print()
