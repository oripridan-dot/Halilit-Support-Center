#!/usr/bin/env python3
"""
Build Skeleton Inventory (Phase 0 — Clean Slate)

Runs nightly or on-demand. Scrapes Halilit sitemap and builds a single
lightweight inventory.json with Tier 1 data only. JIT fills in the rest on demand.

Output: frontend/public/data/inventory.json
Fields per product: id, name, brand, price, image_url, halilit_url, status, spectrum_id.

Usage:
  PYTHONPATH=. python backend/scripts/build_skeleton.py
  PYTHONPATH=. python backend/scripts/build_skeleton.py --limit 100   # quick test
  PYTHONPATH=. python backend/scripts/build_skeleton.py --scrape      # fetch og:image + price (slower)
"""

import json
import re
import sys
from pathlib import Path

# Project root
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

OUTPUT_FILE = PROJECT_ROOT / "frontend" / "public" / "data" / "inventory.json"
HALILIT_BASE = "https://www.halilit.com"


def _generate_id(url: str) -> str:
    """Stable product ID matching catalog format (halilit-{numeric}) for JIT lookup."""
    m = re.search(r"/items/(\d+)", url)
    if m:
        return "halilit-" + m.group(1)
    # Fallback: hash of path
    path = url.split("/items/")[-1].split("?")[0]
    return "halilit-" + (path.replace("-", "_")[:24] if path else "unknown")


def _extract_name_and_brand_from_url(url: str) -> tuple[str, str]:
    """Parse slug after /items/ to get name and brand. e.g. 2276780-adam-audio-t5v -> Adam Audio, T5V."""
    slug = url.split("/items/")[-1].split("?")[0].strip()
    if not slug:
        return "Unknown", "Other"
    # Remove leading digits and dash (e.g. 2276780-adam-audio-t5v)
    rest = re.sub(r"^\d+-", "", slug)
    parts = rest.split("-")
    if len(parts) >= 2:
        # Last part often model (t5v, fp-30x); rest is brand
        brand_parts = parts[:-1]
        model = parts[-1]
        brand = " ".join(p.capitalize() for p in brand_parts)
        name = f"{brand} {model.upper()}" if model.isalnum() else rest.replace("-", " ").title()
        return brand, name
    name = rest.replace("-", " ").title()
    return "Other", name


def _predict_spectrum(name: str, brand: str) -> str:
    """Lightweight spectrum prediction (keyword fallback). For full accuracy use product_normalizer.classify_product."""
    try:
        from backend.product_normalizer import classify_product
        spectrum_id, _ = classify_product(name, brand, "", {})
        return spectrum_id or "general-accessories"
    except Exception:
        pass
    text = f" {name.lower()} {brand.lower()} "
    if "piano" in text or "keyboard" in text or "synth" in text or "stage" in text or "nord" in text:
        return "digital-pianos-keyboards"
    if "guitar" in text or "strat" in text or "bass" in text:
        return "guitars-basses"
    if "microphone" in text or "mic" in text:
        return "microphones"
    if "monitor" in text or "speaker" in text:
        return "studio-monitors"
    if "interface" in text or "audio" in text:
        return "audio-interfaces"
    return "general-accessories"


def _fast_scrape_product(url: str, requests_get) -> dict | None:
    """Fetch one page and extract only og:image, title, and price from meta/JSON-LD. Returns None on failure."""
    try:
        resp = requests_get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (compatible; HalilitSkeleton/1.0)"})
        if resp.status_code != 200:
            return None
        html = resp.text
        result = {}
        # og:image
        m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
        if m:
            result["image_url"] = m.group(1).strip()
        # title
        m = re.search(r"<title>([^<]+)</title>", html, re.I)
        if m:
            result["title"] = m.group(1).strip()
        # price from JSON-LD (schema.org)
        m = re.search(r'"price"\s*:\s*["\']?([\d.]+)', html)
        if m:
            try:
                result["price"] = float(m.group(1))
            except ValueError:
                pass
        return result if result else None
    except Exception:
        return None


def build_skeleton(limit: int | None = None, scrape: bool = False) -> list[dict]:
    """Build skeleton inventory from sitemap. Returns list of product dicts."""
    from backend.ingestion.halilit_page_scraper import HalilitPageScraper

    print("Building Skeleton Inventory...")
    scraper = HalilitPageScraper()
    urls = scraper.scrape_all_product_urls_from_sitemap()
    if limit:
        urls = urls[:limit]
        print(f"  (limited to {limit} URLs)")

    inventory = []
    requests_get = getattr(scraper, "_get", None)
    if scrape and requests_get:
        try:
            import requests
            requests_get = requests.get
        except ImportError:
            requests_get = None
    if not scrape:
        requests_get = None

    for i, url in enumerate(urls):
        if not url or "/items/" not in url:
            continue
        pid = _generate_id(url)
        brand, name = _extract_name_and_brand_from_url(url)
        spectrum_id = _predict_spectrum(name, brand)

        product = {
            "id": pid,
            "name": name,
            "brand": brand,
            "price": 0,
            "image_url": "",
            "halilit_url": url,
            "status": "in_stock",
            "spectrum_id": spectrum_id,
        }

        if requests_get and scrape:
            extra = _fast_scrape_product(url, requests_get)
            if extra:
                if extra.get("image_url"):
                    product["image_url"] = extra["image_url"]
                if extra.get("price"):
                    product["price"] = extra["price"]
                if extra.get("title"):
                    product["name"] = extra["title"][:200]

        inventory.append(product)
        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{len(urls)}...")

    return inventory


def build_skeleton_from_catalog(limit: int | None = None, brand_filter: str | None = None) -> list[dict]:
    """Build skeleton from existing frontend/public/data/*.json brand files (no sitemap)."""
    data_dir = PROJECT_ROOT / "frontend" / "public" / "data"
    files = list(data_dir.glob("*.json"))
    files = [f for f in files if not f.stem.startswith("_") and f.stem not in ("index", "inventory", "galaxy_db", "search_index_min", "sample")]
    if brand_filter:
        b = brand_filter.lower().replace(" ", "")
        files = [f for f in files if b in f.stem.lower().replace(" ", "")]
    inventory = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            products = data if isinstance(data, list) else data.get("products", [])
            if not isinstance(products, list):
                continue
            for p in products:
                pid = p.get("halilit_id") or p.get("id") or ""
                if not pid:
                    continue
                name = p.get("product_name") or p.get("name") or p.get("official_name") or ""
                brand = (p.get("brand") or "").strip()
                if isinstance(brand, str) and brand:
                    brand = brand.replace("-", " ").title()
                halilit_url = p.get("halilit_url") or ""
                image_url = p.get("image_url") or (p.get("image_hero") or {}).get("url") if isinstance(p.get("image_hero"), dict) else ""
                if not image_url and isinstance(p.get("image_gallery"), list) and p["image_gallery"]:
                    image_url = p["image_gallery"][0]
                price = float(p.get("price_il") or p.get("price") or 0)
                spectrum_id = _predict_spectrum(name, brand)
                inventory.append({
                    "id": str(pid),
                    "name": name,
                    "brand": brand,
                    "price": price,
                    "image_url": image_url or "",
                    "halilit_url": halilit_url,
                    "status": "in_stock",
                    "spectrum_id": spectrum_id,
                })
                if limit and len(inventory) >= limit:
                    break
        except Exception as e:
            print(f"  Skip {f.name}: {e}")
        if limit and len(inventory) >= limit:
            break
    return inventory


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Build skeleton inventory from Halilit sitemap or from catalog JSONs.")
    parser.add_argument("--limit", type=int, default=None, help="Max number of products (for testing)")
    parser.add_argument("--scrape", action="store_true", help="Fetch each page for og:image and price (slower)")
    parser.add_argument("--from-catalog", action="store_true", help="Build from existing frontend/public/data/*.json (no sitemap)")
    parser.add_argument("--brand", type=str, default=None, help="With --from-catalog: only this brand (e.g. nord)")
    args = parser.parse_args()

    if args.from_catalog:
        print("Building skeleton from catalog JSONs...")
        inventory = build_skeleton_from_catalog(limit=args.limit, brand_filter=args.brand)
    else:
        inventory = build_skeleton(limit=args.limit, scrape=args.scrape)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Output shape: { "products": [...], "built_at": "...", "count": N }
    from datetime import datetime, timezone
    payload = {
        "products": inventory,
        "count": len(inventory),
        "built_at": datetime.now(timezone.utc).isoformat(),
    }
    OUTPUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"Skeleton built: {len(inventory)} items. Written to {OUTPUT_FILE} ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
