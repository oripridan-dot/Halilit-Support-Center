import json
import os
import glob
import re

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def sync():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    public_data_dir = os.path.join(root_dir, 'frontend', 'public', 'data')
    galaxy_db_path = os.path.join(public_data_dir, 'galaxy_db.json')
    index_path = os.path.join(public_data_dir, 'index.json')
    search_index_path = os.path.join(public_data_dir, 'search_index.json')

    print(f"Loading {galaxy_db_path}...")
    try:
        with open(galaxy_db_path, 'r') as f:
            galaxy = json.load(f)
    except FileNotFoundError:
        print("Error: galaxy_db.json not found. Run rebuild_library.py first.")
        return

    products = galaxy.get('products', [])
    print(f"Found {len(products)} products.")

    # Group by brand
    brands_data = {}
    search_items = []

    for p in products:
        brand_name = p.get('brand')
        if not brand_name:
            continue

        brand_id = slugify(brand_name)
        if brand_id not in brands_data:
            brands_data[brand_id] = {
                'name': brand_name,
                'products': []
            }
        brands_data[brand_id]['products'].append(p)

        # Build search item
        search_items.append({
            "id": p.get('id'),
            "name": p.get('name'),
            "brand": brand_name,
            "brand_id": brand_id,
            "price": p.get('price'),
            "slug": p.get('slug') or f"/{brand_id}/{slugify(p.get('name',''))}", # Fallback/Simple slug
            "image": p.get('images', {}).get('main', ''),
            "in_stock": p.get('stockStatus') == 'in_stock'
        })

    # Write individual brand files and build index
    index_brands = []

    generated_files = set()

    for brand_id, data in brands_data.items():
        filename = f"{brand_id}.json"
        filepath = os.path.join(public_data_dir, filename)

        # Write just the list of products as that seems to be the format of legacy files like roland.json
        with open(filepath, 'w') as f:
            json.dump(data['products'], f, indent=2)

        print(f"Wrote {len(data['products'])} products to {filename}")
        generated_files.add(filename)

        index_brands.append({
            "id": brand_id,
            "name": data['name'],
            "product_count": len(data['products']),
            "data_file": filename
        })

    # Sort brands by name
    index_brands.sort(key=lambda x: x['name'])

    # Write index.json
    index_content = {
        "version": "5.2.0",
        "build_timestamp": galaxy.get("generatedAt", ""),
        "total_products": len(products),
        "brands": index_brands
    }

    with open(index_path, 'w') as f:
        json.dump(index_content, f, indent=2)
    print(f"Updated index.json with {len(index_brands)} brands.")
    generated_files.add("index.json")

    # Write search_index.json
    with open(search_index_path, 'w') as f:
        json.dump(search_items, f, indent=2)
    print(f"Updated search_index.json with {len(search_items)} items.")
    generated_files.add("search_index.json")

    # Clean up old files
    # Keep specific system files
    keep_files = {
        "galaxy_db.json",
        "search_index.json",
        "taxonomy.json",
        "index.json"
    }

    all_json = glob.glob(os.path.join(public_data_dir, "*.json"))
    for fpath in all_json:
        fname = os.path.basename(fpath)
        if fname in keep_files:
            continue

        if fname not in generated_files:
            print(f"Deleting unauthorized/orphan file: {fname}")
            os.remove(fpath)

if __name__ == "__main__":
    sync()
