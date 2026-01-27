
import json
import os
from pathlib import Path

# Setup paths
BASE_DIR = Path("backend")
VAULT_FILE = BASE_DIR / "data/vault/commercial_full_scan.json"
BLUEPRINTS_DIR = BASE_DIR / "data/blueprints"

# Brands map: Slug -> List of Keywords
BRAND_MAP = {
    "roland": ["Roland"],
    "boss": ["Boss"],
    "nord": ["Nord"],
    "moog": ["Moog"],
    "adam-audio": ["Adam Audio", "Adam"],
    "teenage-engineering": ["Teenage Engineering", "Teenage"],
    "universal-audio": ["Universal Audio", "Universal", "UAD"],
    "akai-professional": ["Akai", "Akai Professional"],
    "warm-audio": ["Warm Audio", "Warm"],
    "mackie": ["Mackie"],
    "yamaha": ["Yamaha"],
    "korg": ["Korg"],
    "arturia": ["Arturia"],
    "native-instruments": ["Native Instruments"],
    "sequential": ["Sequential", "Dave Smith"],
    "behringer": ["Behringer"],
    "shure": ["Shure"],
    "sennheiser": ["Sennheiser"],
    "neumann": ["Neumann"],
    "focusrite": ["Focusrite"],
    "presonus": ["Presonus"],
    "zoom": ["Zoom"],
    "alesis": ["Alesis"],
    "maudio": ["M-Audio", "M Audio"],
    "rode": ["Rode"],
    # Add more as needed based on blueprint file list
}

def normalize_slug(text):
    return text.lower().replace(" ", "-").replace("_", "-")

def run():
    print(f"Reading commercial scan from {VAULT_FILE}...")
    if not VAULT_FILE.exists():
        print(f"❌ File not found: {VAULT_FILE}")
        return

    with open(VAULT_FILE, 'r', encoding='utf-8') as f:
        products = json.load(f)

    print(f"Loaded {len(products)} products.")

    brand_buckets = {slug: [] for slug in BRAND_MAP.keys()}
    # Also catch-all for unknown
    brand_buckets["uncategorized"] = []

    for p in products:
        name = p.get('name', '').lower()
        matched = False
        
        # Heuristic matching
        for slug, keywords in BRAND_MAP.items():
            for kw in keywords:
                if kw.lower() in name:
                    brand_buckets[slug].append(p)
                    matched = True
                    break
            if matched: break
            
        if not matched:
            brand_buckets["uncategorized"].append(p)

    # Save to blueprints dir
    BLUEPRINTS_DIR.mkdir(parents=True, exist_ok=True)
    
    for slug, items in brand_buckets.items():
        if not items: continue
        
        # Naming convention: <slug>_commercial.json
        output_file = BLUEPRINTS_DIR / f"{slug}_commercial.json"
        
        # Wrap in expected format if needed, or just list
        # detailed implementation of _merge_with_global_data handles both list and dict with 'products'
        
        payload = {
            "brand_slug": slug,
            "source": "halilit_commercial_scan",
            "products": items
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            
        print(f"Saved {len(items)} items to {output_file.name}")

if __name__ == "__main__":
    run()
