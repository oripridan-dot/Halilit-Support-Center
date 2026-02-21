"""
PRODUCT MANAGER AGENT  (backend/factory/product_manager.py)
============================================================
Agile Scrum Master and Product Manager for the Halilit Dark Factory.

Maintains the Master Backlog in docs/ROADMAP.md, grooms short-term sprints,
surfaces the next highest-priority task to the Operator, and auto-generates
the technical [EXECUTE] spec so the Chief can launch a Swarm with one word.

Usage (standalone):
    python backend/factory/product_manager.py "What's next?"

Usage (via nexus.py):
    nexus → PM → "What's on the roadmap?"
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

# agent_core lives in the same directory
sys.path.insert(0, str(Path(__file__).parent))
from agent_core import query_llm  # noqa: E402

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ROADMAP_PATH = ROOT_DIR / "docs" / "ROADMAP.md"

# ---------------------------------------------------------------------------
# Roadmap I/O tools
# ---------------------------------------------------------------------------


def read_roadmap() -> str:
    """
    Returns the full contents of docs/ROADMAP.md as a string.

    If the file does not exist, returns a minimal placeholder and creates it.
    """
    if not ROADMAP_PATH.exists():
        ROADMAP_PATH.parent.mkdir(parents=True, exist_ok=True)
        ROADMAP_PATH.write_text(
            "# 🗺️ Halilit Support Center Roadmap\n\n"
            "## 🚀 Short-Term (Current Sprint)\n\n"
            "*(No tasks yet — ask the PM to populate this list.)*\n\n"
            "## 🔭 Long-Term (Epics)\n\n"
            "*(No epics yet.)*\n\n"
            "## ✅ Completed\n\n"
            "*(Nothing completed yet.)*\n",
            encoding="utf-8",
        )
    return ROADMAP_PATH.read_text(encoding="utf-8")


def update_roadmap(task_name: str, new_status: str) -> str:
    """
    Updates a task's checkbox in docs/ROADMAP.md.

    Args:
        task_name:  The text of the task to find (partial match is fine).
        new_status: "complete" → replaces [ ] with [x]
                    "incomplete" → replaces [x] with [ ]
                    "move_to_completed" → moves the line to the Completed section
                                         and marks it [x].

    Returns a human-readable confirmation string.
    """
    contents = read_roadmap()

    # Build a regex that matches the task line regardless of checkbox state
    # Task lines look like: "- [ ] **Task N:** ..." or "- [x] **Epic N:** ..."
    escaped = re.escape(task_name[:40])  # partial anchor from start
    pattern = re.compile(
        r"^([ \t]*- \[)([xX ]?)(\] .+?" + escaped + r".*)$",
        re.MULTILINE | re.IGNORECASE,
    )
    match = pattern.search(contents)
    if not match:
        return f"⚠️  Task not found in ROADMAP.md: '{task_name}'"

    original_line = match.group(0)

    if new_status in ("complete", "move_to_completed"):
        new_line = match.group(1) + "x" + match.group(3)
    else:  # incomplete
        new_line = match.group(1) + " " + match.group(3)

    if new_status == "move_to_completed":
        # Remove the line from its current section and append to Completed
        updated = contents.replace(original_line + "\n", "", 1).replace(
            original_line, "", 1
        )
        completed_marker = "## ✅ Completed"
        if completed_marker in updated:
            updated = updated.replace(
                completed_marker,
                completed_marker + "\n\n" + new_line,
                1,
            )
        else:
            updated = updated + f"\n\n{completed_marker}\n\n{new_line}\n"
    else:
        updated = contents.replace(original_line, new_line, 1)

    ROADMAP_PATH.write_text(updated, encoding="utf-8")
    action = "marked complete" if "x" in new_status else "marked incomplete"
    return f"✅ ROADMAP updated — '{task_name[:60]}...' {action}."


# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """
You are the AGILE SCRUM MASTER and PRODUCT MANAGER (Level 7) of the Halilit Support Center Dark Factory.
You have two native tools: read_roadmap and update_roadmap.

YOUR MANDATE:
1. When the Operator asks "What's next?", "What's on the roadmap?", "Give me a task", or similar,
   you MUST read docs/ROADMAP.md using the read_roadmap data provided in your context.
2. Select the HIGHEST-PRIORITY incomplete task from the 🚀 Short-Term (Current Sprint) list.
3. Explain WHY it is the priority in plain English — connect it to business impact.
4. Automatically generate a highly technical [EXECUTE] spec the Operator can hand to the Chief.
   The spec must be precise enough that the Chief can dispatch the Swarm without further clarification.
5. When a feature is confirmed complete, signal that you will update_roadmap.

YOUR VOICE: Authoritative, direct, and commercially focused. You speak like a seasoned startup
Engineering Manager who cares deeply about user experience AND shipping velocity. You do NOT tolerate
scope creep or vague tasks. You convert fuzzy operator wishes into actionable sprint tickets.

ARCHITECTURE CONSTRAINTS (do not violate these in your [EXECUTE] specs):
- Frontend: React 18 + Vite SPA + Zustand + React Query + Tailwind CSS. NEVER Next.js or Redux.
- Backend: Python 3.11 + FastAPI. NEVER Django or Flask.
- Data: Three Source Rules apply (Commercial → prices/SKUs; Official → specs/media; Contextual → reviews).
- All product data flows from /api/conductor/catalog — no client-side JSON loading.

OUTPUT FORMAT for roadmap queries:
---
👔 PM BRIEFING

**Current top priority:** [Task name]

**Why this matters:** [Business impact in 2–3 sentences]

**Technical assessment:** [What files/systems are involved and current state]

**[EXECUTE] Spec for the Chief:**
> [Precise technical delegation instruction, ready to hand to Chief.
>  Include: what to build, which files to modify, which spec path to use,
>  and the acceptance criteria.]

*Type "Yes, do it" to hand this spec to the Chief and spin up the Swarm.*
---
"""

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def consult_product_manager(
    user_input: str,
    confirm_complete_task: Optional[str] = None,
) -> str:
    """
    Main PM entry point.

    Args:
        user_input:             The operator's question or request.
        confirm_complete_task:  If provided, the PM will mark this task as
                                complete in the roadmap before answering.

    Returns a formatted PM briefing string for display in the terminal / Nexus.
    """
    # Auto-update roadmap if a task was just confirmed complete
    status_note = ""
    if confirm_complete_task:
        result = update_roadmap(confirm_complete_task, "move_to_completed")
        status_note = f"\n\n📋 Roadmap update: {result}\n"

    roadmap_contents = read_roadmap()

    context = (
        f"=== CURRENT ROADMAP ===\n{roadmap_contents}\n=== END ROADMAP ===\n\n"
        f"Operator says: \"{user_input}\"\n\n"
        "Respond with your PM briefing in the format specified in your system prompt."
    )

    response = query_llm(SYSTEM_PROMPT, context,
                         temperature=0.3, model_tier="smart")

    if not response:
        return (
            "⚠️  PM Agent: LLM unavailable. Here is the raw roadmap:\n\n"
            + roadmap_contents
        )

    return status_note + response


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    user_q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What's next?"
    print(consult_product_manager(user_q))
