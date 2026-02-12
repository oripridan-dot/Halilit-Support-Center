"""
Enhanced Pipeline Orchestrator v2.0

Integrates all pipeline improvements into the existing 6-phase architecture,
adding new capabilities while preserving compatibility with the existing
IngestionOrchestrator, TrinityIngestionBridge, and SpectrumAdapter.

Architecture:
─────────────────────────────────────────────────────────────────────────
Existing system:
  TrinitySwarm → IngestionOrchestrator (6 phases) → SpectrumAdapter → DB

Enhanced system (this module):
  EnhancedHarvester → IngestionOrchestrator + AI Cache → CrossValidator
                    → ImageProcessor → DiffPublisher
  ──── all wrapped in PipelineTelemetry ────

This does NOT replace the existing orchestrator — it wraps and extends it
with reliability infrastructure (retries, caching, telemetry, diff publishing).

Usage:
    from backend.ingestion.enhanced_pipeline import get_enhanced_pipeline

    pipeline = get_enhanced_pipeline()
    result = pipeline.run(brand="Nord")
    print(result["telemetry"])
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from backend.ingestion.enhanced_harvester import (
    EnhancedHarvester,
    FingerprintStore,
    RateLimiter,
    RetryConfig,
)
from backend.ingestion.cross_validator import CrossValidator
from backend.ingestion.image_processor import ImageProcessor
from backend.ingestion.diff_publisher import DiffPublisher
from backend.ingestion.pipeline_telemetry import PipelineTelemetry
from backend.ingestion.ai_cache import AIResponseCache

logger = logging.getLogger("EnhancedPipeline")


class EnhancedPipeline:
    """
    The improved 7-phase pipeline:

    Phase 1 — HARVEST:         Enhanced scraping (retry/backoff/rate-limit/incremental)
    Phase 2 — NORMALIZE:       Product shape normalization + deduplication
    Phase 3 — VALIDATE:        Source Rules enforcement (Three Source Rules gate)
    Phase 4 — ENRICH:          AI enrichment with response caching
    Phase 5 — VISUAL:          Image optimization (WebP + variant generation)
    Phase 6 — CROSS-VALIDATE:  Multi-source consistency scoring
    Phase 7 — PUBLISH:         Diff-based catalog publishing with snapshots

    All phases wrapped in PipelineTelemetry for complete observability.

    Compatibility:
    - Uses existing IngestionOrchestrator for phases 2–3
    - Uses existing TrinitySwarm agents for enrichment
    - Uses existing source_rules.py for validation
    - Adds new capabilities on top without breaking changes
    """

    def __init__(self):
        # New enhanced components
        self.harvester = EnhancedHarvester(
            fingerprint_store=FingerprintStore(),
            rate_limiter=RateLimiter(requests_per_second=2.0),
            retry_config=RetryConfig(max_retries=3, base_delay=1.0),
        )
        self.cross_validator = CrossValidator()
        self.image_processor = ImageProcessor()
        self.publisher = DiffPublisher()
        self.telemetry = PipelineTelemetry()
        self.ai_cache = AIResponseCache()

        logger.info("Enhanced Pipeline initialized with all components")

    def run(
        self,
        brand: Optional[str] = None,
        urls: Optional[List[str]] = None,
        raw_products: Optional[List[Dict]] = None,
        force_harvest: bool = False,
        skip_images: bool = False,
        trigger: str = "manual",
    ) -> Dict[str, Any]:
        """
        Execute the full enhanced pipeline.

        Entry modes (in priority order):
        1. raw_products — pre-scraped product dicts (skip harvest)
        2. urls — specific URLs to harvest
        3. brand — look up URLs from Golden List for this brand

        Args:
            brand: Brand name to process (looks up URLs from Golden List)
            urls: Specific URLs to harvest
            raw_products: Pre-scraped products (skip harvest phase)
            force_harvest: If True, re-fetch even if fingerprints say unchanged
            skip_images: If True, skip image optimization phase
            trigger: Who/what initiated this run (for telemetry)

        Returns:
            Dict with run_id, product count, stats, and telemetry
        """
        run_id = self._make_run_id(brand)

        with self.telemetry.run(run_id, trigger=trigger) as run:
            products: List[Dict] = []

            # ── Phase 1: HARVEST ──
            if raw_products:
                # Skip harvest — products already provided
                products = list(raw_products)
                logger.info(
                    f"Phase 1 skipped — {len(products)} products provided"
                )
            else:
                with run.phase("harvest") as phase:
                    harvest_urls = urls or self._resolve_urls(brand)
                    phase.items_input = len(harvest_urls)

                    for url in harvest_urls:
                        result = self.harvester.harvest_url(
                            url, force=force_harvest
                        )
                        if result.success and result.content:
                            # Parse raw HTML into product dicts
                            parsed = self._parse_harvest_content(
                                result.content, result.url
                            )
                            products.extend(parsed)
                            if result.was_cached:
                                phase.items_skipped += 1
                        else:
                            phase.items_failed += 1
                            if result.error:
                                phase.errors.append(
                                    f"{url}: {result.error}"
                                )

                    phase.items_output = len(products)

            run.products_in = len(products)

            # ── Phase 2: NORMALIZE + DEDUPLICATE ──
            with run.phase("normalize") as phase:
                phase.items_input = len(products)
                products = self._normalize(products, brand)
                before_dedup = len(products)
                products = self._deduplicate(products)
                deduped = before_dedup - len(products)
                if deduped > 0:
                    logger.info(
                        f"Deduplication removed {deduped} products"
                    )
                phase.items_output = len(products)
                phase.items_skipped = deduped

            # ── Phase 3: VALIDATE (Source Rules) ──
            with run.phase("validate") as phase:
                phase.items_input = len(products)
                products, rejected = self._validate_source_rules(products)
                phase.items_output = len(products)
                phase.items_failed = len(rejected)
                for r in rejected:
                    phase.errors.append(
                        f"Rejected: {r.get('id', r.get('sku', 'unknown'))}"
                    )

            # ── Phase 4: ENRICH (with AI cache) ──
            with run.phase("enrich") as phase:
                phase.items_input = len(products)
                products = self._enrich_with_cache(products, brand)
                phase.items_output = len(products)
                cache_stats = self.ai_cache.get_stats()
                logger.info(
                    f"AI cache stats: {cache_stats['hit_rate']} hit rate "
                    f"({cache_stats['hits']} hits, {cache_stats['misses']} misses)"
                )

            # ── Phase 5: VISUAL (optional) ──
            if not skip_images:
                with run.phase("visual") as phase:
                    phase.items_input = len(products)
                    products = self._process_images(products)
                    phase.items_output = len(products)
            else:
                logger.info("Phase 5 (visual) skipped by request")

            # ── Phase 6: CROSS-VALIDATE ──
            with run.phase("cross_validate") as phase:
                phase.items_input = len(products)
                products = self._cross_validate(products)
                phase.items_output = len(products)

                # Count low-confidence products
                low_conf = sum(
                    1 for p in products
                    if p.get("_cross_validation", {}).get(
                        "overall_confidence", 0
                    ) < 0.35
                )
                phase.items_failed = low_conf
                if low_conf:
                    phase.errors.append(
                        f"{low_conf} products below MINIMAL confidence"
                    )

            # ── Phase 7: PUBLISH ──
            pub_result = None
            with run.phase("publish") as phase:
                phase.items_input = len(products)

                # Determine catalog filename
                filename = (
                    f"{brand.lower().replace(' ', '_')}.json"
                    if brand
                    else "catalog.json"
                )

                pub_result = self.publisher.publish(products, filename)
                phase.items_output = (
                    len(products) if pub_result.success else 0
                )

                if not pub_result.success:
                    phase.errors.append(
                        pub_result.error or "Unknown publish error"
                    )
                elif pub_result.diff.has_changes:
                    logger.info(f"Published: {pub_result.diff.summary}")
                else:
                    logger.info("No changes to publish")

            run.products_out = len(products)

        # ── Build result summary ──
        return {
            "run_id": run_id,
            "brand": brand,
            "products_in": run.products_in,
            "products_out": run.products_out,
            "harvest_stats": self.harvester.get_stats(),
            "cache_stats": self.ai_cache.get_stats(),
            "publish_diff": (
                pub_result.diff.to_dict() if pub_result else None
            ),
            "telemetry": self.telemetry.get_last_run(),
        }

    # ------------------------------------------------------------------
    # Phase implementations
    # ------------------------------------------------------------------

    def _resolve_urls(self, brand: Optional[str] = None) -> List[str]:
        """
        Resolve harvest URLs from the Golden List or URL config.

        For a specific brand: reads from data/brands/{brand}/urls.txt
        For all brands: reads from data/halilit_urls.txt
        """
        if brand:
            brand_urls_path = Path(
                f"backend/data/brands/{brand.lower()}/urls.txt"
            )
            if brand_urls_path.exists():
                urls = [
                    line.strip()
                    for line in brand_urls_path.read_text().splitlines()
                    if line.strip() and not line.startswith("#")
                ]
                if urls:
                    return urls

        # Fallback: master URL list
        master_path = Path("backend/data/halilit_urls.txt")
        if master_path.exists():
            return [
                line.strip()
                for line in master_path.read_text().splitlines()
                if line.strip() and not line.startswith("#")
            ]

        # Golden list check
        golden_path = Path("backend/data/golden_list.json")
        if golden_path.exists():
            try:
                data = json.loads(golden_path.read_text())
                if isinstance(data, list):
                    return [
                        item.get("url", item)
                        if isinstance(item, dict) else str(item)
                        for item in data
                    ]
                if isinstance(data, dict):
                    return list(data.get("urls", []))
            except (json.JSONDecodeError, OSError):
                pass

        logger.warning("No harvest URLs found")
        return []

    def _parse_harvest_content(
        self, content: str, source_url: str
    ) -> List[Dict]:
        """
        Parse raw HTML content into product dicts.
        Delegates to the existing HalilitPageScraper for actual parsing.
        """
        try:
            from backend.ingestion.halilit_page_scraper import (
                HalilitPageScraper,
            )
            scraper = HalilitPageScraper()
            result = scraper.scrape_product_page(source_url)
            if result:
                return [result] if isinstance(result, dict) else result
        except Exception as e:
            logger.warning(f"Failed to parse content from {source_url}: {e}")

        return []

    def _normalize(
        self, products: List[Dict], brand: Optional[str] = None
    ) -> List[Dict]:
        """
        Phase 2: Normalize product shape.
        Delegates to existing ProductNormalizer or IngestionOrchestrator.
        """
        try:
            from backend.product_normalizer import normalize_product

            normalized = []
            for p in products:
                try:
                    norm = normalize_product(p)
                    if norm:
                        # Ensure brand is set
                        if brand and not norm.get("brand"):
                            norm["brand"] = brand
                        normalized.append(norm)
                except Exception as e:
                    logger.warning(
                        f"Normalization failed for "
                        f"{p.get('name', 'unknown')}: {e}"
                    )
                    normalized.append(p)  # Keep raw if normalization fails
            return normalized

        except ImportError:
            logger.warning(
                "ProductNormalizer not available, returning raw products"
            )
            return products

    def _deduplicate(self, products: List[Dict]) -> List[Dict]:
        """
        Remove duplicate products based on SKU (exact) and title (normalized).
        """
        seen_skus: set = set()
        seen_titles: set = set()
        unique: List[Dict] = []

        for p in products:
            sku = str(p.get("sku", "")).strip()
            title = str(p.get("name", p.get("title", ""))).strip().lower()

            # SKU-based dedup (exact match)
            if sku and sku in seen_skus:
                logger.debug(f"Dedup: duplicate SKU '{sku}'")
                continue

            # Title-based dedup (normalized)
            if title and title in seen_titles:
                logger.debug(f"Dedup: duplicate title '{title[:50]}'")
                continue

            if sku:
                seen_skus.add(sku)
            if title:
                seen_titles.add(title)
            unique.append(p)

        return unique

    def _validate_source_rules(
        self, products: List[Dict]
    ) -> tuple:
        """
        Phase 3: Enforce Three Source Rules.
        Delegates to existing source_rules.py enforcement.
        """
        try:
            from backend.source_rules import (
                validate_no_synthetic_data,
                AuthorizedSource,
            )

            valid = []
            rejected = []

            for p in products:
                violations = validate_no_synthetic_data(p)
                if violations:
                    p["_rejection_reason"] = [str(v) for v in violations]
                    rejected.append(p)
                else:
                    valid.append(p)

            return valid, rejected

        except ImportError:
            logger.warning(
                "source_rules not available — passing all products"
            )
            return products, []

    def _enrich_with_cache(
        self, products: List[Dict], brand: Optional[str] = None
    ) -> List[Dict]:
        """
        Phase 4: AI enrichment with response caching.
        Checks cache before calling expensive Gemini API.
        """
        enriched = []

        for p in products:
            pid = p.get("id") or p.get("sku") or p.get("name", "unknown")

            # Check cache first
            cached = self.ai_cache.get("enrich", p)
            if cached:
                enriched.append(cached)
                continue

            # No cache hit — try enrichment via existing agents
            try:
                from backend.unified_agent_orchestrator import OfficialAgent

                agent = OfficialAgent()
                result = agent.enrich(p)

                if result and isinstance(result, dict):
                    # Merge enrichment into product
                    merged = {**p, **result}
                    self.ai_cache.put("enrich", p, merged)
                    enriched.append(merged)
                else:
                    enriched.append(p)

            except Exception as e:
                logger.warning(f"Enrichment failed for {pid}: {e}")
                enriched.append(p)

        return enriched

    def _process_images(self, products: List[Dict]) -> List[Dict]:
        """
        Phase 5: Image optimization and variant generation.
        """
        for p in products:
            pid = p.get("id") or p.get("sku") or "unknown"
            images = p.get("images", {})
            hero = images.get("hero") or p.get("image_url")

            if not hero and not images.get("gallery"):
                continue

            try:
                if hero:
                    result = self.image_processor.process_image(
                        hero, str(pid), ["hero", "thumbnail"]
                    )
                    if result.success and result.variants:
                        p.setdefault("processed_images", {})
                        for v in result.variants:
                            p["processed_images"][v.variant_type] = v.path

            except Exception as e:
                logger.warning(
                    f"Image processing failed for {pid}: {e}"
                )

        return products

    def _cross_validate(self, products: List[Dict]) -> List[Dict]:
        """
        Phase 6: Cross-source validation and confidence scoring.
        """
        for p in products:
            result = self.cross_validator.validate(p)

            p["_cross_validation"] = {
                "overall_confidence": result.overall_confidence,
                "confidence_tier": result.confidence_tier,
                "source_coverage": result.source_coverage,
                "field_scores": result.field_scores,
                "issue_count": len(result.issues),
                "error_count": result.error_count,
                "warning_count": result.warning_count,
                "issues": [
                    {
                        "field": i.field,
                        "severity": i.severity,
                        "message": i.message,
                    }
                    for i in result.issues[:20]  # Cap for storage
                ],
            }

            # Set top-level confidence for the frontend
            p["confidence"] = result.confidence_tier
            p["confidence_score"] = round(result.overall_confidence, 4)

        return products

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_run_id(self, brand: Optional[str] = None) -> str:
        """Generate a unique run ID."""
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        if brand:
            safe_brand = brand.lower().replace(" ", "_")[:20]
            return f"pipeline_{safe_brand}_{ts}"
        return f"pipeline_{ts}"

    # ------------------------------------------------------------------
    # Status & diagnostics
    # ------------------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status and component health."""
        return {
            "health": self.telemetry.get_health_status(),
            "last_run": self.telemetry.get_last_run(),
            "cache_stats": self.ai_cache.get_stats(),
            "cache_size": self.ai_cache.get_cache_size(),
            "harvest_stats": self.harvester.get_stats(),
            "image_stats": self.image_processor.get_stats(),
            "phase_averages": self.telemetry.get_phase_averages(),
        }

    def get_history(self, limit: int = 10) -> List[dict]:
        """Get recent pipeline run history."""
        return self.telemetry.get_history(limit=limit)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_enhanced_pipeline: Optional[EnhancedPipeline] = None


def get_enhanced_pipeline() -> EnhancedPipeline:
    """Get or create the singleton EnhancedPipeline."""
    global _enhanced_pipeline
    if _enhanced_pipeline is None:
        _enhanced_pipeline = EnhancedPipeline()
    return _enhanced_pipeline
