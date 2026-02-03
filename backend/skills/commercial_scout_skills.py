"""
CommercialScout Agent Skills

Capabilities:
- Source harvesting and validation
- Price extraction and normalization
- Product data parsing from various sources
- Confidence scoring for raw data
"""

import re

class SourceHarvesterSkill(BaseSkill):
    """
    Harvests product data from specified sources (e.g., Halilit.com)
    Validates source accessibility and data quality.
    """

    def __init__(self):
        super().__init__()
        self.supported_sources = ['halilit', 'internal_db', 'api_endpoint']

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Harvest product data from specified source.

        Context requires:
        - source_url: str - URL or source identifier
        - brand: str - Brand to search for
        - max_results: int (optional) - Max results to return (default: 10)
        """
        valid, error = self.validate_context(
            context, ['source_url', 'brand'])
        if not valid:
            return False, error

        source_url = context['source_url']
        brand = context['brand']
        max_results = context.get('max_results', 10)

        self.logger.info(f"🔍 Harvesting from {source_url} for brand: {brand}")

        try:
            # In production, this would make actual HTTP requests or DB queries
            # For now, simulate harvesting
            products = self._simulate_harvest(brand, max_results)

            if not products:
                return False, f"No products found for brand: {brand}"

            self.logger.info(
                f"✅ Harvested {len(products)} products for {brand}")
            return True, {
                'source': source_url,
                'brand': brand,
                'products': products,
                'harvest_count': len(products),
                'quality_score': 0.95
            }

        except Exception as e:
            error_msg = f"Harvest failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def _simulate_harvest(self, brand: str, max_results: int) -> List[Dict]:
        """Simulate harvesting product data (real impl would call APIs)"""
        # This is a mock implementation
        return [
            {
                'raw_id': f'{brand}_001',
                'name': f'{brand} Pro Series Model X',
                'brand': brand,
                'price_raw_il': '18500',
                'price_raw_eilat': '15811',
                'source_page': f'https://halilit.com/products/{brand.lower()}_001',
                'html_extracted': True
            }
        ]

class PriceExtractorSkill(BaseSkill):
    """
    Extracts and normalizes prices from raw product data.
    Handles multiple price formats and currency conversions.
    """

    def __init__(self):
        super().__init__()
        self.price_patterns = {
            'decimal_comma': r'(\d+),(\d+)',  # 1,234.56
            'decimal_dot': r'(\d+)\.(\d+)',   # 1.234,56
            'integer': r'(\d+)'                # 1234
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Extract and normalize prices from product data.

        Context requires:
        - product_data: dict - Raw product data with price fields
        - currency: str - Target currency (default: 'ILS')
        """
        valid, error = self.validate_context(context, ['product_data'])
        if not valid:
            return False, error

        product_data = context['product_data']
        currency = context.get('currency', 'ILS')

        self.logger.info(f"💰 Extracting prices for {product_data.get('name')}")

        try:
            extracted_prices = {}

            # Extract IL price
            if 'price_raw_il' in product_data:
                il_price = self._extract_price(product_data['price_raw_il'])
                if il_price is not None:
                    extracted_prices['price_il'] = il_price
                    self.logger.info(f"  IL: ₪{il_price:,.2f}")

            # Extract Eilat price (duty-free zone)
            if 'price_raw_eilat' in product_data:
                eilat_price = self._extract_price(
                    product_data['price_raw_eilat'])
                if eilat_price is not None:
                    extracted_prices['price_eilat'] = eilat_price
                    self.logger.info(f"  Eilat: ₪{eilat_price:,.2f}")

            if not extracted_prices:
                return False, "No valid prices found in product data"

            # Verify price ratio consistency
            ratio_valid = self._validate_price_ratio(extracted_prices)
            confidence = 0.99 if ratio_valid else 0.75

            return True, {
                'prices': extracted_prices,
                'currency': currency,
                'confidence': confidence,
                'ratio_valid': ratio_valid
            }

        except Exception as e:
            error_msg = f"Price extraction failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def _extract_price(self, price_str: str) -> Optional[float]:
        """Extract numeric price from string"""
        if not price_str:
            return None

        # Remove common formatting
        cleaned = price_str.replace('₪', '').replace('$', '').strip()

        # Try to extract numeric value
        numbers = re.findall(r'\d+[.,]\d+|\d+', cleaned)
        if numbers:
            try:
                # Assume first match is the main price
                price_str_clean = numbers[0].replace(',', '.')
                return float(price_str_clean)
            except ValueError:
                return None
        return None

    def _validate_price_ratio(self, prices: Dict[str, float]) -> bool:
        """
        Validate that Eilat price is appropriately lower than IL price (~17-20% discount).
        """
        if 'price_il' not in prices or 'price_eilat' not in prices:
            return True  # Can't validate if both prices missing

        il_price = prices['price_il']
        eilat_price = prices['price_eilat']

        if il_price <= 0:
            return False

        ratio = eilat_price / il_price
        # Eilat should be ~17% cheaper (ratio ~0.83)
        return 0.75 < ratio < 0.95  # Allow 5-25% discount

class DataQualityAssessorSkill(BaseSkill):
    """
    Assesses the quality and completeness of harvested product data.
    Scores data reliability for downstream processing.
    """

    def __init__(self):
        super().__init__()
        self.required_fields = {'name', 'brand', 'price_il', 'price_eilat'}
        self.quality_weights = {
            'required_fields': 0.4,
            'source_reliability': 0.3,
            'data_freshness': 0.2,
            'duplicate_likelihood': 0.1
        }

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Assess quality of harvested product data.

        Context requires:
        - product_data: dict - Product data to assess
        - source_reliability: float (optional) - 0-1 reliability score
        """
        valid, error = self.validate_context(context, ['product_data'])
        if not valid:
            return False, error

        product_data = context['product_data']
        source_reliability = context.get('source_reliability', 0.9)

        self.logger.info(
            f"🔎 Assessing quality for: {product_data.get('name')}")

        try:
            # Check required fields
            present_fields = set(product_data.keys())
            required_present = self.required_fields & present_fields
            fields_score = len(required_present) / len(self.required_fields)

            # Overall quality score
            overall_score = (
                fields_score * self.quality_weights['required_fields'] +
                source_reliability * self.quality_weights['source_reliability'] +
                0.8 * self.quality_weights['data_freshness'] +
                0.9 * self.quality_weights['duplicate_likelihood']
            )

            # Determine tier
            if overall_score >= 0.90:
                tier = 'HIGH'
            elif overall_score >= 0.75:
                tier = 'MEDIUM'
            else:
                tier = 'LOW'

            issues = []
            for required_field in self.required_fields:
                if required_field not in product_data:
                    issues.append(f"Missing required field: {required_field}")

            self.logger.info(
                f"  Quality: {tier} ({overall_score:.1%})")

            return True, {
                'quality_score': overall_score,
                'tier': tier,
                'issues': issues,
                'fields_present': len(required_present),
                'fields_required': len(self.required_fields),
                'is_usable': overall_score >= 0.70
            }

        except Exception as e:
            error_msg = f"Quality assessment failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

class DuplicateDetectorSkill(BaseSkill):
    """
    Detects duplicate or near-duplicate products in harvested data.
    Prevents duplicate entries from polluting the catalog.
    """

    def __init__(self):
        super().__init__()
        self.similarity_threshold = 0.85

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Detect duplicates in product list.

        Context requires:
        - products: List[dict] - List of products to check
        - compare_against: List[dict] (optional) - Golden record to compare
        """
        valid, error = self.validate_context(context, ['products'])
        if not valid:
            return False, error

        products = context['products']
        compare_against = context.get('compare_against', [])

        self.logger.info(f"🔄 Checking {len(products)} products for duplicates")

        try:
            duplicates = []
            unique_products = []

            # Check for duplicates within the products list
            for i, product in enumerate(products):
                is_duplicate = False

                for j, other in enumerate(products[i+1:], start=i+1):
                    if self._are_similar(product, other):
                        is_duplicate = True
                        duplicates.append({
                            'index1': i,
                            'index2': j,
                            'product1': product.get('name'),
                            'product2': other.get('name'),
                            'similarity': 0.92
                        })

                # Check against golden record if provided
                if compare_against:
                    for golden in compare_against:
                        if self._are_similar(product, golden):
                            is_duplicate = True

                if not is_duplicate:
                    unique_products.append(product)

            self.logger.info(
                f"  Duplicates found: {len(duplicates)}")
            self.logger.info(
                f"  Unique products: {len(unique_products)}")

            return True, {
                'total_products': len(products),
                'unique_count': len(unique_products),
                'duplicate_count': len(duplicates),
                'duplicates': duplicates,
                'unique_products': unique_products,
                'quality_estimate': (len(unique_products) / len(products)) if products else 0
            }

        except Exception as e:
            error_msg = f"Duplicate detection failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def _are_similar(self, product1: Dict, product2: Dict) -> bool:
        """Simple similarity check based on name and price"""
        name1 = (product1.get('name') or '').lower()
        name2 = (product2.get('name') or '').lower()

        # Check name similarity
        if name1 and name2:
            common_words = len(set(name1.split()) & set(name2.split()))
            total_words = len(set(name1.split()) | set(name2.split()))
            name_similarity = common_words / total_words if total_words > 0 else 0

            # Check price similarity
            price1 = product1.get('price_il', 0)
            price2 = product2.get('price_il', 0)
            price_diff = abs(price1 - price2) / max(price1, price2, 1)
            price_similar = price_diff < 0.05  # Within 5%

            return name_similarity > 0.7 and price_similar

        return False
