"""
Enhanced Harvester — Phase 1 Improvement

Adds to the existing HalilitPageScraper and OfficialBrandScraper:
- Content fingerprinting for incremental harvests (skip unchanged pages)
- Retry with exponential backoff on transient failures
- Per-domain rate limiting (polite crawling)
- Structured HarvestResult reporting
- Persistent fingerprint store for change detection across runs

Usage:
    harvester = EnhancedHarvester()
    result = harvester.harvest_url("https://halilit.com/product/123")

    if result.success and not result.was_cached:
        # Content changed — process it
        ...
"""

import hashlib
import json
import time
import logging
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List
from dataclasses import dataclass, field, asdict

logger = logging.getLogger("EnhancedHarvester")


# ---------------------------------------------------------------------------
# Fingerprinting — detect whether a page actually changed since last harvest
# ---------------------------------------------------------------------------

@dataclass
class HarvestFingerprint:
    """Tracks per-URL harvest state for incremental scraping."""
    url: str
    content_hash: str
    last_harvested: str  # ISO timestamp
    http_etag: Optional[str] = None
    http_last_modified: Optional[str] = None
    consecutive_failures: int = 0
    last_error: Optional[str] = None

    @staticmethod
    def compute_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()


class FingerprintStore:
    """
    Persistent store for harvest fingerprints.
    Enables incremental harvests by tracking content hashes per URL.
    """

    def __init__(self, store_path: Optional[Path] = None):
        self.store_path = store_path or Path(
            "backend/data/harvest_fingerprints.json")
        self._data: dict = {}
        self._load()

    def _load(self):
        if self.store_path.exists():
            try:
                self._data = json.loads(self.store_path.read_text())
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Failed to load fingerprint store: {e}")
                self._data = {}

    def save(self):
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self.store_path.write_text(json.dumps(
            self._data, indent=2, default=str))

    def get(self, url: str) -> Optional[HarvestFingerprint]:
        raw = self._data.get(url)
        if raw:
            return HarvestFingerprint(**raw)
        return None

    def put(self, fp: HarvestFingerprint):
        self._data[fp.url] = asdict(fp)

    def needs_reharvest(
        self, url: str, content: str, max_age_hours: float = 24.0
    ) -> bool:
        """
        Check if URL needs re-harvesting.
        Returns True if:
        - Never harvested before
        - Content hash changed
        - Enough time has passed (max_age_hours)
        """
        fp = self.get(url)
        if fp is None:
            return True

        new_hash = HarvestFingerprint.compute_hash(content)
        if new_hash != fp.content_hash:
            return True

        last = datetime.fromisoformat(fp.last_harvested)
        age_hours = (datetime.now(timezone.utc) - last).total_seconds() / 3600
        return age_hours >= max_age_hours

    def get_all_urls(self) -> List[str]:
        """Return all tracked URLs."""
        return list(self._data.keys())

    def get_stale_urls(self, max_age_hours: float = 24.0) -> List[str]:
        """Return URLs that haven't been harvested within max_age_hours."""
        stale = []
        now = datetime.now(timezone.utc)
        for url, data in self._data.items():
            try:
                last = datetime.fromisoformat(data["last_harvested"])
                age = (now - last).total_seconds() / 3600
                if age >= max_age_hours:
                    stale.append(url)
            except (KeyError, ValueError):
                stale.append(url)
        return stale

    def get_failed_urls(self, min_failures: int = 3) -> List[str]:
        """Return URLs with consecutive failures above threshold."""
        return [
            url for url, data in self._data.items()
            if data.get("consecutive_failures", 0) >= min_failures
        ]


# ---------------------------------------------------------------------------
# Rate Limiter — respects per-domain crawl politeness
# ---------------------------------------------------------------------------

class RateLimiter:
    """
    Token-bucket style rate limiter keyed by domain.
    Ensures we don't overwhelm any single host.
    """

    def __init__(self, requests_per_second: float = 2.0):
        self._min_interval = 1.0 / requests_per_second
        self._last_request: dict = {}

    def wait(self, domain: str):
        """Block until it's safe to make another request to this domain."""
        now = time.monotonic()
        last = self._last_request.get(domain, 0.0)
        elapsed = now - last
        if elapsed < self._min_interval:
            sleep_time = self._min_interval - elapsed
            logger.debug(
                f"Rate limit: sleeping {sleep_time:.2f}s for {domain}")
            time.sleep(sleep_time)
        self._last_request[domain] = time.monotonic()


# ---------------------------------------------------------------------------
# Retry logic with exponential backoff
# ---------------------------------------------------------------------------

@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    backoff_factor: float = 2.0
    retryable_status_codes: tuple = (429, 500, 502, 503, 504)


def retry_with_backoff(func, retry_config: Optional[RetryConfig] = None, **kwargs):
    """
    Execute func with exponential backoff on failure.

    Each retry doubles the delay (up to max_delay).
    Returns the result on success, raises the last exception on exhaustion.
    """
    config = retry_config or RetryConfig()
    last_exception = None

    for attempt in range(config.max_retries + 1):
        try:
            result = func(**kwargs)
            return result
        except Exception as e:
            last_exception = e
            if attempt < config.max_retries:
                delay = min(
                    config.base_delay * (config.backoff_factor ** attempt),
                    config.max_delay,
                )
                logger.warning(
                    f"Attempt {attempt + 1}/{config.max_retries + 1} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)
            else:
                logger.error(
                    f"All {config.max_retries + 1} attempts failed: {e}"
                )

    raise last_exception  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Harvest result
# ---------------------------------------------------------------------------

@dataclass
class HarvestResult:
    """Structured result from harvesting a single URL."""
    url: str
    success: bool
    content: Optional[str] = None
    content_hash: Optional[str] = None
    was_cached: bool = False
    duration_ms: float = 0.0
    error: Optional[str] = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# Enhanced Harvester — main class
# ---------------------------------------------------------------------------

class EnhancedHarvester:
    """
    Improved Phase 1 harvester wrapping the existing scrapers with:

    - Incremental harvesting (skip unchanged pages via fingerprinting)
    - Rate limiting per domain (polite crawling)
    - Retry with exponential backoff on transient failures
    - Harvest fingerprinting for change detection across runs
    - Structured HarvestResult reporting with timing

    This does NOT replace HalilitPageScraper or OfficialBrandScraper —
    it wraps them with reliability infrastructure. The existing scrapers
    handle HTML parsing; this handles fetch reliability.
    """

    def __init__(
        self,
        fingerprint_store: Optional[FingerprintStore] = None,
        rate_limiter: Optional[RateLimiter] = None,
        retry_config: Optional[RetryConfig] = None,
        max_age_hours: float = 24.0,
    ):
        self.fingerprints = fingerprint_store or FingerprintStore()
        self.rate_limiter = rate_limiter or RateLimiter(
            requests_per_second=2.0)
        self.retry_config = retry_config or RetryConfig()
        self.max_age_hours = max_age_hours
        self._stats = {"total": 0, "skipped": 0, "fetched": 0, "failed": 0}

    def harvest_url(self, url: str, force: bool = False) -> HarvestResult:
        """
        Harvest a single URL with all protections.

        Args:
            url: The URL to fetch
            force: If True, bypass incremental check and always re-fetch

        Returns:
            HarvestResult with success/failure, content, timing, caching info
        """
        self._stats["total"] += 1
        domain = urllib.parse.urlparse(url).netloc
        start = time.monotonic()

        try:
            # Rate limit
            self.rate_limiter.wait(domain)

            # Fetch with retry
            content = retry_with_backoff(
                self._fetch, retry_config=self.retry_config, url=url
            )

            # Check if content actually changed (incremental)
            if not force and not self.fingerprints.needs_reharvest(
                url, content, self.max_age_hours
            ):
                self._stats["skipped"] += 1
                return HarvestResult(
                    url=url,
                    success=True,
                    content=content,
                    content_hash=HarvestFingerprint.compute_hash(content),
                    was_cached=True,
                    duration_ms=(time.monotonic() - start) * 1000,
                )

            # Content is new or changed — update fingerprint
            content_hash = HarvestFingerprint.compute_hash(content)
            self.fingerprints.put(
                HarvestFingerprint(
                    url=url,
                    content_hash=content_hash,
                    last_harvested=datetime.now(timezone.utc).isoformat(),
                    consecutive_failures=0,
                )
            )
            self.fingerprints.save()

            self._stats["fetched"] += 1
            return HarvestResult(
                url=url,
                success=True,
                content=content,
                content_hash=content_hash,
                duration_ms=(time.monotonic() - start) * 1000,
            )

        except Exception as e:
            self._stats["failed"] += 1

            # Track consecutive failures in fingerprint store
            fp = self.fingerprints.get(url)
            if fp:
                fp.consecutive_failures += 1
                fp.last_error = str(e)
                self.fingerprints.put(fp)
            else:
                self.fingerprints.put(
                    HarvestFingerprint(
                        url=url,
                        content_hash="",
                        last_harvested=datetime.now(timezone.utc).isoformat(),
                        consecutive_failures=1,
                        last_error=str(e),
                    )
                )
            self.fingerprints.save()

            return HarvestResult(
                url=url,
                success=False,
                error=str(e),
                duration_ms=(time.monotonic() - start) * 1000,
            )

    def harvest_batch(
        self, urls: List[str], force: bool = False
    ) -> List[HarvestResult]:
        """
        Harvest multiple URLs sequentially with rate limiting.

        Returns list of HarvestResult in the same order as input URLs.
        """
        results = []
        for url in urls:
            result = self.harvest_url(url, force=force)
            results.append(result)
        return results

    def _fetch(self, url: str) -> str:
        """
        Actually fetch a URL.
        Separated into its own method so retry_with_backoff can wrap it.
        """
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "HalilitSupportCenter/1.0 (Product Catalog Bot)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,he;q=0.8",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status >= 400:
                raise RuntimeError(f"HTTP {response.status} for {url}")
            return response.read().decode("utf-8", errors="replace")

    def get_stats(self) -> dict:
        """Return harvest statistics."""
        return dict(self._stats)

    def reset_stats(self):
        """Reset harvest statistics."""
        self._stats = {"total": 0, "skipped": 0, "fetched": 0, "failed": 0}


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_enhanced_harvester: Optional[EnhancedHarvester] = None


def get_enhanced_harvester() -> EnhancedHarvester:
    """Get or create the singleton EnhancedHarvester."""
    global _enhanced_harvester
    if _enhanced_harvester is None:
        _enhanced_harvester = EnhancedHarvester()
    return _enhanced_harvester
