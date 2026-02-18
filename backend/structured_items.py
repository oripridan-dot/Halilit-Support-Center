"""
Structured items: products organized in strict order:

  1. BRAND       — top level (e.g. Roland, PreSonus)
  2. WHAT THEY ARE — category / product type (e.g. Keyboards, Drums, Studio)
  3. RELATIONS   — product lines (series/families), variants, accessories, related

Used by GET /api/structured-items. Response shape:
  _hierarchy: ["brand", "category", "relations"]
  brands: [ { brand, brand_key, categories: [ { ... what they are ... relations: [ ... ] } ] } ]
  products_by_id: { id -> summary }

Accessory families are grouped by semantic type (cases-bags, stands, pedals).
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
    {"pedal", "stand", "cover", "dust", "case", "bag", "monitor stand", "cvr", "flb", "flybar"}
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
    Build hierarchy: 1) Brand, 2) Category (what they are), 3) Relations (product lines, variants, accessories, related).

    Hierarchy rule: Families whose products are all accessories (source of accessory_for) are not
    shown as top-level cards (e.g. flybars, covers). They only appear under their parent product's
    "Accessories & parts" strip for a consistent parent/child relationship across all brands.

    Returns:
      _hierarchy: ["brand", "category", "relations"]
      galaxies: list of { id, label, spectrums } for nav
      brands: list of {
        brand, brand_key,
        categories: [  # what they are (product type)
          { galaxy_id, galaxy_label, spectrum_id, spectrum_label,
            relations: [  # product lines / families with variants, accessories, related
              { series_key, series_label, families, variant_ids, direct_accessory_ids, related_ids }
            ] }
        ]
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

    # Products that are accessories (source of accessory_for) — they belong under a parent, not as top-level cards.
    # Relationship source_id may be numeric (e.g. "3181079") while catalog product id may be prefixed (e.g. "halilit-3181079"); match both.
    graph_accessory_source_ids: set[str] = set()
    for _pid, rels in relationships_map.items():
        for r in rels:
            if (r.get("relationship_type") or "").lower() == "accessory_for":
                src = r.get("source_id")
                if src:
                    graph_accessory_source_ids.add(src)
    accessory_product_ids: set[str] = set(graph_accessory_source_ids)
    for p in products:
        pid = p.get("id")
        if not pid or pid in accessory_product_ids:
            continue
        normalized = pid.replace("halilit-", "", 1) if pid.startswith("halilit-") else pid
        if normalized in graph_accessory_source_ids:
            accessory_product_ids.add(pid)
        elif "-" in pid and pid.split("-", 1)[-1] in graph_accessory_source_ids:
            accessory_product_ids.add(pid)
        elif "_" in pid and pid.split("_", 1)[-1] in graph_accessory_source_ids:
            accessory_product_ids.add(pid)
    # One-pass index: family_id -> list of (product_id, image_url) for variant_ids and hero_image
    family_id_to_variants: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for p in products:
        fid = (p.get("family_id") or "").strip()
        if fid:
            family_id_to_variants[fid].append((p.get("id"), p.get("image_url") or ""))

    # Group families by (brand, spectrum_id, series_key). Skip accessory-only families (e.g. flybar, cover) so they only appear under their parent
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
        variants_list = family_id_to_variants.get(fid, [])
        variant_ids = [vid for vid, _ in variants_list]
        if not hero_image and variants_list:
            hero_image = next((img for _, img in variants_list if img), "")
        # Hierarchy: accessory-only families (e.g. cover, flybar) must not be top-level; they appear under parent's Accessories.
        # 1) All variants are graph-marked accessories (source of accessory_for).
        if variant_ids and all(pid in accessory_product_ids for pid in variant_ids):
            continue
        # 2) Heuristic: family name indicates accessory type (cover, flybar, etc.) — hide as top-level even if graph direction is wrong.
        if _is_accessory_family(family_name):
            continue
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

    # spectrum_id -> (galaxy_id, galaxy_label, spectrum_label) so breadcrumbs show type correctly
    spectrum_to_galaxy: dict[str, tuple[str, str, str]] = {}
    for g in galaxies:
        gid = g.get("id", "")
        glabel = g.get("label", "")
        for sp in g.get("spectrums", []):
            sid = sp.get("id", "")
            slabel = sp.get("label", "")
            if sid:
                spectrum_to_galaxy[sid] = (gid, glabel, slabel)

    # Orphan roof: ensure every product appears under brand → type → series (no data left out)
    placed_ids: set[str] = set()
    for (_, _), series_map in by_brand_spectrum.items():
        for data in series_map.values():
            placed_ids.update(data["variant_ids"])
            placed_ids.update(data["accessory_ids"])
            placed_ids.update(data["related_ids"])
    for p in products:
        pid = p.get("id")
        if not pid or pid in placed_ids:
            continue
        if pid in accessory_product_ids:
            continue
        brand = (p.get("brand") or "").strip().lower()
        if not brand:
            continue
        spectrum_id = (p.get("spectrum_id") or "").strip() or "general-accessories"
        key = (brand, spectrum_id)
        entry = by_brand_spectrum[key]["other"]
        entry["families"].append({
            "family_id": f"orphan_{pid}",
            "family_name": (p.get("name") or p.get("product_name") or "Other"),
            "hero_image": p.get("image_url", ""),
            "variant_count": 1,
            "variants": [{"id": pid, "name": p.get("name", ""), "image_url": p.get("image_url", ""), "price": p.get("price", 0)}],
        })
        entry["variant_ids"].append(pid)
        placed_ids.add(pid)

    # Group by brand (1), then category / what they are (2), then relations (3: series/families)
    by_brand_only: dict[str, dict] = defaultdict(lambda: {"brand": "", "brand_key": "", "categories": defaultdict(lambda: {"galaxy_id": "", "galaxy_label": "", "spectrum_id": "", "spectrum_label": "", "relations": []})})
    for (brand_key, spectrum_id), series_map in sorted(by_brand_spectrum.items()):
        gid, glabel, slabel = spectrum_to_galaxy.get(spectrum_id, ("accessories-utility", "Accessories & Utility", "Uncategorized"))
        if by_brand_only[brand_key]["brand_key"] == "":
            display_name = brand_key.title()
            for p in products:
                if (p.get("brand") or "").strip().lower() == brand_key:
                    display_name = (p.get("brand") or "").strip()
                    break
            by_brand_only[brand_key]["brand"] = display_name
            by_brand_only[brand_key]["brand_key"] = brand_key
        category_key = spectrum_id or "uncategorized"
        cat = by_brand_only[brand_key]["categories"][category_key]
        if not cat.get("galaxy_id"):
            cat["galaxy_id"] = gid
            cat["galaxy_label"] = glabel
            cat["spectrum_id"] = spectrum_id
            cat["spectrum_label"] = slabel
        SEMANTIC_SERIES_LABELS = {"cases-bags": "Cases & Bags", "stands": "Stands", "pedals": "Pedals", "other-accessories": "Other Accessories", "other": "Other"}
        for sk, data in sorted(series_map.items()):
            if not (data.get("families") or data.get("variant_ids")):
                continue
            series_label = SEMANTIC_SERIES_LABELS.get(sk) or (sk.replace("-", " ").title() if sk else "Other")
            cat["relations"].append({
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
        categories_list = []
        for cat in b["categories"].values():
            if cat.get("relations"):
                rels = cat["relations"]
                categories_list.append({
                    "galaxy_id": cat.get("galaxy_id", ""),
                    "galaxy_label": cat.get("galaxy_label", ""),
                    "spectrum_id": cat.get("spectrum_id", ""),
                    "spectrum_label": cat.get("spectrum_label", ""),
                    "relations": rels,
                    "series": rels,
                })
        brands_list.append({
            "brand": b["brand"],
            "brand_key": brand_key,
            "categories": categories_list,
            "types": categories_list,
        })

    products_by_id = {p.get("id"): p for p in products if p.get("id")}

    return {
        "_hierarchy": ["brand", "category", "relations"],
        "galaxies": galaxies,
        "brands": brands_list,
        "products_by_id": products_by_id,
    }
