"""
SYSTEM STEERER & VALIDATOR — Level 6 Strategic Planning Agent
Halilit Support Center v9.6.1 Dark Factory

Reads the Master Plan (strategy/master_plan.md) and audits existing specs to
identify the single most critical gap, then generates a new or updated spec
to close it.

Usage:
    python backend/factory/steerer_agent.py
    # OR via factory.py:
    python factory.py steer
"""
import re
import sys
from pathlib import Path

# Agent runs in backend/factory/ → project root is 3 levels up
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    from agent_core import query_llm, save_artifact
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from agent_core import query_llm, save_artifact

# ---------------------------------------------------------------------------
# Paths — use the real spec directory layout (not specs/ui or specs/data)
# ---------------------------------------------------------------------------
SPECS_ROOT = _PROJECT_ROOT / "specs"
STRATEGY_FILE = SPECS_ROOT / "strategy" / "master_plan.md"

# Directories Steerer reads to understand the current system state
AUDIT_DIRS = [
    SPECS_ROOT / "interface",      # UI component specs
    SPECS_ROOT / "data_pipeline",  # Data/ingestion specs
    SPECS_ROOT / "behavior",       # Scenario / test specs
]

# Generated specs land here by default (interface for UI, data_pipeline for backend)
OUTPUT_DIR_FRONTEND = SPECS_ROOT / "interface"
OUTPUT_DIR_BACKEND = SPECS_ROOT / "data_pipeline"

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are the SYSTEM STEERER & VALIDATOR for the Halilit Support Center Dark Factory.

YOUR ROLE:
1. Read the Strategic Master Plan (business goals + technical standards).
2. Audit ALL existing Technical Specs (the current system state).
3. Identify the SINGLE most critical gap or conflict between what the strategy
   demands and what the specs currently describe.
4. OUTPUT one complete Markdown spec file that closes that gap.

OUTPUT RULES — follow exactly:
- Start with "# Spec: [Title of Feature]"
- Second line: "**Version:** 1.0"
- Third line: "**Component:** `<relative/path/to/target/file.tsx or .py>`"
- Use the Dark Factory spec format: Purpose, Requirements, Behavior Scenarios.
- Requirements must be concrete and testable — no vague language.
- Do NOT wrap your output in markdown fences (no ``` blocks around the whole file).
- Output ONLY the spec file — no preamble, no explanation, no commentary.

ARCHITECTURE REMINDERS:
- Frontend: React 18 + TypeScript + Tailwind CSS + Zustand (useNavigationStore in store/navigationStore.ts).
- Catalog hook: useConductorCatalog() returns { data: { products, metadata }, isLoading, error, refetch }.
- Navigation: useNavigationStore() — actions: goToProduct, goToInventory, goToDashboard, goBack.
- No react-router-dom. No external UI libraries beyond lucide-react and framer-motion.
- Source rules: ZERO synthetic/mock data. Empty better than fake.
"""


def _read_specs() -> str:
    """Reads all current specs from audit directories (first 2 000 chars each)."""
    parts: list[str] = []
    for directory in AUDIT_DIRS:
        if not directory.exists():
            continue
        for spec_file in sorted(directory.glob("*.md")):
            content = spec_file.read_text(encoding="utf-8", errors="replace")
            parts.append(
                f"\n--- EXISTING SPEC: {spec_file.relative_to(_PROJECT_ROOT)} ---\n"
                + content[:2000]
                + ("\n[… truncated …]" if len(content) > 2000 else "")
            )
    return "\n".join(parts) if parts else "(no existing specs found)"


def _classify_domain(response_text: str) -> str:
    """Return 'frontend' or 'backend' based on response content signals."""
    lower = response_text.lower()
    fe_hits = sum(1 for kw in ["react", "tsx", "component",
                  "tailwind", "view", "ui", "frontend"] if kw in lower)
    be_hits = sum(1 for kw in ["fastapi", "python", "backend",
                  "endpoint", "pydantic", "scraper"] if kw in lower)
    return "frontend" if fe_hits >= be_hits else "backend"


def steer_system() -> None:
    if not STRATEGY_FILE.exists():
        print(f"❌  Missing Master Plan: {STRATEGY_FILE}")
        print("    Create it with: python factory.py init  (or edit specs/strategy/master_plan.md)")
        return

    print("🧭  Reading Strategic Compass …")
    strategy = STRATEGY_FILE.read_text(encoding="utf-8")

    print("🔍  Auditing Current System Specs …")
    current_state = _read_specs()

    prompt = f"""
STRATEGIC GOALS (Master Plan):
{strategy}

CURRENT SYSTEM STATE (Existing Specs):
{current_state}

TASK:
Identify the SINGLE most critical missing feature or logic gap that prevents
the Halilit Support Center from achieving the Strategic Goals above.
Then write a complete, production-ready spec file to close that gap.

Remember: output ONLY the spec markdown — no explanation before or after.
"""

    print("🧠  Analysing gaps …")
    response = query_llm(SYSTEM_PROMPT, prompt, temperature=0.3)

    if not response:
        print("❌  Steerer received no response from the LLM.")
        return

    if "# Spec:" not in response:
        print("⚠️  Steerer did not produce a valid spec (missing '# Spec:' header).")
        print("   Raw output preview:")
        print(response[:500])
        return

    # Derive filename from spec title
    title_match = re.search(r"# Spec:\s*(.+)", response)
    filename_base = "auto_steerer_improvement"
    if title_match:
        raw_title = title_match.group(1).strip()
        filename_base = re.sub(r"[^\w\s-]", "", raw_title).strip().lower()
        filename_base = re.sub(r"[\s]+", "_", filename_base)[:60]

    domain = _classify_domain(response)
    output_dir = OUTPUT_DIR_FRONTEND if domain == "frontend" else OUTPUT_DIR_BACKEND
    output_dir.mkdir(parents=True, exist_ok=True)
    save_path = output_dir / f"{filename_base}.md"

    save_artifact(str(save_path), response)

    rel_path = save_path.relative_to(_PROJECT_ROOT)
    print()
    print(f"✅  STEERER ACTION: New directive written → {rel_path}")
    print()
    print("👉  Next steps:")
    print(f"    1. Review the spec:  cat {rel_path}")
    print(f"    2. Build it:         python factory.py build {rel_path}")
    print()


if __name__ == "__main__":
    steer_system()
