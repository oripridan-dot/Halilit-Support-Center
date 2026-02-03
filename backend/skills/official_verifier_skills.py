"""
OfficialVerifier Agent Skills

Capabilities:
- Brand matching against taxonomy
- Official image fetching and validation
- Product enrichment with manufacturer specs
- Data completeness verification
"""

from typing import Dict, Any, Tuple
from .base_skill import BaseSkill

class BrandMatcherSkill(BaseSkill):
    """
    Matches extracted brand names against official taxonomy.
    Handles brand name variations and aliases.
    """

    def __init__(self):
        super().__init__()
        self.brand_aliases = {
            'Nord': ['nord', 'Nord Keyboards', 'North'],
            'Roland': ['roland', 'Roland Corp', 'ROLAND'],
            'Yamaha': ['yamaha', 'Yamaha Corp', 'YAMAHA'],
            'Korg': ['korg', 'Korg Inc', 'KORG'],
            'Moog': ['moog', 'Moog Music', 'MOOG'],
            'Shure': ['shure', 'Shure Inc', 'SHURE'],
            'Focal': ['focal', 'Focal Professional', 'FOCAL'],
            'Neumann': ['neumann', 'Neumann Berlin', 'NEUMANN'],
            'Rode': ['rode', 'Rode Microphones', 'RODE'],
            'Universal Audio': ['ua', 'universal audio', 'UAD', 'UNIVERSAL AUDIO']
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Match brand name against taxonomy.

        Context requires:
        - brand_name: str - Brand name to match
        - taxonomy: List[str] - Official taxonomy list
        - strict_match: bool (optional) - Require exact match
        """
        valid, error = self.validate_context(
            context, ['brand_name', 'taxonomy'])
        if not valid:
            return False, error

        brand_name = context['brand_name'].strip()
        taxonomy = context['taxonomy']
        strict_match = context.get('strict_match', False)

        self.logger.info(f"🔤 Matching brand: {brand_name}")

        try:
            # Try exact match first
            exact_match = brand_name in taxonomy
            if exact_match:
                self.logger.info(f"  ✅ Exact match found: {brand_name}")
                return True, {
                    'matched_brand': brand_name,
                    'match_type': 'exact',
                    'confidence': 1.0,
                    'is_valid': True
                }

            if strict_match:
                return False, f"Brand '{brand_name}' not found in taxonomy"

            # Try alias matching
            for official_name, aliases in self.brand_aliases.items():
                if any(alias.lower() == brand_name.lower() for alias in aliases):
                    self.logger.info(
                        f"  ⚠️  Alias match: {brand_name} -> {official_name}")
                    return True, {
                        'matched_brand': official_name,
                        'original_brand': brand_name,
                        'match_type': 'alias',
                        'confidence': 0.95,
                        'is_valid': True
                    }

            # Try fuzzy matching (simple edit distance)
            best_match = self._fuzzy_match(brand_name, taxonomy)
            if best_match and best_match[1] > 0.80:
                self.logger.info(
                    f"  💭 Fuzzy match: {brand_name} -> {best_match[0]}")
                return True, {
                    'matched_brand': best_match[0],
                    'original_brand': brand_name,
                    'match_type': 'fuzzy',
                    'confidence': best_match[1],
                    'is_valid': best_match[1] > 0.80
                }

            # No match found
            return False, f"Brand '{brand_name}' could not be matched to taxonomy"

        except Exception as e:
            error_msg = f"Brand matching failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def _fuzzy_match(self, brand: str, taxonomy: List[str]) -> Optional[Tuple[str, float]]:
        """Simple fuzzy matching using character overlap"""
        brand_lower = brand.lower()
        best_match = None
        best_score = 0

        for tax_brand in taxonomy:
            tax_lower = tax_brand.lower()
            # Simple character set overlap
            common_chars = len(set(brand_lower) & set(tax_lower))
            all_chars = len(set(brand_lower) | set(tax_lower))
            score = common_chars / all_chars if all_chars > 0 else 0

            if score > best_score:
                best_score = score
                best_match = tax_brand

        return (best_match, best_score) if best_score > 0.5 else None

class ImageFetcherSkill(BaseSkill):
    """
    Fetches official product images from brand sources.
    Validates image quality and format.
    """

    def __init__(self):
        super().__init__()
        self.brand_image_sources = {
            'Nord': 'https://www.nordkeyboards.com/products/',
            'Roland': 'https://www.roland.com/products/',
            'Yamaha': 'https://www.yamaha.com/en/products/',
            'Korg': 'https://www.korg.com/us/products/',
            'Moog': 'https://www.moogmusic.com/products/',
            'Shure': 'https://pubs.shure.com/product/',
            'Focal': 'https://www.focal.com/en/products/',
            'Neumann': 'https://www.neumann.com/en-US/products/',
            'Rode': 'https://en.rode.com/products/',
            'Universal Audio': 'https://www.uaudio.com/uad-plugins/'
        }
        self.valid_image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Fetch official image for product.

        Context requires:
        - product_name: str - Product name
        - brand: str - Brand name
        - fallback_url: str (optional) - URL to fall back to
        """
        valid, error = self.validate_context(
            context, ['product_name', 'brand'])
        if not valid:
            return False, error

        product_name = context['product_name']
        brand = context['brand']
        fallback_url = context.get('fallback_url')

        self.logger.info(
            f"🖼️  Fetching image for: {brand} {product_name}")

        try:
            # In production, this would:
            # 1. Search brand's product page
            # 2. Scrape/API fetch official image
            # 3. Validate image quality
            # For demo, simulate success

            if brand in self.brand_image_sources:
                image_url = self._construct_image_url(
                    brand, product_name)
                self.logger.info(f"  ✅ Found official image")
                return True, {
                    'image_url': image_url,
                    'source': f'official_{brand.lower()}',
                    'quality': 'high',
                    'confidence': 0.98,
                    'image_type': 'official'
                }
            elif fallback_url:
                self.logger.info(f"  ⚠️  Using fallback image")
                return True, {
                    'image_url': fallback_url,
                    'source': 'fallback',
                    'quality': 'medium',
                    'confidence': 0.75,
                    'image_type': 'fallback'
                }
            else:
                return False, f"No image source found for {brand}"

        except Exception as e:
            error_msg = f"Image fetching failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def _construct_image_url(self, brand: str, product_name: str) -> str:
        """Construct URL for product image (simplified)"""
        base_url = self.brand_image_sources.get(brand, '')
        product_slug = product_name.lower().replace(' ', '-')
        return f"{base_url}{product_slug}/image.jpg"

class SpecificationEnricherSkill(BaseSkill):
    """
    Enriches product data with official manufacturer specifications.
    Fetches technical details from brand databases.
    """

    def __init__(self):
        super().__init__()
        self.spec_categories = {
            'keyboards': ['keys', 'voices', 'effects', 'connectivity', 'warranty'],
            'microphones': ['frequency_range', 'impedance', 'sensitivity', 'polar_pattern'],
            'audio_interfaces': ['channels', 'sample_rate', 'connectivity', 'latency'],
            'synthesizers': ['oscillators', 'filters', 'envelopes', 'effects']
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Enrich product with official specifications.

        Context requires:
        - product_data: dict - Product to enrich
        - product_category: str (optional) - Category hint
        """
        valid, error = self.validate_context(context, ['product_data'])
        if not valid:
            return False, error

        product_data = context['product_data']
        category = context.get('product_category', 'unknown')

        self.logger.info(
            f"📊 Enriching specs for: {product_data.get('name')}")

        try:
            specs = self._fetch_specs(
                product_data.get('brand'), product_data.get('name'), category)

            enriched = {
                **product_data,
                'specifications': specs,
                'spec_confidence': 0.92 if specs else 0.0,
                'enriched': True,
                'enrichment_timestamp': 'now'
            }

            self.logger.info(
                f"  ✅ Added {len(specs) if specs else 0} spec fields")
            return True, enriched

        except Exception as e:
            error_msg = f"Specification enrichment failed: {str(e)}"
            self.logger.error(error_msg)
            # Return product as-is on spec enrichment failure
            return True, {
                **product_data,
                'specifications': {},
                'spec_confidence': 0.0,
                'enriched': False
            }

    def _fetch_specs(self, brand: str, product_name: str, category: str) -> Dict:
        """Fetch specifications (simulated)"""
        # In production: API/DB lookup, web scraping, etc.
        return {
            'manufacturer': brand,
            'model': product_name,
            'warranty_years': 2,
            'connectivity': 'USB, MIDI',
            'power_consumption': 'Low',
            'certified': True
        }

class DataCompletenessCheckerSkill(BaseSkill):
    """
    Verifies product data completeness against golden record schema.
    Identifies and reports missing critical fields.
    """

    def __init__(self):
        super().__init__()
        self.critical_fields = {
            'name', 'brand', 'price_il', 'price_eilat',
            'image_url', 'source_url'
        }
        self.optional_fields = {
            'specifications', 'warranty', 'color', 'stock_status'
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Check product data completeness.

        Context requires:
        - product_data: dict - Product to check
        - schema: dict (optional) - Custom schema to validate against
        """
        valid, error = self.validate_context(context, ['product_data'])
        if not valid:
            return False, error

        product_data = context['product_data']
        schema = context.get('schema', {})

        self.logger.info(
            f"✔️  Checking completeness for: {product_data.get('name')}")

        try:
            fields_present = set(product_data.keys())
            critical_present = self.critical_fields & fields_present
            optional_present = self.optional_fields & fields_present
            critical_missing = self.critical_fields - fields_present

            completeness_score = (
                len(critical_present) / len(self.critical_fields) * 0.7 +
                len(optional_present) / len(self.optional_fields) * 0.3
            ) if self.critical_fields else 0

            is_complete = len(critical_missing) == 0

            self.logger.info(
                f"  Completeness: {completeness_score:.1%} ({'Complete' if is_complete else 'Incomplete'})")

            return True, {
                'is_complete': is_complete,
                'completeness_score': completeness_score,
                'fields_present': len(fields_present),
                'critical_present': len(critical_present),
                'critical_required': len(self.critical_fields),
                'critical_missing': list(critical_missing),
                'optional_present': len(optional_present),
                'can_publish': is_complete and completeness_score >= 0.65
            }

        except Exception as e:
            error_msg = f"Completeness check failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
