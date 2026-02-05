#!/usr/bin/env python3
"""
Real Data Integration Test - End-to-End Pipeline Testing

Tests the complete pipeline:
1. Load products from backend/data/brands/{brand}/products.json
2. Process through ingestion orchestrator
3. Convert to Spectrum format
4. Persist to database
5. Verify results and metrics

Usage:
    python3 backend/ingestion/test_real_data_pipeline.py
"""

from backend.ingestion.trinity_integration import get_trinity_ingestion_bridge
import sys
import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            "/workspaces/Halilit-Support-Center/backend/data/ingestion/test_pipeline.log"),
    ],
)

logger = logging.getLogger("TestPipeline")


def find_available_brands() -> List[str]:
    """Find all brands with product data"""
    brands_dir = Path("/workspaces/Halilit-Support-Center/backend/data/brands")
    brands = []

    if not brands_dir.exists():
        logger.warning(f"Brands directory not found: {brands_dir}")
        return brands

    for brand_path in brands_dir.iterdir():
        if brand_path.is_dir():
            product_file = brand_path / "products.json"
            if product_file.exists():
                brands.append(brand_path.name)

    logger.info(f"Found {len(brands)} brands: {', '.join(brands)}")
    return sorted(brands)


def test_single_brand(brand: str, bridge) -> Dict[str, Any]:
    """Test pipeline for a single brand"""
    logger.info(f"\n{'='*70}")
    logger.info(f"Testing Brand: {brand}")
    logger.info(f"{'='*70}")

    start_time = time.time()

    try:
        result = bridge.process_brand_pipeline(brand)
        elapsed = time.time() - start_time

        # Print results
        print(f"\n{'='*70}")
        print(f"✅ PIPELINE RESULTS FOR {brand.upper()}")
        print(f"{'='*70}")

        if result["success"]:
            print(f"Status: ✅ SUCCESS ({elapsed:.2f}s)")
            print(f"\nTrinity Harvest:")
            print(
                f"  • Products harvested: {result['trinity_harvest']['total_harvested']}")

            if result["orchestrator_report"]:
                print(f"\nOrchestrator Report:")
                print(
                    f"  • Total processed: {result['orchestrator_report']['total_processed']}")
                print(
                    f"  • Approved: {result['orchestrator_report']['approved_count']}")
                print(
                    f"  • Rejected: {result['orchestrator_report']['rejected_count']}")
                print(
                    f"  • Execution time: {result['orchestrator_report']['execution_time']:.2f}s")

            if result["metrics"]:
                metrics = result["metrics"]
                print(f"\nDisplay Metrics:")
                print(
                    f"  • Total products: {metrics.get('total_products', 0)}")
                print(
                    f"  • Average quality: {metrics.get('average_quality', 0):.1f}%")
                print(f"  • Hero products: {metrics.get('hero_count', 0)}")

                if "products_by_tier" in metrics:
                    print(f"  • Products by tier:")
                    for tier, count in metrics["products_by_tier"].items():
                        print(f"    - {tier}: {count}")

            if result["database_paths"]:
                print(f"\nDatabase Persistence:")
                for key, path in result["database_paths"].items():
                    print(f"  • {key}: {Path(path).name}")

            if result["quality_report"]:
                quality = result["quality_report"]
                print(f"\nQuality Report:")
                print(
                    f"  • Overall quality: {quality.get('overall_quality_score', 0):.1f}%")
                print(
                    f"  • Avg completeness: {quality.get('average_completeness', 0):.1f}%")
                print(f"  • Warnings: {len(quality.get('warnings', []))}")
                print(
                    f"  • Recommendations: {len(quality.get('recommendations', []))}")

        else:
            print(f"Status: ❌ FAILED ({elapsed:.2f}s)")
            print(f"Errors:")
            for error in result["errors"]:
                print(f"  • {error}")

        print(f"{'='*70}\n")
        return result

    except Exception as e:
        logger.error(f"Test failed for {brand}: {e}", exc_info=True)
        return {"brand": brand, "success": False, "error": str(e)}


def run_comprehensive_test():
    """Run comprehensive test across all brands"""
    logger.info("🚀 STARTING COMPREHENSIVE INTEGRATION TEST")
    logger.info(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize bridge
    bridge = get_trinity_ingestion_bridge()

    # Find brands
    brands = find_available_brands()
    if not brands:
        logger.error("No brands found to test!")
        return False

    # Test each brand
    results = {}
    successful = 0
    failed = 0

    for brand in brands:
        result = test_single_brand(brand, bridge)
        results[brand] = result
        if result.get("success"):
            successful += 1
        else:
            failed += 1

    # Print summary
    print(f"\n{'='*70}")
    print(f"🎯 TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Total brands tested: {len(brands)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"Success rate: {(successful/len(brands)*100):.1f}%")
    print(f"{'='*70}\n")

    # Print detailed summary table
    print("Detailed Results:")
    print(f"{'Brand':<20} {'Status':<12} {'Approved':<12} {'Quality':<12}")
    print("-" * 56)

    for brand in brands:
        result = results[brand]
        if result.get("success"):
            status = "✅ SUCCESS"
            approved = result.get("orchestrator_report",
                                  {}).get("approved_count", 0)
            quality = result.get("quality_report", {}).get(
                "overall_quality_score", 0)
            print(f"{brand:<20} {status:<12} {approved:<12} {quality:.1f}%")
        else:
            status = "❌ FAILED"
            print(f"{brand:<20} {status:<12} {'-':<12} {'-':<12}")

    print("-" * 56)

    # Get analytics
    print(f"\n{'='*70}")
    print(f"📊 ANALYTICS")
    print(f"{'='*70}")

    try:
        analytics = bridge.get_all_analytics()
        print(f"Total brands in database: {len(analytics.get('brands', {}))}")
        for brand, stats in analytics.get("brands", {}).items():
            print(f"\n{brand}:")
            print(f"  • Total runs: {stats.get('total_runs', 0)}")
            print(
                f"  • Approved products: {stats.get('approved_products_count', 0)}")
            print(
                f"  • Rejected products: {stats.get('rejected_products_count', 0)}")
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")

    print(f"{'='*70}\n")

    return successful == len(brands)


def run_single_brand_test(brand: str):
    """Run test for a single brand"""
    logger.info(f"🚀 TESTING SINGLE BRAND: {brand}")

    bridge = get_trinity_ingestion_bridge()
    result = test_single_brand(brand, bridge)

    return result.get("success", False)


def test_spectrum_conversion():
    """Test Spectrum conversion specifically"""
    logger.info("\n🚀 TESTING SPECTRUM CONVERSION")

    from backend.ingestion import (
        get_ingestion_orchestrator,
        get_spectrum_adapter,
        IngestionProductDraft,
        IngestionReport,
    )

    orchestrator = get_ingestion_orchestrator()
    adapter = get_spectrum_adapter()

    # Load sample products
    brand = "Nord"
    try:
        with open("/workspaces/Halilit-Support-Center/backend/data/brands/Nord/products.json") as f:
            data = json.load(f)
            raw_products = data.get("products", [])[:5]  # Test with 5 products

        logger.info(
            f"Testing conversion with {len(raw_products)} Nord products")

        # Process through orchestrator
        report = orchestrator.ingest_batch(brand, raw_products)
        logger.info(
            f"Orchestrator: {report.approved_count} approved, {report.rejected_count} rejected"
        )

        # Convert to Spectrum
        payload, quality = adapter.convert_ingestion_report(report)
        logger.info(
            f"Spectrum: {payload.total_products} products in {len(payload.tracks)} tracks")

        # Print track distribution
        print(f"\n{'='*70}")
        print(f"SPECTRUM TRACK DISTRIBUTION")
        print(f"{'='*70}")
        for tier, track in payload.tracks.items():
            print(f"{track.tier_label:<20} : {track.get_product_count():>3} products")
        print(f"{'='*70}\n")

        return True

    except Exception as e:
        logger.error(f"Spectrum conversion test failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")

    if len(sys.argv) > 1:
        if sys.argv[1] == "--single":
            if len(sys.argv) > 2:
                brand = sys.argv[2]
                success = run_single_brand_test(brand)
            else:
                print(
                    "Usage: python3 test_real_data_pipeline.py --single {brand}")
                success = False
        elif sys.argv[1] == "--spectrum":
            success = test_spectrum_conversion()
        else:
            print(
                "Usage: python3 test_real_data_pipeline.py [--single {brand} | --spectrum]")
            success = False
    else:
        success = run_comprehensive_test()

    sys.exit(0 if success else 1)
