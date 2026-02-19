#!/usr/bin/env python3
"""
Purge weak relationships from the persisted product graph snapshot.

1. Keeps only strict catalog tiers: variant_of, accessory_for, alternative_to.
   Removes: compatible_with, successor_of, bundle_with (and any other types).

2. Of the kept types, removes low-confidence unverified edges:
   - If confidence < CONFIDENCE_THRESHOLD AND not verified by Official source AND not manually_curated → delete.
   Better to show 3 perfect accessories than 20 maybe-accessories.

Usage:
  PYTHONPATH=. python backend/scripts/purge_weak_graph_relationships.py

After running, the next catalog load will use the cleaned graph overlay.
For a full rebuild (brand hierarchy + discovery + purge), use:
  PYTHONPATH=. python backend/conductor_main.py rebuild-catalog
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Project root
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

GRAPH_DATA_DIR = BACKEND_DIR / "data" / "graph"
SNAPSHOT_PATH = GRAPH_DATA_DIR / "product_graph.json"

ALLOWED_TYPES = {"variant_of", "accessory_for", "alternative_to"}
# Very high confidence: keep only 0.9+ or verified. Lower to 0.8 to retain more "likely" matches.
CONFIDENCE_THRESHOLD = 0.9
OFFICIAL_VERIFIED_SOURCES = {"official", "official_text_match", "official_url_match"}


def _is_verified(r: dict) -> bool:
    """True if relationship was verified by official source or human."""
    if r.get("manually_curated"):
        return True
    sources = r.get("sources_verified") or []
    return any(s in OFFICIAL_VERIFIED_SOURCES for s in sources)


def _keep_relationship(r: dict) -> bool:
    rel_type = (r.get("relationship_type") or "").lower()
    if rel_type not in ALLOWED_TYPES:
        return False
    confidence = float(r.get("confidence", 0))
    if confidence >= CONFIDENCE_THRESHOLD:
        return True
    if _is_verified(r):
        return True
    return False


def main() -> int:
    if not SNAPSHOT_PATH.exists():
        print(f"No graph snapshot at {SNAPSHOT_PATH}")
        print("Run rebuild-catalog first: PYTHONPATH=. python backend/conductor_main.py rebuild-catalog")
        return 1

    with open(SNAPSHOT_PATH) as f:
        snapshot = json.load(f)

    relationships = snapshot.get("relationships", [])
    if not isinstance(relationships, list):
        print("Unexpected relationships format")
        return 1

    before = len(relationships)
    kept = [r for r in relationships if _keep_relationship(r)]
    removed = before - len(kept)

    if removed == 0:
        print("No weak relationships to purge.")
        return 0

    snapshot["relationships"] = kept
    snapshot["exported_at"] = datetime.now(timezone.utc).isoformat()
    if "stats" in snapshot and isinstance(snapshot["stats"], dict):
        snapshot["stats"]["total_relationships"] = len(kept)

    backup = GRAPH_DATA_DIR / f"product_graph_pre_purge_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    SNAPSHOT_PATH.rename(backup)
    with open(SNAPSHOT_PATH, "w") as f:
        json.dump(snapshot, f, indent=2, default=str)

    print(f"Purged {removed} weak relationship(s). Kept {len(kept)} (variant_of, accessory_for, alternative_to; confidence >= {CONFIDENCE_THRESHOLD} or verified).")
    print(f"Backup: {backup}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
