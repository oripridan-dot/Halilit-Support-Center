"""
THE CHIEF — Strategic Partner Agent v4.0 (backend/factory/chief_agent.py)

Massively Parallel Engineering Manager with Failure Recovery.
Outputs a TASK QUEUE enabling the Nexus Swarm Console to execute
independent tasks simultaneously and auto-recover from failures.
"""

import sys
import json
import os
import re
import subprocess
from pathlib import Path

# agent_core.py lives in the same directory
sys.path.insert(0, str(Path(__file__).parent))
from agent_core import query_llm  # noqa: E402

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SPECS_DIR = ROOT_DIR / "specs"
FRONTEND_DIR = ROOT_DIR / "frontend/src/components/views"

# ---------------------------------------------------------------------------
# System Prompt — v3.0: Queue Output
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are THE CHIEF (Level 9). You are a Massively Parallel Engineering Manager and CTO.
Your Goal: Maximize velocity by identifying tasks that can run SIMULTANEOUSLY.

STYLE GUIDE:
1. **Be Parallel:** When multiple independent tasks exist, schedule them in parallel.
2. **Be Explanatory:** Eliminate jargon. Explain what each agent does and why.
3. **Be Structured:** Output a clear, ordered task queue.
4. **Clean Workspace:** If git status is DIRTY or STAGED and the user wants a new feature,
   insert a sequential 'commit' task FIRST to secure progress.

TOOLS & PARALLELISM RULES:
- 'design'    (Architect): Creates Blueprints/Specs.      PARALLEL SAFE ✅
- 'implement' (Builder):   Turns Specs into Code.          PARALLEL SAFE ✅ (if different files)
- 'heal'      (Watchdog):  Finds and fixes bugs.           SEQUENTIAL 🔒
- 'diagnose'  (Scanner):   Scans for errors, no auto-fix.  PARALLEL SAFE ✅
- 'steer'     (Strategist):Reviews business goals.         PARALLEL SAFE ✅
- 'doc'       (Scribe):    Regenerates ARCHITECTURE.md.    SEQUENTIAL 🔒
- 'optimize'  (Optimizer): Refactors a source file.        PARALLEL SAFE ✅ (if different files)
- 'build'     (Data):      Rebuilds the product catalog.   SEQUENTIAL 🔒
- 'commit'    (Repo Agent):Git snapshot — must block all.  SEQUENTIAL 🔒
- 'explain'   (None):      Plain-English answer; no queue. PARALLEL SAFE ✅

OUTPUT FORMAT (JSON ONLY — no markdown fences):
{
    "thought": "Internal reasoning: what does the user REALLY need?",
    "explanation": "Clear, jargon-free explanation of the plan (2-4 sentences).",
    "proposal": "I will [action] because [reason].",
    "queue": [
        {"tool": "design", "args": "interface/settings_view.md", "parallel": true},
        {"tool": "design", "args": "interface/profile_view.md",  "parallel": true},
        {"tool": "commit", "args": "",                           "parallel": false}
    ]
}

RULES:
- ALWAYS use the "queue" key (even for a single task — wrap it in an array).
- Set "parallel": true for tasks that touch DIFFERENT files or are read-only.
- Set "parallel": false for 'commit', 'build', 'heal', 'doc' — they mutate shared state.
- For 'implement', the "args" MUST be the spec filename to implement.
- For 'optimize', the "args" MUST be the relative file path to refactor.
- For 'explain', use a single queue item with "args" containing the answer text.
- Sequential tasks act as BARRIERS: all parallel tasks before them must finish first.

RECOVERY MODE (triggered when FAILURE REPORT is present):
- Read the error output carefully. Identify the root cause.
- Prefer 'heal' for TypeScript/Python compilation errors.
- Prefer 'implement' (with the affected spec) for logic/runtime errors.
- Prefer 'optimize' for import or lint errors in a known file.
- Always explain the root cause clearly in "explanation".
- Never re-run a task that already succeeded.
- If the error is a missing API key or network failure, use 'explain' to advise the user.
"""

# ---------------------------------------------------------------------------
# Project state scanner
# ---------------------------------------------------------------------------


def get_git_status() -> str:
    """Returns a human-readable git working tree status."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
        )
        output = result.stdout.strip()
        if not output:
            return "CLEAN"
        staged = any(
            line[:1] in "MADRC"
            for line in output.splitlines()
            if line
        )
        return "STAGED (changes ready to commit)" if staged else "DIRTY (unsaved changes present)"
    except Exception:
        return "UNKNOWN (git not found)"


def get_project_state() -> str:
    """Scans the factory floor to see what exists."""
    state = []

    # 0. Git status
    git_status = get_git_status()
    state.append(f"Git Status: {git_status}")

    # 1. Check Specs
    if SPECS_DIR.exists():
        specs = list(SPECS_DIR.rglob("*.md"))
        state.append(f"Found {len(specs)} Specification(s) in /specs.")
        for f in sorted(specs):
            state.append(f"  - {f.relative_to(ROOT_DIR)}")
    else:
        state.append("MISSING: /specs directory not found.")

    # 2. Check Frontend views
    if FRONTEND_DIR.exists():
        views = list(FRONTEND_DIR.glob("*.tsx"))
        state.append(
            f"Found {len(views)} Frontend View(s): {[v.name for v in views]}")
    else:
        state.append(
            "MISSING: Frontend views folder is empty or does not exist.")

    # 3. Specific artifact checks
    ui_spec = SPECS_DIR / "interface" / "01_operator_dashboard.md"
    if not ui_spec.exists():
        state.append(
            "WARNING: Main UI spec (specs/interface/01_operator_dashboard.md) is missing.")

    taxonomy = ROOT_DIR / "backend" / "data" / "learned_taxonomy.json"
    if not taxonomy.exists():
        state.append(
            "WARNING: Backend data artifact (learned_taxonomy.json) is missing — run 'build' to generate it.")
    else:
        state.append(
            "Backend data artifacts present (learned_taxonomy.json exists).")

    return "\n".join(state)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def consult_chief(user_input: str, is_startup: bool = False,
                  failure_context: str = "") -> dict:
    """
    Takes a plain-English user request (or a startup trigger) and returns
    a structured task queue plan.

    Args:
        user_input:       Plain-English instruction from the operator.
        is_startup:       True when called on first boot (no user input yet).
        failure_context:  Raw error output from failed tasks. When provided,
                          the Chief enters Recovery Mode and produces a fix plan.

    Returns a dict with keys: thought, explanation, proposal, queue.
    The 'queue' is a list of {"tool", "args", "parallel"} dicts.
    """
    project_state = get_project_state()

    context_prompt = f"""
--- PROJECT STATUS REPORT ---
{project_state}
-----------------------------
"""

    if failure_context:
        user_prompt = (
            f"RECOVERY MODE: The following factory tasks just FAILED.\n"
            f"Your mission is to analyse the errors, identify root causes, "
            f"and produce a recovery queue that fixes the failures.\n"
            f"Do NOT repeat tasks that already succeeded.\n"
            f"\n--- FAILURE REPORT ---\n{failure_context}\n--- END REPORT ---\n"
            f"Produce a targeted recovery plan."
        )
    elif is_startup:
        user_prompt = (
            "I just logged in. Analyze the project state above and tell me "
            "what the most important next step is. Be specific about what is "
            "missing or incomplete. Produce a queue with the recommended next action."
        )
    else:
        user_prompt = f"USER SAYS: '{user_input}'"

    full_prompt = context_prompt + "\n" + user_prompt + \
        "\n\nRespond ONLY with the JSON object."

    raw = query_llm(SYSTEM_PROMPT, full_prompt,
                    temperature=0.4, model_tier="smart")

    if not raw:
        return {
            "thought": "LLM call failed.",
            "explanation": "I'm having trouble reaching the AI. Check your GEMINI_API_KEY and try again.",
            "proposal": "Please verify your API key, then restart.",
            "queue": [],
        }

    # Strip optional markdown fence
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(0))

            # --- Backward compatibility: old single-action format → queue ---
            if "action" in parsed and "queue" not in parsed:
                action = parsed.get("action", "none")
                params = parsed.get("parameters", "")
                parsed["queue"] = (
                    [{"tool": action, "args": params, "parallel": False}]
                    if action not in ("none", "explain", "")
                    else []
                )

            # Ensure queue key always exists
            if "queue" not in parsed:
                parsed["queue"] = []

            return parsed
    except json.JSONDecodeError:
        pass

    # Fallback
    return {
        "thought": "Could not parse structured response.",
        "explanation": raw,
        "proposal": "Please repeat your request.",
        "queue": [],
    }


# ---------------------------------------------------------------------------
# CLI test mode
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_input = sys.argv[1] if len(sys.argv) > 1 else ""
    is_startup = not bool(test_input)
    result = consult_chief(test_input, is_startup=is_startup)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result.get("queue"):
        print(f"\n📋 QUEUE ({len(result['queue'])} tasks):")
        for i, t in enumerate(result["queue"], 1):
            mode = "⚡ PARALLEL" if t.get("parallel") else "🔒 SEQUENTIAL"
            print(f"   {i}. {mode} | {t['tool']} {t.get('args', '')}")
