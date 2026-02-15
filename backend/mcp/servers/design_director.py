"""
MCP Server: Design Director (v2)
Orchestrates a "Design Competition" for the full Halilit App Suite.

Supported Components:
1. GalaxyDashboard (Discovery Layer)
2. SpectrumModule (Search & Filter Layer)
3. ProductPage (Detail & Intelligence Layer)

Run standalone:
    PYTHONPATH=. python backend/mcp/servers/design_director.py

Listens on http://localhost:8300/mcp (SSE transport).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

logger = logging.getLogger("mcp.server.design_director")

app = FastAPI(title="Halilit Design Director")

# Project root
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
_FRONTEND_VIEWS = _PROJECT_ROOT / "frontend" / "src" / "components" / "views"
_ARENA_DIR = _FRONTEND_VIEWS / "arena"

# -------------------------------------------------------------------------
# 1. THE LOGIC (Data Contracts & Requirements)
# -------------------------------------------------------------------------

COMPONENT_LOGIC = {
    "GalaxyDashboard": """
**FUNCTIONAL LOGIC:**
- This is the Home/Landing view (category browser).
- **Goal:** Visual exploration of the catalog taxonomy.
- **Data Source:** useConductorCatalog() returns: { isLoading, error, refetch, galaxyCounts, spectrumCounts, metadata }.
- **Taxonomy Structure:** 6 galaxies: guitars-bass, drums-percussion, keys-production, studio-recording, live-dj, accessories-utility. Each has 6-7 spectrum subcategories.
- **Category Data Shape:** Map from UNIVERSAL_CATEGORIES to { id, name, icon, iconComponent, color, children: [{ id, name, image, fallbackGradient }] }.
- **Navigation:** Clicking a subcategory calls goToSpectrum(mainCategoryId, subcategoryId, []) from useNavigationStore.
- **Health Display:** Show metadata.health_score (0-100), metadata.health_status ('COMPLETE'|'GOOD'|'PARTIAL'|'MINIMAL').
- **Graph Stats:** metadata.graph_stats.total_families, metadata.graph_stats.total_relationships.
- **Backend Connectivity:** Health check at /api/health with 6s timeout. Show "Cannot reach server" full-screen if unreachable.
- **Loading States:** Skeleton grid (3x2 sectors), slow-load message after 12s.
- **Sample Data Detection:** Single brand "sample" triggers hint banner.
- **Icons:** lucide-react (Guitar, Music, Piano, Mic2, Speaker, Plug).
- **Sub-component:** CategorySlot - aspect-square, image + label + count, hover spotlight effect. Each slot shows spectrum count from spectrumCounts.
- **Layout:** 3x2 grid of galaxy sectors; each sector has header (icon + name) and 4-column grid of CategorySlot children.
""",
    "SpectrumModule": """
**FUNCTIONAL LOGIC:**
- This is the Search & Filter view (product spectrum by brand and price).
- **Goal:** Narrow down products to the perfect one. Visual price spectrum.
- **Data Source:** useProductsBySpectrum(activeSubcategoryId) for products; useConductorCatalog() for metadata, galaxies, families.
- **Product Shape (ConductorProduct):** id, name, brand, brand_logo, galaxy_id, spectrum_id, price, price_eilat, tier, market_price_estimate, image_url, image_gallery, description, specs, features, rating, review_count, pros, cons, quality_score, data_status, data_trust, family_id, variant_key.
- **Core Features:**
  1. Price spectrum: Log-scale horizontal axis, ₪ (ILS) currency.
  2. Four pricing tiers: Entry (0-500, green), Mid (500-1500, blue), Pro (1500-4000, purple), Flagship (4000+, amber).
  3. Zoom lens with minimap (focus range on price axis).
  4. Brand track grouping: products grouped by brand in horizontal lanes.
  5. Series sub-tracks within brands (e.g. "ART" within RCF).
  6. Family grouping: variant_of relationships create stacked cards.
  7. Smart tags filtering (auto-generated: "Has Image", "Official Specs", brand names).
  8. Accessory filtering: accessories excluded from main view.
  9. Product hover preview: image, specs, data sources badge (Commercial/Official/Contextual).
- **Navigation:** goToGalaxy() for back, openProductPage(productId) for product detail.
- **Data Trust Display:** Three-source badges - Halilit Commercial (blue), Brand Official (green), Contextual Reviews (amber).
- **Source Rules:** Price ONLY from Commercial Scout; Specs ONLY from Official Scout; Reviews ONLY from Contextual Scout (3+ sites).
- **Existing Utilities:** getBrandLogoUrl(), getBrandTheme(), generateSmartTags(), ImageWithFallback.
""",
    "ProductPage": """
**FUNCTIONAL LOGIC:**
- This is the "Mission Control" detail view.
- **Data Source:** product object from useConductorCatalog (or product page API).
- **Strict Data Zones (The Law):**
  1. **Commercial Header:** Price (product.price), Stock, SKU - Halilit.com only.
  2. **Official Grid:** Main Specs (product.specs), Description, Images - brand pages only.
  3. **Contextual Sidebar:** Reviews (product.reviews), pros/cons - 3+ trusted review sites.
- **Interaction:** "Add to Cart" button, "Compare" toggle.
""",
}

# -------------------------------------------------------------------------
# 2. THE STYLES (The Competitors)
# -------------------------------------------------------------------------

STYLES = {
    "A": {
        "name": "The Industrial Pro",
        "vibe": "High density, data-heavy, Sweetwater/Thomann vibes. Dark grays, amber warnings, monospace fonts. For serious audio engineers. Use 'Geist Mono' or 'JetBrains Mono' feel. Dense information layout, minimal ornamentation.",
    },
    "B": {
        "name": "The Cyber-Futurist",
        "vibe": "Neon glows, glassmorphism, Teenage Engineering vibes. Deep blacks, glowing blues/purples, animated borders. Immersive and gamified. Use large blur effects, subtle gradients, glow accents.",
    },
    "C": {
        "name": "The Radical Minimalist",
        "vibe": "Stark black & white, massive typography, Apple/Braun vibes. Huge whitespace, no borders, focus purely on the product image. High fashion. Swiss Design. Let content breathe.",
    },
}


# -------------------------------------------------------------------------
# TOOL 1: BRIEF GENERATOR
# -------------------------------------------------------------------------


def _handle_generate_briefs(arguments: dict[str, Any]) -> dict[str, Any]:
    component = arguments.get("component_name", "ProductPage")

    logic = COMPONENT_LOGIC.get(component)
    if not logic:
        return {
            "error": f"Unknown component: {component}. Supported: {list(COMPONENT_LOGIC.keys())}"
        }

    briefs = {}
    for key, style in STYLES.items():
        prompt = f"""
ACT AS: Senior UI Designer specializing in '{style["name"]}'.
TASK: Create a React/TypeScript/Tailwind component for '{component}'.

### VISUAL STYLE: {style["vibe"]}

### REQUIRED LOGIC (DO NOT BREAK THIS):
{logic}

### IMPLEMENTATION DETAILS:
- Use 'lucide-react' for icons.
- Use standard Tailwind classes (no arbitrary values if possible).
- Use dark theme: bg-zinc-950, text-zinc-100, border-zinc-800.
- Mock data interfaces if needed, but match the field names in the logic.
- Import paths should be relative: '../../hooks/useConductorCatalog', '../../store/navigationStore', etc.
- OUTPUT: Just the React/TSX code. No markdown, no explanations.
"""
        briefs[f"Option_{key}"] = prompt

    return {
        "status": "success",
        "instructions": f"Paste these 3 prompts into Lovable.dev or v0.dev. Save results as '{component}A.tsx', '{component}B.tsx', '{component}C.tsx' in frontend/src/components/views/arena/.",
        "prompts": briefs,
    }


# -------------------------------------------------------------------------
# TOOL 2: SCAFFOLD DESIGN ARENA
# -------------------------------------------------------------------------


def _handle_scaffold_arena(arguments: dict[str, Any]) -> dict[str, Any]:
    component_name = arguments.get("component_name", "GalaxyDashboard")
    target_path = _FRONTEND_VIEWS / "DesignArena.tsx"

    # Arena supports both Galaxy and Spectrum - scaffold (plain string, no f-string)
    code = '''import React, { useState } from "react";
import { Monitor, Zap, Hexagon, LayoutGrid, ScanLine } from "lucide-react";

// Arena variant components - create these files and uncomment
// import { GalaxyDashboardA } from "./arena/GalaxyDashboardA";
// import { GalaxyDashboardB } from "./arena/GalaxyDashboardB";
// import { GalaxyDashboardC } from "./arena/GalaxyDashboardC";
// import { SpectrumModuleA } from "./arena/SpectrumModuleA";
// import { SpectrumModuleB } from "./arena/SpectrumModuleB";
// import { SpectrumModuleC } from "./arena/SpectrumModuleC";

type ComponentType = "GalaxyDashboard" | "SpectrumModule";
type Variant = "A" | "B" | "C";

export const DesignArena = () => {
  const [activeComponent, setActiveComponent] = useState<ComponentType>("GalaxyDashboard");
  const [activeVariant, setActiveVariant] = useState<Variant>("A");

  return (
    <div className="w-full h-full flex flex-col bg-[#050505] text-white">
      {/* Tab bar: Component + Variant switcher */}
      <div className="h-16 border-b border-zinc-800 flex items-center justify-between px-6 bg-zinc-950/95 z-50 shrink-0">
        <div className="flex items-center gap-4">
          <span className="text-zinc-500 font-mono text-xs tracking-widest uppercase mr-2">
            Design Competition
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setActiveComponent("GalaxyDashboard")}
              className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 ${activeComponent === "GalaxyDashboard" ? "bg-blue-600/80 text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`}
            >
              <LayoutGrid size={14} /> Galaxy
            </button>
            <button
              onClick={() => setActiveComponent("SpectrumModule")}
              className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 ${activeComponent === "SpectrumModule" ? "bg-blue-600/80 text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`}
            >
              <ScanLine size={14} /> Spectrum
            </button>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveVariant("A")}
            className={`px-4 py-2 rounded-full text-xs font-bold flex items-center gap-2 transition-all ${activeVariant === "A" ? "bg-amber-600 text-white shadow-lg shadow-amber-900/50" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`}
          >
            <Monitor size={14} /> Industrial
          </button>
          <button
            onClick={() => setActiveVariant("B")}
            className={`px-4 py-2 rounded-full text-xs font-bold flex items-center gap-2 transition-all ${activeVariant === "B" ? "bg-purple-600 text-white shadow-lg shadow-purple-900/50" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`}
          >
            <Zap size={14} /> Futurist
          </button>
          <button
            onClick={() => setActiveVariant("C")}
            className={`px-4 py-2 rounded-full text-xs font-bold flex items-center gap-2 transition-all ${activeVariant === "C" ? "bg-white text-black shadow-lg shadow-white/20" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`}
          >
            <Hexagon size={14} /> Minimalist
          </button>
        </div>
      </div>

      {/* Stage - replace with actual components once files exist */}
      <div className="flex-1 overflow-hidden relative">
        <div className="absolute inset-0 flex flex-col items-center justify-center text-zinc-500 font-mono text-sm pointer-events-none">
          <p className="mb-2">Create arena variants and uncomment imports above.</p>
          <p className="text-xs opacity-60">
            {activeComponent} variant {activeVariant}
          </p>
        </div>
        {/* Uncomment when variant files exist:
        <div className="w-full h-full overflow-auto">
          {activeComponent === "GalaxyDashboard" && activeVariant === "A" && <GalaxyDashboardA />}
          {activeComponent === "GalaxyDashboard" && activeVariant === "B" && <GalaxyDashboardB />}
          {activeComponent === "GalaxyDashboard" && activeVariant === "C" && <GalaxyDashboardC />}
          {activeComponent === "SpectrumModule" && activeVariant === "A" && <SpectrumModuleA />}
          {activeComponent === "SpectrumModule" && activeVariant === "B" && <SpectrumModuleB />}
          {activeComponent === "SpectrumModule" && activeVariant === "C" && <SpectrumModuleC />}
        </div>
        */}
      </div>
    </div>
  );
};
'''

    _ARENA_DIR.mkdir(parents=True, exist_ok=True)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(code, encoding="utf-8")

    return {
        "status": "success",
        "file_created": str(target_path.relative_to(_PROJECT_ROOT)),
        "arena_dir": str(_ARENA_DIR.relative_to(_PROJECT_ROOT)),
        "message": f"Design Arena scaffolded. Create GalaxyDashboardA/B/C.tsx and SpectrumModuleA/B/C.tsx in arena/, then uncomment the imports in DesignArena.tsx.",
    }


# -------------------------------------------------------------------------
# MCP Tool Registry
# -------------------------------------------------------------------------

TOOLS = {
    "generate_design_briefs": {
        "name": "generate_design_briefs",
        "description": "Generates 3 contrasting design prompts for GalaxyDashboard, SpectrumModule, or ProductPage.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "component_name": {
                    "type": "string",
                    "enum": ["GalaxyDashboard", "SpectrumModule", "ProductPage"],
                    "description": "Component to generate design briefs for",
                },
            },
            "required": ["component_name"],
        },
        "handler": _handle_generate_briefs,
    },
    "scaffold_design_arena": {
        "name": "scaffold_design_arena",
        "description": "Creates the React DesignArena component to view 3 design variants side-by-side for Galaxy and Spectrum.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "component_name": {
                    "type": "string",
                    "description": "Optional: component name for context (default GalaxyDashboard)",
                    "default": "GalaxyDashboard",
                },
            },
        },
        "handler": _handle_scaffold_arena,
    },
}


# -------------------------------------------------------------------------
# MCP JSON-RPC Handler
# -------------------------------------------------------------------------


@app.post("/mcp")
async def mcp_endpoint(request: Request) -> JSONResponse:
    """Handle MCP JSON-RPC 2.0 requests."""
    body = await request.json()
    method = body.get("method", "")
    req_id = body.get("id", 0)
    params = body.get("params", {})
    arguments = params.get("arguments", {})

    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "halilit-design-director",
                    "version": "1.0.0",
                },
                "capabilities": {
                    "tools": {"listChanged": False},
                },
            },
        })

    if method == "tools/list":
        tool_list = [
            {
                "name": t["name"],
                "description": t["description"],
                "inputSchema": t["inputSchema"],
            }
            for t in TOOLS.values()
        ]
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": tool_list},
        })

    if method == "tools/call":
        tool_name = params.get("name", "")
        tool = TOOLS.get(tool_name)
        if not tool:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"},
            })

        try:
            result = tool["handler"](arguments)
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result,
            })
        except Exception as exc:
            logger.exception("Tool %s failed", tool_name)
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(exc)},
            })

    return JSONResponse({
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method '{method}' not supported"},
    })


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = int(os.getenv("MCP_DESIGN_DIRECTOR_PORT", "8300"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
