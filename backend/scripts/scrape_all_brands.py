#!/usr/bin/env python3
"""
Halilit Full Brand Scraper — fetches ALL products from ALL brands via Tor proxy.

Usage:
    # Via Tor (default — install: brew install tor && tor):
    python3 backend/scripts/scrape_all_brands.py

    # With custom proxy:
    HTTP_PROXY=socks5h://127.0.0.1:9050 python3 backend/scripts/scrape_all_brands.py

Requirements:
    pip install requests beautifulsoup4 pysocks
"""

import json, re, os, sys, time, math, hashlib, signal
from pathlib import Path
from collections import defaultdict
import requests
from bs4 import BeautifulSoup

# ─── Config ───────────────────────────────────────────────────────────
BASE        = "https://www.halilit.com"
BRANDS_URL  = f"{BASE}/g/5193-Brand"
PER_PAGE    = 24
DELAY       = 2.0   # seconds between requests (be polite)
TIMEOUT     = 45     # request timeout in seconds
MAX_RETRIES = 3
PROJECT_ROOT= Path(__file__).resolve().parent.parent.parent
DATA_DIR    = PROJECT_ROOT / "frontend" / "public" / "data"
BRAND_FILE  = PROJECT_ROOT / "backend" / "data" / "brand_discovery.json"
URL_FILE    = PROJECT_ROOT / "backend" / "data" / "all_product_urls.txt"
PROGRESS_FILE = PROJECT_ROOT / "backend" / "data" / "scrape_progress.json"

# Default to Tor SOCKS5 proxy
DEFAULT_PROXY = "socks5h://127.0.0.1:9050"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": f"{BASE}/",
    "Connection": "keep-alive",
}

# ─── Progress tracking ───────────────────────────────────────────────
_progress = {"completed_brands": [], "completed_pages": {}, "total_urls": 0}

def load_progress():
    global _progress
    if PROGRESS_FILE.exists():
        try:
            _progress = json.loads(PROGRESS_FILE.read_text("utf-8"))
        except:
            pass

def save_progress():
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(json.dumps(_progress, indent=2, ensure_ascii=False), "utf-8")

# ─── Helpers ──────────────────────────────────────────────────────────
def get_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    proxy = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY") or DEFAULT_PROXY
    s.proxies = {"http": proxy, "https": proxy}
    print(f"  Using proxy: {proxy}")
    return s

def fetch(session, url, retries=MAX_RETRIES):
    for attempt in range(retries):
        try:
            resp = session.get(url, timeout=TIMEOUT)
            if resp.status_code == 403:
                print(f"    403 Forbidden, waiting longer...")
                time.sleep(DELAY * 5)
                if attempt < retries - 1:
                    continue
                return None
            if "page_no_referer" in resp.text or "limit_no_referer" in resp.text:
                if attempt < retries - 1:
                    print(f"    Anti-bot detected, retry {attempt+1}...")
                    time.sleep(DELAY * 3)
                    continue
                print(f"    BLOCKED: {url}")
                return None
            if resp.status_code == 404:
                # 404 on Konimbo sometimes still has content
                if len(resp.text) > 10000:
                    return resp.text
                return None
            return resp.text
        except requests.exceptions.ConnectionError as e:
            if attempt < retries - 1:
                print(f"    Connection error, retry {attempt+1}...")
                time.sleep(DELAY * 2)
                continue
            print(f"    CONN ERROR: {url} — {e}")
            return None
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(DELAY)
                continue
            print(f"    ERROR: {url} — {e}")
            return None
    return None

def extract_total(html):
    """Extract total product count from 'תוצאות: <b>NNN</b>' text."""
    # Handle HTML tags around the number: תוצאות: <b>512</b>
    m = re.search(r'תוצאות[:\s]*(?:<[^>]+>)?\s*([\d,]+)', html)
    if m:
        return int(m.group(1).replace(",", ""))
    # Fallback: parse with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    results_span = soup.find("span", class_="results")
    if results_span:
        text = results_span.get_text()
        m2 = re.search(r'([\d,]+)', text)
        if m2:
            return int(m2.group(1).replace(",", ""))
    return 0

def extract_products_from_html(html, brand_name):
    """Extract product data from layout_list_item elements."""
    products = []
    soup = BeautifulSoup(html, "html.parser")
    
    for item_div in soup.find_all(class_="layout_list_item"):
        product = {"brand": brand_name}
        
        # Get item ID from id="item_id_NNNNN"
        item_id_attr = item_div.get("id", "")
        if item_id_attr.startswith("item_id_"):
            product["halilit_id"] = item_id_attr.replace("item_id_", "")
        
        # Get SKU from data-item-code
        sku = item_div.get("data-item-code", "")
        if sku:
            product["sku"] = sku
        
        # Get brand from data-brand-title (more accurate)
        brand_attr = item_div.get("data-brand-title", "")
        if brand_attr:
            product["brand"] = brand_attr
        
        # Get category from data-category-title
        cat = item_div.get("data-category-title", "")
        if cat:
            product["category"] = cat
        
        # Get URL from first <a> with /items/ in href
        for a in item_div.find_all("a", href=True):
            href = a["href"].strip()
            if "/items/" in href:
                product["url"] = BASE + href if not href.startswith("http") else href
                product["slug"] = href.split("/items/")[-1].strip()
                break
        
        # Get title from h3.title_with_brand or first h3/h4
        title_el = item_div.find(["h3", "h4"], class_=re.compile("title"))
        if not title_el:
            title_el = item_div.find(["h3", "h4"])
        if title_el:
            product["product_name"] = title_el.get_text(strip=True)
        
        # Get description from p.content
        desc_el = item_div.find("p", class_="content")
        if desc_el:
            product["description"] = desc_el.get_text(strip=True)
        
        # Get prices from text
        item_text = item_div.get_text()
        
        # Regular price: "מחיר43,952 ₪" or "מחיר 43,952 ₪"
        price_match = re.search(r'מחיר\s*([\d,]+)\s*₪', item_text)
        if price_match:
            product["price_il"] = int(price_match.group(1).replace(",", ""))
        
        # Eilat price: "מחיר באילת37,247 ₪"
        eilat_match = re.search(r'מחיר באילת\s*([\d,]+)\s*₪', item_text)
        if eilat_match:
            product["price_eilat"] = int(eilat_match.group(1).replace(",", ""))
        
        # Sale price: "מחיר רגיל:14,280 ₪"
        sale_match = re.search(r'מחיר רגיל[:\s]*([\d,]+)\s*₪', item_text)
        if sale_match:
            product["price_regular"] = int(sale_match.group(1).replace(",", ""))
        
        # Get image
        img = item_div.find("img", class_="img-responsive")
        if img:
            product["image"] = img.get("src", "")
        
        # Only add if we have at least an ID or URL
        if product.get("halilit_id") or product.get("url"):
            if not product.get("product_name"):
                product["product_name"] = product.get("slug", "unknown")
            products.append(product)
    
    return products

def slugify(text):
    """Simple slugify for file names."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def save_brand_products(name, new_products):
    """Save products for a brand, merging with existing data."""
    if not new_products:
        return 0
    
    filename = slugify(name) + ".json"
    filepath = DATA_DIR / filename
    
    # Load existing
    existing = []
    if filepath.exists():
        try:
            data = json.loads(filepath.read_text("utf-8"))
            existing = data if isinstance(data, list) else data.get("products", [])
        except:
            pass
    
    # Build dedup keys from existing
    existing_ids = set()
    for p in existing:
        if p.get("halilit_id"):
            existing_ids.add(str(p["halilit_id"]))
        if p.get("url"):
            existing_ids.add(p["url"])
    
    # Add new unique products
    added = 0
    for p in new_products:
        pid = str(p.get("halilit_id", ""))
        purl = p.get("url", "")
        if pid and pid not in existing_ids:
            existing.append(p)
            existing_ids.add(pid)
            if purl:
                existing_ids.add(purl)
            added += 1
        elif purl and purl not in existing_ids:
            existing.append(p)
            existing_ids.add(purl)
            added += 1
    
    if added > 0:
        filepath.write_text(json.dumps(existing, indent=2, ensure_ascii=False), "utf-8")
    
    return added

# ─── Main ─────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Halilit Full Brand Scraper (via Tor)")
    print("=" * 60)
    
    load_progress()
    session = get_session()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\n\n  Interrupted! Saving progress...")
        save_progress()
        print(f"  Progress saved. {_progress['total_urls']} URLs so far.")
        print(f"  Re-run the script to resume from where you left off.")
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Step 1: Always re-fetch brands from the master page (URLs change)
    print(f"\n[1/4] Fetching brands list from master page...")
    html = fetch(session, BRANDS_URL)
    if not html:
        # Fall back to cached
        if BRAND_FILE.exists():
            brands = json.loads(BRAND_FILE.read_text("utf-8"))
            print(f"  Using cached {len(brands)} brands (master page blocked)")
        else:
            print("FATAL: Cannot access brands page and no cache. Is Tor running?")
            sys.exit(1)
    else:
        brands = []
        soup = BeautifulSoup(html, "html.parser")
        seen_ids = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/g/5193-Brand/" in href:
                slug = href.split("/g/5193-Brand/")[-1]
                if not slug or slug.startswith("?"):
                    continue
                brand_id = slug.split("-")[0]
                if brand_id in seen_ids:
                    continue
                seen_ids.add(brand_id)
                name = a.get_text(strip=True)
                if name:
                    brands.append({
                        "name": name,
                        "id": brand_id,
                        "slug": slug,
                        "url": f"/g/5193-Brand/{slug}",
                    })
        
        BRAND_FILE.parent.mkdir(parents=True, exist_ok=True)
        BRAND_FILE.write_text(json.dumps(brands, indent=2, ensure_ascii=False), "utf-8")
        print(f"  Discovered {len(brands)} brands")
    
    time.sleep(DELAY)
    
    # Step 2: Fetch page 1 of each brand
    completed = set(_progress.get("completed_brands", []))
    remaining = [b for b in brands if b["name"] not in completed]
    print(f"\n[2/4] Fetching page 1 for {len(remaining)} brands ({len(completed)} already done)...")
    
    all_product_urls = set()
    brand_counts = {}
    total_new = 0
    
    for i, brand in enumerate(remaining):
        brand_url = BASE + brand["url"]
        name = brand["name"]
        print(f"  [{i+1}/{len(remaining)}] {name}...", end=" ", flush=True)
        
        html = fetch(session, brand_url)
        if not html:
            print("BLOCKED")
            time.sleep(DELAY * 2)
            continue
        
        total = extract_total(html)
        brand_counts[name] = total
        brand["product_count"] = total
        
        # Extract products from page 1
        products = extract_products_from_html(html, name)
        for p in products:
            if p.get("url"):
                all_product_urls.add(p["url"])
        
        added = save_brand_products(name, products)
        total_new += added
        
        pages = math.ceil(total / PER_PAGE) if total > 0 else 1
        print(f"{total} products ({pages} pages), extracted {len(products)}, +{added} new")
        
        _progress["completed_brands"].append(name)
        _progress["total_urls"] = len(all_product_urls)
        
        # Save progress every 10 brands
        if (i + 1) % 10 == 0:
            save_progress()
            BRAND_FILE.write_text(json.dumps(brands, indent=2, ensure_ascii=False), "utf-8")
            print(f"    [checkpoint: {len(all_product_urls)} URLs, +{total_new} new products]")
        
        time.sleep(DELAY)
    
    save_progress()
    BRAND_FILE.write_text(json.dumps(brands, indent=2, ensure_ascii=False), "utf-8")
    
    total_on_site = sum(brand_counts.values())
    print(f"\n  Total products found on page 1s: {len(all_product_urls)}")
    print(f"  New products added: {total_new}")
    if total_on_site:
        print(f"  Estimated total on site: {total_on_site}")
    
    # Step 3: Fetch remaining pages for brands with > 24 products
    brands_needing_pages = []
    for brand in brands:
        count = brand.get("product_count", 0)
        if count > PER_PAGE:
            pages_needed = math.ceil(count / PER_PAGE)
            # Check which pages we already did
            done_pages = _progress.get("completed_pages", {}).get(brand["name"], [])
            for pg in range(2, pages_needed + 1):
                if pg not in done_pages:
                    brands_needing_pages.append((brand, pg))
    
    print(f"\n[3/4] Fetching {len(brands_needing_pages)} additional pages...")
    
    page_count = 0
    for brand, page_num in brands_needing_pages:
        name = brand["name"]
        url = f"{BASE}{brand['url']}?page={page_num}"
        page_count += 1
        print(f"  [{page_count}/{len(brands_needing_pages)}] {name} p{page_num}...", end=" ", flush=True)
        
        html = fetch(session, url)
        if not html:
            print("BLOCKED — skipping rest of brand")
            # Skip remaining pages for this brand
            time.sleep(DELAY * 3)
            continue
        
        products = extract_products_from_html(html, name)
        for p in products:
            if p.get("url"):
                all_product_urls.add(p["url"])
        
        added = save_brand_products(name, products)
        total_new += added
        
        print(f"+{len(products)} extracted, +{added} new (total URLs: {len(all_product_urls)})")
        
        # Track page progress
        if name not in _progress.get("completed_pages", {}):
            _progress.setdefault("completed_pages", {})[name] = []
        _progress["completed_pages"][name].append(page_num)
        _progress["total_urls"] = len(all_product_urls)
        
        # Save progress every 10 pages
        if page_count % 10 == 0:
            save_progress()
            print(f"    [checkpoint: {len(all_product_urls)} URLs, +{total_new} new products]")
        
        time.sleep(DELAY)
    
    # Step 4: Save final results
    print(f"\n[4/4] Saving final results...")
    
    # Save all URLs
    URL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(URL_FILE, "w") as f:
        for url in sorted(all_product_urls):
            f.write(url + "\n")
    print(f"  Saved {len(all_product_urls)} URLs to {URL_FILE.name}")
    
    save_progress()
    
    # Count total products in all JSON files
    total_products = 0
    for f in DATA_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text("utf-8"))
            if isinstance(data, list):
                total_products += len(data)
        except:
            pass
    
    print(f"\n{'=' * 60}")
    print(f"  DONE!")
    print(f"  {len(all_product_urls)} unique product URLs discovered")
    print(f"  {total_new} new products added this run")
    print(f"  {total_products} total products in catalog")
    print(f"  Restart the backend to reload: ./factory_reset.sh or ./start_console.sh")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
