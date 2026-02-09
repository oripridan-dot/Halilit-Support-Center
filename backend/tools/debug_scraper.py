import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


def test_scrape(brand="Arturia"):
    print(f"Testing scrape for {brand}...")
    encoded_brand = quote(brand)
    url = f"https://www.halilit.com/search?q={encoded_brand}&page=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    resp = requests.get(url, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"URL: {resp.url}")

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Check selectors from unified_agent_orchestrator_v73
    items = soup.select(".box, .item, .product_item, .product_box")
    print(f"Found {len(items)} items with selectors")

    for i, item in enumerate(items[:5]):
        title_el = item.select_one(
            ".title, .product-title, h3, h4, .title_with_brand, .item-title")
        name = title_el.get_text(strip=True) if title_el else "NO TITLE"

        id_el = item.get("id")  # item_id_...

        print(f"Item {i}: {name} (ID: {id_el})")

        # Test loose validation
        if brand.lower() not in name.lower() and brand.replace(" ", "").lower() not in name.lower():
            print(
                f"   -> REJECTED by loose brand check? Name: '{name}' vs Brand: '{brand}'")
        else:
            print(f"   -> ACCEPTED by loose brand check")


if __name__ == "__main__":
    test_scrape(brand="ארטוריה")
