#!/usr/bin/env python3
from backend.ingestion.brand_harvester import BrandHarvester
import sys
import json
import asyncio
import logging
from pathlib import Path

# Add root to sys.path to allow imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("BrandMetaIngestion")


def load_manifest():
    manifest_path = ROOT_DIR / "backend/ingestion/manifest.json"
    if not manifest_path.exists():
        logger.error(f"Manifest not found at {manifest_path}")
        return None

    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


async def main(brand_id: str):
    logger.info(f"Starting Brand Metadata Ingestion for {brand_id}")

    manifest = load_manifest()
    if not manifest:
        sys.exit(1)

    brand_entry = next((b for b in manifest.get(
        "brands", []) if b["id"] == brand_id), None)

    if not brand_entry:
        logger.error(f"Brand {brand_id} not found in manifest.")
        sys.exit(1)

    name = brand_entry.get("name")
    official_url = brand_entry.get("technical", {}).get("source_url")

    if not official_url:
        logger.warning(
            f"No official URL configured for {name}. Skipping metadata harvest.")
        # We don't exit with error because it might be valid to have no url yet
        # But for this specific task, we probably want to try.
        sys.exit(0)

    harvester = BrandHarvester()
    brand_info = await harvester.harvest_brand(brand_id, name, official_url)

    if brand_info:
        logger.info(f"Successfully harvested metadata for {brand_info.name}")
        # print(brand_info.json(indent=2))
    else:
        logger.warning("Failed to harvest brand metadata.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ingest_brand_meta.py <brand_id>")
        sys.exit(1)

    asyncio.run(main(sys.argv[1]))
