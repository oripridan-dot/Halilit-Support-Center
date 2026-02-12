#!/usr/bin/env python3
"""
CONDUCTOR MAIN - Central Hub for Halilit Support Center v8.4

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
from backend.unified_data_service import IngestToFrontendSyncEngine, get_ingest_to_frontend_engine
from backend.ingestion.orchestrator import IngestionOrchestrator
from backend.unified_agent_orchestrator import CommercialAgent
from backend.unified_quality_gates import feedback_engine, FeedbackType, audit_logger, AuditCategory, AuditLevel

from backend.ingestion.visual_validator import visual_validator
from backend.ingestion.match_learning import MatchLearningSystem
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
        self.config_dir = Path(
            "/workspaces/Halilit-Support-Center/backend/config")

        # Initialize Learning System
        self.match_learner = MatchLearningSystem(self.data_dir)

        # Load Brand Tiers
        self.brand_tiers = self._load_tiers()

    def _load_tiers(self) -> Dict[str, List[str]]:
        try:
            tier_file = self.config_dir / "brand_tiers.json"
            if tier_file.exists():
                with open(tier_file) as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load brand tiers: {e}")
        return {}

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

    def ingest_brand(self, brand: Optional[str], tier: Optional[str] = None, force: bool = False) -> bool:
        """
        Run ingestion pipeline for a brand.
        If brand is None, ingest all brands (filtered by tier if provided).
        """
        if brand:
            brands = [brand]
        else:
            if tier:
                tier_key = f"tier_{tier}"
                brands = self.brand_tiers.get(tier_key, [])
                logger.info(f"🎯 Ingesting Tier {tier}: {len(brands)} brands")
                if not brands:
                    logger.warning(f"No brands found for Tier {tier}")
                    return False
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
                raw_products = self._load_brand_source_data(b, force=force)
                if not raw_products:
                    logger.warning(f"⚠️  No data found for {b}")
                    continue

                # --- VISUAL VALIDATION PRE-FLIGHT ---
                # v7.6: Check if candidates exist and validate them
                validated_products = []
                for p in raw_products:
                    if 'candidates' in p and isinstance(p['candidates'], list) and p['candidates']:
                        logger.info(
                            f"🔎 Running Visual Validator for {p.get('product_name')}")
                        match = process_candidates(
                            p, p['candidates'], self.match_learner)
                        if match:
                            p['verified_match'] = match
                            validated_products.append(p)
                        else:
                            # Keep product but mark as unverified? Or skip?
                            # For safety, we keep it but log warning
                            logger.warning(
                                f"   No visual match confirmed for {p.get('product_name')}")
                            validated_products.append(p)
                    else:
                        validated_products.append(p)

                raw_products = validated_products
                # ------------------------------------

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
                            version_id=report.batch_id,
                            batch_id=report.batch_id,
                            product_count=report.total_products_processed,
                            products_approved=report.approved_count,
                            products_validated=report.approved_count + report.rejected_count,
                            completeness_score=avg_completeness,
                            compliance_score=avg_quality,
                            notes=f"Recommendations: {'; '.join(report.recommendations)}",
                            source="automatic_ingestion"
                        )
                        # NOTE: IngestionVersion definition has:
                        # brand: str
                        # version_id: str
                        # batch_id: str
                        # created_at: datetime
                        # phase: IngestionPhase
                        # product_count: int
                        # products_enriched: int
                        # products_validated: int
                        # products_approved: int

                        # Just in case, let's update checks since we don't have all args in definition

                        version.execution_time_seconds = report.execution_time_seconds
                        version.data_completeness = avg_completeness
                        version.quality_score = avg_quality
                        version.recommendations = report.recommendations

                        self.version_manager.update_version(version)
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

        # Rebuild global artifacts (Search Index, Shards)
        if success_count > 0:
            self._rebuild_global_artifacts(engine)

        return success_count > 0

    def _rebuild_global_artifacts(self, engine: Any) -> bool:
        """Rebuild global frontend artifacts (Search Index, Categories)."""
        logger.info("\n🌍 Rebuilding Global Artifacts (Index & Shards)...")
        try:
            # 1. Load ALL valid frontend data
            all_products = []
            frontend_brands = self.get_all_brands()

            for b in frontend_brands:
                data_file = self.frontend_dir / "public" / "data" / f"{b}.json"
                if data_file.exists():
                    try:
                        with open(data_file) as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                all_products.extend(data)
                    except Exception as e:
                        logger.warning(f"Skipping {b} in artifacts build: {e}")

            # 2. Generate artifacts
            if all_products:
                engine.generate_smart_artifacts(all_products)
                logger.info(
                    f"✅ Global build complete ({len(all_products)} products indexed)")
                return True
            else:
                logger.warning("⚠️  No products found for global build")
                return False

        except Exception as e:
            logger.error(f"❌ Global build failed: {e}")
            return False

    def full_build(self, brand: Optional[str] = None, tier: Optional[int] = None, force: bool = False) -> bool:
        """Run full build: ingest + sync."""
        logger.info("🏗️  FULL BUILD: ingest + sync")
        logger.info("=" * 60)

        # Phase 1: Ingest
        ingest_success = self.ingest_brand(brand, tier=tier, force=force)
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

        total_products = 0
        for b in brands:
            data_file = self.frontend_dir / "public" / "data" / f"{b}.json"
            if data_file.exists():
                try:
                    with open(data_file) as f:
                        data = json.load(f)
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

    def _load_brand_source_data(self, brand: str, force: bool = False) -> List[Dict[str, Any]]:
        """Load raw product data for a brand."""
        if not force:
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

        # Last resort: Fresh Scrape via CommercialScout
        if force:
            logger.info(
                f"   ⚡ FORCE ENABLED: Skipping local files. Launching CommercialScout for {brand}...")
        else:
            logger.info(
                f"   🔎 No local data found for {brand}. Launching CommercialScout...")
        try:
            # Use CommercialAgent (Scout) directly - already imported from unified_agent_orchestrator
            scout = CommercialAgent()
            raw_data = scout.harvest(brand)
            logger.info(
                f"   ✓ Scout harvested {len(raw_data) if raw_data else 0} items.")

            # Normalize to list
            if isinstance(raw_data, dict):
                return [raw_data]
            elif isinstance(raw_data, list):
                return raw_data

        except Exception as e:
            logger.error(f"   ❌ Scout failed: {e}")

        return []

    def _detect_brands_from_sources(self) -> List[str]:
        """
        Auto-detect available brands from ALL sources:
        1. Halilit.com brands page (authoritative — discovers ALL brands)
        2. Existing frontend JSON files (golden list already processed)
        3. Brand tiers config (configured brands)

        This ensures we capture every brand Halilit carries, not just
        the ones we've already processed.
        """
        brands = set()

        # Source 1: Discover ALL brands from Halilit.com (authoritative)
        try:
            from backend.ingestion.halilit_page_scraper import HalilitPageScraper
            scraper = HalilitPageScraper()
            halilit_brands = scraper.discover_all_brands()
            for b in halilit_brands:
                brands.add(b["name"].lower())
                logger.debug(f"   🌐 Halilit brand: {b['name']}")
            logger.info(
                f"🌐 Discovered {len(halilit_brands)} brands from Halilit.com")
        except Exception as e:
            logger.warning(
                f"⚠️ Failed to discover brands from Halilit.com: {e}")

        # Source 2: Existing frontend data (golden list already processed)
        data_dir = self.frontend_dir / "public" / "data"
        if data_dir.exists():
            metadata = {"index.json", "search_index.json",
                        "search_index_min.json"}
            for f in data_dir.glob("*.json"):
                if f.name not in metadata:
                    brands.add(f.stem.lower())
                    logger.debug(f"   📋 Golden list brand: {f.stem}")

        # Source 3: Brand tiers config
        for tier_key, tier_brands in self.brand_tiers.items():
            for b in tier_brands:
                brands.add(b.lower())

        logger.info(
            f"🔒 Total brands from all sources: {len(brands)}")
        return sorted(list(brands))


def process_candidates(
    halilit_product: Dict[str, Any],
    thomann_candidates: List[Dict[str, Any]],
    match_learner: Optional[MatchLearningSystem] = None
) -> Optional[Dict[str, Any]]:
    """
    Filters a list of potential matches using AI Visual Verification.
    Uses MatchLearningSystem to skip expensive AI checks if match is already known.
    """

    # 0. Check cache first
    # Use name as ID primarily as it's the stable identifier in this pipeline iteration
    product_id = halilit_product.get('name') or halilit_product.get('id')
    if match_learner and product_id:
        cached = match_learner.get_match(str(product_id))
        if cached:
            print(
                f"      🧠 Using LEARNED MATCH for {halilit_product.get('name')} (Conf: {cached.get('confidence', 0)*100:.1f}%)")
            return cached.get('candidate')

    best_match = None
    highest_confidence = 0.0

    print(
        f"🔍 Validating {len(thomann_candidates)} candidates for: {halilit_product.get('name', 'Unknown')}")

    for candidate in thomann_candidates:
        # 1. Commercial Pre-Check (Fast Fail)
        # If price difference is > 300% or < 10%, it's likely wrong (e.g. cable vs mixer)
        # (Optional logic to save API tokens)

        # 2. AI Visual Check
        verification = visual_validator.verify_match(
            reference={
                "name": halilit_product.get('name'),
                "brand": halilit_product.get('brand'),
                "image_url": halilit_product.get('image_url'),
                "description": halilit_product.get('description')
            },
            candidate={
                "name": candidate.get('name'),
                "image_url": candidate.get('image_url'),
                "price": candidate.get('price')
            }
        )

        if verification.is_match:
            print(
                f"   ✅ MATCH FOUND: {candidate.get('name')} ({verification.confidence*100:.1f}%)")
            print(f"      Reason: {verification.reason}")

            if verification.confidence > highest_confidence:
                highest_confidence = verification.confidence
                best_match = candidate
                best_match['ai_verification'] = verification.dict()
        else:
            print(
                f"   ❌ REJECTED: {candidate.get('name', 'Unknown')} - {verification.reason}")

    # Register the best successful match
    if best_match and match_learner and product_id:
        match_learner.register_match(
            str(product_id),
            best_match,
            highest_confidence
        )

    return best_match


def main():
    parser = argparse.ArgumentParser(
        description="Conductor CLI - Halilit Support Center v8.2",
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
    ingest_parser.add_argument(
        "--tier", type=int, choices=[1, 2, 3], help="Ingest only brands in specific tier")
    ingest_parser.add_argument(
        "--force", action="store_true", help="Force fresh scrape (ignore local data)")

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
    build_parser.add_argument(
        "--tier", type=int, choices=[1, 2, 3], help="Build only brands in specific tier")
    build_parser.add_argument(
        "--force", action="store_true", help="Force fresh scrape (ignore local data)")

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
            success = conductor.ingest_brand(
                args.brand, tier=args.tier, force=args.force)
        elif args.command == "test":
            success = conductor.test_brand(args.brand)
        elif args.command == "sync":
            success = conductor.sync_to_frontend(args.brand)
        elif args.command == "build":
            success = conductor.full_build(
                args.brand, tier=args.tier, force=args.force)
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
