#!/usr/bin/env python3
"""
Conductor: Spectrum Data Management & Verification

This script provides automated verification gates and quality reporting
for the Spectrum Screen's data pipeline.
"""

from backend.skills.spectrum_enrichment import (
    OfficialSpecsEnricher,
    TrustedReviewAggregator,
    SpecificationNormalizer
)
from backend.skills.spectrum_validator import (
    SpectrumValidator,
    QualityReportGenerator,
    DataProvenanceTracker
)
from backend.skills.spectrum_data_pipeline import SpectrumDataPipeline
import json
import sys
import os
from typing import Dict, List, Any
from datetime import datetime
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SpectrumDataConductor:
    """
    Master conductor for Spectrum data management.
    Orchestrates pipeline, validation, and reporting.
    """

    def __init__(self):
        self.pipeline = SpectrumDataPipeline()
        self.validator = SpectrumValidator()
        self.reporter = QualityReportGenerator()
        self.tracker = DataProvenanceTracker()
        self.enricher_specs = OfficialSpecsEnricher()
        self.enricher_reviews = TrustedReviewAggregator()
        self.normalizer = SpecificationNormalizer()

    def run_complete_pipeline(self, brand: str, deep_refresh: bool = False) -> Dict[str, Any]:
        """
        Execute complete pipeline: scrape → validate → enrich → report
        """
        print(f"\n{'='*70}")
        print(f"🌌 SPECTRUM DATA CONDUCTOR - {brand.upper()}")
        print(f"{'='*70}\n")

        results = {
            'brand': brand,
            'timestamp': datetime.utcnow().isoformat(),
            'phases': {}
        }

        # PHASE 1: Pipeline
        print("📊 PHASE 1: Data Pipeline Execution")
        print("-" * 70)
        phase1_success, payload = self.pipeline.execute({
            'brand': brand,
            'include_enrichment': True,
            'force_refresh': deep_refresh
        })

        if not phase1_success:
            print(f"❌ Pipeline failed: {payload}")
            return {'success': False, 'error': payload}

        print(f"✅ Pipeline succeeded")
        print(f"   Total products: {payload.get('total_products')}")
        print(f"   Tracks: {len(payload.get('tracks', []))}")

        results['phases']['pipeline'] = {
            'success': True,
            'total_products': payload.get('total_products')
        }

        # PHASE 2: Validation
        print("\n✓ PHASE 2: Data Validation")
        print("-" * 70)
        valid, validation_results = self.validator.execute({
            'payload': payload,
            'brand_taxonomy': ['Nord', 'Moog', 'Roland', 'Yamaha', 'Korg', 'Universal-Audio']
        })

        print(
            f"{'✅' if valid else '⚠️ '} Validation {'PASSED' if valid else 'COMPLETED WITH WARNINGS'}")
        print(
            f"   Quality Score: {validation_results.get('quality_score'):.1f}/100")
        print(
            f"   Products Validated: {validation_results.get('products_validated')}")
        print(
            f"   Products Rejected: {validation_results.get('products_rejected')}")
        print(
            f"   Critical Errors: {len(validation_results.get('errors', []))}")
        print(f"   Warnings: {len(validation_results.get('warnings', []))}")

        results['phases']['validation'] = {
            'passed': valid,
            'quality_score': validation_results.get('quality_score'),
            'products_validated': validation_results.get('products_validated'),
            'products_rejected': validation_results.get('products_rejected'),
            'error_count': len(validation_results.get('errors', [])),
            'warning_count': len(validation_results.get('warnings', []))
        }

        # Show first few errors/warnings
        if validation_results.get('errors'):
            print(f"\n   ⚠️  Critical Errors:")
            for error in validation_results.get('errors', [])[:3]:
                print(f"      - {error}")

        if validation_results.get('warnings'):
            print(f"\n   ℹ️  Warnings:")
            for warning in validation_results.get('warnings', [])[:3]:
                print(f"      - {warning}")

        # PHASE 3: Quality Report
        print("\n📋 PHASE 3: Quality Report Generation")
        print("-" * 70)
        report_success, report = self.reporter.execute({
            'validation_results': validation_results,
            'brand': brand
        })

        if report_success:
            summary = report.get('summary', {})
            print(f"✅ Report generated successfully")
            print(f"   Overall Quality: {summary.get('overall_quality'):.1f}%")
            print(f"   Critical Errors: {summary.get('critical_errors')}")
            print(f"   Warnings Count: {summary.get('warnings')}")

            recommendations = report.get('recommendations', [])
            if recommendations:
                print(f"\n   📌 Recommendations:")
                for rec in recommendations[:3]:
                    print(f"      - {rec}")

            results['phases']['report'] = {
                'success': True,
                'quality_score': summary.get('overall_quality'),
                'recommendations': recommendations
            }
        else:
            print(f"⚠️  Report generation failed: {report}")
            results['phases']['report'] = {'success': False}

        # PHASE 4: Data Provenance Tracking
        print("\n🔗 PHASE 4: Data Provenance Verification")
        print("-" * 70)

        # Sample a product for provenance check
        sample_product = None
        for track in payload.get('tracks', []):
            if track.get('products'):
                sample_product = track['products'][0]
                break

        if sample_product:
            prov_success, provenance = self.tracker.execute({
                'product': sample_product
            })

            if prov_success:
                print(f"✅ Provenance tracking verified")
                print(f"   Sample Product: {sample_product.get('name')}")
                print(f"   Sources: {sample_product.get('sources', [])}")

                provenance = provenance.get('provenance', {})
                print(f"   Data lineage:")
                print(
                    f"      - Halilit: {provenance.get('halilit', {}).get('source', 'N/A')}")
                print(
                    f"      - Official: {provenance.get('official_sources', {}).get('sources', 'N/A')}")
                print(
                    f"      - Reviews: {provenance.get('trusted_reviews', {}).get('sources', 'N/A')}")

                results['phases']['provenance'] = {
                    'success': True,
                    'sample_product': sample_product.get('name')
                }

        # FINAL SUMMARY
        print("\n" + "="*70)
        print("🎯 SUMMARY")
        print("="*70)

        overall_success = (
            phase1_success and
            valid and
            (validation_results.get('quality_score', 0) > 70)
        )

        print(
            f"\n{'✅ PIPELINE READY FOR PRODUCTION' if overall_success else '⚠️  PIPELINE NEEDS ATTENTION'}\n")
        print(f"Brand: {brand}")
        print(f"Total Products: {payload.get('total_products')}")
        print(
            f"Quality Score: {validation_results.get('quality_score'):.1f}/100")
        print(
            f"Validation Status: {'✅ PASSED' if valid else '⚠️  WITH WARNINGS'}")
        print(
            f"Data Sources: {', '.join(payload.get('metadata', {}).get('data_sources', {}).keys())}")

        results['success'] = overall_success
        results['quality_score'] = validation_results.get('quality_score')

        print(f"\n{'-'*70}\n")

        return results

    def verify_all_brands(self) -> Dict[str, Any]:
        """
        Verify all brands in the system.
        """
        brands = ['Nord', 'Moog', 'Roland',
                  'Yamaha', 'Korg', 'Universal-Audio']

        print("\n" + "="*70)
        print("🌍 VERIFYING ALL BRANDS")
        print("="*70 + "\n")

        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_brands': len(brands),
            'brands': {}
        }

        for brand in brands:
            brand_results = self.run_complete_pipeline(
                brand, deep_refresh=False)
            results['brands'][brand] = {
                'success': brand_results.get('success'),
                'quality_score': brand_results.get('quality_score'),
                'phases': brand_results.get('phases')
            }

        # Summary statistics
        successful = sum(
            1 for r in results['brands'].values()
            if r.get('success')
        )
        avg_quality = sum(
            r.get('quality_score', 0) for r in results['brands'].values()
        ) / len(brands)

        print("\n" + "="*70)
        print("📊 OVERALL SUMMARY")
        print("="*70)
        print(f"\nBrands Verified: {len(brands)}")
        print(f"Successful: {successful}/{len(brands)}")
        print(f"Average Quality Score: {avg_quality:.1f}/100")

        if successful == len(brands):
            print(f"\n✅ ALL BRANDS VERIFIED SUCCESSFULLY!\n")
        else:
            print(
                f"\n⚠️  {len(brands) - successful} brand(s) need attention\n")

        return results

    def generate_html_report(self, results: Dict[str, Any], output_file: str = "spectrum_report.html"):
        """
        Generate HTML report for visualization.
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Spectrum Data Quality Report</title>
            <style>
                body {{ font-family: monospace; background: #0b0c10; color: #e0e0e0; padding: 20px; }}
                .header {{ color: #00d4ff; font-size: 24px; font-weight: bold; margin-bottom: 20px; }}
                .summary {{ background: #1a1a2e; padding: 15px; border-left: 4px solid #00d4ff; margin: 10px 0; }}
                .success {{ border-left-color: #00ff88; color: #00ff88; }}
                .warning {{ border-left-color: #ffaa00; color: #ffaa00; }}
                .error {{ border-left-color: #ff0055; color: #ff0055; }}
                .metric {{ margin: 10px 0; }}
                .brand-section {{ margin: 20px 0; padding: 15px; background: #1a1a2e; border: 1px solid #333; }}
            </style>
        </head>
        <body>
            <div class="header">🌌 Spectrum Data Quality Report</div>
            <div class="summary">
                Generated: {results.get('timestamp')}
                <br>Total Brands: {results.get('total_brands')}
            </div>
            
            <div class="metric" style="font-size: 18px; color: #00d4ff; margin: 20px 0;">Brand Reports:</div>
            
            {self._generate_brand_html(results.get('brands', {}))}
            
        </body>
        </html>
        """

        with open(output_file, 'w') as f:
            f.write(html)

        print(f"✅ Report saved to {output_file}")

    def _generate_brand_html(self, brands: Dict[str, Any]) -> str:
        """Generate HTML for brand results."""
        html = ""
        for brand, result in brands.items():
            success = result.get('success')
            quality = result.get('quality_score', 0)
            status_class = 'success' if success else 'warning'

            html += f"""
            <div class="brand-section">
                <div style="color: #00ff88; font-size: 16px;">{brand}</div>
                <div class="metric">Status: <span class="{status_class}">{'✅ PASS' if success else '⚠️  NEEDS ATTENTION'}</span></div>
                <div class="metric">Quality Score: {quality:.1f}/100</div>
            </div>
            """

        return html


def main():
    """Main entry point."""
    conductor = SpectrumDataConductor()

    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'verify':
            # Verify specific brand or all
            brand = sys.argv[2] if len(sys.argv) > 2 else None

            if brand:
                results = conductor.run_complete_pipeline(
                    brand, deep_refresh=False)
            else:
                results = conductor.verify_all_brands()

            # Generate report
            conductor.generate_html_report(results)

        elif command == 'rebuild':
            # Rebuild specific brand data
            brand = sys.argv[2] if len(sys.argv) > 2 else 'Nord'
            deep = '--deep' in sys.argv

            print(f"🔄 Rebuilding {brand} (deep={deep})...")
            results = conductor.run_complete_pipeline(brand, deep_refresh=deep)

        else:
            print(f"Unknown command: {command}")
            print(
                "Usage: python conductor_spectrum.py [verify|rebuild] [brand]")
            sys.exit(1)
    else:
        # Default: verify all
        results = conductor.verify_all_brands()
        conductor.generate_html_report(results)


if __name__ == '__main__':
    main()
