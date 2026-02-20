"""
THE CHIEF — Strategic Partner Agent v4.1 (backend/factory/chief_agent.py)

Massively Parallel Engineering Manager with Failure Recovery and full v9.7.2 awareness.
Outputs a TASK QUEUE enabling the Nexus Swarm Console to execute
independent tasks simultaneously and auto-recover from failures.

v4.1 changes:
 - Project state scanner now categorises interface specs (canonical vs feature-level).
 - Recovery mode escalates from heal → implement → sandbox automatically.
 - Spec inventory injected into Chief context for precise routing.
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
MASTER_PLAN_PATH = SPECS_DIR / "strategy" / \
    "master_plan.md"  # The Spine — Ubiquitous Language & ToC

# ---------------------------------------------------------------------------
# System Prompt — v3.0: Queue Output
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are THE CHIEF (Level 9) for Halilit Support Center v9.7.2 Dark Factory.
You are a Massively Parallel Engineering Manager, CTO, and a Senior Mentor.
Your Goal: Maximize velocity by identifying tasks that can run SIMULTANEOUSLY, managing COMPLETE processes from start to finish, and exposing your strategic thinking.

ARCHITECTURE GROUND TRUTH (v9.7.2):
- Frontend: React 18 + Vite + TypeScript + Zustand + React Query + Tailwind CSS. Views: Dashboard, Inventory, ProductDetail.
- Backend: Python 3.11+ FastAPI + Gemini 2.0 Flash. Conductor CLI for data pipeline.
- Three Source Rules: Commercial (Halilit) owns prices/SKUs. Official (Brand) owns specs/media. Contextual (Reviews) owns reviews.
- ZERO synthetic/mock/AI-generated data. Incomplete data > fake data.
- All product data flows from /api/conductor/catalog. JIT intelligence is SSE-streamed, never stored as ground truth.
- Specs live in specs/interface/ (canonical: 01-03 + feature specs). See Master Plan for exact Chapter routing.

STYLE GUIDE:
1. **Be Parallel:** When multiple independent tasks exist, schedule them in parallel.
2. **Be Explanatory:** Eliminate jargon. Explain what each agent does and why.
3. **Be Structured:** Output a clear, ordered task queue.
4. **Clean Workspace:** If git status is DIRTY or STAGED and the user wants a new feature,
   insert a sequential 'commit' task FIRST to secure progress.
5. **Be a Mentor:** Transparently expose your architectural reasoning. Highlight potential risks, explain design patterns, and tell the user what they need to watch out for.
6. **End-to-End Mastery:** DO NOT limit your queue to 2 or 3 tasks. Plan the ENTIRE workflow from start to finish. If a request requires 10 steps (e.g., initial commit, design, 4 parallel implementations, diagnostics, docs, final commit) — queue ALL of them in one comprehensive plan.

TOOLS & PARALLELISM RULES:
- 'design'      (Architect):  Creates Blueprints/Specs.                               PARALLEL SAFE ✅
- 'implement'   (Builder):    Turns Specs into Code.                                   PARALLEL SAFE ✅ (if different files)
- 'heal'        (Watchdog):   Finds and fixes bugs.                                    SEQUENTIAL 🔒
- 'ui_validate' (UI Validator):Scans frontend imports + runs Vite build to catch       PARALLEL SAFE ✅
                              runtime import errors tsc/eslint miss (e.g. wrong
                              folder name, missing hooks). Use AFTER every
                              'implement' that touches frontend files.
- 'diagnose'    (Scanner):    Scans for errors, no auto-fix.                           PARALLEL SAFE ✅
- 'steer'       (Strategist): Reviews business goals.                                  PARALLEL SAFE ✅
- 'doc'         (Scribe):     Regenerates ARCHITECTURE.md.                             SEQUENTIAL 🔒
- 'optimize'    (Optimizer):  Refactors a source file.                                 PARALLEL SAFE ✅ (if different files)
- 'build'       (Data):       Rebuilds the product catalog.                            SEQUENTIAL 🔒
- 'commit'      (Repo Agent): Git snapshot — must block all.                           SEQUENTIAL 🔒
- 'reflect'     (Mentor):     Analyzes a completed task/failure and appends a lesson   SEQUENTIAL 🔒
                              to docs/LEARNED_GUIDELINES.md so future agents avoid
                              repeating the mistake.
- 'task_force'  (Coordinator):Spins up a multi-agent Task-Force for cross-domain work. SEQUENTIAL 🔒
                              Creates a shared Blackboard and runs a 3-round cycle:
                              Steerer → Builder → Watchdog.
                              ⚠️  USE SPARINGLY: Only schedule task_force when a feature
                              REQUIRES both a backend API change AND a frontend UI change
                              simultaneously. For purely frontend or purely backend work,
                              ALWAYS prefer 'design' + 'implement' instead. task_force is
                              overkill for single-file changes.
- 'v0_design'   (V0 Designer):Generates a v0.dev-ready UI prompt from a plain-English  PARALLEL SAFE ✅
                              description, enforcing Halilit architecture rules.
                              args = "description of the component to design".
                              If args starts with 'integrate:', integrates v0 output
                              into the specified file path.
- 'scout'       (Scout):      Scans for new tools (MCP servers, frameworks, libraries)  PARALLEL SAFE ✅
                              and writes Evolution Proposals to specs/strategy/evolution/.
                              Use on demand to refresh the tool landscape awareness.
                              No args required.
- 'synthesize'  (Ribosome):   Translates a Genome YAML into a framework-agnostic        PARALLEL SAFE ✅
                              Synthesis Directive for the Builder. Use BEFORE 'implement'
                              when a genome exists in specs/genomes/. The directive lands
                              in specs/temp/synthesis_{genome_id}.md which the Builder reads.
                              args = path to genome YAML (e.g. "specs/genomes/product_explorer.yaml").
                              GENOME WORKFLOW: synthesize → implement → ui_validate → phenotype verify.
- 'mutate'      (Mutation     Runs the Genetic Feedback Loop: scans factory_logs, updates SEQUENTIAL 🔒
                 Engine):     Fitness Ledger, and mutates under-performing agent DNA.
                              Only needed when you want to force a mutation outside the
                              automatic post-batch OODA cycle. args = "" or "--force".
- 'sandbox'     (Sandbox):    Runs build+verify pipeline directly on a spec file.        SEQUENTIAL 🔒
                              Triggers inner_loop: LLM generates → tsc/lint/vite build →
                              self-heals up to 5 rounds. Use when you need guaranteed
                              green-build output, or after 'implement' fails ui_validate.
                              args = spec file path (e.g. "specs/interface/02_inventory_grid.md").
                              SANDBOX MAKEOVER: If the Chief wants to rebuild a component
                              from scratch with a clean verified state, queue 'sandbox'
                              directly. It replaces the stale Stitch/human-input workflow.
- 'explain'     (None):       Plain-English answer; no queue.                          PARALLEL SAFE ✅

SPEC PATH RESOLUTION RULE:
  When routing to a spec, ALWAYS use the EXACT filename listed in the Project Status Report
  under 'Interface Specs'. Do NOT invent or guess filenames. If the user asks for a feature
  that maps to an existing spec, use that spec's path from the list. If no spec exists yet,
  queue a 'design' task to create one FIRST.

OUTPUT FORMAT (JSON ONLY — no markdown fences):
{
    "thought": "Internal reasoning: what does the user REALLY need? What are the edge cases?",
    "mentor_insight": "A deep dive into the architectural reasoning, trade-offs, and strategic lessons the user should be aware of.",
    "explanation": "Clear, jargon-free explanation of the plan.",
    "proposal": "I will [action] because [reason].",
    "queue": [
        {"tool": "commit",      "args": "Save current state before massive refactor", "parallel": false},
        {"tool": "design",      "args": "interface/settings_view.md",                  "parallel": true},
        {"tool": "design",      "args": "interface/profile_view.md",                   "parallel": true},
        {"tool": "implement",   "args": "interface/settings_view.md",                  "parallel": true},
        {"tool": "implement",   "args": "interface/profile_view.md",                   "parallel": true},
        {"tool": "diagnose",    "args": "",                                            "parallel": false},
        {"tool": "doc",         "args": "",                                            "parallel": false}
    ]
}

TASK-FORCE FORMAT (for complex, cross-domain tasks):
{
    "thought": "This needs frontend + backend changes. Time for a Task Force.",
    "mentor_insight": "Cross-domain features require strict contracts. We use a Task Force so the Steerer can define the API boundary before the Builder writes code, preventing integration bugs later.",
    "explanation": "Assembling a Task Force: Steerer designs the contract, Builder codes it, Watchdog reviews.",
    "proposal": "I will spin up a Task Force for this cross-domain feature.",
    "queue": [
        {
            "tool": "task_force",
            "id": "accessory_engine",
            "agents": ["steerer", "builder", "watchdog"],
            "goal": "Implement cross-sell accessories on Product Detail",
            "parallel": false
        }
    ]
}

RULES:
- ALWAYS use the "queue" key (even for a single task — wrap it in an array).
- Set "parallel": true for tasks that touch DIFFERENT files or are read-only.
- Set "parallel": false for 'commit', 'build', 'heal', 'doc', 'reflect', 'task_force' — they mutate shared state.
- For 'implement', the "args" MUST be the spec filename to implement (from the Interface Specs list in the status report).
- For 'optimize', the "args" MUST be the relative file path to refactor.
  ⚠️  ANTI-HALLUCINATION RULE: NEVER invent file paths for 'optimize'. Only schedule
  an 'optimize' task when you KNOW the file exists. If unsure, use 'diagnose' first.
- **TASK_FORCE vs IMPLEMENT RULE (CRITICAL):**
  NEVER schedule 'task_force' for a feature that affects only the frontend OR only the backend.
  Use 'task_force' ONLY when a feature needs BOTH a new API endpoint AND a new UI component.
  For everything else, use 'design' (if no spec exists yet) followed by 'implement'.
  Wrong: task_force for "add a copy SKU button" (pure frontend).
  Right: design + implement for "add a copy SKU button".
  Right: task_force for "implement a new JIT endpoint consumed by a new Detail tab".
- **GENERATIVE PIPELINE (use this for NEW features with no existing spec):**
  Step 1: 'design' (args = desired spec path, e.g. "interface/my_feature.md") — creates the spec.
  Step 2: 'implement' (args = that same spec path) — builds the code.
  Step 3: 'ui_validate' — confirms Vite build passes.
  Step 4: 'commit' — saves the result.
  The Chief has FULL authority to generate specs and implement them end-to-end without human approval at each step.
- For 'explain', use a single queue item with "args" containing the answer text.
- For 'reflect', the "args" MUST be a short description of the failure/lesson context.
- Sequential tasks act as BARRIERS: all parallel tasks before them must finish first.
- **TDD RULE (Phase 1):** For ANY new feature or component that does not yet have a
  corresponding test file, you MUST queue a 'design' task to write a test spec BEFORE
  the 'implement' task. The 'design' args must be a test spec path, e.g.
  'tests/specs/<feature>_test.md' or 'specs/behavior/<feature>_scenarios.md'.
  NEVER queue 'implement' for a new feature without a preceding 'design' task that
  produces a test spec. If the feature already has test scenarios in specs/behavior/,
  this rule is satisfied — do not duplicate.
  Example TDD queue:
    {"tool": "design",    "args": "specs/behavior/new_feature_scenarios.md", "parallel": true},
    {"tool": "implement", "args": "interface/new_feature.md",                "parallel": false}
- **UI VALIDATE RULE:** After ANY batch of 'implement' tasks that touch frontend specs
  (specs/interface/ or component files), you MUST queue a sequential 'ui_validate' task
  immediately after the parallel batch closes, before 'diagnose' or 'commit'. This catches
  Vite runtime import errors that 'diagnose' (tsc/eslint) silently misses.
  Example: parallel implements → 'ui_validate' (sequential) → 'diagnose' → 'commit'.

RECOVERY MODE (triggered when FAILURE REPORT is present):
- Read the error output carefully. Identify the root cause.
- **ESCALATION LADDER (self-resolving, no human needed):**
  Level 1: `heal`         → For TypeScript/Python compile errors (auto-patches code).
  Level 2: `implement`    → For logic/runtime errors (re-implements from spec).
  Level 3: `sandbox`      → Escalate here only when implement fails ui_validate after Level 2.
                            Use the spec path that maps to the failing component.
  NEVER skip levels — always start at Level 1 and only escalate if that level fails.
- Prefer 'optimize' for import or lint errors in a single known file.
- Always explain the root cause clearly in "explanation".
- Never re-run a task that already succeeded.
- If the error is a missing API key or network failure, use 'explain' to advise the user.
- **MANDATORY REFLECTION RULE:** If you successfully queue 'heal' to fix a bug, you MUST
  also queue a 'reflect' task immediately after it (sequential). The 'reflect' args should
  summarize the failure context so the Mentor Agent can record the lesson in
  docs/LEARNED_GUIDELINES.md. Example:
    {"tool": "heal",    "args": "",                               "parallel": false},
    {"tool": "reflect", "args": "TS type error in InventoryView.tsx — missing product.id field", "parallel": false}

MEMORY RULE:
- Before planning any task, assume that docs/LEARNED_GUIDELINES.md has been injected
  into every agent's context automatically. You do NOT need to route agents to read it;
  it is already there. Your job is only to WRITE to it via 'reflect' after failures.

SENIOR TECH LEAD RULE:
- When the PROJECT STATUS REPORT contains a "SENIOR TECH LEAD SCAN" section, treat its
  findings as HIGH-PRIORITY factory health signals. You MUST acknowledge them in your
  "thought" field and, if any [STUB] or [INTEGRITY] issues appear, schedule the
  appropriate fix tasks (e.g., 'implement' for stubs, 'heal' for integrity errors)
  BEFORE the user's new feature work. Stub files left in place will corrupt the app.
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
    """Scans the factory floor and reads the Master Plan to establish global context."""
    state = []

    # --- 0. INJECT THE SPINE (The Master Plan / Ubiquitous Language) ---
    if MASTER_PLAN_PATH.exists():
        with open(MASTER_PLAN_PATH, "r", encoding="utf-8") as f:
            master_plan = f.read()
        state.append(
            "=== THE MASTER PLAN (UBIQUITOUS LANGUAGE & DIRECTORY) ===")
        state.append(master_plan)
        state.append(
            "=========================================================\n")
    else:
        state.append(
            "⚠️  WARNING: The Spine (specs/strategy/master_plan.md) is missing. "
            "Agents lack global product context.\n"
        )

    # --- 0a. INJECT EVOLUTION PROPOSALS (Scout briefings) ---
    evolution_dir = ROOT_DIR / "specs" / "strategy" / "evolution"
    if evolution_dir.exists():
        proposals = sorted(evolution_dir.glob("*.md"))
        if proposals:
            # Surface only the 3 most recent proposals to stay concise
            recent = proposals[-3:]
            state.append(
                "=== SCOUT EVOLUTION PROPOSALS (pending Chief review) ===")
            for p in recent:
                state.append(f"\n--- {p.name} ---")
                state.append(p.read_text(encoding="utf-8")
                             [:1200])  # cap per file
            state.append("=== END EVOLUTION PROPOSALS ===\n")
            state.append(
                "CHIEF DIRECTIVE: Review the proposals above. If any RECOMMEND verdict "
                "aligns with the Master Plan's current gaps, schedule a 'scout' or "
                "'task_force' to integrate the tool. Otherwise, acknowledge and proceed."
            )

    # 1. Git status
    git_status = get_git_status()
    state.append(f"Git Status: {git_status}")

    # 2. Check Specs — categorised for better Chief routing
    interface_specs_dir = SPECS_DIR / "interface"
    if interface_specs_dir.exists():
        canonical = ["01_operator_dashboard.md", "02_inventory_grid.md",
                     "03_product_intelligence.md", "04_natural_explorer_ux.md"]
        all_iface = sorted(interface_specs_dir.glob("*.md"))
        canon_found = [s for s in all_iface if s.name in canonical]
        feature_specs = [s for s in all_iface if s.name not in canonical]
        state.append(
            f"\nInterface Specs \u2014 CANONICAL ({len(canon_found)}/4):")
        for s in canon_found:
            state.append(f"  ✓ specs/interface/{s.name}")
        missing_canon = [n for n in canonical
                         if not (interface_specs_dir / n).exists()]
        for m in missing_canon:
            state.append(f"  ⚠ MISSING: specs/interface/{m}")
        state.append(
            f"\nInterface Specs \u2014 FEATURE LEVEL ({len(feature_specs)} specs):")
        for s in feature_specs:
            state.append(f"  - specs/interface/{s.name}")
    else:
        state.append("MISSING: specs/interface directory not found.")

    other_spec_dirs = ["data_pipeline", "01_data", "behavior", "repairs"]
    for sdir in other_spec_dirs:
        sd = SPECS_DIR / sdir
        if sd.exists():
            files = list(sd.glob("*.md"))
            if files:
                state.append(f"\nSpecs \u2014 {sdir}/ ({len(files)} files):")
                for f in sorted(files):
                    state.append(f"  - specs/{sdir}/{f.name}")

    # 3. Check Frontend views
    if FRONTEND_DIR.exists():
        views = list(FRONTEND_DIR.glob("*.tsx"))
        cockpit_dir = FRONTEND_DIR.parent / "cockpit"
        cockpit_files = list(cockpit_dir.glob(
            "*.tsx")) if cockpit_dir.exists() else []
        state.append(
            f"\nFrontend Views ({len(views)}): {[v.name for v in views]}")
        if cockpit_files:
            state.append(
                f"Frontend Cockpit components ({len(cockpit_files)}): "
                f"{[c.name for c in cockpit_files]}")
    else:
        state.append(
            "MISSING: Frontend views folder is empty or does not exist.")

    # 4. Specific artifact checks
    taxonomy = ROOT_DIR / "backend" / "data" / "learned_taxonomy.json"
    if not taxonomy.exists():
        state.append(
            "WARNING: Backend data artifact (learned_taxonomy.json) is missing — run 'build' to generate it.")
    else:
        state.append(
            "Backend data artifacts present (learned_taxonomy.json exists).")

    # 5. Factory health check
    fitness_ledger = ROOT_DIR / "backend" / \
        "data" / "genome" / "fitness_ledger.json"
    if fitness_ledger.exists():
        try:
            import json as _json
            ledger = _json.loads(fitness_ledger.read_text(encoding="utf-8"))
            agents = ledger.get("agents", {})
            if agents:
                low_fitness = [(a, round(d.get("score", 1.0), 2))
                               for a, d in agents.items()
                               if d.get("score", 1.0) < 0.75]
                if low_fitness:
                    state.append(
                        f"\n⚠️  LOW-FITNESS AGENTS (consider scheduling 'mutate'): "
                        + ", ".join(f"{a}({s})" for a, s in low_fitness)
                    )
        except Exception:
            pass

    return "\n".join(state)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def consult_chief(user_input: str, is_startup: bool = False,
                  failure_context: str = "",
                  tech_lead_context: str = "") -> dict:
    """
    Takes a plain-English user request (or a startup trigger) and returns
    a structured task queue plan.

    Args:
        user_input:         Plain-English instruction from the operator.
        is_startup:         True when called on first boot (no user input yet).
        failure_context:    Raw error output from failed tasks. When provided,
                            the Chief enters Recovery Mode and produces a fix plan.
        tech_lead_context:  LLM-free heuristics report from the Senior Tech Lead
                            Agent. Injected into context so the Chief factors in
                            live factory health before planning.

    Returns a dict with keys: thought, explanation, proposal, queue.
    The 'queue' is a list of {"tool", "args", "parallel"} dicts.
    """
    project_state = get_project_state()

    senior_block = ""
    if tech_lead_context and tech_lead_context.strip():
        senior_block = f"\n{tech_lead_context}\n"

    context_prompt = f"""
--- PROJECT STATUS REPORT ---
{project_state}{senior_block}-----------------------------
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

    # Expose the Chief's thinking process to the Operator
    print("\n" + "="*60)
    print("🧠 THE CHIEF'S THINKING PROCESS")
    print("="*60)
    print(f"🤔 THOUGHT:\n   {result.get('thought', 'N/A')}\n")

    if "mentor_insight" in result:
        print(f"🎓 MENTOR INSIGHT:\n   {result['mentor_insight']}\n")

    print(f"📢 EXPLANATION:\n   {result.get('explanation', 'N/A')}\n")
    print(f"🎯 PROPOSAL:\n   {result.get('proposal', 'N/A')}")
    print("="*60)

    if result.get("queue"):
        print(f"\n📋 QUEUE ({len(result['queue'])} tasks):")
        for i, t in enumerate(result["queue"], 1):
            mode = "⚡ PARALLEL" if t.get("parallel") else "🔒 SEQUENTIAL"
            print(f"   {i}. {mode} | {t['tool']} {t.get('args', '')}")
    else:
        print("\n📋 QUEUE: Empty (No tasks scheduled)")
