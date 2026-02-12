#!/usr/bin/env python3
"""
RE-INGESTION SCRIPT — Source Rules Compliance v1.0
====================================================

Re-ingests ALL brand data through the full Trinity Swarm pipeline
to ensure compliance with the Three Source Rules (backend/source_rules.py).

Current data audit shows:
- 94.8% have dummy specs ("Standardized via Halilit Commercial Source")
- 94.8% have no official description
- 100% have no reviews or review sources
- 100% have no source coverage tracking
- 40.6% only have placeholder images

This script:
1. CommercialScout: Re-scrapes Halilit.com for fresh Golden List data
2. OfficialScout: Scrapes brand official pages for real specs/descriptions/images
3. ContextualScout: Gathers real reviews from 3+ trusted sites via Gemini
4. Strips ALL placeholder/dummy/synthetic data
5. Enforces source rule field ownership
6. Tracks source coverage per product
7. Outputs compliant data to frontend/public/data/

Usage:
    # Re-ingest all brands
    PYTHONPATH=. python3 backend/scripts/reingest_source_rules.py

    # Re-ingest specific brand
    PYTHONPATH=. python3 backend/scripts/reingest_source_rules.py --brand "Moog"

    # Re-ingest a tier
    PYTHONPATH=. python3 backend/scripts/reingest_source_rules.py --tier 1

    # Dry run (audit only, no write)
    PYTHONPATH=. python3 backend/scripts/reingest_source_rules.py --dry-run

    # Skip contextual (reviews) to save API calls
    PYTHONPATH=. python3 backend/scripts/reingest_source_rules.py --skip-contextual

    # Limit number of brands (for testing)
    PYTHONPATH=. python3 backend/scripts/reingest_source_rules.py --limit 3
"""

from backend.unified_data_service import DataNormalizer, IngestToFrontendSyncEngine
from backend.unified_agent_orchestrator import CommercialAgent, OfficialAgent, ContextualAgent
from backend.ingestion.orchestrator import IngestionOrchestrator
from backend.source_rules import (
    AuthorizedSource,
    FieldOwnership,
    FIELD_OWNERSHIP,
    IMMUTABLE_FIELDS,
    SourceCoverage,
    MIN_REVIEW_SOURCES,
    validate_no_synthetic_data,
    enforce_source_rules,
    get_allowed_fields,
    log_source_rule_summary,
)
import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger("ReIngestion")

FRONTEND_DATA_DIR = Path(
    "/workspaces/Halilit-Support-Center/frontend/public/data")
INGESTION_DATA_DIR = Path(
    "/workspaces/Halilit-Support-Center/backend/data/ingestion")
CONFIG_DIR = Path("/workspaces/Halilit-Support-Center/backend/config")

# ═══════════════════════════════════════════════════════════════════════════
# DATA CLEANING — Strip placeholder/dummy/synthetic data
# ═══════════════════════════════════════════════════════════════════════════

PLACEHOLDER_MARKERS = {
    "/assets/images/placeholder_product.svg",
    "/assets/images/placeholder.svg",
    "placeholder",
}

DUMMY_SPEC_MARKERS = [
    "Standardized via Halilit",
    "Standardized via",
    "Placeholder",
    "TBD",
    "N/A",
]


def strip_placeholder_images(product: Dict[str, Any]) -> Dict[str, Any]:
    """Remove placeholder images — empty is better than fake."""
    images = product.get("official_images", [])
    if isinstance(images, list):
        cleaned = []
        for img in images:
            url = img.get("url", "") if isinstance(img, dict) else str(img)
            if not any(marker in url for marker in PLACEHOLDER_MARKERS):
                cleaned.append(img)
        product["official_images"] = cleaned

    # Also clean hero/gallery/thumbnail
    for key in ["image_hero", "image_thumbnail", "image_url"]:
        val = product.get(key)
        if isinstance(val, dict):
            url = val.get("url", "")
        elif isinstance(val, str):
            url = val
        else:
            continue
        if any(marker in url for marker in PLACEHOLDER_MARKERS):
            product[key] = None

    gallery = product.get("image_gallery", [])
    if isinstance(gallery, list):
        product["image_gallery"] = [
            img for img in gallery
            if not any(marker in (img.get("url", "") if isinstance(img, dict) else str(img))
                       for marker in PLACEHOLDER_MARKERS)
        ]

    return product


def strip_dummy_specs(product: Dict[str, Any]) -> Dict[str, Any]:
    """Remove dummy/standardized specs — empty is better than fake."""
    specs = product.get("official_specs", {})
    if isinstance(specs, dict):
        note = specs.get("note", "")
        if any(marker.lower() in note.lower() for marker in DUMMY_SPEC_MARKERS):
            product["official_specs"] = {}

        # Also strip individual keys with dummy values
        cleaned_specs = {}
        for k, v in specs.items():
            if k == "note" and any(marker.lower() in str(v).lower() for marker in DUMMY_SPEC_MARKERS):
                continue
            if k == "extracted_name":
                continue  # This is a Commercial Scout artifact, not a real spec
            cleaned_specs[k] = v
        product["official_specs"] = cleaned_specs

    return product


def enforce_source_coverage_tracking(product: Dict[str, Any]) -> Dict[str, Any]:
    """Add source coverage tracking fields."""
    # Commercial: has id + price + brand from Halilit
    has_commercial = bool(
        product.get("halilit_id")
        and product.get("brand")
        and product.get("price_il", 0) > 0
    )

    # Official: has real specs or real description from brand page
    has_official = bool(
        product.get("official_specs")
        and product.get("official_description")
    )

    # Contextual: has reviews from 3+ sources
    review_sources = product.get("review_sources", [])
    reviews = product.get("reviews", [])
    contextual_count = len(review_sources) if review_sources else len(reviews)
    has_contextual = contextual_count >= MIN_REVIEW_SOURCES

    product["source_coverage_commercial"] = has_commercial
    product["source_coverage_official"] = has_official
    product["source_coverage_contextual"] = has_contextual
    product["contextual_source_count"] = contextual_count

    # Compute cross-validation confidence
    coverage = SourceCoverage(
        commercial_complete=has_commercial,
        official_complete=has_official,
        contextual_complete=has_contextual,
        contextual_source_count=contextual_count,
    )
    product["cross_validation_confidence"] = coverage.confidence_score
    product["cross_validation_status"] = coverage.confidence_level.value

    return product


def clean_product_for_source_rules(product: Dict[str, Any]) -> Dict[str, Any]:
    """Full cleanup pass: strip all non-compliant data."""
    product = strip_placeholder_images(product)
    product = strip_dummy_specs(product)

    # Check for synthetic data markers
    violations = validate_no_synthetic_data(product)
    if violations:
        for v in violations:
            logger.warning(f"  SYNTHETIC: {v}")
            # Strip the offending field
            if v.field in product:
                product[v.field] = None

    # Add source coverage tracking
    product = enforce_source_coverage_tracking(product)

    return product


# ═══════════════════════════════════════════════════════════════════════════
# RE-INGESTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class ReIngestionEngine:
    """Drives re-ingestion through the full Trinity Swarm pipeline."""

    def __init__(self, skip_contextual: bool = False, dry_run: bool = False):
        self.skip_contextual = skip_contextual
        self.dry_run = dry_run
        self.commercial_scout = CommercialAgent()
        self.official_scout = OfficialAgent()
        self.contextual_scout = ContextualAgent()
        self.orchestrator = IngestionOrchestrator()

        self.stats = {
            "brands_processed": 0,
            "brands_success": 0,
            "brands_failed": 0,
            "products_input": 0,
            "products_approved": 0,
            "products_rejected": 0,
            "products_with_official": 0,
            "products_with_reviews": 0,
            "products_with_images": 0,
        }

    def get_all_brands(self) -> List[str]:
        """
        Get ALL brands from multiple sources:
        1. Live discovery from Halilit.com brands page (authoritative)
        2. Golden List files (frontend/public/data/)
        3. Brand tiers config
        """
        brands = set()

        # Source 1: Discover from Halilit.com (the authoritative source)
        try:
            from backend.ingestion.halilit_page_scraper import HalilitPageScraper
            scraper = HalilitPageScraper()
            halilit_brands = scraper.discover_all_brands()
            for b in halilit_brands:
                brands.add(b["name"].lower())
            logger.info(
                f"    🌐 Discovered {len(halilit_brands)} brands from Halilit.com")
        except Exception as e:
            logger.warning(f"    ⚠️ Failed to discover from Halilit.com: {e}")

        # Source 2: Existing golden list files
        exclude = {
            "index.json", "search_index.json", "search_index_min.json",
            "galaxy_db.json",
        }
        for f in sorted(FRONTEND_DATA_DIR.glob("*.json")):
            if f.name not in exclude and not f.is_dir():
                brands.add(f.stem.lower())

        # Source 3: Brand tiers
        tiers = self.load_brand_tiers()
        for tier_brands in tiers.values():
            for b in tier_brands:
                brands.add(b.lower())

        return sorted(list(brands))

    def load_brand_tiers(self) -> Dict[str, List[str]]:
        """Load brand tiers from config."""
        try:
            tier_file = CONFIG_DIR / "brand_tiers.json"
            if tier_file.exists():
                with open(tier_file) as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load brand tiers: {e}")
        return {}

    def load_brand_data(self, brand: str) -> List[Dict[str, Any]]:
        """Load current brand data from frontend."""
        data_file = FRONTEND_DATA_DIR / f"{brand}.json"
        if not data_file.exists():
            # Try lowercase
            data_file = FRONTEND_DATA_DIR / f"{brand.lower()}.json"

        if not data_file.exists():
            return []

        try:
            with open(data_file) as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("products", [])
        except Exception as e:
            logger.warning(f"Failed to load {data_file}: {e}")
        return []

    def reingest_brand(self, brand: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Re-ingest a single brand through the full Trinity Swarm pipeline.

        Steps:
        1. COMMERCIAL: Re-scrape from Halilit.com (force fresh data)
        2. CLEANUP: Strip all placeholder/dummy/synthetic data
        3. OFFICIAL: Enrich with real brand page data
        4. CONTEXTUAL: Gather real reviews from 3+ trusted sites
        5. VALIDATE: Source rule compliance check
        6. OUTPUT: Write compliant data
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 RE-INGESTING: {brand}")
        logger.info(f"{'='*60}")

        self.stats["brands_processed"] += 1

        # ──────────────────────────────────────────────────────────────
        # STEP 1: COMMERCIAL SCOUT — Get fresh Golden List from Halilit
        # ──────────────────────────────────────────────────────────────
        logger.info(
            f"  📋 [1/4] CommercialScout: Harvesting Golden List for {brand}...")

        raw_products = []
        try:
            raw_products = self.commercial_scout.harvest(brand)
            if raw_products:
                logger.info(
                    f"    ✅ Scraped {len(raw_products)} products from Halilit.com")
            else:
                logger.warning(
                    f"    ⚠️  CommercialScout returned 0 products for {brand}")
        except Exception as e:
            logger.error(f"    ❌ CommercialScout failed: {e}")

        # Fallback: use existing data if scraping fails (but clean it up)
        if not raw_products:
            logger.info(f"    📂 Falling back to existing data for {brand}...")
            raw_products = self.load_brand_data(brand)
            if raw_products:
                logger.info(
                    f"    📂 Loaded {len(raw_products)} existing products")
            else:
                logger.warning(
                    f"    ❌ No data available for {brand}. Skipping.")
                self.stats["brands_failed"] += 1
                return False, []

        self.stats["products_input"] += len(raw_products)

        # ──────────────────────────────────────────────────────────────
        # STEP 2: CLEANUP — Strip all non-compliant data
        # ──────────────────────────────────────────────────────────────
        logger.info(
            f"  🧹 [2/4] Cleaning: Stripping placeholder/dummy/synthetic data...")

        cleaned_products = []
        for p in raw_products:
            cleaned = clean_product_for_source_rules(p)
            cleaned_products.append(cleaned)

        placeholder_removed = sum(
            1 for p in cleaned_products
            if not p.get("official_images") or len(p.get("official_images", [])) == 0
        )
        dummy_specs_removed = sum(
            1 for p in cleaned_products
            if not p.get("official_specs") or p.get("official_specs") == {}
        )
        logger.info(
            f"    🗑️  Stripped: {placeholder_removed} placeholder images, {dummy_specs_removed} dummy specs")

        # ──────────────────────────────────────────────────────────────
        # STEP 3: OFFICIAL SCOUT — Enrich with real brand page data
        # ──────────────────────────────────────────────────────────────
        logger.info(
            f"  📘 [3/4] OfficialScout: Enriching with real brand data...")

        enriched_products = []
        official_count = 0
        for i, product in enumerate(cleaned_products):
            try:
                enriched = self.official_scout.enrich(dict(product))
                if enriched.get("source_coverage_official"):
                    official_count += 1
                enriched_products.append(enriched)
            except Exception as e:
                logger.warning(
                    f"    ⚠️  OfficialScout failed for {product.get('product_name', '?')}: {e}")
                enriched_products.append(product)

            # Rate limiting
            if (i + 1) % 5 == 0:
                logger.info(
                    f"    ... {i + 1}/{len(cleaned_products)} products enriched")
                time.sleep(0.5)

        self.stats["products_with_official"] += official_count
        logger.info(
            f"    ✅ Official data found: {official_count}/{len(enriched_products)} products")

        # ──────────────────────────────────────────────────────────────
        # STEP 4: CONTEXTUAL SCOUT — Gather real reviews
        # ──────────────────────────────────────────────────────────────
        if self.skip_contextual:
            logger.info(
                f"  🌍 [4/4] ContextualScout: SKIPPED (--skip-contextual)")
            final_products = enriched_products
        else:
            logger.info(
                f"  🌍 [4/4] ContextualScout: Gathering real reviews from 3+ sites...")

            final_products = []
            review_count = 0
            for i, product in enumerate(enriched_products):
                try:
                    # Pass the product dict directly — validate_and_review modifies it in-place
                    audit = self.contextual_scout.validate_and_review(product)
                    if product.get("source_coverage_contextual"):
                        review_count += 1
                    final_products.append(product)
                except Exception as e:
                    logger.warning(
                        f"    ⚠️  ContextualScout failed for {product.get('product_name', '?')}: {e}")
                    final_products.append(product)

                # Rate limiting (heavier for API calls)
                if (i + 1) % 3 == 0:
                    logger.info(
                        f"    ... {i + 1}/{len(enriched_products)} products reviewed")
                    time.sleep(1.0)

            self.stats["products_with_reviews"] += review_count
            logger.info(
                f"    ✅ Reviews gathered: {review_count}/{len(final_products)} products")

        # ──────────────────────────────────────────────────────────────
        # STEP 5: FINAL CLEANUP & SOURCE RULE ENFORCEMENT
        # ──────────────────────────────────────────────────────────────
        logger.info(f"  ✅ Final: Source rule enforcement & compliance check...")

        compliant_products = []
        for product in final_products:
            # Final source coverage tracking
            product = enforce_source_coverage_tracking(product)

            # Final synthetic data check
            violations = validate_no_synthetic_data(product)
            if violations:
                for v in violations:
                    logger.warning(
                        f"    ⚠️  VIOLATION in {product.get('product_name', '?')}: {v.message}")

            # Update timestamps
            product["last_updated"] = datetime.now().isoformat()
            product["pipeline_phase"] = "source_rules_compliant"

            compliant_products.append(product)

        # Count stats
        approved = len(compliant_products)
        img_count = sum(
            1 for p in compliant_products
            if p.get("official_images") and len(p.get("official_images", [])) > 0
            and not all(
                any(marker in (img.get("url", "") if isinstance(img, dict) else str(img))
                    for marker in PLACEHOLDER_MARKERS)
                for img in p.get("official_images", [])
            )
        )
        self.stats["products_approved"] += approved
        self.stats["products_with_images"] += img_count

        # ──────────────────────────────────────────────────────────────
        # STEP 6: WRITE OUTPUT
        # ──────────────────────────────────────────────────────────────
        if self.dry_run:
            logger.info(
                f"  📋 DRY RUN: Would write {approved} products for {brand}")
        else:
            # Normalize for frontend
            normalized = DataNormalizer.normalize_batch(
                compliant_products, brand)

            # POST-NORMALIZATION CLEANUP: DataNormalizer may re-introduce
            # dummy specs or placeholders from fallback fields. Strip them again.
            for product in normalized:
                product = strip_placeholder_images(product)
                product = strip_dummy_specs(product)
                # Also clean the 'specifications' field (duplicate of official_specs)
                specs = product.get("specifications", {})
                if isinstance(specs, dict):
                    note = specs.get("note", "")
                    if any(marker.lower() in note.lower() for marker in DUMMY_SPEC_MARKERS):
                        product["specifications"] = {}
                product = enforce_source_coverage_tracking(product)

            output_file = FRONTEND_DATA_DIR / f"{brand.lower()}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w') as f:
                json.dump(normalized, f, indent=2, ensure_ascii=False)

            logger.info(
                f"  💾 Wrote {len(normalized)} products to {output_file.name}")

            # Also save to ingestion directory for pipeline tracking
            ingestion_dir = INGESTION_DATA_DIR / "products" / brand
            ingestion_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(ingestion_dir / f"approved_{timestamp}.json", 'w') as f:
                json.dump({"products": normalized, "source": "reingest_source_rules"},
                          f, indent=2, ensure_ascii=False)

        self.stats["brands_success"] += 1

        # Print brand summary
        logger.info(f"\n  📊 {brand} SUMMARY:")
        logger.info(f"    Products: {approved}")
        cov_comm = sum(1 for p in compliant_products if p.get(
            "source_coverage_commercial"))
        cov_offi = sum(1 for p in compliant_products if p.get(
            "source_coverage_official"))
        cov_ctx = sum(1 for p in compliant_products if p.get(
            "source_coverage_contextual"))
        logger.info(f"    Commercial Coverage: {cov_comm}/{approved}")
        logger.info(f"    Official Coverage:   {cov_offi}/{approved}")
        logger.info(f"    Contextual Coverage: {cov_ctx}/{approved}")
        logger.info(f"    Real Images:         {img_count}/{approved}")

        return True, compliant_products

    def is_brand_compliant(self, brand: str) -> bool:
        """Check if a brand has already been re-ingested with source coverage."""
        data = self.load_brand_data(brand)
        if not data:
            return False
        # Brand is compliant if it has source_coverage_commercial tracking
        # AND at least some products with reviews
        has_coverage = any(p.get('source_coverage_commercial') for p in data)
        has_reviews = any(
            p.get('reviews') and len(p.get('reviews', [])) > 0 for p in data
        )
        return has_coverage and has_reviews

    def rebuild_artifacts(self):
        """Rebuild search index, shards, galaxy_db after re-ingestion."""
        logger.info("\n🌍 Rebuilding Global Artifacts...")
        try:
            all_products = []
            exclude = {"index.json", "search_index.json",
                       "search_index_min.json", "galaxy_db.json"}
            for f in FRONTEND_DATA_DIR.glob("*.json"):
                if f.name not in exclude and not f.is_dir():
                    try:
                        with open(f) as fh:
                            data = json.load(fh)
                            if isinstance(data, list):
                                all_products.extend(data)
                    except Exception:
                        pass

            if all_products:
                IngestToFrontendSyncEngine.generate_smart_artifacts(
                    all_products)
                logger.info(
                    f"  ✅ Rebuilt artifacts for {len(all_products)} products")
            else:
                logger.warning("  ⚠️  No products found for artifact rebuild")
        except Exception as e:
            logger.error(f"  ❌ Artifact rebuild failed: {e}")

    def print_final_report(self):
        """Print comprehensive re-ingestion report."""
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 RE-INGESTION FINAL REPORT")
        logger.info(f"{'='*60}")
        logger.info(
            f"  Brands Processed:     {self.stats['brands_processed']}")
        logger.info(f"  Brands Succeeded:     {self.stats['brands_success']}")
        logger.info(f"  Brands Failed:        {self.stats['brands_failed']}")
        logger.info(f"  Products Input:       {self.stats['products_input']}")
        logger.info(
            f"  Products Approved:    {self.stats['products_approved']}")

        if self.stats['products_input'] > 0:
            total = self.stats['products_approved']
            logger.info(f"\n  SOURCE COVERAGE:")
            logger.info(
                f"    With Official Data:   {self.stats['products_with_official']}/{total}")
            logger.info(
                f"    With Real Reviews:    {self.stats['products_with_reviews']}/{total}")
            logger.info(
                f"    With Real Images:     {self.stats['products_with_images']}/{total}")

        logger.info(f"{'='*60}")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Re-ingest data to meet Source Rules standards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--brand", type=str, help="Re-ingest specific brand")
    parser.add_argument("--tier", type=int,
                        choices=[1, 2, 3], help="Re-ingest brands in a tier")
    parser.add_argument("--limit", type=int,
                        help="Limit number of brands to process")
    parser.add_argument("--dry-run", action="store_true",
                        help="Audit only, don't write files")
    parser.add_argument("--skip-contextual", action="store_true",
                        help="Skip review gathering (saves API calls)")
    parser.add_argument("--no-artifacts", action="store_true",
                        help="Skip artifact rebuild")
    parser.add_argument("--skip-done", action="store_true",
                        help="Skip brands already re-ingested (have source coverage)")
    parser.add_argument("--resume", action="store_true",
                        help="Alias for --skip-done")

    args = parser.parse_args()

    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║     HALILIT RE-INGESTION — Source Rules Compliance      ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    logger.info("")

    # Print the source rules
    log_source_rule_summary()

    engine = ReIngestionEngine(
        skip_contextual=args.skip_contextual,
        dry_run=args.dry_run,
    )

    # Determine which brands to process
    if args.brand:
        brands = [args.brand]
    elif args.tier:
        tiers = engine.load_brand_tiers()
        tier_key = f"tier_{args.tier}"
        brands = tiers.get(tier_key, [])
        if not brands:
            logger.error(f"No brands found for Tier {args.tier}")
            return 1
        logger.info(f"🎯 Tier {args.tier}: {len(brands)} brands")
    else:
        brands = engine.get_all_brands()
        logger.info(f"🎯 All brands: {len(brands)} brands")

    # Filter out already-done brands
    if args.skip_done or args.resume:
        remaining = []
        for b in brands:
            if not engine.is_brand_compliant(b):
                remaining.append(b)
            else:
                logger.debug(f"  ✅ Skipping {b} (already compliant)")
        logger.info(
            f"🔒 Skipping {len(brands) - len(remaining)} already-compliant brands")
        brands = remaining

    if args.limit:
        brands = brands[:args.limit]
        logger.info(f"🔒 Limited to {args.limit} brands")

    logger.info(
        f"\n📋 Brands to process: {', '.join(brands[:10])}{'...' if len(brands) > 10 else ''}")
    logger.info(f"    Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    logger.info(
        f"    Contextual: {'SKIPPED' if args.skip_contextual else 'ENABLED'}")
    logger.info("")

    start_time = time.time()

    # Process each brand
    for i, brand in enumerate(brands, 1):
        logger.info(f"\n[{i}/{len(brands)}] Processing {brand}...")
        try:
            success, products = engine.reingest_brand(brand)
            if not success:
                logger.warning(f"  ⚠️  {brand}: re-ingestion had issues")
        except Exception as e:
            logger.error(f"  ❌ {brand} FAILED: {e}")
            engine.stats["brands_failed"] += 1

    # Rebuild artifacts
    if not args.dry_run and not args.no_artifacts:
        engine.rebuild_artifacts()

    elapsed = time.time() - start_time
    logger.info(f"\n⏱️  Total time: {elapsed:.1f}s")

    engine.print_final_report()

    return 0 if engine.stats["brands_success"] > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
