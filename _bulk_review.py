#!/usr/bin/env python3
"""One-shot bulk review of all pending evolution proposals."""
from backend.factory.evolution_manager import process_all_pending
import sys
from pathlib import Path
sys.path.insert(0, "/workspaces/Halilit-Support-Center")
_ROOT = Path("/workspaces/Halilit-Support-Center")


results = process_all_pending(max_batch=100)
print(f"\n{'='*60}")
print(f"TOTAL PROCESSED: {len(results)}")
pending_after = list((_ROOT / "specs" / "strategy" / "evolution").glob("*.md"))
reviewed_after = list((_ROOT / "specs" / "strategy" /
                      "evolution" / "reviewed").glob("*.md"))
print(f"Pending remaining: {len(pending_after)}")
print(f"Total reviewed: {len(reviewed_after)}")
