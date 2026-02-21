"""
STITCH MCP  (backend/mcp/servers/stitch_mcp.py)
================================================
Internal UI synthesis engine — autonomously generates pristine
React + Tailwind CSS visual shells using the project LLM.

This eliminates the need for the Operator to manually copy-paste
code from external design tools. The Swarm calls `generate_stitch_ui_shell`
to get the "face" of a component, then the Builder Agent wires
the real backend hooks into that shell.

THREE SOURCE RULES COMPLIANCE:
  - Generated shells use PLACEHOLDER slots ({{product.name}}, etc.)
    NOT fabricated product data. Real data always comes from the
    authorised sources (Commercial / Official / Contextual).

Exposed via factory_mcp_server.py as the `generate_stitch_ui_shell` tool.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

STITCH_SYSTEM_PROMPT = """You are the Halilit Internal Stitch Engine — a world-class UI/UX design engine
for the Halilit Support Center (a dark-mode enterprise SaaS app for musical instrument operators).

Your ONLY purpose: generate stunning, modern, enterprise-grade React + Tailwind CSS visual shells.

ABSOLUTE RULES:
1. OUTPUT ONLY a pristine React functional component (TypeScript .tsx).
2. Use ONLY Tailwind CSS for styling. Never write inline styles or CSS modules.
3. Dark mode ONLY. Color palette: bg-zinc-950 / bg-zinc-900 backgrounds, blue-500 accents,
   text-zinc-100 / text-zinc-400 text, border-zinc-800 borders. Hover: hover:bg-zinc-800.
4. ICONS: Use lucide-react exclusively. Never heroicons or other icon libraries.
5. PLACEHOLDER DATA ONLY. Do NOT invent or hardcode real product names, prices, SKUs, or specs.
   Use clearly labelled slot strings: {{product.name}}, {{product.price}}, {{product.sku}},
   {{product.brand}}, {{product.category}}, {{product.imageUrl}}, {{product.description}}.
6. NO business logic, state management, or API calls. The shell is visual only.
   Props must accept the real data shape so the Builder Agent can wire hooks into it cleanly.
7. Make it look like a $50,000 enterprise dashboard: sticky headers, subtle dividers,
   smooth hover transitions, proper spacing, badge components for status.
8. DO NOT wrap the output in markdown fences. Return raw TSX only.
9. Component must be a named export (e.g. `export function InventoryGrid(...)`).
10. Include a sensible TypeScript Props interface at the top of the component.
"""

# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------


def generate_stitch_ui_shell(design_prompt: str, component_name: str = "UIComponent") -> dict:
    """Generate a pure React/Tailwind visual shell from a plain-English design prompt.

    Uses the project LLM (Gemini via backend.llm) to produce a pristine TSX shell that
    the Builder Agent can merge real backend hooks into.

    Args:
        design_prompt: Plain-English description of the desired UI component.
        component_name: Name hint for the React component (e.g. "InventoryGrid").

    Returns:
        dict with keys:
          - component_name: str
          - shell_code: str  (raw TSX)
          - design_prompt: str
          - instructions: str  (merge guidance for the Builder Agent)
    """
    print(
        f"\n🎨  STITCH ENGINE: Generating pristine UI shell for '{design_prompt}'...")

    try:
        from backend.llm import get_llm  # type: ignore
        llm = get_llm()
    except Exception as e:
        return {
            "error": f"LLM unavailable: {e}",
            "component_name": component_name,
            "design_prompt": design_prompt,
        }

    user_prompt = (
        f"Design a React/Tailwind TSX visual shell for: {design_prompt}\n\n"
        f"Component name: {component_name}\n\n"
        "Remember: placeholder slots ({{product.name}} etc.), no real data, no API calls.\n"
        "Return raw TSX only — no markdown fences."
    )

    shell_code, ok = llm.call(
        "StitchEngine",
        user_prompt,
        system=STITCH_SYSTEM_PROMPT,
        use_cache=False,
    )

    if not ok:
        return {
            "error": "LLM call failed. Check GEMINI_API_KEY.",
            "component_name": component_name,
            "design_prompt": design_prompt,
        }

    # Strip any accidental markdown fences
    import re
    shell_code = re.sub(r'^```[a-zA-Z]*\n', '', shell_code, flags=re.MULTILINE)
    shell_code = re.sub(r'\n```\s*$', '', shell_code,
                        flags=re.MULTILINE).strip()

    print(f"   ✅  UI shell generated ({len(shell_code)} chars).")

    merge_instructions = (
        f"MERGER INSTRUCTIONS FOR BUILDER AGENT:\n"
        f"The shell above is the visual face of `{component_name}`.\n"
        f"Your task:\n"
        f"  1. Replace every {{{{product.X}}}} placeholder with the correct field\n"
        f"     from the `ConductorProduct` type (frontend/src/types/index.ts).\n"
        f"  2. Wire `useConductorCatalog` (or the relevant hook) to supply the data.\n"
        f"  3. Do NOT change a single Tailwind class — the layout is frozen.\n"
        f"  4. Add loading skeleton (same Tailwind palette) and error state.\n"
        f"  5. Ensure all lucide-react imports are correct (match package.json)."
    )

    return {
        "component_name": component_name,
        "design_prompt": design_prompt,
        "shell_code": shell_code,
        "instructions": merge_instructions,
    }
