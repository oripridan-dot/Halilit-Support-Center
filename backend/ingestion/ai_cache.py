"""
AI Response Cache — Avoids Duplicate Gemini API Calls

Content-addressed cache for AI enrichment responses.
If the input data hasn't changed, the AI output won't change either.
Hash the input → cache the output → skip expensive API calls.

Features:
- Content-hash keying (deterministic — same input → same cache hit)
- TTL-based expiry (default 72 hours)
- Separate namespaces per operation type (enrich, classify, summarize)
- Sharded storage (avoids too many files in one directory)
- Cache stats for monitoring hit rates

This saves significant Gemini API costs by avoiding re-enrichment of
products whose source data hasn't changed since the last run.

Usage:
    cache = AIResponseCache()

    # Check cache before calling Gemini
    cached = cache.get("enrich", product_dict)
    if cached:
        result = cached  # Free! No API call needed
    else:
        result = gemini_enrich(product_dict)
        cache.put("enrich", product_dict, result)
"""

import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Any

logger = logging.getLogger("AIResponseCache")


class AIResponseCache:
    """
    Content-addressed cache for AI enrichment responses.

    Architecture:
    - Cache is on-disk JSON files, sharded by first 2 chars of hash
    - Each entry stores: input hash, operation, timestamp, TTL, response
    - Lookups are O(1) — direct file path from hash
    - No external dependencies (Redis etc.) — filesystem only
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        default_ttl_hours: float = 72.0,
    ):
        self.cache_dir = cache_dir or Path("backend/data/ai_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl_hours = default_ttl_hours
        self._stats = {"hits": 0, "misses": 0, "expired": 0, "errors": 0}

    def get(self, operation: str, input_data: Any) -> Optional[Any]:
        """
        Look up a cached AI response.

        Args:
            operation: Cache namespace (e.g., "enrich", "classify")
            input_data: The input that was given to the AI

        Returns:
            Cached response if found and not expired, else None
        """
        cache_key = self._make_key(operation, input_data)
        cache_file = self._cache_path(operation, cache_key)

        if not cache_file.exists():
            self._stats["misses"] += 1
            return None

        try:
            entry = json.loads(cache_file.read_text())

            # Check TTL
            cached_at = datetime.fromisoformat(entry["cached_at"])
            ttl_hours = entry.get("ttl_hours", self.default_ttl_hours)
            age_hours = (
                datetime.now(timezone.utc) - cached_at
            ).total_seconds() / 3600

            if age_hours > ttl_hours:
                self._stats["expired"] += 1
                cache_file.unlink()
                logger.debug(
                    f"Cache EXPIRED for {operation}:{cache_key[:8]} "
                    f"(age={age_hours:.1f}h, ttl={ttl_hours}h)"
                )
                return None

            self._stats["hits"] += 1
            logger.debug(f"Cache HIT for {operation}:{cache_key[:8]}")
            return entry["response"]

        except (json.JSONDecodeError, KeyError, OSError) as e:
            self._stats["errors"] += 1
            logger.warning(f"Cache read error for {cache_key[:8]}: {e}")
            return None

    def put(
        self,
        operation: str,
        input_data: Any,
        response: Any,
        ttl_hours: Optional[float] = None,
    ):
        """
        Store an AI response in the cache.

        Args:
            operation: Cache namespace
            input_data: The input that was given to the AI
            response: The AI's response to cache
            ttl_hours: Custom TTL (default: self.default_ttl_hours)
        """
        cache_key = self._make_key(operation, input_data)
        cache_file = self._cache_path(operation, cache_key)

        entry = {
            "cache_key": cache_key,
            "operation": operation,
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "ttl_hours": ttl_hours or self.default_ttl_hours,
            "response": response,
        }

        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(
                json.dumps(entry, indent=2, default=str)
            )
            logger.debug(f"Cache PUT for {operation}:{cache_key[:8]}")
        except OSError as e:
            logger.warning(f"Cache write error for {cache_key[:8]}: {e}")

    def invalidate(self, operation: str, input_data: Any):
        """Remove a specific cache entry."""
        cache_key = self._make_key(operation, input_data)
        cache_file = self._cache_path(operation, cache_key)
        if cache_file.exists():
            cache_file.unlink()
            logger.debug(f"Cache INVALIDATED for {operation}:{cache_key[:8]}")

    def clear(self, operation: Optional[str] = None):
        """
        Clear cache entries.

        Args:
            operation: If provided, only clear entries for this operation.
                       If None, clear ALL cached entries.
        """
        import shutil

        if operation:
            op_dir = self.cache_dir / operation
            if op_dir.exists():
                shutil.rmtree(op_dir)
                logger.info(f"Cache cleared for operation: {operation}")
        else:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("All cache cleared")

    def get_stats(self) -> dict:
        """Return cache statistics including hit rate."""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / max(total, 1)
        return {
            **self._stats,
            "total_requests": total,
            "hit_rate": f"{hit_rate:.1%}",
        }

    def reset_stats(self):
        """Reset cache statistics."""
        self._stats = {"hits": 0, "misses": 0, "expired": 0, "errors": 0}

    def get_cache_size(self) -> dict:
        """Get cache size metrics."""
        if not self.cache_dir.exists():
            return {"entries": 0, "size_mb": 0.0}

        entries = 0
        total_bytes = 0
        for p in self.cache_dir.rglob("*.json"):
            entries += 1
            total_bytes += p.stat().st_size

        return {
            "entries": entries,
            "size_mb": round(total_bytes / (1024 * 1024), 2),
        }

    # ------------------------------------------------------------------
    # Internal methods
    # ------------------------------------------------------------------

    def _make_key(self, operation: str, input_data: Any) -> str:
        """Create a deterministic cache key from operation + input."""
        content = json.dumps(
            {"op": operation, "data": input_data},
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(content.encode()).hexdigest()

    def _cache_path(self, operation: str, cache_key: str) -> Path:
        """
        Build cache file path with sharding.
        Shards by first 2 hex chars to limit files per directory.
        """
        shard = cache_key[:2]
        return self.cache_dir / operation / shard / f"{cache_key}.json"


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_ai_cache: Optional[AIResponseCache] = None


def get_ai_cache() -> AIResponseCache:
    """Get or create the singleton AIResponseCache."""
    global _ai_cache
    if _ai_cache is None:
        _ai_cache = AIResponseCache()
    return _ai_cache
