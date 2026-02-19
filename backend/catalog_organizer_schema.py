"""
Unified schema for per-brand consolidated catalogs.

Every brand catalog written by the organizer has this structure so that:
- Search is trivial (search_index with id, t, s, b)
- Browsing by category is trivial (categories[].product_ids)
- Frontend and API can assume the same shape for every brand.

Compliance: Data is derived from existing Halilit/ingestion data only.
"""

from __future__ import annotations

from typing import Any, Dict, List

# ─── Consolidated brand catalog (single source of truth per brand) ───

def consolidated_catalog_shape() -> Dict[str, Any]:
    """Return the canonical shape for documentation and validation."""
    return {
        "brand_identity": {
            "id": "string (slug, e.g. roland)",
            "name": "string (display name)",
            "slug": "string (URL-safe)",
            "logo_url": "string | null",
            "website": "string | null",
            "description": "string | null",
        },
        "categories": [
            {
                "id": "string (e.g. keyboards-synths)",
                "label": "string (e.g. Keyboards & Synthesizers)",
                "product_ids": ["halilit_id", "..."],
            }
        ],
        "products": "[ { ...product } ]  # full product objects, same as current",
        "search_index": [
            {
                "id": "halilit_id",
                "t": "product name / search title",
                "s": "category label",
                "b": "brand slug",
            }
        ],
        "meta": {
            "total_products": "int",
            "total_categories": "int",
            "organized_at": "ISO8601",
        },
    }


def build_search_index(products: List[Dict[str, Any]], brand_slug: str) -> List[Dict[str, Any]]:
    """Build search_index from products list. Used by fallback organizer."""
    out: List[Dict[str, Any]] = []
    for p in products:
        pid = p.get("halilit_id") or p.get("id") or ""
        name = (p.get("product_name") or p.get("name") or "").strip()
        tax = p.get("taxonomy") or {}
        cat = tax.get("canonical_category") if isinstance(tax, dict) else None
        out.append({
            "id": pid,
            "t": name,
            "s": (cat or "Uncategorized").strip(),
            "b": brand_slug.lower(),
        })
    return out


def build_categories_from_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group product IDs by canonical_category. Used by fallback organizer."""
    by_cat: Dict[str, List[str]] = {}
    for p in products:
        pid = p.get("halilit_id") or p.get("id")
        if not pid:
            continue
        tax = p.get("taxonomy") or {}
        cat = tax.get("canonical_category") if isinstance(tax, dict) else None
        label = (cat or "Uncategorized").strip()
        # slug-style id
        cid = label.lower().replace(" & ", "-").replace(" ", "-").replace(",", "")
        cid = "".join(c for c in cid if c.isalnum() or c == "-") or "uncategorized"
        by_cat.setdefault(cid, []).append(pid)
    categories = []
    for cid, ids in sorted(by_cat.items()):
        label = "Uncategorized"
        for p in products:
            if (p.get("halilit_id") or p.get("id")) in ids:
                tax = p.get("taxonomy") or {}
                label = tax.get("canonical_category") if isinstance(tax, dict) else "Uncategorized"
                label = (label or "Uncategorized").strip()
                break
        categories.append({"id": cid, "label": label, "product_ids": ids})
    return categories
