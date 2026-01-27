#!/usr/bin/env python3
"""
################################################################################
#               HALILIT SUPPORT CENTER - SYSTEM CONTROLLER                     #
#                                                                              #
#  The central nervous system for the HSC Data Factory.                        #
#  Orchestrates Scraping, Data Synthesis, and Frontend Generation.             #
################################################################################
"""

import os
import sys
import shutil
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any

# --- 1. BOOTSTRAP ENVIRONMENT ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Ensure data directories exist
STATUS_FILE = os.path.join(BASE_DIR, "data", "system_status.json")
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)-15s | %(levelname)-7s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIR, "system.log"))
    ]
)
logger = logging.getLogger("SYSTEM")

# --- 2. CONTEXT MANAGER (STATE ENGINE) ---
class SystemContext:
    """
    Manages the state of the data pipeline. 
    Writes to backend/data/system_status.json so we know when things last ran.
    """
    @staticmethod
    def load() -> Dict[str, Any]:
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    @staticmethod
    def update(section: str, status: str, details: Dict[str, Any] = None):
        """Updates the system status registry."""
        data = SystemContext.load()
        
        if section not in data:
            data[section] = {}
            
        data[section].update({
            "last_run": datetime.now().isoformat(),
            "status": status,
        })
        
        if details:
            data[section].update(details)
            
        # Write back
        try:
            with open(STATUS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save system status: {e}")

# --- 3. FILESYSTEM OPERATIONS ---
def organize_repository():
    """Cleans up the repo structure."""
    logger.info("🧹 EXECUTING FILESYSTEM PROTOCOL...")
    
    # Structure Definition
    structure = [
        "scripts",
        "data/static/blueprints",
        "data/generated/catalogs",
        "data/generated/radar",
        "data/vault/catalogs_brand", # Ensure Vault exists
        "data/vault/raw_commercial",
        "logs"
    ]
    
    for folder in structure:
        path = os.path.join(BASE_DIR, folder)
        os.makedirs(path, exist_ok=True)

    # Move Operational Scripts
    scripts_to_move = [
        "analyze_gaps.py", "forge_backbone.py", "generate_review_bundle.py",
        "mass_ingest_protocol.py", "run_clean_ingestion.py", "run_discovery.py",
        "debug_visual_factory.py", "run_data_factory.py"
    ]
    
    scripts_dir = os.path.join(BASE_DIR, "scripts")
    moved = 0
    for script in scripts_to_move:
        src = os.path.join(BASE_DIR, script)
        dst = os.path.join(scripts_dir, script)
        if os.path.exists(src):
            shutil.move(src, dst)
            moved += 1
            
    # Clean Frontend
    frontend_dir = os.path.abspath(os.path.join(BASE_DIR, "../frontend"))
    junk = ["test-data-load.cjs", "test-data-load.mjs", "test-images.html", "public/test-image.html"]
    cleaned = 0
    if os.path.exists(frontend_dir):
        for j in junk:
            jp = os.path.join(frontend_dir, j)
            if os.path.exists(jp):
                os.remove(jp)
                cleaned += 1

    logger.info(f"✨ Cleanup Complete. Moved {moved} scripts, removed {cleaned} temp files.")
    SystemContext.update("filesystem", "CLEAN", {"files_moved": moved})

# --- 4. DATA FACTORY TIERS ---

async def run_commercial_tier():
    """Phase 1: Scrape Halilit (The Source of Truth)."""
    from services.halilit_direct_scraper import HalilitDirectScraper
    print("\n📦 [TIER 1] COMMERCIAL DATA HARVEST")
    
    try:
        scraper = HalilitDirectScraper()
        if hasattr(scraper, 'run_full_catalog_scan'):
            results = await scraper.run_full_catalog_scan()
        else:
            results = await scraper.scrape_catalog()
            
        count = len(results) if results else 0
        SystemContext.update("commercial", "SUCCESS", {"product_count": count})
        logger.info(f"✅ Commercial Tier Complete. Products: {count}")
    except Exception as e:
        logger.error(f"❌ Commercial Tier Failed: {e}")
        SystemContext.update("commercial", "ERROR", {"error": str(e)})

async def run_knowledge_tier():
    """Phase 2: Scrape Official Brands (Manuals/Specs)."""
    print("\n🧠 [TIER 2] KNOWLEDGE ENRICHMENT")
    
    try:
        from services.roland_scraper import RolandScraper
        from services.boss_scraper import BossScraper
        
        # Run concurrently
        results = await asyncio.gather(
            RolandScraper().scrape_all(),
            BossScraper().scrape_all(),
            return_exceptions=True
        )
        
        # Check results
        success = True
        for r in results:
            if isinstance(r, Exception):
                logger.error(f"   Agent Failure: {r}")
                success = False
        
        status = "SUCCESS" if success else "PARTIAL_FAILURE"
        SystemContext.update("knowledge", status)
        logger.info(f"✅ Knowledge Tier Complete.")
    except ImportError as e:
        logger.error(f"❌ Knowledge Tier Skipped (Missing Dependencies): {e}")
        SystemContext.update("knowledge", "SKIPPED", {"error": str(e)})
    except Exception as e:
        logger.error(f"❌ Knowledge Tier Failed: {e}")
        SystemContext.update("knowledge", "ERROR", {"error": str(e)})

def run_synthesis_tier():
    """Phase 3: Link Commercial Data with Knowledge Data."""
    print("\n🔗 [TIER 3] DATA RECONCILIATION")
    
    try:
        try:
            from services.relationship_engine import RelationshipEngine
            engine = RelationshipEngine()
        except ImportError:
            from services.relationship_engine import ProductRelationshipEngine
            engine = ProductRelationshipEngine()
            
        if hasattr(engine, 'link_commercial_to_official'):
            engine.link_commercial_to_official()
            SystemContext.update("synthesis", "SUCCESS")
            logger.info("✅ Data Synthesis Complete.")
        else:
            logger.warning("   ⚠️ RelationshipEngine missing 'link_commercial_to_official'. Skipping step.")
            SystemContext.update("synthesis", "SKIPPED", {"reason": "method_missing"})
            
    except Exception as e:
        logger.error(f"❌ Synthesis Failed: {e}")
        SystemContext.update("synthesis", "ERROR", {"error": str(e)})

def run_genesis_tier():
    """Phase 4: Generate Frontend JSON Artifacts."""
    from services.genesis_builder import GenesisBuilder
    print("\n💎 [TIER 4] GENESIS (Frontend Build)")
    
    try:
        gb = GenesisBuilder("")
        gb.construct_all_brands()
        
        if hasattr(gb, 'construct_category_catalogs'):
            gb.construct_category_catalogs()
        else:
            logger.warning("   ⚠️ construct_category_catalogs() missing in GenesisBuilder. Update service!")
            
        SystemContext.update("genesis", "SUCCESS", {"built_at": datetime.now().isoformat()})
        logger.info("✅ Genesis Build Complete. Frontend updated.")
    except Exception as e:
        logger.error(f"❌ Genesis Failed: {e}")
        SystemContext.update("genesis", "ERROR", {"error": str(e)})

async def run_full_factory():
    """Executes the entire pipeline in order."""
    logger.info("🏭 STARTING FULL DATA FACTORY PIPELINE")
    
    await run_commercial_tier()
    await run_knowledge_tier()
    run_synthesis_tier()
    run_genesis_tier()
    
    print("\n🎉 SYSTEM UPDATE COMPLETE.")

# --- 5. CLI INTERFACE ---
def print_menu():
    status = SystemContext.load()
    last_gen = status.get('genesis', {}).get('last_run', 'Never')
    
    print(f"""
    🎛️  HALILIT SUPPORT CENTER - COMMAND DECK
    ==========================================
    Last System Build: {last_gen}
    
    1. 🧹 Organize Repository  (Fix Folders)
    2. 🏭 Run FULL DATA FACTORY (All Tiers)
    3. 💎 Run GENESIS Only     (Rebuild Frontend JSONs)
    4. 📦 Run Commercial Only  (Halilit Prices)
    5. 🧠 Run Knowledge Only   (Brand Specs/Docs)
    0. Exit
    """)

async def interactive_mode():
    while True:
        print_menu()
        choice = input("Select Operation: ").strip()
        
        if choice == "1":
            organize_repository()
        elif choice == "2":
            await run_full_factory()
        elif choice == "3":
            run_genesis_tier()
        elif choice == "4":
            await run_commercial_tier()
        elif choice == "5":
            await run_knowledge_tier()
        elif choice == "0":
            print("👋 System Shutdown.")
            sys.exit()
        else:
            print("❌ Invalid selection.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            cmd = sys.argv[1].lower()
            if cmd == "cleanup": organize_repository()
            elif cmd == "factory": asyncio.run(run_full_factory())
            elif cmd == "build": run_genesis_tier()
            else: print(f"Unknown command: {cmd}")
        else:
            asyncio.run(interactive_mode())
    except KeyboardInterrupt:
        print("\n👋 Force Quit.")
