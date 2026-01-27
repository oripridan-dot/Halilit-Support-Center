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
# from services.relationship_engine import RelationshipEngine
from services.genesis_builder import GenesisBuilder

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FAST_REGEN")

async def run_factory():
    print("🚀 INITIALIZING FAST REGENERATION SEQUENCE...")

    # --- PHASE 1: COMMERCIAL HARVEST (THE TRUTH) ---
    print("\n📦 PHASE 1: COMMERCIAL HARVEST (Halilit Prices & Stock)")
    
    commercial_scraper = HalilitDirectScraper()
    commercial_results = await commercial_scraper.run_full_catalog_scan()
    
    print(f"   ✅ Commercial Harvest Complete. Found {len(commercial_results)} SKUs.")

    # --- PHASE 2: SKIPPED (OFFICIAL DATA PRESERVED) ---
    print("\n⏩ PHASE 2: SKIPPED (Preserving existing brand data)")

    # --- PHASE 3: RECONCILIATION ---
    print("\n🔗 PHASE 3: SKIPPED (Engine unavailable/Not required for pricing fix)")
    # try:
    #     engine = RelationshipEngine()
    #     engine.link_commercial_to_official()
    #     print("   ✅ Data Merged.")
    # except Exception as e:
    #     print(f"   ⚠️ Reconciliation Warning: {e}")

    # --- PHASE 4: GENESIS ---
    print("\n💎 PHASE 4: GENESIS BUILDER")
    builder = GenesisBuilder("")
    builder.construct_all_brands()
    builder.construct_category_catalogs()
    
    print("   ✅ Frontend Catalogs Generated.")

if __name__ == "__main__":
    asyncio.run(run_factory())
