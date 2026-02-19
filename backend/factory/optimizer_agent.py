"""
CODE OPTIMIZER AGENT — Halilit Support Center Dark Factory
Refactors an existing source file for readability, strict typing, and
performance — without changing observable behaviour.

Usage (via factory.py):
  python factory.py optimize frontend/src/components/views/InventoryView.tsx

Direct:
  python optimizer_agent.py /absolute/path/to/file.tsx
"""
import sys
import re
from pathlib import Path

# agent_core lives in the same package
from agent_core import query_llm, get_project_context

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

SYSTEM_PROMPT = """
You are the CODE OPTIMIZER inside a Dark Factory for a React/TypeScript application.
Your mission:
  1. Remove unused imports.
  2. Extract inline/anonymous types to named interfaces or type aliases.
  3. Improve variable and function names where they are cryptic.
  4. Add concise JSDoc comments for non-obvious logic.
  5. Prefer `const` over `let`; prefer explicit return types on exported functions.

CRITICAL RULES:
  - Do NOT change component behavior, props API, or visual output.
  - Do NOT introduce new dependencies.
  - Do NOT add, remove, or rearrange React hooks.
  - Output the FULL improved file — no truncation, no ellipsis.
"""


def _strip_markdown_fences(text: str) -> str:
    """Remove leading/trailing code fences that LLMs sometimes emit."""
    text = re.sub(r"^```[a-zA-Z]*\n", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n```\s*$", "", text, flags=re.MULTILINE)
    return text.strip()


def optimize_file(file_path: str | Path) -> bool:
    """
    Refactor *file_path* in-place.
    Returns True on success, False if the LLM call failed or output looks bad.
    """
    target = Path(file_path)
    if not target.exists():
        print(f"❌ File not found: {target}")
        return False

    suffix = target.suffix.lower()
    if suffix in {".ts", ".tsx"}:
        context_type = "frontend"
    elif suffix in {".py"}:
        context_type = "backend"
    else:
        context_type = "frontend"  # default

    print(f"💎 Polishing: {target.relative_to(ROOT_DIR)}…")
    code = target.read_text(encoding="utf-8")

    project_context = get_project_context(context_type)

    prompt = f"""
PROJECT CONTEXT
===============
{project_context}

SOURCE FILE: {target.relative_to(ROOT_DIR)}
============
{code}

TASK
====
Refactor the source file following the SYSTEM PROMPT rules.
Output the COMPLETE improved file content — nothing else.
Do NOT wrap the output in markdown fences.
"""

    optimized = query_llm(SYSTEM_PROMPT, prompt, temperature=0.05)

    if not optimized:
        print("❌ Optimizer received no response from the LLM.")
        return False

    cleaned = _strip_markdown_fences(optimized)

    # Sanity-check: the output must look like real code
    has_code_markers = any(
        marker in cleaned
        for marker in ["import ", "const ", "function ", "def ", "class ", "export "]
    )
    if not has_code_markers or len(cleaned) < 50:
        print("⚠️  LLM output does not look like valid code — aborting write.")
        print("   Raw output preview:", cleaned[:200])
        return False

    # Back up the original
    backup = target.with_suffix(target.suffix + ".bak")
    backup.write_text(code, encoding="utf-8")

    # Write optimized version
    target.write_text(cleaned, encoding="utf-8")
    print(f"✨ Optimized: {target.relative_to(ROOT_DIR)}")
    print(f"   Original backed up to: {backup.relative_to(ROOT_DIR)}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python optimizer_agent.py <absolute_file_path>")
        sys.exit(1)

    success = optimize_file(sys.argv[1])
    sys.exit(0 if success else 1)
