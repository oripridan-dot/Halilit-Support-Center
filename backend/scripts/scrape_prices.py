"""
Batch price scraper — scrapes real prices from Halilit.com for all products
that have a halilit_url but no price.

Writes prices back into frontend/public/data/*.json files.
"""

from bs4 import BeautifulSoup
import requests
import json
import glob
import time
import re
import sys
import os
import logging
from pathlib import Path

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("PriceScraper")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "he-IL,he;q=0.9,en;q=0.8",
    "Referer": "https://www.halilit.com/",
}

FRONTEND_DATA = Path(__file__).parent.parent.parent / \
    "frontend" / "public" / "data"


def extract_price_from_page(url: str, session: requests.Session) -> dict:
    """Scrape a single Halilit product page for price + SKU."""
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}"}

        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract JSON-LD
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                items = []
                if "@graph" in data:
                    items = [i for i in data["@graph"]
                             if i.get("@type") == "Product"]
                elif data.get("@type") == "Product":
                    items = [data]

                for item in items:
                    offers = item.get("offers", {})
                    if isinstance(offers, list):
                        offers = offers[0] if offers else {}
                    price = offers.get("price", 0)
                    if price:
                        try:
                            price = float(price)
                        except (ValueError, TypeError):
                            price = 0

                    sku = item.get("sku", "")
                    name = item.get("name", "")

                    if price > 0:
                        return {
                            "price": price,
                            "sku": sku,
                            "name": name,
                            "price_eilat": round(price / 1.17, 2),
                        }
            except (json.JSONDecodeError, TypeError):
                continue

        return {"error": "No price in JSON-LD"}
    except requests.RequestException as e:
        return {"error": str(e)}


def main():
    session = requests.Session()

    # Gather all products that need prices
    json_files = sorted(glob.glob(str(FRONTEND_DATA / "*.json")))
    logger.info(f"Found {len(json_files)} brand files in {FRONTEND_DATA}")

    total_need = 0
    total_scraped = 0
    total_success = 0
    total_failed = 0

    for jf in json_files:
        brand_name = Path(jf).stem
        try:
            products = json.load(open(jf))
        except (json.JSONDecodeError, IOError):
            continue

        if not isinstance(products, list):
            continue

        # Find products needing prices
        needs_price = []
        for i, p in enumerate(products):
            price = p.get("price") or p.get("price_il") or 0
            url = p.get("halilit_url", "")
            if (not price or float(price) <= 0) and url and url.startswith("http"):
                needs_price.append((i, url))

        if not needs_price:
            continue

        total_need += len(needs_price)
        logger.info(
            f"[{brand_name}] {len(needs_price)} products need prices (of {len(products)} total)")

        modified = False
        for idx, (prod_idx, url) in enumerate(needs_price):
            result = extract_price_from_page(url, session)
            total_scraped += 1

            if "price" in result and result["price"] > 0:
                products[prod_idx]["price"] = result["price"]
                products[prod_idx]["price_il"] = result["price"]
                products[prod_idx]["price_eilat"] = result.get(
                    "price_eilat", 0)
                if result.get("sku"):
                    products[prod_idx]["sku"] = result["sku"]
                modified = True
                total_success += 1
            else:
                total_failed += 1

            # Rate limiting — be respectful
            time.sleep(0.3)

            # Progress logging every 50 products
            if total_scraped % 50 == 0:
                logger.info(
                    f"Progress: {total_scraped}/{total_need} scraped, {total_success} success, {total_failed} failed")

        # Write back
        if modified:
            with open(jf, "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            logger.info(f"[{brand_name}] Updated {jf}")

    logger.info(f"\n=== COMPLETE ===")
    logger.info(f"Products needing prices: {total_need}")
    logger.info(f"Successfully scraped: {total_success}")
    logger.info(f"Failed: {total_failed}")
    logger.info(f"Success rate: {100*total_success/max(total_scraped,1):.1f}%")


if __name__ == "__main__":
    main()
