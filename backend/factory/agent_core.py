import os
from pathlib import Path

from dotenv import load_dotenv
import google.genai as genai

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


def get_project_context(target_type: str = "frontend") -> str:
    """
    Loads critical project context so the Agent respects the Architecture.
    Returns a formatted string of key files to inject into prompts.
    """
    root = _PROJECT_ROOT
    context_parts: list[str] = []

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
