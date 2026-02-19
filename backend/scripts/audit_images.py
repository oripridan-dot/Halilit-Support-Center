#!/usr/bin/env python3
"""
Image Audit Script
==================
Scans all products in frontend/public/data/*.json.
Validates 'image_url' using VisualValidator (heuristic and/or AI).

Usage:
  PYTHONPATH=. python backend/scripts/audit_images.py [--limit N] [--ai]
  PYTHONPATH=. python backend/scripts/audit_images.py --brand nord --ai

  --limit N   Check only first N products (default: all).
  --ai        Use Gemini vision to audit each image (set GOOGLE_API_KEY or GEMINI_API_KEY).
  --brand X   Only products from brand file matching X (e.g. nord, roland).
Run from project root. Requires: httpx, Pillow. For --ai: google-genai, API key.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Project root
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env so GOOGLE_API_KEY / GEMINI_API_KEY are available for AI audit
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

DATA_DIR = PROJECT_ROOT / "frontend" / "public" / "data"


def _load_validator():
    """Load VisualValidator without pulling in full backend.ingestion (avoids pydantic)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "visual_validator",
        BACKEND_DIR / "ingestion" / "visual_validator.py",
        submodule_search_locations=[str(BACKEND_DIR)],
    )
    if spec is None or spec.loader is None:
        raise ImportError("Could not load visual_validator")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["visual_validator"] = mod
    spec.loader.exec_module(mod)
    return mod.get_visual_validator()


def _run_ai_audit(validator, img_bytes: bytes, product_name: str, brand: str):
    """Run sync AI audit in thread (validator.audit_quality_ai is blocking)."""
    return validator.audit_quality_ai(img_bytes, product_name=product_name, brand=brand)


async def audit_catalog(
    limit: int | None,
    use_ai: bool = False,
    brand_filter: str | None = None,
) -> None:
    import asyncio

    validator = _load_validator()
    files = list(DATA_DIR.glob("*.json"))
    files = [f for f in files if not f.stem.startswith("_") and f.stem != "index"]

    if brand_filter:
        brand_lower = brand_filter.lower().replace(" ", "-")
        files = [f for f in files if brand_lower in f.stem.lower().replace(" ", "-")]
        if not files:
            print(f"No brand files matching '{brand_filter}'.")
            return
        print(f"Brand filter: {brand_filter} ({len(files)} file(s))")

    limit_msg = f" (first {limit} products)" if limit else ""
    ai_msg = " [AI audit]" if use_ai else ""
    print(f"Scanning {len(files)} brand files for image issues{limit_msg}{ai_msg}...")

    report: dict = {"missing": [], "low_quality": [], "placeholders": [], "ok": 0}
    checked = 0
    loop = asyncio.get_event_loop()

    for f in files:
        if limit is not None and checked >= limit:
            break
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            products = data if isinstance(data, list) else data.get("products", [])
            if not isinstance(products, list):
                continue

            for p in products:
                if limit is not None and checked >= limit:
                    break
                checked += 1
                url = p.get("image_url")
                name = p.get("name") or p.get("id") or "?"
                brand = p.get("brand") or ""

                if not url:
                    report["missing"].append(f"{name} (no URL)")
                    continue

                img_bytes, _ = await validator.fetch_image(url)
                if not img_bytes:
                    report["missing"].append(f"{name} (broken URL)")
                    continue

                if use_ai:
                    quality = await loop.run_in_executor(
                        None,
                        (lambda v, b, n, br: lambda: _run_ai_audit(v, b, n, br))(
                            validator, img_bytes, name, brand
                        ),
                    )
                    issues = quality.get("ai_issues") or quality.get("issues") or []
                    if quality.get("is_placeholder"):
                        report["placeholders"].append(f"{name}: AI marked as placeholder")
                    if quality.get("status") == "fail":
                        report["low_quality"].append(
                            f"{name}: {'; '.join(issues) or quality.get('ai_verdict', '')}"
                        )
                    else:
                        report["ok"] += 1
                else:
                    quality = validator.validate_quality(img_bytes, purpose="hero")
                    if quality.get("status") == "fail":
                        issues = ", ".join(quality.get("issues", []))
                        report["low_quality"].append(f"{name}: {issues}")
                    else:
                        report["ok"] += 1

        except Exception as e:
            print(f"Error reading {f}: {e}")

    print("\nAUDIT REPORT" + (" (AI)" if use_ai else ""))
    print(f"  Missing/Broken: {len(report['missing'])}")
    print(f"  Low quality:    {len(report['low_quality'])}")
    print(f"  Placeholders:   {len(report['placeholders'])}")
    print(f"  OK:             {report['ok']}")

    if report["missing"]:
        print("\nSample missing/broken (first 10):")
        for issue in report["missing"][:10]:
            print(f"  - {issue}")

    if report["placeholders"]:
        print("\nSample placeholders (first 10):")
        for issue in report["placeholders"][:10]:
            print(f"  - {issue}")

    if report["low_quality"]:
        print("\nSample low quality (first 10):")
        for issue in report["low_quality"][:10]:
            print(f"  - {issue}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit product image URLs in catalog JSON.")
    parser.add_argument("--limit", type=int, default=None, help="Max number of products to check")
    parser.add_argument("--ai", action="store_true", help="Use Gemini vision to audit each image")
    parser.add_argument("--brand", type=str, default=None, help="Only audit products from this brand (e.g. nord)")
    args = parser.parse_args()

    if not DATA_DIR.exists():
        print(f"Data directory not found: {DATA_DIR}")
        print("Run from project root.")
        return 1
    asyncio.run(
        audit_catalog(
            limit=args.limit,
            use_ai=args.ai,
            brand_filter=args.brand,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
