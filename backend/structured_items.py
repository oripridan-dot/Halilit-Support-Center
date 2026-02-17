"""
Structured items tree: brand → type (galaxy/spectrum) → series/family → variants, colors, accessories, related.

Used by GET /api/structured-items and by the Items UI for an interactive hierarchy
with large images and product thumbnails, ready to switch with interconnected products.

Accessory families are grouped by semantic type (cases-bags, stands, pedals) so e.g. all
guitar bags appear under one "Cases & Bags" item. Visual classification (see
ingestion.visual_validator.classify_product_image) can be used to verify or suggest
merges and to store visual_product_type for grouping overrides.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def get_visual_series_overrides() -> dict[str, str]:
    """Load family_id -> series_key overrides from visual_grouping_overrides.json (verify-and-apply)."""
    try:
        from backend.project_config import DATA_DIR
        path = DATA_DIR / "visual_grouping_overrides.json"
        if not path.exists():
            return {}
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return dict(data.get("overrides", {}))
    except Exception:
        return {}

ACCESSORY_KEYWORDS = frozenset(
    {"pedal", "stand", "cover", "dust", "case", "bag", "monitor stand"}
)

# Semantic groups for accessories so e.g. all guitar bags/cases group under one item
ACCESSORY_SEMANTIC_GROUPS = [
    ("cases-bags", ("bag", "case", "cover", "dust")),  # guitar bags, cases, dust covers
    ("stands", ("stand", "monitor stand")),
    ("pedals", ("pedal",)),
    ("other-accessories", ()),  # fallback
]


def _normalize_series_token(token: str) -> str:
    """Collapse model numbers to product line: Vad316 → vad, Td713 → td."""
    if not token:
        return ""
    s = token.strip().lower()
    letters = "".join(c for c in s if c.isalpha())
    if letters:
        return letters
    for i, c in enumerate(s):
        if c.isalpha():
            end = i + 1
            while end < len(s) and s[end].isalpha():
                end += 1
            return s[i:end]
    return s


def _series_key(brand: str, family_name: str, series: str, family_id: str) -> str:
    """
    Canonical series key. For accessory families (bag, case, stand, pedal, cover)
    returns a semantic group (cases-bags, stands, pedals) so they group under one item.
    """
    name = (family_name or "").strip()
    if _is_accessory_family(name):
        return _accessory_semantic_series(name)
    s = (series or "").strip()
    if s:
        return s.lower()
    br = (brand or "").strip()
    if br and name.lower().startswith(br.lower() + " "):
        rest = name[len(br) :].strip()
        if rest:
            first_token = rest.split()[0].strip().lower()
            normalized = _normalize_series_token(first_token)
            if normalized:
                return normalized
            return first_token
    if name:
        first_token = name.split()[0].strip().lower()
        normalized = _normalize_series_token(first_token)
        if normalized:
            return normalized
        return first_token
    return (family_id or "").replace("fam_", "").split("_")[0].lower()


def _is_accessory_family(family_name: str) -> bool:
    name = (family_name or "").lower()
    return any(kw in name for kw in ACCESSORY_KEYWORDS)


def _accessory_semantic_series(family_name: str) -> str:
    """
    Group accessory families by semantic type so e.g. all guitar bags/cases
    become one item (cases-bags), all stands one item (stands), all pedals one (pedals).
    """
    name = (family_name or "").lower()
    for group_key, keywords in ACCESSORY_SEMANTIC_GROUPS:
        if any(kw in name for kw in keywords):
            return group_key
    return "other-accessories"


def build_structured_items(catalog: dict[str, Any]) -> dict[str, Any]:
    """
    Build hierarchy: brand → type (galaxy/spectrum) → series → items with variants, accessories, related.

    Returns:
      galaxies: list of { id, label, spectrums } for nav
      brands: list of {
        brand, brand_key,
        types: [ { galaxy_id, galaxy_label, spectrum_id, spectrum_label, series: [ {
          series_key, series_label,
          families: [ { family_id, family_name, hero_image, variant_count, variants: [ product summaries ] } ],
          variant_ids, direct_accessory_ids, related_ids
        } ] } ]
      }
      products_by_id: { id -> product } for resolving thumbnails/links
    """
    products = catalog.get("products", [])
    families_meta = catalog.get("families", {})
    indexes = catalog.get("indexes", {})
    relationships_map = indexes.get("relationships", {})
    product_id_to_idx = {p.get("id"): i for i, p in enumerate(products) if p.get("id")}

    # Product lookup
    def get_product(pid: str) -> dict | None:
        if pid in product_id_to_idx:
            idx = product_id_to_idx[pid]
            if 0 <= idx < len(products):
                return products[idx]
        return None

    # Group families by (brand, spectrum_id, series_key). Spectrum from first variant.
    # Structure: (brand_key, spectrum_id) -> (series_key -> { families, variant_ids, ... })
    by_brand_spectrum: dict[tuple[str, str], dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {
        "families": [],
        "variant_ids": [],
        "accessory_ids": [],
        "related_ids": [],
    }))

    visual_overrides = get_visual_series_overrides()
    for fid, fam in families_meta.items():
        brand = (fam.get("brand") or "").strip()
        if not brand:
            continue
        brand_key = brand.lower()
        family_name = fam.get("family_name", "") or ""
        series_key = visual_overrides.get(fid) or _series_key(brand, family_name, fam.get("series", ""), fid)
        hero_image = fam.get("hero_image", "")
        variant_ids = []  # from graph we don't have variant_ids in families_meta; get from products
        for p in products:
            if (p.get("family_id") or "").strip() == fid:
                variant_ids.append(p.get("id"))
                if not hero_image and p.get("image_url"):
                    hero_image = p.get("image_url")
        spectrum_id = ""
        if variant_ids and variant_ids[0]:
            first_p = get_product(variant_ids[0])
            if first_p:
                spectrum_id = (first_p.get("spectrum_id") or "").strip() or "uncategorized"
        key = (brand_key, spectrum_id)
        entry = by_brand_spectrum[key][series_key]
        entry["families"].append({
            "family_id": fid,
            "family_name": family_name,
            "hero_image": hero_image,
            "variant_count": len(variant_ids),
            "variants": [
                {
                    "id": pid,
                    "name": (get_product(pid) or {}).get("name", ""),
                    "image_url": (get_product(pid) or {}).get("image_url", ""),
                    "price": (get_product(pid) or {}).get("price", 0),
                }
                for pid in variant_ids[:20]
            ],
        })
        entry["variant_ids"].extend(variant_ids)
        # Collect accessories and related from relationships
        for pid in variant_ids:
            rels = relationships_map.get(pid, [])
            for r in rels:
                rel_type = (r.get("relationship_type") or "").lower()
                other_id = r.get("target_id") if r.get("source_id") == pid else r.get("source_id")
                if not other_id:
                    continue
                if rel_type == "accessory_for":
                    if other_id not in entry["accessory_ids"]:
                        entry["accessory_ids"].append(other_id)
                elif rel_type in ("compatible_with", "alternative_to", "variant_of", "bundle_with"):
                    if other_id not in entry["related_ids"]:
                        entry["related_ids"].append(other_id)

    # Build galaxy/spectrum labels from product_normalizer
    try:
        from backend.product_normalizer import GALAXIES
        galaxies = GALAXIES
    except Exception:
        galaxies = []

    spectrum_to_galaxy: dict[str, tuple[str, str]] = {}
    for g in galaxies:
        gid = g.get("id", "")
        glabel = g.get("label", "")
        for sp in g.get("spectrums", []):
            sid = sp.get("id", "")
            slabel = sp.get("label", "")
            if sid:
                spectrum_to_galaxy[sid] = (gid, glabel)

    # Group by brand_key, then by spectrum (type), then series
    by_brand_only: dict[str, dict] = defaultdict(lambda: {"brand": "", "brand_key": "", "types": defaultdict(lambda: {"galaxy_id": "", "galaxy_label": "", "spectrum_id": "", "spectrum_label": "", "series": []})})
    for (brand_key, spectrum_id), series_map in sorted(by_brand_spectrum.items()):
        gid, glabel = spectrum_to_galaxy.get(spectrum_id, (spectrum_id or "uncategorized", spectrum_id or "Uncategorized"))
        if by_brand_only[brand_key]["brand_key"] == "":
            display_name = brand_key.title()
            for p in products:
                if (p.get("brand") or "").strip().lower() == brand_key:
                    display_name = (p.get("brand") or "").strip()
                    break
            by_brand_only[brand_key]["brand"] = display_name
            by_brand_only[brand_key]["brand_key"] = brand_key
        type_key = spectrum_id or "uncategorized"
        t = by_brand_only[brand_key]["types"][type_key]
        if not t.get("galaxy_id"):
            t["galaxy_id"] = gid
            t["galaxy_label"] = glabel
            t["spectrum_id"] = spectrum_id
            t["spectrum_label"] = glabel
        SEMANTIC_SERIES_LABELS = {"cases-bags": "Cases & Bags", "stands": "Stands", "pedals": "Pedals", "other-accessories": "Other Accessories"}
        for sk, data in sorted(series_map.items()):
            series_label = SEMANTIC_SERIES_LABELS.get(sk) or (sk.replace("-", " ").title() if sk else "Other")
            t["series"].append({
                "series_key": sk,
                "series_label": series_label,
                "families": data["families"],
                "variant_ids": data["variant_ids"][:50],
                "direct_accessory_ids": data["accessory_ids"][:30],
                "related_ids": data["related_ids"][:30],
            })

    brands_list = []
    for brand_key in sorted(by_brand_only.keys()):
        b = by_brand_only[brand_key]
        types_list = []
        for t in b["types"].values():
            if t.get("series"):
                types_list.append({
                    "galaxy_id": t.get("galaxy_id", ""),
                    "galaxy_label": t.get("galaxy_label", ""),
                    "spectrum_id": t.get("spectrum_id", ""),
                    "spectrum_label": t.get("spectrum_label", ""),
                    "series": t["series"],
                })
        brands_list.append({"brand": b["brand"], "brand_key": brand_key, "types": types_list})

    products_by_id = {p.get("id"): p for p in products if p.get("id")}

    return {
        "galaxies": galaxies,
        "brands": brands_list,
        "products_by_id": products_by_id,
    }
