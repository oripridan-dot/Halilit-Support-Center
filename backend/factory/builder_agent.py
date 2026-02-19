import sys
import re
import subprocess
from pathlib import Path

# Project root (backend/factory -> backend -> root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Import from same package
try:
    from agent_core import query_llm, save_artifact, get_project_context, build_dynamic_context
    from sandbox_executor import inner_loop, parse_verification_commands
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from agent_core import query_llm, save_artifact, get_project_context, build_dynamic_context
    from sandbox_executor import inner_loop, parse_verification_commands

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MAX_RETRIES = 3

SYSTEM_PROMPT = """
You are the FACTORY BUILDER AGENT (Level 6 — Self-Healing).
Your goal: Implement the Spec strictly while adhering to the Project Architecture.

RULES:
1. OUTPUT ONLY CODE. No markdown fences (```), no explanations, no 'Here is the file'.
2. USE CONTEXT. Use the provided Type definitions and CSS variables. Do not invent new types or styles.
3. ROBUSTNESS. Handle loading states, error states, and empty states.
4. STRICT ADHERENCE. Follow the spec exactly. Do not add features not in the spec.
5. SYNTAX. Use TypeScript/React for frontend (functional components + hooks), Python 3.11+ for backend.
6. SELF-HEAL. If you receive an ERROR LOG, analyse it carefully and rewrite the code to fix every listed error.
   Do NOT repeat the same mistake. Check every import path, every type name, every hook signature.
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

def build_component(spec_path: str) -> None:
    spec_file = Path(spec_path)
    if not spec_file.exists():
        print(f"❌ Spec not found: {spec_path}")
        return

    print(f"📖 Reading Spec: {spec_file.name}...")
    spec_content = spec_file.read_text(encoding="utf-8")

    domain = _detect_domain(spec_content)

    # --- Dynamic Context Discovery (Pillar 1) --------------------------------
    # Extract meaningful search queries from the spec title and component path
    _title_match = re.search(r"#\s+Spec:\s*(.+)", spec_content)
    _comp_match = re.search(
        r"\*{0,2}(?:Target|Component):?\*{0,2}\s*`?([^`\n*#]+)`?", spec_content, re.IGNORECASE)
    discovery_queries: list[str] = []
    if _title_match:
        discovery_queries.append(_title_match.group(1).strip())
    if _comp_match:
        # e.g. "frontend/src/components/views/InventoryView.tsx" → "InventoryView"
        comp_name = Path(_comp_match.group(1).strip()).stem
        discovery_queries.append(comp_name)

    if discovery_queries:
        print(f"🔎  Discovering context for: {discovery_queries}...")
        dynamic_ctx = build_dynamic_context(discovery_queries)
    else:
        print(f"📥 Loading {domain} context (static fallback)...")
        dynamic_ctx = get_project_context(domain)

    context = dynamic_ctx
    full_path = _extract_target(spec_content, spec_file)

    # --- Closure: the builder_fn passed to inner_loop -------------------------
    # State shared across inner-loop rounds
    _state: dict = {"critic_issues": None}

    def _builder_fn(spec_text: str, error_feedback: str | None) -> bool:
        """
        Called by inner_loop on each round.
        Generates code, runs critic review, writes to disk.
        Returns True if code was written, False if LLM returned nothing.
        """
        attempt_label = "⚡  Generating code" if error_feedback is None else "🩹  Self-healing"
        print(f"{attempt_label}...")

        # Build feedback block from sandbox errors + previous critic issues
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
            "Write the COMPLETE file content for the target file defined in the spec.\n"
            "Ensure all imports are relative to the project structure in the context above.\n"
            "Output ONLY raw code — no markdown fences, no commentary."
        )

        raw_output = query_llm(SYSTEM_PROMPT, prompt, model_tier="fast")
        if not raw_output:
            print("❌ Agent returned no output.")
            return False

        clean_code = _strip_fences(raw_output)

        # Critic gate (before touching disk)
        critic_ok, critic_issues = _critic_review(
            clean_code, spec_text, context)
        _state["critic_issues"] = None
        if not critic_ok:
            print(f"⚠️   Critic rejected the code.")
            _state["critic_issues"] = critic_issues
            # Write anyway so inner_loop can run verification (which will also fail
            # and provide real compiler errors)

        if full_path:
            save_artifact(str(full_path), clean_code)
        else:
            print("⚠️  Target path not found in Spec. Printing to stdout:")
            print(clean_code)
            return False

        return True

    # --- Run the autonomous inner loop (Pillar 3) ----------------------------
    passed = inner_loop(
        spec_text=spec_content,
        builder_fn=_builder_fn,
        max_rounds=MAX_RETRIES,
        verbose=True,
    )

    if passed:
        rel = full_path.relative_to(
            PROJECT_ROOT) if full_path else spec_file.name
        print(f"✅  Verified & Approved: {rel}")
    else:
        print(
            "❌  Could not auto-heal after max retries. Last build saved — review manually.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python builder_agent.py <path_to_spec>")
    else:
        build_component(sys.argv[1])
