# backend/processing/taxonomy_matrix.py
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger("TaxonomyEngine")

# Load configuration relative to this file
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "taxonomy_map.json"

_TAXONOMY_CONFIG = None


def load_config() -> Dict[str, Any]:
    global _TAXONOMY_CONFIG
    if _TAXONOMY_CONFIG:
        return _TAXONOMY_CONFIG

    if not CONFIG_PATH.exists():
        logger.error(f"Taxonomy config not found at {CONFIG_PATH}")
        return {"frontend_taxonomy": {}, "mappings": []}

    try:
        with open(CONFIG_PATH, "r") as f:
            _TAXONOMY_CONFIG = json.load(f)
            logger.info("Loaded taxonomy configuration")
    except Exception as e:
        logger.error(f"Failed to load taxonomy config: {e}")
        _TAXONOMY_CONFIG = {"frontend_taxonomy": {}, "mappings": []}

    return _TAXONOMY_CONFIG


def get_frontend_taxonomy():
    config = load_config()
    return config.get("frontend_taxonomy", {})


def normalize_category(raw_category: str, product_name: str) -> dict:
    """
    Intelligently maps raw category inputs to Frontend Taxonomy.
    Uses 'taxonomy_map.json' for dynamic rules and priority matching.
    """
    config = load_config()
    mappings = config.get("mappings", [])

    if not raw_category:
        raw_category = ""
    if not product_name:
        product_name = ""

    # Normalize input for matching
    # We combine them to catch context (e.g. category="Pro Audio", name="USB Interface")
    context_text = (raw_category + " " + product_name).lower()

    best_match = None

    for rule in mappings:
        result = rule.get("result")
        priority = rule.get("priority", 50)

        # Check 'contains_any' (Must match at least one)
        # Usually checking the main keywords
        triggers = rule.get("contains_any", [])
        if triggers:
            if not any(t.lower() in context_text for t in triggers):
                continue  # Skip if no trigger found

        # Check 'contains_context' (Refining keywords)
        # e.g. "interface" must also have "usb"
        contexts = rule.get("contains_context", [])
        if contexts:
            if not any(c.lower() in context_text for c in contexts):
                continue  # Skip if context missing

        # If we are here, it's a match.
        # Simple Logic: Highest priority wins. Same priority -> First one wins.
        if best_match is None or priority > best_match["priority"]:
            best_match = {
                "result": result,
                "priority": priority
            }

    if best_match:
        return best_match["result"]

    # Default Fallback
    return {"primary": "UNCATEGORIZED", "sub": "General"}
