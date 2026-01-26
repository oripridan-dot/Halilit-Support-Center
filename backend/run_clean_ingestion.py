
import asyncio
import logging
import shutil
import os
from pathlib import Path
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.roland_scraper import RolandScraper
from services.boss_scraper import BossScraper
from services.nord_scraper import scrape_nord_products
from services.moog_scraper import scrape_moog_products

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CleanIngestion")

DATA_DIR = Path("data")
BLUEPRINTS_DIR = DATA_DIR / "blueprints"
CATALOGS_BRAND_DIR = DATA_DIR / "catalogs_brand"

BLUEPRINTS_DIR.mkdir(parents=True, exist_ok=True)
CATALOGS_BRAND_DIR.mkdir(parents=True, exist_ok=True)

async def run_roland():
    logger.info("🚀 Starting Roland Scraper (Limit 15 for clean ingestion)...")
    scraper = RolandScraper()
    catalog = await scraper.scrape_all_products(max_products=15)
    
    output_file = CATALOGS_BRAND_DIR / "roland_brand_comprehensive.json"
    with open(output_file, 'w') as f:
        f.write(catalog.model_dump_json(indent=2))
    return output_file

async def run_boss():
    logger.info("🚀 Starting Boss Scraper (Limit 15)...")
    scraper = BossScraper()
    catalog = await scraper.scrape_all_products(max_products=15)
    output_file = CATALOGS_BRAND_DIR / "boss_brand_comprehensive.json"
    with open(output_file, 'w') as f:
        f.write(catalog.model_dump_json(indent=2))
    return output_file

async def run_nord():
    logger.info("🚀 Starting Nord Scraper (Limit 15)...")
    catalog = await scrape_nord_products(max_products=15)
    output_file = CATALOGS_BRAND_DIR / "nord_brand_comprehensive.json"
    with open(output_file, 'w') as f:
        f.write(catalog.model_dump_json(indent=2))
    return output_file

async def run_moog():
    logger.info("🚀 Starting Moog Scraper (Limit 15)...")
    catalog = await scrape_moog_products(max_products=15)
    output_file = CATALOGS_BRAND_DIR / "moog_brand_comprehensive.json"
    with open(output_file, 'w') as f:
        f.write(catalog.model_dump_json(indent=2))
    return output_file

async def main():
    logger.info("🧹 Starting Clean Ingestion Process...")
    
    # 1. Scrape Brands (Sequential to avoid resource exhaustion in container)
    roland_file = await run_roland()
    logger.info(f"✅ Roland Done: {roland_file}")
    
    boss_file = await run_boss()
    logger.info(f"✅ Boss Done: {boss_file}")
    
    nord_file = await run_nord()
    logger.info(f"✅ Nord Done: {nord_file}")
    
    moog_file = await run_moog()
    logger.info(f"✅ Moog Done: {moog_file}")
    
    # 2. Promote to Blueprints
    # Rename and move to blueprints dir
    pairs = [
        (roland_file, "roland_blueprint.json"),
        (boss_file, "boss_blueprint.json"),
        (nord_file, "nord_blueprint.json"),
        (moog_file, "moog_blueprint.json")
    ]
    
    for src, dest_name in pairs:
        dest = BLUEPRINTS_DIR / dest_name
        shutil.copy2(src, dest)
        logger.info(f"📦 Promoted {src.name} -> {dest_name}")

    logger.info("✨ Ingestion Complete. Ready for Forge.")

if __name__ == "__main__":
    asyncio.run(main())
