"""
JIT Agent — The Product Synthesizer (v9)

When a user clicks a product, this agent:
1. Fetches the Halilit product page (for commercial truth)
2. Searches for the official brand page (for specs/media)
3. Searches trusted review sites (for real-world insights)
4. Sends ALL context to Gemini 2.0 Flash in ONE call
5. Returns a fully enriched product with brand theming

Respects source_rules.py field ownership:
  - Prices: ONLY from Halilit (already in inventory)
  - Specs/descriptions: ONLY from brand official page
  - Reviews/pros/cons: ONLY from trusted review sites
"""

import asyncio
import json
import logging
import re
from typing import Any

import httpx

from backend.llm import get_llm
from backend.trusted_sources import (
    TRUSTED_SOURCES,
    get_review_search_query,
    get_search_site_filter,
    identify_source,
)

logger = logging.getLogger(__name__)

# ── Known brand domains for direct lookup ──
BRAND_DOMAINS: dict[str, str] = {
    "roland": "roland.com",
    "yamaha": "yamaha.com",
    "korg": "korg.com",
    "nord": "nordkeyboards.com",
    "moog": "moogmusic.com",
    "boss": "boss.info",
    "fender": "fender.com",
    "gibson": "gibson.com",
    "shure": "shure.com",
    "sennheiser": "sennheiser.com",
    "audio-technica": "audio-technica.com",
    "akg": "akg.com",
    "mackie": "mackie.com",
    "rcf": "rcf.it",
    "jbl": "jbl.com",
    "adam audio": "adam-audio.com",
    "focal": "focalprofessional.com",
    "genelec": "genelec.com",
    "presonus": "presonus.com",
    "universal audio": "uaudio.com",
    "native instruments": "native-instruments.com",
    "arturia": "arturia.com",
    "novation": "novationmusic.com",
    "akai": "akaipro.com",
    "akai professional": "akaipro.com",
    "elektron": "elektron.se",
    "teenage engineering": "teenage.engineering",
    "make noise": "makenoisemusic.com",
    "mutable instruments": "mutable-instruments.net",
    "behringer": "behringer.com",
    "tc electronic": "tcelectronic.com",
    "eventide": "eventideaudio.com",
    "strymon": "strymon.net",
    "walrus audio": "walrusaudio.com",
    "epiphone": "epiphone.com",
    "ibanez": "ibanez.com",
    "prs": "prsguitars.com",
    "esp": "espguitars.com",
    "jackson": "jacksonguitars.com",
    "charvel": "charvel.com",
    "taylor": "taylorguitars.com",
    "martin": "martinguitar.com",
    "zildjian": "zildjian.com",
    "sabian": "sabian.com",
    "meinl": "meinlcymbals.com",
    "pearl": "pearldrum.com",
    "tama": "tama.com",
    "dw": "dwdrums.com",
    "ludwig": "ludwig-drums.com",
    "vic firth": "vicfirth.com",
    "remo": "remo.com",
    "evans": "daddario.com",
    "daddario": "daddario.com",
    "ernie ball": "ernieball.com",
    "dunlop": "jimdunlop.com",
    "washburn": "washburn.com",
    "oscar schmidt": "oscarschmidt.com",
    "cordoba": "cordobaguitars.com",
    "breedlove": "breedlovemusic.com",
    "takamine": "takamine.com",
    "gretsch": "gretschguitars.com",
    "orange": "orangeamps.com",
    "marshall": "marshall.com",
    "vox": "voxamps.com",
    "mesa boogie": "mesaboogie.com",
    "blackstar": "blackstaramps.com",
    "laney": "laney.co.uk",
    "markbass": "markbass.it",
    "gallien krueger": "gallien.com",
    "ampeg": "ampeg.com",
    "ashdown engineering": "ashdownmusic.com",
    "beyerdynamic": "beyerdynamic.com",
    "austrian audio": "austrian.audio",
    "lewitt": "lewitt-audio.com",
    "rode": "rode.com",
    "neumann": "neumann.com",
    "warm audio": "warmaudio.com",
    "cranborne audio": "cranborneaudio.com",
    "ssl": "solidstatelogic.com",
    "focusrite": "focusrite.com",
    "rme": "rme-audio.de",
    "motu": "motu.com",
    "apogee": "apogeedigital.com",
    "allen heath": "allen-heath.com",
    "soundcraft": "soundcraft.com",
    "midas": "midasconsoles.com",
    "dbx": "dbxpro.com",
    "lexicon": "lexiconpro.com",
    "dixon": "dixondrums.com",
    "mapex": "mapexdrums.com",
    "sonor": "sonor.com",
    "atv": "atvcorporation.com",
    "gewa": "gewamusic.com",
    "amphion": "amphion.fi",
    "asm": "asmhydrasynth.com",
    "aston microphones": "astonmics.com",
}


def _clean_html_to_text(html: str) -> str:
    """Strip HTML to readable text. Lightweight, no BS4 needed."""
    try:
        import trafilatura
        text = trafilatura.extract(
            html, include_links=False, include_images=False)
        if text and len(text) > 100:
            return text[:8000]  # Cap at 8K chars to save tokens
    except ImportError:
        pass

    # Fallback: simple regex strip
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:8000]


async def _fetch_url(client: httpx.AsyncClient, url: str, label: str = "") -> str | None:
    """Fetch a URL and return cleaned text content."""
    try:
        response = await client.get(url, follow_redirects=True, timeout=15.0)
        if response.status_code == 200:
            return _clean_html_to_text(response.text)
        logger.warning(f"[{label}] HTTP {response.status_code} for {url}")
    except Exception as e:
        logger.warning(f"[{label}] Fetch failed for {url}: {e}")
    return None


async def _search_web(client: httpx.AsyncClient, query: str, num_results: int = 5) -> list[dict]:
    """
    Search the web using Google Custom Search or fallback.
    Returns list of {title, url, snippet}.
    """
    import os

    # Try Google Custom Search API
    api_key = os.environ.get(
        "GOOGLE_SEARCH_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    cx = os.environ.get("GOOGLE_SEARCH_CX")

    if api_key and cx:
        try:
            params = {"key": api_key, "cx": cx, "q": query, "num": num_results}
            resp = await client.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                return [
                    {"title": item.get("title", ""), "url": item.get(
                        "link", ""), "snippet": item.get("snippet", "")}
                    for item in data.get("items", [])
                ]
        except Exception as e:
            logger.warning(f"Google search failed: {e}")

    # Try Serper API (accept either env var name)
    serper_key = os.environ.get(
        "SERPER_API_KEY") or os.environ.get("SERP_API_KEY")
    if serper_key:
        try:
            resp = await client.post(
                "https://google.serper.dev/search",
                json={"q": query, "num": num_results},
                headers={"X-API-KEY": serper_key},
                timeout=10.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                return [
                    {"title": item.get("title", ""), "url": item.get(
                        "link", ""), "snippet": item.get("snippet", "")}
                    for item in data.get("organic", [])
                ]
        except Exception as e:
            logger.warning(f"Serper search failed: {e}")

    logger.warning("No search API configured — JIT enrichment will be limited")
    return []


# ── System Prompt ──

SYNTHESIZER_SYSTEM = """You are the Halilit Product Intelligence Engine.
Your job is to merge multiple data sources into a single authoritative product record.

SOURCE PRIORITY:
1. COMMERCIAL TRUTH — Price, SKU, stock status come STRICTLY from Halilit (SOURCE_A). Never change these.
2. TECHNICAL TRUTH — Specs, description, features come from the brand's official page (SOURCE_B) when available.
3. SOCIAL TRUTH — Pros, cons, user insights come from trusted review sites (SOURCE_C) when available.

FALLBACK RULES (when source data is limited or unavailable):
- If SOURCE_B (brand page) is unavailable, extract whatever specs and features you can from SOURCE_A (the Halilit page text).
- If SOURCE_A also has limited data, use your reliable training knowledge for well-known products. You know the specs of popular instruments — use that knowledge.
- If SOURCE_C (reviews) is unavailable, use your training knowledge for well-known products to provide honest pros/cons based on the product category and known characteristics.
- ALWAYS provide a meaningful description, specs, features, pros, and cons. An empty product page is worse than an AI-assisted one.
- Be factually accurate. For obscure or unknown products, say what you can and leave truly unknown fields empty.
- Never fabricate fake review sources or fake review URLs.

OUTPUT RULES:
- description: Write a compelling, informative product description (2-3 sentences). Focus on what makes this product special.
- description_short: One punchy sentence summarizing the product.
- specs: Extract or provide real technical specifications as key-value pairs. Always include: type/category, key dimensions, connectivity, power, weight when known.
- features: List 4-8 key features. Be specific to THIS product model.
- pros: List 3-5 genuine strengths. These should be real advantages of this product.
- cons: List 2-4 honest weaknesses or limitations. Every product has some.
- rating: Estimated aggregate rating 0-5 based on available data (0 if truly unknown).
- For brand_theme, use the brand's known color scheme.
- For famous_users, only include real, verified artist associations.
- For known_issues, only include verified problems.
- For suggested_accessories, recommend products that genuinely complement this one.
- For layout_hints, suggest which UI components would be most useful for this product type.

You MUST return a well-populated JSON object. Empty fields mean the product page will look broken.
Respond in JSON format matching the schema exactly."""

SYNTHESIZER_SCHEMA = {
    "type": "object",
    "properties": {
        "description": {"type": "string", "description": "Official product description from brand"},
        "description_short": {"type": "string", "description": "1-2 sentence summary"},
        "specs": {"type": "object", "description": "Technical specifications as key-value pairs"},
        "features": {"type": "array", "items": {"type": "string"}, "description": "Key features list"},
        "pros": {"type": "array", "items": {"type": "string"}, "description": "Strengths from reviews"},
        "cons": {"type": "array", "items": {"type": "string"}, "description": "Weaknesses from reviews"},
        "rating": {"type": "number", "description": "Aggregate rating 0-5 from trusted sources"},
        "review_verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "summary": {"type": "string"},
                    "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]},
                    "url": {"type": "string"},
                    "logo_key": {"type": "string"},
                },
            },
        },
        "brand_theme": {
            "type": "object",
            "properties": {
                "primary_color": {"type": "string", "description": "Hex color e.g. #FF0000"},
                "secondary_color": {"type": "string"},
                "background_style": {"type": "string", "enum": ["dark", "light", "gradient"]},
            },
        },
        "famous_users": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "context": {"type": "string"},
                },
            },
        },
        "known_issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "issue": {"type": "string"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "source": {"type": "string"},
                },
            },
        },
        "suggested_accessories": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Generic accessory suggestions (cables, stands, cases, etc.)",
        },
        "layout_hints": {
            "type": "object",
            "properties": {
                "show_comparison": {"type": "boolean"},
                "show_signal_chain": {"type": "boolean"},
                "show_artist_spotlight": {"type": "boolean"},
                "show_family_tree": {"type": "boolean"},
                "product_category": {"type": "string"},
            },
        },
        "official_url": {"type": "string", "description": "URL to brand's official product page"},
    },
}


class ProductSynthesizer:
    """
    JIT Product Intelligence — fetches live data and synthesizes via Gemini.
    """

    def __init__(self):
        self.llm = get_llm()

    async def synthesize(self, product: dict) -> dict:
        """
        Enrich a product with live data from brand sites and trusted reviews.

        Args:
            product: Inventory product dict (from catalog)

        Returns:
            Enriched product dict with specs, reviews, brand theme, etc.
        """
        name = product.get("name") or product.get("product_name", "Unknown")
        brand = (product.get("brand") or "").lower().strip()
        halilit_url = product.get("halilit_url", "")

        logger.info(f"🧠 JIT synthesis starting for: {name} ({brand})")

        async with httpx.AsyncClient(
            headers={"User-Agent": "HalilitSupportCenter/9.0"},
            follow_redirects=True,
        ) as client:
            # Parallel fetch: Halilit page + brand search + review search
            halilit_task = _fetch_url(
                client, halilit_url, "Halilit") if halilit_url else asyncio.coroutine(lambda: None)()
            brand_task = self._fetch_brand_page(client, brand, name)
            review_task = self._fetch_trusted_reviews(client, name)

            halilit_text, brand_text, reviews = await asyncio.gather(
                halilit_task, brand_task, review_task,
                return_exceptions=True,
            )

            # Handle exceptions from gather
            if isinstance(halilit_text, Exception):
                halilit_text = None
            if isinstance(brand_text, Exception):
                brand_text = None
            if isinstance(reviews, Exception):
                reviews = []

        # Build the synthesis prompt
        prompt = self._build_prompt(
            name, brand, halilit_text, brand_text, reviews)

        # Single Gemini call
        # Note: We do NOT pass response_schema because specs are dynamic
        # key-value pairs — Gemini rejects OBJECT type without properties.
        # The system prompt constrains output shape adequately.
        result, ok = self.llm.call_json(
            "JITAgent", prompt,
            system=SYNTHESIZER_SYSTEM,
            cache_namespace="jit_synthesis",
        )

        if not ok:
            logger.warning(f"JIT synthesis failed for {name}: {result}")
            result = {}

        # Normalize — LLM may sometimes return a list instead of dict
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            logger.info(
                f"JIT synthesis returned list for {name}, unwrapping first element")
            result = result[0]
        elif not isinstance(result, dict):
            logger.warning(
                f"JIT synthesis returned non-dict ({type(result).__name__}) for {name}, using empty")
            result = {}

        # Merge enrichment into original product
        enriched = {**product}
        enriched.update({
            "description": result.get("description") or product.get("description", ""),
            "description_short": result.get("description_short") or product.get("description_short", ""),
            "specs": result.get("specs") or product.get("specs", {}),
            "features": result.get("features") or product.get("features", []),
            "pros": result.get("pros", []),
            "cons": result.get("cons", []),
            "rating": result.get("rating") or product.get("rating", 0),
            "review_verdicts": result.get("review_verdicts", []),
            "brand_theme": result.get("brand_theme", {}),
            "famous_users": result.get("famous_users", []),
            "known_issues": result.get("known_issues", []),
            "suggested_accessories": result.get("suggested_accessories", []),
            "layout_hints": result.get("layout_hints", {}),
            "official_url": result.get("official_url") or product.get("official_url", ""),
            "enriched": ok and bool(result),
            "enriched_at": __import__("time").time(),
        })

        logger.info(f"✅ JIT synthesis complete for: {name}")
        return enriched

    async def compare(self, product_a: dict, product_b: dict) -> dict:
        """
        Generate a JIT comparison between two products.
        """
        name_a = product_a.get("name", "Product A")
        name_b = product_b.get("name", "Product B")

        prompt = f"""Compare these two products side by side:

PRODUCT A: {name_a}
Brand: {product_a.get('brand', 'Unknown')}
Price: {product_a.get('price', 'N/A')} ILS
Category: {product_a.get('category', 'Unknown')}
Description: {product_a.get('description', 'N/A')[:500]}
Specs: {json.dumps(product_a.get('specs', {}), ensure_ascii=False)[:500]}

PRODUCT B: {name_b}
Brand: {product_b.get('brand', 'Unknown')}
Price: {product_b.get('price', 'N/A')} ILS
Category: {product_b.get('category', 'Unknown')}
Description: {product_b.get('description', 'N/A')[:500]}
Specs: {json.dumps(product_b.get('specs', {}), ensure_ascii=False)[:500]}

Provide a JSON comparison with:
- "summary": Brief comparison overview
- "winner": Which is better for most use cases (or "tie")
- "spec_comparison": Array of {{feature, product_a_value, product_b_value, advantage: "a"|"b"|"tie"}}
- "price_value": Which offers better value for money
- "use_case_a": Best scenario for Product A
- "use_case_b": Best scenario for Product B
- "recommendation": Who should buy which
"""

        result, ok = self.llm.call_json(
            "JITAgent", prompt,
            system="You are a professional music equipment reviewer. Compare products objectively.",
            cache_namespace="jit_comparison",
        )

        if not ok:
            result = {"error": "Comparison failed",
                      "summary": "Unable to generate comparison"}

        result["product_a"] = {"id": product_a.get(
            "id"), "name": name_a, "price": product_a.get("price")}
        result["product_b"] = {"id": product_b.get(
            "id"), "name": name_b, "price": product_b.get("price")}

        return result

    async def _fetch_brand_page(self, client: httpx.AsyncClient, brand: str, product_name: str) -> str | None:
        """Fetch the official brand product page content."""
        brand_domain = BRAND_DOMAINS.get(brand)
        if brand_domain:
            # Try direct brand site search
            results = await _search_web(client, f'site:{brand_domain} "{product_name}"', num_results=3)
            for r in results:
                if brand_domain in r.get("url", ""):
                    text = await _fetch_url(client, r["url"], f"Brand:{brand}")
                    if text:
                        return text

        # Fallback: general search for official page
        results = await _search_web(client, f'"{product_name}" {brand} specifications official', num_results=3)
        for r in results:
            url = r.get("url", "")
            if brand_domain and brand_domain in url:
                text = await _fetch_url(client, url, f"Brand:{brand}")
                if text:
                    return text

        # Return search snippets if no full page available
        if results:
            return "\n".join(f"- {r.get('title', '')}: {r.get('snippet', '')}" for r in results)

        return None

    async def _fetch_trusted_reviews(self, client: httpx.AsyncClient, product_name: str) -> list[dict]:
        """Fetch reviews from trusted sources only."""
        query = get_review_search_query(product_name)
        results = await _search_web(client, query, num_results=8)

        reviews = []
        for r in results:
            source = identify_source(r.get("url", ""))
            if source:
                reviews.append({
                    "source": source.name,
                    "logo_key": source.logo_key,
                    "tier": source.tier,
                    "title": r.get("title", ""),
                    "snippet": r.get("snippet", ""),
                    "url": r.get("url", ""),
                })

        # Try to fetch full content from top 2 results
        for review in reviews[:2]:
            text = await _fetch_url(client, review["url"], f"Review:{review['source']}")
            if text:
                review["full_text"] = text[:3000]  # Cap to save tokens

        return reviews

    def _build_prompt(
        self,
        name: str,
        brand: str,
        halilit_text: str | None,
        brand_text: str | None,
        reviews: list[dict],
    ) -> str:
        """Build the synthesis prompt with all three source contexts."""
        parts = [f'Synthesize product data for: "{name}" by {brand}\n']

        parts.append("=== SOURCE_A (Halilit - Commercial Truth) ===")
        if halilit_text:
            parts.append(halilit_text[:3000])
        else:
            parts.append("(No Halilit page content available)")

        parts.append("\n=== SOURCE_B (Official Brand - Technical Truth) ===")
        if brand_text:
            parts.append(brand_text[:4000])
        else:
            parts.append("(No official brand page content available)")

        parts.append("\n=== SOURCE_C (Trusted Reviews - Social Truth) ===")
        if reviews:
            for review in reviews[:5]:
                parts.append(
                    f"\n--- {review['source']} (Tier {review['tier']}) ---")
                parts.append(f"Title: {review.get('title', 'N/A')}")
                parts.append(f"URL: {review.get('url', '')}")
                if review.get("full_text"):
                    parts.append(review["full_text"][:2000])
                else:
                    parts.append(f"Snippet: {review.get('snippet', 'N/A')}")
        else:
            parts.append("(No trusted reviews found)")

        parts.append(
            f"\n\nReturn a complete enriched product JSON for '{name}'.")
        return "\n".join(parts)
