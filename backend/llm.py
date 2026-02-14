"""
LLM Gateway — Single point of contact for all Gemini API calls.
═══════════════════════════════════════════════════════════════

Replaces scattered Gemini call patterns across the codebase with ONE
centralized module that handles:

1. Rate limiting (token-bucket per agent)
2. Caching (content-addressed, via ai_cache)
3. Batching (group N products into fewer API calls)
4. Retries with exponential backoff
5. Audit logging

Previously these concerns were scattered across:
- unified_quality_gates.call_gemini_with_rate_limit() (rate limiting + audit)
- ingestion/ai_cache.py (caching)
- Individual agent classes (retry logic)

Now: ONE import → llm.call() or llm.batch()

Usage:
    from backend.llm import get_llm

    llm = get_llm()

    # Single call (cached + rate-limited)
    text, ok = llm.call("CommercialScout", prompt, system="You are...")

    # Batch call (groups products into fewer API calls)
    results = llm.batch("OfficialScout", prompts, system="You are...")

    # JSON mode (parsed response)
    data, ok = llm.call_json("CommercialScout", prompt)
"""

import json
import logging
import os
import time
import threading
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Optional, Tuple

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

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

    __slots__ = ("max_rpm", "request_times", "agent_backoff",
                 "agent_counts", "lock")

    def __init__(self, max_rpm: int = 60):
        self.max_rpm = max_rpm
        self.request_times: deque = deque()
        self.agent_backoff: dict[str, datetime] = {}
        self.agent_counts: dict[str, int] = {}
        self.lock = threading.Lock()

    def wait_if_needed(self, agent: str) -> float:
        with self.lock:
            now = datetime.now()

            # Per-agent backoff
            if agent in self.agent_backoff:
                wait = (self.agent_backoff[agent] - now).total_seconds()
                if wait > 0:
                    return wait
                del self.agent_backoff[agent]

            # Global RPM check
            cutoff = now - timedelta(minutes=1)
            while self.request_times and self.request_times[0] < cutoff:
                self.request_times.popleft()

            if len(self.request_times) >= self.max_rpm:
                return (self.request_times[0] +
                        timedelta(minutes=1) - now).total_seconds()
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
            # Double existing backoff up to 5 min cap
            if agent in self.agent_backoff:
                remaining = (self.agent_backoff[agent] -
                             datetime.now()).total_seconds()
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
    """
    Centralized Gemini API gateway with caching, rate limiting, and batching.

    Replaces:
    - unified_quality_gates.call_gemini_with_rate_limit()
    - Direct genai_client.models.generate_content() calls in agents
    - Scattered retry logic

    All Gemini calls in the app should go through this gateway.
    """

    def __init__(self, max_rpm: int = 60, cache_ttl_hours: float = 72.0,
                 model: str = "gemini-2.0-flash"):
        self.model = model
        self._limiter = _RateLimiter(max_rpm)
        self._cache_ttl = cache_ttl_hours
        self._cache = None  # Lazy — avoid circular imports
        self._call_count = 0
        self._cache_hits = 0

    @property
    def cache(self):
        if self._cache is None:
            from backend.ingestion.ai_cache import get_ai_cache
            self._cache = get_ai_cache()
        return self._cache

    @property
    def rate_limiter(self) -> _RateLimiter:
        """Expose rate limiter for status checks."""
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
        """
        Make a single Gemini call with rate limiting + caching.

        Args:
            agent: Agent name (for rate-limit tracking)
            prompt: The user/content prompt
            system: Optional system instruction
            model: Override default model
            use_cache: Whether to check/store cache
            cache_namespace: Cache category key

        Returns:
            (response_text, success_bool)
        """
        # 1. Check cache
        if use_cache:
            cache_input = {"prompt": prompt, "system": system or "",
                           "model": model or self.model}
            cached = self.cache.get(cache_namespace, cache_input)
            if cached is not None:
                self._cache_hits += 1
                logger.debug(f"[{agent}] LLM cache hit")
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
            text = response.text if hasattr(response, "text") else str(
                response)

            self._limiter.on_success(agent)

            # 4. Cache the result
            if use_cache:
                self.cache.put(cache_namespace, cache_input, text,
                               ttl_hours=self._cache_ttl)

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
    ) -> Tuple[Any, bool]:
        """
        Call Gemini and parse the response as JSON.

        Returns:
            (parsed_dict_or_list, success_bool)
        """
        # 1. Check cache (stores parsed JSON directly)
        if use_cache:
            cache_input = {"prompt": prompt, "system": system or "",
                           "model": model or self.model}
            cached = self.cache.get(cache_namespace, cache_input)
            if cached is not None:
                self._cache_hits += 1
                return cached, True

        # 2. Rate limit
        wait = self._limiter.wait_if_needed(agent)
        if wait > 0:
            time.sleep(wait)

        # 3. Call with JSON response config
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
            if system:
                config.system_instruction = system

            response = client.models.generate_content(
                model=model or self.model,
                contents=prompt,
                config=config,
            )
            text = response.text if hasattr(response, "text") else str(
                response)

            parsed = json.loads(text)
            self._limiter.on_success(agent)

            if use_cache:
                self.cache.put(cache_namespace, cache_input, parsed,
                               ttl_hours=self._cache_ttl)

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

    def batch(
        self,
        agent: str,
        prompts: list[str],
        *,
        system: Optional[str] = None,
        model: Optional[str] = None,
        use_cache: bool = True,
        batch_size: int = 5,
        cache_namespace: str = "llm_batch",
    ) -> list[Tuple[Any, bool]]:
        """
        Process multiple prompts efficiently by batching cached lookups
        and rate-limiting uncached calls.

        Does NOT combine prompts into mega-prompts (unreliable for structured
        extraction). Instead, it:
        1. Resolves all cache hits first (free)
        2. Fires uncached calls sequentially with rate limiting

        Args:
            agent: Agent name
            prompts: List of prompts to process
            system: Optional system instruction
            batch_size: How many uncached calls before a cooldown pause
            cache_namespace: Cache namespace

        Returns:
            List of (response, success) tuples in same order as prompts
        """
        results: list[Tuple[Any, bool]] = [("", False)] * len(prompts)
        uncached_indices: list[int] = []

        # Phase 1: Resolve cache hits
        for i, prompt in enumerate(prompts):
            if use_cache:
                cache_input = {"prompt": prompt, "system": system or "",
                               "model": model or self.model}
                cached = self.cache.get(cache_namespace, cache_input)
                if cached is not None:
                    results[i] = (cached, True)
                    self._cache_hits += 1
                    continue
            uncached_indices.append(i)

        if not uncached_indices:
            logger.info(f"[{agent}] Batch: all {len(prompts)} from cache")
            return results

        logger.info(
            f"[{agent}] Batch: {len(prompts) - len(uncached_indices)}"
            f" cached, {len(uncached_indices)} to call"
        )

        # Phase 2: Call uncached prompts with rate limiting
        for count, idx in enumerate(uncached_indices, 1):
            text, ok = self.call(
                agent, prompts[idx],
                system=system, model=model,
                use_cache=use_cache, cache_namespace=cache_namespace,
            )
            results[idx] = (text, ok)

            # Small cooldown every batch_size calls to stay within RPM
            if count % batch_size == 0 and count < len(uncached_indices):
                time.sleep(1.0)

        return results

    def stats(self) -> dict:
        """Combined stats from rate limiter + cache."""
        total = self._call_count + self._cache_hits
        return {
            "total_requests": total,
            "api_calls": self._call_count,
            "cache_hits": self._cache_hits,
            "cache_hit_rate": (f"{self._cache_hits / max(total, 1):.1%}"),
            "rate_limiter": self._limiter.status(),
            "cache": self.cache.get_stats(),
        }


# ── Singleton ──────────────────────────────────────────────────────────────

_instance: Optional[LLMGateway] = None


def get_llm() -> LLMGateway:
    """Get or create the singleton LLM gateway."""
    global _instance
    if _instance is None:
        _instance = LLMGateway()
    return _instance
