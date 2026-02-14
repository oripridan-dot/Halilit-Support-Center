#!/usr/bin/env python3
"""
Product Image Enrichment Script v2

Scrapes product thumbnail images from Halilit.com category listing pages
and updates the JSON data files in frontend/public/data/.

Strategy:
  - Category/listing pages are accessible (no anti-bot block)
  - Each page shows 25 products with CDN thumbnail images
  - We paginate through all category pages to collect images
  - Then match by product name to update JSON data files

Usage:
    cd project_root
    .venv/bin/python3 backend/scripts/enrich_images.py
"""

import json
import logging
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import requests
from bs4 import BeautifulSoup

# ═══════════════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "frontend" / "public" / "data"
PROGRESS_FILE = PROJECT_ROOT / "backend" / "data" / "image_enrichment_progress.json"
IMAGE_MAP_FILE = PROJECT_ROOT / "backend" / "data" / "image_map.json"

HALILIT_BASE = "https://www.halilit.com"
CDN_PREFIX = "d3m9l0v76dty0.cloudfront.net"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

RATE_LIMIT = 1.0  # seconds between requests
MAX_RETRIES = 3
MAX_PAGES_PER_CATEGORY = 30  # safety limit

# All Halilit category URLs (extracted from site navigation)
CATEGORY_URLS = [
    # Guitars & Amps
    "/23612-electric-guitars",
    "/23610-acoustic-guitars",
    "/23608-classical-guitars",
    "/23640-bass-guitars",
    "/23622-electric-guitar-amplifiers",
    "/569082-bass-guitar-amps",
    "/569083-acoustic-classic-guitar-amps",
    "/23606-guitar-effects",
    "/23636-guitar-strings",
    "/23605-guitar-accessories",
    "/354193-guitar-bags",
    "/163138-kids-guitars",
    "/23609-ukulele",
    "/100536-left-handed-guitars",
    # Drums
    "/23653-drum-kits",
    "/23632-snares-toms-bass-drums",
    "/23633-cymbals",
    "/23650-drum-heads",
    "/154328-percussion",
    "/23644-drums-accessories",
    "/23701-concert-percussion",
    "/29590-marching-drums",
    "/23664-educational-instruments",
    # Electronic Drums
    "/23607-roland-v-drums",
    "/23693-medeli-drums",
    "/156122-atv-drums-accessories",
    "/23615-drum-machines",
    "/23645-roland-v-drums-pads",
    "/23663-v-drums-modules",
    "/23677-v-drums-amplifiers",
    "/23661-v-drums-accessories",
    "/23699-acoustic-drum-triggers",
    "/219418-pearl-e-merge-electronic-drums-",
    # Keys & Synths
    "/23628-digital-pianos",
    "/722466-stage-pianos",
    "/23672-arranger-keyboards",
    "/254063-oriental-keyboards",
    "/23648-synth",
    "/23635-keyboard-accessories",
    "/23700-keyboard-amplifiers",
    "/23687-roland-v-accordion",
    # Studio & Recording
    "/23621-audio-interfaces",
    "/23614-recording-software",
    "/23604-studio-monitors",
    "/23625-studio-microphones",
    "/259295-studio-headphones",
    "/23616-samplers-controllers",
    "/23656-preamps-sound-processors",
    "/23631-keyboard-controllers",
    "/23626-control-surfaces",
    "/23067-uad-dsp-card",
    "/23667-midi-interfaces",
    "/23624-recording-systems",
    "/23627-studio-accessories",
    "/727879-vocal-effects",
    "/163524-studio-bundles",
    # Headphones
    "/23679-studio-headphones",
    "/23617-dj-headphones",
    "/23682-mobile-headphones",
    "/42989-audiophile-headphones",
    "/258586-gaming-headphones",
    "/178254-headphones-amplifiers",
    # DJ
    "/23618-DJ-Mixers",
    "/83871-dj-mixers",
    "/23619-cdj-players",
    "/23646-vocal-effects",
    "/24457-DJ-Accessories",
    # PA & Live Sound
    "/23054-pa-equipment",
    "/22555-pa-speakers",
    "/30329-line-array",
    "/23643-portable-pa-systems",
    "/35217-mobile-pa-and-karaoke",
    # Wind Instruments
    "/23654-trumpets",
    "/23671-saxophones",
    "/23669-clarinets",
    "/23684-recorders",
    "/23688-harmonicas",
    "/23691-flutes",
    "/23703-brass",
    "/23651-eectronic-wind-instruments",
    "/23142-wind-instruments-accessories",
    "/23195-wind-instruments-mouthpieces",
    # Acoustics
    "/23665-absorbents",
    "/23668-diffusers",
    "/23666-bass-traps",
    "/23697-soundproofing",
    "/92384-acoustics-accessories",
    # Cables
    "/197051-guitar-cables",
    "/203770-patch-cables",
    "/203931-microphone-cables",
    "/257155-keyboard-cables",
    "/203930-monitor-cables",
    "/203934-audio-cables",
    "/211659-xlr-cables",
    "/212208-usb-cables",
    "/211657-midi-cables",
    "/203933-speaker-cables",
    "/211664-digital-cables",
    "/212148-adapters",
    "/211663-adapter-cables",
    "/211662-stage-boxes",
    "/211658-di-boxes",
    "/211661-hdmi-sdi-bnc-cables",
    "/212151-sc-rode-cable",
    # Misc
    "/23867-mobile-speakers",
    "/197053-speaker-cables",
    # Video & Broadcast
    "/200832-filming-broadcasting-podcasting-microphones",
    "/200826-video-routers-mixers-switchers",
    # Sale categories
    "/300132-guitars-special-price",
    "/300133-amplifiers-special-price",
    "/300134-guitar-pedals-effects-special-price",
    "/300138-life-style-special-price",
    "/300142-keyboards-special-price",
    "/300143-audio-interfaces-special-price",
    "/300144-studio-monitors-special-price",
    "/300145-midi-keyboard-special-price",
    "/300146-headphones-special-price",
    "/300147-microphones-special-price",
    "/300148-drums-special-price",
    "/300149-video-broadcast-special-price",
    "/300150-pa-special-price",
    "/300153-accessories-special-price",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ImageEnrich")


# ═══════════════════════════════════════════════════════════════════════
# SCRAPING
# ═══════════════════════════════════════════════════════════════════════

def normalize_image_url(url: str) -> str:
    """Normalize to /large/ size."""
    url = re.sub(
        r"/system/photos/(\d+)/(medium|original|extra_large|thumb)/",
        r"/system/photos/\1/large/", url
    )
    url = re.sub(r"\?\d+$", "", url)
    return url


def scrape_listing_page(
    session: requests.Session, url: str
) -> Tuple[List[Dict], int]:
    """
    Scrape a single listing page. Returns (products, max_page).
    Each product dict: {name, image_url, product_url}
    """
    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(RATE_LIMIT)
            resp = session.get(url, timeout=15)
            if resp.status_code != 200:
                continue

            # Check for anti-bot page
            if len(resp.text) < 2000 and "page_no_referer" in resp.text:
                if attempt < MAX_RETRIES - 1:
                    wait = (attempt + 1) * 3
                    logger.debug(f"Anti-bot on {url}, retry in {wait}s")
                    time.sleep(wait)
                    continue
                return [], 0

            soup = BeautifulSoup(resp.text, "html.parser")

            # Extract products
            items = soup.select(
                ".layout_list_item, .box, .item, .product_item, .product_box"
            )
            products = []
            for item in items:
                title_el = item.select_one(
                    ".title, .product-title, h3, h4, .title_with_brand, .item-title"
                )
                if not title_el:
                    continue

                name = title_el.get_text(strip=True)
                if not name:
                    continue

                img_el = item.select_one("img")
                img_url = ""
                if img_el:
                    img_url = img_el.get("data-src") or img_el.get("src") or ""
                    if img_url.startswith("//"):
                        img_url = "https:" + img_url
                    elif img_url and not img_url.startswith("http"):
                        img_url = HALILIT_BASE + img_url

                # Only keep CDN images
                if img_url and CDN_PREFIX in img_url:
                    img_url = normalize_image_url(img_url)
                else:
                    img_url = ""

                link_el = item.select_one("a")
                product_url = ""
                if link_el:
                    href = link_el.get("href", "").strip()
                    if href:
                        href = href.replace("\n", "").replace("\r", "").strip()
                        product_url = (
                            href if href.startswith("http") else HALILIT_BASE + href
                        )

                products.append({
                    "name": name,
                    "image_url": img_url,
                    "product_url": product_url,
                })

            # Get max page from pagination
            max_page = 1
            pagination = soup.select_one(".pagination")
            if pagination:
                for link in pagination.find_all("a", href=True):
                    pm = re.search(r"page=(\d+)", link.get("href", ""))
                    if pm:
                        pg = int(pm.group(1))
                        if pg > max_page:
                            max_page = pg

            return products, max_page

        except Exception as e:
            logger.debug(f"Error scraping {url}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2)
            continue

    return [], 0


def scrape_all_categories(session: requests.Session) -> Dict[str, str]:
    """
    Scrape all category pages to build name→image map.
    Returns dict of product_name → image_url.
    """
    image_map: Dict[str, str] = {}
    url_map: Dict[str, str] = {}  # name → product_url
    total_pages = 0
    blocked_categories = 0

    for i, cat_path in enumerate(CATEGORY_URLS):
        cat_url = HALILIT_BASE + cat_path
        cat_name = cat_path.split("-", 1)[-1] if "-" in cat_path else cat_path

        # Scrape first page
        products, max_page = scrape_listing_page(session, cat_url)

        if not products and max_page == 0:
            blocked_categories += 1
            logger.debug(f"  [{i+1}/{len(CATEGORY_URLS)}] BLOCKED: {cat_name}")
            continue

        for p in products:
            if p["image_url"] and p["name"]:
                image_map[p["name"]] = p["image_url"]
                if p["product_url"]:
                    url_map[p["name"]] = p["product_url"]

        total_pages += 1
        new_count = len(products)

        # Paginate
        for page_num in range(2, min(max_page + 1, MAX_PAGES_PER_CATEGORY)):
            page_url = f"{cat_url}?page={page_num}"
            page_products, _ = scrape_listing_page(session, page_url)
            if not page_products:
                break
            for p in page_products:
                if p["image_url"] and p["name"]:
                    image_map[p["name"]] = p["image_url"]
                    if p["product_url"]:
                        url_map[p["name"]] = p["product_url"]
            new_count += len(page_products)
            total_pages += 1

        logger.info(
            f"  [{i+1}/{len(CATEGORY_URLS)}] {cat_name}: "
            f"{new_count} products, {max_page} pages "
            f"(total images: {len(image_map)})"
        )

    logger.info(
        f"\nScraping complete: {len(image_map)} unique images from "
        f"{total_pages} pages ({blocked_categories} categories blocked)"
    )

    return image_map, url_map


# ═══════════════════════════════════════════════════════════════════════
# MATCHING & UPDATING
# ═══════════════════════════════════════════════════════════════════════

def name_to_slug(name: str) -> str:
    """Normalize product name to slug for matching."""
    slug = name.lower().strip()
    slug = re.sub(r"[\u0590-\u05FF]+", "", slug)  # Remove Hebrew
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def build_slug_index(image_map: Dict[str, str]) -> Dict[str, Tuple[str, str]]:
    """Build slug → (name, image_url) index."""
    index = {}
    for name, img_url in image_map.items():
        slug = name_to_slug(name)
        if slug:
            index[slug] = (name, img_url)
    return index


def find_image_for_product(
    product_name: str, slug_index: Dict[str, Tuple[str, str]]
) -> Optional[str]:
    """Find the best matching image URL for a product name."""
    product_slug = name_to_slug(product_name)
    if not product_slug:
        return None

    # Exact match
    if product_slug in slug_index:
        return slug_index[product_slug][1]

    # Product slug contained in scraped slug
    best_match = None
    best_score = 0
    for slug, (name, img_url) in slug_index.items():
        if product_slug in slug:
            score = len(product_slug)
            if score > best_score:
                best_score = score
                best_match = img_url
        elif slug in product_slug:
            score = len(slug)
            if score > best_score:
                best_score = score
                best_match = img_url

    return best_match


def update_json_files(
    image_map: Dict[str, str], url_map: Dict[str, str]
):
    """Update all JSON data files with scraped images."""
    slug_index = build_slug_index(image_map)
    url_slug_index = build_slug_index(url_map) if url_map else {}

    json_files = sorted(DATA_DIR.glob("*.json"))
    total_products = 0
    total_updated = 0
    already_had = 0
    files_modified = 0

    for json_file in json_files:
        try:
            with open(json_file) as f:
                products = json.load(f)
            if not isinstance(products, list):
                continue

            file_updated = 0
            for product in products:
                total_products += 1
                name = product.get("product_name", "")
                if not name:
                    continue

                # Skip products that already have valid images
                existing = product.get("image_url", "")
                if (
                    existing
                    and "placeholder" not in existing
                    and existing.startswith("http")
                    and CDN_PREFIX in existing
                ):
                    already_had += 1
                    continue

                # Find matching image
                img_url = find_image_for_product(name, slug_index)
                if not img_url:
                    continue

                # Update product fields
                product["image_url"] = img_url
                product["image_gallery"] = [
                    {
                        "url": img_url,
                        "alt": name,
                        "type": "image",
                        "display_purpose": "hero",
                        "priority": 100,
                        "source": "halilit_listing",
                    }
                ]
                product["official_images"] = [
                    {
                        "url": img_url,
                        "type": "image",
                        "display_purpose": "hero",
                        "source": "halilit_listing",
                        "priority": 100,
                    }
                ]
                product["image_hero"] = {
                    "url": img_url,
                    "alt": name,
                    "type": "image",
                    "display_purpose": "hero",
                    "priority": 100,
                    "source": "halilit_listing",
                }
                product["image_thumbnail"] = product["image_hero"].copy()
                product["image_thumbnail"]["display_purpose"] = "thumbnail"

                if "display" in product and isinstance(product["display"], dict):
                    product["display"]["hero_image"] = product["image_hero"]
                    product["display"]["thumbnail_image"] = product["image_thumbnail"]

                # Update halilit_url if we have a real one
                product_slug = name_to_slug(name)
                if product_slug and product.get("halilit_url") in (
                    "", "https://halilit.com"
                ):
                    for slug, (uname, purl) in url_slug_index.items():
                        if product_slug in slug or slug in product_slug:
                            if purl.startswith("http"):
                                product["halilit_url"] = purl
                                break

                file_updated += 1

            if file_updated > 0:
                with open(json_file, "w") as f:
                    json.dump(products, f, indent=2, ensure_ascii=False)
                total_updated += file_updated
                files_modified += 1
                logger.info(f"  {json_file.name}: {file_updated} products updated")

        except Exception as e:
            logger.error(f"Error processing {json_file.name}: {e}")

    logger.info(f"\nUpdate complete:")
    logger.info(f"  Total products: {total_products}")
    logger.info(f"  Already had images: {already_had}")
    logger.info(f"  Updated with new images: {total_updated}")
    logger.info(f"  Files modified: {files_modified}")
    logger.info(
        f"  Still missing: {total_products - already_had - total_updated}"
    )


def rebuild_conductor():
    """Rebuild conductor catalog so frontend picks up new images."""
    logger.info("Rebuilding conductor catalog...")
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from backend.product_normalizer import normalize_all_products
        normalize_all_products()
        logger.info("Conductor catalog rebuilt!")
    except Exception as e:
        logger.warning(f"Could not rebuild catalog: {e}")
        logger.info("Run manually: .venv/bin/python3 -m backend.product_normalizer")


def main():
    logger.info("=" * 60)
    logger.info("PRODUCT IMAGE ENRICHMENT v2")
    logger.info("Strategy: Scrape Halilit category listing pages")
    logger.info("=" * 60)

    start = time.time()

    # Create session
    session = requests.Session()
    session.headers.update(HEADERS)

    # Phase 1: Scrape images from category pages
    logger.info("\nPHASE 1: Scraping category listing pages...")
    image_map, url_map = scrape_all_categories(session)

    # Save image map
    IMAGE_MAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(IMAGE_MAP_FILE, "w") as f:
        json.dump(image_map, f, indent=2, ensure_ascii=False)
    logger.info(f"Image map saved: {IMAGE_MAP_FILE}")

    # Phase 2: Update JSON files
    logger.info("\nPHASE 2: Updating JSON data files...")
    update_json_files(image_map, url_map)

    # Phase 3: Rebuild conductor catalog
    logger.info("\nPHASE 3: Rebuilding catalog...")
    rebuild_conductor()

    elapsed = time.time() - start
    logger.info(f"\nDone in {elapsed:.0f}s ({elapsed/60:.1f}min)")
    logger.info("Restart the dev server to see updated images.")


if __name__ == "__main__":
    main()
