# backend/services/halilit_direct_scraper.py
import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
import logging
from typing import Dict, Optional, Set

# Setup logging
logger = logging.getLogger(__name__)

class HalilitDirectScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        self.cdn_base = "https://d3m9l0v76dty0.cloudfront.net"
        self.output_dir = "backend/data/blueprints"
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self, brand_slug: str, brand_url: str):
        """Standard entry point alias for compatibility."""
        return self.scrape_brand(brand_slug, brand_url)

    def scrape_brand(self, brand_slug: str, brand_url: str) -> Optional[str]:
        print(f"📡 Establishing Direct Uplink: {brand_slug.upper()} ({brand_url})")
        
        all_products = []
        seen_ids: Set[str] = set() # O(1) Lookup for deduplication
        page = 1
        max_pages = 25 
        
        while page <= max_pages:
            paged_url = f"{brand_url}?page={page}" if page > 1 else brand_url
            if page > 1: print(f"   Scanning page {page}...")
            
            try:
                res = self.session.get(paged_url, timeout=10)
                if res.status_code == 404:
                    break # End of pagination
                if res.status_code != 200:
                    print(f"   ❌ Failed to load page {page}: {res.status_code}")
                    break
                
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Check for "No products found" indicator
                if "לא נמצאו מוצרים" in soup.text or not soup.select('.layout_list_item'):
                    if page == 1: print("   ⚠️  No products found on page 1.")
                    break
                
                product_nodes = soup.select('.layout_list_item')
                new_items_count = 0
                
                for node in product_nodes:
                    product_data = self._parse_node(node, brand_slug)
                    
                    if product_data and product_data['id'] not in seen_ids:
                        all_products.append(product_data)
                        seen_ids.add(product_data['id'])
                        new_items_count += 1
                
                # Stop if we parsed a page but found 0 NEW items (likely infinite scroll loop or duplicate page)
                if new_items_count == 0:
                    print("   ⚠️  Page loaded but no new unique items found. Stopping.")
                    break

                # Check for 'Next' button specifically to exit cleanly
                next_btn = soup.select_one('.pagination a.next_page')
                if not next_btn:
                    break

                page += 1
                time.sleep(0.5) # Polite delay
                
            except Exception as e:
                print(f"   ❌ Critical error on page {page}: {e}")
                break
        
        # --- DATA INTEGRITY CHECK ---
        if not all_products:
            print(f"   ❌ {brand_slug.upper()}: No products found. Check CSS selectors.")
            return None
            
        print(f"✅ Mission Complete: {len(all_products)} Lifeforms Mapped.")
        
        output_path = os.path.join(self.output_dir, f"{brand_slug}_commercial.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
            
        return output_path

    def _parse_node(self, node, brand_slug) -> Optional[Dict]:
        try:
            # ID Extraction
            halilit_id = node.get('data-item-code')
            
            # Name Extraction
            name_el = node.select_one('.title_with_brand')
            name = name_el.text.strip() if name_el else "Unknown Product"
            
            # Link Extraction
            link_el = node.find('a', href=True)
            rel_url = link_el['href'].strip() if link_el else ""
            
            # Robust ID Fallback
            if not halilit_id:
                if rel_url:
                    # Extract "12345" from "/product/12345-some-name"
                    parts = rel_url.split('/')[-1].split('-')
                    if parts[0].isdigit():
                        halilit_id = parts[0]
                    else:
                        halilit_id = rel_url.split('/')[-1] # Fallback to slug
                else:
                    return None # Skip if no ID and no URL

            # Image Extraction
            img_el = node.select_one('.img_wrapper img')
            img_url = img_el['src'] if img_el else ""
            if img_url and not img_url.startswith('http'):
                 img_url = f"{self.cdn_base}{img_url}"

            # Pricing
            pricing = self._extract_pricing_tiers(node)

            safe_id = f"{brand_slug}_{halilit_id}".lower()
            full_url = f"https://www.halilit.com{rel_url}" if rel_url else ""

            return {
                "id": safe_id,
                "name": name,
                "url": full_url,
                "image": img_url,
                "halilit_id": halilit_id,
                "sku": halilit_id, # Usually map ID to SKU for this retailer
                "pricing": pricing,
                "description": name,
                "category": "general"
            }
            
        except Exception:
            # Fail silently on individual nodes to keep the loop alive, 
            # but maybe log if needed.
            return None

    def _extract_pricing_tiers(self, node) -> Dict:
        """Isolated pricing logic for cleaner main loop"""
        pricing = {
            "currency": "ILS",
            "regular_price": None,
            "eilat_price": None, 
            "sale_price": None
        }
        
        try:
            price_container = node.select_one('.price')
            if not price_container:
                return pricing

            # 1. Eilat Price (Red text usually)
            eilat_node = price_container.select_one('.yilat_price_value, .eilat-price')
            if eilat_node:
                pricing['eilat_price'] = self._parse_price_text(eilat_node.get_text())

            # 2. Old/List Price (Crossed out)
            old_price_node = price_container.select_one('.old_price_value, .old-price, strike, del')
            if old_price_node:
                pricing['sale_price'] = self._parse_price_text(old_price_node.get_text())
            
            # 3. Regular/Current Price
            # We look for the main price class, OR fallback to stripping the container 
            # if we didn't find specific nodes.
            main_price_node = price_container.select_one('.price_value, .regular-price')
            if main_price_node:
                 pricing['regular_price'] = self._parse_price_text(main_price_node.get_text())
            elif not pricing['regular_price']:
                # Dangerous fallback: grabbing all text. 
                # Be careful not to grab the "Old Price" number by accident.
                # Usually safer to rely on class selectors.
                pass 
                
        except Exception:
            pass
            
        return pricing

    def _parse_price_text(self, text: str) -> Optional[float]:
        if not text: return None
        try:
            # Logic: Remove non-numeric chars except '.' 
            # Handle "1,200.00" -> "1200.00"
            clean = re.sub(r'[^\d.]', '', text.replace(',', ''))
            val = float(clean)
            return val if val > 0 else None
        except:
            return None

    async def run_full_catalog_scan(self):
        """
        Crawls the main navigation to find ALL products, not just a test set.
        """
        print("   🔍 Scanning Halilit Navigation...")
        
        # 1. Define the Master Category URLs (Hardcoded for stability)
        # These are the "Tribes" we care about
        entry_points = [
            "https://halilit.com/collections/synthesizers",
            "https://halilit.com/collections/pianos",
            "https://halilit.com/collections/drums",
            "https://halilit.com/collections/guitars",
            "https://halilit.com/collections/studio-equipment",
            "https://halilit.com/collections/live-sound",
            "https://halilit.com/collections/dj-equipment"
        ]
        
        all_products = []
        global_ids = set()
        
        for url in entry_points:
            print(f"      > Crawling {url} ...")
            products = self._scrape_collection_page(url) 
            for p in products:
                if p['id'] not in global_ids:
                    all_products.append(p)
                    global_ids.add(p['id'])
            
        # Save to Raw Commercial Vault
        self._save_to_vault(all_products)
        return all_products

    def _scrape_collection_page(self, url):
        products = []
        page = 1
        max_pages = 25
        
        while page <= max_pages:
            paged_url = f"{url}?page={page}" if page > 1 else url
            
            try:
                res = self.session.get(paged_url, timeout=10)
                if res.status_code != 200: break
                
                soup = BeautifulSoup(res.text, 'html.parser')
                product_nodes = soup.select('.layout_list_item')
                
                if not product_nodes: break
                
                new_count = 0
                for node in product_nodes:
                    # Generic 'halilit' brand slug for raw collection
                    # Use 'halilit' to avoid mismatches, we can resolve brand later
                    data = self._parse_node(node, "halilit") 
                    if data:
                        products.append(data)
                        new_count += 1
                
                if new_count == 0: break
                
                next_btn = soup.select_one('.pagination a.next_page')
                if not next_btn: break
                
                page += 1
                time.sleep(0.5)
            except Exception as e:
                print(f"      ❌ Error scraping {url} page {page}: {e}")
                break
                
        return products

    def _save_to_vault(self, products):
        path = "backend/data/vault/commercial_full_scan.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
