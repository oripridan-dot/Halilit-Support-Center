"""
ORACLE AGENT — JIT Oracle Lifeline  (backend/factory/oracle_agent.py)
======================================================================
The Oracle is a completely isolated "cold-booted" consultant AI that the
Swarm calls when it is STUCK in a failure loop.  It has zero memory of
previous attempts, which is precisely its superpower.

Architecture: JIT Oracle Lifeline (Level 8 Safety Net)
-------------------------------------------------------
Design principle: "Pair Programming / Rubber Ducking"
  When a developer is staring at the same broken code for two hours, they
  go blind to their own typos. They ask a Senior Developer to look over
  their shoulder, and the Senior spots the missing comma in 10 seconds.

  For an AI Swarm, getting stuck happens because the Context Window becomes
  polluted with its own failed attempts.  By routing the problem to a
  completely fresh Gemini call with a different framing, the Oracle escapes
  that pollution and often spots what the Swarm cannot.

Trigger points (auto-wired, never manual):
  1. watchdog_agent.run_watchdog()  — called when LLM prescription fails
  2. MCP tool `consult_oracle`      — callable by Core LLM voluntarily

Usage:
    from backend.factory.oracle_agent import consult_external_oracle

    strategy = consult_external_oracle(
        intent="Render a 4-column product grid in ProductDetailView.tsx",
        current_code="<tsx content>",
        error_logs="<tsc / browser console errors>",
    )
    # strategy is a plain-text Rescue Protocol the Swarm can adopt
"""

from __future__ import annotations

import sys
from pathlib import Path

_FACTORY_DIR = Path(__file__).resolve().parent
if str(_FACTORY_DIR) not in sys.path:
    sys.path.insert(0, str(_FACTORY_DIR))

try:
    from agent_core import query_llm
except ImportError:
    from .agent_core import query_llm  # type: ignore


# ---------------------------------------------------------------------------
# Oracle System Prompt — The Oracle's "clean room" persona
# ---------------------------------------------------------------------------
ORACLE_SYSTEM_PROMPT = """\
You are the 'External Oracle' — a pristine, Level 10 Principal Architect.
You are entirely detached from the current coding swarm.  The swarm has
called you because they are STUCK in a loop and their current strategy is
failing.

They will provide you with:
  1. What they are trying to do  (the intent).
  2. The code they are struggling with.
  3. The errors they are seeing.

Your mandate:
  • DO NOT validate their broken approach.  Assume their current strategy
    is fundamentally flawed and start reasoning from first principles.
  • Think completely outside the box.  Provide a radical, simplified, or
    completely different alternative to solve their intent.
  • Output a strict, step-by-step 'Rescue Protocol' the swarm can execute
    immediately.  Number every step.  Be exact — name files, class names,
    and Tailwind classes where relevant.
  • If the root cause is obvious (wrong Tailwind utility, wrong import
    path, wrong hook dependency array, mismatched Pydantic field, etc.),
    say so bluntly at the top.
  • End with a one-line "Root Cause Summary".

Output format (Markdown):
  ## 🚨 Root-Cause Hypothesis
  <one concise paragraph>

  ## 🔧 Rescue Protocol
  1. <exact step>
  2. <exact step>
  …

  ## ✅ Root Cause Summary
  <one sentence>
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def consult_external_oracle(
    intent: str,
    current_code: str,
    error_logs: str,
) -> str:
    """
    JIT lifeline triggered when the Swarm is stuck in a failure loop.

    Packages the failure context and routes it to a fresh, cold-booted LLM
    call (the Oracle) that has no memory of previous failed attempts.

    Args:
        intent:       What the Swarm was trying to accomplish.
        current_code: The code (or file content) that is failing.
        error_logs:   Raw compiler / runtime / test error output.

    Returns:
        A plain-text Rescue Protocol (Markdown) from the Oracle.
        Returns an error message string if the LLM call fails.
    """
    divider = "🚨" * 10
    print(f"\n{divider}")
    print("📞 INITIATING JIT ORACLE LIFELINE: Phoning an external expert...")
    print(f"{divider}\n")

    # Trim inputs to stay within context-window budget
    code_excerpt = current_code[:4000] if current_code else "(none provided)"
    error_excerpt = error_logs[:3000] if error_logs else "(none provided)"

    user_prompt = (
        f"### THE INTENT\n{intent}\n\n"
        f"### THE BROKEN CODE\n```\n{code_excerpt}\n```\n\n"
        f"### THE ERRORS\n```\n{error_excerpt}\n```\n\n"
        "Please provide a Rescue Protocol."
    )

    # Oracle always uses the smart tier — this is a last-resort call
    rescue_strategy = query_llm(
        ORACLE_SYSTEM_PROMPT,
        user_prompt,
        temperature=0.1,   # near-zero temperature → maximum determinism
        model_tier="smart",
    )

    if not rescue_strategy:
        fallback = (
            "⚠️  Oracle returned no response. "
            "Check GEMINI_API_KEY and network connectivity."
        )
        print(fallback)
        return fallback

    print("\n✨ ORACLE RESPONSE RECEIVED ✨")
    print(rescue_strategy)
    print("-" * 50 + "\n")

    return rescue_strategy


# ---------------------------------------------------------------------------
# Standalone test harness
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    _demo_intent = "Render a responsive 4-column product grid in ProductDetailView.tsx"
    _demo_code = (
        "<div className='grid grid-cols-4 gap-4'>\n"
        "  {products.map(p => <ProductCard key={p.id} product={p} />)}\n"
        "</div>"
    )
    _demo_errors = (
        "Warning: Each child in a list should have a unique 'key' prop.\n"
        "TypeError: Cannot read properties of undefined (reading 'map')"
    )

    result = consult_external_oracle(_demo_intent, _demo_code, _demo_errors)
    print(result)
