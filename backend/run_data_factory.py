import os
import sys
import logging
import asyncio
from datetime import datetime
import json

# Setup paths
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

# Import your services
from services.halilit_direct_scraper import HalilitDirectScraper
from services.roland_scraper import RolandScraper
from services.boss_scraper import BossScraper
# from services.nord_scraper import NordScraper # Uncomment when ready
from services.relationship_engine import RelationshipEngine
from services.genesis_builder import GenesisBuilder

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DATA_FACTORY")

async def run_factory():
    print("""
    ██████╗  █████╗ ████████╗ █████╗     ███████╗██████╗  ██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗
    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗    ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝
    ██║  ██║███████║   ██║   ███████║    █████╗  ███████║██║        ██║   ██║   ██║██████╔╝ ╚████╔╝ 
    ██║  ██║██╔══██║   ██║   ██╔══██║    ██╔══╝  ██╔══██║██║        ██║   ██║   ██║██╔══██╗  ╚██╔╝  
    ██████╔╝██║  ██║   ██║   ██║  ██║    ██║     ██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║   ██║   
    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
    """)
    
    print("🚀 INITIALIZING DATA FACTORY SEQUENCE...")

    # --- PHASE 1: COMMERCIAL HARVEST (THE TRUTH) ---
    # We scrape Halilit first because if they don't sell it, we probably don't care about it (for now).
    print("\n📦 PHASE 1: COMMERCIAL HARVEST (Halilit Prices & Stock)")
    print("   Target: https://halilit.com")
    
    commercial_scraper = HalilitDirectScraper()
    # Ensure this runs a FULL scan, not just a test
    commercial_results = await commercial_scraper.run_full_catalog_scan()
    
    print(f"   ✅ Commercial Harvest Complete. Found {len(commercial_results)} SKUs.")

    # --- PHASE 2: KNOWLEDGE HARVEST (Official Specs, Docs, Media) ---
    # Now we go to the brands to get the "Good Stuff" (Manuals, HD Images)
    print("\n🧠 PHASE 2: KNOWLEDGE HARVEST (Official Brand Data)")
    
    tasks = []
    
    # ROLAND
    print("   > Launching Roland Agent...")
    roland = RolandScraper()
    tasks.append(roland.scrape_all()) # Ensure this method extracts PDFs!

    # BOSS
    print("   > Launching Boss Agent...")
    boss = BossScraper()
    tasks.append(boss.scrape_all())
    
    # Run them in parallel for speed
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print(f"   ✅ Knowledge Harvest Complete.")

    # --- PHASE 3: RECONCILIATION (The Marriage) ---
    # Link the Halilit Price to the Roland Manual
    print("\n🔗 PHASE 3: RECONCILIATION ENGINE")
    engine = RelationshipEngine()
    engine.link_commercial_to_official()
    
    print("   ✅ Data Merged.")

    # --- PHASE 4: GENESIS (Frontend Compilation) ---
    # Build the JSONs for the UI
    print("\n💎 PHASE 4: GENESIS BUILDER")
    builder = GenesisBuilder("")
    builder.construct_all_brands()
    builder.construct_category_catalogs() # The method we added previously
    
    print("   ✅ Frontend Catalogs Generated.")

    # --- PHASE 5: AUDIT ---
    print("\n📊 FINAL FACTORY REPORT:")
    _run_audit()

def _run_audit():
    # Simple check to see if we actually got prices and docs
    base_dir = "frontend/public/data/categories"
    if not os.path.exists(base_dir): return
    
    total_items = 0
    items_with_price = 0
    items_with_docs = 0
    
    for f in os.listdir(base_dir):
        if f.endswith(".json"):
            try:
                with open(os.path.join(base_dir, f), 'r') as jf:
                    data = json.load(jf)
                    products = data.get('products', [])
                    total_items += len(products)
                    for p in products:
                        if p.get('price', 0) > 0: items_with_price += 1
                        if p.get('downloads'): items_with_docs += 1
            except: pass
            
    print(f"   TOTAL PRODUCTS: {total_items}")
    print(f"   WITH PRICES:    {items_with_price}  ({(items_with_price/total_items)*100:.1f}%)" if total_items > 0 else "   WITH PRICES:    0 (0.0%)")
    print(f"   WITH DOCS:      {items_with_docs}  ({(items_with_docs/total_items)*100:.1f}%)" if total_items > 0 else "   WITH DOCS:      0 (0.0%)")

if __name__ == "__main__":
    asyncio.run(run_factory())
