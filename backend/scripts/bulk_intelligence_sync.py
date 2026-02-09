from backend.unified_agent_orchestrator_v76 import TrinitySwarm
import asyncio
import sys
import os
import json
import random
import logging
import glob
from typing import List, Dict, Any

# Ensure backend path is in sys.path
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))

# Import Agents

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LocalProductLoader:
    """Simple loader that reads direct from frontend/public/data to avoid import hell."""

    def __init__(self):
        self.data_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '../../frontend/public/data'))

    def get_all_products(self) -> List[Dict]:
        products = []
        try:
            # OPTIMIZATION: Prioritize nord.json and limit load to avoid OOM
            target_files = ['nord.json', 'roland.json', 'yamaha.json']
            all_files = glob.glob(os.path.join(self.data_dir, "*.json"))

            # Sort files: target files first, then the rest
            sorted_files = []
            for t in target_files:
                full_path = os.path.join(self.data_dir, t)
                if full_path in all_files:
                    sorted_files.append(full_path)

            # Add a few random others for variety, but limit total files
            other_files = [f for f in all_files if f not in sorted_files]
            random.shuffle(other_files)
            # Only load 5 other files to save memory
            sorted_files.extend(other_files[:5])

            logger.info(
                f"📂 Loading products from {len(sorted_files)} files to prevent OOM...")

            for fpath in sorted_files:
                if 'index.json' in fpath or 'package.json' in fpath:
                    continue
                try:
                    with open(fpath, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            products.extend(data)
                        elif isinstance(data, dict) and 'products' in data:
                            products.extend(data['products'])
                except Exception as e:
                    logger.warning(f"Failed to load {fpath}: {e}")
        except Exception as e:
            logger.error(f"Error listing files: {e}")
        return products


class BulkIntelligenceSync:
    def __init__(self):
        self.loader = LocalProductLoader()
        self.swarm = TrinitySwarm()
        self.processed_count = 0
        self.conflict_count = 0

    async def run_batch(self, limit: int = 20):
        """
        Run intelligence sync on a batch of products.
        Prioritizes 'Nord' products first to find known interesting conflicts,
        then shuffles the rest to get a random sample.
        """
        logger.info(f"🚀 Starting Bulk Intelligence Sync (Limit: {limit})")

        # 1. Get all products
        all_products = self.loader.get_all_products()
        logger.info(f"📚 Total products loaded directly: {len(all_products)}")

        # 2. Prioritize & Shuffle
        nord_products = [p for p in all_products if 'nord' in str(
            p.get('brand', '')).lower()]
        other_products = [p for p in all_products if 'nord' not in str(
            p.get('brand', '')).lower()]

        logger.info(
            f"🎹 Found {len(nord_products)} Nord products (Prioritizing)")

        random.shuffle(other_products)
        target_batch = (nord_products + other_products)[:limit]

        logger.info(f"🎯 Processing batch of {len(target_batch)} products")

        for product in target_batch:
            await self.process_product(product)

        logger.info(
            f"✅ Sync Complete. Processed: {self.processed_count}, Conflicts Found: {self.conflict_count}")

    def _extract_image_url(self, product: Dict[str, Any]) -> str:
        """Robustly extract the best image URL from various schema formats."""
        # Strategy 1: 'official_images' list (common in this schema)
        images = product.get('official_images', [])
        if images and isinstance(images, list) and len(images) > 0:
            first = images[0]
            if isinstance(first, str):
                return first
            if isinstance(first, dict):
                return first.get('url')  # <--- FIXED

        # Strategy 2: 'images' list (sometimes strings, sometimes dicts)
        images = product.get('images', [])
        if images and isinstance(images, list) and len(images) > 0:
            first = images[0]
            if isinstance(first, str):
                return first
            if isinstance(first, dict):
                return first.get('url')

        # Strategy 3: 'image_url' string
        if product.get('image_url') and isinstance(product.get('image_url'), str):
            return product.get('image_url')

        return None

    async def process_product(self, product: Dict[str, Any]):
        product_id = product.get('id', product.get('halilit_id', 'unknown'))
        name = product.get('product_name', product.get(
            'name', 'Unknown Product'))

        # 1. Extract Image
        image_url = self._extract_image_url(product)
        if not image_url:
            # logger.debug(f"⏭️ Skipping {name}: No image found")
            return

        # 2. Extract Claims (simplified for demo)
        claims = {
            "product_name": name,
            "category": product.get('category', 'Unknown'),
            # "brand": product.get('brand', 'Unknown'),
            # "description": product.get('description', '')[:200]
        }

        try:
            logger.info(f"🔍 Inspecting {name}...")

            # 3. Visual Validation via Swarm's Visual Component
            # We access the visual_comparator directly from the swarm instance
            validation_check = self.swarm.visual_comparator.validate_single_image_claims(
                image_url=image_url,
                claims=claims
            )

            # Handle return format (tuple or dict? implementation varies in v75/76)
            # v76 code from previous read_file showed:
            # is_consistent, visual_evidence, discrepancy, conf = ...

            if isinstance(validation_check, tuple) and len(validation_check) >= 4:
                is_consistent, visual_evidence, discrepancy, score = validation_check
            else:
                logger.warning(
                    f"Unexpected validation return for {name}: {validation_check}")
                return

            if not is_consistent and score > 0.8:
                logger.warning(
                    f"⚠️ CONFLICT DETECTED for {name} (Score: {score})")
                logger.warning(f"   Reason: {discrepancy}")

                self.conflict_count += 1

                # 4. Trigger Arbitration (The 'Brain')
                # Use the public resolve_conflict method
                resolution = self.swarm.resolve_conflict(
                    product_name=name,
                    claims=claims,
                    visual_evidence=visual_evidence,
                    discrepancy=discrepancy,
                    image_url=image_url
                )

                winner = resolution.get('winner')
                logger.info(f"⚖️ Resolved: {winner} wins.")
                if resolution.get('learning_insight'):
                    logger.info(
                        f"🧠 Learned: {resolution.get('learning_insight')}")

                self.processed_count += 1
            else:
                pass
                # logger.debug(f"✅ Verified {name} (Score: {score})")

        except Exception as e:
            logger.error(f"❌ Error processing {name}: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=10)
    args = parser.parse_args()

    syncer = BulkIntelligenceSync()
    asyncio.run(syncer.run_batch(limit=args.limit))
