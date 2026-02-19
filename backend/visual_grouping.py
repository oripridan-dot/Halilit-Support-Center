"""
Visual grouping: run vision AI on family hero images and suggest merges.

Used by:
- backend/scripts/visual_grouping_suggest.py (CLI)
- POST /api/visual-grouping/suggest (API)
- verify_and_apply: persist series_key overrides so suggested merges take effect.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _flatten_families(structured: dict, brand_filter: str | None, limit: int | None) -> list[dict]:
    """From structured items output, flatten to one row per family with hero_image."""
    rows = []
    for b in structured.get("brands", []):
        brand_key = (b.get("brand_key") or "").strip().lower()
        brand_display = (b.get("brand") or brand_key).strip()
        if brand_filter and brand_key != brand_filter.lower():
            continue
        for t in b.get("types", []):
            spectrum_id = t.get("spectrum_id") or "uncategorized"
            for s in t.get("series", []):
                series_key = s.get("series_key") or ""
                for fam in s.get("families", []):
                    hero = (fam.get("hero_image") or "").strip()
                    if not hero:
                        continue
                    rows.append({
                        "brand_key": brand_key,
                        "brand": brand_display,
                        "spectrum_id": spectrum_id,
                        "series_key": series_key,
                        "series_label": s.get("series_label") or series_key,
                        "family_id": fam.get("family_id", ""),
                        "family_name": fam.get("family_name", ""),
                        "hero_image": hero,
                    })
                    if limit and len(rows) >= limit:
                        return rows
    return rows


def _fetch_image_sync(url: str, timeout: float = 10.0) -> bytes | None:
    try:
        import httpx
        with httpx.Client(follow_redirects=True, timeout=timeout) as client:
            r = client.get(url)
            if r.status_code == 200:
                return r.content
    except Exception:
        pass
    return None


def run_visual_grouping_suggest(
    catalog: dict[str, Any],
    *,
    brand: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Classify family hero images with vision AI and suggest series merges.

    Returns:
        classified, with_visual_type, suggested_merges_count, results, suggested_merges
    """
    from backend.structured_items import build_structured_items
    from backend.ingestion.visual_validator import get_visual_validator

    structured = build_structured_items(catalog)
    rows = _flatten_families(structured, brand, limit if limit > 0 else None)
    if not rows:
        return {
            "classified": 0,
            "with_visual_type": 0,
            "suggested_merges_count": 0,
            "results": [],
            "suggested_merges": [],
        }

    validator = get_visual_validator()
    results = []
    for row in rows:
        img_bytes = _fetch_image_sync(row["hero_image"])
        if not img_bytes:
            results.append({
                **row,
                "visual_type": None,
                "visual_type_normalized": None,
                "confidence": 0,
                "error": "Failed to fetch image",
            })
            continue
        out = validator.classify_product_image(
            img_bytes,
            product_name=row.get("family_name") or row.get("family_id"),
            brand=row.get("brand"),
        )
        visual_norm = out.get("visual_type_normalized") or ""
        results.append({
            **row,
            "visual_type": out.get("visual_type"),
            "visual_type_normalized": visual_norm or None,
            "confidence": out.get("confidence", 0),
            "error": out.get("error"),
        })

    by_group: dict[tuple[str, str, str], list[dict]] = {}
    for r in results:
        if not r.get("visual_type_normalized"):
            continue
        key = (r["brand_key"], r["spectrum_id"], r["visual_type_normalized"])
        by_group.setdefault(key, []).append(r)

    suggested_merges = []
    for (brand_key, spectrum_id, visual_norm), group in by_group.items():
        series_keys = {r["series_key"] for r in group}
        if len(series_keys) <= 1:
            continue
        suggested_merges.append({
            "brand_key": brand_key,
            "spectrum_id": spectrum_id,
            "visual_type_normalized": visual_norm,
            "current_series_keys": sorted(series_keys),
            "families": [
                {"family_id": r["family_id"], "family_name": r["family_name"], "series_key": r["series_key"]}
                for r in group
            ],
            "suggestion": f"Merge {len(series_keys)} items into one '{visual_norm}' item",
        })

    return {
        "classified": len(results),
        "with_visual_type": sum(1 for r in results if r.get("visual_type_normalized")),
        "suggested_merges_count": len(suggested_merges),
        "results": results,
        "suggested_merges": suggested_merges,
    }


def _overrides_path() -> Path:
    from backend.project_config import DATA_DIR
    return DATA_DIR / "visual_grouping_overrides.json"


def load_visual_overrides() -> dict[str, str]:
    """Load current family_id -> series_key overrides from disk."""
    path = _overrides_path()
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return dict(data.get("overrides", {}))
    except Exception:
        return {}


def verify_and_apply(
    report: dict[str, Any],
    *,
    min_confidence: float = 0.7,
) -> dict[str, Any]:
    """
    Verify suggested merges (all families in group have confidence >= min_confidence)
    and apply by writing family_id -> visual_type_normalized to visual_grouping_overrides.json.
    Structured items will then group those families under the same series item.
    """
    results_by_fid: dict[str, dict] = {r["family_id"]: r for r in report.get("results", []) if r.get("family_id")}
    suggested = report.get("suggested_merges", [])
    overrides = load_visual_overrides()
    applied: list[dict] = []
    skipped_low_confidence: list[dict] = []

    for merge in suggested:
        target_series = (merge.get("visual_type_normalized") or "").strip()
        if not target_series:
            continue
        families = merge.get("families", [])
        if not families:
            continue
        # Verify: every family in this merge has confidence >= min_confidence
        all_ok = True
        for fam in families:
            fid = fam.get("family_id")
            r = results_by_fid.get(fid) if fid else None
            conf = (r.get("confidence") or 0) if r else 0
            if conf < min_confidence:
                all_ok = False
                skipped_low_confidence.append({"family_id": fid, "confidence": conf, "merge": merge})
                break
        if not all_ok:
            continue
        # Apply: set override for each family to target_series
        for fam in families:
            fid = fam.get("family_id")
            if fid:
                overrides[fid] = target_series
                applied.append({"family_id": fid, "series_key": target_series})

    path = _overrides_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "overrides": overrides,
        "applied_at": datetime.utcnow().isoformat() + "Z",
        "source": "visual_grouping_verify_and_apply",
        "last_applied_count": len(applied),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return {
        "applied": len(applied),
        "overrides_written": len(overrides),
        "applied_families": applied,
        "skipped_low_confidence": skipped_low_confidence,
        "path": str(path),
    }
