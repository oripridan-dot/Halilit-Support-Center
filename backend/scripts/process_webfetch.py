#!/usr/bin/env python3
"""
Process WebFetch markdown files into product JSON data.

Usage:
    python3 process_webfetch.py <markdown_file_or_directory>
    
    # Process a single file
    python3 process_webfetch.py /tmp/webfetch/roland-p5.md
    
    # Process all .md files in a directory
    python3 process_webfetch.py /tmp/webfetch/
"""

import json, re, sys, hashlib
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "frontend" / "public" / "data"

# Brand detection patterns
BRAND_DETECT = {
    'roland': 'roland', 'boss': 'boss', 'pearl': 'pearl',
    'mackie': 'mackie', 'esp': 'esp', 'rode': 'rode',
    'marshall': 'marshall', 'steinberg': 'steinberg',
    'presonus': 'presonus', 'remo': 'remo', 'guild': 'guild',
    'rcf': 'rcf', 'paiste': 'paiste cymbals', 'bespeco': 'bespeco',
    'beyerdynamic': 'beyerdynamic', 'akg': 'akg',
    'cordoba': 'cordoba', 'shure': 'shure', 'moog': 'moog',
    'sennheiser': 'sennheiser', 'audio-technica': 'audio-technica',
    'korg': 'korg', 'behringer': 'behringer', 'on stage': 'on stage',
    'adam audio': 'adam audio', 'allen & heath': 'allen heath',
    'washburn': 'washburn', 'oscar schmidt': 'oscar schmidt',
    'samson': 'samson', 'dbx': 'dbx', 'avid': 'avid',
    'zildjian': 'zildjian', 'sabian': 'sabian', 'vic firth': 'vic firth',
    'promark': 'promark', 'ludwig': 'ludwig', 'tama': 'tama',
    'ibanez': 'ibanez', 'jackson': 'jackson', 'ltd': 'ltd',
    'takamine': 'takamine', 'taylor': 'taylor', 'martin': 'martin',
    'universal audio': 'universal audio', 'heritage audio': 'heritage audio',
    'warm audio': 'warm audio', 'akai': 'akai professional',
    "d'addario": "d'addario", 'vintage': 'vintage', 'medeli': 'medeli',
    'novation': 'novation', 'nord': 'nord', 'oberheim': 'oberheim',
    'asm': 'asm', 'gibson': 'gibson', 'solar': 'solar',
    'gon bops': 'gon bops', 'mtd': 'mtd', 'dynaudio': 'dynaudio',
    'magma': 'magma', 'austrian audio': 'austrian audio',
    "roger's": "roger's", 'fzone': 'fzone', 'rode x': 'rode x',
    'm-audio': 'm-audio', 'fender': 'fender', 'd\'angelico': "d'angelico",
    'charvel': 'charvel', 'gretsch': 'gretsch', 'evh': 'evh',
}


def detect_brand(name):
    """Detect brand from product name."""
    name_lower = name.lower()
    for pattern, brand in sorted(BRAND_DETECT.items(), key=lambda x: -len(x[0])):
        if name_lower.startswith(pattern):
            return brand
    return 'other'


def extract_products(text):
    """Extract products from Halilit page markdown."""
    products = []
    seen = set()
    
    # Find all /items/ links
    item_re = re.compile(r'\[([^\]]+)\]\((https://www\.halilit\.com/items/(\d+)-[^)]+)\)')
    
    # Group by URL
    url_groups = defaultdict(list)
    for m in item_re.finditer(text):
        url_groups[m.group(2)].append(m.group(1).strip())
    
    for url, texts in url_groups.items():
        if url in seen:
            continue
        seen.add(url)
        
        slug = url.split('/items/')[-1]
        item_id = slug.split('-')[0]
        
        title = ''
        description = ''
        sku = ''
        price_il = 0.0
        price_eilat = 0.0
        
        for t in texts:
            # SKU pattern
            sku_m = re.match(r'^([\w]+-[\w]+)\s*--$', t)
            if sku_m:
                sku = sku_m.group(1)
                continue
            
            # Price
            price_m = re.search(r'מחיר\s*([\d,]+)\s*₪', t)
            eilat_m = re.search(r'באילת\s*([\d,]+)\s*₪', t)
            if price_m:
                try: price_il = float(price_m.group(1).replace(',', ''))
                except: pass
                if eilat_m:
                    try: price_eilat = float(eilat_m.group(1).replace(',', ''))
                    except: pass
                continue
            
            # Skip nav/menu items
            if len(t) < 5 or t in ('-', '+', '0'):
                continue
            
            # Title or description
            if not title:
                title = t
            elif not description and len(t) > 10:
                description = t
        
        if not title:
            title = slug.split('-', 1)[-1].replace('-', ' ').title() if '-' in slug else slug
        
        brand = detect_brand(title)
        
        product = {
            'halilit_id': f'web-{item_id}',
            'product_name': title,
            'brand': brand,
            'price_il': price_il,
            'price_eilat': price_eilat,
            'halilit_url': url,
            'sku': sku or None,
            'model_number': None,
            'official_name': None,
            'official_specs': None,
            'official_description': None,
            'official_images': None,
            'official_url': None,
            'reviews': None,
            'review_synthesis': None,
            'average_rating': None,
            'status': 'scraped',
            'pipeline_phase': 'enriched' if price_il > 0 else 'discovered',
            'created_at': None,
            'last_updated': None,
        }
        
        if description:
            product['description_short'] = description
        
        products.append(product)
    
    return products


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "other"


def save_products(products):
    """Save products to brand JSON files, merging with existing."""
    # Load existing IDs and names
    existing_ids = set()
    existing_names = set()
    
    for f in DATA_DIR.glob('*.json'):
        if f.name in ('inventory.json', 'sample.json', '_galaxy_map.json'):
            continue
        try:
            data = json.loads(f.read_text('utf-8'))
            prods = data if isinstance(data, list) else data.get('products', [])
            for p in prods:
                if p.get('halilit_id'):
                    existing_ids.add(p['halilit_id'])
                if p.get('product_name'):
                    existing_names.add(p['product_name'].lower().strip())
        except:
            pass
    
    # Group new products by brand
    brand_new = defaultdict(list)
    skipped = 0
    for p in products:
        if p['halilit_id'] in existing_ids:
            skipped += 1
            continue
        if p['product_name'].lower().strip() in existing_names:
            skipped += 1
            continue
        brand_new[p['brand']].append(p)
    
    # Save to files
    saved = 0
    for brand, new_prods in brand_new.items():
        filename = slugify(brand) + '.json'
        filepath = DATA_DIR / filename
        
        # Try to find existing file with matching name
        for f in DATA_DIR.glob('*.json'):
            if f.stem.lower().replace(' ', '-') == slugify(brand):
                filepath = f
                break
        
        # Load existing
        existing = []
        if filepath.exists():
            try:
                data = json.loads(filepath.read_text('utf-8'))
                existing = data if isinstance(data, list) else data.get('products', [])
            except:
                pass
        
        existing.extend(new_prods)
        filepath.write_text(json.dumps(existing, indent=2, ensure_ascii=False), 'utf-8')
        saved += len(new_prods)
    
    return saved, skipped


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 process_webfetch.py <file_or_dir>")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    
    if path.is_dir():
        files = sorted(path.glob('*.md'))
    elif path.is_file():
        files = [path]
    else:
        # Try reading from stdin
        text = sys.stdin.read()
        products = extract_products(text)
        saved, skipped = save_products(products)
        print(f"Extracted {len(products)} products, saved {saved}, skipped {skipped} (duplicates)")
        return
    
    all_products = []
    for f in files:
        text = f.read_text('utf-8')
        products = extract_products(text)
        all_products.extend(products)
        print(f"  {f.name}: {len(products)} products")
    
    saved, skipped = save_products(all_products)
    print(f"\nTotal: {len(all_products)} extracted, {saved} saved, {skipped} skipped")
    
    # Final count
    total = 0
    for f in DATA_DIR.glob('*.json'):
        if f.name in ('inventory.json', 'sample.json', '_galaxy_map.json'):
            continue
        try:
            data = json.loads(f.read_text('utf-8'))
            prods = data if isinstance(data, list) else data.get('products', [])
            total += len(prods)
        except:
            pass
    print(f"Total products in catalog: {total}")


if __name__ == "__main__":
    main()
