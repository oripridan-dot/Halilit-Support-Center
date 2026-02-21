"""
SPEC ARCHITECT AGENT
Translates vague human intent into rigorous "Dark Factory" Markdown specifications.
Usage: python spec_writer.py 'I want a button that...' [category]
"""
import sys
import re
from pathlib import Path

# Project root (backend/factory -> backend -> root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Import from same package
try:
    from agent_core import query_llm, save_artifact
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from agent_core import query_llm, save_artifact

SYSTEM_PROMPT = """
You are the SPEC ARCHITECT for "Halilit Support Center — Dark Factory".
You translate vague human desires into rigorous technical specifications in Markdown.

OUTPUT FORMAT (follow exactly):
# Spec: [Title]
**Target:** [relative/file/path]

## Overview
One paragraph describing the purpose of the component or service.

## Requirements
- [Requirement 1]
- [Requirement 2]
- ...

## Data Contract
Describe input props / API request+response shapes relevant to this feature.

## Behavior Scenarios
- **Scenario:** [Name]
  - Input: [Data or action]
  - Outcome: [Expected behavior or rendered state]

## Out of Scope
- [What this spec does NOT cover]

RULES:
1. Be explicit about the Target file path.
2. For frontend: use React 18 + TypeScript + Tailwind CSS (dark theme, slate-900/blue-500 palette).
3. For backend: use Python 3.11+ + FastAPI + Pydantic v2.
4. NEVER propose synthetic or mock data — compliance with Three Source Rules is mandatory.
5. Keep scenarios testable and unambiguous.
"""


def generate_spec(user_request: str, category: str = "interface") -> None:
    """
    Generates a Dark Factory spec from a plain-text feature request.
    Saves to specs/<category>/<filename>.md
    """
    print(f"📐 Designing Spec for: '{user_request}'...")

    prompt = f"""
Create a strict technical specification for the following feature request:
"{user_request}"

Determine if this is a UI component/view, a Backend Service/endpoint, or a Data Script.
Suggest a sensible relative file path for the Target (from the project root).
Make the spec complete enough for an AI coding agent to implement it without further questions.
"""

    content = query_llm(SYSTEM_PROMPT, prompt, temperature=0.5)

    if not content:
        print("❌ Architect failed to generate spec.")
        return

    # Derive filename from spec title
    name_match = re.search(r'^#\s*Spec:\s*(.+)', content, re.MULTILINE)
    filename = "new_feature"
    if name_match:
        raw_name = name_match.group(1).strip()
        filename = re.sub(r'[^a-z0-9]+', '_', raw_name.lower()).strip('_')

    # Save to specs/<category>/<filename>.md
    spec_dir = PROJECT_ROOT / "specs" / category
    spec_dir.mkdir(parents=True, exist_ok=True)
    output_path = spec_dir / f"{filename}.md"

    save_artifact(str(output_path), content)
    print(f"✅ Spec written to: specs/{category}/{filename}.md")
    print(
        f"   Next step → review the spec, then: python factory.py build specs/{category}/{filename}.md")


# ---------------------------------------------------------------------------
# JIT Innovation Pipeline entry-point
# ---------------------------------------------------------------------------

JIT_SYSTEM_PROMPT = """You are the SPEC ARCHITECT for "Halilit Support Center — Dark Factory".
A new feature has been approved by the Boardroom. Translate the operator's need and the
Boardroom's architectural verdict into a rigorous Markdown specification.

OUTPUT FORMAT (follow exactly):
# Spec: [Title]
**Target:** [relative/file/path]

## Overview
One paragraph describing the feature.

## Requirements
- [Requirement 1]
- ...

## Data Contract
Describe API request/response shapes or React prop types.

## Behavior Scenarios
- **Scenario:** [Name]
  - Input: [Data or action]
  - Outcome: [Expected behavior]

## Out of Scope
- [What this spec does NOT cover]

CRITICAL RULE: You MUST append a JSON block at the very end, enclosed in ```json ... ```,
listing the exact file paths that need to be CREATED OR MODIFIED.
Example:
```json
{"files_to_scaffold": ["frontend/src/components/NewFeature.tsx", "backend/api/new_route.py"]}
```

RULES:
1. Frontend: React 18 + TypeScript + Tailwind CSS (dark theme, slate-900/blue-500 palette).
2. Backend: Python 3.11+ + FastAPI + Pydantic v2.
3. NEVER propose synthetic or mock data — Three Source Rules are absolute law.
4. Keep file paths realistic — they must fit the existing project structure.
"""


def generate_jit_specification(
    need_description: str,
    boardroom_verdict: str,
    timestamp: int | None = None,
) -> tuple[str, list[str]]:
    """
    Called by the JIT Innovation Pipeline (innovation_router.py).

    Writes a formal Markdown spec to specs/interface/JIT_SPEC_<ts>.md
    and extracts the ``files_to_scaffold`` JSON array embedded in the spec.

    Returns:
        (spec_relative_path, files_to_scaffold_list)
    """
    import json as _json
    import time as _time

    if timestamp is None:
        timestamp = int(_time.time())

    print("\n📐 SPEC WRITER: Drafting formal technical specification…")

    prompt = (
        f"Operator Need: {need_description}\n\n"
        f"Boardroom Architecture:\n{boardroom_verdict}"
    )

    content = query_llm(JIT_SYSTEM_PROMPT, prompt, temperature=0.4)

    if not content:
        print("   ❌ Spec Writer: LLM returned empty content.")
        return f"specs/interface/JIT_SPEC_{timestamp}.md", []

    # Write spec to disk
    spec_dir = PROJECT_ROOT / "specs" / "interface"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_filename = f"JIT_SPEC_{timestamp}.md"
    spec_path = spec_dir / spec_filename
    spec_path.write_text(content, encoding="utf-8")
    print(f"   ✅ Formal Spec written to: specs/interface/{spec_filename}")

    # Extract files_to_scaffold JSON embedded in the spec
    files_to_scaffold: list[str] = []
    try:
        json_block = content.split("```json")[1].split("```")[0].strip()
        files_to_scaffold = _json.loads(
            json_block).get("files_to_scaffold", [])
    except Exception:
        pass  # Graceful degradation — no JSON block

    return f"specs/interface/{spec_filename}", files_to_scaffold


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python spec_writer.py 'Feature description' [category]")
        print("  category defaults to 'interface'")
        sys.exit(1)

    request = sys.argv[1]
    cat = sys.argv[2] if len(sys.argv) > 2 else "interface"
    generate_spec(request, cat)
