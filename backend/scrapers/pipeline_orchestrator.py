#!/usr/bin/env python3
"""
Master Orchestrator: Complete Scraping & Comparison Pipeline
Coordinates all scrapers and processors in correct sequence
"""

import json
import logging
import sys
import time
from pathlib import Path
from datetime import datetime
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """
    Orchestrates the complete scraping and comparison pipeline
    Sequence:
    1. Halilit extraction (Method 1: JSON)
    2. Thomann full-catalog scraping
    3. Data processing & matching
    4. Report generation
    """

    def __init__(self,
                 base_dir="/workspaces/Halilit-Support-Center",
                 brands=["RCF", "Mackie"]):
        self.base_dir = Path(base_dir)
        self.brands = brands
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'steps': {}
        }

    def step_1_extract_halilit(self):
        """Step 1: Extract ALL products from Halilit"""
        logger.info(f"\n{'='*80}")
        logger.info("STEP 1: Extract ALL Halilit Data")
        logger.info(f"{'='*80}")

        try:
            script = self.base_dir / "backend/scrapers/halilit_full_catalog_scraper.py"

            if not script.exists():
                logger.error(f"Script not found: {script}")
                return False

            logger.info(f"Running: {script}")

            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=300
            )

            logger.info(result.stdout)

            if result.returncode == 0:
                self.results['steps']['halilit_extraction'] = {
                    'status': 'SUCCESS',
                    'output': result.stdout[-500:] if result.stdout else ''
                }
                logger.info("✓ Halilit extraction complete")
                return True
            else:
                logger.error(f"Script failed: {result.stderr}")
                self.results['steps']['halilit_extraction'] = {
                    'status': 'FAILED',
                    'error': result.stderr
                }
                return False

        except Exception as e:
            logger.error(f"Error in Step 1: {e}")
            self.results['steps']['halilit_extraction'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            return False

    def step_2_scrape_thomann(self):
        """Step 2: Scrape Thomann full category pages"""
        logger.info(f"\n{'='*80}")
        logger.info("STEP 2: Scrape Thomann Full Catalog")
        logger.info(f"{'='*80}")

        try:
            # Check if cloudscraper is installed
            try:
                import cloudscraper
            except ImportError:
                logger.warning("cloudscraper not installed. Installing...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "cloudscraper"],
                    capture_output=True,
                    timeout=60
                )

            script = self.base_dir / "backend/scrapers/thomann_full_catalog_scraper.py"

            if not script.exists():
                logger.error(f"Script not found: {script}")
                return False

            logger.info(f"Running: {script}")

            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )

            logger.info(result.stdout)

            if result.returncode == 0:
                self.results['steps']['thomann_scraping'] = {
                    'status': 'SUCCESS',
                    'output': result.stdout[-500:] if result.stdout else ''
                }
                logger.info("✓ Thomann scraping complete")
                return True
            else:
                logger.error(f"Script failed: {result.stderr}")
                self.results['steps']['thomann_scraping'] = {
                    'status': 'FAILED',
                    'error': result.stderr
                }
                return False

        except Exception as e:
            logger.error(f"Error in Step 2: {e}")
            self.results['steps']['thomann_scraping'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            return False

    def step_3_process_data(self):
        """Step 3: Process, match, and compare data"""
        logger.info(f"\n{'='*80}")
        logger.info("STEP 3: Process & Compare Data")
        logger.info(f"{'='*80}")

        try:
            script = self.base_dir / "backend/scrapers/data_processor.py"

            if not script.exists():
                logger.error(f"Script not found: {script}")
                return False

            logger.info(f"Running: {script}")

            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=300
            )

            logger.info(result.stdout)

            if result.returncode == 0:
                self.results['steps']['data_processing'] = {
                    'status': 'SUCCESS',
                    'output': result.stdout[-500:] if result.stdout else ''
                }
                logger.info("✓ Data processing complete")
                return True
            else:
                logger.error(f"Script failed: {result.stderr}")
                self.results['steps']['data_processing'] = {
                    'status': 'FAILED',
                    'error': result.stderr
                }
                return False

        except Exception as e:
            logger.error(f"Error in Step 3: {e}")
            self.results['steps']['data_processing'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            return False

    def verify_outputs(self):
        """Verify that all outputs were generated correctly"""
        logger.info(f"\n{'='*80}")
        logger.info("STEP 4: Verify Outputs")
        logger.info(f"{'='*80}")

        scrapers_dir = self.base_dir / "backend/scrapers"
        reports_dir = self.base_dir / "backend/reports"

        expected_files = {
            'Halilit': [
                scrapers_dir / "halilit_rcf_full.json",
                scrapers_dir / "halilit_mackie_full.json",
                scrapers_dir / "halilit_full_merged.json",
                scrapers_dir / "halilit_extraction_summary.json"
            ],
            'Thomann': [
                scrapers_dir / "thomann_rcf_full.json",
                scrapers_dir / "thomann_mackie_full.json",
                scrapers_dir / "thomann_full_merged.json",
                scrapers_dir / "thomann_scraping_summary.json"
            ],
            'Reports': [
                reports_dir / "rcf_comparison_detailed.csv",
                reports_dir / "mackie_comparison_detailed.csv",
                reports_dir / "comparison_summary.json"
            ]
        }

        verification = {}
        all_good = True

        for category, files in expected_files.items():
            logger.info(f"\n{category} Files:")
            verification[category] = {}

            for filepath in files:
                exists = filepath.exists()
                size = filepath.stat().st_size if exists else 0

                status = "✓" if exists and size > 0 else "✗"
                logger.info(f"  {status} {filepath.name} ({size} bytes)")

                verification[category][filepath.name] = {
                    'exists': exists,
                    'size': size
                }

                if not exists or size == 0:
                    all_good = False

        self.results['verification'] = verification

        if all_good:
            logger.info("\n✓ All output files verified successfully!")
        else:
            logger.warning("\n⚠ Some output files missing or empty")

        return all_good

    def generate_final_report(self):
        """Generate final pipeline report"""
        logger.info(f"\n{'='*80}")
        logger.info("FINAL PIPELINE REPORT")
        logger.info(f"{'='*80}")

        # Try to load summary statistics
        summary_file = self.base_dir / "backend/reports/comparison_summary.json"
        if summary_file.exists():
            try:
                with open(summary_file) as f:
                    summary = json.load(f)

                logger.info("\nCOMPARISON RESULTS:")
                for brand, stats in summary.get('by_brand', {}).items():
                    logger.info(f"\n{brand}:")
                    logger.info(
                        f"  Total Products: {stats.get('total_products')}")
                    logger.info(
                        f"  Matched: {stats.get('matched_count')} ({stats.get('match_rate')})")
                    logger.info(f"  Unmatched: {stats.get('unmatched_count')}")
                    if stats.get('avg_price_difference_usd'):
                        logger.info(
                            f"  Avg Price Diff: ${stats['avg_price_difference_usd']:.2f}")

                self.results['summary'] = summary
            except Exception as e:
                logger.warning(f"Could not load summary: {e}")

        # Save final report
        report_file = self.base_dir / "backend/reports/pipeline_execution_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"\n✓ Full report saved: {report_file}")

    def run(self):
        """Execute complete pipeline"""
        logger.info(f"\n{'#'*80}")
        logger.info(
            "# HALILIT VS THOMANN: COMPLETE SCRAPING & COMPARISON PIPELINE")
        logger.info(f"{'#'*80}")

        start_time = time.time()

        # Step 1: Extract Halilit
        if not self.step_1_extract_halilit():
            logger.error("Stopping pipeline: Halilit extraction failed")
            return False

        # Step 2: Scrape Thomann
        if not self.step_2_scrape_thomann():
            logger.error("Stopping pipeline: Thomann scraping failed")
            return False

        # Step 3: Process data
        if not self.step_3_process_data():
            logger.error("Stopping pipeline: Data processing failed")
            return False

        # Step 4: Verify outputs
        if not self.verify_outputs():
            logger.warning("Some output files missing, but continuing...")

        # Step 5: Generate report
        self.generate_final_report()

        # Timing
        elapsed = time.time() - start_time
        logger.info(f"\n✓ PIPELINE COMPLETE in {elapsed:.1f} seconds")

        return True


if __name__ == "__main__":
    orchestrator = PipelineOrchestrator()
    success = orchestrator.run()

    sys.exit(0 if success else 1)
