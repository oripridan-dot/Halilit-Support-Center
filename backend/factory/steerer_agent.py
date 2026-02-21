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
    from agent_core import query_llm, save_artifact, build_dynamic_context, search_codebase
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from agent_core import query_llm, save_artifact, build_dynamic_context, search_codebase

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
3. Examine the DYNAMICALLY DISCOVERED CONTEXT (real codebase files found by search).
4. Identify the SINGLE most critical gap or conflict between what the strategy
   demands and what the specs currently describe.
5. OUTPUT one complete Markdown spec file that closes that gap.

OUTPUT RULES — follow exactly:
- Start with "# Spec: [Title of Feature]"
- Second line: "**Version:** 1.0"
- Third line: "**Component:** `<relative/path/to/target/file.tsx or .py>`"
- Use the Dark Factory spec format: Purpose, Requirements, Behavior Scenarios.
- Requirements must be concrete and testable — no vague language.
- Do NOT wrap your output in markdown fences (no ``` blocks around the whole file).
- Output ONLY the spec file — no preamble, no explanation, no commentary.
- **ANTI-DUPLICATE RULE:** Before selecting a topic, scan the CURRENT SYSTEM STATE
  for specs that already target the same component or goal. If one exists, your output
  must UPDATE that existing spec (keep its filename concept) rather than inventing a new
  topic. Never write two specs for the same component file.

**NEW RULE: STITCH UI PROMPT (FRONTEND ONLY)**
If the target component is a Frontend UI view (.tsx), you MUST include a dedicated
section called "## Stitch UI Prompt" immediately before "## Verification Commands".
This section must contain a highly detailed prompt meant to be copy-pasted into
Google Stitch (or Lovable/v0).
- Define the layout (e.g., Bento Grid, Flexbox, CSS Grid).
- Define the visual style (Dark mode, Tailwind CSS, slate-900 background, blue-500 accents).
- Define "Data Slots" with placeholders (do NOT hardcode real product names or prices).
- Describe component hierarchy and spacing clearly so Stitch can produce pixel-perfect code.
- Reference the exact Tailwind color tokens used in the rest of the Operator Console.

**MANDATORY SECTION — every spec MUST end with:**

## Verification Commands
List the exact terminal commands that PROVE this feature works after the Builder
implements it. Each command must be runnable non-interactively. Examples:
- `pnpm tsc --noEmit`       (TypeScript compile check — always include for .tsx specs)
- `pnpm run lint`           (ESLint check — include when touching JSX/TSX)
- `pytest backend/tests/test_feature.py -v`  (pytest — include for backend specs)
- `python -m py_compile backend/module.py`   (syntax check — lightweight backend)

RULES for Verification Commands:
1. Always include at least ONE compile/type-check command.
2. Only include commands appropriate to the domain (frontend vs backend).
3. The commands will be run AUTOMATICALLY by the Builder's sandbox. They must be
   deterministic and idempotent.

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
    import os as _os

    if not STRATEGY_FILE.exists():
        print(f"❌  Missing Master Plan: {STRATEGY_FILE}")
        print("    Create it with: python factory.py init  (or edit specs/strategy/master_plan.md)")
        return

    # When invoked from a Task Force, focus on the explicit goal
    tf_goal = _os.environ.get("TF_GOAL", "").strip()

    print("🧭  Reading Strategic Compass …")
    strategy = STRATEGY_FILE.read_text(encoding="utf-8")

    print("🔍  Auditing Current System Specs …")
    current_state = _read_specs()

    # --- Dynamic Context Discovery (Pillar 1) ---
    print("🔎  Discovering relevant codebase context …")
    _kw_pattern = re.compile(
        r'\b(?:implement|add|build|fix|create|upgrade|improve)\s+([a-z][a-z _\-]{3,40})', re.IGNORECASE)
    base_queries = [m.group(1).strip()
                    for m in _kw_pattern.finditer((tf_goal or strategy)[:3000])][:5]
    base_queries += ["inventory grid", "product detail", "dashboard"]
    dynamic_ctx = build_dynamic_context(base_queries[:6])

    if tf_goal:
        task_instruction = (
            f"TASK FORCE GOAL (MANDATORY — write a spec SPECIFICALLY for this goal):\n"
            f"  {tf_goal}\n\n"
            f"Do NOT identify a different gap. Write ONE complete spec for the goal above.\n"
            f"The spec MUST include a '**Component:**' field pointing to the exact file to create/edit."
        )
    else:
        task_instruction = (
            "TASK:\n"
            "Identify the SINGLE most critical missing feature or logic gap that prevents\n"
            "the Halilit Support Center from achieving the Strategic Goals above.\n"
            "Then write a complete, production-ready spec file to close that gap.\n"
            "The spec MUST include a '**Component:**' field pointing to the exact file to create/edit."
        )

    prompt = f"""
STRATEGIC GOALS (Master Plan):
{strategy}

CURRENT SYSTEM STATE (Existing Specs):
{current_state}

DYNAMICALLY DISCOVERED CODEBASE CONTEXT (real files found by searching the repo):
{dynamic_ctx}

{task_instruction}

Remember: output ONLY the spec markdown — no explanation before or after.
The spec MUST include a "## Verification Commands" section at the end.
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

    # ── Duplicate-spec guard ─────────────────────────────────────────────────
    # If an existing spec already targets the same component file, UPDATE it
    # instead of creating a second one.  Prevents Steerer loops from flooding
    # specs/interface/ with near-identical files.
    component_match = re.search(r"\*\*Component:\*\*\s*`?([^\`\n]+)`?", response)
    if component_match:
        target_component = component_match.group(1).strip().lower()
        for existing in output_dir.glob("*.md"):
            if existing == save_path:
                continue  # same name → normal overwrite, no issue
            try:
                existing_text = existing.read_text(encoding="utf-8")
                em = re.search(r"\*\*Component:\*\*\s*`?([^\`\n]+)`?", existing_text)
                if em and em.group(1).strip().lower() == target_component:
                    print(f"⚠️  Duplicate spec detected — same component '{target_component}'")
                    print(f"   Updating existing spec: {existing.name}")
                    save_path = existing  # overwrite in place
                    break
            except Exception:
                continue

    save_artifact(str(save_path), response)

    rel_path = save_path.relative_to(_PROJECT_ROOT)
    # Write the output path to a temp file so the Task Force coordinator
    # can reliably pick up the spec without timestamp/set-difference heuristics
    last_output_file = _PROJECT_ROOT / "specs" / "temp" / "steerer_last_output.txt"
    last_output_file.parent.mkdir(parents=True, exist_ok=True)
    last_output_file.write_text(str(save_path), encoding="utf-8")
    print()
    print(f"✅  STEERER ACTION: New directive written → {rel_path}")

    # ── Phase 2: API Contract Enforcement ───────────────────────────────────
    # For cross-domain features touching an API boundary, generate a binding
    # TypeScript contract and save it to specs/contracts/.
    is_cross_domain = any(
        kw in response.lower()
        for kw in ["api", "endpoint", "fetch", "usequery", "react query", "/api/", "fastapi"]
    )
    if is_cross_domain:
        print("📋  Cross-domain feature detected — generating API contract...")
        contract_prompt = f"""
You are a TypeScript API Contract Architect.
Based on the spec below, write a minimal but complete TypeScript type declaration file.
Define:
  - The endpoint path (as a const string)
  - The Request body type (if any)
  - The Response type
  - Any shared sub-types

Spec:
{response[:3000]}

Output ONLY valid TypeScript. No markdown fences. No explanation.
File should be self-contained and start with // Contract: <feature name>
"""
        contract_code = query_llm(
            "You output only TypeScript type declarations.",
            contract_prompt, temperature=0.0
        )
        if contract_code and "type" in contract_code.lower():
            contracts_dir = _PROJECT_ROOT / "specs" / "contracts"
            contracts_dir.mkdir(parents=True, exist_ok=True)
            contract_path = contracts_dir / f"{filename_base}.schema.ts"
            save_artifact(str(contract_path), contract_code.strip())
            print(
                f"   📄 Contract written → specs/contracts/{contract_path.name}")

    print()
    print("👉  Next steps:")
    print(f"    1. Review the spec:  cat {rel_path}")
    print(f"    2. Build it:         python factory.py build {rel_path}")
    print()


if __name__ == "__main__":
    steer_system()
