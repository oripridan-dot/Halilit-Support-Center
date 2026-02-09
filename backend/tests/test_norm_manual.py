import json
from pathlib import Path


def normalize(p):
    # ID
    pid = p.get('id') or p.get('halilit_id') or "unknown"

    # Name
    name = p.get('name') or p.get('product_name') or "Unknown"

    # Category
    cat = p.get('category')
    if not cat:
        tax = p.get('taxonomy', {})
        cat = tax.get('canonical_category', 'Uncategorized')

    # Price
    price = p.get('price')
    if not price:
        price = p.get('price_il', 0)

    # Image
    img = p.get('image_url')
    if not img:
        # Try official images
        off_imgs = p.get('official_images', [])
        if off_imgs and isinstance(off_imgs, list):
            # Find hero
            for i in off_imgs:
                if i.get('display_purpose') == 'hero':
                    img = i.get('url')
                    break
            # Fallback to first
            if not img and len(off_imgs) > 0:
                img = off_imgs[0].get('url')

    if not img:
        # Try display
        disp = p.get('display', {})
        hero = disp.get('hero_image')
        if hero:
            if isinstance(hero, dict):
                img = hero.get('url')
            elif isinstance(hero, str):
                img = hero

    return {
        "id": pid,
        "name": name,
        "category": cat,
        "price": price,
        "image_url": img
    }


try:
    with open('../frontend/public/data/nord.json') as f:
        data = json.load(f)
        products = data.get('products', [])
        print(f"Loaded {len(products)} products from nord.json")

        valid = 0
        for p in products:
            n = normalize(p)
            if n['price'] > 0 and n['image_url']:
                valid += 1
                # print(f"Valid: {n['name']} | {n['price']} | {n['image_url'][:30]}...")
            else:
                pass
                # print(f"Invalid: {n['name']} | Price: {n['price']} | Img: {n['image_url']}")

        print(f"Valid products: {valid}/{len(products)}")

except Exception as e:
    print(e)
