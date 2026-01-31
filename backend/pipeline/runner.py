"""
Pipeline Runner - Orchestrates the complete data pipeline.

Usage:
    python -m backend.pipeline run          # Full pipeline
    python -m backend.pipeline ingest       # Only harvest data
    python -m backend.pipeline process      # Only process (layers 1-3)
    python -m backend.pipeline deploy       # Only deploy to frontend
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from .config import config
from .models import (
    OfficialData,
    CommercialData,
    ContextualData,
    NormalizedProduct,
    EnrichedProduct,
    OptimizedProduct,
    CatalogIndex,
    BrandSummary,
    BrandCatalog,
    TierLevel,
)
from .harvesters import OfficialHarvester, CommercialHarvester, ContextualHarvester
from .layers import NormalizeLayer, EnrichLayer, OptimizeLayer

logger = logging.getLogger(__name__)


class PipelineRunner:
    """
    Main pipeline orchestrator.

    Coordinates the complete flow:
      Ingest (3 sources) → Normalize → Enrich → Optimize → Deploy
    """

    def __init__(self):
        # Ensure directories exist
        config.ensure_directories()

        # Initialize harvesters
        self.official_harvester = OfficialHarvester()
        self.commercial_harvester = CommercialHarvester()
        self.contextual_harvester = ContextualHarvester()

        # Initialize layers
        self.normalize_layer = NormalizeLayer()
        self.enrich_layer = EnrichLayer()
        self.optimize_layer = OptimizeLayer()

        # Brand registry (from manifest or discovery)
        self.brands: Dict[str, Dict[str, Any]] = {}

    def load_brands(self, manifest_path: Optional[Path] = None) -> None:
        """Load brand registry from manifest or existing data."""

        # Try manifest file
        if manifest_path and manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.brands = {b['id']: b for b in data.get('brands', [])}
                logger.info(f"Loaded {len(self.brands)} brands from manifest")
                return

        # Try default manifest
        default_manifest = config.BACKEND_DIR / "ingestion" / "manifest.json"
        if default_manifest.exists():
            with open(default_manifest, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.brands = {b['id']: b for b in data.get('brands', [])}
                logger.info(
                    f"Loaded {len(self.brands)} brands from default manifest")
                return

        # Discover from existing data
        for source_dir in [config.OFFICIAL_DIR, config.GOLDEN_DIR]:
            if source_dir.exists():
                for f in source_dir.glob("*.json"):
                    brand_id = f.stem.replace(
                        '-normalized', '').replace('-enriched', '')
                    if brand_id not in self.brands:
                        self.brands[brand_id] = {
                            "id": brand_id,
                            "name": brand_id.replace('-', ' ').title(),
                        }

        logger.info(f"Discovered {len(self.brands)} brands from existing data")

    async def run_full_pipeline(
        self,
        brand_ids: Optional[List[str]] = None,
        skip_ingest: bool = False,
        skip_process: bool = False,
        skip_deploy: bool = False,
    ) -> Dict[str, Any]:
        """
        Run the complete pipeline for specified brands.

        Args:
            brand_ids: Specific brands to process (None = all)
            skip_ingest: Skip data harvesting
            skip_process: Skip layer processing
            skip_deploy: Skip frontend deployment

        Returns:
            Pipeline report with stats and errors
        """
        start_time = datetime.utcnow()
        report = {
            "started_at": start_time.isoformat(),
            "brands_processed": 0,
            "products_total": 0,
            "errors": [],
        }

        logger.info("🚀 Starting Halilit Pipeline v5.0")

        # Load brand registry
        self.load_brands()

        # Filter brands
        if brand_ids:
            brands_to_process = {k: v for k,
                                 v in self.brands.items() if k in brand_ids}
        else:
            brands_to_process = self.brands

        if not brands_to_process:
            logger.warning("No brands to process")
            return report

        logger.info(f"Processing {len(brands_to_process)} brands")

        all_optimized: Dict[str, List[OptimizedProduct]] = {}

        for brand_id, brand_info in brands_to_process.items():
            try:
                logger.info(
                    f"\n{'='*60}\n📦 Processing: {brand_info.get('name', brand_id)}\n{'='*60}")

                # Step 1: Ingest
                official = []
                commercial = []
                contextual = []

                if not skip_ingest:
                    official, commercial, contextual = await self._ingest_brand(
                        brand_id, brand_info
                    )
                else:
                    # Load from cache
                    official = self.official_harvester.load_cached(
                        brand_id) or []
                    commercial = self.commercial_harvester.load_cached(
                        brand_id) or []
                    contextual = self.contextual_harvester.load_cached(
                        brand_id) or []

                # Step 2: Process through layers
                optimized = []
                if not skip_process and official:
                    optimized = self._process_layers(
                        brand_id, official, commercial, contextual
                    )

                if optimized:
                    all_optimized[brand_id] = optimized
                    report["products_total"] += len(optimized)

                report["brands_processed"] += 1

            except Exception as e:
                logger.error(f"Error processing {brand_id}: {e}")
                report["errors"].append({"brand": brand_id, "error": str(e)})

        # Step 3: Deploy to frontend
        if not skip_deploy and all_optimized:
            self._deploy_to_frontend(all_optimized)

        # Generate TypeScript types
        if config.GENERATE_TYPES:
            self._generate_typescript_types()

        # Finalize report
        report["completed_at"] = datetime.utcnow().isoformat()
        report["duration_seconds"] = (
            datetime.utcnow() - start_time).total_seconds()

        self._save_report(report)

        logger.info(
            f"\n✅ Pipeline complete: {report['brands_processed']} brands, {report['products_total']} products")

        return report

    async def _ingest_brand(
        self,
        brand_id: str,
        brand_info: Dict[str, Any]
    ) -> tuple:
        """Ingest data from all 3 sources for a brand."""

        logger.info(f"📥 Ingesting data for {brand_id}")

        # Official data
        official = []
        official_url = brand_info.get('official_url', '')
        if official_url:
            official = await self.official_harvester.harvest_brand(
                brand_id=brand_id,
                brand_name=brand_info.get('name', brand_id),
                official_url=official_url,
            )
        else:
            # Try to load from cache or use mock
            official = self.official_harvester.load_cached(brand_id) or []
            if not official:
                official = await self.official_harvester._harvest_mock(
                    brand_id, brand_info.get('name', brand_id)
                )

        # Commercial data
        commercial = await self.commercial_harvester.harvest_brand(
            brand_id=brand_id,
            brand_name=brand_info.get('name', brand_id),
        )

        # Contextual data
        if official:
            products_for_context = [
                {"id": p.manufacturer_sku, "name": p.official_name,
                    "brand": brand_info.get('name', brand_id)}
                for p in official
            ]
            contextual = await self.contextual_harvester.harvest_brand(
                brand_id=brand_id,
                products=products_for_context,
            )
        else:
            contextual = []

        logger.info(
            f"  → Official: {len(official)}, Commercial: {len(commercial)}, Contextual: {len(contextual)}")

        return official, commercial, contextual

    def _process_layers(
        self,
        brand_id: str,
        official: List[OfficialData],
        commercial: List[CommercialData],
        contextual: List[ContextualData],
    ) -> List[OptimizedProduct]:
        """Process data through 3 layers."""

        logger.info(f"⚙️ Processing layers for {brand_id}")

        # Layer 1: Normalize
        normalized = self.normalize_layer.process_brand(
            brand_id, official, commercial, contextual
        )

        # Layer 2: Enrich
        enriched = self.enrich_layer.process_products(brand_id, normalized)

        # Layer 3: Optimize
        optimized = self.optimize_layer.process_products(brand_id, enriched)

        return optimized

    def _deploy_to_frontend(
        self,
        all_products: Dict[str, List[OptimizedProduct]]
    ) -> None:
        """Deploy catalogs to frontend/public/data."""

        logger.info(f"🚀 Deploying to frontend")

        output_dir = config.FRONTEND_DATA_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        brand_summaries = []
        total_products = 0
        total_verified = 0

        for brand_id, products in all_products.items():
            # Write brand catalog
            catalog = BrandCatalog(
                brand=brand_id,
                brand_name=brand_id.replace('-', ' ').title(),
                product_count=len(products),
                products=products,
                generated_at=datetime.utcnow().isoformat(),
            )

            catalog_file = output_dir / f"{brand_id}.json"
            with open(catalog_file, 'w', encoding='utf-8') as f:
                json.dump(catalog.model_dump(mode='json'),
                          f, indent=2, ensure_ascii=False)

            # Count for index
            verified = sum(1 for p in products if p.tier in [
                           "diamond", "gold"])
            total_products += len(products)
            total_verified += verified

            brand_summaries.append(BrandSummary(
                id=brand_id,
                name=brand_id.replace('-', ' ').title(),
                product_count=len(products),
                verified_count=verified,
                data_file=f"{brand_id}.json",
            ))

        # Write index.json
        index = CatalogIndex(
            version="5.0.0",
            build_timestamp=datetime.utcnow().isoformat(),
            total_products=total_products,
            total_verified=total_verified,
            brands=brand_summaries,
        )

        index_file = output_dir / "index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index.model_dump(mode='json'),
                      f, indent=2, ensure_ascii=False)

        logger.info(
            f"  → Deployed {len(brand_summaries)} brands, {total_products} products to {output_dir}")

    def _generate_typescript_types(self) -> None:
        """Generate TypeScript types from Pydantic models."""
        from .typescript_generator import generate_types

        output_path = config.TYPES_OUTPUT_PATH
        try:
            generate_types(output_path)
            logger.info(f"  → Generated TypeScript types at {output_path}")
        except Exception as e:
            logger.error(f"Failed to generate TypeScript types: {e}")

    def _save_report(self, report: Dict[str, Any]) -> None:
        """Save pipeline report."""
        reports_dir = config.REPORTS_DIR
        reports_dir.mkdir(parents=True, exist_ok=True)

        report_file = reports_dir / \
            f"pipeline-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)


# Convenience functions for CLI
async def run_pipeline(
    brand_ids: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Run the full pipeline."""
    runner = PipelineRunner()
    return await runner.run_full_pipeline(brand_ids, **kwargs)


async def ingest_sources(
    brand_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Run only the ingestion phase."""
    runner = PipelineRunner()
    return await runner.run_full_pipeline(
        brand_ids,
        skip_process=True,
        skip_deploy=True,
    )


def process_layers(
    brand_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Run only the processing layers."""
    runner = PipelineRunner()
    return asyncio.run(runner.run_full_pipeline(
        brand_ids,
        skip_ingest=True,
        skip_deploy=True,
    ))


def deploy_catalog() -> None:
    """Deploy existing catalogs to frontend."""
    runner = PipelineRunner()

    # Load from golden directory
    all_products = {}
    for f in config.GOLDEN_DIR.glob("*.json"):
        brand_id = f.stem
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            products = [OptimizedProduct(**p)
                        for p in data.get('products', [])]
            if products:
                all_products[brand_id] = products

    runner._deploy_to_frontend(all_products)
