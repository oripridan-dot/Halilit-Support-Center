#!/usr/bin/env python3
"""
Purge weak relationships from the persisted product graph snapshot.

Keeps only strict catalog tiers:
  - variant_of
  - accessory_for
  - alternative_to

Removes: compatible_with, successor_of, bundle_with (and any other types).

Usage:
  PYTHONPATH=. python backend/scripts/purge_weak_graph_relationships.py

After running, the next catalog load will use the cleaned graph overlay.
For a full rebuild (brand hierarchy + discovery + purge), use:
  PYTHONPATH=. python backend/conductor_main.py rebuild-catalog
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Project root
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

GRAPH_DATA_DIR = BACKEND_DIR / "data" / "graph"
SNAPSHOT_PATH = GRAPH_DATA_DIR / "product_graph.json"

ALLOWED_TYPES = {"variant_of", "accessory_for", "alternative_to"}


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
    kept = [r for r in relationships if (r.get("relationship_type") or "").lower() in ALLOWED_TYPES]
    removed = before - len(kept)

    if removed == 0:
        print("No weak relationships to purge.")
        return 0

    snapshot["relationships"] = kept
    snapshot["exported_at"] = datetime.utcnow().isoformat()
    if "stats" in snapshot and isinstance(snapshot["stats"], dict):
        snapshot["stats"]["total_relationships"] = len(kept)

    backup = GRAPH_DATA_DIR / f"product_graph_pre_purge_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    SNAPSHOT_PATH.rename(backup)
    with open(SNAPSHOT_PATH, "w") as f:
        json.dump(snapshot, f, indent=2, default=str)

    print(f"Purged {removed} weak relationship(s). Kept {len(kept)} (variant_of, accessory_for, alternative_to).")
    print(f"Backup: {backup}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
