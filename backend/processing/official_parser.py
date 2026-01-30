from bs4 import BeautifulSoup
from pathlib import Path
import json
import re


def parse_official_page(html_path: Path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    data = {}

    # 1. Product Name (Title)
    # Usually in a hero section or H1.
    # Adam Audio usually has a large H1 in the first module.
    h1 = soup.find("h1")
    if h1:
        data["name"] = h1.get_text(strip=True)

    # 2. Description
    # Strategy A: The ".product-overview .wysiwyg" block is the main bio/description
    desc_html = ""
    intro_div = soup.select_one(".product-overview .wysiwyg")
    if intro_div:
        desc_html = intro_div.get_text(separator=" ", strip=True)

    # Strategy B: Fallback to old "product-intro" if main overview is missing
    if not desc_html or len(desc_html) < 20:
        intro_div = soup.select_one(".product-intro .content")
        if intro_div:
            desc_html = intro_div.get_text(separator=" ", strip=True)

    # Strategy C: Fallback to meta description
    if not desc_html or len(desc_html) < 20:
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            desc_html = meta_desc.get("content", "")

    data["description"] = desc_html

    # 2b. Categories (New)
    # Extract from footer catalog structure
    category = "Studio Monitors"  # Default fallback
    sub_category = None

    # Locate the product in the footer catalog to find its series
    footer_catalog = soup.select_one(".footer-row.product-catalog")
    if footer_catalog and data.get("name"):
        product_name = data["name"]
        # Find a link with the product name text
        product_link = footer_catalog.find(
            string=lambda text: text and product_name.lower() in text.lower())
        if product_link:
            # Go up to the column
            col = product_link.find_parent("div", class_="col-sm-3")
            if col:
                serie_title = col.find(class_="serie-title")
                if serie_title:
                    category = serie_title.get_text(strip=True)

    data["category"] = category
    data["sub_category"] = sub_category

    # 3. Technical Data (Specs)
    specs = []
    tech_section = soup.find(id="technical-data")
    if tech_section:
        # It's an accordion list
        list_items = tech_section.select("li")
        for li in list_items:
            text = li.get_text(strip=True)
            if ":" in text:
                key, val = text.split(":", 1)
                specs.append({"key": key.strip(), "value": val.strip()})
            else:
                specs.append({"key": "Feature", "value": text})

    data["specs"] = specs

    # 4. Box Contents (Necessities / In the box)
    # Often found inside specs with key "Delivery Contents"
    box_contents = []
    for s in specs:
        if "Delivery Contents" in s["key"]:
            # Split by comma usually
            items = s["value"].split(",")
            box_contents = [i.strip() for i in items]

    data["box_contents"] = box_contents

    # 5. Related Products (Accessories / Family)
    related = []
    related_section = soup.select(".posts-teasers h4.post-title")
    for r in related_section:
        related.append(r.get_text(strip=True))

    data["related_products"] = related

    return data


if __name__ == "__main__":
    import sys
    # Test on a specific file
    test_path = Path(
        "backend/data/raw/official/adam-audio/2280897/official_page.html")
    if test_path.exists():
        result = parse_official_page(test_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Test file not found: {test_path}")
