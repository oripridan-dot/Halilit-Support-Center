import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import google.genai as genai

# Make context_discovery importable even when running from inside the package
_FACTORY_DIR = Path(__file__).resolve().parent
if str(_FACTORY_DIR) not in sys.path:
    sys.path.insert(0, str(_FACTORY_DIR))

try:
    from context_discovery import (
        search_codebase as _search_codebase,
        read_file_context as _read_file_context,
        build_dynamic_context as _build_dynamic_context,
        SearchHit,
    )
    _DISCOVERY_AVAILABLE = True
except ImportError:
    _DISCOVERY_AVAILABLE = False

# Load .env from project root (backend/factory -> backend -> root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# --- CONFIGURATION ---
_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
_CLIENT = genai.Client(api_key=_API_KEY) if _API_KEY else None

# --- TIERED MODEL ROUTING ---
# Tier 1: The Strategist (Strategy, Architecture, Complex Logic) — High Quality
SMART_MODEL = "gemini-2.0-flash"
# Tier 2: The Worker (Coding, Docs, Diagnostics, Grunt work) — Fast & Cheap
FAST_MODEL = "gemini-2.0-flash-lite"

# Legacy alias — keep backward compat for any external references
MODEL = SMART_MODEL


def get_project_context(target_type: str = "frontend", blackboard_file: str = "") -> str:
    """
    Loads critical project context so the Agent respects the Architecture.
    Returns a formatted string of key files to inject into prompts.

    Args:
        target_type:     "frontend" | "backend" — selects architecture files.
        blackboard_file: Optional path to a Task-Force Blackboard file.
                         When set, its contents are injected as shared context.
    """
    root = _PROJECT_ROOT
    context_parts: list[str] = []

    # --- Always inject Lessons Learned (persistent agent memory) ---
    lessons_path = root / "docs" / "LEARNED_GUIDELINES.md"
    if lessons_path.exists():
        lessons = lessons_path.read_text(encoding="utf-8")
        context_parts.append(
            f"--- CRITICAL LESSONS LEARNED (read before acting) ---\n{lessons}\n"
            f"--- END LESSONS ---\n"
        )

    # --- Task-Force Blackboard (shared context for current mission) ---
    if blackboard_file:
        bb_path = Path(blackboard_file)
        if not bb_path.is_absolute():
            bb_path = root / blackboard_file
        if bb_path.exists():
            bb_content = bb_path.read_text(encoding="utf-8")
            context_parts.append(
                f"--- TASK-FORCE BLACKBOARD (shared team context) ---\n{bb_content}\n"
                f"--- END BLACKBOARD ---\n"
            )

    if target_type == "frontend":
        files = [
            "frontend/src/types/index.ts",
            "frontend/src/styles/design-tokens.css",
            "frontend/tailwind.config.cjs",
        ]
        context_parts.append("--- FRONTEND ARCHITECTURE CONTEXT ---")
    elif target_type == "backend":
        files = [
            "backend/ingestion/data_models.py",
            "backend/mcp/schemas.py",
            "backend/source_rules.py",
        ]
        context_parts.append("--- BACKEND ARCHITECTURE CONTEXT ---")
    else:
        files = []

    for f_path in files:
        full_path = root / f_path
        if full_path.exists():
            content = full_path.read_text(encoding="utf-8", errors="replace")
            context_parts.append(f"File: {f_path}\n```\n{content}\n```\n")
        else:
            context_parts.append(f"# (not found) {f_path}")

    return "\n".join(context_parts)


def query_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.1,
    model_tier: str = "smart",
) -> str | None:
    """
    Routes the request to the appropriate model based on complexity tier.

    model_tier="smart"  → SMART_MODEL (Strategy, Architecture, Critic review)
    model_tier="fast"   → FAST_MODEL  (Coding, Docs, Diagnostics, Intent parsing)
    """
    if not _CLIENT:
        print("❌ No GEMINI_API_KEY / GOOGLE_API_KEY set")
        return None

    target_model = SMART_MODEL if model_tier == "smart" else FAST_MODEL

    try:
        combined = f"{system_prompt}\n\n{user_prompt}"
        response = _CLIENT.models.generate_content(
            model=target_model,
            contents=combined,
        )
        return response.text
    except Exception as e:
        print(f"❌ LLM Error ({target_model}): {e}")
        return None


def save_artifact(path: str, content: str) -> None:
    """
    Writes the code artifact to the disk safely.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"💾 Wrote: {path}")


# ---------------------------------------------------------------------------
# Dynamic codebase search (wraps context_discovery)
# ---------------------------------------------------------------------------

def search_codebase(query: str, max_results: int = 8) -> list:
    """
    Search the source tree for files matching the query.
    Returns list[SearchHit] or [] if context_discovery is unavailable.

    Example::
        hits = search_codebase("inventory grid out-of-stock")
        for h in hits:
            print(h.path, h.line)
    """
    if not _DISCOVERY_AVAILABLE:
        return []
    return _search_codebase(query, max_results=max_results)


def read_file_tool(path: str, max_chars: int = 4000) -> str:
    """
    Read a repo-relative or absolute file and return its content.
    Safe to call from any agent — returns a formatted context block.
    """
    if not _DISCOVERY_AVAILABLE:
        full = _PROJECT_ROOT / path
        if full.exists():
            c = full.read_text(encoding="utf-8", errors="replace")
            return f"### File: {path}\n```\n{c[:max_chars]}\n```\n"
        return f"# (file not found) {path}"
    return _read_file_context(path, max_chars=max_chars)


def build_dynamic_context(queries: list[str], extra_paths: list[str] | None = None) -> str:
    """
    Discover and concatenate relevant codebase context for the given queries.
    Agents call this instead of the hardcoded get_project_context() when they
    need to find relevant files at runtime.

    Example::
        ctx = build_dynamic_context(["related products", "ProductDetailView"])
        # ctx now contains content of relevant files
    """
    if not _DISCOVERY_AVAILABLE:
        return get_project_context()
    return _build_dynamic_context(queries, extra_paths=extra_paths)
