#!/usr/bin/env python3
"""
CONDUCTOR MAIN — JIT Architecture CLI

Lightweight orchestrator for the Halilit Support Center:
  skeleton-sync    Fetch basic inventory from Halilit.com (no AI needed)
  sync             Sync data to frontend
  catalog          Show catalog statistics
  dev              Start dev environment (backend + frontend)
  server           Start API server only

Usage:
    python3 backend/conductor_main.py skeleton-sync          # Fetch all brands
    python3 backend/conductor_main.py skeleton-sync "Roland"  # Fetch one brand
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
from typing import List, Optional
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
        """Rebuild global search index."""
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
            if all_products:
                engine.generate_smart_artifacts(all_products)
                logger.info(f"  {len(all_products)} products indexed")
        except Exception as e:
            logger.error(f"Search index rebuild failed: {e}")

    def show_catalog(self) -> bool:
        """Display catalog statistics."""
        brands = self.get_all_brands()
        logger.info(f"\nCATALOG STATISTICS")
        logger.info("=" * 50)
        logger.info(f"Total Brands: {len(brands)}")

        total_products = 0
        for b in brands:
            data_file = self.frontend_dir / "public" / "data" / f"{b}.json"
            if data_file.exists():
                try:
                    with open(data_file) as f:
                        data = json.load(f)
                        count = len(data) if isinstance(data, list) else len(data.get("products", []))
                        total_products += count
                        logger.info(f"  {b}: {count} products")
                except Exception as e:
                    logger.warning(f"  {b}: Error ({e})")

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
  %(prog)s sync                       # Rebuild frontend data
  %(prog)s catalog                    # Show statistics
  %(prog)s dev                        # Start dev environment
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # skeleton-sync
    ss = subparsers.add_parser("skeleton-sync", help="Fetch inventory from Halilit.com")
    ss.add_argument("brand", nargs="?", help="Brand name (optional)")

    # sync
    sync_p = subparsers.add_parser("sync", help="Rebuild frontend data from existing files")
    sync_p.add_argument("brand", nargs="?", help="Brand name (optional)")

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
        elif args.command == "sync":
            success = conductor.sync_to_frontend(getattr(args, "brand", None))
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
