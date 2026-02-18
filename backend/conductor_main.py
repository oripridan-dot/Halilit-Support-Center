#!/usr/bin/env python3
"""
CONDUCTOR MAIN — JIT Architecture CLI

Lightweight orchestrator for the Halilit Support Center:
  skeleton-sync       Fetch basic inventory from Halilit.com (no AI needed)
  commercial-ingest   Full Halilit commercial ingestion (Golden List: sitemap + optional page scrape)
  enrich              Enrich catalog from Halilit product pages (description, images, features)
  ingest-all          Full pipeline: commercial-ingest → enrich → sync → catalog+graph
                      (Relationships: official → commercial → contextual → spectrum)
  sync                Sync data to frontend
  catalog             Show catalog statistics
  dev                 Start dev environment (backend + frontend)
  server              Start API server only

Usage:
    python3 backend/conductor_main.py skeleton-sync          # Fetch all brands
    python3 backend/conductor_main.py skeleton-sync "Roland"  # Fetch one brand
    python3 backend/conductor_main.py commercial-ingest      # Full Golden List (all brands)
    python3 backend/conductor_main.py commercial-ingest "Roland"  # One brand
    python3 backend/conductor_main.py sync                    # Rebuild frontend data
    python3 backend/conductor_main.py catalog                 # Show stats
    python3 backend/conductor_main.py dev                     # Start dev
"""

import sys
import os
import argparse
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict
import subprocess
from concurrent.futures import ThreadPoolExecutor

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger("Conductor")


class ConductorCLI:
    """Lightweight CLI for the JIT architecture."""

    def __init__(self):
        from backend.project_config import DATA_DIR, FRONTEND_DIR, CONFIG_DIR
        self.data_dir = DATA_DIR
        self.frontend_dir = FRONTEND_DIR
        self.config_dir = CONFIG_DIR

    def get_all_brands(self) -> List[str]:
        """Get all available brands from public/data/ (excludes metadata files)."""
        data_dir = self.frontend_dir / "public" / "data"
        if not data_dir.exists():
            return []

        exclude = {"index", "search_index", "search_index_min", "galaxy_db", "sample", "inventory"}
        brands = []
        for f in data_dir.glob("*.json"):
            if f.stem not in exclude:
                brands.append(f.stem)
        return sorted(brands)

    def skeleton_sync(self, brand: Optional[str] = None) -> bool:
        """
        Run the lightweight skeleton sync — fetches basic inventory from Halilit.com.
        No AI agents needed. Just scrapes listing pages for name, price, URL, thumbnail.
        """
        try:
            from backend.skeleton_sync import run_skeleton_sync
            return run_skeleton_sync(brand)
        except ImportError:
            logger.error("skeleton_sync.py not found. Run Phase 2 of the JIT plan first.")
            return False
        except Exception as e:
            logger.error(f"Skeleton sync failed: {e}")
            return False

    def commercial_ingest(
        self,
        brand: Optional[str] = None,
        try_scrape: bool = False,
        resume: bool = False,
        workers: int = 1,
    ) -> bool:
        """
        Run full Halilit commercial ingestion (Golden List) per source rules.
        Use workers > 1 to process multiple brands in parallel.
        """
        try:
            cmd = [sys.executable, str(PROJECT_ROOT / "backend" / "scripts" / "full_rescrape.py")]
            if brand:
                cmd.extend(["--brand", brand])
            if try_scrape:
                cmd.append("--try-scrape")
            if resume:
                cmd.append("--resume")
            if workers > 1:
                cmd.extend(["--workers", str(workers)])
            logger.info("Running commercial ingestion (Golden List builder)...")
            env = os.environ.copy()
            env["PYTHONPATH"] = str(PROJECT_ROOT)
            result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), env=env)
            if result.returncode == 0:
                self._rebuild_index_after_commercial_ingest()
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Commercial ingest failed: {e}")
            return False

    def _rebuild_index_after_commercial_ingest(self) -> None:
        """Rebuild index.json and search artifacts from frontend/public/data brand JSONs."""
        from backend.unified_data_service import get_ingest_to_frontend_engine
        engine = get_ingest_to_frontend_engine()
        all_products = []
        for b in self.get_all_brands():
            data_file = self.frontend_dir / "public" / "data" / f"{b}.json"
            if data_file.exists():
                try:
                    with open(data_file) as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            all_products.extend(data)
                except Exception as e:
                    logger.warning(f"  Skip {b}: {e}")
        if all_products:
            engine.generate_smart_artifacts(all_products)
            engine.generate_index_metadata(all_products)
            logger.info(f"Rebuilt index and search for {len(all_products)} products")

    def enrich(
        self,
        brand: Optional[str] = None,
        delay: float = 0.5,
        merge_dupes: bool = False,
        workers: int = 1,
        concurrent_products: int = 50,
    ) -> bool:
        """
        Enrich catalog from Halilit product pages (description, images, features, FAQ).
        Use concurrent_products for parallel pages within each file (default: 50 for fast async scraping).
        """
        try:
            cmd = [sys.executable, str(PROJECT_ROOT / "backend" / "scripts" / "enrich_catalog.py")]
            if brand:
                cmd.extend(["--brand", brand])
            if merge_dupes:
                cmd.append("--merge-dupes")
            # enrich_catalog.py uses --concurrency (default: 50)
            cmd.extend(["--concurrency", str(concurrent_products)])
            env = os.environ.copy()
            env["PYTHONPATH"] = str(PROJECT_ROOT)
            logger.info("Running catalog enrichment (Halilit page detail)...")
            result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), env=env)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Enrich failed: {e}")
            return False

    def ingest_all(
        self,
        try_scrape: bool = False,
        workers: int = 1,
        concurrent_products: int = 1,
        with_review_agent: bool = False,
    ) -> bool:
        """
        Run full ingestion pipeline in order:
        1. Commercial ingest (Golden List: sitemap + optional page scrape, prices, SKUs)
        2. Enrich (Halilit product pages: description, images, features, media)
        3. Sync (rebuild catalog + product graph with relationships in priority order)
        Use workers > 1 to run commercial and enrich with multiple parallel instances.
        Use with_review_agent=True to validate each phase and retry/improve on the fly.
        """
        if with_review_agent:
            return self._ingest_all_with_review(
                try_scrape=try_scrape, workers=workers, concurrent_products=concurrent_products
            )

        logger.info("=== Running full ingestion (commercial → enrich → sync) ===")
        if not self.commercial_ingest(brand=None, try_scrape=try_scrape, resume=False, workers=workers):
            logger.error("Commercial ingest failed; stopping.")
            return False
        if not self.enrich(brand=None, delay=0.5, workers=workers, concurrent_products=concurrent_products):
            logger.warning("Enrich had errors; check log.")
        if not self.sync_to_frontend(brand=None):
            logger.warning("Sync had errors; catalog/graph may be incomplete.")
        self._rebuild_catalog_and_graph()
        self._prebuild_catalog_cache()
        # Populate hierarchy DB (for /api/hierarchy/items display)
        try:
            if self.populate_hierarchy():
                logger.info("Hierarchy DB populated.")
            else:
                logger.warning("Hierarchy populate skipped or failed (DB may be unavailable).")
        except Exception:
            logger.warning("Hierarchy populate skipped (run manually: populate-hierarchy).")
        logger.info("=== Full ingestion complete (products, media, relationships) ===")
        return True

    def _ingest_all_with_review(
        self, try_scrape: bool = False, workers: int = 1, concurrent_products: int = 1
    ) -> bool:
        """Run full pipeline with Pipeline Review Agent: validate each phase, retry on failure, suggest improvements."""
        try:
            from backend.ingestion.pipeline_review_agent import PipelineReviewAgent
        except ImportError as e:
            logger.error(f"Pipeline review agent not available: {e}")
            return self.ingest_all(
                try_scrape=try_scrape, workers=workers,
                concurrent_products=concurrent_products, with_review_agent=False,
            )

        frontend_data = self.frontend_dir / "public" / "data"
        agent = PipelineReviewAgent(frontend_data_dir=frontend_data)

        def run_commercial() -> bool:
            return self.commercial_ingest(brand=None, try_scrape=try_scrape, resume=False, workers=workers)

        def run_enrich() -> bool:
            return self.enrich(brand=None, delay=0.5, workers=workers, concurrent_products=concurrent_products)

        def run_sync() -> bool:
            return self.sync_to_frontend(brand=None)

        logger.info("=== Running full ingestion WITH REVIEW AGENT (validate + retry + improve) ===")
        success = agent.run_with_review(
            run_commercial=run_commercial,
            run_enrich=run_enrich,
            run_sync=run_sync,
            run_rebuild_catalog=self._rebuild_catalog_and_graph,
        )
        for d in agent.get_decisions():
            logger.info(f"  [Review] {d['phase']}: {d['action']} — {d['reason']}")
        if success:
            logger.info("=== Full ingestion complete (review agent passed all phases) ===")
        else:
            logger.error("=== Full ingestion stopped (review agent reported failure) ===")
        return success

    def _rebuild_catalog_and_graph(self) -> None:
        """Build catalog and product graph (official → commercial → contextual → spectrum), persist graph snapshot."""
        try:
            from backend.product_normalizer import build_catalog
            data_dir = str(self.frontend_dir / "public" / "data")
            build_catalog(data_dir, resolve=False)
            logger.info("Catalog and relationship graph rebuilt and persisted.")
        except Exception as e:
            logger.warning(f"Catalog/graph rebuild failed (non-fatal): {e}")

    def _prebuild_catalog_cache(self) -> None:
        """Write catalog_cache.json.gz so first browser load is instant."""
        try:
            result = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "backend" / "scripts" / "prebuild_catalog_cache.py")],
                cwd=str(PROJECT_ROOT),
                env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT)},
                capture_output=True,
                text=True,
                timeout=180,
            )
            if result.returncode == 0:
                logger.info("Catalog cache prebuilt for fast first load.")
            else:
                logger.warning(f"Catalog prebuild failed (non-fatal): {result.stderr or result.stdout}")
        except Exception as e:
            logger.warning(f"Catalog prebuild skipped: {e}")

    def purge_weak_graph(self) -> bool:
        """Remove weak relationships from persisted graph snapshot (keep strict tiers only)."""
        try:
            from backend.scripts.purge_weak_graph_relationships import main as purge_main
            return purge_main() == 0
        except Exception as e:
            logger.error(f"Purge graph failed: {e}")
            return False

    def populate_hierarchy(self) -> bool:
        """Populate hierarchy DB tables from frontend product JSONs (after ingest + rebuild-catalog)."""
        try:
            import subprocess
            cmd = [sys.executable, str(PROJECT_ROOT / "populate-hierarchy.py")]
            env = os.environ.copy()
            env["PYTHONPATH"] = str(PROJECT_ROOT)
            result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), env=env)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Populate hierarchy failed: {e}")
            return False

    def sync_to_frontend(self, brand: Optional[str] = None) -> bool:
        """Rebuild frontend catalog from existing data files."""
        from backend.unified_data_service import get_ingest_to_frontend_engine

        if brand:
            brands = [brand]
        else:
            brands = self.get_all_brands()

        if not brands:
            logger.info("No brands to sync. Run skeleton-sync first.")
            return False

        logger.info(f"Syncing {len(brands)} brand(s) to frontend...")

        engine = get_ingest_to_frontend_engine()
        success_count = 0
        for b in brands:
            try:
                success, products = engine.sync_brand_to_frontend(b)
                if success:
                    logger.info(f"  {b}: {len(products)} products synced")
                    success_count += 1
            except Exception as e:
                logger.error(f"  {b}: Sync failed — {e}")

        if success_count > 0:
            self._rebuild_search_index(engine)

        logger.info(f"Sync complete: {success_count}/{len(brands)} brands")
        return success_count > 0

    def _rebuild_search_index(self, engine) -> None:
        """Rebuild global search index and index.json metadata."""
        logger.info("Rebuilding search index...")
        try:
            all_products = []
            for b in self.get_all_brands():
                data_file = self.frontend_dir / "public" / "data" / f"{b}.json"
                if data_file.exists():
                    with open(data_file) as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            all_products.extend(data)
                        elif isinstance(data, dict) and "products" in data:
                            all_products.extend(data["products"])
            if all_products:
                engine.generate_smart_artifacts(all_products)
                engine.generate_index_metadata(all_products)
                logger.info(f"  {len(all_products)} products indexed")
        except Exception as e:
            logger.error(f"Search index rebuild failed: {e}")

    def show_catalog(self) -> bool:
        """Display catalog statistics.

        Uses _normalize_brand_name (canonical map) as primary grouping key,
        then merges remaining groups where one brand name is a prefix of another,
        so the unique brand count reflects actual Halilit partner brands (~84).
        """
        from backend.product_normalizer import _normalize_brand_name

        brands = self.get_all_brands()
        logger.info(f"\nCATALOG STATISTICS")
        logger.info("=" * 50)
        logger.info(f"Raw Brand Files: {len(brands)}")

        # First pass: Group by canonical display name (uses _BRAND_CANONICAL_NAMES)
        # This merges hyphen/space variants, sub-brands (e.g. "akai" + "akai professional")
        brand_groups: Dict[str, List[str]] = {}
        brand_product_counts: Dict[str, int] = {}

        for b in brands:
            data_file = self.frontend_dir / "public" / "data" / f"{b}.json"
            if data_file.exists():
                try:
                    with open(data_file) as f:
                        data = json.load(f)
                        count = len(data) if isinstance(data, list) else len(data.get("products", []))
                    canonical = _normalize_brand_name(b)
                    if canonical not in brand_groups:
                        brand_groups[canonical] = []
                        brand_product_counts[canonical] = 0
                    brand_groups[canonical].append(b)
                    brand_product_counts[canonical] += count
                except Exception as e:
                    logger.warning(f"  {b}: Error ({e})")

        # Second pass: Merge groups where one canonical name is a prefix of another
        # (handles brands not in canonical map, e.g. "halilit" + "halilit-expo")
        def _norm_for_prefix(s: str) -> str:
            return s.lower().strip().replace("-", " ").replace("&", "and")

        merged_groups: Dict[str, List[str]] = {}
        merged_counts: Dict[str, int] = {}
        processed = set()

        for canonical in sorted(brand_groups.keys()):
            if canonical in processed:
                continue
            variants = brand_groups[canonical].copy()
            product_count = brand_product_counts[canonical]
            canon_norm = _norm_for_prefix(canonical)

            for other_canonical, other_variants in brand_groups.items():
                if other_canonical == canonical or other_canonical in processed:
                    continue
                other_norm = _norm_for_prefix(other_canonical)
                if len(canon_norm) >= 3 and len(other_norm) >= 3:
                    if canon_norm.startswith(other_norm) or other_norm.startswith(canon_norm):
                        variants.extend(other_variants)
                        product_count += brand_product_counts[other_canonical]
                        processed.add(other_canonical)

            merged_groups[canonical] = variants
            merged_counts[canonical] = product_count
            processed.add(canonical)

        unique_brands = len(merged_groups)
        partner_brands = unique_brands if "Other" not in merged_groups else unique_brands - 1
        logger.info(f"Unique Brands (deduplicated): {unique_brands}")
        if "Other" in merged_groups:
            logger.info(f"Partner Brands (excl. Other): {partner_brands}")
        logger.info("")

        total_products = 0
        for canonical in sorted(merged_groups.keys()):
            variants = merged_groups[canonical]
            product_count = merged_counts[canonical]
            total_products += product_count
            display = ", ".join(sorted(set(variants))) if len(variants) > 1 else ""
            if display:
                logger.info(f"  {canonical}: {product_count} products (variants: {display})")
            else:
                logger.info(f"  {canonical}: {product_count} products")

        # Check inventory.json
        inv_file = self.frontend_dir / "public" / "data" / "inventory.json"
        if inv_file.exists():
            try:
                with open(inv_file) as f:
                    inv = json.load(f)
                    inv_count = inv.get("total_products", 0)
                    logger.info(f"\nSkeleton Inventory: {inv_count} products")
                    logger.info(f"Last Sync: {inv.get('last_sync', 'unknown')}")
            except Exception:
                pass

        logger.info(f"\nTotal Products in Frontend: {total_products}")
        logger.info("=" * 50)
        return True

    def start_dev_server(self) -> bool:
        """Start dev environment (backend + frontend)."""
        logger.info("Starting development environment...")

        def run_backend():
            subprocess.run([sys.executable, str(PROJECT_ROOT / "backend" / "server.py")])

        def run_frontend():
            subprocess.run(["npm", "run", "dev"], cwd=str(self.frontend_dir))

        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(run_backend)
            executor.submit(run_frontend)
            logger.info("Dev environment running")
            logger.info("  Frontend: http://localhost:5173")
            logger.info("  Backend:  http://localhost:8000")
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                logger.info("Shutting down...")

    def start_api_server(self) -> bool:
        """Start API server only."""
        logger.info("Starting API server...")
        subprocess.run([sys.executable, str(PROJECT_ROOT / "backend" / "server.py")])
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Conductor CLI — Halilit JIT Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s skeleton-sync              # Fetch all brands from Halilit.com
  %(prog)s skeleton-sync "Roland"     # Fetch one brand
  %(prog)s commercial-ingest         # Full Golden List (all brands, sitemap)
  %(prog)s commercial-ingest "Roland" --try-scrape   # One brand, attempt page scrape
  %(prog)s enrich                     # Enrich all brands from Halilit pages
  %(prog)s enrich "Roland" --delay 0.3   # Enrich one brand, faster delay
  %(prog)s ingest-all                 # Commercial + enrich (all planned batch ingestions)
  %(prog)s sync                       # Rebuild frontend data
  %(prog)s catalog                    # Show statistics
  %(prog)s dev                        # Start dev environment
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # skeleton-sync
    ss = subparsers.add_parser("skeleton-sync", help="Fetch inventory from Halilit.com")
    ss.add_argument("brand", nargs="?", help="Brand name (optional)")

    # commercial-ingest
    ci = subparsers.add_parser("commercial-ingest", help="Full Halilit Golden List (sitemap + optional page scrape)")
    ci.add_argument("brand", nargs="?", help="Brand name (optional)")
    ci.add_argument("--try-scrape", action="store_true", help="Attempt to scrape product pages for prices/details")
    ci.add_argument("--resume", action="store_true", help="Resume from last progress")

    # enrich
    en = subparsers.add_parser("enrich", help="Enrich catalog from Halilit product pages (description, images, features)")
    en.add_argument("brand", nargs="?", help="Brand name (optional)")
    en.add_argument("--delay", type=float, default=0.5, help="Delay between HTTP requests (seconds)")
    en.add_argument("--merge-dupes", action="store_true", help="Merge duplicate brand files first")
    en.add_argument("--workers", type=int, default=1, help="Process brand files in parallel")
    en.add_argument("--concurrent-products", type=int, default=4, help="Scrape N product pages at once per brand (default 4)")

    # ingest-all
    ia = subparsers.add_parser("ingest-all", help="Run all planned ingestions: commercial-ingest then enrich")
    ia.add_argument("--try-scrape", action="store_true", help="Use page scrape during commercial ingest")
    ia.add_argument("--workers", type=int, default=1, help="Process multiple brands in parallel (commercial + enrich)")
    ia.add_argument("--concurrent-products", type=int, default=4, help="Scrape N product pages at once per brand file during enrich (default 4)")
    ia.add_argument("--with-review-agent", action="store_true", help="Validate each phase, retry on failure, suggest improvements")

    # sync
    sync_p = subparsers.add_parser("sync", help="Rebuild frontend data from existing files")
    sync_p.add_argument("brand", nargs="?", help="Brand name (optional)")

    # rebuild-catalog
    subparsers.add_parser("rebuild-catalog", help="Rebuild catalog and product graph (official → commercial → contextual → spectrum), persist graph snapshot")

    # purge-graph
    subparsers.add_parser("purge-graph", help="Remove weak relationships from persisted graph (keep variant_of, accessory_for, alternative_to only)")

    # populate-hierarchy
    subparsers.add_parser("populate-hierarchy", help="Populate hierarchy DB tables from frontend JSONs (run after ingest-all)")

    # catalog
    subparsers.add_parser("catalog", help="Show catalog statistics")

    # dev
    subparsers.add_parser("dev", help="Start dev environment")

    # server
    subparsers.add_parser("server", help="Start API server")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    conductor = ConductorCLI()

    try:
        if args.command == "skeleton-sync":
            success = conductor.skeleton_sync(getattr(args, "brand", None))
        elif args.command == "commercial-ingest":
            success = conductor.commercial_ingest(
                getattr(args, "brand", None),
                try_scrape=getattr(args, "try_scrape", False),
                resume=getattr(args, "resume", False),
            )
        elif args.command == "enrich":
            success = conductor.enrich(
                getattr(args, "brand", None),
                delay=getattr(args, "delay", 0.5),
                merge_dupes=getattr(args, "merge_dupes", False),
                workers=getattr(args, "workers", 1),
                concurrent_products=getattr(args, "concurrent_products", 4),
            )
        elif args.command == "ingest-all":
            success = conductor.ingest_all(
                try_scrape=getattr(args, "try_scrape", False),
                workers=getattr(args, "workers", 1),
                concurrent_products=getattr(args, "concurrent_products", 4),
                with_review_agent=getattr(args, "with_review_agent", False),
            )
        elif args.command == "sync":
            success = conductor.sync_to_frontend(getattr(args, "brand", None))
        elif args.command == "rebuild-catalog":
            conductor._rebuild_catalog_and_graph()
            success = True
        elif args.command == "purge-graph":
            success = conductor.purge_weak_graph()
        elif args.command == "populate-hierarchy":
            success = conductor.populate_hierarchy()
        elif args.command == "catalog":
            success = conductor.show_catalog()
        elif args.command == "dev":
            success = conductor.start_dev_server()
        elif args.command == "server":
            success = conductor.start_api_server()
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1

        return 0 if success else 1

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
