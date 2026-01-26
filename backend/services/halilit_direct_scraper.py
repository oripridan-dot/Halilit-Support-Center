import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
from typing import List, Dict, Optional

class HalilitDirectScraper:
    """
    Directly scrapes product listings from Halilit's brand pages.
    Used as a fallback when no deep scraper is available or for "No Deep Map" brands.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.cdn_base = "https://d3m9l0v76dty0.cloudfront.net" # Fallback if needed
        # Ensure output directory exists
        os.makedirs("backend/data/blueprints", exist_ok=True)

    def scrape_brand(self, brand_slug: str, brand_url: str) -> Optional[str]:
        print(f"📡 Establishing Direct Uplink: {brand_slug.upper()} ({brand_url})")
        
        all_products = []
        page = 1
        has_next_page = True
        
        # Safety limit for pagination
        max_pages = 20 
        
        while has_next_page and page <= max_pages:
            paged_url = f"{brand_url}?page={page}" if page > 1 else brand_url
            if page > 1:
                print(f"   Scanning page {page}...")
            
            try:
                res = self.session.get(paged_url)
                if res.status_code != 200:
                    print(f"   ❌ Failed to load page {page}: {res.status_code}")
                    break
                
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Check pagination
                next_btn = soup.select_one('.pagination a.next_page')
                has_next_page = bool(next_btn)
                
                # Extract products
                product_nodes = soup.select('.layout_list_item')
                
                if not product_nodes:
                    if page == 1:
                        print(f"   ⚠️  No products found on page 1.")
                    break
                
                initial_count = len(all_products)
                for node in product_nodes:
                    product_data = self._parse_node(node, brand_slug)
                    # Deduplication check
                    if product_data and not any(p['id'] == product_data['id'] for p in all_products):
                        all_products.append(product_data)
                
                if len(all_products) == initial_count:
                     # No new products found on this page? Suspicious.
                     # But maybe duplicates within page.
                     pass

                page += 1
                time.sleep(0.5) # Be nice
                
            except Exception as e:
                print(f"   ❌ Error on page {page}: {e}")
                break
        
        if not all_products:
            print(f"   ❌ {brand_slug.upper()}: No products found.")
            return None
            
        print(f"✅ Mission Complete: {len(all_products)} Lifeforms Mapped.")
        
        # Save Commercial Blueprint
        output_path = f"backend/data/blueprints/{brand_slug}_commercial.json"
        
        # Ensure directory exists (just in case)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(all_products, f, indent=2)
            
        print(f"   Commercial Blueprint saved to: {output_path}")
        return output_path

    def _parse_node(self, node, brand_slug) -> Optional[Dict]:
        try:
            # unique ID from data attribute (Halilit Internal ID)
            halilit_id = node.get('data-item-code')
            
            # The 'class="title_with_brand"' element usually contains the name
            name_el = node.select_one('.title_with_brand')
            name = name_el.text.strip() if name_el else "Unknown Product"
            
            # Image
            img_el = node.select_one('.img_wrapper img')
            img_url = img_el['src'] if img_el else ""
            if img_url and not img_url.startswith('http'):
                 img_url = f"{self.cdn_base}{img_url}"
            
            # Pricing Extraction (Complex)
            pricing = {
                "currency": "ILS",
                "regular_price": None, # Black
                "eilat_price": None,   # Red
                "sale_price": None,    # Grey/Crossed (List Price)
            }
            
            price_container = node.select_one('.price')
            if price_container:
                # 1. Try to find Eilat price (Red)
                # Look for specific class or text indicating Eilat
                eilat_node = price_container.select_one('.yilat_price_value, .eilat-price')
                if eilat_node:
                    pricing['eilat_price'] = self._extract_price(eilat_node.get_text())

                # 2. Try to find List Price / Old Price (Grey/Crossed)
                old_price_node = price_container.select_one('.old_price_value, .old-price, strike, del')
                if old_price_node:
                    pricing['sale_price'] = self._extract_price(old_price_node.get_text())
                
                # 3. Main Price (Black/Regular)
                # Usually the remaining text or specific class
                main_price_node = price_container.select_one('.price_value, .regular-price')
                if main_price_node:
                     pricing['regular_price'] = self._extract_price(main_price_node.get_text())
                else:
                    # Fallback: Extract largest number from container text if not found specific
                    pricing['regular_price'] = self._extract_price(price_container.get_text())

            # Link
            link_el = node.find('a', href=True)
            rel_url = link_el['href'].strip() if link_el else ""
            if rel_url and not rel_url.startswith('/'):
                 rel_url = f"/{rel_url}"

            full_url = f"https://www.halilit.com{rel_url}" if rel_url else ""
            
            # Construct ID & SKU
            # Accessing SKU from raw HTML might be tricky if not in DOM. 
            # We'll treat item_code as internal ID. 
            # SKU might be same as item code or hidden.
            
            # Fallback ID generation
            if not halilit_id:
                 if rel_url:
                     halilit_id = rel_url.split('/')[-1]
                 else:
                     halilit_id = f"unknown_{int(time.time())}"

            # SKU mapping (User requested SKU)
            # Often data-item-code IS the internal SKU/ID.
            sku = halilit_id

            # Sanitize ID for System
            safe_id = f"{brand_slug}_{halilit_id}".lower()
            
            # Construct Result matching Blueprint schema
            return {
                "id": safe_id,
                "name": name,
                "url": full_url,
                "image": img_url,
                "halilit_id": halilit_id,
                "sku": sku,
                "pricing": pricing,  # New Rich Pricing Object
                "description": name, # Placeholder
                "category": "general"
            }
            
        except Exception as e:
            print(f"   ⚠️ Skipping node: {e}")
            return None

    def _extract_price(self, text: str) -> Optional[float]:
        """Extracts the first valid number from a string."""
        if not text: return None
        try:
            # Remove currency symbol and commas
            clean = re.sub(r'[^\d.]', '', text.replace(',', ''))
            return float(clean) if clean else None
        except:
            return None
