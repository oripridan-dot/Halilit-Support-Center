"""
LLM Gateway v9 — Centralized Gemini API access with built-in cache.

All Gemini calls in the app go through this gateway:
  - Rate limiting (token-bucket per agent)
  - File-based content-addressed cache (7-day TTL)
  - Retries with exponential backoff

Usage:
    from backend.llm import get_llm

    llm = get_llm()
    text, ok = llm.call("JITAgent", prompt, system="You are...")
    data, ok = llm.call_json("JITAgent", prompt)
"""

import hashlib
import json
import logging
import os
import time
import threading
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Tuple

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Cache directory ──
CACHE_DIR = Path(__file__).parent / "data" / "ai_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ── Built-in File Cache ──────────────────────────────────────────────────

class _FileCache:
    """Content-addressed file cache with configurable TTL."""

    def __init__(self, cache_dir: Path = CACHE_DIR, default_ttl_hours: float = 168.0):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl_hours * 3600  # Convert to seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._hits = 0
        self._misses = 0

    def _key(self, namespace: str, inputs: dict) -> str:
        raw = json.dumps({"ns": namespace, **inputs}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def _path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def get(self, namespace: str, inputs: dict) -> Any | None:
        key = self._key(namespace, inputs)
        path = self._path(key)
        if not path.exists():
            self._misses += 1
            return None
        try:
            data = json.loads(path.read_text())
            if time.time() - data.get("ts", 0) > self.default_ttl:
                path.unlink(missing_ok=True)
                self._misses += 1
                return None
            self._hits += 1
            return data["value"]
        except Exception:
            self._misses += 1
            return None

    def put(self, namespace: str, inputs: dict, value: Any, ttl_hours: float | None = None):
        key = self._key(namespace, inputs)
        path = self._path(key)
        try:
            path.write_text(json.dumps(
                {"ts": time.time(), "value": value}, ensure_ascii=False))
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")

    def get_stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{self._hits / max(total, 1):.1%}",
            "cache_files": len(list(self.cache_dir.glob("*.json"))),
        }


# ── Lazy Gemini client ─────────────────────────────────────────────────────
_genai_client = None


def _get_client():
    global _genai_client
    if _genai_client is None:
        try:
            from google import genai
            _genai_client = genai.Client(
                api_key=os.environ.get("GOOGLE_API_KEY"))
        except Exception as e:
            logger.error(f"Failed to init Gemini client: {e}")
    return _genai_client


# ── Rate Limiter ───────────────────────────────────────────────────────────

class _RateLimiter:
    """Token-bucket rate limiter with per-agent exponential backoff."""

    __slots__ = ("max_rpm", "request_times",
                 "agent_backoff", "agent_counts", "lock")

    def __init__(self, max_rpm: int = 60):
        self.max_rpm = max_rpm
        self.request_times: deque = deque()
        self.agent_backoff: dict[str, datetime] = {}
        self.agent_counts: dict[str, int] = {}
        self.lock = threading.Lock()

    def wait_if_needed(self, agent: str) -> float:
        with self.lock:
            now = datetime.now()
            if agent in self.agent_backoff:
                wait = (self.agent_backoff[agent] - now).total_seconds()
                if wait > 0:
                    return wait
                del self.agent_backoff[agent]

            cutoff = now - timedelta(minutes=1)
            while self.request_times and self.request_times[0] < cutoff:
                self.request_times.popleft()

            if len(self.request_times) >= self.max_rpm:
                return (self.request_times[0] + timedelta(minutes=1) - now).total_seconds()
            return 0.0

    def record(self, agent: str):
        with self.lock:
            self.request_times.append(datetime.now())
            self.agent_counts[agent] = self.agent_counts.get(agent, 0) + 1

    def on_success(self, agent: str):
        with self.lock:
            self.agent_backoff.pop(agent, None)

    def on_failure(self, agent: str, error_code: Optional[int] = None):
        with self.lock:
            if error_code == 429:
                delay = 60.0
            elif error_code == 503:
                delay = 30.0
            else:
                delay = 5.0
            if agent in self.agent_backoff:
                remaining = (
                    self.agent_backoff[agent] - datetime.now()).total_seconds()
                delay = min(300, max(delay, remaining * 2))
            self.agent_backoff[agent] = datetime.now() + \
                timedelta(seconds=delay)

    def status(self) -> dict:
        with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(minutes=1)
            current = sum(1 for t in self.request_times if t > cutoff)
            return {
                "current_rpm": current,
                "max_rpm": self.max_rpm,
                "remaining": max(0, self.max_rpm - current),
                "agents_backing_off": list(self.agent_backoff.keys()),
                "agent_counts": dict(self.agent_counts),
            }


# ── LLM Gateway ───────────────────────────────────────────────────────────

class LLMGateway:
    """Centralized Gemini API gateway with caching and rate limiting."""

    def __init__(self, max_rpm: int = 60, cache_ttl_hours: float = 168.0,
                 model: str = "gemini-2.0-flash"):
        self.model = model
        self._limiter = _RateLimiter(max_rpm)
        self._cache = _FileCache(default_ttl_hours=cache_ttl_hours)
        self._call_count = 0
        self._cache_hits = 0

    @property
    def cache(self):
        return self._cache

    @property
    def rate_limiter(self) -> _RateLimiter:
        return self._limiter

    def call(
        self,
        agent: str,
        prompt: str,
        *,
        system: Optional[str] = None,
        model: Optional[str] = None,
        use_cache: bool = True,
        cache_namespace: str = "llm",
    ) -> Tuple[str, bool]:
        """Single Gemini call with rate limiting + caching."""
        # 1. Check cache
        if use_cache:
            cache_input = {"prompt": prompt,
                           "system": system or "", "model": model or self.model}
            cached = self._cache.get(cache_namespace, cache_input)
            if cached is not None:
                self._cache_hits += 1
                return cached, True

        # 2. Rate limit
        wait = self._limiter.wait_if_needed(agent)
        if wait > 0:
            logger.info(f"[{agent}] Rate limit — waiting {wait:.1f}s")
            time.sleep(wait)

        # 3. Call Gemini
        client = _get_client()
        if not client:
            return "Error: Gemini client not initialized", False

        try:
            self._limiter.record(agent)
            self._call_count += 1

            config = {}
            if system:
                config["system_instruction"] = system

            response = client.models.generate_content(
                model=model or self.model,
                contents=prompt,
                config=config if config else None,
            )
            text = response.text if hasattr(
                response, "text") else str(response)

            self._limiter.on_success(agent)

            if use_cache:
                self._cache.put(cache_namespace, cache_input, text)

            return text, True

        except Exception as e:
            error_msg = str(e)
            code = (429 if "429" in error_msg or "Quota" in error_msg
                    else 503 if "503" in error_msg else None)
            self._limiter.on_failure(agent, code)
            logger.error(f"[{agent}] Gemini call failed: {error_msg}")
            return f"API Error: {error_msg}", False

    def call_json(
        self,
        agent: str,
        prompt: str,
        *,
        system: Optional[str] = None,
        model: Optional[str] = None,
        use_cache: bool = True,
        cache_namespace: str = "llm_json",
        response_schema: Optional[dict] = None,
    ) -> Tuple[Any, bool]:
        """Call Gemini and parse response as JSON."""
        if use_cache:
            cache_input = {"prompt": prompt,
                           "system": system or "", "model": model or self.model}
            cached = self._cache.get(cache_namespace, cache_input)
            if cached is not None:
                self._cache_hits += 1
                return cached, True

        wait = self._limiter.wait_if_needed(agent)
        if wait > 0:
            time.sleep(wait)

        client = _get_client()
        if not client:
            return {"error": "Client not initialized"}, False

        try:
            from google.genai import types as genai_types

            self._limiter.record(agent)
            self._call_count += 1

            config = genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            )
            if response_schema:
                try:
                    config.response_schema = response_schema
                except Exception:
                    pass  # Older SDK versions may not support this
            if system:
                config.system_instruction = system

            response = client.models.generate_content(
                model=model or self.model,
                contents=prompt,
                config=config,
            )
            text = response.text if hasattr(
                response, "text") else str(response)

            parsed = json.loads(text)
            self._limiter.on_success(agent)

            if use_cache:
                self._cache.put(cache_namespace, {"prompt": prompt, "system": system or "",
                                                  "model": model or self.model}, parsed)

            return parsed, True

        except json.JSONDecodeError as e:
            logger.warning(f"[{agent}] JSON parse failed: {e}")
            return {"error": f"JSON parse error: {e}"}, False
        except Exception as e:
            error_msg = str(e)
            code = (429 if "429" in error_msg or "Quota" in error_msg
                    else 503 if "503" in error_msg else None)
            self._limiter.on_failure(agent, code)
            logger.error(f"[{agent}] Gemini JSON call failed: {error_msg}")
            return {"error": error_msg}, False

    def stats(self) -> dict:
        total = self._call_count + self._cache_hits
        return {
            "total_requests": total,
            "api_calls": self._call_count,
            "cache_hits": self._cache_hits,
            "cache_hit_rate": f"{self._cache_hits / max(total, 1):.1%}",
            "rate_limiter": self._limiter.status(),
            "cache": self._cache.get_stats(),
        }


# ── Singleton ──────────────────────────────────────────────────────────────

_instance: Optional[LLMGateway] = None


def get_llm() -> LLMGateway:
    """Get or create the singleton LLM gateway."""
    global _instance
    if _instance is None:
        _instance = LLMGateway()
    return _instance
