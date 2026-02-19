"""
THE PATCHER — Surgical File Modification Agent
Halilit Support Center v9.6.1 Dark Factory

Receives a file path and a plain-English instruction, then rewrites ONLY the
affected file using the FAST model tier. Designed for quick, targeted edits
(fix a colour, rename a label, tweak a threshold) without rebuilding from
a full spec.

Usage:
    python factory.py patch <relative/path/to/file> "instruction"

Example:
    python factory.py patch frontend/src/components/views/InventoryView.tsx \
        "Change the low-stock badge colour from yellow to orange"
"""

import re
import sys
from pathlib import Path

# agent_core lives in the same directory
try:
    from agent_core import query_llm, save_artifact, FAST_MODEL
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from agent_core import query_llm, save_artifact, FAST_MODEL

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are the CODE PATCHER — a surgical code modification agent.

You receive an EXISTING FILE and a PLAIN-ENGLISH REQUEST.

RULES:
1. OUTPUT ONLY THE COMPLETE REWRITTEN FILE — no markdown fences (no ```), no commentary.
2. Apply ONLY the requested change. Do NOT refactor, rename, or "improve" anything else.
3. Preserve every import, every comment, every line that is not related to the request.
4. Use the same code style as the original file (indentation, quotes, semicolons, etc.).
5. TypeScript/React: keep all existing hook signatures, prop types, and component structure.
"""


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def patch_file(file_path: str, request: str) -> None:
    """
    Read *file_path*, apply *request* using the FAST model, write it back.
    """
    target = Path(file_path)
    if not target.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    code = target.read_text(encoding="utf-8")
    extension = target.suffix.lstrip(".")

    prompt = f"""FILE: {file_path}
LANGUAGE: {extension}

CURRENT CONTENT:
{code}

REQUEST: {request}

Rewrite the complete file with ONLY the above request applied.
Output ONLY raw code — no markdown fences, no explanation.
"""

    print(f"🩹  Patcher is applying: \"{request}\"")
    print(f"    Target : {file_path}")
    print(f"    Model  : {FAST_MODEL}")

    new_code = query_llm(SYSTEM_PROMPT, prompt,
                         temperature=0.05, model_tier="fast")

    if not new_code:
        print("❌ Patcher received no response from model.")
        sys.exit(1)

    # Strip accidental markdown fences that some models add despite instructions
    clean = re.sub(r"^```[a-zA-Z]*\n", "", new_code, flags=re.MULTILINE)
    clean = re.sub(r"\n```\s*$", "", clean, flags=re.MULTILINE)
    clean = clean.strip()

    # Safety guard: refuse to write an empty file
    if len(clean) < 50:
        print("❌ Patcher output is suspiciously short — aborting to protect the file.")
        print(f"   Raw output was: {repr(new_code[:200])}")
        sys.exit(1)

    target.write_text(clean, encoding="utf-8")
    print(f"✅  Patched: {file_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python patcher_agent.py <file_path> \"instruction\"")
        sys.exit(1)

    patch_file(sys.argv[1], sys.argv[2])
