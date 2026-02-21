#!/usr/bin/env python3
"""Test Selenium WebDriver to verify page loading"""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Chrome driver
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    url = "https://www.thomannmusic.com/rcf.html"
    logger.info(f"Loading: {url}")

    driver.get(url)
    time.sleep(5)  # Wait longer

    # Get page source
    page_source = driver.page_source

    logger.info(f"Page loaded, length: {len(page_source)} bytes")

    # Check if blocked
    if "403" in page_source or "Access Denied" in page_source or "Cloudflare" in page_source:
        logger.error("Page blocked by Cloudflare!")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Look for product links
    links = soup.find_all('a', href=True)
    logger.info(f"Found {len(links)} total links")

    # Filter for .htm product links
    product_links = [l for l in links if '.htm' in l.get('href', '')]
    logger.info(f"Found {len(product_links)} .htm product links")

    # Sample first few links
    for link in product_links[:5]:
        logger.info(f"  - {link.get('href', '')[:80]}")

    # Look for RCF specifically
    rcf_links = [l for l in product_links if 'rcf' in l.get(
        'href', '').lower()]
    logger.info(f"Found {len(rcf_links)} RCF product links")

    for link in rcf_links[:3]:
        logger.info(f"  - {link.get('href', '')}")

finally:
    driver.quit()
    logger.info("Driver closed")
