# backend/mass_ingest_protocol.py
import argparse
from services.raw_collector import RawCollector
from services.genesis_builder import GenesisBuilder
from services.delta_auditor import DeltaAuditor
# We will import processors dynamically or statically after we create them
# For now, let's assume RolandProcessor will be available
import sys
import os
import asyncio
import json

# Add backend to path for imports to work if running as script from backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class MassIngestProtocol:
    def __init__(self, mode="official_only"):
        self.collector = RawCollector()
        self.builder = None
        self.mode = mode
        self.auditor = DeltaAuditor()

    def run_brand_pipeline(self, brand_name, scraper_class, processor_class):
        if self.mode != "official_only":
            print(f"⏩ [SKIP] Skipping Official Brand Pipeline for {brand_name} (Mode: {self.mode})")
            return

        print(f"🚀 Starting OFFICIAL Pipeline for {brand_name}")
        
        # Initialize GenesisBuilder for this brand
        self.builder = GenesisBuilder(brand_name.lower())
        
        # Step 1: Scrape & Save AS-IS (The "Raw" Phase)
        print(f"🕵️ [AS-IS] initializing scraper for {brand_name}...")
        scraper = scraper_class()
        
        # Run async scraper synchronously
        raw_items = []
        if hasattr(scraper, 'scrape_and_return_raw'):
             raw_items = asyncio.run(scraper.scrape_and_return_raw(max_products=5)) # LIMIT TO 5 FOR DEMO speed
        else:
             print(f"⚠️ Scraper for {brand_name} does not have 'scrape_and_return_raw'.")
             return

        saved_raw_files = []
        for item in raw_items:
            # SAVE AS-IS: No processing, just dump to disk
            model_name = item.get('model', item.get('name', 'Unknown_Model'))
            
            saved = self.collector.save_as_is(brand_name, model_name, item)
            saved_raw_files.append(saved)
            print(f"📦 [AS-IS] Saved raw data for {model_name}")

        # Step 2: Process from Disk (The "Refinery" Phase)
        processor = processor_class()
        processed_blueprints = []
        brand_audit_results = []
        
        for raw_wrapper in saved_raw_files:
            # Read from the raw payload we just saved
            try:
                blueprint = processor.normalize(raw_wrapper['raw_payload'])
                processed_blueprints.append(blueprint)
                print(f"⚙️ [PROCESS] normalized {blueprint.get('name')}")
                
                # AUDIT STEP: Compare Raw vs Blueprint
                audit = self.auditor.audit_product(raw_wrapper['raw_payload'], blueprint)
                brand_audit_results.append(audit)

                if audit['missing_critical']:
                    print(f"⚠️  [GAP] {audit['model']} missing: {audit['missing_critical']}")
                if audit['extra_unmapped_data']:
                    print(f"💎 [DISCOVERY] {audit['model']} has unused data: {audit['extra_unmapped_data']}")

            except Exception as e:
                print(f"❌ Error processing {raw_wrapper['metadata']['model']}: {e}")

        # Save Audit Report
        if brand_audit_results:
             report_path = self.auditor.save_brand_report(brand_name, brand_audit_results)
             print(f"📊 Audit Report saved to: {report_path}")

        # Save merged blueprints
        if processed_blueprints:
            bp_path = f"backend/data/blueprints/{brand_name.lower().replace(' ', '_')}_blueprint.json"
            os.makedirs(os.path.dirname(bp_path), exist_ok=True)
            
            with open(bp_path, 'w', encoding='utf-8') as f:
                json.dump(processed_blueprints, f, indent=2, ensure_ascii=False)
            print(f"💾 [SAVED] {len(processed_blueprints)} blueprints to {bp_path}")

        print(f"✅ [COMPLETE] {brand_name} Official Pipeline Finished.")

    def run_commercial_sync(self):
        """
        Runs the Commercial Pipeline (Halilit Scraper)
        """
        if self.mode != "commercial_sync":
            return

        print("🚀 Starting COMMERCIAL Pipeline (Halilit Sync)")
        try:
            from services.halilit_direct_scraper import HalilitDirectScraper
            # Assuming HalilitScraper has a main or run method
            # For now, triggering the logic we can infer or creating a placeholder
            scraper = HalilitDirectScraper()
            print("🕵️ [COMMERCIAL] Scraper initialized (HalilitDirectScraper)")
            # In a real scenario: asyncio.run(scraper.run())
            # Resulting data should be saved to backend/data/blueprints/{brand}_commercial.json
            print("⚠️ Commercial sync execution logic would go here.")
        except ImportError:
            print("❌ HalilitDirectScraper not found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mass Ingestion Protocol")
    parser.add_argument("--mode", choices=["official_only", "commercial_sync"], default="official_only", help="Ingestion Mode")
    args = parser.parse_args()

    from services.roland_scraper import RolandScraper
    from services.processors.roland_processor import RolandProcessor
    from services.nord_scraper import NordScraper
    from services.processors.nord_processor import NordProcessor
    from services.moog_scraper import MoogScraper
    from services.processors.moog_processor import MoogProcessor
    
    protocol = MassIngestProtocol(mode=args.mode)
    try:
        if args.mode == "official_only":
            # Run Moog
            protocol.run_brand_pipeline("Moog", MoogScraper, MoogProcessor)
            # Run Nord
            protocol.run_brand_pipeline("Nord", NordScraper, NordProcessor)
            # Run Roland (if needed, commented in original but good to have)
            # protocol.run_brand_pipeline("Roland", RolandScraper, RolandProcessor)
        elif args.mode == "commercial_sync":
            protocol.run_commercial_sync()
        
    except Exception as e:
        print(f"Pipeline Failed: {e}")

