from backend.scripts.refinery_engine import RefineryEngine
import json
import logging
from pathlib import Path
from typing import List, Dict
import sys

# Add backend to path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))


class MasterPipeline:
    """
    The Single Button.

    Responsibilities:
    1. Scan for raw content (Stage 1).
    2. Invoke the Refinery Engine for every product.
    3. Compile the "Golden Catalog".
    4. Publish to Frontend (Public Data).
    5. Generate a "Refinery Report".
    """

    def __init__(self, brand_id: str):
        self.brand_id = brand_id
        self.engine = RefineryEngine(brand_id)
        self.logger = logging.getLogger("MasterPipeline")

        # Paths
        self.ingest_dir = ROOT_DIR / "backend" / "data" / \
            "refinery" / "1_official_ingest" / self.brand_id
        self.frontend_out = ROOT_DIR / "frontend" / \
            "public" / "data" / f"{self.brand_id}.json"

    def run(self):
        """Execute the full lifecycle."""
        print(
            f"\n🏭 Starting Refinery Pipeline for Brand: {self.brand_id.upper()}")
        print("="*60)

        if not self.ingest_dir.exists():
            print(f"❌ No ingestion data found at: {self.ingest_dir}")
            return

        products = self._scan_products()
        print(f"📦 Found {len(products)} raw products queued for refinement.\n")

        golden_catalog = []
        report = {"total": 0, "diamond": 0,
                  "gold": 0, "silver": 0, "issues": 0}

        for pid in products:
            print(f"   ⚙️  Refining: {pid}...", end=" ")

            # THE CORE REFINERY PROCESS
            golden_entry = self.engine.run_pipeline_for_product(pid)

            if not golden_entry:
                print("❌ FAILED (Missing Data)")
                continue

            # Check Trust Status for Report
            badges = golden_entry["ui_meta"].get("badges", [])
            trust_score = golden_entry["ui_meta"].get("y_axis_score", 0)

            status_icon = "🥈"
            if "DIAMOND" in badges:
                status_icon = "💎"
                report["diamond"] += 1
            elif "GOLD" in badges:
                status_icon = "🥇"
                report["gold"] += 1
            else:
                report["silver"] += 1

            issues = golden_entry["ui_meta"].get("validation_flags", [])
            if issues:
                print(f"{status_icon} (Issues: {len(issues)})", end="\n")
                for issue in issues:
                    print(f"      ⚠️  {issue}")
                report["issues"] += len(issues)
            else:
                print(f"{status_icon} [Score: {trust_score}]")

            # Save individual Golden Master (Step 5)
            self.engine.save_golden_master(pid, golden_entry)

            # --- FILTER: ONLY LOAD DIAMOND PRODUCTS TO UI ---
            if "DIAMOND" in badges:
                golden_catalog.append(golden_entry)
            else:
                print(f"      🗑️  Skipping {pid} for UI (Not Diamond)")

            report["total"] += 1

        # Publish to Frontend
        print("\n" + "="*60)
        print(f"🚀 Publishing {len(golden_catalog)} products to Frontend...")
        self._publish_to_frontend(golden_catalog)

        # Final Summary
        print(f"\n📊 REFINERY REPORT: {self.brand_id.upper()}")
        print(f"   Total Processed: {report['total']}")
        print(f"   💎 Diamond Tier: {report['diamond']}")
        print(f"   🥇 Gold Tier:    {report['gold']}")
        print(f"   🥈 Silver Tier:  {report['silver']}")
        print(f"   ⚠️  Issues Flagged: {report['issues']}")
        print("="*60 + "\n")

        return {
            "brand_id": self.brand_id,
            "product_count": report['total'],
            # Assuming Diamond = Verified for index
            "verified_count": report['diamond'],
            "filename": f"{self.brand_id}.json"
        }

    def _scan_products(self) -> List[str]:
        """Finds all product IDs in Step 1."""
        return [f.stem for f in self.ingest_dir.glob("*.json")]

    def _publish_to_frontend(self, catalog: List[Dict]):
        """Writes the huge array that the React App consumes."""

        # TRANSFORMATION LAYER: Adapt Golden Catalog to Frontend Schema (BrandFile)
        # The frontend expects: { brand_identity: {...}, products: [...] }

        # 1. Construct Brand Identity (Mocked or derived)
        img_ext = "svg" if self.brand_id == "adam-audio" else "png"
        brand_identity = {
            "id": self.brand_id,
            "name": self.brand_id.replace("-", " ").title(),
            "logo_url": f"/assets/logos/{self.brand_id}_logo.{img_ext}",
            "product_count": len(catalog)
            # Add other required fields if necessary
        }

        # 2. Transform Products to Legacy/Frontend Schema
        legacy_products = []
        for golden in catalog:
            # Map Golden Fields -> UI Fields
            legacy_p = {
                # Core
                "id": golden["id"],
                "name": golden["official_name"],
                "brand": self.brand_id,

                # Classification
                "category": golden["ui_meta"]["primary_category"],
                "subcategory": golden["ui_meta"]["sub_division"],

                # Commerce
                "price": golden["commercial_meta"].get("price"),
                "availability": "in-stock" if golden["commercial_meta"].get("stock") == "IN_STOCK" else "out-of-stock",
                "sku": golden["commercial_meta"].get("sku_local"),

                # Media (Stubbing for now, real implementation would map assets)
                "image_url": f"/assets/products/{golden['id']}.jpg",

                # Rich Data (The 3 Pillars preserved for new components)
                "pill_data": golden,  # Embed the FULL golden object for the new UI to use!

                # Compliance with old types
                "description": f"Verified {golden['ui_meta']['primary_category']} from {self.brand_id}.",
                "specs": golden.get("specs", {}),
                "sources_of_truth": golden.get("context_meta", {}).get("sources_of_truth", [])
            }
            legacy_products.append(legacy_p)

        final_output = {
            "brand_identity": brand_identity,
            "products": legacy_products,
            "stats": {
                "total_products": len(legacy_products),
                "verified_products": len(legacy_products)
            }
        }

        with open(self.frontend_out, "w") as f:
            json.dump(final_output, f, indent=2)
        print(f"✅ Published to: {self.frontend_out}")


# CLI Entry Point
if __name__ == "__main__":
    import argparse
    import shutil

    # Configure logging slightly cleaner for CLI
    logging.basicConfig(level=logging.ERROR)

    parser = argparse.ArgumentParser(
        description="Master Data Refinery Pipeline")
    parser.add_argument(
        "brand", help="The brand slug (e.g., adam-audio) or 'all' to process everything")

    args = parser.parse_args()

    import datetime

    if args.brand == "all":
        # 1. Purge Frontend Data
        public_data = ROOT_DIR / "frontend" / "public" / "data"
        print("🧹 Cleaning Frontend Data Store...")
        for f in public_data.glob("*.json"):
            f.unlink()

        # 2. Find all ingestable brands
        ingest_root = ROOT_DIR / "backend" / "data" / "refinery" / "1_official_ingest"
        brands = [d.name for d in ingest_root.iterdir() if d.is_dir()]

        print(f"🌍 Processing ALL {len(brands)} detected brands...")

        brand_entries = []
        total_products = 0
        total_verified = 0

        for b in brands:
            pipeline = MasterPipeline(b)
            stats = pipeline.run()
            if stats:
                # Constuct BrandIndexEntry
                img_ext = "svg" if b == "adam-audio" else "png"
                entry = {
                    "id": b,
                    "name": b.replace("-", " ").title(),
                    "brand_color": "#333333",  # Default
                    "logo_url": f"/assets/logos/{b}_logo.{img_ext}",
                    "product_count": stats["product_count"],
                    "verified_count": stats["verified_count"],
                    "data_file": stats["filename"]
                }
                brand_entries.append(entry)
                total_products += stats["product_count"]
                total_verified += stats["verified_count"]

        # 3. Generate Master Index
        master_index = {
            "build_timestamp": datetime.datetime.now().isoformat(),
            "version": "5.0.0-Refinery",
            "total_products": total_products,
            "total_verified": total_verified,
            "brands": brand_entries
        }

        with open(public_data / "index.json", "w") as f:
            json.dump(master_index, f, indent=2)
        print(f"\n✅ Generated Master Index at: {public_data / 'index.json'}")

    else:
        pipeline = MasterPipeline(args.brand)
        pipeline.run()
