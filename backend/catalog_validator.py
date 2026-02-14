"""
Catalog Validator & Resolver — Smart Data Quality Engine
=========================================================

Single module that answers: "How complete is my catalog and what needs fixing?"

Scores every product on what the UI ACTUALLY renders:
  - name (required)        → 5pts
  - price (hero metric)    → 25pts
  - image_url (visual)     → 20pts
  - description (content)  → 15pts
  - specs (detail)         → 15pts
  - features (tags)        → 5pts
  - rating (social proof)  → 5pts
  - classification ok      → 5pts
  - sources/data_trust     → 5pts

Products get a status:
  COMPLETE  (90-100) — ready to shine
  GOOD      (70-89)  — usable, minor gaps
  PARTIAL   (40-69)  — visible but weak
  MINIMAL   (0-39)   — needs work

Provides:
  - Per-product scoring + what's missing
  - Catalog-wide health metrics
  - Smart resolution suggestions
  - Brand-level rollup
"""

import logging
from datetime import datetime
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# FIELD WEIGHTS — What the UI actually cares about
# ═══════════════════════════════════════════════════════════════════════════

FIELD_WEIGHTS = {
    "name":           5,   # required — always present if product exists
    "price":         25,   # hero metric in Spectrum + ProductPage
    "image":         20,   # visual identity
    "description":   15,   # ProductPage overview + Spectrum hover
    "specs":         15,   # ProductPage table + Spectrum grid
    "features":       5,   # smart tags + ProductPage bullets
    "rating":         5,   # stars in Spectrum + ProductPage
    "classification": 5,   # correct galaxy/spectrum placement
    "sources":        5,   # data trust three-pillar display
}

TOTAL_WEIGHT = sum(FIELD_WEIGHTS.values())  # 100


def _status_label(score: int) -> str:
    if score >= 90:
        return "COMPLETE"
    if score >= 70:
        return "GOOD"
    if score >= 40:
        return "PARTIAL"
    return "MINIMAL"


def _status_emoji(status: str) -> str:
    return {"COMPLETE": "✅", "GOOD": "🟢", "PARTIAL": "🟡", "MINIMAL": "🔴"}.get(status, "❓")


# ═══════════════════════════════════════════════════════════════════════════
# PER-PRODUCT VALIDATOR
# ═══════════════════════════════════════════════════════════════════════════

def validate_product(p: dict) -> dict:
    """
    Score a single normalized product on UI-relevant completeness.

    Args:
        p: Normalized product dict (output of normalize_product or catalog product)

    Returns:
        {
            "score": 0-100,
            "status": "COMPLETE" | "GOOD" | "PARTIAL" | "MINIMAL",
            "fields": { field: { "score": int, "max": int, "ok": bool } },
            "missing": ["price", "description", ...],
            "suggestions": ["Add price from Halilit catalog", ...]
        }
    """
    fields = {}
    missing = []
    suggestions = []

    # Name — always present if product was normalized
    name = p.get("name") or p.get("product_name") or ""
    name_ok = bool(name and len(name.strip()) > 2)
    fields["name"] = {"score": FIELD_WEIGHTS["name"] if name_ok else 0,
                      "max": FIELD_WEIGHTS["name"], "ok": name_ok}
    if not name_ok:
        missing.append("name")

    # Price — the most impactful missing field
    price = p.get("price") or p.get("price_il") or 0
    if isinstance(p.get("pricing"), dict):
        price = price or p["pricing"].get("price_il", 0)
    try:
        price = float(price)
    except (TypeError, ValueError):
        price = 0
    price_ok = price > 0
    fields["price"] = {"score": FIELD_WEIGHTS["price"] if price_ok else 0,
                       "max": FIELD_WEIGHTS["price"], "ok": price_ok}
    if not price_ok:
        missing.append("price")
        suggestions.append(
            "Add price — this is the #1 missing field for UI display")

    # Image
    image = p.get("image_url") or ""
    image_ok = bool(image and len(image) >
                    10 and "placeholder" not in image.lower())
    fields["image"] = {"score": FIELD_WEIGHTS["image"] if image_ok else 0,
                       "max": FIELD_WEIGHTS["image"], "ok": image_ok}
    if not image_ok:
        missing.append("image")
        suggestions.append("Add product image from manufacturer site")

    # Description
    desc = p.get("description") or p.get("official_description") or ""
    desc_ok = bool(desc and len(desc.strip()) >= 20)
    # Partial credit for short descriptions
    desc_partial = bool(desc and 10 <= len(desc.strip()) < 20)
    desc_score = (FIELD_WEIGHTS["description"] if desc_ok
                  else FIELD_WEIGHTS["description"] // 2 if desc_partial
                  else 0)
    fields["description"] = {"score": desc_score,
                             "max": FIELD_WEIGHTS["description"], "ok": desc_ok}
    if not desc_ok:
        missing.append("description")
        suggestions.append("Add product description from brand website")

    # Specs
    specs = p.get("specs") or p.get("official_specs") or {}
    if isinstance(specs, dict):
        # Filter out meta keys
        real_specs = {k: v for k, v in specs.items()
                      if k not in ("sku", "note", "extracted_name", "features",
                                   "short_description", "long_description")}
    else:
        real_specs = {}
    specs_ok = len(real_specs) >= 3
    specs_partial = 1 <= len(real_specs) < 3
    specs_score = (FIELD_WEIGHTS["specs"] if specs_ok
                   else FIELD_WEIGHTS["specs"] // 2 if specs_partial
                   else 0)
    fields["specs"] = {"score": specs_score,
                       "max": FIELD_WEIGHTS["specs"], "ok": specs_ok}
    if not specs_ok:
        missing.append("specs")
        suggestions.append("Add technical specifications from manufacturer")

    # Features
    features = p.get("features") or p.get("feature_list") or []
    features_ok = isinstance(features, list) and len(features) >= 2
    fields["features"] = {"score": FIELD_WEIGHTS["features"] if features_ok else 0,
                          "max": FIELD_WEIGHTS["features"], "ok": features_ok}
    if not features_ok:
        missing.append("features")

    # Rating
    rating = p.get("rating") or p.get("average_rating") or 0
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        rating = 0
    rating_ok = rating > 0
    fields["rating"] = {"score": FIELD_WEIGHTS["rating"] if rating_ok else 0,
                        "max": FIELD_WEIGHTS["rating"], "ok": rating_ok}
    if not rating_ok:
        missing.append("rating")

    # Classification — check it's not in the catch-all bucket
    galaxy = p.get("galaxy_id") or ""
    spectrum = p.get("spectrum_id") or ""
    class_ok = bool(galaxy and spectrum and spectrum != "general-accessories")
    fields["classification"] = {
        "score": FIELD_WEIGHTS["classification"] if class_ok else 0,
        "max": FIELD_WEIGHTS["classification"], "ok": class_ok
    }
    if not class_ok:
        missing.append("classification")
        suggestions.append(
            "Re-classify product — currently in catch-all category")

    # Sources — data trust completeness
    sources = p.get("sources") or []
    source_count = len(sources) if isinstance(sources, list) else 0
    sources_ok = source_count >= 2  # At least 2 of 3 pillars
    sources_score = (FIELD_WEIGHTS["sources"] if sources_ok
                     else FIELD_WEIGHTS["sources"] // 2 if source_count == 1
                     else 0)
    fields["sources"] = {"score": sources_score,
                         "max": FIELD_WEIGHTS["sources"], "ok": sources_ok}
    if not sources_ok:
        missing.append("sources")

    # Total score
    total_score = sum(f["score"] for f in fields.values())
    status = _status_label(total_score)

    return {
        "score": total_score,
        "status": status,
        "fields": fields,
        "missing": missing,
        "suggestions": suggestions[:3],  # Top 3 most impactful
    }


# ═══════════════════════════════════════════════════════════════════════════
# CATALOG-WIDE HEALTH
# ═══════════════════════════════════════════════════════════════════════════

def validate_catalog(products: List[dict]) -> dict:
    """
    Score the entire catalog. Returns health metrics the UI can display.

    Returns:
        {
            "health_score": 0-100 (catalog average),
            "total_products": int,
            "status_counts": { "COMPLETE": N, "GOOD": N, "PARTIAL": N, "MINIMAL": N },
            "field_coverage": { "price": 13.0, "image": 100.0, ... },
            "brand_health": { "roland": { "score": 75, "count": 50, ... }, ... },
            "top_issues": ["87% of products missing price", ...],
            "resolution_queue": [ { product summary + what's missing } ... ],
        }
    """
    if not products:
        return _empty_health()

    total = len(products)
    status_counts = {"COMPLETE": 0, "GOOD": 0, "PARTIAL": 0, "MINIMAL": 0}
    field_ok_counts = {f: 0 for f in FIELD_WEIGHTS}
    brand_scores: Dict[str, List[int]] = {}
    brand_counts: Dict[str, int] = {}
    score_sum = 0
    resolution_queue = []

    for p in products:
        result = validate_product(p)
        score = result["score"]
        status = result["status"]
        score_sum += score
        status_counts[status] = status_counts.get(status, 0) + 1

        # Field coverage
        for field_name, field_data in result["fields"].items():
            if field_data["ok"]:
                field_ok_counts[field_name] = field_ok_counts.get(
                    field_name, 0) + 1

        # Brand rollup
        brand = (p.get("brand") or "Unknown").strip().lower()
        brand_scores.setdefault(brand, []).append(score)
        brand_counts[brand] = brand_counts.get(brand, 0) + 1

        # Resolution queue — products that need work (not complete)
        if status != "COMPLETE" and result["missing"]:
            resolution_queue.append({
                "id": p.get("id") or p.get("halilit_id") or "?",
                "name": p.get("name") or p.get("product_name") or "?",
                "brand": p.get("brand") or "?",
                "score": score,
                "status": status,
                "missing": result["missing"],
                "top_suggestion": result["suggestions"][0] if result["suggestions"] else None,
            })

    # Catalog health score
    health_score = round(score_sum / total) if total else 0

    # Field coverage percentages
    field_coverage = {
        f: round(100 * field_ok_counts.get(f, 0) / total, 1) if total else 0
        for f in FIELD_WEIGHTS
    }

    # Brand health rollup
    brand_health = {}
    for brand, scores in sorted(brand_scores.items()):
        avg = round(sum(scores) / len(scores)) if scores else 0
        brand_health[brand] = {
            "score": avg,
            "status": _status_label(avg),
            "count": brand_counts.get(brand, 0),
        }

    # Top issues — sorted by impact
    top_issues = []
    for field, coverage in sorted(field_coverage.items(), key=lambda x: x[1]):
        if coverage < 95:
            pct_missing = round(100 - coverage, 1)
            count_missing = total - field_ok_counts.get(field, 0)
            top_issues.append(
                f"{pct_missing}% of products ({count_missing}) missing {field}"
            )

    # Sort resolution queue by score (worst first) and limit
    resolution_queue.sort(key=lambda x: x["score"])

    return {
        "health_score": health_score,
        "health_status": _status_label(health_score),
        "total_products": total,
        "status_counts": status_counts,
        "field_coverage": field_coverage,
        "brand_health": brand_health,
        "top_issues": top_issues[:10],
        "resolution_queue_size": len(resolution_queue),
        "resolution_queue": resolution_queue[:50],  # Top 50 worst products
        "timestamp": datetime.now().isoformat(),
    }


def _empty_health() -> dict:
    return {
        "health_score": 0,
        "health_status": "MINIMAL",
        "total_products": 0,
        "status_counts": {"COMPLETE": 0, "GOOD": 0, "PARTIAL": 0, "MINIMAL": 0},
        "field_coverage": {f: 0 for f in FIELD_WEIGHTS},
        "brand_health": {},
        "top_issues": ["No products in catalog"],
        "resolution_queue_size": 0,
        "resolution_queue": [],
        "timestamp": datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════
# SMART RESOLVER — Auto-fix what can be fixed
# ═══════════════════════════════════════════════════════════════════════════

def resolve_product(p: dict, catalog_products: List[dict] = None) -> Tuple[dict, List[str]]:
    """
    Attempt to resolve missing data using smart heuristics.
    Does NOT mutate the original — returns a new dict + list of changes made.

    Strategies:
    1. Price estimation from same-brand/same-spectrum peers
    2. Description synthesis from specs + features
    3. Feature extraction from specs keys
    4. Source inference from available data
    """
    resolved = dict(p)  # shallow copy
    changes = []

    # 1. Price estimation from peers — flagged as market estimation, NOT real price
    price = resolved.get("price", 0)
    if not price or float(price) <= 0:
        if catalog_products:
            peer_prices = _get_peer_prices(resolved, catalog_products)
            if peer_prices:
                estimated = round(sum(peer_prices) / len(peer_prices), 2)
                # Store estimation as supplementary data, NOT as the real price
                # The main price stays 0 (= "Price on request")
                resolved["market_price_estimate"] = estimated
                resolved["market_price_peers"] = len(peer_prices)
                resolved["price_eilat"] = 0.0
                # Mark as no real price
                dt = resolved.get("data_trust") or {}
                dt["price_source"] = "none"
                resolved["data_trust"] = dt
                changes.append(
                    f"Market estimate ₪{estimated:.0f} from {len(peer_prices)} peers (not shown as price)")

    # 2. Description synthesis from specs + features + name
    desc = resolved.get("description") or ""
    if not desc or len(desc.strip()) < 20:
        synth = _synthesize_description(resolved)
        if synth:
            resolved["description"] = synth
            resolved["description_short"] = synth[:200] + \
                ("..." if len(synth) > 200 else "")
            dt = resolved.get("data_trust") or {}
            dt["description_source"] = "synthesized"
            resolved["data_trust"] = dt
            changes.append("Synthesized description from specs/features")

    # 3. Feature extraction from specs
    features = resolved.get("features") or []
    if not features or len(features) < 2:
        extracted = _extract_features_from_specs(resolved)
        if extracted:
            resolved["features"] = extracted
            changes.append(f"Extracted {len(extracted)} features from specs")

    # 4. Source inference
    sources = resolved.get("sources") or []
    if not sources or len(sources) < 2:
        inferred = _infer_sources(resolved)
        if len(inferred) > len(sources):
            resolved["sources"] = inferred
            changes.append(f"Inferred sources: {', '.join(inferred)}")

    # Recompute quality score after resolution
    if changes:
        result = validate_product(resolved)
        resolved["quality_score"] = result["score"]
        resolved["data_status"] = result["status"]
        resolved["data_missing"] = result["missing"]

    return resolved, changes


def resolve_catalog(products: List[dict]) -> Tuple[List[dict], dict]:
    """
    Resolve all products in a catalog. Returns resolved products + summary.
    """
    resolved_products = []
    total_changes = 0
    products_improved = 0

    for p in products:
        resolved, changes = resolve_product(p, catalog_products=products)
        resolved_products.append(resolved)
        if changes:
            total_changes += len(changes)
            products_improved += 1

    summary = {
        "total_products": len(products),
        "products_improved": products_improved,
        "total_changes": total_changes,
        "timestamp": datetime.now().isoformat(),
    }

    return resolved_products, summary


# ═══════════════════════════════════════════════════════════════════════════
# RESOLUTION HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _get_peer_prices(product: dict, catalog: List[dict]) -> List[float]:
    """Find prices from products in the same brand + spectrum."""
    brand = (product.get("brand") or "").lower()
    spectrum = product.get("spectrum_id") or ""
    galaxy = product.get("galaxy_id") or ""

    prices = []

    # Strategy 1: Same brand + same spectrum
    for p in catalog:
        if p.get("id") == product.get("id"):
            continue
        p_price = p.get("price", 0)
        if not p_price or float(p_price) <= 0:
            continue
        p_brand = (p.get("brand") or "").lower()
        p_spectrum = p.get("spectrum_id") or ""

        if p_brand == brand and p_spectrum == spectrum:
            prices.append(float(p_price))

    if prices:
        return prices

    # Strategy 2: Same brand only (any spectrum)
    for p in catalog:
        if p.get("id") == product.get("id"):
            continue
        p_price = p.get("price", 0)
        if not p_price or float(p_price) <= 0:
            continue
        p_brand = (p.get("brand") or "").lower()

        if p_brand == brand:
            prices.append(float(p_price))

    if prices:
        return prices

    # Strategy 3: Same spectrum, any brand (wider net)
    for p in catalog:
        if p.get("id") == product.get("id"):
            continue
        p_price = p.get("price", 0)
        if not p_price or float(p_price) <= 0:
            continue
        p_spectrum = p.get("spectrum_id") or ""

        if p_spectrum == spectrum:
            prices.append(float(p_price))

    # Limit to avoid outlier pollution
    if len(prices) > 10:
        prices.sort()
        prices = prices[len(prices) // 4: 3 * len(prices) // 4]  # IQR

    return prices


def _compute_tier_from_price(price: float) -> str:
    if price <= 0:
        return "entry"
    if price < 500:
        return "entry"
    if price < 1500:
        return "mid"
    if price < 4000:
        return "pro"
    return "flagship"


def _synthesize_description(p: dict) -> str:
    """Build a description from what we have."""
    name = p.get("name") or ""
    brand = p.get("brand") or ""
    specs = p.get("specs") or {}
    features = p.get("features") or []
    category = p.get("category") or p.get("galaxy_id") or ""
    spectrum = p.get("spectrum_id") or ""

    parts = []

    # Opening line from name + brand
    if name and brand:
        # Extract English portion for cleaner description
        import re
        eng = re.search(r'[A-Za-z][\w\s\-\.\/]+', name)
        model = eng.group(0).strip() if eng else name
        parts.append(f"The {brand} {model}")
    elif name:
        parts.append(name)

    # Add category context
    spectrum_label = spectrum.replace("-", " ").title() if spectrum else ""
    if spectrum_label:
        parts.append(f"is a professional {spectrum_label.lower()} solution")

    # Add spec highlights (top 3 most interesting)
    _BORING_KEYS = {"sku", "note", "extracted_name", "features",
                    "short_description", "long_description", "weight", "dimensions"}
    interesting_specs = {k: v for k, v in specs.items()
                         if k.lower() not in _BORING_KEYS and v}
    if interesting_specs:
        spec_highlights = list(interesting_specs.items())[:3]
        spec_text = ", ".join(f"{k}: {v}" for k, v in spec_highlights)
        parts.append(f"featuring {spec_text}")

    # Add features
    if features:
        feat_text = ", ".join(features[:3])
        parts.append(f"with {feat_text}")

    result = ". ".join(parts).strip()
    if result and not result.endswith("."):
        result += "."

    return result if len(result) >= 20 else ""


def _extract_features_from_specs(p: dict) -> List[str]:
    """Extract feature-like entries from specs dict."""
    specs = p.get("specs") or {}
    features = []

    _BORING = {"sku", "note", "extracted_name", "weight", "dimensions",
               "width", "height", "depth", "color"}

    for key, val in specs.items():
        if key.lower() in _BORING or not val:
            continue
        if isinstance(val, str) and len(val) > 5:
            features.append(f"{key}: {val}")

    return features[:8]


def _infer_sources(p: dict) -> List[str]:
    """Infer which data pillars are represented."""
    sources = []

    # Halilit — has Halilit URL or price
    if p.get("halilit_url") or (p.get("price", 0) and float(p.get("price", 0)) > 0):
        sources.append("halilit")

    # Official — has specs or official description or official URL
    specs = p.get("specs") or {}
    real_specs = {k: v for k, v in specs.items()
                  if k not in ("sku", "note", "extracted_name") and v}
    if real_specs or p.get("description") or p.get("official_url"):
        sources.append("official")

    # Contextual — has ratings or reviews
    if (p.get("rating") and float(p.get("rating", 0)) > 0) or p.get("pros") or p.get("cons"):
        sources.append("contextual")

    if not sources:
        sources = ["halilit"]  # Minimum — we have the listing

    return sources
