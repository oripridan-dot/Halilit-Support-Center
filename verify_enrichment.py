
import sys
import logging
import json
from pathlib import Path
from backend.agents.trinity_swarm import TrinitySwarm

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestEnrichment")


def test():
    swarm = TrinitySwarm()

    # Load actual file
    path = Path(
        "/workspaces/Halilit-Support-Center/backend/data/brands/Moog/products.json")
    with open(path) as f:
        data = json.load(f)

    raw_products = data.get('products', [])
    product = raw_products[0]

    logger.info(f"Loaded product: {product.get('name')}")
    logger.info(f"Keys before: {product.keys()}")

    # Simulate what happens currently in trinity_integration.py (NO fix yet)
    try:
        enriched = swarm.verifier.enrich(product)
        logger.info(f"Enrich executed.")
        logger.info(f"Keys after: {enriched.keys()}")
        logger.info(f"Official Specs: {enriched.get('official_specs')}")

    except Exception as e:
        logger.error(f"Enrichment failed: {e}")


if __name__ == "__main__":
    test()
