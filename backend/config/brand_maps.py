# backend/config/brand_maps.py
"""
Brand Maps - Configuration for how to read different brand websites.
Maps each brand to its product listing structure (selectors, URLs, etc.)
"""

BRAND_MAPS = {
    "roland": {
        "start_url": "https://www.roland.com/global/products/",
        "logo_url": "https://static.roland.com/assets/images/logo.svg",
        "selectors": {
            "group": ".product-group", 
            "group_title": ".product-group__title",
            "product": ".product-group__item",
            "name": ".product-group__item-name",
            "desc": ".product-group__item-description",
            "link": "a.product-group__item-link",
            "image": "img.product-group__item-image"
        }
    },
    "boss": {
        "start_url": "https://www.boss.info/global/products/",
        "logo_url": "https://static.roland.com/assets/images/logo_boss.svg",
        "selectors": {
            "group": ".product-group",
            "group_title": ".product-group__title",
            "product": ".product-group__item",
            "name": ".product-group__item-name",
            "desc": ".product-group__item-description",
            "link": "a.product-group__item-link",
            "image": "img.product-group__item-image"
        }
    },
    "nord": {
        "start_url": "https://www.nordkeyboards.com/products",
        "logo_url": "https://www.nordkeyboards.com/sites/all/themes/nord/logo.png",
        "selectors": {
            "group": None,  # Flat list
            # Updated for Next.js site structure (Jan 2026)
            "product": "div[class*='ProductCardList'] a[href^='/products/']",
            "name": "h2",
            "desc": "p[class*='Description']",
            "link": None, # The product element itself is the link
            "image": "div[class*='ProductImageWrapper'] img"
        }
    },
    "moog": {
        "start_url": "https://www.moogmusic.com/products",
        "logo_url": "https://www.moogmusic.com/themes/custom/moog/logo.svg",
        "selectors": {
            "group": None,  # Flat list
            "product": ".product-card",
            "name": ".product-card__title",
            "desc": ".product-card__description",
            "link": "a.product-card__link",
            "image": "img.product-card__image"
        }
    }
}
