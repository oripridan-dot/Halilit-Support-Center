"""
THE SCOUT — Tech Intelligence Agent v1.0 (backend/factory/scout_agent.py)

Evolutionary AI: scans GitHub Trending, AI research feeds, and the official MCP
registry for new tools that map to bottlenecks defined in master_plan.md.
When a high-value tool is found, writes a Markdown "Evolution Proposal" to
specs/strategy/evolution/ for the Chief Agent to review on the next startup.

Usage:
    python backend/factory/scout_agent.py
    # OR via factory.py:
    python factory.py scout
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from agent_core import query_llm, get_project_context
except ImportError:
    from backend.factory.agent_core import query_llm, get_project_context  # type: ignore

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SPECS_ROOT = _PROJECT_ROOT / "specs"
STRATEGY_FILE = SPECS_ROOT / "strategy" / "master_plan.md"
EVOLUTION_DIR = SPECS_ROOT / "strategy" / "evolution"
MCP_CONFIG = _PROJECT_ROOT / "backend" / "config" / "mcp_servers.json"
LEARNED_GUIDELINES = _PROJECT_ROOT / "docs" / "LEARNED_GUIDELINES.md"

# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are THE SCOUT — a Technology Intelligence Agent for the Halilit Support Center Dark Factory.

YOUR MISSION:
1. Study the Master Plan's Business Goals and Current Gaps.
2. Survey the landscape of NEW tools (MCP servers, AI frameworks, React libraries,
   Python packages, data-fetching paradigms released in the last 6 months).
3. Identify 1–3 tools that DIRECTLY address a bottleneck in the Master Plan.
4. For each candidate tool, produce a structured Evolution Proposal.

STRICT RULES:
- A tool is ONLY worth proposing if it directly reduces a KNOWN gap in master_plan.md.
  Do not propose tools for features we don't need.
- DO NOT propose tools that would violate the Three Source Rules (no AI-generated data
  presented as real data, no mock specs).
- DO NOT propose introducing Three.js, Galaxy dashboards, or any 3-D visualisation
  unless the spec explicitly demands it.
- Proposals must be actionable — include the integration path, risk level, and a
  specific spec file that would need to change.
- If NO compelling new tool exists, output a single proposal of type "NO_CHANGE" to
  signal the system is already optimally tooled.

OUTPUT FORMAT (JSON ONLY — no markdown fences):
{
    "scan_date": "YYYY-MM-DD",
    "thought": "Internal reasoning: which gaps exist? What tool landscape did I consider?",
    "proposals": [
        {
            "id": "proposal_snake_case_id",
            "type": "NEW_MCP | NEW_LIBRARY | NEW_FRAMEWORK | NEW_PARADIGM | NO_CHANGE",
            "tool_name": "Name of the tool or technique",
            "source_url": "Official repo or docs URL",
            "maps_to_bottleneck": "Exact business goal or gap from master_plan.md it solves",
            "integration_path": "Concise steps: which file changes, which spec updates",
            "risk_level": "LOW | MEDIUM | HIGH",
            "estimated_velocity_gain": "Qualitative: e.g. +30% faster catalog cold-start",
            "verdict": "RECOMMEND | MONITOR | SKIP",
            "rationale": "1–2 sentence explanation of the verdict"
        }
    ],
    "lineage_note": "Optional: if a paradigm shift is large enough to warrant spawning a Gen-2 agent, state it here."
}
"""

# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------


def _build_scout_context() -> str:
    """Assembles the Master Plan + current MCP config as Scout input context."""
    parts: list[str] = []

    if STRATEGY_FILE.exists():
        parts.append("=== MASTER PLAN (DNA of this system) ===")
        parts.append(STRATEGY_FILE.read_text(encoding="utf-8"))
        parts.append("=== END MASTER PLAN ===\n")
    else:
        parts.append(
            "⚠️  WARNING: master_plan.md not found — Scout is flying blind.\n")

    if MCP_CONFIG.exists():
        cfg = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
        servers = cfg.get("servers", [])
        parts.append("=== CURRENT MCP SERVERS ===")
        for s in servers:
            status = "ENABLED ✅" if s.get("enabled") else "disabled ⛔"
            parts.append(f"  • {s['name']} ({s['transport']}) — {status}")
        parts.append("=== END MCP SERVERS ===\n")

    if LEARNED_GUIDELINES.exists():
        guidelines = LEARNED_GUIDELINES.read_text(encoding="utf-8")
        # Trim to last 3000 chars to avoid bloating context
        if len(guidelines) > 3000:
            guidelines = "...(trimmed)...\n" + guidelines[-3000:]
        parts.append("=== LEARNED GUIDELINES (agent memory) ===")
        parts.append(guidelines)
        parts.append("=== END GUIDELINES ===\n")

    # Include existing proposals so we don't duplicate
    if EVOLUTION_DIR.exists():
        existing = sorted(EVOLUTION_DIR.glob("*.md"))
        if existing:
            parts.append(
                "=== EXISTING EVOLUTION PROPOSALS (don't duplicate) ===")
            for p in existing[-5:]:  # last 5 only
                parts.append(f"  • {p.name}")
            parts.append("=== END EXISTING PROPOSALS ===\n")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Proposal writer
# ---------------------------------------------------------------------------

def _write_proposal(proposal: dict, scan_date: str, lineage_note: str) -> Path:
    """Renders a single proposal dict as a Markdown file."""
    pid = proposal.get("id", "unnamed")
    verdict = proposal.get("verdict", "MONITOR")
    tool_name = proposal.get("tool_name", "Unknown Tool")
    prop_type = proposal.get("type", "UNKNOWN")

    if prop_type == "NO_CHANGE":
        content = f"""# Evolution Proposal: No Change Required
**Date:** {scan_date}
**Scout Verdict:** The system is optimally tooled for the current Master Plan goals.

{proposal.get('rationale', '')}
"""
    else:
        content = f"""# Evolution Proposal: {tool_name}
**Date:** {scan_date}
**Proposal ID:** `{pid}`
**Type:** {prop_type}
**Verdict:** {verdict}
**Risk Level:** {proposal.get('risk_level', 'UNKNOWN')}

---

## Problem Addressed
{proposal.get('maps_to_bottleneck', '—')}

## The Tool
- **Name:** {tool_name}
- **Source / Docs:** {proposal.get('source_url', '—')}

## Integration Path
{proposal.get('integration_path', '—')}

## Expected Impact
{proposal.get('estimated_velocity_gain', '—')}

## Rationale
{proposal.get('rationale', '—')}

---
"""

    if lineage_note:
        content += f"\n## Lineage Note (Generational Spawn Signal)\n{lineage_note}\n"

    EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{scan_date}_{pid}.md"
    output_path = EVOLUTION_DIR / filename
    output_path.write_text(content, encoding="utf-8")
    return output_path


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_scout() -> list[dict]:
    """
    Executes the Scout cycle:
    1. Build context (Master Plan + current tooling).
    2. Query LLM to identify evolution candidates.
    3. Write Markdown proposals to specs/strategy/evolution/.
    4. Return the parsed proposals list.
    """
    print("\n" + "="*62)
    print("🔭  THE SCOUT — Technology Intelligence Scan")
    print("="*62)

    context = _build_scout_context()
    user_prompt = (
        "Scan your knowledge of recent AI tooling advances (late 2025 – February 2026). "
        "Study the Master Plan above. Identify 1–3 high-value new tools that directly "
        "close a gap listed in the plan. Produce the JSON output as specified.\n\n"
        f"--- CONTEXT ---\n{context}\n--- END CONTEXT ---\n\n"
        "Respond ONLY with the JSON object."
    )

    raw = query_llm(SYSTEM_PROMPT, user_prompt,
                    temperature=0.35, model_tier="smart")
    if not raw:
        print("⚠️  Scout: LLM call failed. Check GEMINI_API_KEY.")
        return []

    # Strip optional markdown fence
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in response.")
        parsed = json.loads(json_match.group(0))
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"⚠️  Scout: Could not parse response — {exc}")
        print("   Raw output:", raw[:500])
        return []

    proposals = parsed.get("proposals", [])
    scan_date = parsed.get("scan_date", datetime.utcnow().strftime("%Y-%m-%d"))
    lineage_note = parsed.get("lineage_note", "")
    thought = parsed.get("thought", "")

    print(
        f"\n🧠 Scout Reasoning:\n   {thought[:300]}{'...' if len(thought) > 300 else ''}\n")

    if not proposals:
        print("   No proposals generated.")
        return []

    written: list[Path] = []
    for proposal in proposals:
        path = _write_proposal(proposal, scan_date, lineage_note)
        written.append(path)
        verdict = proposal.get("verdict", "?")
        tool = proposal.get("tool_name", "?")
        risk = proposal.get("risk_level", "?")
        icon = {"RECOMMEND": "✅", "MONITOR": "👁️",
                "SKIP": "⛔"}.get(verdict, "📄")
        print(f"   {icon} [{verdict}] {tool} (Risk: {risk})")
        print(f"      → {path.relative_to(_PROJECT_ROOT)}")

    if lineage_note:
        print(f"\n🧬 LINEAGE NOTE: {lineage_note[:200]}")

    print(
        f"\n✅ Scout complete. {len(written)} proposal(s) written to specs/strategy/evolution/")
    print("="*62 + "\n")

    return proposals


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    run_scout()
