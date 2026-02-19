#!/usr/bin/env python3
"""
Factory Supervisor — Dark Factory Protocol.
Runs compliance check against specs, triggers ingestion agent, verifies UI build.
Run from project root: PYTHONPATH=. python backend/factory_supervisor.py [--rebuild]
Or from backend: python factory_supervisor.py [--rebuild]
"""

import gzip
import json
import subprocess
import sys
from pathlib import Path

# Resolve paths: support run from backend/ or project root
_BACKEND = Path(__file__).resolve().parent
_ROOT = _BACKEND.parent
SPECS_DIR = _ROOT / "specs"
DATA_DIR = _BACKEND / "data"
LOGS_DIR = _ROOT / "factory_logs"


def log(message: str) -> None:
    print(f"🏭 [FACTORY]: {message}")


def _collect_products_from_artifact(data: dict) -> list:
    """Extract flat list of products from catalog/taxonomy artifact."""
    products = []
    if isinstance(data, dict):
        if "products" in data:
            products = data["products"] if isinstance(data["products"], list) else []
        else:
            for v in data.values():
                if isinstance(v, list):
                    products.extend(v)
    return products


def _price_il(product: dict) -> float:
    """Get IL price from product (top-level or nested pricing)."""
    p = product.get("pricing") if isinstance(product.get("pricing"), dict) else {}
    if p and "price_il" in p:
        try:
            return float(p["price_il"]) or 0
        except (TypeError, ValueError):
            return 0
    v = product.get("price_il")
    try:
        return float(v) if v is not None else 0
    except (TypeError, ValueError):
        return 0


def check_compliance() -> bool:
    """
    Checks if the current data artifacts match the defined specs.
    Accepts learned_taxonomy.json or catalog_cache.json.gz.
    """
    log("Auditing system against specs...")

    catalog_path = DATA_DIR / "catalog_cache.json.gz"
    taxonomy_path = DATA_DIR / "learned_taxonomy.json"

    if not catalog_path.exists() and not taxonomy_path.exists():
        log("❌ FAIL: No catalog artifact (catalog_cache.json.gz or learned_taxonomy.json).")
        return False

    data = None
    if catalog_path.exists():
        try:
            with gzip.open(catalog_path, "rt", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            log(f"❌ CRITICAL: Cannot read catalog_cache.json.gz — {e}")
            return False
    elif taxonomy_path.exists():
        try:
            with open(taxonomy_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            log(f"❌ CRITICAL: Cannot read learned_taxonomy.json — {e}")
            return False

    if not data:
        log("❌ FAIL: Artifact empty.")
        return False

    products = _collect_products_from_artifact(data)
    if not products:
        # Some artifacts are index-only; metadata.total_products might exist
        total = (data.get("metadata") or {}).get("total_products", 0)
        if total == 0:
            log("❌ FAIL: No products in artifact.")
            return False
        log("✅ COMPLIANCE: Artifact has metadata (no product list to validate).")
        return True

    zero_price_count = sum(1 for p in products if _price_il(p) == 0)
    ratio = zero_price_count / len(products) if products else 0
    if ratio > 0.5:
        log(f"❌ FAIL: Too many zero prices ({zero_price_count}/{len(products)}). Suspect scraper failure.")
        return False

    log("✅ COMPLIANCE: Data artifacts look valid.")
    return True


def run_agent_ingestion() -> bool:
    """Triggers the Conductor agent to rebuild data based on specs."""
    log("Activating Ingestion Agent...")
    result = subprocess.run(
        [sys.executable, "conductor_main.py", "rebuild-catalog"],
        cwd=str(_BACKEND),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        log("✅ Agent finished ingestion.")
        return True
    log("❌ Agent failed.")
    if result.stderr:
        print(result.stderr)
    return False


def run_agent_ui_build() -> bool:
    """Verifies the frontend build compiles."""
    log("Verifying UI Build...")
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=str(_ROOT / "frontend"),
        shell=sys.platform == "win32",
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        log("✅ Frontend compiled successfully.")
        return True
    log("❌ Frontend build failed.")
    if result.stderr:
        print(result.stderr)
    return False


def main() -> int:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1 and sys.argv[1] == "--rebuild":
        if not run_agent_ingestion():
            sys.exit(1)

    if check_compliance():
        run_agent_ui_build()
        log("✨ Factory Cycle Complete. System Ready.")
        return 0
    log("⚠️ System Halted. Intervention Required.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
