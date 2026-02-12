#!/usr/bin/env python3
"""
Sitemap-Based Golden List Builder
==================================
Builds the complete Golden List by:
1. Discovering all brands from Halilit.com's brands page (no anti-bot)
2. Extracting ALL product URLs from the sitemap (no anti-bot)
3. Matching products to brands via URL slug analysis
4. Attempting page scrapes with anti-bot detection + retry/backoff
5. Merging with existing enriched data from frontend JSON files
6. Saving complete brand JSON files

This bypasses Konimbo's anti-bot (page_no_referer) by:
- Using the sitemap (always accessible, no referrer check)
- Using brands page (always accessible)
- Trying product pages individually with backoff
- Falling back to URL-derived data when pages are blocked

Usage:
    PYTHONPATH=. python3 backend/scripts/full_rescrape.py
    PYTHONPATH=. python3 backend/scripts/full_rescrape.py --brand "Boss"
    PYTHONPATH=. python3 backend/scripts/full_rescrape.py --dry-run
    PYTHONPATH=. python3 backend/scripts/full_rescrape.py --sitemap-only
    PYTHONPATH=. python3 backend/scripts/full_rescrape.py --resume
"""

from backend.ingestion.halilit_page_scraper import (
    HalilitPageScraper,
    extract_model_name,
    extract_model_number,
)
import argparse
import hashlib
import json
import logging
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


# ── Logging ───────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("golden_list_builder")

# ── Paths ─────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = ROOT / "frontend" / "public" / "data"
BACKUP_DIR = ROOT / "backend" / "data" / "ingestion" / "rescrape_backups"
PROGRESS_FILE = ROOT / "backend" / "data" / \
    "ingestion" / "rescrape_progress.json"

# ── Anti-bot detection ────────────────────────────────────────────────────
ANTI_BOT_MARKERS = ["page_no_referer", "limit_no_referer"]
ANTI_BOT_MAX_SIZE = 2000  # The blocker page is ~1648 bytes


def is_anti_bot_page(html: str) -> bool:
    """Detect Konimbo's anti-bot referrer check page."""
    if len(html) > ANTI_BOT_MAX_SIZE:
        return False
    return any(marker in html for marker in ANTI_BOT_MARKERS)


# ═══════════════════════════════════════════════════════════════════════════
# BRAND-URL MATCHING
# ═══════════════════════════════════════════════════════════════════════════

# Additional brand slugs not discoverable from the brands page
# These are brands whose products appear in the sitemap but aren't
# listed on the /pages/4367 brands page
EXTRA_BRAND_SLUGS = {
    "rode": "RODE",
    "novation": "Novation",
    "teenage": "Teenage Engineering",
    "marshall": "Marshall",
    "beyerdynamic": "Beyerdynamic",
    "promark": "ProMark",
    "sequential": "Sequential",
    "moog": "Moog",
    "kinsman": "Kinsman",
    "atv": "ATV",
    "aston": "Aston Microphones",
    "fender": "Fender",
    "vicoustic": "Vicoustic",
    "rico": "Rico",
    "mtd": "MTD",
    "paiste": "Paiste",
    "martin": "Martin",
}


def build_brand_patterns(brands: List[Dict]) -> List[Tuple[str, str]]:
    """Build URL slug -> brand name matching patterns."""
    patterns = []
    seen_slugs = set()

    # From discovered brands
    for b in brands:
        name = b["name"].lower()
        full_slug = re.sub(r"[^a-z0-9]+", "-", name).strip("-")
        if full_slug not in seen_slugs:
            patterns.append((full_slug, b["name"]))
            seen_slugs.add(full_slug)

        # Add first-word variant for multi-word brands
        words = name.split()
        if len(words) > 1:
            short = re.sub(r"[^a-z0-9]+", "-", words[0]).strip("-")
            if len(short) >= 3 and short not in seen_slugs:
                patterns.append((short, b["name"]))
                seen_slugs.add(short)

    # Add extra brand slugs
    for slug, brand_name in EXTRA_BRAND_SLUGS.items():
        if slug not in seen_slugs:
            patterns.append((slug, brand_name))
            seen_slugs.add(slug)

    # Sort by length descending for longest-match-first
    patterns.sort(key=lambda x: -len(x[0]))
    return patterns


def match_url_to_brand(url: str, patterns: List[Tuple[str, str]]) -> Optional[str]:
    """Match a product URL to a brand name using slug patterns."""
    m = re.search(r"/items/\d+-(.+)$", url)
    if not m:
        return None
    product_slug = m.group(1).lower()

    for pattern, brand_name in patterns:
        if product_slug.startswith(pattern):
            return brand_name
    return None


def slugify(name: str) -> str:
    """Convert brand name to filename slug."""
    return re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()


def product_name_from_url(url: str, brand: str) -> str:
    """Extract a human-readable product name from the URL slug."""
    m = re.search(r"/items/\d+-(.+)$", url)
    if not m:
        return ""
    slug = m.group(1)
    # Convert slug to name: replace dashes with spaces, title-case
    name = slug.replace("-", " ").strip()
    # Clean up trailing/leading punctuation and extra whitespace
    name = re.sub(r"\s+", " ", name).strip()
    # Title-case but preserve known acronyms
    parts = name.split()
    result = []
    for p in parts:
        if p.upper() == p and len(p) <= 5:  # Keep acronyms uppercase
            result.append(p.upper())
        else:
            result.append(p.capitalize())
    return " ".join(result)


def halilit_id_from_url(url: str) -> str:
    """Generate a stable halilit_id from a URL."""
    m = re.search(r"/items/(\d+)", url)
    if m:
        return f"halilit-{m.group(1)}"
    return f"scraped-{hashlib.md5(url.encode()).hexdigest()[:16]}"


# ═══════════════════════════════════════════════════════════════════════════
# PRODUCT DATA BUILDING
# ═══════════════════════════════════════════════════════════════════════════

def build_product_from_url(url: str, brand: str) -> Dict:
    """Build a minimal product entry from just the URL."""
    name = product_name_from_url(url, brand)
    model = extract_model_name(name, brand)
    model_number = extract_model_number(model, brand)

    return {
        "halilit_id": halilit_id_from_url(url),
        "product_name": name,
        "official_name": model,
        "model_number": model_number,
        "brand": brand.lower(),
        "sku": None,
        "price_il": 0.0,
        "price_eilat": 0.0,
        "description": "",
        "page_description": "",
        "image_url": "",
        "image_gallery": [],
        "official_images": [],
        "features": [],
        "faq": [],
        "audiences": [],
        "halilit_url": url,
        "source": "sitemap",
        "_data_source": "sitemap_url",
    }


def try_scrape_product(scraper: HalilitPageScraper, url: str) -> Optional[Dict]:
    """
    Attempt to scrape a product page. Returns None if blocked by anti-bot.
    """
    try:
        resp = scraper._get(url)
        if resp is None:
            return None
        if is_anti_bot_page(resp.text):
            return None  # Blocked
        return scraper.scrape_product_page(url)
    except Exception as e:
        logger.debug(f"Scrape failed for {url}: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# MERGE LOGIC
# ═══════════════════════════════════════════════════════════════════════════

# Fields we preserve from existing enriched data
ENRICHED_FIELDS = [
    "official_description", "official_specs", "official_url",
    "reviews", "review_synthesis", "average_rating",
    "taxonomy", "specifications", "description_short", "description_long",
    "feature_list", "sources", "primary_source", "lineage",
    "data_completeness", "quality_score", "validation_status",
    "source_coverage_official", "source_coverage_contextual",
    "contextual_source_count", "cross_validation_confidence",
    "cross_validation_status", "review_sources", "review_pros",
    "review_cons", "user_sentiment", "real_world_insights",
    "contextual_data", "status", "pipeline_phase",
    "created_at", "last_updated", "pricing", "display",
    "raw_snapshot", "validation_errors", "validation_warnings",
    "price", "currency", "brand_logo", "image_hero",
    "image_thumbnail",
]

# Fields from scraped page data that should override existing
SCRAPED_OVERRIDE_FIELDS = [
    "price_il", "price_eilat", "image_url", "image_gallery",
    "official_images", "description", "page_description",
    "features", "faq", "audiences", "sku", "model_number",
]


def load_existing_products(slug: str) -> Dict[str, Dict]:
    """Load existing products indexed by URL and name."""
    existing_file = OUTPUT_DIR / f"{slug}.json"
    if not existing_file.exists():
        return {}

    try:
        with open(existing_file) as f:
            data = json.load(f)
        if not isinstance(data, list):
            return {}
    except (json.JSONDecodeError, Exception):
        return {}

    index = {}
    for p in data:
        url = p.get("halilit_url", "")
        if url and url != "https://halilit.com":
            index[url] = p
        name = (p.get("product_name") or p.get("name") or "").lower().strip()
        if name and name not in index:
            index[f"name:{name}"] = p
    return index


def merge_product(new_p: Dict, existing_index: Dict) -> Dict:
    """Merge new product data with existing enriched data."""
    url = new_p.get("halilit_url", "")
    name = (new_p.get("product_name") or "").lower().strip()

    old = existing_index.get(url) or existing_index.get(f"name:{name}")
    if not old:
        return new_p

    # Start with new data (fresh from scrape/sitemap)
    merged = dict(new_p)

    # If new data is URL-only (sitemap source), pull commercial fields from old
    if new_p.get("_data_source") == "sitemap_url":
        for field in SCRAPED_OVERRIDE_FIELDS:
            if old.get(field):
                merged[field] = old[field]

    # Always preserve enriched fields from old data
    for field in ENRICHED_FIELDS:
        if old.get(field):
            merged[field] = old[field]

    return merged


# ═══════════════════════════════════════════════════════════════════════════
# PROGRESS TRACKING
# ═══════════════════════════════════════════════════════════════════════════

def load_progress() -> Dict:
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"completed_brands": [], "started_at": None}


def save_progress(progress: Dict):
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def backup_existing(slug: str):
    src = OUTPUT_DIR / f"{slug}.json"
    if src.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        dst = BACKUP_DIR / f"{slug}_{ts}.json"
        shutil.copy2(src, dst)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Sitemap-based Golden List builder")
    parser.add_argument("--brand", type=str, help="Process a single brand")
    parser.add_argument("--dry-run", action="store_true",
                        help="Count only, don't write files")
    parser.add_argument("--sitemap-only", action="store_true",
                        help="Build from sitemap URLs only, don't attempt page scrapes")
    parser.add_argument("--try-scrape", action="store_true",
                        help="Attempt to scrape individual product pages (slow, may be blocked)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from last saved progress")
    parser.add_argument("--scrape-delay", type=float, default=2.0,
                        help="Delay between page scrape attempts (seconds)")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 70)
    logger.info("  GOLDEN LIST BUILDER — Sitemap-Based Full Inventory")
    logger.info("=" * 70)

    scraper = HalilitPageScraper()

    # ── Step 1: Discover all brands ────────────────────────────────────
    logger.info("\nStep 1: Discovering all brands from Halilit.com...")
    brands = scraper.discover_all_brands()
    logger.info(f"  -> {len(brands)} brands discovered from brands page")

    brand_patterns = build_brand_patterns(brands)
    logger.info(
        f"  -> {len(brand_patterns)} matching patterns built (inc. extra brands)")

    # ── Step 2: Get ALL product URLs from sitemap ──────────────────────
    logger.info("\nStep 2: Scanning all sitemap pages for product URLs...")
    all_urls = scraper.scrape_all_product_urls_from_sitemap()
    logger.info(f"  -> {len(all_urls)} product URLs found in sitemap")

    # ── Step 3: Match URLs to brands ───────────────────────────────────
    logger.info("\nStep 3: Matching products to brands...")
    brand_urls: Dict[str, List[str]] = {}
    unmatched_urls: List[str] = []

    for url in all_urls:
        brand_name = match_url_to_brand(url, brand_patterns)
        if brand_name:
            brand_urls.setdefault(brand_name, []).append(url)
        else:
            unmatched_urls.append(url)

    matched_count = sum(len(v) for v in brand_urls.values())
    logger.info(
        f"  -> {matched_count} products matched to {len(brand_urls)} brands")
    logger.info(
        f"  -> {len(unmatched_urls)} products unmatched (will be in 'other' brand)")

    if unmatched_urls:
        brand_urls["Other"] = unmatched_urls

    # ── Filter for single brand if requested ───────────────────────────
    if args.brand:
        target = args.brand.lower().strip()
        filtered = {k: v for k, v in brand_urls.items()
                    if k.lower() == target or slugify(k) == target}
        if not filtered:
            logger.error(
                f"Brand '{args.brand}' not found. Available: {sorted(brand_urls.keys())[:20]}")
            return 1
        brand_urls = filtered
        logger.info(f"\n  Single brand mode: {list(brand_urls.keys())[0]}")

    # ── Resume support ─────────────────────────────────────────────────
    progress = load_progress() if args.resume else {
        "completed_brands": [], "started_at": None}
    if not progress.get("started_at"):
        progress["started_at"] = datetime.now(timezone.utc).isoformat()

    completed_set = set(progress.get("completed_brands", []))
    if args.resume and completed_set:
        before = len(brand_urls)
        brand_urls = {k: v for k, v in brand_urls.items() if slugify(k)
                      not in completed_set}
        logger.info(
            f"  Resuming — skipping {before - len(brand_urls)} completed brands")

    # ── Step 4: Process each brand ─────────────────────────────────────
    logger.info(f"\nStep 4: Processing {len(brand_urls)} brands...")

    all_stats = []
    total_products = 0
    total_scraped = 0
    total_from_url = 0
    total_merged = 0
    start_time = time.time()

    sorted_brands = sorted(brand_urls.items(), key=lambda x: -len(x[1]))

    for i, (brand_name, urls) in enumerate(sorted_brands, 1):
        slug = slugify(brand_name)
        logger.info(
            f"\n[{i}/{len(sorted_brands)}] {brand_name} ({len(urls)} from sitemap)")

        # Load existing data for this brand
        existing_index = load_existing_products(slug)
        existing_url_count = len(
            [k for k in existing_index if not k.startswith("name:")])

        products = []
        scraped_count = 0
        url_only_count = 0
        merged_count = 0

        # Check if anti-bot is blocking (test first URL)
        anti_bot_active = True
        if args.try_scrape and not args.sitemap_only:
            test_product = try_scrape_product(scraper, urls[0])
            if test_product:
                anti_bot_active = False
                logger.info(f"  Pages accessible — scraping product details")
            else:
                logger.info(
                    f"  Anti-bot active — using URL data + existing enrichment")

        for url in urls:
            product = None

            # Try page scrape if not blocked
            if args.try_scrape and not args.sitemap_only and not anti_bot_active:
                product = try_scrape_product(scraper, url)
                if product:
                    scraped_count += 1
                    time.sleep(args.scrape_delay)
                else:
                    anti_bot_active = True

            # Fall back to URL-derived data
            if product is None:
                product = build_product_from_url(url, brand_name)
                url_only_count += 1

            # Merge with existing enriched data
            merged = merge_product(product, existing_index)
            if merged is not product:
                merged_count += 1

            products.append(merged)

        # Add existing products not in sitemap (keep enriched data)
        sitemap_urls = set(urls)
        for key, old_p in existing_index.items():
            if key.startswith("name:"):
                continue
            if key not in sitemap_urls:
                old_p["_possibly_delisted"] = True
                products.append(old_p)

        stats = {
            "brand": brand_name, "slug": slug,
            "total": len(products), "from_sitemap": len(urls),
            "scraped": scraped_count, "url_only": url_only_count,
            "merged": merged_count,
            "extra_existing": len(products) - len(urls),
        }
        all_stats.append(stats)
        total_products += len(products)
        total_scraped += scraped_count
        total_from_url += url_only_count
        total_merged += merged_count

        logger.info(f"  -> {len(products)} total | {merged_count} enriched | "
                    f"{len(products) - len(urls)} kept from existing")

        if not args.dry_run and products:
            clean_products = [{k: v for k, v in p.items() if not k.startswith("_")}
                              for p in products]
            backup_existing(slug)
            output_file = OUTPUT_DIR / f"{slug}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(clean_products, f, indent=2, ensure_ascii=False)
            logger.info(
                f"  Saved {len(clean_products)} products -> {output_file.name}")

            completed_set.add(slug)
            progress["completed_brands"] = list(completed_set)
            save_progress(progress)

    elapsed = time.time() - start_time

    # ── Summary ──────────────────────────────────────────────────────────
    logger.info("\n" + "=" * 70)
    logger.info("  GOLDEN LIST BUILD COMPLETE")
    logger.info("=" * 70)
    logger.info(f"  Total brands:        {len(all_stats)}")
    logger.info(f"  Total products:      {total_products}")
    logger.info(f"  From page scrape:    {total_scraped}")
    logger.info(f"  From sitemap URL:    {total_from_url}")
    logger.info(f"  Merged w/ existing:  {total_merged}")
    logger.info(f"  Time:                {elapsed:.0f}s ({elapsed / 60:.1f}m)")
    if not args.dry_run:
        logger.info(f"  Output:              {OUTPUT_DIR}")

    # Per-brand breakdown
    logger.info("\n  All brands:")
    for s in sorted(all_stats, key=lambda x: x["total"], reverse=True):
        logger.info(f"    {s['brand']:35s} -> {s['total']:>5d} products")

    # Cleanup progress on full success
    if not args.dry_run and not args.brand:
        if PROGRESS_FILE.exists():
            PROGRESS_FILE.unlink()
        logger.info("\n  All brands processed — progress file cleaned up")

    return 0


if __name__ == "__main__":
    sys.exit(main())
