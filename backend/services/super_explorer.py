# backend/services/super_explorer.py
"""
Super Explorer - The Discovery Layer

Maps the global terrain of brand product listings and cross-references
with Halilit to enrich product metadata before the Genesis Builder
constructs the app structure.

Workflow:
  1. Read brand configuration (selectors, URLs)
  2. Scrape brand website to get all products
  3. Check Halilit for pricing/availability
  4. Save as "blueprint" JSON for Genesis Builder to consume
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import os
import time
from typing import Dict, List, Optional
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.brand_maps import BRAND_MAPS
from services.halilit_client import HalilitClient


class SuperExplorer:
    """
    Scans brand websites and enriches product data with Halilit intelligence.
    
    Produces "blueprint" JSON files that are consumed by GenesisBuilder
    to construct the app's file structure.
    """
    
    def __init__(self):
        self.halilit = HalilitClient()
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'HSC-Explorer/1.0 (Genesis Protocol)'
        }
        
        # Ensure output directory exists
        os.makedirs("backend/data/blueprints", exist_ok=True)

    def scan_brand(self, brand_key: str) -> Optional[str]:
        """
        Scan a brand's website and generate a blueprint.
        
        Args:
            brand_key: Brand identifier (e.g., "roland")
            
        Returns:
            Path to blueprint JSON file, or None on failure
        """
        if brand_key not in BRAND_MAPS:
            print(f"❌ No map found for {brand_key}")
            return None

        config = BRAND_MAPS[brand_key]
        print(f"📡 Establishing Uplink: {brand_key.upper()} ({config['start_url']})")
        
        try:
            response = self.session.get(config['start_url'], timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            blueprint = []
            
            # Logic for grouped lists (like Roland's category pages)
            if config['selectors'].get('group'):
                print(f"   Mode: Grouped Categories")
                groups = soup.select(config['selectors']['group'])
                print(f"   Found {len(groups)} groups")
                
                for g in groups:
                    group_title_elem = g.select_one(config['selectors']['group_title'])
                    category = group_title_elem.text.strip() if group_title_elem else "General"
                    
                    products = g.select(config['selectors']['product'])
                    print(f"   └─ {category}: {len(products)} products")
                    
                    for p in products:
                        item = self._parse_product_node(p, config, brand_key, category)
                        if item:
                            blueprint.append(item)
            else:
                # Logic for flat lists
                print(f"   Mode: Flat Product List")
                products = soup.select(config['selectors']['product'])
                print(f"   Found {len(products)} products")
                
                for p in products:
                    item = self._parse_product_node(p, config, brand_key, "General")
                    if item:
                        blueprint.append(item)
                    
                    # Rate limiting to be respectful
                    time.sleep(0.1)

            # Save Blueprint
            output_path = f"backend/data/blueprints/{brand_key}_blueprint.json"
            with open(output_path, 'w') as f:
                json.dump(blueprint, f, indent=2)
            
            print(f"✅ Mission Complete: {len(blueprint)} Lifeforms Mapped.")
            print(f"   Blueprint saved to: {output_path}")
            return output_path

        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Severed: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            return None

    def _parse_product_node(self, element, config: Dict, brand: str, category: str) -> Optional[Dict]:
        """
        Parse a single product element from the DOM.
        
        Args:
            element: BeautifulSoup element
            config: Brand configuration (selectors)
            brand: Brand name
            category: Product category
            
        Returns:
            Product dict or None if parsing fails
        """
        sel = config['selectors']
        
        try:
            # Extract text fields
            name_elem = element.select_one(sel['name'])
            desc_elem = element.select_one(sel['desc'])
            
            if not name_elem:
                return None
                
            name = name_elem.text.strip()
            desc = desc_elem.text.strip() if desc_elem else ""
            
            # Image extraction
            img_tag = element.select_one(sel['image'])
            raw_img_url = ""
            
            if img_tag:
                # Try data-src first (lazy loading), then src
                raw_img_url = img_tag.attrs.get('data-src', '') or img_tag.attrs.get('src', '')
            
            # Fix relative URLs
            if raw_img_url:
                if not raw_img_url.startswith('http'):
                    full_img_url = urljoin(config['start_url'], raw_img_url)
                else:
                    full_img_url = raw_img_url
            else:
                full_img_url = ""

            # INTELLIGENCE CHECK (Halilit)
            intel = self.halilit.check_availability(brand, name)

            return {
                "id": f"{brand}-{name.replace(' ', '-').replace('/', '').lower()}",
                "brand": brand,
                "name": name,
                "category": category,
                "short_description": desc,
                "remote_image": full_img_url,
                "intelligence": intel
            }
            
        except AttributeError:
            return None
        except Exception as e:
            return None

    def scan_all_brands(self) -> Dict[str, str]:
        """
        Scan all configured brands.
        
        Returns:
            Dict mapping brand names to blueprint file paths
        """
        results = {}
        for brand_key in BRAND_MAPS.keys():
            print()
            blueprint_path = self.scan_brand(brand_key)
            if blueprint_path:
                results[brand_key] = blueprint_path
            time.sleep(1)  # Be respectful to servers
        
        return results


if __name__ == "__main__":
    explorer = SuperExplorer()
    
    # Scan a single brand
    # explorer.scan_brand("roland")
    
    # Or scan all brands
    results = explorer.scan_all_brands()
    print(f"\n📊 Summary: {len(results)} brands processed")
    for brand, path in results.items():
        print(f"   ✓ {brand}: {path}")
