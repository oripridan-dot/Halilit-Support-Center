#!/usr/bin/env python3
"""
Visual Factory - Image Scraper (v3.7.4)
Extracts product images and brand logos during discovery phase.
Part of the early scrape pipeline.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VisualFactory:
    """
    Extracts visual assets (images, logos) during product discovery.
    Runs during early scrape phase to populate image_url and images fields.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'HSC-VisualFactory/1.0 (image extraction)'
        }
        self.timeout = 10
    
    def scrape_product_image_from_url(self, product_url: str) -> Optional[str]:
        """
        Scrape product image URL from a product page.
        """
        try:
            response = self.session.get(product_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Common image selectors across brands
            selectors = [
                'img[alt*="product"]',
                'img[class*="product"]',
                'figure img',
                'img[class*="main"]',
                'picture img',
                'img.hero',
                'img.featured',
            ]
            
            for selector in selectors:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    img_url = urljoin(product_url, img['src'])
                    return img_url
            
            # Fallback: get first large image
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src and any(x in src.lower() for x in ['product', 'image', 'photo']):
                    return urljoin(product_url, src)
            
            return None
        except Exception as e:
            logger.debug(f"Failed to scrape image from {product_url}: {e}")
            return None
    
    def extract_logo_from_homepage(self, brand_url: str) -> Optional[str]:
        """
        Extract brand logo from brand homepage.
        """
        try:
            response = self.session.get(brand_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Common logo selectors
            selectors = [
                'img[alt*="logo"]',
                'img.logo',
                'img[class*="logo"]',
                'header img',
                'nav img',
            ]
            
            for selector in selectors:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    return urljoin(brand_url, img['src'])
            
            return None
        except Exception as e:
            logger.debug(f"Failed to scrape logo from {brand_url}: {e}")
            return None
    
    def enrich_products_with_images(
        self,
        brand: str,
        products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Enrich products with scraped image URLs.
        """
        enriched = []
        
        for product in products:
            # Skip if already has good image
            if product.get("image_url") and "placeholder" not in product["image_url"]:
                enriched.append(product)
                continue
            
            # Try to scrape image if product has URL
            if product.get("url"):
                image_url = self.scrape_product_image_from_url(product["url"])
                if image_url:
                    product["image_url"] = image_url
                    product["images"] = [
                        {
                            "url": image_url,
                            "type": "main",
                            "alt_text": f"{product.get('name')} main product image",
                            "description": f"Scraped from {brand} website"
                        }
                    ]
                    logger.info(f"✅ Scraped image for {product.get('name')}")
            
            enriched.append(product)
        
        return enriched


def populate_with_real_images(brands: List[str] = None) -> int:
    """
    Run visual factory to extract real images from brand websites.
    """
    if not brands:
        brands = ["boss", "nord", "moog", "mackie"]
    
    factory = VisualFactory()
    data_dir = Path("/workspaces/hsc-jit-v3/frontend/public/data")
    total_images = 0
    
    print("📷 VISUAL FACTORY - Real Image Extraction\n")
    print("Scraping product images from brand websites...\n")
    
    for brand in brands:
        catalog_path = data_dir / f"{brand}.json"
        
        if not catalog_path.exists():
            print(f"⏭️  {brand.upper():20} | Catalog not found")
            continue
        
        try:
            with open(catalog_path, "r") as f:
                catalog = json.load(f)
        except Exception as e:
            print(f"❌ {brand.upper():20} | Failed to load: {e}")
            continue
        
        products = catalog.get("products", [])
        before = sum(1 for p in products if p.get("image_url"))
        
        # Enrich with scraped images
        products = factory.enrich_products_with_images(brand, products)
        
        after = sum(1 for p in products if p.get("image_url"))
        added = after - before
        
        catalog["products"] = products
        
        with open(catalog_path, "w") as f:
            json.dump(catalog, f, indent=2)
        
        print(f"✅ {brand.upper():20} | {before:2} → {after:2} products with images (+{added:2})")
        total_images += added
    
    print(f"\n🎉 SUCCESS: {total_images} product images extracted from brand websites\n")
    
    return total_images


if __name__ == "__main__":
    populate_with_real_images()
