
import asyncio
import logging
import shutil
import os
from pathlib import Path
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HighOctaneIngestion")

# Define Root Paths
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
BLUEPRINTS_DIR = DATA_DIR / "blueprints"
CATALOGS_BRAND_DIR = DATA_DIR / "catalogs_brand"

BLUEPRINTS_DIR.mkdir(parents=True, exist_ok=True)
CATALOGS_BRAND_DIR.mkdir(parents=True, exist_ok=True)

# --- Import Scrapers with Environmental Safety Checks ---

# 1. Halilit (Requests-based, should always work)
try:
    import services.halilit_direct_scraper
    print(f"DEBUG: Loaded Scraper from {services.halilit_direct_scraper.__file__}")
    from services.halilit_direct_scraper import HalilitDirectScraper
    HALILIT_AVAILABLE = True
except ImportError as e:
    logger.error(f"❌ Failed to import HalilitDirectScraper: {e}")
    HALILIT_AVAILABLE = False

# 2. Playwright Scrapers (May fail on Alpine/minimal envs)
PLAYWRIGHT_AVAILABLE = False
RolandScraper = None
BossScraper = None
scrape_nord_products = None
scrape_moog_products = None

try:
    from services.roland_scraper import RolandScraper
    from services.boss_scraper import BossScraper
    from services.nord_scraper import scrape_nord_products
    from services.moog_scraper import scrape_moog_products
    PLAYWRIGHT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️  Playwright-based scrapers (Roland/Boss/Nord/Moog) are UNAVAILABLE in this environment.")
    logger.warning(f"   Reason: {e}")
    logger.warning(f"   (This is expected on Alpine Linux. Only 'Halilit' scrape will proceed.)")


async def run_roland():
    if not RolandScraper: return None
    logger.info("🚀 Starting Roland Scraper (HIGH OCTANE - NO LIMITS)...")
    scraper = RolandScraper()
    catalog = await scraper.scrape_all_products(max_products=None)
    
    output_file = CATALOGS_BRAND_DIR / "roland_brand_comprehensive.json"
    with open(output_file, 'w') as f:
        f.write(catalog.model_dump_json(indent=2))
    return output_file

async def run_boss():
    if not BossScraper: return None
    logger.info("🚀 Starting Boss Scraper (HIGH OCTANE - NO LIMITS)...")
    scraper = BossScraper()
    catalog = await scraper.scrape_all_products(max_products=None)
    output_file = CATALOGS_BRAND_DIR / "boss_brand_comprehensive.json"
    with open(output_file, 'w') as f:
        f.write(catalog.model_dump_json(indent=2))
    return output_file

async def run_nord():
    if not scrape_nord_products: return None
    logger.info("🚀 Starting Nord Scraper (HIGH OCTANE - NO LIMITS)...")
    catalog = await scrape_nord_products(max_products=None)
    output_file = CATALOGS_BRAND_DIR / "nord_brand_comprehensive.json"
    with open(output_file, 'w') as f:
        f.write(catalog.model_dump_json(indent=2))
    return output_file

async def run_moog():
    if not scrape_moog_products: return None
    logger.info("🚀 Starting Moog Scraper (HIGH OCTANE - NO LIMITS)...")
    catalog = await scrape_moog_products(max_products=None)
    output_file = CATALOGS_BRAND_DIR / "moog_brand_comprehensive.json"
    with open(output_file, 'w') as f:
        f.write(catalog.model_dump_json(indent=2))
    return output_file

async def run_halilit():
    if not HALILIT_AVAILABLE: return None
    logger.info("🚀 Starting Halilit Direct Scraper (HIGH OCTANE - FULL SCAN)...")
    scraper = HalilitDirectScraper()
    # run_full_catalog_scan returns a list of items, we might want to save it similarly
    results = await scraper.run_full_catalog_scan()
    
    # Save raw results
    output_file = CATALOGS_BRAND_DIR / "halilit_commercial_comprehensive.json"
    import json
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"✅ Halilit Harvested: {len(results)} SKUs.")
    return output_file

async def main():
    print("""
    🔥🔥 HIGH OCTANE INGESTION PROTOCOL INITIATED 🔥🔥
    WARNING: EXECUTING FULL CATALOG SCANS.
    """)
    
    # 0. Run Halilit (Commercial)
    if HALILIT_AVAILABLE:
        hal_file = await run_halilit()
    
    # 1. Scrape Brands (Sequential)
    roland_file = await run_roland()
    if roland_file: logger.info(f"✅ Roland Done: {roland_file}")
    
    boss_file = await run_boss()
    if boss_file: logger.info(f"✅ Boss Done: {boss_file}")
    
    nord_file = await run_nord()
    if nord_file: logger.info(f"✅ Nord Done: {nord_file}")
    
    moog_file = await run_moog()
    if moog_file: logger.info(f"✅ Moog Done: {moog_file}")
    
    # 2. Promote to Blueprints
    # Rename and move to blueprints dir
    pairs = [
        (roland_file, "roland_blueprint.json"),
        (boss_file, "boss_blueprint.json"),
        (nord_file, "nord_blueprint.json"),
        (moog_file, "moog_blueprint.json")
    ]
    
    if PLAYWRIGHT_AVAILABLE:
        for src, dest_name in pairs:
            if src and src.exists():
                dest = BLUEPRINTS_DIR / dest_name
                shutil.copy2(src, dest)
                logger.info(f"📦 Promoted {src.name} -> {dest_name}")
    else:
        print("\n⚠️  SKIPPING BLUEPRINT PROMOTION: Source scrapers were unavailable.")

    logger.info("✨ HIGH OCTANE Ingestion Complete. Ready for Forge.")

if __name__ == "__main__":
    asyncio.run(main())
