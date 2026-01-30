#!/usr/bin/env python3
"""
Master Ingestion Pipeline
-------------------------
Orchestrates the complete lifecycle of a brand's data ingestion:
1. Harvest Commercial Data (Halilit) -> Source of Truth for ID/Price/Stock
2. Harvest Technical Data (Official) -> Source of Truth for Specs/Manuals/Deep Description
3. Process & Merge -> Standardize into a unified Knowledge Schema
4. Validate & Badge -> Verify structural integrity and issue 'Raw Ingestion Badge'

Usage:
    python3 backend/scripts/ingest_brand.py <brand_id>
"""

from backend.monitoring.tracker import IngestionTracker
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
import subprocess

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("IngestionPipeline")

# Constants
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))  # Ensure backend module is resolvable


BADGE_DIR = ROOT_DIR / "backend" / "data" / "badges"


def run_step(step_name, command):
    logger.info(f"🚀 START: {step_name}")
    try:
        result = subprocess.run(
            command,
            cwd=ROOT_DIR,
            text=True,
            capture_output=True,
            check=True
        )
        logger.info(f"✅ FINISHED: {step_name}")
        # logger.debug(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ FAILED: {step_name}")
        logger.error(e.stderr)
        return False


def validate_standards(brand_id: str):
    """
    Analyzes the processed data against the 'Knowledge Standard'.
    Does not crash on missing data, but grades the ingestion.
    """
    logger.info("🧐 Analyzing Data Standards & Coverage...")

    file_path = ROOT_DIR / "backend" / "data" / \
        "processed" / f"{brand_id}.json"
    if not file_path.exists():
        logger.error(f"Processed file not found: {file_path}")
        return None

    with open(file_path, "r") as f:
        data = json.load(f)

    products = data.get("products", [])
    total_products = len(products)

    if total_products == 0:
        logger.warning("No products found in catalog.")
        return None

    # Metrics
    enriched_count = 0
    with_specs_count = 0
    with_manuals_count = 0
    with_media_count = 0
    valid_categories = 0

    for p in products:
        # Check Enrichment (do we have official data description?)
        if len(p.get("description", "")) > 100:
            enriched_count += 1

        # Check Specs
        if p.get("specs") and len(p.get("specs")) > 0:
            with_specs_count += 1

        # Check Manuals
        if p.get("official_manuals"):
            with_manuals_count += 1

        # Check Rich Media (Images, Video, 3D)
        imgs = p.get("images", {}).get("gallery", [])
        media = p.get("media_files", [])
        if len(imgs) > 0 or len(media) > 0:
            with_media_count += 1

        # Check Categorization
        if p.get("category") and p.get("category") != "uncategorized":
            valid_categories += 1

    # Heuristic scoring
    score = {
        "total_products": total_products,
        "commercial_coverage": "100%",  # By definition if in processed list
        "technical_enrichment_rate": f"{round(enriched_count/total_products*100)}%",
        "specification_rate": f"{round(with_specs_count/total_products*100)}%",
        "manual_availability": f"{round(with_manuals_count/total_products*100)}%",
        "media_coverage": f"{round(with_media_count/total_products*100)}%",
        "categorization_health": f"{round(valid_categories/total_products*100)}%"
    }

    logger.info(f"📊 Ingestion Report for {brand_id}:")
    logger.info(json.dumps(score, indent=2))

    return score


def issue_badge(brand_id: str, score: dict):
    """
    Issues a 'Raw Ingestion Badge' if the process completed successfully
    and data structure is intact.
    """
    BADGE_DIR.mkdir(parents=True, exist_ok=True)

    badge = {
        "brand_id": brand_id,
        "badge_type": "RAW_PASS",  # Certified Exhaustive Capture
        "issued_at": datetime.now().isoformat(),
        "status": "READY_FOR_VECTORIZATION",
        "digest": score,
        "pipeline_version": "v1.1"
    }

    badge_path = BADGE_DIR / f"{brand_id}_badge.json"
    with open(badge_path, "w") as f:
        json.dump(badge, f, indent=2)

    logger.info(f"🏅 BADGE ISSUED: {badge_path}")
    logger.info(
        "The brand is now certified as Raw Ingested and ready for next steps.")


def main():
    parser = argparse.ArgumentParser(
        description="Run the Full Ingestion Pipeline")
    parser.add_argument(
        "brand_id", help="The slug of the brand to ingest (e.g. adam-audio)")
    args = parser.parse_args()

    brand = args.brand_id

    # Initialize Tracker
    tracker = IngestionTracker(brand)
    tracker.start_run()

    print("\n" + "="*60)
    print(f"   🌀 INGESTION PIPELINE STARTED: {brand.upper()}")
    print("="*60 + "\n")

    try:
        # Step 0: Brand Metadata Ingestion (Logos, Socials, Context)
        if not run_step("Brand Metadata Harvester", ["python3", "backend/scripts/ingest_brand_meta.py", brand]):
            logger.warning(
                "Brand Metadata ingestion failed or skipped (non-critical). Continuing...")

        # Step 1: Harvest Commercial (Halilit)
        if not run_step("Harvester: Commercial", ["python3", "backend/ingestion/raw_harvester.py", brand, "--step", "commercial"]):
            raise Exception("Commercial Harvest Failed")

        # Step 2: Processor Phase 1 (Generate Product List)
        if not run_step("Processor: Phase 1", ["python3", "backend/processing/processor.py", brand]):
            raise Exception("Processor Phase 1 Failed")

        # Step 3: Harvest Technical (Official - Depends on Phase 1)
        # We use "continueOnError" logic implicitly - checking output isn't easy here, but raw_harvester prints warnings if it skips
        run_step("Harvester: Technical", [
            "python3", "backend/ingestion/raw_harvester.py", brand, "--step", "technical"])

        # Step 4: Processor Phase 2 (Enrichment)
        if not run_step("Processor: Phase 2", ["python3", "backend/processing/processor.py", brand]):
            raise Exception("Processor Phase 2 Failed")

        # Step 5: Analysis & Badging
        score = validate_standards(brand)

        # Step 6: Historic Tracking Record
        processed_file = ROOT_DIR / "backend" / \
            "data" / "processed" / f"{brand}.json"
        if processed_file.exists():
            logger.info("📊 Recording historic snapshots...")
            with open(processed_file, "r") as f:
                data = json.load(f)
                for prod in data.get("products", []):
                    tracker.track_product(prod)

        if score:
            issue_badge(brand, score)
            tracker.finish_run("SUCCESS", score)
        else:
            logger.error("Analysis failed. No badge issued.")
            tracker.finish_run("FAILED", {"error": "Validation failed"})
            sys.exit(1)

    except Exception as e:
        logger.error(f"Pipeline Failed: {e}")
        tracker.finish_run("FAILED", {"error": str(e)})
        sys.exit(1)
    finally:
        tracker.close()


if __name__ == "__main__":
    main()
