#!/usr/bin/env python3
"""
CONDUCTOR MAIN - Central Hub for Halilit Support Center v7.3

The Conductor CLI orchestrates all operations:
- Data ingestion (Trinity Swarm)
- Frontend synchronization
- Quality validation
- Development server management

Usage:
    python3 backend/conductor_main.py ingest [brand]    # Run ingestion pipeline
    python3 backend/conductor_main.py test [brand]      # Test a brand
    python3 backend/conductor_main.py sync              # Sync to frontend
    python3 backend/conductor_main.py build             # Full build (ingest + sync)
    python3 backend/conductor_main.py dev               # Start dev environment
    python3 backend/conductor_main.py server            # Start API server
    python3 backend/conductor_main.py catalog           # Show catalog statistics
"""

from backend.ingestion_versioning import get_version_manager, IngestionVersion
from backend.ingestion.ingestion_database import get_ingestion_database
from backend.ingestion.trinity_integration import TrinityIngestionBridge
from backend.unified_data_service_v73 import IngestToFrontendSyncEngine, get_ingest_to_frontend_engine
from backend.ingestion.orchestrator import IngestionOrchestrator
from backend.unified_quality_gates_v73 import feedback_engine, FeedbackType, audit_logger, AuditCategory, AuditLevel
import sys
import os
import argparse
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger("Conductor")


class ConductorCLI:
    """Central orchestrator for all Halilit pipelines."""

    def __init__(self):
        self.orchestrator = IngestionOrchestrator()
        self.trinity_bridge = TrinityIngestionBridge()
        self.database = get_ingestion_database()
        self.version_manager = get_version_manager()
        self.data_dir = Path("/workspaces/Halilit-Support-Center/backend/data")
        self.frontend_dir = Path("/workspaces/Halilit-Support-Center/frontend")

    def get_all_brands(self) -> List[str]:
        """Get all available brands from public/data/."""
        data_dir = self.frontend_dir / "public" / "data"
        if not data_dir.exists():
            return []

        brands = []
        for f in data_dir.glob("*.json"):
            if f.name != "index.json":
                brands.append(f.stem)
        return sorted(brands)

    def ingest_brand(self, brand: Optional[str]) -> bool:
        """
        Run ingestion pipeline for a brand.
        If brand is None, ingest all brands.
        """
        if brand:
            brands = [brand]
        else:
            logger.info(
                "No brand specified, using Trinity to detect brands...")
            brands = self._detect_brands_from_sources()

        if not brands:
            logger.warning("No brands to ingest")
            return False

        logger.info(
            f"🎯 Starting ingestion for {len(brands)} brand(s): {', '.join(brands)}")

        success_count = 0
        for b in brands:
            try:
                logger.info(f"\n📦 Ingesting: {b}")

                # Load raw data from appropriate source
                raw_products = self._load_brand_source_data(b)
                if not raw_products:
                    logger.warning(f"⚠️  No data found for {b}")
                    continue

                # Run ingestion pipeline
                report = self.orchestrator.ingest_batch(b, raw_products)

                if report.approved_count > 0:
                    logger.info(
                        f"✅ {b}: {report.approved_count} products approved")

                    # Save ingestion results to database
                    try:
                        self.database.save_products(
                            b,
                            report.approved_products,
                            [p for p, _ in report.rejected_products] if report.rejected_products else [
                            ]
                        )
                        self.database.save_report(report)
                        logger.info(f"   💾 Saved to database")
                    except Exception as e:
                        logger.warning(
                            f"   ⚠️  Failed to save to database: {e}")

                    # Track version for versioning system
                    try:
                        avg_completeness = (
                            sum(p.data_completeness for p in report.approved_products)
                            / len(report.approved_products)
                            if report.approved_products else 0.0
                        )
                        avg_quality = (
                            sum(p.quality_score for p in report.approved_products)
                            / len(report.approved_products)
                            if report.approved_products else 0.0
                        )

                        version = IngestionVersion(
                            brand=b,
                            batch_id=report.batch_id,
                            approved_count=report.approved_count,
                            rejected_count=report.rejected_count,
                            total_processed=report.total_products_processed,
                            execution_time_seconds=report.execution_time_seconds,
                            data_completeness=avg_completeness,
                            quality_score=avg_quality,
                            recommendations=report.recommendations,
                        )
                        self.version_manager.save_version(version)
                        logger.info(
                            f"   📌 Version tracked: {version.version_id}")
                    except Exception as e:
                        logger.warning(f"   ⚠️  Failed to track version: {e}")

                    success_count += 1
                else:
                    logger.warning(
                        f"⚠️  {b}: 0 products approved ({report.rejected_count} rejected)")

            except Exception as e:
                logger.error(f"❌ Failed to ingest {b}: {e}")

        logger.info(
            f"\n✅ Ingestion complete: {success_count}/{len(brands)} brands")
        return success_count > 0

    def test_brand(self, brand: str) -> bool:
        """Test ingestion for a single brand without writing to frontend."""
        logger.info(f"🧪 Testing brand: {brand}")

        try:
            raw_products = self._load_brand_source_data(brand)
            if not raw_products:
                logger.error(f"No data found for {brand}")
                return False

            report = self.orchestrator.ingest_batch(brand, raw_products)

            logger.info(f"\n📊 Test Results:")
            logger.info(f"  Status: Completed")
            logger.info(
                f"  Products: {report.approved_count}/{len(raw_products)}")
            logger.info(f"  Approved: {report.approved_count}")
            logger.info(f"  Rejected: {report.rejected_count}")

            if report.recommendations:
                logger.info("\n💡 Recommendations:")
                for rec in report.recommendations[:5]:
                    logger.info(f"    - {rec}")

            return report.approved_count > 0

        except Exception as e:
            logger.error(f"Test failed: {e}")
            return False

    def sync_to_frontend(self, brand: Optional[str]) -> bool:
        """Sync ingested data to frontend."""
        if brand:
            brands = [brand]
        else:
            brands = self.get_all_brands()

        logger.info(f"🔄 Syncing {len(brands)} brand(s) to frontend...")

        success_count = 0
        engine = get_ingest_to_frontend_engine()
        for b in brands:
            try:
                success, products = engine.sync_brand_to_frontend(b)
                if success:
                    logger.info(f"✅ {b}: {len(products)} products synced")
                    success_count += 1
                else:
                    logger.warning(f"⚠️  {b}: Sync failed")
            except Exception as e:
                logger.error(f"❌ Sync failed for {b}: {e}")

        logger.info(f"✅ Sync complete: {success_count}/{len(brands)} brands")
        return success_count > 0

    def full_build(self, brand: Optional[str]) -> bool:
        """Run full build: ingest + sync."""
        logger.info("🏗️  FULL BUILD: ingest + sync")
        logger.info("=" * 60)

        # Phase 1: Ingest
        ingest_success = self.ingest_brand(brand)
        if not ingest_success:
            logger.error("❌ Ingestion failed")
            return False

        # Phase 2: Sync
        logger.info("\n" + "=" * 60)
        sync_success = self.sync_to_frontend(brand)

        logger.info("=" * 60)
        if sync_success:
            logger.info("✅ Build complete!")
        else:
            logger.warning("⚠️  Build partially complete (some syncs failed)")

        return True

    def show_catalog(self) -> bool:
        """Display catalog statistics."""
        brands = self.get_all_brands()
        logger.info(f"\n📊 CATALOG STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Total Brands: {len(brands)}")

    def show_agent_learning(self) -> bool:
        """Display agent learning progress and health."""
        logger.info(f"\n🧠 AGENT LEARNING & HEALTH REPORT")
        logger.info("=" * 60)

        health = feedback_engine.get_pipeline_health_report()

        logger.info(f"Timestamp: {health['timestamp']}")
        logger.info(f"Pipeline Accuracy: {health['pipeline_accuracy']}%")
        logger.info(f"Total Decisions: {health['total_decisions']}")
        logger.info(f"Total Feedback: {health['total_feedback_received']}")

        logger.info("\n📈 AGENT SUMMARIES:")
        for agent_name, summary in health['agents'].items():
            logger.info(f"\n  {agent_name}:")
            logger.info(f"    ✅ Decisions: {summary['total_decisions']}")
            logger.info(f"    📊 Accuracy: {summary['accuracy']}%")
            logger.info(f"    ✓ Approved: {summary['approved']}")
            logger.info(f"    ✗ Rejected: {summary['rejected']}")
            logger.info(f"    ⏳ Pending: {summary['pending_review']}")
            logger.info(f"    🎯 Confidence: {summary['confidence_score']}%")

            if summary['improvement_areas']:
                logger.info(f"    ⚠️  Improvement Areas:")
                for area in summary['improvement_areas']:
                    logger.info(f"       - {area}")

        if health['bottlenecks']:
            logger.info("\n⚠️  BOTTLENECKS:")
            for bottleneck in health['bottlenecks']:
                logger.info(f"  - {bottleneck}")

        if health['recommendations']:
            logger.info("\n💡 RECOMMENDATIONS:")
            for rec in health['recommendations'][:10]:
                logger.info(f"  - {rec}")

        return True

    def show_audit_trail(self, limit: int = 50) -> bool:
        """Display recent audit events."""
        logger.info(f"\n🔍 AUDIT TRAIL (Last {limit} events)")
        logger.info("=" * 60)

        trail = audit_logger.get_audit_trail(limit=limit)

        for event in trail:
            level_emoji = {
                "info": "ℹ️ ",
                "warning": "⚠️ ",
                "error": "❌",
                "critical": "🚨",
                "security": "🔒",
            }.get(event['level'], "•")

            logger.info(
                f"{level_emoji} [{event['category']}] {event['action']} "
                f"({event['status']}) - {event['execution_time_ms']:.2f}ms"
            )
            if event['agent']:
                logger.info(f"   Agent: {event['agent']}")

        return True

    def show_security_audit(self) -> bool:
        """Display security audit summary."""
        logger.info(f"\n🔒 SECURITY AUDIT REPORT")
        logger.info("=" * 60)

        audit = audit_logger.get_security_audit()

        logger.info(f"Timestamp: {audit['timestamp']}")
        logger.info(f"Total Security Events: {audit['total_security_events']}")
        logger.info(f"🚨 Critical: {audit['critical_events']}")
        logger.info(f"🔴 High Severity: {audit['high_severity_events']}")

        if audit['recent_events']:
            logger.info("\n📋 Recent Security Events:")
            for event in audit['recent_events'][:10]:
                logger.info(
                    f"  - [{event['category']}] {event['action']} ({event['status']})")

        return True

    def show_performance_metrics(self) -> bool:
        """Display agent performance metrics."""
        logger.info(f"\n⚡ PERFORMANCE METRICS")
        logger.info("=" * 60)

        perf = audit_logger.get_performance_report()

        logger.info(f"Report Time: {perf['timestamp']}")

        for agent_name, metrics in perf['by_agent'].items():
            logger.info(f"\n  {agent_name}:")
            logger.info(f"    Total Actions: {metrics['total_actions']}")
            logger.info(f"    ✓ Successful: {metrics['successful']}")
            logger.info(f"    ✗ Failed: {metrics['failed']}")
            logger.info(f"    Success Rate: {metrics['success_rate']}%")
            logger.info(
                f"    Avg Execution: {metrics['avg_execution_time_ms']:.2f}ms")
            logger.info(
                f"    Total Execution: {metrics['total_execution_time_ms']:.2f}ms")

        return True

        total_products = 0
        for b in brands:
            data_file = self.frontend_dir / "public" / "data" / f"{b}.json"
            if data_file.exists():
                try:
                    with open(data_file) as f:
                        data = json.load(f)
                        # Data can be either a list or dict
                        if isinstance(data, list):
                            count = len(data)
                        elif isinstance(data, dict):
                            count = len(data.get("products", []))
                        else:
                            count = 0
                        total_products += count
                        logger.info(f"  • {b}: {count} products")
                except Exception as e:
                    logger.warning(f"  • {b}: Error reading ({e})")

        logger.info(f"\nTotal Products: {total_products}")
        logger.info("=" * 60)
        return True

    def start_dev_server(self) -> bool:
        """Start dev environment (backend + frontend)."""
        logger.info("🚀 Starting development environment...")
        logger.info("=" * 60)

        # Start backend server in subprocess
        def run_backend():
            logger.info("▶️  Starting FastAPI backend...")
            subprocess.run([
                sys.executable,
                str(PROJECT_ROOT / "backend" / "server.py")
            ])

        def run_frontend():
            logger.info("▶️  Starting Vite frontend...")
            subprocess.run(
                ["npm", "run", "dev"],
                cwd=str(self.frontend_dir)
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(run_backend)
            executor.submit(run_frontend)
            logger.info("\n✅ Dev environment running on http://localhost:5173")
            logger.info("Backend API: http://localhost:8000")

            # Keep running
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                logger.info("\n⭐ Shutting down...")

    def start_api_server(self) -> bool:
        """Start API server only."""
        logger.info("🚀 Starting API server...")
        subprocess.run([
            sys.executable,
            str(PROJECT_ROOT / "backend" / "server.py")
        ])
        return True

    def _load_brand_source_data(self, brand: str) -> List[Dict[str, Any]]:
        """Load raw product data for a brand."""
        # Try exact match first
        data_file = self.frontend_dir / "public" / "data" / f"{brand}.json"
        if data_file.exists():
            try:
                with open(data_file) as f:
                    data = json.load(f)
                    # Data can be either a list (processed) or dict with "products" key
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict):
                        return data.get("products", [])
            except Exception as e:
                logger.warning(f"Failed to load {data_file}: {e}")

        # Try lowercase match
        data_file = self.frontend_dir / "public" / \
            "data" / f"{brand.lower()}.json"
        if data_file.exists():
            try:
                with open(data_file) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict):
                        return data.get("products", [])
            except Exception as e:
                logger.warning(f"Failed to load {data_file}: {e}")

        # Fallback to backend data
        ingestion_file = self.data_dir / "ingestion" / "products" / brand / "raw_*.json"
        try:
            import glob
            files = glob.glob(str(ingestion_file))
            if files:
                with open(files[0]) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict):
                        return data.get("products", [])
        except Exception as e:
            logger.warning(f"Failed to load ingestion data: {e}")

        return []

    def _detect_brands_from_sources(self) -> List[str]:
        """
        Auto-detect available brands ONLY from Halilit's golden list.
        Golden list is the ONLY source of truth: /frontend/public/data/*.json
        """
        brands = set()

        # From frontend/public/data/ - use exact filenames (GOLDEN LIST ONLY)
        data_dir = self.frontend_dir / "public" / "data"
        if data_dir.exists():
            # Metadata files to exclude
            metadata = {"index.json", "search_index.json",
                        "search_index_min.json"}

            for f in data_dir.glob("*.json"):
                if f.name not in metadata:
                    brands.add(f.stem)
                    logger.debug(f"   📋 Golden list brand: {f.stem}")

        logger.info(
            f"🔒 Locked to {len(brands)} golden list brands (source: /frontend/public/data/)")
        return sorted(list(brands))


def main():
    parser = argparse.ArgumentParser(
        description="Conductor CLI - Halilit Support Center v7.3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest all brands
  %(prog)s ingest
  
  # Ingest specific brand
  %(prog)s ingest "Adam Audio"
  
  # Full build (ingest + sync)
  %(prog)s build
  
  # Start dev environment
  %(prog)s dev
  
  # Show statistics
  %(prog)s catalog
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # ingest command
    ingest_parser = subparsers.add_parser(
        "ingest", help="Run ingestion pipeline")
    ingest_parser.add_argument(
        "brand", nargs="?", help="Brand name (optional, ingest all if not specified)")

    # test command
    test_parser = subparsers.add_parser("test", help="Test ingestion")
    test_parser.add_argument("brand", help="Brand name")

    # sync command
    sync_parser = subparsers.add_parser("sync", help="Sync to frontend")
    sync_parser.add_argument(
        "brand", nargs="?", help="Brand name (optional, sync all if not specified)")

    # build command
    build_parser = subparsers.add_parser(
        "build", help="Full build (ingest + sync)")
    build_parser.add_argument(
        "brand", nargs="?", help="Brand name (optional, build all if not specified)")

    # dev command
    dev_parser = subparsers.add_parser("dev", help="Start dev environment")

    # server command
    server_parser = subparsers.add_parser("server", help="Start API server")

    # catalog command
    catalog_parser = subparsers.add_parser(
        "catalog", help="Show catalog statistics")

    # learning command
    learning_parser = subparsers.add_parser(
        "learning", help="Show agent learning progress")

    # audit command
    audit_parser = subparsers.add_parser(
        "audit", help="Show audit trail")
    audit_parser.add_argument(
        "--limit", type=int, default=50, help="Number of events to show")

    # security command
    security_parser = subparsers.add_parser(
        "security", help="Show security audit report")

    # performance command
    performance_parser = subparsers.add_parser(
        "performance", help="Show performance metrics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    conductor = ConductorCLI()

    try:
        if args.command == "ingest":
            success = conductor.ingest_brand(args.brand)
        elif args.command == "test":
            success = conductor.test_brand(args.brand)
        elif args.command == "sync":
            success = conductor.sync_to_frontend(args.brand)
        elif args.command == "build":
            success = conductor.full_build(args.brand)
        elif args.command == "dev":
            success = conductor.start_dev_server()
        elif args.command == "server":
            success = conductor.start_api_server()
        elif args.command == "catalog":
            success = conductor.show_catalog()
        elif args.command == "learning":
            success = conductor.show_agent_learning()
        elif args.command == "audit":
            success = conductor.show_audit_trail(limit=args.limit)
        elif args.command == "security":
            success = conductor.show_security_audit()
        elif args.command == "performance":
            success = conductor.show_performance_metrics()
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1

        return 0 if success else 1

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
