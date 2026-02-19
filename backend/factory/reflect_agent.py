"""
THE MENTOR — Reflect Agent  (backend/factory/reflect_agent.py)

Analyzes a completed task or failure event, extracts a transferable lesson,
and appends it to docs/LEARNED_GUIDELINES.md (the persistent agent memory).

Called by nexus.py when the Chief queues a 'reflect' task after a successful
heal or a resolved error.

Usage:
  python reflect_agent.py "Short failure context string"
"""

import sys
from datetime import date
from pathlib import Path

# Resolve project root (backend/factory → backend → project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_GUIDELINES_PATH = _PROJECT_ROOT / "docs" / "LEARNED_GUIDELINES.md"

# Add agent_core to path
sys.path.insert(0, str(Path(__file__).parent))
from agent_core import query_llm, get_project_context  # noqa: E402

# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------
REFLECT_SYSTEM_PROMPT = """
You are THE MENTOR (Level 9), an expert software engineering coach.

Your ONLY job is to extract ONE concise engineering lesson from a failure or recovery event
and return it in a strict Markdown format so it can be appended to LEARNED_GUIDELINES.md.

OUTPUT FORMAT (return ONLY this block, no extra text, no markdown fences):

### [{today}] {short_title}
**Symptom:** <one sentence describing what went wrong from the operator's perspective>
**Root Cause:** <one sentence identifying the technical root cause>
**Fix:** <one sentence describing what was changed to resolve it>
**Lesson:** <one actionable rule to prevent this from happening again. Start with "NEVER" or "ALWAYS">

RULES:
- Keep every field to one sentence maximum.
- The "Lesson" MUST be an imperative rule (starts with NEVER, ALWAYS, PREFER, AVOID, ENSURE).
- Do NOT add commentary, preamble, or trailing text outside the block.
- If the context is too vague to extract a meaningful lesson, return:
  ### [{today}] Context Too Vague
  **Symptom:** Insufficient failure detail provided.
  **Root Cause:** Unknown.
  **Fix:** Not documented.
  **Lesson:** ALWAYS provide detailed failure context when calling 'reflect'.
"""

# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------


def run_reflect(failure_context: str) -> bool:
    """
    Asks the LLM to extract a lesson from the failure context and appends it
    to docs/LEARNED_GUIDELINES.md.

    Returns True on success, False on failure.
    """
    today = date.today().isoformat()

    # Build a richer prompt including existing lessons so the LLM avoids duplication
    existing = ""
    if _GUIDELINES_PATH.exists():
        existing = _GUIDELINES_PATH.read_text(encoding="utf-8")

    user_prompt = f"""
FAILURE / RECOVERY CONTEXT:
{failure_context}

EXISTING GUIDELINES (avoid duplicating these):
{existing[:3000]}  

Today's date: {today}

Extract ONE new lesson from the failure context above.
"""

    system = REFLECT_SYSTEM_PROMPT.replace("{today}", today).replace(
        "{short_title}", "<concise 3-6 word title>"
    )

    print("🧠 [MENTOR] Extracting lesson from failure context...")
    raw = query_llm(system, user_prompt, temperature=0.2, model_tier="smart")
    if not raw:
        print("❌ [MENTOR] LLM call failed — lesson not recorded.")
        return False

    lesson_block = raw.strip()

    # Append to LEARNED_GUIDELINES.md
    _GUIDELINES_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not _GUIDELINES_PATH.exists():
        # Bootstrap the file if missing
        header = (
            "# LEARNED GUIDELINES — Persistent Agent Memory\n\n"
            "> Auto-maintained by the Reflect Agent.\n\n---\n\n## Guidelines\n\n"
        )
        _GUIDELINES_PATH.write_text(header, encoding="utf-8")

    current = _GUIDELINES_PATH.read_text(encoding="utf-8")

    # Remove the "(No lessons recorded yet…)" placeholder if first real lesson
    placeholder = "*(No lessons recorded yet. The Reflect Agent will populate this section as the system self-heals.)*"
    current = current.replace(placeholder, "")

    updated = current.rstrip() + "\n\n" + lesson_block + "\n"
    _GUIDELINES_PATH.write_text(updated, encoding="utf-8")

    print(f"✅ [MENTOR] Lesson recorded in docs/LEARNED_GUIDELINES.md")
    print("─" * 60)
    print(lesson_block)
    print("─" * 60)
    return True


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    context = sys.argv[1] if len(sys.argv) > 1 else ""
    if not context:
        print("❌ [MENTOR] Usage: python reflect_agent.py \"failure context\"")
        sys.exit(1)

    success = run_reflect(context)
    sys.exit(0 if success else 1)
