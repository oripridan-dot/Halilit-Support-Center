import sys
import re
from pathlib import Path

# Project root (backend/factory -> backend -> root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Import from same package (run with cwd=backend and PYTHONPATH=backend/factory or from backend/factory)
try:
    from agent_core import query_llm, save_artifact
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from agent_core import query_llm, save_artifact

# --- PROMPTS ---
SYSTEM_PROMPT = """
You are the FACTORY BUILDER AGENT.
Your job is to read a technical specification and generate production-ready code.

RULES:
1. OUTPUT ONLY CODE. No markdown fences (```), no explanations, no 'Here is the file'.
2. STRICT ADHERENCE. Follow the spec exactly. Do not add features not requested.
3. PROFESSIONAL STYLE. Use TypeScript/React for frontend, Python/FastAPI for backend.
4. IMPORT SAFETY. Assume standard imports. If unsure, ask for clarification (but usually just infer standard libs).
"""

def build_component(spec_path):
    spec_file = Path(spec_path)
    if not spec_file.exists():
        print(f"❌ Spec not found: {spec_path}")
        return

    print(f"📖 Reading Spec: {spec_file.name}...")
    spec_content = spec_file.read_text()

    # Create the Prompt
    prompt = f"""
    SOURCE SPECIFICATION:
    {spec_content}

    TASK:
    Based strictly on the spec above, write the full file content.
    The spec should define the target file path. If not, infer it based on the component name.

    If the spec defines 'Target File:' or 'Target:', extract that path.
    """

    # Agent "Thinks"
    print("⚙️  Agent is coding...")
    code_output = query_llm(SYSTEM_PROMPT, prompt)

    if not code_output:
        print("❌ Agent failed to generate code.")
        return

    # Clean up the output (remove markdown code blocks if the LLM slipped up)
    clean_code = re.sub(r'^```[a-z]*\n', '', code_output, flags=re.MULTILINE)
    clean_code = re.sub(r'\n```\s*$', '', clean_code, flags=re.MULTILINE)
    clean_code = clean_code.strip()

    # Extract target path from spec (e.g. "Target: path" or "**Target:** path")
    target_match = re.search(r'Target:\s*(?:\*\*)?\s*([^\n*#]+)', spec_content)
    if target_match:
        target_path = target_match.group(1).strip()
        full_path = PROJECT_ROOT / target_path
        save_artifact(str(full_path), clean_code)
    else:
        print("⚠️  Target path not found in Spec. Outputting to stdout:")
        print(clean_code)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python builder_agent.py <path_to_spec>")
    else:
        build_component(sys.argv[1])
