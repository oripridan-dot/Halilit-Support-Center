"""
SpectrumDataPipeline Skill

Enhanced data pipeline for the Spectrum Screen:
- Deep scraping with multi-source coordination
- Price-based track organization
- Brand hierarchy enforcement
- Data source tracking (Halilit primary, official+reviews secondary)
"""

import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from .base_skill import BaseSkill

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SpectrumDataPipeline")


class SpectrumDataPipeline(BaseSkill):
    """
    Master pipeline for Spectrum Screen data aggregation.
    Orchestrates scraping, validation, and enrichment.
    """

    def __init__(self):
        super().__init__()
        self.name = "SpectrumDataPipeline"
        self.version = "5.3.0"

        # Price tier boundaries (in ILS)
        self.price_tiers = {
            'entry': (0, 500),
            'mid': (500, 1500),
            'pro': (1500, 4000),
            'flagship': (4000, float('inf'))
        }

        # Data source priority (for conflict resolution)
        self.source_priority = {
            'halilit_direct': 100,  # Highest: from Halilit commerce
            'official_specs': 80,   # Official manufacturer specs
            # Trusted review sites (Thomann, Sweetwater)
            'trusted_reviews': 70,
            'marketplace': 50,      # Generic marketplace
            'cache': 10             # Cached/legacy
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Execute full spectrum data pipeline.

        Context requires:
        - brand: str - Brand to process
        - include_enrichment: bool - Fetch from official/review sources
        - force_refresh: bool - Skip cache
        """
        valid, error = self.validate_context(context, ['brand'])
        if not valid:
            return False, error

        brand = context['brand']
        include_enrichment = context.get('include_enrichment', True)
        force_refresh = context.get('force_refresh', False)

        logger.info(f"🌌 [SpectrumDataPipeline] Processing {brand}...")

        try:
            # Phase 1: Scrape Halilit (primary source - prices & product numbers)
            halilit_data = self._scrape_halilit(brand, force_refresh)
            if not halilit_data:
                return False, f"Failed to scrape Halilit data for {brand}"

            logger.info(
                f"✅ Phase 1: Scraped {len(halilit_data)} items from Halilit")

            # Phase 2: Organize by price spectrum
            spectrum_tracks = self._organize_by_price_spectrum(halilit_data)
            logger.info(
                f"✅ Phase 2: Organized into {len(spectrum_tracks)} price tracks")

            # Phase 3: Enrich with official specs and reviews (if enabled)
            enriched_data = spectrum_tracks
            if include_enrichment:
                enriched_data = self._enrich_with_official_sources(
                    spectrum_tracks, brand)
                logger.info(
                    f"✅ Phase 3: Enriched with official/review sources")

            # Phase 4: Build brand hierarchy
            brand_hierarchy = self._build_brand_hierarchy(enriched_data, brand)
            logger.info(f"✅ Phase 4: Built brand hierarchy")

            # Phase 5: Attach data provenance
            final_payload = self._attach_provenance(brand_hierarchy, brand)

            return True, {
                'brand': brand,
                'timestamp': datetime.utcnow().isoformat(),
                'total_products': sum(
                    len(track['products']) for track in final_payload['tracks']
                ),
                'tracks': final_payload['tracks'],
                'metadata': final_payload['metadata']
            }

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            return False, f"Pipeline error: {str(e)}"

    def _scrape_halilit(self, brand: str, force_refresh: bool) -> List[Dict]:
        """
        Phase 1: Scrape Halilit for this brand.
        Returns products with:
        - halilit_id (product number)
        - name
        - price_il (Israel mainland price)
        - price_eilat (Eilat discount price)
        - source: 'halilit_direct'
        """
        logger.info(f"  Scraping Halilit for {brand}...")

        # In production, this would:
        # 1. Call Halilit API or web scraper
        # 2. Extract product number, name, prices
        # 3. Cache results

        # For now, simulate from data/brands structure
        halilit_products = []

        # Mock implementation - in production, load from actual Halilit
        halilit_products = [
            {
                'halilit_id': f'{brand.upper()}_001',
                'name': f'{brand} Professional Series X',
                'category': 'Keyboards',
                'price_il': 8500.00,
                'price_eilat': 7225.00,
                'source': 'halilit_direct',
                'source_confidence': 0.98,
                'image_url': None,
                'stock_status': 'in_stock',
                'source_url': f'https://halilit.com/{brand.lower()}_001'
            },
            {
                'halilit_id': f'{brand.upper()}_002',
                'name': f'{brand} Entry Model Y',
                'category': 'Keyboards',
                'price_il': 2500.00,
                'price_eilat': 2125.00,
                'source': 'halilit_direct',
                'source_confidence': 0.98,
                'image_url': None,
                'stock_status': 'in_stock',
                'source_url': f'https://halilit.com/{brand.lower()}_002'
            }
        ]

        logger.info(
            f"  Found {len(halilit_products)} Halilit items for {brand}")
        return halilit_products

    def _organize_by_price_spectrum(self, products: List[Dict]) -> List[Dict]:
        """
        Phase 2: Organize products into price-based tracks.
        Each track represents a price tier with products sorted by price.
        """
        tracks = {}

        for product in products:
            price = product.get('price_il', 0)

            # Determine which tier this price falls into
            tier = self._determine_price_tier(price)

            if tier not in tracks:
                tracks[tier] = {
                    'tier': tier,
                    'tier_label': tier.replace('_', ' ').title(),
                    'price_range': self.price_tiers[tier],
                    'products': []
                }

            tracks[tier]['products'].append(product)

        # Sort products within each track by price
        for tier in tracks:
            tracks[tier]['products'].sort(key=lambda p: p.get('price_il', 0))

        # Return as ordered list (entry -> mid -> pro -> flagship)
        tier_order = ['entry', 'mid', 'pro', 'flagship']
        return [tracks[t] for t in tier_order if t in tracks]

    def _determine_price_tier(self, price: float) -> str:
        """Determine which tier a price falls into."""
        for tier, (min_p, max_p) in self.price_tiers.items():
            if min_p <= price < max_p:
                return tier
        return 'flagship'

    def _enrich_with_official_sources(self, tracks: List[Dict], brand: str) -> List[Dict]:
        """
        Phase 3: Enrich product data with:
        - Official manufacturer specifications
        - Trusted review site data (Thomann, Sweetwater, etc.)
        - Images from official sources
        """
        logger.info(f"  Enriching with official/review sources for {brand}...")

        enriched_tracks = []

        for track in tracks:
            enriched_track = track.copy()
            enriched_track['products'] = []

            for product in track['products']:
                enriched_product = product.copy()

                # Enrich with official specs
                official_specs = self._fetch_official_specs(
                    brand, product.get('name'))
                if official_specs:
                    enriched_product['official_specs'] = official_specs
                    enriched_product['sources'].append('official_specs')

                # Enrich with review data
                review_data = self._fetch_trusted_reviews(
                    brand, product.get('name'))
                if review_data:
                    enriched_product['review_data'] = review_data
                    enriched_product['sources'].append('trusted_reviews')

                # Ensure sources array exists
                if 'sources' not in enriched_product:
                    enriched_product['sources'] = []
                enriched_product['sources'].append(
                    product.get('source', 'halilit_direct'))

                enriched_track['products'].append(enriched_product)

            enriched_tracks.append(enriched_track)

        return enriched_tracks

    def _fetch_official_specs(self, brand: str, product_name: str) -> Optional[Dict]:
        """
        Fetch official specs from manufacturer website.
        Returns specs dict or None if not found.
        """
        # In production:
        # 1. Query manufacturer API (e.g., Nord, Moog, Roland official APIs)
        # 2. Extract: features, weight, dimensions, connectivity, power
        # 3. Cache results

        return {
            'source': 'official_manufacturer',
            'polyphony': 64,
            'connectivity': ['MIDI', 'USB', 'Audio Out'],
            'power': '230V AC',
            'warranty': '2 years'
        }

    def _fetch_trusted_reviews(self, brand: str, product_name: str) -> Optional[Dict]:
        """
        Fetch aggregated review data from trusted sources.
        Includes: ratings, pros/cons, expert reviews.
        """
        # In production:
        # 1. Query Thomann, Sweetwater, Reverb, Gearspace APIs
        # 2. Extract: average rating, review count, pros/cons tags
        # 3. Aggregate scores across sources

        return {
            'sources': ['thomann', 'sweetwater'],
            'average_rating': 4.7,
            'review_count': 45,
            'pros': ['Great build quality', 'Excellent sound'],
            'cons': ['Expensive', 'Heavy']
        }

    def _build_brand_hierarchy(self, tracks: List[Dict], brand: str) -> Dict:
        """
        Phase 4: Build brand hierarchy with products organized by:
        - Brand name
        - Product family (if detectable)
        - Price tier
        """
        return {
            'brand': brand,
            'total_products': sum(len(t['products']) for t in tracks),
            'price_distribution': {
                t['tier']: len(t['products']) for t in tracks
            },
            'tracks': tracks
        }

    def _attach_provenance(self, hierarchy: Dict, brand: str) -> Dict:
        """
        Phase 5: Attach data provenance/lineage to each product.
        Enables users to see where each piece of data came from.
        """
        metadata = {
            'pipeline_version': self.version,
            'processed_at': datetime.utcnow().isoformat(),
            'brand': brand,
            'data_sources': {
                'halilit_direct': 'Primary source for prices and product numbers',
                'official_specs': 'Manufacturer specifications',
                'trusted_reviews': 'Aggregated reviews from Thomann, Sweetwater, etc.'
            },
            'validation_stats': {
                'total_processed': sum(len(t['products']) for t in hierarchy['tracks']),
                'approved': 0,
                'rejected': 0
            }
        }

        # Attach source badges to products
        for track in hierarchy['tracks']:
            for product in track['products']:
                product['data_provenance'] = {
                    'halilit': {
                        'id': product.get('halilit_id'),
                        'price': product.get('price_il'),
                        'source_url': product.get('source_url'),
                        'confidence': product.get('source_confidence', 0.95)
                    },
                    'official': {
                        'specs': product.get('official_specs'),
                        'image_url': product.get('official_image_url')
                    },
                    'reviews': {
                        'data': product.get('review_data'),
                        'sources': product.get('review_sources', [])
                    }
                }

        return {
            'tracks': hierarchy['tracks'],
            'metadata': metadata
        }


class PriceSpectrumAnalyzer(BaseSkill):
    """
    Analyzes price distribution and organizes products into visual tracks.
    Handles price normalization, outlier detection, and spectrum boundaries.
    """

    def __init__(self):
        super().__init__()
        self.name = "PriceSpectrumAnalyzer"

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Analyze price spectrum for a set of products.

        Context requires:
        - products: List[Dict] - Products to analyze
        """
        valid, error = self.validate_context(context, ['products'])
        if not valid:
            return False, error

        products = context['products']

        try:
            # Calculate statistics
            prices = [p.get('price_il', 0)
                      for p in products if p.get('price_il')]
            if not prices:
                return False, "No valid prices found"

            stats = self._calculate_spectrum_stats(prices)

            # Detect price outliers
            outliers = self._detect_outliers(prices, stats)

            # Calculate optimal track boundaries
            boundaries = self._calculate_track_boundaries(prices, stats)

            return True, {
                'stats': stats,
                'outliers': outliers,
                'boundaries': boundaries,
                'track_count': len(boundaries)
            }

        except Exception as e:
            return False, f"Analysis failed: {str(e)}"

    def _calculate_spectrum_stats(self, prices: List[float]) -> Dict:
        """Calculate price statistics."""
        prices.sort()
        n = len(prices)

        return {
            'min': prices[0],
            'max': prices[-1],
            'mean': sum(prices) / n,
            'median': prices[n // 2],
            'count': n
        }

    def _detect_outliers(self, prices: List[float], stats: Dict) -> List[float]:
        """Detect price outliers using IQR method."""
        prices.sort()
        q1_idx = len(prices) // 4
        q3_idx = (3 * len(prices)) // 4

        q1 = prices[q1_idx] if q1_idx < len(prices) else prices[0]
        q3 = prices[q3_idx] if q3_idx < len(prices) else prices[-1]
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        return [p for p in prices if p < lower_bound or p > upper_bound]

    def _calculate_track_boundaries(self, prices: List[float], stats: Dict) -> List[Tuple[float, float]]:
        """Calculate optimal boundaries for price tracks."""
        # Simplified: use quartile-based boundaries
        prices.sort()
        n = len(prices)

        boundaries = []
        step = n // 4

        for i in range(0, n, step):
            if i + step < n:
                boundaries.append((prices[i], prices[i + step - 1]))

        return boundaries
