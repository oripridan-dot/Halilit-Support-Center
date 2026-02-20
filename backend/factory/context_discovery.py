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

try:
    from backend.factory.hippocampus import swarm_memory as _swarm_memory
    _HIPPOCAMPUS_AVAILABLE = True
except Exception:  # noqa: BLE001
    _HIPPOCAMPUS_AVAILABLE = False
    _swarm_memory = None  # type: ignore[assignment]

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

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
# Holographic Spec — Hydration Engine
# ---------------------------------------------------------------------------

def parse_holographic_spec(spec_path: str | Path) -> dict:
    """
    Parses a Markdown spec file, extracting YAML frontmatter and the main body.

    Returns a dict with two keys:
      - ``metadata``: parsed YAML dict (empty dict for legacy specs without frontmatter)
      - ``content``:  the Markdown body after the closing ``---``

    Falls back gracefully for any spec that does not yet have YAML frontmatter.
    """
    spec_file = Path(spec_path)
    if not spec_file.exists():
        return {"metadata": {}, "content": ""}

    raw_text = spec_file.read_text(encoding="utf-8")

    # Match YAML frontmatter between --- delimiters
    match = re.match(r"^---\n(.*?)\n---\n(.*)", raw_text, re.DOTALL)
    if match:
        yaml_text = match.group(1)
        body = match.group(2)
        if _YAML_AVAILABLE:
            try:
                metadata = yaml.safe_load(yaml_text) or {}
                return {"metadata": metadata, "content": body.strip()}
            except yaml.YAMLError as exc:
                print(f"⚠️  YAML parse error in {spec_file.name}: {exc}")
        else:
            # PyYAML not installed — attempt a minimal key-value parse
            print("⚠️  PyYAML not available; using raw spec body.")
        return {"metadata": {}, "content": body.strip()}

    # Legacy spec — no YAML frontmatter
    return {"metadata": {}, "content": raw_text}


def hydrate_context(spec_path: str | Path) -> str:
    """
    Hydration Engine: turns a Holographic Spec into a rich, real-time context
    block ready to be injected into an LLM prompt.

    Pipeline
    --------
    1. Parse YAML frontmatter (governance, dependencies / api_contracts,
       ui_dependencies, golden_scenarios_validation).
    2. Inject governance directives as **CRITICAL DIRECTIVES**.
    3. Fetch the live file content of every declared dependency and embed it.
    4. Append the spec intent body.

    Falls back transparently for legacy specs: returns the raw Markdown text.
    """
    spec_file = Path(spec_path)
    print(f"🌊 Hydrating Holographic Spec: {spec_file.name}...")

    parsed = parse_holographic_spec(spec_path)
    metadata: dict = parsed.get("metadata", {})
    intent_body: str = parsed.get("content", "")

    hydrated: list[str] = []

    # ── 1. Governance Rules ────────────────────────────────────────────────
    governance: list[str] = metadata.get("governance", [])
    if governance:
        hydrated.append("=" * 56)
        hydrated.append("🏛️  GOVERNANCE RULES — STRICTLY ENFORCED")
        hydrated.append("=" * 56)
        for rule in governance:
            hydrated.append(f"  • {rule}")
        hydrated.append("=" * 56 + "\n")

    # ── 2. Hydrate all dependency categories ──────────────────────────────
    # Merge keys that all represent live file dependencies
    dep_groups: list[tuple[str, list[str]]] = [
        ("API CONTRACTS",              metadata.get("api_contracts", [])),
        ("LIVE DEPENDENCIES",          metadata.get("dependencies", [])),
        ("UI DEPENDENCIES",            metadata.get("ui_dependencies", [])),
        ("GOLDEN SCENARIOS VALIDATION", metadata.get(
            "golden_scenarios_validation", [])),
    ]

    any_deps = any(deps for _, deps in dep_groups)
    if any_deps:
        hydrated.append("=" * 56)
        hydrated.append("🔗 REAL-TIME CODEBASE STATE (fetched at build time)")
        hydrated.append("=" * 56)

        for group_label, deps in dep_groups:
            if not deps:
                continue
            hydrated.append(f"\n[ {group_label} ]")
            for dep in deps:
                dep_path = _PROJECT_ROOT / dep
                if dep_path.exists():
                    raw = dep_path.read_text(
                        encoding="utf-8", errors="replace")
                    # Cap very large files to avoid prompt bloat
                    if len(raw) > 15_000:
                        raw = raw[:15_000] + \
                            "\n... [CONTENT TRUNCATED — file exceeds 15 000 chars] ..."
                    hydrated.append(f"\n--- 📄  {dep} ---")
                    hydrated.append(raw)
                else:
                    hydrated.append(
                        f"\n--- ⚠️  WARNING: declared dependency not found: {dep} ---"
                    )

        hydrated.append("\n" + "=" * 56 + "\n")

    # ── 3. Spec Intent ────────────────────────────────────────────────────
    hydrated.append("=" * 56)
    hydrated.append("🎯 SPECIFICATION INTENT")
    hydrated.append("=" * 56)
    hydrated.append(intent_body)

    return "\n".join(hydrated)


# ---------------------------------------------------------------------------
# Vector Memory — Hippocampus integration
# ---------------------------------------------------------------------------

def dynamic_vector_discovery(task_intent: str) -> str:
    """
    Semantic Vector DB recall replacing brute-force file scanning.

    Queries the Hippocampus (ChromaDB) for memory fragments whose *embedded
    meaning* best matches the task intent.  Falls back to an informational
    string if the Hippocampus is offline or empty.

    Architecture role: Gap 1 remediation — prevents Context Collapse by
    returning only the 2-3 most relevant code fragments instead of loading
    the full repository into the prompt.

    Args:
        task_intent: Natural-language description of the agent's current task
                     (e.g. "Update the search debounce logic in GlobalSearch").

    Returns:
        A formatted context block ready to inject into an LLM prompt,
        or a fallback warning string if no relevant memories exist.
    """
    if not _HIPPOCAMPUS_AVAILABLE or _swarm_memory is None:
        return "⚠️ Hippocampus unavailable. Falling back to text-search context discovery."

    memories = _swarm_memory.recall(task_intent)

    if not memories:
        return "⚠️ Hippocampus empty. No memories encoded yet — relying on default context..."

    context_block = "=== 🧠 HIPPOCAMPUS RECALL (VECTOR MEMORY) ===\n"
    for mem in memories:
        context_block += f"\n--- 📄 {mem['filepath']} ---\n"
        context_block += f"Purpose: {mem['description']}\n"
        # Truncate individual fragments to keep the prompt razor-sharp
        context_block += f"Code Snippet:\n{mem['content'][:2000]}\n"

    context_block += "\n=== END HIPPOCAMPUS RECALL ===\n"
    return context_block


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
