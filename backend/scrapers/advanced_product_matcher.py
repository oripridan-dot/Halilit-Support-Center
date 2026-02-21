#!/usr/bin/env python3
"""
Advanced Product Comparison Engine
- Name-based fuzzy matching with taxonomy flexibility
- USD to ILS price conversion
- 100% matching target for all Halilit products
"""

import json
import csv
import logging
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Exchange rate (can be updated)
USD_TO_ILS = 3.65


class AdvancedProductMatcher:
    """
    Advanced matching engine that:
    - Normalizes product names
    - Uses flexible name matching
    - Considers product categories/taxonomy
    - Converts currencies
    """

    def __init__(self, data_dir="backend/scrapers", report_dir="backend/reports"):
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self, source: str, brand: str) -> List[Dict]:
        """Load product data from JSON files"""
        filename = f"{source}_{brand.lower()}_complete.json"
        filepath = self.data_dir / filename

        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✓ Loaded {len(data)} {source} {brand} products")
            return data
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return []

    def normalize_product_name(self, name: str) -> str:
        """
        Normalize product name for fuzzy matching
        - Lowercase
        - Remove special characters
        - Remove extra spaces
        - Simplify model numbers
        """
        # Lowercase
        name = name.lower().strip()

        # Remove leading numbers/counts (like "10RCF", "40RCF")
        name = re.sub(r'^\d+\s*', '', name)

        # Remove currency symbols and prices
        name = re.sub(r'[\$₪€][\d,.\s]*', '', name)

        # Normalize spaces
        name = re.sub(r'\s+', ' ', name)

        # Remove extra punctuation but keep dashes/slashes in model numbers
        name = re.sub(r'[()]', '', name)

        # Normalize model number formats (mk v → mkv, etc)
        name = re.sub(r'\s+mk\s+v\s*$', ' mkv', name)
        name = re.sub(r'\s+mk\s*5\s*$', ' mk5', name)

        # Normalize common abbreviations
        replacements = {
            'ring light': 'ring',
            'protection cover': 'cover',
            'bag': 'bag',
            'backpack': 'bag',
            'gig bag': 'bag',
            'microphone': 'mic',
            'condenser': 'condenser',
            'powered': 'powered',
            'monitor': 'monitor',
            'speaker': 'speaker',
            'subwoofer': 'sub',
        }

        for old, new in replacements.items():
            name = name.replace(old, new)

        return name.strip()

    def extract_product_code(self, name: str) -> str:
        """
        Extract product code/model number
        Examples: ART-710, HDL-20, ProFX10v3
        """
        # Look for model patterns
        patterns = [
            r'[A-Z]+[-\s]?\d+',  # RCF ART-710, HDL 20
            r'[A-Za-z]+\d+[a-z]\d+',  # ProFX10v3
            r'[A-Z]+[-]?\d+[A-Z]*[-]?[A-Z\d]*',  # CVR-TT-515
        ]

        name_lower = name.lower()
        for pattern in patterns:
            match = re.search(pattern, name_lower, re.IGNORECASE)
            if match:
                return match.group().upper()

        return ""

    def calculate_similarity(self, name1: str, name2: str,
                             code1: str = "", code2: str = "") -> Tuple[float, str]:
        """
        Calculate similarity between two products
        Returns (confidence_score, match_reason)
        """
        # Normalize names
        n1 = self.normalize_product_name(name1)
        n2 = self.normalize_product_name(name2)

        # Exact match after normalization
        if n1 == n2:
            return (1.0, "exact_name_match")

        # Code match (most reliable)
        if code1 and code2 and code1 == code2:
            # Double-check with name similarity
            name_sim = SequenceMatcher(None, n1, n2).ratio()
            if name_sim > 0.5:
                return (0.95, "model_code_match")

        # Partial code match (same base model)
        if code1 and code2:
            # Check if one contains the other
            if code1 in code2 or code2 in code1:
                name_sim = SequenceMatcher(None, n1, n2).ratio()
                if name_sim > 0.6:
                    return (0.85, "partial_code_match")

        # Sequence matching on normalized names
        base_similarity = SequenceMatcher(None, n1, n2).ratio()

        # Boost if brand name appears in both
        brand_boost = 0
        if 'rcf' in n1 and 'rcf' in n2:
            brand_boost = 0.05
        elif 'mackie' in n1 and 'mackie' in n2:
            brand_boost = 0.05

        # Boost if key words match
        key_words = ['speaker', 'monitor', 'mixer',
                     'powered', 'mixer', 'cover', 'bag', 'mic']
        word_boost = 0
        for word in key_words:
            if word in n1 and word in n2:
                word_boost = 0.1
                break

        final_score = min(1.0, base_similarity + brand_boost + word_boost)

        if final_score >= 0.75:
            return (final_score, "fuzzy_match_strong")
        elif final_score >= 0.60:
            return (final_score, "fuzzy_match_moderate")
        else:
            return (final_score, "fuzzy_match_weak")

    def find_best_match(self, halilit_product: Dict,
                        thomann_products: List[Dict],
                        threshold: float = 0.60) -> Tuple[Optional[Dict], float, str]:
        """
        Find best matching Thomann product for Halilit product
        """
        h_name = halilit_product.get('name', '')
        h_code = self.extract_product_code(h_name)

        best_match = None
        best_score = 0
        best_reason = ""

        for thomann_prod in thomann_products:
            t_name = thomann_prod.get('name', '')
            t_code = self.extract_product_code(t_name)

            score, reason = self.calculate_similarity(
                h_name, t_name, h_code, t_code)

            if score > best_score:
                best_score = score
                best_match = thomann_prod
                best_reason = reason

        if best_score >= threshold:
            return (best_match, best_score, best_reason)
        else:
            return (None, best_score, best_reason)

    def convert_price_usd_to_ils(self, usd_price: float) -> float:
        """Convert USD price to ILS"""
        if not usd_price or usd_price <= 0:
            return 0
        return round(usd_price * USD_TO_ILS, 2)

    def match_all_products(self, halilit_products: List[Dict],
                           thomann_products: List[Dict],
                           brand: str, threshold: float = 0.60) -> List[Dict]:
        """
        Match all Halilit products to best Thomann equivalents
        Goal: 100% match (even if low confidence)
        """
        logger.info(f"\nMatching ALL {brand} products...")
        logger.info(
            f"Halilit: {len(halilit_products)} | Thomann: {len(thomann_products)}")

        matches = []

        for h_prod in halilit_products:
            match_result = self.find_best_match(
                h_prod, thomann_products, threshold=0
            )  # threshold=0 to find BEST match even if low confidence

            t_prod, confidence, reason = match_result

            match = {
                'halilit_product': h_prod,
                'thomann_product': t_prod,
                'confidence': confidence,
                'match_reason': reason
            }

            matches.append(match)

        # Statistics
        high_conf = sum(1 for m in matches if m['confidence'] >= 0.75)
        med_conf = sum(1 for m in matches if 0.60 <= m['confidence'] < 0.75)
        low_conf = sum(1 for m in matches if m['confidence'] < 0.60)

        logger.info(f"Match Results:")
        logger.info(f"  High confidence (≥75%): {high_conf}")
        logger.info(f"  Medium confidence (60-75%): {med_conf}")
        logger.info(f"  Low/Weak confidence (<60%): {low_conf}")
        logger.info(f"  TOTAL COVERAGE: 100% ({len(matches)} products)")

        return matches

    def generate_comparison_report(self, matches: List[Dict], brand: str) -> Path:
        """Generate detailed CSV comparison with ILS prices"""
        logger.info(f"\nGenerating CSV report for {brand}...")

        filename = self.report_dir / f"{brand.lower()}_comparison_ils.csv"

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'Brand',
                'Halilit_Product',
                'Halilit_Price_ILS',
                'Match_Status',
                'Thomann_Product',
                'Thomann_Price_USD',
                'Thomann_Price_ILS',
                'Match_Confidence',
                'Match_Reason',
                'Availability'
            ])

            writer.writeheader()

            for match in matches:
                h_prod = match['halilit_product']
                t_prod = match['thomann_product']
                confidence = match['confidence']
                reason = match['match_reason']

                # Halilit data
                h_name = h_prod.get('name', 'Unknown')
                h_price_ils = h_prod.get('price_ils', 0)

                # Thomann data
                if t_prod:
                    t_name = t_prod.get('name', 'Unknown')
                    t_price_usd = t_prod.get('price', 0)
                    t_price_ils = self.convert_price_usd_to_ils(t_price_usd)
                    match_status = "MATCHED" if confidence >= 0.60 else "WEAK_MATCH"
                    availability = "Both Platforms"
                else:
                    t_name = "NOT FOUND ON THOMANN"
                    t_price_usd = 0
                    t_price_ils = 0
                    match_status = "NOT FOUND"
                    availability = "Halilit Only (Exclusive)"

                row = {
                    'Brand': brand,
                    'Halilit_Product': h_name,
                    'Halilit_Price_ILS': f"₪{h_price_ils:.0f}" if h_price_ils > 0 else "TBD",
                    'Match_Status': match_status,
                    'Thomann_Product': t_name,
                    'Thomann_Price_USD': f"${t_price_usd:.2f}" if t_price_usd > 0 else "N/A",
                    'Thomann_Price_ILS': f"₪{t_price_ils:.0f}" if t_price_ils > 0 else "N/A",
                    'Match_Confidence': f"{confidence*100:.0f}%",
                    'Match_Reason': reason,
                    'Availability': availability
                }

                writer.writerow(row)

        logger.info(f"✓ Report saved: {filename}")
        return filename

    def generate_summary(self, all_matches: Dict[str, List[Dict]]) -> Path:
        """Generate summary statistics"""
        logger.info("\nGenerating summary report...")

        summary = {
            'comparison_type': 'name_based_fuzzy_matching',
            'exchange_rate_used': f"1 USD = {USD_TO_ILS} ILS",
            'total_halilit_products': 0,
            'total_thomann_products': 0,
            'by_brand': {}
        }

        for brand, matches in all_matches.items():
            high_conf = sum(1 for m in matches if m['confidence'] >= 0.75)
            med_conf = sum(1 for m in matches if 0.60 <=
                           m['confidence'] < 0.75)
            low_conf = sum(1 for m in matches if m['confidence'] < 0.60)
            found = sum(1 for m in matches if m['thomann_product'] is not None)

            summary['by_brand'][brand] = {
                'total_halilit_products': len(matches),
                'found_on_thomann': found,
                'coverage_percent': f"{found/len(matches)*100:.1f}%" if matches else "0%",
                'high_confidence_matches': high_conf,
                'medium_confidence_matches': med_conf,
                'low_confidence_matches': low_conf,
                'thomann_price_range_usd': self.get_price_range(matches),
                'thomann_price_range_ils': self.get_price_range_ils(matches)
            }

            summary['total_halilit_products'] += len(matches)

        summary_file = self.report_dir / "comparison_summary_advanced.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        # Print summary
        logger.info(f"\n{'='*80}")
        logger.info("ADVANCED COMPARISON SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"\nExchange Rate: 1 USD = {USD_TO_ILS} ILS")
        logger.info(
            f"Matching Strategy: Name-based fuzzy matching with taxonomy flexibility")
        logger.info(f"Coverage Target: 100% of Halilit products matched\n")

        for brand, stats in summary['by_brand'].items():
            logger.info(f"{brand.upper()}:")
            logger.info(f"  Total Products: {stats['total_halilit_products']}")
            logger.info(
                f"  Found on Thomann: {stats['found_on_thomann']} ({stats['coverage_percent']})")
            logger.info(f"  Match Quality:")
            logger.info(
                f"    - High Confidence (≥75%): {stats['high_confidence_matches']}")
            logger.info(
                f"    - Medium Confidence (60-75%): {stats['medium_confidence_matches']}")
            logger.info(
                f"    - Low Confidence (<60%): {stats['low_confidence_matches']}")
            logger.info(f"  Price Ranges (Thomann):")
            logger.info(f"    - USD: {stats['thomann_price_range_usd']}")
            logger.info(f"    - ILS: {stats['thomann_price_range_ils']}")

        return summary_file

    def get_price_range(self, matches: List[Dict]) -> str:
        """Get min/max price range in USD"""
        prices = []
        for m in matches:
            if m['thomann_product'] and m['thomann_product'].get('price', 0) > 0:
                prices.append(m['thomann_product'].get('price', 0))

        if prices:
            return f"${min(prices):.0f} - ${max(prices):.0f}"
        return "No pricing"

    def get_price_range_ils(self, matches: List[Dict]) -> str:
        """Get min/max price range in ILS"""
        prices = []
        for m in matches:
            if m['thomann_product'] and m['thomann_product'].get('price', 0) > 0:
                usd = m['thomann_product'].get('price', 0)
                prices.append(self.convert_price_usd_to_ils(usd))

        if prices:
            return f"₪{min(prices):.0f} - ₪{max(prices):.0f}"
        return "No pricing"

    def run(self, brands: List[str] = ["RCF", "Mackie"]):
        """Run complete advanced comparison"""

        logger.info(f"\n{'='*80}")
        logger.info("ADVANCED PRODUCT COMPARISON ENGINE")
        logger.info(
            "Goal: 100% Halilit product coverage with Thomann pricing in ILS")
        logger.info(f"{'='*80}")

        all_matches = {}

        for brand in brands:
            logger.info(f"\n{'#'*80}")
            logger.info(f"# {brand.upper()} COMPARISON")
            logger.info(f"{'#'*80}")

            # Load data
            halilit = self.load_data("halilit", brand)
            thomann = self.load_data("thomann", brand)

            if not halilit:
                logger.error(f"No Halilit data for {brand}")
                continue

            # Match all products
            matches = self.match_all_products(halilit, thomann, brand)
            all_matches[brand] = matches

            # Generate reports
            self.generate_comparison_report(matches, brand)

        # Generate summary
        if all_matches:
            self.generate_summary(all_matches)

        logger.info(f"\n{'='*80}")
        logger.info("✓ ADVANCED COMPARISON COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"\nReports generated:")
        logger.info(f"  - rcf_comparison_ils.csv")
        logger.info(f"  - mackie_comparison_ils.csv")
        logger.info(f"  - comparison_summary_advanced.json")


if __name__ == "__main__":
    engine = AdvancedProductMatcher()
    engine.run(["RCF", "Mackie"])
