#!/usr/bin/env python3
"""
Pre-build catalog cache to avoid slow first load in the browser.

Writes backend/data/catalog_cache.json.gz so the server can load it
immediately instead of building from scratch (2–5 min).

Run once after ingest or when cache is missing/stale:

    PYTHONPATH=. python backend/scripts/prebuild_catalog_cache.py

Then start the backend — first catalog request will be fast.
"""

import gzip
import json
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

STRIP_FIELDS = {"search_text", "subcategory", "currency"}


def main():
    from backend.product_normalizer import build_catalog
    from backend.project_config import FRONTEND_PUBLIC_DATA, DATA_DIR

    data_dir = Path(FRONTEND_PUBLIC_DATA)
    if not data_dir.exists():
        print("❌ Data directory not found:", data_dir)
        return 1

    t0 = time.time()

    def on_progress(step: str, pct: float, msg: str) -> None:
        elapsed = int(time.time() - t0)
        bar_len = 24
        filled = int(bar_len * pct)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\r  [{bar}] {pct*100:5.1f}% {msg} ({elapsed}s)  ", end="", flush=True)
        if pct >= 1.0:
            print()

    print("Building catalog (7,000+ products)...")
    catalog = build_catalog(
        str(FRONTEND_PUBLIC_DATA),
        resolve=False,
        on_progress=on_progress,
    )

    for p in catalog["products"]:
        for f in STRIP_FIELDS:
            p.pop(f, None)
    catalog["metadata"]["timestamp"] = datetime.now().isoformat()

    path = DATA_DIR / "catalog_cache.json.gz"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    json_bytes = json.dumps(catalog, ensure_ascii=False).encode("utf-8")
    with gzip.open(path, "wb", compresslevel=6) as f:
        f.write(json_bytes)

    elapsed = int(time.time() - t0)
    n = catalog["metadata"]["total_products"]
    print(f"✅ Done in {elapsed}s. {n} products → {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
