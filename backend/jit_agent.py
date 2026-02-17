"""
JIT AGENT — Live Product Intelligence Engine

When a user clicks a product, this agent:
  1. Loads inventory data instantly (snap phase)
  2. Reads the Halilit product page for full details
  3. Searches official brand pages for specs
  4. Consults the Golden Circle of trusted review sites
  5. Streams typed SSE events to the frontend cockpit

Uses Gemini 2.0 Flash for real-time research and reasoning.
Cache: First hit ~5s, subsequent ~0ms (7-day TTL file cache).

Source Rules remain LAW:
  - Commercial truth (Halilit) for prices
  - Official (brand) for specs
  - Contextual (3+ trusted reviews) for opinions
  - NEVER fabricate data
"""

import asyncio
import json
import logging
import os
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Optional

from backend.trusted_sources import (
    build_site_restricted_query,
    get_source_info,
    TRUSTED_SOURCES,
)

logger = logging.getLogger("JITAgent")

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

CACHE_DIR = Path(__file__).parent / "data" / "jit_cache"
CACHE_TTL_SECONDS = 7 * 24 * 3600  # 7 days
GEMINI_MODEL = "gemini-2.0-flash"


def _get_cache_path(product_id: str) -> Path:
    """Get file-based cache path for a product."""
    safe_id = hashlib.md5(product_id.encode()).hexdigest()[:16]
    return CACHE_DIR / f"{safe_id}.json"


def _read_cache(product_id: str) -> Optional[Dict]:
    """Read cached intelligence for a product (returns None if expired or missing)."""
    path = _get_cache_path(product_id)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        cached_at = data.get("_cached_at", 0)
        if time.time() - cached_at > CACHE_TTL_SECONDS:
            return None
        return data
    except Exception:
        return None


def _write_cache(product_id: str, data: Dict) -> None:
    """Write intelligence to file cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _get_cache_path(product_id)
    data["_cached_at"] = time.time()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def _load_inventory_product(product_id: str) -> Optional[Dict]:
    """Load product from inventory.json by ID."""
    from backend.project_config import FRONTEND_PUBLIC_DATA
    inv_path = Path(FRONTEND_PUBLIC_DATA) / "inventory.json"
    if not inv_path.exists():
        return None
    try:
        inventory = json.loads(inv_path.read_text())
        for p in inventory.get("products", []):
            if p.get("id") == product_id:
                return p
    except Exception as e:
        logger.warning(f"Failed to read inventory: {e}")
    return None


# ═══════════════════════════════════════════════════════════════════════════
# TOOL FUNCTIONS (called by the Gemini agent)
# ═══════════════════════════════════════════════════════════════════════════

def read_halilit_page(url: str) -> Dict[str, Any]:
    """Fetch and parse a Halilit product page for full details."""
    try:
        from backend.ingestion.halilit_page_scraper import HalilitPageScraper
        scraper = HalilitPageScraper()
        data = scraper.scrape_product_page(url)
        if data:
            # Extract features and specs from the scraper's {name, value} dicts
            raw_features = data.get("features", [])
            features: list[str] = []
            specs: Dict[str, Any] = {}
            for f in raw_features:
                if isinstance(f, dict):
                    name = f.get("name", "").strip()
                    value = f.get("value", "").strip()
                    if name and value:
                        specs[name] = value
                    elif value:
                        features.append(value)
                    elif name:
                        features.append(name)
                elif isinstance(f, str):
                    features.append(f)

            return {
                "source": "halilit",
                "name": data.get("product_name", ""),
                "brand": data.get("brand", ""),
                "price": data.get("price_il", 0),
                "description": data.get("description", ""),
                "features": features,
                "specs": specs,
                "images": [img.get("url") for img in data.get("official_images", []) if img.get("url")],
                "faq": data.get("faq", []),
            }
    except Exception as e:
        logger.warning(f"Failed to read Halilit page {url}: {e}")
    return {"source": "halilit", "error": "Could not read page"}


def read_brand_page(brand: str, product_name: str) -> Dict[str, Any]:
    """
    Search and read the official brand page for a product.
    Attempts to find the product on the brand's official website.

    NOTE: In production, this would use Google Custom Search API
    to find the exact product page on the brand domain. For now,
    we construct a likely URL and attempt to fetch it.
    """
    import requests

    # Common brand domain patterns
    brand_domains = {
        "roland": "roland.com",
        "yamaha": "yamaha.com",
        "fender": "fender.com",
        "gibson": "gibson.com",
        "boss": "boss.info",
        "korg": "korg.com",
        "casio": "casio.com",
        "shure": "shure.com",
        "sennheiser": "sennheiser.com",
        "audio-technica": "audio-technica.com",
        "jbl": "jbl.com",
        "harman": "harman.com",
        "pioneer": "pioneerdj.com",
        "native instruments": "native-instruments.com",
        "arturia": "arturia.com",
        "focusrite": "focusrite.com",
        "universal audio": "uaudio.com",
        "akai": "akaipro.com",
        "novation": "novationmusic.com",
        "moog": "moogmusic.com",
        "nord": "nordkeyboards.com",
        "kawai": "kawai.co.jp",
        "marshall": "marshall.com",
        "orange": "orangeamps.com",
        "vox": "voxamps.com",
        "line 6": "line6.com",
        "tc electronic": "tcelectronic.com",
        "behringer": "behringer.com",
        "mackie": "mackie.com",
        "presonus": "presonus.com",
    }

    brand_lower = brand.lower().strip()
    domain = brand_domains.get(brand_lower, f"{brand_lower.replace(' ', '')}.com")

    # Build a search query for the brand's official page
    search_query = f"{product_name} site:{domain}"

    result = {
        "source": "brand_official",
        "brand": brand,
        "domain": domain,
        "search_query": search_query,
    }

    # Attempt to reach the brand's website
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(
            f"https://{domain}/",
            headers=headers,
            timeout=8,
            allow_redirects=True,
        )
        if resp.status_code == 200:
            result["brand_site_reachable"] = True
            result["note"] = f"Brand site {domain} is reachable. Search query prepared."
        else:
            result["brand_site_reachable"] = False
            result["note"] = f"Brand site returned status {resp.status_code}"
    except Exception as e:
        result["brand_site_reachable"] = False
        result["note"] = f"Could not reach brand site: {str(e)[:100]}"

    return result


def verify_integrity(official_url: str, our_specs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify that our stored specs match the official manufacturer page.
    Fetches official_url, checks if key spec values appear in page text.
    Used to stamp data_trust.specs_source = "official_verified" when matched.

    Returns:
        specs_verified: True if a reasonable number of spec values appear on the page
        matched: list of spec keys that were found
        missing: list of spec keys not found (or empty if page not fetched)
    """
    import re
    import requests

    result: Dict[str, Any] = {
        "specs_verified": False,
        "matched": [],
        "missing": [],
        "note": "",
    }
    if not official_url or not our_specs:
        result["note"] = "No official URL or specs to verify"
        return result

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; HalilitSupport/1.0; +https://halilit.com)",
        }
        resp = requests.get(official_url, headers=headers, timeout=10, allow_redirects=True)
        if resp.status_code != 200:
            result["note"] = f"Official page returned {resp.status_code}"
            return result
        text = (resp.text or "").lower()
    except Exception as e:
        result["note"] = f"Could not fetch official page: {e}"
        return result

    # Skip noisy keys
    skip_keys = {"sku", "note", "extracted_name", "model", "name"}
    matched = []
    missing = []
    for key, value in our_specs.items():
        if key.lower() in skip_keys or value is None:
            continue
        val_str = str(value).strip().lower()
        if len(val_str) < 2:
            continue
        # Normalize for match: digits and units (e.g. "128" or "128 voices")
        if val_str in text or re.search(re.escape(val_str[:20]), text):
            matched.append(key)
        else:
            missing.append(key)

    total = len(matched) + len(missing)
    result["matched"] = matched
    result["missing"] = missing
    result["specs_verified"] = total > 0 and len(matched) / total >= 0.5
    result["note"] = "Official page verified" if result["specs_verified"] else "Partial or no match on official page"
    return result


def _fetch_official_data(brand: str, product_name: str) -> Dict[str, Any]:
    """
    Fetch candidate official product page: find URL then extract og:image, description, specs.
    Used by JIT parallel swarm. Returns dict with url, image_url, description, specs.
    """
    try:
        from backend.ingestion.official_scraper import find_official_product_url, fetch_official_page
        url = find_official_product_url(brand, product_name)
        if not url:
            return {}
        data = fetch_official_page(url)
        if data.get("url"):
            return data
    except Exception as e:
        logger.debug("_fetch_official_data: %s", e)
    return {}


def search_trusted_reviews(product_name: str) -> Dict[str, Any]:
    """
    Build a site-restricted search query for the Golden Circle sources.
    Returns the query and source info for the frontend to display.

    NOTE: In production, this would call Google Custom Search API.
    For now, returns the structured query and source metadata
    so the frontend can display which sources were consulted.
    """
    query = build_site_restricted_query(product_name)
    sources = []
    for s in TRUSTED_SOURCES[:6]:
        sources.append({
            "source": s["name"],
            "domain": s["domain"],
            "logo": s["logo"],
            "summary": f"{s['specialty']} — search prepared for {product_name}",
            "sentiment": "neutral",
        })
    return {
        "query": query,
        "sources": sources,
        "note": "Search query prepared for Golden Circle sources",
    }


# ═══════════════════════════════════════════════════════════════════════════
# SSE EVENT HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _sse_event(event: str, data: Any) -> str:
    """Format an SSE event."""
    json_str = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {json_str}\n\n"


# ═══════════════════════════════════════════════════════════════════════════
# MAIN JIT STREAM
# ═══════════════════════════════════════════════════════════════════════════

async def stream_product_intelligence(product_id: str) -> AsyncGenerator[str, None]:
    """
    Main entry point: streams JIT intelligence for a product as SSE events.

    Event types:
      status         — Phase updates ("Reading Halilit page...")
      snap           — Instant inventory data (name, price, brand)
      official_specs — Specs from brand/Halilit page
      trusted_reviews — Golden Circle source metadata
      verdict        — AI summary with pros/cons
      field_notes    — Pro tips and warnings
      exploration    — Suggested next actions
      complete       — Done signal with cache status
    """
    logger.info(f"JIT stream starting for: {product_id}")

    # ── Check cache first ──
    cached = _read_cache(product_id)
    if cached:
        logger.info(f"Cache HIT for {product_id}")
        yield _sse_event("status", {"phase": "cached", "message": "Loading from cache..."})

        # Replay cached events
        if "snap" in cached:
            yield _sse_event("snap", cached["snap"])
        if "official_specs" in cached:
            yield _sse_event("official_specs", cached["official_specs"])
        if "trusted_reviews" in cached:
            yield _sse_event("trusted_reviews", cached["trusted_reviews"])
        if "verdict" in cached:
            yield _sse_event("verdict", cached["verdict"])
        if "field_notes" in cached:
            yield _sse_event("field_notes", cached["field_notes"])
        if "exploration" in cached:
            yield _sse_event("exploration", cached["exploration"])
        if "verification" in cached:
            yield _sse_event("verification", cached["verification"])
        if "visual_intel" in cached:
            yield _sse_event("visual_intel", cached["visual_intel"])

        yield _sse_event("complete", {"cached": True, "ttl": CACHE_TTL_SECONDS})
        return

    # ── Phase 1: SNAP — Instant inventory data ──
    yield _sse_event("status", {"phase": "snap", "message": "Loading inventory..."})

    inv_product = _load_inventory_product(product_id)
    snap_data = {}
    if inv_product:
        snap_data = {
            "name": inv_product.get("name", ""),
            "brand": inv_product.get("brand", ""),
            "price": inv_product.get("price", 0),
            "price_eilat": inv_product.get("price_eilat", 0),
            "thumbnail": inv_product.get("thumbnail") or inv_product.get("image_url", ""),
            "halilit_url": inv_product.get("halilit_url", ""),
            "category_hint": inv_product.get("category_hint", "") or inv_product.get("spectrum_id", ""),
        }
        yield _sse_event("snap", snap_data)

    cache_result = {"snap": snap_data}
    product_name = snap_data.get("name", "") or product_id
    brand_name = snap_data.get("brand", "")
    halilit_url = snap_data.get("halilit_url", "")

    # ── Phase 2: PARALLEL SWARM — Halilit + Official fetch ──
    yield _sse_event("status", {"phase": "intel", "message": "Fetching Halilit & official data in parallel..."})
    loop = asyncio.get_event_loop()
    halilit_data = {}
    official_candidate = {}

    async def _run_halilit():
        if not halilit_url:
            return {}
        return await loop.run_in_executor(None, lambda: read_halilit_page(halilit_url))

    async def _run_official():
        if not brand_name:
            return {}
        return await loop.run_in_executor(None, lambda: _fetch_official_data(brand_name, product_name))

    halilit_data, official_candidate = await asyncio.gather(_run_halilit(), _run_official())

    # ── Phase 2b: THE AUDITOR — Visual verification (compare commercial vs official image) ──
    combined_data = dict(halilit_data) if halilit_data else {}
    identity_verified = False
    try:
        from backend.ingestion.visual_validator import get_visual_validator
        validator = get_visual_validator()
        halilit_image_url = (halilit_data.get("images") or [None])[0] if halilit_data else None
        if not halilit_image_url:
            halilit_image_url = inv_product.get("image_url") or snap_data.get("thumbnail") or ""
        official_image_url = (official_candidate or {}).get("image_url") or ""

        if halilit_image_url and official_image_url:
            bytes_halilit, _ = await validator.fetch_image(halilit_image_url)
            bytes_official, _ = await validator.fetch_image(official_image_url)
            if bytes_halilit and bytes_official:
                comparison = await loop.run_in_executor(
                    None, lambda: validator.compare_images(bytes_halilit, bytes_official)
                )
                similarity = comparison.get("similarity", 0)
                identity_verified = similarity > 0.85
                if identity_verified:
                    yield _sse_event("status", {
                        "phase": "auditor",
                        "message": f"Identity verified via image match (confidence: {similarity:.0%})",
                    })
                    combined_data["description"] = (
                        (official_candidate.get("description") or "").strip()
                        + "\n\n---\n\n"
                        + (halilit_data.get("description") or "").strip()
                    ).strip()
                    combined_data["specs"] = {**(halilit_data.get("specs") or {}), **(official_candidate.get("specs") or {})}
                    combined_data["official_url"] = official_candidate.get("url", "")
                else:
                    yield _sse_event("status", {
                        "phase": "auditor",
                        "message": "Official match uncertain. Using commercial data.",
                    })
    except Exception as e:
        logger.warning("Auditor step failed: %s", e)

    # Emit official_specs from combined data (for frontend)
    # When identity not verified (commercial vs official image mismatch), do not persist official URL/images
    if combined_data and not combined_data.get("error"):
        official_specs = {
            "specs": combined_data.get("specs", {}),
            "features": combined_data.get("features", []),
            "description": combined_data.get("description", ""),
            "images": combined_data.get("images", []) if identity_verified else [],
            "official_url": combined_data.get("official_url", "") if identity_verified else "",
            "identity_verified": identity_verified,
        }
        yield _sse_event("official_specs", official_specs)
        cache_result["official_specs"] = official_specs

    # ── Phase 2c: VERIFY INTEGRITY — Compare specs to official page text ──
    verification_result = None
    official_url = (inv_product or {}).get("official_url", "") or (official_candidate or {}).get("url", "")
    our_specs = combined_data.get("specs", {})
    if official_url and our_specs:
        try:
            verification_result = verify_integrity(official_url, our_specs)
            yield _sse_event("verification", verification_result)
            cache_result["verification"] = verification_result
        except Exception as e:
            logger.warning(f"verify_integrity failed: {e}")

    # ── Phase 2d: VISUAL INTELLIGENCE — signal_chain + cheat_sheet ──
    visual_intel = _generate_visual_intelligence(combined_data, product_name, brand_name)
    if visual_intel:
        yield _sse_event("visual_intel", visual_intel)
        cache_result["visual_intel"] = visual_intel

    # ── Phase 3: WISDOM — Trusted reviews + AI Reasoning ──
    yield _sse_event("status", {"phase": "wisdom", "message": f"Consulting trusted sources for {product_name}..."})

    # Search trusted review sources
    trusted_data = search_trusted_reviews(product_name)
    trusted_reviews = trusted_data.get("sources", [])
    if trusted_reviews:
        yield _sse_event("trusted_reviews", {"reviews": trusted_reviews})
        cache_result["trusted_reviews"] = {"reviews": trusted_reviews}

    # Try to use Gemini for intelligent analysis (use combined_data so merged official specs are included)
    verdict_data = None
    field_notes_data = None
    try:
        verdict_data, field_notes_data = await _generate_ai_intelligence(
            product_name=product_name,
            brand_name=brand_name,
            halilit_data=combined_data,
        )
    except Exception as e:
        logger.warning(f"AI intelligence failed: {e}")

    if verdict_data:
        yield _sse_event("verdict", verdict_data)
        cache_result["verdict"] = verdict_data

    if field_notes_data:
        yield _sse_event("field_notes", field_notes_data)
        cache_result["field_notes"] = field_notes_data

    # ── Phase 4: EXPLORATION — Suggest next actions ──
    exploration_data = _generate_exploration_paths(product_name, brand_name)
    yield _sse_event("exploration", exploration_data)
    cache_result["exploration"] = exploration_data

    # ── Cache & Complete ──
    _write_cache(product_id, cache_result)
    yield _sse_event("complete", {"cached": False, "ttl": CACHE_TTL_SECONDS})
    logger.info(f"JIT stream complete for: {product_id}")


def _generate_visual_intelligence(
    combined_data: Dict[str, Any],
    product_name: str,
    brand_name: str,
) -> Dict[str, Any]:
    """
    Build signal_chain and cheat_sheet from combined product data for the Visual Intelligence UI.
    """
    signal_chain = []
    features = combined_data.get("features", [])
    specs = combined_data.get("specs", {})
    if isinstance(features, list) and features:
        for i, f in enumerate(features[:6]):
            signal_chain.append({"step": i + 1, "label": f if isinstance(f, str) else str(f), "type": "feature"})
    if not signal_chain and specs:
        for i, (k, v) in enumerate(list(specs.items())[:5]):
            signal_chain.append({"step": i + 1, "label": f"{k}: {v}", "type": "spec"})
    if not signal_chain:
        signal_chain = [{"step": 1, "label": product_name or "Product", "type": "node"}]

    bullets = []
    for f in (features or [])[:8]:
        if isinstance(f, str) and f.strip():
            bullets.append(f.strip())
    for k, v in list(specs.items())[:5]:
        if k and str(v).strip():
            bullets.append(f"{k}: {v}")

    return {
        "signal_chain": signal_chain,
        "cheat_sheet": {
            "title": f"{brand_name} {product_name}" if brand_name else product_name,
            "bullets": bullets[:12],
        },
    }


async def _generate_ai_intelligence(
    product_name: str,
    brand_name: str,
    halilit_data: Dict,
) -> tuple:
    """
    Use Gemini to generate verdict and field notes from available data.
    Returns (verdict_data, field_notes_data) or (None, None) on failure.
    """
    from backend.env_secrets import get_gemini_api_key
    api_key = get_gemini_api_key()
    if not api_key:
        logger.info("No Gemini API key — skipping AI analysis (set GEMINI_API_KEY in .env from aistudio.google.com/app/apikey)")
        return None, None

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        # Build context from available data
        description = halilit_data.get("description", "")
        features = halilit_data.get("features", [])
        specs = halilit_data.get("specs", {})

        context_parts = [f"Product: {product_name}", f"Brand: {brand_name}"]
        if description:
            context_parts.append(f"Description: {description[:500]}")
        if features:
            context_parts.append(f"Features: {', '.join(features[:8])}")
        if specs:
            specs_str = ", ".join(f"{k}: {v}" for k, v in list(specs.items())[:10])
            context_parts.append(f"Specs: {specs_str}")

        context = "\n".join(context_parts)

        prompt = f"""You are an expert music equipment advisor for Halilit, Israel's leading music instrument distributor.

Based on the following product data, provide:
1. A concise verdict (2-3 sentences) summarizing who this product is for and why it matters
2. Up to 3 pros (short phrases)
3. Up to 2 cons or considerations (short phrases)
4. Up to 2 pro tips for users considering this product
5. Up to 1 warning about common issues or things to watch out for

IMPORTANT RULES:
- ONLY use facts from the provided data. NEVER fabricate specs, reviews, or claims.
- If data is limited, say so honestly.
- Be practical and professional — this is for music store employees.

Product Data:
{context}

Respond in this exact JSON format:
{{
  "verdict": {{
    "text": "...",
    "badge": "Recommended" or "Professional Choice" or "Best Value" or "Specialist" or null,
    "pros": ["...", "..."],
    "cons": ["...", "..."]
  }},
  "field_notes": {{
    "tips": ["...", "..."],
    "warnings": ["..."]
  }}
}}"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        # Parse response
        text = response.text.strip()
        # Extract JSON from potential markdown code blocks
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        result = json.loads(text)

        verdict_data = result.get("verdict")
        field_notes_data = result.get("field_notes")

        if verdict_data:
            verdict_data["source"] = "AI Analysis (Gemini)"

        return verdict_data, field_notes_data

    except Exception as e:
        logger.warning(f"Gemini AI generation failed: {e}")
        return None, None


def _generate_exploration_paths(product_name: str, brand_name: str) -> Dict:
    """Generate exploration path suggestions."""
    paths = []

    if brand_name:
        paths.append({
            "type": "comparison",
            "label": f"Compare {brand_name} alternatives",
            "target": brand_name,
        })

    paths.append({
        "type": "deep_dive",
        "label": f"Deep dive: {product_name}",
        "target": product_name,
    })

    paths.append({
        "type": "compatibility",
        "label": "Check compatibility",
        "target": product_name,
    })

    paths.append({
        "type": "how_to",
        "label": "Setup guide",
        "target": product_name,
    })

    return {"paths": paths[:4]}
