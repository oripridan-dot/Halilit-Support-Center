"""
V0 DESIGN AGENT  (backend/factory/v0_agent.py)
===============================================
Bridges the Dark Factory to v0.dev.

Two responsibilities:
  1. generate_v0_prompt(description, component_type)
     → Calls Gemini to produce a detailed, structured v0.dev-ready prompt
       that enforces Halilit architecture rules (Three Source Rules, Tailwind
       dark theme, lucide-react icons, correct hook imports).

  2. integrate_v0_output(v0_code, target_file)
     → Takes raw TSX pasted from v0.dev, runs it through the Halilit
       Integration Engine (same rules as ui_bridge.py) and writes the
       result to the target file.

Can be called from:
  - factory.py  (CLI: python factory.py v0_design "description")
  - factory_mcp_server.py  (MCP tool: factory_v0_design)
  - nexus.py  (swarm tool: v0_design)
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

_GENERATOR_SYSTEM = """
You are the Halilit UI Architect. Generate a DETAILED PROMPT for v0.dev.

The generated prompt MUST enforce:
1. STYLE: Dark mode. Background: bg-zinc-950 or bg-zinc-900. Accents: blue-500.
   Text: text-zinc-100 / text-zinc-400.  Borders: border-zinc-800.
2. ICONS: Use lucide-react only. Never use heroicons or other icon libraries.
3. DATA SLOTS — explicitly request UI zones for each data source:
   - Zone A (Commercial / Halilit): price (₪), Eilat price (₪ Eilat),
     stock status (badge: OUT OF STOCK / UNCONFIRMED / In Stock), SKU.
   - Zone B (Official / Brand): product title, full specs table,
     hero image, description.
   - Zone C (Contextual / Reviews): pros list, cons list, star rating,
     source count badge.
4. PLACEHOLDERS: NO hardcoded product names, prices, or SKUs.
   Use {{product.name}}, {{product.price}}, {{product.sku}} etc.
5. HOOKS: Note that in the real implementation, data will come from
   `useConductorCatalog()` and navigation from `useNavigationStore()`.
6. ACCESSIBILITY: Include aria-labels on interactive elements.
7. OUTPUT: Ask v0 to output a single self-contained TSX component.

Return ONLY the prompt text — no preamble, no markdown fences.
"""

_INTEGRATOR_SYSTEM = """
You are the Halilit Code Integration Engine. Refactor raw v0.dev TSX output
into a production-ready Halilit component.

RULES:
1. Replace any static mock data with prop access or hook data:
   - Product data: use props or `useConductorCatalog()` patterns
   - Navigation: import `useNavigationStore` from '../../store/navigationStore'
   - Catalog hook: import `useConductorCatalog` from '../../hooks/useConductorCatalog'
2. Replace any <img> tag with <ImageWithFallback> if a product image is shown.
   Import: `import ImageWithFallback from '../ImageWithFallback'`
3. Preserve ALL Tailwind CSS classes exactly as v0 output them.
4. Keep ALL lucide-react icon imports.
5. Add TypeScript prop types at the top of the file.
6. Ensure the file has `export default <ComponentName>` at the end.
7. Remove any hardcoded strings that should come from data.
8. Output ONLY valid TSX — no markdown fences, no explanations.
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    try:
        from google import genai  # type: ignore
        return genai.Client(api_key=api_key)
    except ImportError:
        return None


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:tsx?|jsx?|typescript|javascript)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_v0_prompt(description: str, component_type: str = "UIComponent") -> dict[str, Any]:
    """
    Generate a structured v0.dev prompt from a plain-English description.

    Returns:
        {
            "status": "success" | "error",
            "component_type": str,
            "v0_prompt": str,          # paste this into v0.dev
            "instructions": str,       # what to do next
        }
    """
    client = _get_client()
    if not client:
        # Return a structured prompt without Gemini enhancement
        raw_prompt = _build_fallback_prompt(description, component_type)
        return {
            "status": "success",
            "component_type": component_type,
            "v0_prompt": raw_prompt,
            "instructions": (
                "1. Copy the v0_prompt and paste it into https://v0.dev\n"
                "2. When v0 generates the TSX, copy the full component code\n"
                "3. Call factory_v0_design again with v0_output_code + target_file "
                "to integrate it into the codebase"
            ),
        }

    user_msg = (
        f"Component type: {component_type}\n"
        f"Description: {description}\n\n"
        "Generate the v0.dev prompt now."
    )
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[_GENERATOR_SYSTEM, user_msg],
        )
        v0_prompt = response.text.strip()
    except Exception as e:
        v0_prompt = _build_fallback_prompt(description, component_type)

    return {
        "status": "success",
        "component_type": component_type,
        "v0_prompt": v0_prompt,
        "instructions": (
            "1. Copy the v0_prompt and paste it into https://v0.dev\n"
            "2. When v0 generates the TSX, copy the full component code\n"
            "3. Call factory_v0_design again with v0_output_code + target_file "
            "to integrate it into the codebase"
        ),
    }


def integrate_v0_output(v0_code: str, target_file: str) -> dict[str, Any]:
    """
    Integrate raw v0.dev TSX output into the Halilit codebase.

    Args:
        v0_code:     Raw TSX from v0.dev
        target_file: Relative path where the component should be saved
                     (e.g. frontend/src/components/ProductCard.tsx)

    Returns:
        {"status": "success"|"error", "file_written": str, "message": str}
    """
    if not v0_code.strip():
        return {"status": "error", "message": "v0_output_code is empty"}

    full_path = _ROOT / target_file.lstrip("/")
    full_path.parent.mkdir(parents=True, exist_ok=True)

    client = _get_client()
    if client:
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    _INTEGRATOR_SYSTEM,
                    f"Refactor this v0.dev output for the Halilit codebase:\n\n{v0_code}",
                ],
            )
            integrated = _strip_fences(response.text)
        except Exception:
            integrated = _strip_fences(v0_code)
    else:
        integrated = _strip_fences(v0_code)

    if len(integrated.strip()) < 50:
        return {"status": "error", "message": "Integration produced empty output — raw code not written"}

    # Backup existing file
    if full_path.exists():
        backup = full_path.with_suffix(".bak.tsx")
        backup.write_text(full_path.read_text(
            encoding="utf-8"), encoding="utf-8")

    full_path.write_text(integrated, encoding="utf-8")

    return {
        "status": "success",
        "file_written": str(full_path.relative_to(_ROOT)),
        "message": f"Component integrated and written to {target_file}",
    }


def _build_fallback_prompt(description: str, component_type: str) -> str:
    return f"""Build a React TypeScript component: {component_type}

Description: {description}

STYLE REQUIREMENTS:
- Dark mode only. Background: bg-zinc-950. Card backgrounds: bg-zinc-900.
- Accent color: blue-500 for interactive elements, emerald-400 for success states.
- Text: text-zinc-100 (primary), text-zinc-400 (secondary), text-zinc-600 (muted).
- Borders: border-zinc-800. Rounded corners: rounded-xl.
- Use Tailwind CSS exclusively. No inline styles.

ICONS:
- Import icons from lucide-react only.

DATA ZONES (use placeholders, not hardcoded values):
- Commercial data (price, stock, SKU): show {{product.price}} ₪, {{product.stock}} status badge, {{product.sku}}
- Official data (title, specs, image): show {{product.name}}, {{product.description}}, specs table
- Source badges: small badge indicating data source (Commercial / Official / Contextual)

STRUCTURE:
- Single self-contained TSX component with TypeScript props interface at top
- export default at the bottom
- No external state management — accept all data as props

ACCESSIBILITY:
- Add aria-label to all buttons and interactive elements
- Use semantic HTML (nav, main, article as appropriate)
"""


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json as _json
    if len(sys.argv) < 2:
        print("Usage: python v0_agent.py 'description' [component_type]")
        sys.exit(1)
    desc = sys.argv[1]
    ctype = sys.argv[2] if len(sys.argv) > 2 else "UIComponent"
    result = generate_v0_prompt(desc, ctype)
    print(_json.dumps(result, indent=2))
