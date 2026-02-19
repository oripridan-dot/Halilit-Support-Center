import sys
import re
import subprocess
from pathlib import Path

# Project root (backend/factory -> backend -> root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Import from same package
try:
    from agent_core import query_llm, save_artifact, get_project_context
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from agent_core import query_llm, save_artifact, get_project_context

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
    print(f"📥 Loading {domain} context...")
    context = get_project_context(domain)

    full_path = _extract_target(spec_content, spec_file)

    base_task = (
        "Write the COMPLETE file content for the target file defined in the spec.\n"
        "Ensure all imports are relative to the project structure in the context above.\n"
        "Output ONLY raw code — no markdown fences, no commentary."
    )

    current_error: str | None = None
    critic_issues: str | None = None

    for attempt in range(MAX_RETRIES):
        if attempt == 0:
            print("⚡  Agent is coding...")
        else:
            print(f"🩹  Self-Healing attempt {attempt}/{MAX_RETRIES - 1}...")

        # Build prompt — include any feedback from previous iteration
        feedback_block = ""
        if current_error:
            feedback_block += f"\n\n--- ❌ PREVIOUS TSC ERRORS — FIX ALL OF THESE ---\n{current_error}\n"
        if critic_issues:
            feedback_block += f"\n\n--- ❌ CRITIC REJECTION — FIX ALL OF THESE ---\n{critic_issues}\n"

        prompt = (
            f"{context}\n\n"
            f"--- SPECIFICATION TO IMPLEMENT ---\n{spec_content}\n\n"
            f"{feedback_block}"
            f"--- TASK ---\n{base_task}"
        )

        # Coding is routine — use the fast/cheap tier
        raw_output = query_llm(SYSTEM_PROMPT, prompt, model_tier="fast")
        if not raw_output:
            print("❌ Agent returned no output.")
            return

        clean_code = _strip_fences(raw_output)

        # Critic pass (before touching disk)
        critic_ok, critic_issues = _critic_review(
            clean_code, spec_content, context)
        if not critic_ok:
            print(f"⚠️   Critic rejected the code. Rewriting…")
            current_error = None  # clear TSC error — focus on critic issues
            continue

        # Write to disk
        if full_path:
            save_artifact(str(full_path), clean_code)
        else:
            print("⚠️  Target path not found in Spec. Printing to stdout:")
            print(clean_code)
            return

        # TSC validation (frontend only)
        if domain == "frontend":
            tsc_ok, tsc_errors = _run_tsc()
            if tsc_ok:
                print(
                    f"✅  Verified & Approved: {full_path.relative_to(PROJECT_ROOT)}")
                return
            print(f"⚠️  TSC failed. Feeding errors back to agent…")
            current_error = tsc_errors
            critic_issues = None
        else:
            print(f"✅  Written: {full_path.relative_to(PROJECT_ROOT)}")
            return

    print("❌  Could not auto-heal after max retries. Last build saved — review manually.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python builder_agent.py <path_to_spec>")
    else:
        build_component(sys.argv[1])
