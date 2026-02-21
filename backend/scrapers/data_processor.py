#!/usr/bin/env python3
"""
Data Processor & Comparison Engine
Handles:
- Data merging
- Deduplication
- Fuzzy product matching
- Price comparison analysis
- Report generation (CSV, JSON)
"""

import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Processes and compares product data from Halilit and Thomann
    """

    def __init__(self,
                 data_dir="backend/scrapers",
                 report_dir="backend/reports"):
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self, source: str, brand: str) -> List[Dict]:
        """Load product data from JSON files"""
        filename = f"{source}_{brand.lower()}_full.json"
        filepath = self.data_dir / filename

        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✓ Loaded {len(data)} products from {filename}")
            return data
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return []

    def similarity_score(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two product names
        Returns score between 0 and 1
        """
        # Normalize names
        n1 = name1.lower().strip()
        n2 = name2.lower().strip()

        # Direct match
        if n1 == n2:
            return 1.0

        # Use SequenceMatcher
        score = SequenceMatcher(None, n1, n2).ratio()

        # Boost score if key words match
        keywords = ['rcf', 'mackie', 'pro', 'speaker', 'mixer', 'powered']

        for keyword in keywords:
            if keyword in n1 and keyword in n2:
                score *= 1.05

        return min(1.0, score)

    def find_best_match(self,
                        product: Dict,
                        candidates: List[Dict],
                        threshold: float = 0.5) -> Optional[Tuple[Dict, float]]:
        """
        Find best matching product from candidates
        Returns (matched_product, confidence_score) or None
        """
        best_match = None
        best_score = 0

        product_name = product.get('product_name') or product.get('name', '')

        for candidate in candidates:
            candidate_name = candidate.get(
                'product_name') or candidate.get('name', '')

            score = self.similarity_score(product_name, candidate_name)

            if score > best_score:
                best_score = score
                best_match = candidate

        if best_score >= threshold:
            return (best_match, best_score)

        return None

    def match_products(self,
                       source1_products: List[Dict],
                       source2_products: List[Dict],
                       threshold: float = 0.60) -> List[Dict]:
        """
        Match products across two sources
        """
        logger.info(
            f"Matching {len(source1_products)} vs {len(source2_products)} products...")

        matches = []

        for s1_prod in source1_products:
            match_result = self.find_best_match(
                s1_prod, source2_products, threshold)

            if match_result:
                s2_prod, confidence = match_result
                matches.append({
                    'source1_product': s1_prod,
                    'source2_product': s2_prod,
                    'confidence': confidence
                })
            else:
                # No match found
                matches.append({
                    'source1_product': s1_prod,
                    'source2_product': None,
                    'confidence': 0.0
                })

        matched_count = sum(1 for m in matches if m['source2_product'])
        logger.info(
            f"✓ Found {matched_count}/{len(matches)} matches ({matched_count/len(matches)*100:.1f}%)")

        return matches

    def calculate_price_comparison(self,
                                   match: Dict) -> Dict:
        """
        Calculate pricing metrics for a matched pair
        """
        import re

        s1_prod = match['source1_product']
        s2_prod = match['source2_product']

        # Parse Thomann price (may be string like "$839")
        s1_price = s1_prod.get('price', 0)
        if isinstance(s1_price, str):
            match_val = re.search(r'[\d,]+\.?\d*', s1_price.replace(',', ''))
            s1_price = float(match_val.group()) if match_val else 0
        else:
            s1_price = float(s1_price) if s1_price else 0

        comparison = {
            'thomann_price_usd': s1_price,
            'halilit_price_ils': s2_prod.get('price_ils') if s2_prod else None,
            'halilit_price_usd': s2_prod.get('price_usd') if s2_prod else None,
            'difference_usd': None,
            'difference_percent': None,
            'cheaper_platform': None
        }

        if comparison['thomann_price_usd'] and comparison['halilit_price_usd']:
            diff = comparison['thomann_price_usd'] - \
                comparison['halilit_price_usd']
            comparison['difference_usd'] = diff
            comparison['difference_percent'] = (
                diff / comparison['halilit_price_usd'] * 100) if comparison['halilit_price_usd'] > 0 else 0

            if diff < -5:  # Halilit cheaper by more than $5
                comparison['cheaper_platform'] = 'Halilit'
            elif diff > 5:
                comparison['cheaper_platform'] = 'Thomann'
            else:
                comparison['cheaper_platform'] = 'Similar'

        return comparison

    def generate_csv_report(self,
                            matches: List[Dict],
                            brand: str,
                            source1_name: str = "Halilit",
                            source2_name: str = "Thomann") -> Path:
        """
        Generate detailed CSV comparison report
        source1: Halilit (base catalog)
        source2: Thomann (comparison)
        """
        logger.info(f"Generating CSV report for {brand}...")

        filename = self.report_dir / f"{brand.lower()}_comparison_detailed.csv"

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'Brand',
                'Match_Status',
                f'{source1_name}_Name',
                f'{source1_name}_Price_ILS',
                f'{source1_name}_Price_USD',
                f'{source2_name}_Name',
                f'{source2_name}_Price_USD',
                'Price_Difference_USD',
                'Price_Difference_Percent',
                'Cheaper_Platform',
                'Match_Confidence',
                'Availability_Status',
                'Notes'
            ])

            writer.writeheader()

            for match in matches:
                s1_prod = match['source1_product']  # Halilit
                s2_prod = match['source2_product']  # Thomann

                price_comp = self.calculate_price_comparison(match)

                # Parse Halilit price
                s1_price = s1_prod.get('price', 0)
                if isinstance(s1_price, str):
                    import re
                    match_val = re.search(
                        r'[\d,]+\.?\d*', s1_price.replace(',', ''))
                    s1_price = float(match_val.group()) if match_val else 0
                else:
                    s1_price = float(s1_price) if s1_price else 0

                # Parse Thomann price (may be string like "$839")
                s2_price = 0
                if s2_prod:
                    s2_price = s2_prod.get('price', 0)
                    if isinstance(s2_price, str):
                        import re
                        match_val = re.search(
                            r'[\d,]+\.?\d*', s2_price.replace(',', ''))
                        s2_price = float(match_val.group()) if match_val else 0
                    else:
                        s2_price = float(s2_price) if s2_price else 0

                availability = 'Both'
                if s2_prod is None:
                    availability = f'Halilit only'
                elif s2_price == 0:
                    availability = 'Thomann no pricing'

                row = {
                    'Brand': brand,
                    'Match_Status': 'MATCHED' if s2_prod else 'UNMATCHED',
                    f'{source1_name}_Name': s1_prod.get('name') or s1_prod.get('product_name', ''),
                    f'{source1_name}_Price_ILS': f"₪{s1_prod.get('price_ils', 0):.0f}" if s1_prod.get('price_ils') else 'N/A',
                    f'{source1_name}_Price_USD': f"${s1_price:.2f}" if s1_price > 0 else 'N/A',
                    f'{source2_name}_Name': (s2_prod.get('name', '') if s2_prod else 'NOT FOUND'),
                    f'{source2_name}_Price_USD': f"${s2_price:.2f}" if s2_price > 0 else 'N/A',
                    'Price_Difference_USD': f"${price_comp['difference_usd']:.2f}" if price_comp['difference_usd'] else 'N/A',
                    'Price_Difference_Percent': f"{price_comp['difference_percent']:.1f}%" if price_comp['difference_percent'] is not None else 'N/A',
                    'Cheaper_Platform': price_comp['cheaper_platform'] or 'N/A',
                    'Match_Confidence': f"{match['confidence']*100:.0f}%",
                    'Availability_Status': availability,
                    'Notes': ''
                }

                writer.writerow(row)

        logger.info(f"✓ Report saved: {filename}")
        return filename

    def generate_summary_report(self,
                                all_matches: Dict[str, List[Dict]]) -> Path:
        """
        Generate summary statistics report
        """
        logger.info("Generating summary report...")

        summary = {
            'timestamp': str(Path('/proc/self/fd').stat().st_mtime),
            'total_products': 0,
            'total_matches': 0,
            'by_brand': {}
        }

        for brand, matches in all_matches.items():
            matched = sum(1 for m in matches if m['source2_product'])

            # Price analysis
            prices_matched = []
            for m in matches:
                if m['source2_product'] and m['source2_product'].get('price_usd'):
                    price_comp = self.calculate_price_comparison(m)
                    if price_comp['difference_usd']:
                        prices_matched.append(price_comp['difference_usd'])

            summary['by_brand'][brand] = {
                'total_products': len(matches),
                'matched_count': matched,
                'match_rate': f"{matched/len(matches)*100:.1f}%" if matches else "0%",
                'unmatched_count': len(matches) - matched,
                'avg_price_difference_usd': sum(prices_matched) / len(prices_matched) if prices_matched else None,
                'cheaper_platform': 'Thomann' if prices_matched and sum(prices_matched) > 0 else 'Halilit'
            }

            summary['total_products'] += len(matches)
            summary['total_matches'] += matched

        summary['overall_match_rate'] = f"{summary['total_matches']/summary['total_products']*100:.1f}%" if summary['total_products'] > 0 else "0%"

        # Save
        summary_file = self.report_dir / "comparison_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"✓ Summary saved: {summary_file}")

        # Print summary
        logger.info(f"\n{'='*80}")
        logger.info("COMPARISON SUMMARY")
        logger.info(f"{'='*80}")
        for brand, stats in summary['by_brand'].items():
            logger.info(f"\n{brand}:")
            logger.info(f"  Total Products: {stats['total_products']}")
            logger.info(
                f"  Matches: {stats['matched_count']} ({stats['match_rate']})")
            logger.info(f"  Unmatched: {stats['unmatched_count']}")
            if stats['avg_price_difference_usd']:
                logger.info(
                    f"  Avg Price Diff: ${stats['avg_price_difference_usd']:.2f}")

        return summary_file

    def run(self, brands: List[str] = ["RCF", "Mackie"]):
        """
        Master method: Run complete processing pipeline
        Halilit is the primary (base) catalog
        Find matches for each Halilit product on Thomann
        """
        logger.info(f"\n{'='*80}")
        logger.info("DATA PROCESSING & COMPARISON ENGINE")
        logger.info("Base Catalog: Halilit | Comparison: Thomann")
        logger.info(f"{'='*80}")

        all_matches = {}

        for brand in brands:
            logger.info(f"\n{'#'*80}")
            logger.info(f"# PROCESSING {brand.upper()}")
            logger.info(
                f"# Comparing {brand} products: Halilit (base) → Thomann (comparison)")
            logger.info(f"{'#'*80}")

            # Load data
            halilit = self.load_data("halilit", brand)
            thomann = self.load_data("thomann", brand)

            if not halilit:
                logger.warning(f"Skipping {brand}: no Halilit data")
                continue

            if not thomann:
                logger.warning(
                    f"No Thomann data for {brand}, creating unmatched list")
                thomann = []

            # Match products - Halilit is PRIMARY (source1), Thomann is secondary (source2)
            matches = self.match_products(halilit, thomann, threshold=0.60)
            all_matches[brand] = matches

            logger.info(f"\nHalilit products to match: {len(halilit)}")
            logger.info(f"Thomann products available: {len(thomann)}")
            matched = sum(1 for m in matches if m['source2_product'])
            logger.info(
                f"Matched on Thomann: {matched}/{len(matches)} ({matched/len(matches)*100:.1f}%)")

            # Generate CSV report
            self.generate_csv_report(matches, brand)

        # Generate summary report
        if all_matches:
            self.generate_summary_report(all_matches)

        logger.info(f"\n✓ All reports saved to: {self.report_dir}")


if __name__ == "__main__":
    processor = DataProcessor()
    processor.run(["RCF", "Mackie"])
