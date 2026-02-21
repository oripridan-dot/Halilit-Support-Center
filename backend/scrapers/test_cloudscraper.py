#!/usr/bin/env python3
"""Test CloudScraper to verify page fetching"""

import logging
import cloudscraper
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize CloudScraper
scraper = cloudscraper.create_scraper()

try:
    url = "https://www.thomannmusic.com/rcf.html"
    logger.info(f"Loading: {url}")

    response = scraper.get(url, timeout=30)

    logger.info(f"Status: {response.status_code}")
    logger.info(f"Content length: {len(response.text)} bytes")

    if response.status_code == 200:
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for product links
        all_links = soup.find_all('a', href=True)
        logger.info(f"Total links: {len(all_links)}")

        # Filter for .htm product links
        product_links = [l for l in all_links if '.htm' in l.get('href', '')]
        logger.info(f".htm product links: {len(product_links)}")

        # Sample first few links
        for link in product_links[:10]:
            href = link.get('href', '')
            text = link.get_text(strip=True)[:50]
            logger.info(f"  - {href[:70]}")

        # Look for RCF specifically
        rcf_links = [l for l in product_links if 'rcf' in l.get(
            'href', '').lower()]
        logger.info(f"RCF product links: {len(rcf_links)}")

        for link in rcf_links[:5]:
            logger.info(f"  - {link.get('href', '')}")
    else:
        logger.error(f"Failed to fetch: {response.status_code}")
        if "Cloudflare" in response.text:
            logger.error("Page is blocked by Cloudflare!")

except Exception as e:
    logger.error(f"Error: {e}")
    import traceback
    traceback.print_exc()
