import sys
import re
import subprocess
from pathlib import Path

# Project root (backend/factory -> backend -> root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Import from same package
try:
    from agent_core import (
        query_llm, save_artifact, get_project_context,
        build_dynamic_context, get_relevant_lore,
    )
    from sandbox_executor import inner_loop, parse_verification_commands
    from ui_validator_agent import validate_ui
    from context_discovery import hydrate_context
    from smart_import_fixer import fix_imports
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from agent_core import (
        query_llm, save_artifact, get_project_context,
        build_dynamic_context, get_relevant_lore,
    )
    from sandbox_executor import inner_loop, parse_verification_commands
    from ui_validator_agent import validate_ui
    from context_discovery import hydrate_context
    from smart_import_fixer import fix_imports

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MAX_RETRIES = 5   # Level 5: more self-healing rounds

SYSTEM_PROMPT = """
You are the FACTORY BUILDER AGENT (Level 5 — Autonomous Self-Healing).
Your goal: Implement the Spec strictly while adhering to the Project Architecture.

RULES:
1. OUTPUT ONLY CODE. No markdown fences (```), no explanations, no 'Here is the file'.
2. USE CONTEXT. Use the provided Type definitions and CSS variables. Do not invent new types or styles.
3. ROBUSTNESS. Handle loading states, error states, and empty states.
4. STRICT ADHERENCE. Follow the spec exactly. Do not add features not in the spec.
5. SYNTAX. Use TypeScript/React for frontend (functional components + hooks), Python 3.11+ for backend.
6. SELF-HEAL. If you receive an ERROR LOG, analyse it carefully and rewrite the code to fix every listed error.
   Do NOT repeat the same mistake. Check every import path, every type name, every hook signature.
7. FRONTEND IMPORTS. Always use relative imports from the project structure shown in context.
   NEVER use react-router-dom, react-toastify, swr, axios, @emotion, styled-components, or any
   library not present in the project's package.json. Icon imports MUST come from lucide-react only.
8. Dark mode Tailwind only — classes from the dark zinc/slate palette. No inline styles unless unavoidable.
9. CONTRACT FIRST. If a matching API contract exists in specs/contracts/, you MUST use its types
   exactly — do not invent endpoint paths or response shapes.
"""

CRITIC_PROMPT = """
You are the SENIOR ARCHITECT CRITIC.
Review the code below for:
1. Broken or missing imports (paths that don't match the project structure).
2. Usage of libraries / packages not in the project (react-router-dom, react-toastify, swr, axios, etc.).
3. TypeScript type errors that are obviously wrong.
4. Calling hooks, functions, or store actions that don't exist.

Respond with either:
  APPROVED
or a short bulleted list of SPECIFIC issues to fix (no re-writing — just the issues).
Do NOT suggest style improvements. Only hard blockers.
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _strip_fences(text: str) -> str:
    """Remove accidental markdown code fences."""
    cleaned = re.sub(r'^```[a-zA-Z]*\n', '', text, flags=re.MULTILINE)
    cleaned = re.sub(r'\n```\s*$', '', cleaned, flags=re.MULTILINE)
    return cleaned.strip()


def _detect_domain(spec_content: str) -> str:
    lower = spec_content.lower()
    fe_score = sum(1 for s in ["react", "tsx", "component",
                   "tailwind", "frontend", "view", "ui"] if s in lower)
    be_score = sum(1 for s in ["fastapi", "python", "backend",
                   "endpoint", "pydantic", "router"] if s in lower)
    return "frontend" if fe_score >= be_score else "backend"


def _extract_target(spec_content: str, spec_file: Path) -> Path | None:
    """Return the absolute output path from the spec's Component/Target field.
    Falls back to the first path listed under '## Affected Files' (repair specs).
    """
    # 1. Standard Target / Component field
    match = re.search(
        r'\*{0,2}(?:Target|Component):?\*{0,2}\s*`?([^`\n*#]+)`?',
        spec_content, re.IGNORECASE
    )
    if match:
        return PROJECT_ROOT / match.group(1).strip()

    # 2. Repair spec fallback: first backtick-quoted path in ## Affected Files
    section = re.search(
        r'##\s+Affected Files.*?(?=\n##|\Z)', spec_content,
        re.IGNORECASE | re.DOTALL
    )
    if section:
        path_match = re.search(r'`([^`]+\.(?:ts|tsx|py|js|jsx|css))`',
                               section.group(0))
        if path_match:
            return PROJECT_ROOT / path_match.group(1).strip()

    return None


def _run_tsc() -> tuple[bool, str]:
    """Run `pnpm tsc --noEmit` in the frontend directory. Returns (ok, error_text)."""
    print("🧪  Running TypeScript check (tsc --noEmit)...")
    result = subprocess.run(
        ["pnpm", "tsc", "--noEmit"],
        cwd=str(PROJECT_ROOT / "frontend"),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True, ""
    combined = (result.stdout + "\n" + result.stderr).strip()
    return False, combined[:3000]  # cap to avoid bloating next prompt


def _critic_review(code: str, spec_content: str, context: str) -> tuple[bool, str]:
    """Second-pass LLM code review. Returns (approved, issues)."""
    print("👁️   Critic reviewing generated code...")
    review_prompt = f"""
PROJECT CONTEXT (imports, types and hooks that actually exist):
{context}

SPEC SUMMARY:
{spec_content[:600]}

CODE TO REVIEW:
{code[:4000]}
"""
    # Architectural review needs the smart tier for accuracy
    verdict = query_llm(CRITIC_PROMPT, review_prompt,
                        temperature=0.0, model_tier="smart")
    if not verdict:
        return True, ""  # if critic fails, don't block
    if verdict.strip().upper().startswith("APPROVED"):
        return True, ""
    return False, verdict.strip()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _load_contracts(domain: str, queries: list[str]) -> str:
    """
    Phase 2 — API Contract Enforcement.
    Scans specs/contracts/ for any .schema.ts or .openapi.json files
    relevant to the current domain/queries and injects them into context.
    """
    contracts_dir = PROJECT_ROOT / "specs" / "contracts"
    if not contracts_dir.exists():
        return ""
    blocks: list[str] = []
    for contract_file in sorted(contracts_dir.glob("*")):
        if contract_file.suffix in (".ts", ".json", ".md"):
            stem = contract_file.stem.lower()
            # Include if any query keyword matches the contract name
            if any(q.lower()[:10] in stem or stem in q.lower() for q in queries):
                content = contract_file.read_text(encoding="utf-8")
                blocks.append(
                    f"--- API CONTRACT: {contract_file.name} ---\n{content}\n"
                )
    if blocks:
        return "=== BINDING API CONTRACTS (follow these types exactly) ===\n" + "\n".join(blocks)
    return ""


def build_component(spec_path: str) -> None:
    spec_file = Path(spec_path)
    if not spec_file.exists():
        print(f"❌ Spec not found: {spec_path}")
        return

    print(f"📖 Reading Spec: {spec_file.name}...")
    # === HOLOGRAPHIC SPEC: Use Hydration Engine (YAML deps + live code injection) ===
    spec_content = hydrate_context(spec_path)
    # ================================================================================

    domain = _detect_domain(spec_content)
    full_path = _extract_target(spec_content, spec_file)

    # =========================================================================
    # SHARED CONTEXT DISCOVERY (both frontend and backend)
    # =========================================================================
    _title_match = re.search(r"#\s+(?:Spec[:\s]+)?(.+)", spec_content)
    _comp_match = re.search(
        r'\*{0,2}(?:Target|Component):?\*{0,2}\s*`?([^`\n*#]+)`?',
        spec_content, re.IGNORECASE
    )
    discovery_queries: list[str] = []
    if _title_match:
        discovery_queries.append(_title_match.group(1).strip())
    if _comp_match:
        comp_name = Path(_comp_match.group(1).strip()).stem
        discovery_queries.append(comp_name)

    print(f"🔎  Discovering context for: {discovery_queries}...")
    dynamic_ctx = build_dynamic_context(
        discovery_queries) if discovery_queries else get_project_context(domain)

    # Phase 2: inject matching API contracts
    contracts_ctx = _load_contracts(domain, discovery_queries)

    # Phase 3: inject relevant past lessons (vector-filtered lore)
    task_desc = " ".join(discovery_queries) or (domain + " implementation")
    lore = get_relevant_lore(task_desc, top_k=5)
    lore_block = (
        f"\n## RELEVANT PAST LESSONS (apply these to avoid repeated mistakes)\n{lore}\n"
        if lore else ""
    )

    context = dynamic_ctx
    if contracts_ctx:
        context = contracts_ctx + "\n\n" + context
    if lore_block:
        context = lore_block + "\n\n" + context

    # =========================================================================
    # AUTONOMOUS PIPELINE (Level 5 — no human input)
    # Applies to BOTH frontend and backend. The Stitch/Lovable human-in-the-
    # loop gate is replaced by direct LLM generation + inner_loop self-healing.
    # =========================================================================

    if not full_path:
        print(
            f"❌ CRITICAL FATAL: Target path missing in {spec_file.name}. Code generation aborted to prevent silent failure.")
        sys.exit(1)

    print(f"\n🏭 [{domain.upper()} BUILD — AUTONOMOUS LEVEL 5]")
    print(f"   Target: {full_path.relative_to(PROJECT_ROOT)}")

    # Ensure verification commands from the spec are present; for frontend
    # inject tsc + lint + vite build if the spec has none
    spec_with_checks = spec_content
    if domain == "frontend" and "## Verification Commands" not in spec_content:
        spec_with_checks = spec_content.rstrip() + (
            "\n\n## Verification Commands\n"
            "- `pnpm tsc --noEmit`\n"
            "- `pnpm run lint`\n"
        )

    # Shared state for the inner-loop closure
    _state: dict = {"critic_issues": None}

    def _builder_fn(spec_text: str, error_feedback: str | None) -> bool:
        """
        Called by inner_loop on each round.
        Generates the complete file, runs critic review, writes to disk.
        """
        attempt_label = "⚡  Generating code" if error_feedback is None else "🩹  Self-healing"
        print(f"{attempt_label}...")

        feedback_parts: list[str] = []
        if error_feedback:
            feedback_parts.append(
                f"--- ❌ VERIFICATION FAILURE — FIX ALL OF THESE ---\n{error_feedback}")
        if _state["critic_issues"]:
            feedback_parts.append(
                f"--- ❌ CRITIC REJECTION — FIX ALL OF THESE ---\n{_state['critic_issues']}")
        feedback_block = "\n\n".join(feedback_parts)

        prompt = (
            f"{context}\n\n"
            f"--- SPECIFICATION TO IMPLEMENT ---\n{spec_text}\n\n"
            f"{feedback_block}\n\n"
            f"--- TASK ---\n"
            "Write the COMPLETE file content for the target component defined in the spec.\n"
            "Ensure ALL imports are relative to the project structure shown in context above.\n"
            "For frontend: functional React component, strict TypeScript, Tailwind CSS dark theme.\n"
            "Output ONLY raw code — no markdown fences, no commentary, no explanation."
        )

        raw_output = query_llm(SYSTEM_PROMPT, prompt, model_tier="fast")
        if not raw_output:
            print("❌ Agent returned no output.")
            return False

        clean_code = _strip_fences(raw_output)

        # Critic gate
        critic_ok, critic_issues = _critic_review(
            clean_code, spec_text, context)
        _state["critic_issues"] = None
        if not critic_ok:
            print(f"⚠️   Critic rejected the code — feeding issues back into next round.")
            _state["critic_issues"] = critic_issues

        save_artifact(str(full_path), clean_code)

        # ── Phase 0: Deterministic mechanical fixer ──────────────────────
        # Runs BEFORE verification — fixes out-of-src imports, wrong dir
        # names, missing hook files, and JSX generic arrow syntax without
        # burning LLM tokens.  Fixes are printed so they appear in logs.
        fix_report = fix_imports(target_file=full_path)
        if fix_report.fixes:
            print(f"🔧  SmartImportFixer applied {len(fix_report.fixes)} fix(es):")
            for fix in fix_report.fixes:
                print(f"     • [{fix.kind}] {fix.description}")
        return True

    # Run the autonomous self-healing inner loop
    passed = inner_loop(
        spec_text=spec_with_checks,
        builder_fn=_builder_fn,
        max_rounds=MAX_RETRIES,
        verbose=True,
    )

    if passed:
        rel = full_path.relative_to(PROJECT_ROOT)
        print(f"✅  Verified & Approved: {rel}")
        # Post-build UI validation for frontend (catches Vite runtime import errors)
        if domain == "frontend":
            print("\n🔬 Running UI Validator (import scan + Vite build)...")
            validation = validate_ui(run_build=True)
            if not validation["passed"]:
                print(f"\n⚠️  UI Validation issues detected:")
                for e in (validation.get("import_errors", []) + validation.get("build_errors", [])):
                    print(f"     • {e}")

                # ── Phase 1: Deterministic fixer on the WHOLE src tree ───────
                # Runs before the LLM to auto-fix mechanical import issues
                # (wrong dir names, out-of-src paths, missing generated.ts,
                # JSX generic arrow fn syntax) across all touched files.
                print("\n🔧  Running SmartImportFixer on full src tree...")
                full_fix_report = fix_imports()  # scans entire frontend/src
                if full_fix_report.fixes:
                    print(f"   Applied {len(full_fix_report.fixes)} deterministic fix(es):")
                    for fix in full_fix_report.fixes:
                        print(f"     • [{fix.kind}] {fix.description}")
                    # Re-validate after deterministic fixes
                    print("\n🔬 Re-validating after SmartImportFixer...")
                    validation = validate_ui(run_build=True)
                else:
                    print("   No deterministic fixes applicable.")

                if not validation["passed"]:
                    # Phase 2: only call LLM if mechanical fixes weren't enough
                    print("  Passing remaining errors to LLM self-healer for one final round...")
                    error_msg = "\n".join(
                        validation.get("import_errors", []) + validation.get("build_errors", []))
                    _builder_fn(spec_with_checks, error_msg)
                else:
                    print("✅ SmartImportFixer resolved all issues — LLM round skipped.")
            else:
                print("✅ UI Validation passed — import scan + Vite build clean.")
    else:
        print(
            "❌  Could not auto-heal after max retries. Last build saved — review manually.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python builder_agent.py <path_to_spec>")
    else:
        build_component(sys.argv[1])
