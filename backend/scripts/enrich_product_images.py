#!/usr/bin/env python3
"""
Image Enrichment Script — Fetches real product images from halilit.com

Strategy:
1. Load all product URLs from Halilit's sitemap (cached in halilit_urls.txt)
2. For each product in our catalog that lacks a real image:
   a. Fuzzy-match the product name + brand to a Halilit URL slug
   b. Fetch the matching product page
   c. Extract the og:image meta tag (cloudfront CDN URL)
3. Update the brand JSON files with real image URLs

Usage:
    python -m backend.scripts.enrich_product_images
    python -m backend.scripts.enrich_product_images --brand nord
    python -m backend.scripts.enrich_product_images --dry-run
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import unquote

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("image_enricher")

# ── Configuration ─────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parents[2] / "frontend" / "public" / "data"
URLS_CACHE = Path(__file__).resolve().parents[1] / "data" / "halilit_urls.txt"
HALILIT_SITEMAP_PAGES = range(2, 7)  # pages 2-6 contain product URLs
REQUEST_DELAY = 0.35  # seconds between requests (be polite)
REQUEST_TIMEOUT = 12  # seconds
HEADERS = {
    "User-Agent": "HalilitSupportCenter/1.0 (product-image-enrichment)",
    "Accept": "text/html",
    "Accept-Language": "he,en;q=0.9",
}

# Placeholder markers that should be replaced
PLACEHOLDER_MARKERS = (
    "placeholder", "brand.com", "example.com",
    "/assets/images/placeholder",
)


def is_real_image(url: str) -> bool:
    """Check if a URL is a real product image, not a placeholder."""
    if not url or not isinstance(url, str):
        return False
    url_lower = url.lower()
    return not any(m in url_lower for m in PLACEHOLDER_MARKERS)


# ── URL Loading ───────────────────────────────────────────────────────────

def load_halilit_urls() -> List[str]:
    """Load cached Halilit product URLs, refreshing from sitemap if needed."""
    if URLS_CACHE.exists():
        urls = URLS_CACHE.read_text().strip().splitlines()
        if len(urls) > 100:
            logger.info(f"Loaded {len(urls)} cached Halilit URLs")
            return urls

    logger.info("Fetching Halilit sitemap...")
    urls = []
    for page in HALILIT_SITEMAP_PAGES:
        try:
            r = requests.get(
                f"https://www.halilit.com/sitemap.xml?page={page}",
                headers=HEADERS, timeout=REQUEST_TIMEOUT
            )
            for match in re.finditer(
                r"<loc>(https://www\.halilit\.com/items/[^<]+)</loc>", r.text
            ):
                urls.append(match.group(1))
        except requests.RequestException as e:
            logger.warning(f"Sitemap page {page} failed: {e}")
        time.sleep(0.5)

    URLS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    URLS_CACHE.write_text("\n".join(urls))
    logger.info(f"Cached {len(urls)} Halilit product URLs")
    return urls


# ── URL Matching ──────────────────────────────────────────────────────────

def _slug_from_url(url: str) -> str:
    """Extract the slug portion from a Halilit URL and normalize it."""
    # https://www.halilit.com/items/447477-washburn-t24-bass-guitar
    # → "washburn t24 bass guitar"
    path = unquote(url.rsplit("/", 1)[-1])  # decode %D7%... Hebrew chars
    # Remove leading numeric ID
    path = re.sub(r"^\d+-", "", path)
    # Replace separators with spaces, lowercase
    return re.sub(r"[-_]+", " ", path).lower().strip()


def _normalize_for_match(text: str) -> str:
    """Normalize a product name for fuzzy matching."""
    text = text.lower()
    # Remove Hebrew characters for matching purposes
    text = re.sub(r"[\u0590-\u05FF]+", "", text)
    # Remove special chars, keep alphanumeric and spaces
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    # Collapse whitespace
    return re.sub(r"\s+", " ", text).strip()


def _token_overlap(a: str, b: str) -> float:
    """Calculate Jaccard-style token overlap between two strings."""
    tokens_a = set(a.split())
    tokens_b = set(b.split())
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


def _key_tokens(product_name: str, brand: str) -> set:
    """Extract the most discriminative tokens (model numbers, brand)."""
    text = _normalize_for_match(f"{brand} {product_name}")
    tokens = set(text.split())
    # Remove very common short words
    stop = {"the", "a", "an", "and", "or",
            "for", "in", "of", "with", "by", "to"}
    return tokens - stop


def build_url_index(urls: List[str]) -> Dict[str, List[Tuple[str, str]]]:
    """Build a brand → [(slug, url)] index for fast lookup."""
    index: Dict[str, List[Tuple[str, str]]] = {}
    for url in urls:
        slug = _slug_from_url(url)
        # First word of slug is typically the brand
        parts = slug.split()
        brand_token = parts[0] if parts else ""
        if brand_token not in index:
            index[brand_token] = []
        index[brand_token].append((slug, url))
    return index


def match_product_to_url(
    product_name: str,
    brand: str,
    url_index: Dict[str, List[Tuple[str, str]]],
) -> Optional[str]:
    """Find the best matching Halilit URL for a product."""
    brand_norm = _normalize_for_match(brand).split()[0] if brand else ""
    product_norm = _normalize_for_match(f"{brand} {product_name}")
    product_tokens = _key_tokens(product_name, brand)

    # Get candidate URLs for this brand
    candidates = url_index.get(brand_norm, [])

    # Also check multi-word brand variants
    brand_full = _normalize_for_match(brand)
    for bn_token in brand_full.split():
        if bn_token != brand_norm and bn_token in url_index:
            candidates.extend(url_index[bn_token])

    if not candidates:
        # Fall back to searching ALL URLs (slower)
        all_urls = []
        for slug_list in url_index.values():
            all_urls.extend(slug_list)
        candidates = all_urls

    best_score = 0.0
    best_url = None

    for slug, url in candidates:
        slug_tokens = set(slug.split())

        # Strategy 1: Token overlap (Jaccard)
        score = _token_overlap(product_norm, slug)

        # Strategy 2: Key token matching (model numbers are critical)
        key_matches = product_tokens & slug_tokens
        if len(product_tokens) > 0:
            key_score = len(key_matches) / len(product_tokens)
            score = max(score, key_score)

        # Strategy 3: Substring containment
        # If the slug contains the model number portion, strong signal
        name_norm = _normalize_for_match(product_name)
        if len(name_norm) > 3 and name_norm in slug:
            score = max(score, 0.85)

        if score > best_score:
            best_score = score
            best_url = url

    # Require minimum confidence
    if best_score >= 0.35:
        return best_url
    return None


# ── Image Extraction ──────────────────────────────────────────────────────

def fetch_og_image(url: str) -> Optional[str]:
    """Fetch a Halilit product page and extract the og:image URL."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()

        # Extract og:image
        match = re.search(
            r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
            r.text,
        )
        if match:
            img_url = match.group(1)
            if "cloudfront" in img_url or img_url.startswith("http"):
                return img_url

        # Fallback: look for cloudfront image URLs in the page
        cf_match = re.search(
            r'(https://d3m9l0v76dty0\.cloudfront\.net/system/photos/\d+/(?:original|large)/[^"\')\s]+)',
            r.text,
        )
        if cf_match:
            return cf_match.group(1)

    except requests.RequestException as e:
        logger.debug(f"Failed to fetch {url}: {e}")
    return None


def build_gallery_from_page(url: str) -> List[str]:
    """Extract all product image URLs from a Halilit product page."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()

        # Find all cloudfront image URLs
        cf_urls = re.findall(
            r'(https://d3m9l0v76dty0\.cloudfront\.net/system/photos/\d+/(?:original|large)/[^"\')\s?]+)',
            r.text,
        )
        # Deduplicate while preserving order, skip layout/icon images
        seen = set()
        gallery = []
        for img_url in cf_urls:
            # Clean URL (remove query params)
            clean = img_url.split("?")[0]
            if clean not in seen:
                seen.add(clean)
                gallery.append(clean)

        # The first large/original image is typically the product hero
        return gallery[:10]  # cap at 10 images
    except requests.RequestException:
        return []


# ── Brand JSON Processing ─────────────────────────────────────────────────

def load_brand_json(filepath: Path) -> Tuple[List[dict], dict]:
    """Load a brand JSON file and return (products, raw_data)."""
    with open(filepath) as f:
        data = json.load(f)

    if isinstance(data, list):
        return data, {"_is_list": True}
    elif isinstance(data, dict):
        products = data.get("products", [data])
        return products, data
    return [], data


def save_brand_json(filepath: Path, products: List[dict], raw_data: dict):
    """Save updated brand JSON file."""
    if raw_data.get("_is_list"):
        out = products
    elif "products" in raw_data:
        raw_data["products"] = products
        out = raw_data
    else:
        out = products[0] if len(products) == 1 else products

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)


# ── Main Enrichment Logic ────────────────────────────────────────────────

def enrich_brand(
    brand_file: Path,
    url_index: Dict[str, List[Tuple[str, str]]],
    dry_run: bool = False,
) -> dict:
    """Enrich a single brand file with real product images."""
    products, raw_data = load_brand_json(brand_file)
    brand_name = brand_file.stem.replace("-", " ").replace("_", " ").title()

    stats = {"total": 0, "already_has": 0, "found": 0, "not_found": 0}

    for product in products:
        stats["total"] += 1
        name = product.get("product_name", product.get("name", ""))
        brand = product.get("brand", brand_name)
        current_img = product.get("image_url", "")

        # Skip if already has a real image
        if is_real_image(current_img):
            stats["already_has"] += 1
            continue

        # Find matching Halilit URL
        matched_url = match_product_to_url(name, brand, url_index)
        if not matched_url:
            stats["not_found"] += 1
            logger.debug(f"  ✗ No match: {brand} - {name[:50]}")
            continue

        # Fetch the image
        time.sleep(REQUEST_DELAY)
        gallery = build_gallery_from_page(matched_url)

        if gallery:
            hero_url = gallery[0]
            stats["found"] += 1
            logger.debug(f"  ✓ {name[:40]} → {hero_url[:60]}")

            if not dry_run:
                # Update product
                product["image_url"] = hero_url

                # Update hero image object
                product["image_hero"] = {
                    "url": hero_url,
                    "alt": name,
                    "type": "image",
                    "display_purpose": "hero",
                    "priority": 90,
                    "source": "halilit_enrichment",
                }

                # Update gallery
                product["image_gallery"] = [
                    {"url": u, "alt": name, "type": "image",
                     "display_purpose": "gallery", "source": "halilit_enrichment"}
                    for u in gallery
                ]

                # Update official_images
                product["official_images"] = [
                    {"url": u, "alt": name, "type": "image",
                     "display_purpose": "hero" if i == 0 else "gallery",
                     "priority": 90 - i, "source": "halilit_enrichment"}
                    for i, u in enumerate(gallery)
                ]

                # Update display object
                disp = product.get("display", {})
                if isinstance(disp, dict):
                    disp["hero_image"] = product["image_hero"]
                    disp["thumbnail_image"] = {
                        "url": hero_url.replace("/original/", "/large/"),
                        "alt": name,
                        "type": "image",
                        "display_purpose": "thumbnail",
                        "source": "halilit_enrichment",
                    }
                    product["display"] = disp

                # Set halilit_url to the actual product page
                product["halilit_url"] = matched_url
        else:
            stats["not_found"] += 1
            logger.debug(f"  ✗ No image on page: {matched_url[:60]}")

    # Save updated file
    if not dry_run and stats["found"] > 0:
        save_brand_json(brand_file, products, raw_data)
        logger.info(
            f"  💾 Saved {brand_file.name}: "
            f"{stats['found']} images added"
        )

    return stats


def run_enrichment(
    brand_filter: Optional[str] = None,
    dry_run: bool = False,
    verbose: bool = False,
):
    """Run image enrichment across all brand JSON files."""
    if verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("=" * 60)
    logger.info("🖼️  Halilit Product Image Enrichment")
    logger.info("=" * 60)

    # Load Halilit URLs
    urls = load_halilit_urls()
    url_index = build_url_index(urls)
    logger.info(
        f"URL index: {len(url_index)} brand tokens, {len(urls)} total URLs")

    # Find brand files (skip non-brand files like galaxy_db.json)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    brand_files = sorted(
        f for f in DATA_DIR.glob("*.json")
        if f.stat().st_size < MAX_FILE_SIZE
    )
    if brand_filter:
        brand_files = [
            f for f in brand_files
            if brand_filter.lower() in f.stem.lower()
        ]

    logger.info(f"Processing {len(brand_files)} brand files...")
    if dry_run:
        logger.info("🔍 DRY RUN — no files will be modified")

    totals = {"total": 0, "already_has": 0, "found": 0, "not_found": 0}

    for i, brand_file in enumerate(brand_files, 1):
        logger.info(f"[{i}/{len(brand_files)}] {brand_file.stem}")
        stats = enrich_brand(brand_file, url_index, dry_run=dry_run)

        for k in totals:
            totals[k] += stats[k]

        if stats["found"] > 0 or stats["not_found"] > 0:
            logger.info(
                f"  ✓ {stats['found']} found, "
                f"✗ {stats['not_found']} unmatched, "
                f"⏭ {stats['already_has']} already had images"
            )

    logger.info("")
    logger.info("=" * 60)
    logger.info("📊 ENRICHMENT SUMMARY")
    logger.info(f"  Total products:    {totals['total']}")
    logger.info(f"  Already had image: {totals['already_has']}")
    logger.info(f"  Images found:      {totals['found']}")
    logger.info(f"  Not matched:       {totals['not_found']}")
    pct = (totals["found"] + totals["already_has"]) / \
        max(totals["total"], 1) * 100
    logger.info(f"  Coverage:          {pct:.1f}%")
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Enrich product images from halilit.com")
    parser.add_argument("--brand", type=str, help="Filter to a specific brand")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't modify files")
    parser.add_argument("--verbose", "-v",
                        action="store_true", help="Verbose output")
    args = parser.parse_args()

    run_enrichment(
        brand_filter=args.brand,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )
