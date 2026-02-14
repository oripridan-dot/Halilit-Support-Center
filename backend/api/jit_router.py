"""
JIT Intelligence Router — SSE Streaming + Exploration Paths

Provides:
  GET  /api/jit/{product_id}/stream    — SSE stream: snap → promise → delivery
  POST /api/jit/explore                — Exploration action (comparison, deep-dive, etc.)
  GET  /api/jit/{product_id}/quick     — Non-streaming quick intelligence
"""

import asyncio
import json
import logging
import time
from typing import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jit", tags=["JIT Intelligence"])


# ═══════════════════════════════════════════════════════════════════════════
# SSE STREAMING INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════

def _sse_event(event: str, data: dict) -> str:
    """Format a Server-Sent Event."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _stream_intelligence(product_id: str) -> AsyncGenerator[str, None]:
    """
    Stream product intelligence in 3 phases:
      1. SNAP   — Instant skeleton data (< 100ms)
      2. PROMISE — Research progress updates
      3. DELIVER — Full enriched intelligence cards
    """
    from backend.server import _get_catalog

    # ── Phase 1: SNAP (instant skeleton from cache) ──
    catalog = _get_catalog()
    product = None
    for p in catalog.get("products", []):
        if p.get("id") == product_id:
            product = p
            break

    if not product:
        yield _sse_event("error", {"message": f"Product '{product_id}' not found"})
        return

    # Send skeleton immediately
    yield _sse_event("snap", {
        "id": product.get("id"),
        "name": product.get("name"),
        "brand": product.get("brand"),
        "price": product.get("price", 0),
        "price_eilat": product.get("price_eilat", 0),
        "tier": product.get("tier"),
        "image_url": product.get("image_url"),
        "image_gallery": product.get("image_gallery", []),
        "brand_logo": product.get("brand_logo"),
        "halilit_url": product.get("halilit_url"),
        "official_url": product.get("official_url"),
        "galaxy_id": product.get("galaxy_id"),
        "spectrum_id": product.get("spectrum_id"),
        "description": product.get("description", ""),
        "features": product.get("features", []),
        "specs": product.get("specs", {}),
        "family_id": product.get("family_id"),
        "variant_key": product.get("variant_key"),
        "quality_score": product.get("quality_score", 0),
        "data_status": product.get("data_status"),
    })

    # ── Phase 2: PROMISE (check cache or start research) ──
    from backend.jit_cache import get_cached_intelligence

    cached = get_cached_intelligence(product_id)
    if cached:
        # Skip research phase — deliver from cache instantly
        yield _sse_event("promise", {
            "step": "cache_hit",
            "message": "Loading cached intelligence…",
            "progress": 100,
        })
        await asyncio.sleep(0.1)  # Brief pause for UI transition

        # Deliver cached data
        try:
            yield _sse_event("deliver", _build_delivery_payload(product, cached))
            yield _sse_event("complete", {"cached": True, "duration_ms": 100})
        except Exception as e:
            logger.error(
                f"Failed to build delivery payload for {product_id} (cached): {e}")
            yield _sse_event("error", {"message": f"Failed to build product data: {str(e)}"})
        return

    # Research needed — stream progress updates
    brand = product.get("brand", "")
    research_steps = [
        {"step": "halilit", "message": f"Checking Halilit catalog…", "progress": 10},
        {"step": "brand", "message": f"Reading {brand} official page…", "progress": 30},
        {"step": "reviews", "message": "Scanning trusted review sites…", "progress": 55},
        {"step": "synthesis", "message": "Cross-validating sources…", "progress": 75},
        {"step": "rendering", "message": "Building intelligence cards…", "progress": 90},
    ]

    # Send progress events as the agent works
    t0 = time.time()

    # Start the actual synthesis in background
    from backend.jit_agent import ProductSynthesizer
    from backend.jit_cache import cache_intelligence

    synthesizer = ProductSynthesizer()

    # Stream progress concurrently with synthesis
    synthesis_task = asyncio.create_task(synthesizer.synthesize(product))

    for i, step in enumerate(research_steps):
        yield _sse_event("promise", step)
        # Wait a bit between steps, but check if synthesis is done
        wait = 0.8 if i < 3 else 0.5
        try:
            await asyncio.wait_for(asyncio.shield(synthesis_task), timeout=wait)
            # If synthesis finishes early, fast-forward remaining steps
            for remaining in research_steps[i + 1:]:
                remaining["progress"] = 100
                yield _sse_event("promise", remaining)
            break
        except asyncio.TimeoutError:
            pass  # Still working, send next progress

    # Wait for synthesis to complete
    try:
        enriched = await synthesis_task
    except Exception as e:
        logger.error(f"JIT synthesis failed for {product_id}: {e}")
        yield _sse_event("error", {"message": f"Research failed: {str(e)}"})
        return

    # Cache the result
    cache_intelligence(product_id, enriched)

    duration_ms = int((time.time() - t0) * 1000)

    # ── Phase 3: DELIVER ──
    try:
        yield _sse_event("deliver", _build_delivery_payload(product, enriched))
        yield _sse_event("complete", {"cached": False, "duration_ms": duration_ms})
    except Exception as e:
        logger.error(f"Failed to build delivery payload for {product_id}: {e}")
        yield _sse_event("error", {"message": f"Failed to build product data: {str(e)}"})


def _safe_layout_hints(enriched: dict) -> dict:
    """Ensure layout_hints is always a dict (agents sometimes return a list)."""
    hints = enriched.get("layout_hints", {})
    if isinstance(hints, dict):
        return hints
    return {}


def _is_genuinely_enriched(product: dict, enriched: dict) -> bool:
    """Check if the enriched data has meaningful content beyond the raw catalog."""
    catalog_desc = (product.get("description") or "").strip()
    enriched_desc = (enriched.get("description") or "").strip()

    # Description is different and non-trivial
    if enriched_desc and enriched_desc != catalog_desc and len(enriched_desc) > 20:
        return True
    # Has specs that the catalog didn't have
    catalog_specs = product.get("specs") or {}
    enriched_specs = enriched.get("specs") or {}
    if len(enriched_specs) > len(catalog_specs):
        return True
    # Has features
    if enriched.get("features") and len(enriched.get("features", [])) > 0:
        return True
    # Has review data
    if enriched.get("review_verdicts") or enriched.get("pros") or enriched.get("cons"):
        return True
    if enriched.get("famous_users") or enriched.get("known_issues"):
        return True
    return False


def _build_delivery_payload(product: dict, enriched: dict) -> dict:
    """Build the full delivery payload with all intelligence cards."""
    brand = product.get("brand", "")
    name = product.get("name", "")

    # Normalize layout_hints to always be a dict
    enriched["layout_hints"] = _safe_layout_hints(enriched)

    # Determine if the description is genuinely enriched (not just catalog echo)
    genuinely_enriched = _is_genuinely_enriched(product, enriched)
    catalog_desc = (product.get("description") or "").strip()
    enriched_desc = (enriched.get("description") or "").strip()

    # Only use enriched description for "verdict" if it's genuinely new content
    verdict_description = enriched_desc if (
        enriched_desc and enriched_desc != catalog_desc) else ""

    # Extract exploration paths
    exploration_paths = enriched.get("exploration_paths", [])
    if not exploration_paths:
        exploration_paths = _generate_default_explorations(product, enriched)

    return {
        # Core enriched data — verdict_description is empty if not genuinely enriched
        "description": verdict_description,
        "description_short": enriched.get("description_short", "") if genuinely_enriched else "",
        "specs": enriched.get("specs") or product.get("specs", {}),
        "features": enriched.get("features") or product.get("features", []),
        "enriched": genuinely_enriched,

        # Review intelligence
        "pros": enriched.get("pros", []),
        "cons": enriched.get("cons", []),
        "rating": enriched.get("rating", 0),
        "review_verdicts": enriched.get("review_verdicts", []),

        # Brand theming
        "brand_theme": enriched.get("brand_theme", {}),

        # Community intelligence
        "famous_users": enriched.get("famous_users", []),
        "known_issues": enriched.get("known_issues", []),
        "suggested_accessories": enriched.get("suggested_accessories", []),

        # Layout hints
        "layout_hints": enriched.get("layout_hints", {}),

        # Official links
        "official_url": enriched.get("official_url") or product.get("official_url", ""),

        # Exploration paths — the "Action Dock"
        "exploration_paths": exploration_paths,
    }


def _generate_default_explorations(product: dict, enriched: dict) -> list[dict]:
    """Generate smart exploration paths based on product context."""
    paths = []
    brand = product.get("brand", "")
    name = product.get("name", "")
    category = enriched.get("layout_hints", {}).get("product_category", "")

    # Always offer specs deep-dive
    if enriched.get("specs"):
        paths.append({
            "type": "deep_dive",
            "label": "Full Specifications",
            "icon": "specs",
            "description": f"Complete technical specifications for {name}",
            "action": {"type": "show_specs"},
        })

    # Comparison if alternatives exist
    if enriched.get("layout_hints", {}).get("show_comparison"):
        paths.append({
            "type": "comparison",
            "label": "Compare Models",
            "icon": "compare",
            "description": f"Side-by-side comparison with similar {category or 'products'}",
            "action": {"type": "compare"},
        })

    # Setup / How-to
    paths.append({
        "type": "how_to",
        "label": "Setup Guide",
        "icon": "setup",
        "description": f"How to set up and get the best from your {name}",
        "action": {"type": "explore", "topic": "setup"},
    })

    # Artist spotlight if we have famous users
    if enriched.get("famous_users"):
        paths.append({
            "type": "artist_spotlight",
            "label": "Who Uses This",
            "icon": "artists",
            "description": f"Famous artists and professionals who use {brand} {name}",
            "action": {"type": "explore", "topic": "artists"},
        })

    # Known issues / field notes
    if enriched.get("known_issues"):
        paths.append({
            "type": "field_notes",
            "label": "Field Notes",
            "icon": "warning",
            "description": "Real-world tips, known issues, and firmware notes",
            "action": {"type": "explore", "topic": "issues"},
        })

    # Upsell / accessories
    if enriched.get("suggested_accessories"):
        paths.append({
            "type": "accessories",
            "label": "Essential Accessories",
            "icon": "accessories",
            "description": f"Must-have accessories and bundles for {name}",
            "action": {"type": "explore", "topic": "accessories"},
        })

    return paths[:6]  # Max 6 exploration paths


@router.get("/{product_id}/stream")
async def stream_intelligence(product_id: str, request: Request):
    """
    SSE stream: Snap → Promise → Deliver phases.

    Events:
      snap    — Instant skeleton data
      promise — Research progress updates  
      deliver — Full enriched intelligence
      complete — Stream finished
      error   — Something went wrong
    """
    return StreamingResponse(
        _stream_intelligence(product_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{product_id}/quick")
async def quick_intelligence(product_id: str):
    """Non-streaming intelligence — returns cached or generates new."""
    from backend.jit_cache import get_cached_intelligence, cache_intelligence
    from backend.jit_agent import ProductSynthesizer
    from backend.server import _get_catalog

    cached = get_cached_intelligence(product_id)
    if cached:
        return cached

    catalog = _get_catalog()
    product = None
    for p in catalog.get("products", []):
        if p.get("id") == product_id:
            product = p
            break

    if not product:
        return JSONResponse(status_code=404, content={"error": f"Product '{product_id}' not found"})

    synthesizer = ProductSynthesizer()
    enriched = await synthesizer.synthesize(product)
    cache_intelligence(product_id, enriched)
    return enriched


# ═══════════════════════════════════════════════════════════════════════════
# EXPLORATION ACTIONS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/explore")
async def explore_action(body: dict):
    """
    Execute an exploration action — comparison, deep-dive, setup guide, etc.

    Body:
      product_id: str — The product being explored
      action_type: str — "compare" | "deep_dive" | "how_to" | "artist_spotlight" | "field_notes"
      target_id?: str — For comparisons, the other product ID
      topic?: str — For deep-dives, the topic to explore
    """
    from backend.llm import get_llm
    from backend.server import _get_catalog

    product_id = body.get("product_id")
    action_type = body.get("action_type")
    topic = body.get("topic", "")
    target_id = body.get("target_id")

    if not product_id or not action_type:
        return JSONResponse(status_code=400, content={"error": "Missing product_id or action_type"})

    catalog = _get_catalog()
    products_map = {p["id"]: p for p in catalog.get("products", [])}
    product = products_map.get(product_id)

    if not product:
        return JSONResponse(status_code=404, content={"error": f"Product '{product_id}' not found"})

    # Dispatch to the right exploration handler
    if action_type == "compare" and target_id:
        target = products_map.get(target_id)
        if not target:
            return JSONResponse(status_code=404, content={"error": f"Target product '{target_id}' not found"})
        from backend.jit_agent import ProductSynthesizer
        synthesizer = ProductSynthesizer()
        return await synthesizer.compare(product, target)

    # For all other exploration types, use the LLM directly
    llm = get_llm()
    name = product.get("name", "Unknown")
    brand = product.get("brand", "Unknown")

    prompts = {
        "setup": f"""Create a practical setup guide for the {brand} {name}.

Return a JSON object with this EXACT structure:
{{
  "title": "Setup Guide: {brand} {name}",
  "overview": "One sentence summary of what this guide covers",
  "sections": [
    {{
      "title": "Section Name (e.g. Unboxing Checklist)",
      "steps": [
        {{
          "step": 1,
          "title": "Short step title",
          "instruction": "Detailed instruction for this step",
          "tip": "Optional pro tip (only if genuinely useful)"
        }}
      ]
    }}
  ]
}}

Include these sections (3-5 steps each):
1. Unboxing & What's in the Box — verify all components
2. Physical Setup — placement, stands, positioning
3. Connections — cables, interfaces, signal chain for this specific model
4. First Power On & Calibration — initial settings, break-in, optimization
5. Common Scenarios — typical use cases (live, studio, home) with settings

Be specific to the {brand} {name}. Mention actual port names, button labels, and real settings.
If you include a tip, make it genuinely useful — not generic advice.""",

        "artists": f"""Who are the famous artists, producers, or sound engineers known to use the {brand} {name}?
Include: their name, what genre/context they use it in, any specific settings or configurations they're known for.
Only include VERIFIED, real artist associations. No guessing.""",

        "issues": f"""What are the known real-world issues, quirks, and maintenance tips for the {brand} {name}?
Include: firmware update recommendations, common failure points, environmental considerations,
things the manual doesn't tell you. Source from professional forums and verified user reports only.""",

        "accessories": f"""What are the essential and recommended accessories for the {brand} {name}?
Categorize as: ESSENTIAL (won't work properly without), RECOMMENDED (significantly improves experience), 
NICE-TO-HAVE (optional upgrades). Include specific model recommendations where possible.
Explain WHY each accessory matters — don't just list names.""",

        "deep_dive": f"""Provide an expert-level deep dive on "{topic}" for the {brand} {name}.
Explain the technology, how it compares to competitors, practical implications,
and insider tips that only experienced users would know.""",
    }

    prompt = prompts.get(topic or action_type, prompts.get("deep_dive", ""))
    if not prompt:
        return JSONResponse(status_code=400, content={"error": f"Unknown exploration type: {action_type}"})

    system = """You are a senior product specialist at a professional music equipment retailer.
You provide expert-level, practical advice based on real-world experience.
Never guess or fabricate. If you don't know something, say so.
Format your response as structured JSON with clear sections.
Be specific to the exact product model — don't give generic advice."""

    try:
        result, ok = await asyncio.to_thread(
            llm.call_json,
            "JITExplorer", prompt, system=system, cache_namespace="jit_explore")

        if not ok:
            # Fallback to text response
            text, ok2 = await asyncio.to_thread(
                llm.call,
                "JITExplorer", prompt, system=system, cache_namespace="jit_explore")
            if ok2:
                result = {"content": text, "format": "text"}
            else:
                logger.warning(
                    f"Exploration LLM failed for {product_id}/{action_type}: {result}")
                return JSONResponse(
                    status_code=503,
                    content={
                        "error": "Intelligence service temporarily unavailable",
                        "product_id": product_id,
                        "action_type": action_type,
                        "topic": topic,
                    },
                )
    except Exception as e:
        logger.error(f"Exploration error for {product_id}/{action_type}: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "error": "Intelligence service temporarily unavailable",
                "product_id": product_id,
                "action_type": action_type,
                "topic": topic,
            },
        )

    # Normalize result — LLM may return a list or other non-dict JSON
    if isinstance(result, list) and len(result) == 1 and isinstance(result[0], dict):
        result = result[0]
    elif not isinstance(result, dict):
        result = {"content": result, "format": "structured"}

    result["product_id"] = product_id
    result["action_type"] = action_type
    result["topic"] = topic
    return result
