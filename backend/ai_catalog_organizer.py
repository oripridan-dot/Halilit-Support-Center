"""
AI-Powered Catalog Organizer — Professional Data Organization

Uses Gemini 2.0 Flash to intelligently:
- Group products into logical families (variants, series, product lines)
- Discover relationships (accessories, alternatives, bundles, compatibility)
- Build hierarchical categories with semantic understanding
- Infer product metadata (series, generation, product line)
- Create professional search indexes with synonyms and related terms

This is a drop-in replacement for catalog_organizer.py that produces
much more sophisticated organization than rule-based heuristics.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from backend.catalog_organizer_schema import (
    build_categories_from_products,
    build_search_index,
)
from backend.project_config import FRONTEND_PUBLIC_DATA

logger = logging.getLogger("AICatalogOrganizer")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
AI_ORGANIZER_ENABLED = os.getenv("AI_ORGANIZER_ENABLED", "true").lower() == "true"
AI_ORGANIZER_TIMEOUT = float(os.getenv("AI_ORGANIZER_TIMEOUT", "180.0"))
AI_MAX_PRODUCTS = int(os.getenv("AI_ORGANIZER_MAX_PRODUCTS", "300"))


def _slug(s: str) -> str:
    """Convert string to URL-friendly slug."""
    if not s:
        return "unknown"
    return "".join(c if c.isalnum() or c in " -" else " " for c in s).strip().replace(" ", "-").lower().strip("-")


def _prepare_products_for_ai(products: List[Dict[str, Any]], max_count: int = AI_MAX_PRODUCTS) -> List[Dict[str, Any]]:
    """Extract key fields for AI processing."""
    simplified = []
    for p in products[:max_count]:
        simplified.append({
            "halilit_id": p.get("halilit_id") or p.get("id", ""),
            "product_name": p.get("product_name") or p.get("name", ""),
            "brand": p.get("brand", ""),
            "category": (p.get("taxonomy") or {}).get("canonical_category", ""),
            "price": p.get("price"),
            "model_number": p.get("model_number") or "",
            "series": p.get("series") or "",
        })
    return simplified


async def _organize_via_ai(brand_slug: str, brand_name: str, products: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Use Gemini AI to intelligently organize products into families, relationships, and categories."""
    if not AI_ORGANIZER_ENABLED or not GEMINI_API_KEY or not genai:
        return None
    
    if len(products) > AI_MAX_PRODUCTS:
        logger.warning("AI organizer: too many products (%d > %d), skipping", len(products), AI_MAX_PRODUCTS)
        return None
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
    except Exception as e:
        logger.warning("AI organizer: failed to initialize Gemini: %s", e)
        return None
    
    # Prepare simplified product data for AI
    simplified_products = _prepare_products_for_ai(products)
    
    # Build comprehensive prompt
    prompt = f"""You are a professional product catalog organizer for a music equipment retailer.

Your task: Analyze {len(simplified_products)} products from the brand "{brand_name}" and organize them into a professional structure.

**Input Products:**
{json.dumps(simplified_products, indent=2, ensure_ascii=False)}

**Your Output (JSON only, no markdown):**
Return a JSON object with this exact structure:

{{
  "brand_identity": {{
    "id": "{brand_slug}",
    "name": "{brand_name}",
    "slug": "{brand_slug}",
    "logo_url": null,
    "website": null,
    "description": null
  }},
  "families": [
    {{
      "family_id": "fam_{brand_slug}_example-series",
      "family_name": "Example Series Name",
      "series": "series-name",
      "brand": "{brand_name}",
      "variant_ids": ["halilit-123", "halilit-456"],
      "is_accessory_family": false,
      "generation": 4,
      "product_line": "Professional Series"
    }}
  ],
  "relationships": [
    {{
      "source_id": "halilit-123",
      "target_id": "halilit-789",
      "relationship_type": "accessory_for"
    }}
  ],
  "categories": [
    {{
      "id": "keyboards-synthesizers",
      "label": "Keyboards & Synthesizers",
      "product_ids": ["halilit-123", "halilit-456"]
    }}
  ],
  "products": [... same products as input, optionally reordered ...],
  "search_index": [
    {{
      "id": "halilit-123",
      "t": "Product Name",
      "s": "Category Label",
      "b": "{brand_slug}"
    }}
  ],
  "meta": {{
    "total_products": {len(products)},
    "total_categories": 0,
    "organized_at": "{datetime.now(timezone.utc).isoformat()}",
    "source": "ai_gemini"
  }}
}}

**Rules:**
1. **Families:** Group products that are variants of the same model/series:
   - Same base model name (e.g., "TD-27KV", "TD-27K2" → "TD-27" family)
   - Same series (e.g., "Stage 4 88", "Stage 4 73" → "Stage 4" family)
   - Same product line (e.g., "Professional", "Entry", "Flagship")
   - Mark `is_accessory_family: true` only if ALL variants are clearly accessories (bags, cases, stands, pedals, covers)

2. **Relationships:** Infer high-confidence relationships:
   - `accessory_for`: Bags, cases, stands, pedals that mention a specific model
   - `alternative_to`: Products in same category/price range that serve similar purpose
   - `bundle_with`: Products commonly sold together (check names for "bundle", "kit", "combo")
   - `compatible_with`: Products that work together (e.g., interface + microphone)
   - `variant_of`: Products that are clearly variants (already in families, but can link across families)

3. **Categories:** Use the `category` field from each product. Group product IDs by category. Use slug for `id` (lowercase, hyphens).

4. **Search Index:** One entry per product: `id` = halilit_id, `t` = short product name, `s` = category label, `b` = brand_slug.

5. **Products:** Return the same array (preserve all fields). Optionally reorder by category or family.

**Constraints:**
- Output MUST be valid JSON only. No markdown, no explanation.
- Only include relationships where confidence is high (clear from names/SKUs/categories).
- All `variant_ids`, `product_ids`, `source_id`, `target_id` MUST be valid halilit_id values from input.
- Be conservative: prefer fewer, high-quality families/relationships over many speculative ones.

**Output JSON:**
"""
    
    try:
        logger.info("AI organizer: Analyzing %d products for %s...", len(products), brand_name)
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,  # Lower temperature for more consistent, factual output
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            },
        )
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        result = json.loads(response_text)
        
        # Validate structure
        if not isinstance(result, dict):
            logger.warning("AI organizer: Response is not a dict")
            return None
        
        if "products" not in result or "brand_identity" not in result:
            logger.warning("AI organizer: Missing required fields in response")
            return None
        
        # Ensure meta field exists
        if "meta" not in result:
            result["meta"] = {
                "total_products": len(result.get("products", [])),
                "total_categories": len(result.get("categories", [])),
                "organized_at": datetime.now(timezone.utc).isoformat(),
                "source": "ai_gemini",
            }
        
        logger.info(
            "AI organizer: Successfully organized %s (%d products, %d families, %d relationships)",
            brand_name,
            len(result.get("products", [])),
            len(result.get("families", [])),
            len(result.get("relationships", [])),
        )
        
        return result
        
    except json.JSONDecodeError as e:
        logger.warning("AI organizer: Failed to parse JSON response: %s | Response: %s", e, response_text[:200])
        return None
    except Exception as e:
        logger.warning("AI organizer: Failed to organize %s: %s", brand_name, e)
        return None


def organize_brand_sync(brand_slug: str, brand_name: str, products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build consolidated catalog for one brand using AI when enabled, otherwise Python fallback.
    Synchronous wrapper for scripts.
    """
    import asyncio
    return asyncio.run(organize_brand(brand_slug, brand_name, products))


async def organize_brand(brand_slug: str, brand_name: str, products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build consolidated catalog for one brand. Prefer AI; fallback to Python.
    """
    if not products:
        from backend.catalog_organizer import _fallback_organize
        return _fallback_organize(brand_slug, brand_name, [])
    
    # Try AI organizer first
    consolidated = await _organize_via_ai(brand_slug, brand_name, products)
    if consolidated:
        return consolidated
    
    # Fallback to Python organizer
    from backend.catalog_organizer import _fallback_organize
    logger.info("AI organizer: Using Python fallback for %s", brand_name)
    return _fallback_organize(brand_slug, brand_name, products)


def write_consolidated_catalog(brand_slug: str, consolidated: Dict[str, Any], out_dir: Path | None = None) -> Path:
    """Write consolidated catalog to frontend data dir. Returns path written."""
    out_dir = out_dir or FRONTEND_PUBLIC_DATA
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = (consolidated.get("brand_identity") or {}).get("id") or _slug(brand_slug)
    path = out_dir / f"{slug}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(consolidated, f, indent=2, ensure_ascii=False)
    logger.info("Wrote consolidated catalog: %s (%s products)", path.name, len(consolidated.get("products", [])))
    return path
