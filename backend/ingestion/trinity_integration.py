"""
Trinity-Ingestion Integration - Connects Trinity Swarm with Orchestrator Pipeline

Bridges the Trinity Swarm agents (CommercialScout, OfficialVerifier, ExternalValidator)
with the unified ingestion orchestrator pipeline.

Data Flow:
  Trinity Agents (harvest, enrich, audit) → Raw Product Data
                                          ↓
                              IngestionOrchestrator
                        (6-phase pipeline processing)
                                          ↓
                              SpectrumAdapter
                          (convert to display format)
                                          ↓
                            IngestionDatabase
                        (persistent storage & analytics)
                                          ↓
                          Spectrum Display System
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json

from backend.agents.trinity_swarm import TrinitySwarm
from backend.ingestion import (
    get_ingestion_orchestrator,
    get_spectrum_adapter,
    get_ingestion_database,
    IngestionProductDraft,
    IngestionReport,
)

logger = logging.getLogger("TrinityIngestionIntegration")


class TrinityIngestionBridge:
    """
    Bridges Trinity Swarm with Ingestion Pipeline

    Orchestrates the complete flow:
    1. Trinity Swarm harvests raw product data
    2. Ingestion Orchestrator processes through 6-phase pipeline
    3. SpectrumAdapter converts to display format
    4. IngestionDatabase persists results
    """

    def __init__(self):
        self.swarm = TrinitySwarm()
        self.orchestrator = get_ingestion_orchestrator()
        self.spectrum_adapter = get_spectrum_adapter()
        self.database = get_ingestion_database()
        logger.info("✅ TrinityIngestionBridge initialized")

    def process_brand_pipeline(
        self, brand: str, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Complete pipeline: Trinity Swarm → Orchestrator → Spectrum → Database

        Args:
            brand: Brand name to process (e.g., "Nord", "Moog")
            force_refresh: Force re-processing even if cached

        Returns:
            Dict with complete processing results
        """
        logger.info(f"🚀 Starting pipeline for brand: {brand}")

        result = {
            "brand": brand,
            "timestamp": datetime.utcnow().isoformat(),
            "trinity_harvest": None,
            "orchestrator_report": None,
            "spectrum_payload": None,
            "quality_report": None,
            "database_paths": {},
            "metrics": {},
            "success": False,
            "errors": [],
        }

        try:
            # STEP 1: Trinity Swarm - Harvest raw data
            logger.info(f"Step 1/5: Trinity Swarm harvesting for {brand}...")
            raw_products = self._harvest_with_trinity(brand)

            # STEP 1.5: Trinity Swarm - Enrich with Official Data
            if raw_products:
                logger.info(
                    f"Step 1.5/5: Trinity Swarm enriching {len(raw_products)} products...")
                enriched_raw = []
                for p in raw_products:
                    try:
                        # OfficialVerifier enriches in-place or returns updated dict
                        enriched = self.swarm.verifier.enrich(p)
                        enriched_raw.append(enriched)
                    except Exception as e:
                        logger.warning(
                            f"Failed to enrich {p.get('product_name', 'unknown')}: {e}")
                        enriched_raw.append(p)
                raw_products = enriched_raw

            result["trinity_harvest"] = {
                "total_harvested": len(raw_products),
                "products_sample": raw_products[:2] if raw_products else [],
            }
            logger.info(f"✅ Harvested & Enriched {len(raw_products)} products")

            if not raw_products:
                logger.warning(f"No products harvested for {brand}")
                result["errors"].append(f"No products harvested for {brand}")
                return result

            # STEP 2: Orchestrator - Process through 6-phase pipeline
            logger.info(f"Step 2/5: Processing through ingestion pipeline...")
            report = self.orchestrator.ingest_batch(
                brand, raw_products, force_refresh)
            result["orchestrator_report"] = {
                "batch_id": report.batch_id,
                "total_processed": report.total_products_processed,
                "approved_count": report.approved_count,
                "rejected_count": report.rejected_count,
                "execution_time": report.execution_time_seconds,
            }
            logger.info(
                f"✅ Processed {report.total_products_processed} products "
                f"({report.approved_count} approved, {report.rejected_count} rejected) "
                f"in {report.execution_time_seconds:.2f}s"
            )

            if report.approved_count == 0:
                logger.warning(f"No products approved for {brand}")
                result["errors"].append(f"No products approved for {brand}")
                return result

            # STEP 3: SpectrumAdapter - Convert to display format
            logger.info(f"Step 3/5: Converting to Spectrum format...")
            spectrum_payload, quality_report = self.spectrum_adapter.convert_ingestion_report(
                report
            )
            result["spectrum_payload"] = spectrum_payload.to_dict()
            result["quality_report"] = quality_report.to_dict()
            logger.info(f"✅ Converted to Spectrum format")

            # STEP 4: Generate display metrics
            logger.info(f"Step 4/5: Generating display metrics...")
            metrics = self.spectrum_adapter.generate_display_metrics(
                spectrum_payload)            # Inject pipeline metrics
            metrics["approved_count"] = report.approved_count
            metrics["rejected_count"] = report.rejected_count
            result["metrics"] = metrics
            logger.info(f"✅ Generated display metrics")

            # STEP 5: Database - Persist results
            logger.info(f"Step 5/5: Persisting to database...")
            db_paths = self._persist_results(
                brand, report, spectrum_payload, quality_report)
            result["database_paths"] = db_paths
            logger.info(f"✅ Persisted to database")

            result["success"] = True
            logger.info(
                f"🎉 Pipeline complete for {brand}: "
                f"{report.approved_count} approved products ready for display"
            )

        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
            result["errors"].append(str(e))

        return result

    def _harvest_with_trinity(self, brand: str) -> List[Dict[str, Any]]:
        """
        Use Trinity Swarm to harvest raw product data

        Returns:
            List of raw product dicts
        """
        try:
            # In real implementation, this would use CommercialScout.harvest()
            # For now, load from file if available
            raw_products = self._load_brand_from_file(brand)
            if raw_products:
                logger.info(
                    f"✅ Loaded {len(raw_products)} products from file for {brand}")
                return raw_products

            # Fallback to Trinity agent
            logger.info(f"Loading from Trinity Swarm for {brand}...")
            raw_data = self.swarm.scout.harvest(brand)
            return [raw_data] if raw_data else []

        except Exception as e:
            logger.error(f"Trinity harvest failed: {e}")
            return []

    def _load_brand_from_file(self, brand: str) -> List[Dict[str, Any]]:
        """
        Load products from backend/data/brands/{brand}/products.json

        Returns:
            List of product dicts
        """
        import os
        from pathlib import Path

        brand_file = (
            Path("/workspaces/Halilit-Support-Center/backend/data/brands")
            / brand
            / "products.json"
        )

        if not brand_file.exists():
            logger.warning(f"No product file for {brand} at {brand_file}")
            return []

        try:
            with open(brand_file, "r") as f:
                data = json.load(f)

            # Handle both list and dict formats
            if isinstance(data, list):
                products = data
            else:
                products = data.get("products", [])

            logger.info(f"Loaded {len(products)} products from {brand_file}")
            return products

        except Exception as e:
            logger.error(f"Error loading {brand_file}: {e}")
            return []

    def _persist_results(
        self,
        brand: str,
        report: IngestionReport,
        spectrum_payload,
        quality_report,
    ) -> Dict[str, str]:
        """
        Persist results to database

        Returns:
            Dict with paths to saved files
        """
        paths = {}

        # Save report
        report_path = self.database.save_report(report)
        paths["report"] = report_path

        # Save products
        product_paths = self.database.save_products(
            brand,
            report.approved_products,
            report.rejected_products if report.rejected_products else None,
        )
        paths.update(product_paths)

        # Save quality metrics
        quality_path = self.database.save_quality_snapshot(
            brand, quality_report.to_dict()
        )
        paths["quality"] = quality_path

        # Save Spectrum payload
        spectrum_file = (
            Path("/workspaces/Halilit-Support-Center/backend/data/ingestion/spectrum")
            / brand
            / f"spectrum_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        )
        spectrum_file.parent.mkdir(parents=True, exist_ok=True)
        with open(spectrum_file, "w") as f:
            # Convert datetime objects to ISO format strings for JSON serialization
            payload_dict = spectrum_payload.to_dict()
            json.dump(payload_dict, f, indent=2, default=str)
        paths["spectrum"] = str(spectrum_file)

        return paths

    def process_multiple_brands(
        self, brands: List[str], force_refresh: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """
        Process multiple brands in sequence

        Args:
            brands: List of brand names
            force_refresh: Force re-processing

        Returns:
            Dict mapping brand to its results
        """
        logger.info(f"🚀 Processing {len(brands)} brands...")
        results = {}

        for brand in brands:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing: {brand}")
            logger.info(f"{'='*60}")

            result = self.process_brand_pipeline(brand, force_refresh)
            results[brand] = result

        # Summary
        successful = sum(1 for r in results.values() if r["success"])
        logger.info(f"\n{'='*60}")
        logger.info(
            f"✅ Completed: {successful}/{len(brands)} brands successful")
        logger.info(f"{'='*60}")

        return results

    def get_brand_analytics(self, brand: str) -> Dict[str, Any]:
        """
        Get analytics for a brand

        Returns:
            Dict with analytics
        """
        return self.database.get_brand_history(brand)

    def get_all_analytics(self) -> Dict[str, Any]:
        """
        Get analytics for all brands

        Returns:
            Dict with all analytics
        """
        return self.database.export_analytics()

    def generate_report(self, brand: str) -> Optional[Dict[str, Any]]:
        """
        Get latest report for a brand

        Returns:
            Report dict or None if not found
        """
        return self.database.load_latest_report(brand)


# Singleton pattern
_bridge = None


def get_trinity_ingestion_bridge() -> TrinityIngestionBridge:
    """Get singleton TrinityIngestionBridge instance"""
    global _bridge
    if _bridge is None:
        _bridge = TrinityIngestionBridge()
    return _bridge
