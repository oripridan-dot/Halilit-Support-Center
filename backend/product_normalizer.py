"""
Product Normalizer — Single source of truth for product shape.

ALL products served to the frontend pass through normalize_product().
This guarantees a clean, flat, predictable shape so the frontend
never needs fallback chains for basic fields (price, image, name).

Design principles:
  - One function, one shape. No duplicates anywhere in the codebase.
  - Fail-fast: products without price OR image are dropped (quality gates).
  - The output dict is the API contract with the frontend.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Image extraction — single ordered cascade
# ---------------------------------------------------------------------------

_PLACEHOLDER_MARKERS = ("/assets/images/placeholder",
                        "brand.com", "example.com")


def _is_valid_image(url: Any) -> bool:
    """Return True for a non-empty string that isn't a known placeholder."""
    if not url or not isinstance(url, str):
        return False
    return not any(m in url for m in _PLACEHOLDER_MARKERS)


def _extract_image_url(p: dict) -> str:
    """Walk a priority-ordered list of fields and return the first valid URL."""

    # 1. image_hero (dict or str)
    hero = p.get("image_hero")
    if isinstance(hero, dict):
        url = hero.get("url", "")
        if _is_valid_image(url):
            return url
    elif _is_valid_image(hero):
        return hero

    # 2. official_images[] — prefer hero display_purpose
    for img in (p.get("official_images") or []):
        if isinstance(img, dict):
            if img.get("display_purpose") == "hero" and _is_valid_image(img.get("url")):
                return img["url"]
    for img in (p.get("official_images") or []):
        url = img.get("url") if isinstance(img, dict) else img
        if _is_valid_image(url):
            return url

    # 3. image_gallery[]
    for img in (p.get("image_gallery") or []):
        url = img.get("url") if isinstance(img, dict) else img
        if _is_valid_image(url):
            return url

    # 4. display.hero_image (dict or str)
    disp = p.get("display", {}).get("hero_image")
    if isinstance(disp, dict) and _is_valid_image(disp.get("url")):
        return disp["url"]
    if _is_valid_image(disp):
        return disp

    # 5. primary_source.image (Halilit scraper fallback)
    src = p.get("primary_source", {})
    if isinstance(src, dict) and _is_valid_image(src.get("image")):
        return src["image"]

    return ""


def _collect_gallery(p: dict, hero_url: str) -> List[dict]:
    """Gather all usable gallery images (max 20), with hero first."""
    gallery: List[dict] = []

    # Start with hero
    if hero_url:
        gallery.append({"url": hero_url})

    # Add from image_gallery
    for img in (p.get("image_gallery") or [])[:20]:
        entry = img if isinstance(img, dict) else {"url": img}
        url = entry.get("url", "")
        if _is_valid_image(url) and url != hero_url:
            gallery.append(entry)

    return gallery[:20]


# ---------------------------------------------------------------------------
# Core normalizer
# ---------------------------------------------------------------------------

def normalize_product(p: dict, fallback_brand: str = "") -> Optional[dict]:
    """
    Transform a raw product dict into the canonical frontend shape.
    Returns None if the product fails quality gates (no price or no image).
    """

    # --- ID ---
    pid = p.get("id") or p.get("halilit_id")
    if not pid:
        return None

    # --- Name ---
    name = (
        p.get("name")
        or p.get("product_name")
        or p.get("official_name")
        or "Unknown Product"
    )

    # --- Category ---
    category = p.get("category") or p.get(
        "taxonomy", {}).get("canonical_category", "Other")
    if category == "Uncategorized":
        category = "Other"

    # --- Price ---
    price = p.get("price") or p.get("price_il", 0) or p.get(
        "pricing", {}).get("price_il", 0)
    try:
        price = float(price)
    except (TypeError, ValueError):
        price = 0.0
    if price <= 0:
        return None  # Quality gate: must have price

    # --- Image ---
    image_url = _extract_image_url(p)
    if not image_url:
        return None  # Quality gate: must have image

    # --- Description ---
    description = (
        p.get("official_description")
        or p.get("description_long")
        or p.get("description_short")
        or ""
    )

    # --- Specs (merge two possible sources) ---
    specs: dict = {}
    if p.get("official_specs"):
        specs.update(p["official_specs"])
    if p.get("specifications"):
        specs.update(p["specifications"])

    # --- Gallery ---
    gallery = _collect_gallery(p, image_url)

    # --- Brand ---
    brand = p.get("brand") or fallback_brand or "Unknown"

    # --- Pricing tier ---
    tier = (
        p.get("pricing", {}).get("tier")
        or ("pro" if price > 2000 else "mid" if price > 500 else "entry")
    )

    # --- Sources ---
    sources = p.get("sources") or []
    if not sources:
        sources = ["halilit_direct"]
        if specs or description:
            sources.append("official_specs")

    # --- Assemble the canonical product ---
    return {
        "id": pid,
        "halilit_id": pid,
        "name": name,
        "product_name": name,
        "brand": brand,
        "category": category,
        "price": price,
        "price_il": price,
        "currency": "ILS",
        "image_url": image_url,
        "description": description,
        "image_hero": image_url,
        "image_gallery": gallery,
        "official_images": p.get("official_images", []),
        "taxonomy": p.get("taxonomy") or {"canonical_category": category},
        "display": {
            "hero_image": {"url": image_url},
            "color_hint": p.get("display", {}).get("color_hint", "bg-slate-800"),
            "display_role": p.get("display", {}).get("display_role", "entry"),
            "should_highlight": p.get("display", {}).get("should_highlight", False),
        },
        "sources": sources,
        "official_specs": specs,
        "specifications": specs,
        "quality_score": p.get("quality_score", 0),
        "data_completeness": p.get("data_completeness", 0),
        "review_data": {
            "aggregate_rating": (
                p.get("average_rating")
                or p.get("review_data", {}).get("aggregate_rating", 0)
            ),
            "total_reviews": (
                len(p.get("reviews", []))
                or p.get("review_data", {}).get("total_reviews", 0)
            ),
            "pros_and_cons": (
                p.get("pros_and_cons")
                or p.get("review_data", {}).get("pros_and_cons", {})
            ),
        },
        "pricing": {
            "price_il": price,
            "price_eilat": p.get("price_eilat") or 0,
            "tier": tier,
        },
    }


# ---------------------------------------------------------------------------
# Batch API — load + normalize every brand JSON in frontend/public/data/
# ---------------------------------------------------------------------------

def build_catalog(data_dir: str) -> Tuple[List[dict], dict]:
    """
    Read all brand JSON files in *data_dir*, normalize every product,
    and return (products_list, metadata_dict).
    """
    import json
    from pathlib import Path

    data_path = Path(data_dir)
    if not data_path.exists():
        logger.warning(f"Data directory not found: {data_dir}")
        return [], {"total_products": 0, "brands": [], "categories": {}}

    excluded = {"index.json", "search_index.json", "search_index_min.json",
                "galaxy_db.json", "package.json"}

    products_map: Dict[str, dict] = {}
    brands_found: set = set()

    for json_file in sorted(data_path.glob("*.json")):
        if json_file.name in excluded:
            continue

        try:
            with open(json_file, "r") as f:
                file_data = json.load(f)

            raw_products = (
                file_data if isinstance(file_data, list)
                else file_data.get("products", []) if isinstance(file_data, dict)
                else []
            )

            for raw in raw_products:
                product = normalize_product(raw, fallback_brand=json_file.stem)
                if product:
                    products_map[product["id"]] = product
                    brands_found.add(json_file.stem)
        except Exception as e:
            logger.error(f"Error loading {json_file.name}: {e}")

    products = list(products_map.values())
    categories: Dict[str, int] = {}
    for p in products:
        c = p.get("category", "Other")
        categories[c] = categories.get(c, 0) + 1

    metadata = {
        "total_products": len(products),
        "brands": sorted(brands_found),
        "categories": categories,
        "source": "conductor_verified_enriched_v8.2",
        "verification_status": "complete",
        "cache_ttl_seconds": 300,
    }

    logger.info(
        f"Catalog built: {len(products)} products from {len(brands_found)} brands")
    return products, metadata
