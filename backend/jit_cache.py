"""
JIT Cache — Simple file-based cache for JIT intelligence results.

Cache key: product_id
TTL: 7 days (configurable)
Storage: JSON files in backend/data/jit_cache/
"""

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).parent / "data" / "jit_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_TTL = 7 * 24 * 3600  # 7 days in seconds


def _cache_path(product_id: str) -> Path:
    """Get cache file path for a product ID."""
    # Sanitize product_id for filesystem
    safe_id = product_id.replace("/", "_").replace("\\", "_")
    return CACHE_DIR / f"{safe_id}.json"


def get_cached_intelligence(product_id: str, ttl: int = DEFAULT_TTL) -> dict | None:
    """
    Get cached JIT intelligence for a product.

    Returns:
        Cached enriched product dict, or None if cache miss/expired.
    """
    path = _cache_path(product_id)
    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        cached_at = data.get("_cached_at", 0)
        if time.time() - cached_at > ttl:
            path.unlink(missing_ok=True)
            logger.debug(f"Cache expired for {product_id}")
            return None

        logger.debug(f"Cache hit for {product_id}")
        return data
    except Exception as e:
        logger.warning(f"Cache read error for {product_id}: {e}")
        return None


def cache_intelligence(product_id: str, enriched: dict):
    """
    Cache JIT intelligence result for a product.

    Args:
        product_id: Product identifier
        enriched: The enriched product data to cache
    """
    path = _cache_path(product_id)
    try:
        enriched["_cached_at"] = time.time()
        path.write_text(json.dumps(
            enriched, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.debug(f"Cached intelligence for {product_id}")
    except Exception as e:
        logger.warning(f"Cache write error for {product_id}: {e}")


def invalidate(product_id: str):
    """Remove cached data for a specific product."""
    path = _cache_path(product_id)
    path.unlink(missing_ok=True)


def invalidate_all():
    """Clear all cached JIT intelligence."""
    count = 0
    for path in CACHE_DIR.glob("*.json"):
        path.unlink(missing_ok=True)
        count += 1
    logger.info(f"Cleared {count} cached JIT results")
    return count


def cache_stats() -> dict:
    """Get cache statistics."""
    files = list(CACHE_DIR.glob("*.json"))
    total_size = sum(f.stat().st_size for f in files)
    return {
        "cached_products": len(files),
        "total_size_kb": round(total_size / 1024, 1),
        "cache_dir": str(CACHE_DIR),
    }
