"""
Trinity Swarm Agent Workflows

Each agent has its own workflow optimized for its role:
1. CommercialScout: Harvest -> Parse -> Quality Check -> Deduplicate
2. OfficialVerifier: Match -> Enrich -> Validate Completeness
3. ExternalValidator: Audit -> Risk Assess -> Validate Consistency -> Report
"""

import logging

from backend.skills.commercial_scout_skills import (
    SourceHarvesterSkill, PriceExtractorSkill,
    DataQualityAssessorSkill, DuplicateDetectorSkill
)
from backend.skills.official_verifier_skills import (
    BrandMatcherSkill, ImageFetcherSkill,
    SpecificationEnricherSkill, DataCompletenessCheckerSkill
)
    ComplianceAuditorSkill, RiskAssessorSkill,
    ConsistencyValidatorSkill, AuditReportGeneratorSkill
)

class WorkflowState(Enum):
    """States in agent workflows"""
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"

class CommercialScoutWorkflow:
    """
    CommercialScout Workflow: HARVEST -> PARSE -> QUALITY -> DEDUPLICATE

    This workflow harvests product data from sources, normalizes prices,
    assesses quality, and detects duplicates.
    """

    def __init__(self):
        self.logger = logging.getLogger("CommercialScoutWorkflow")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - [CommercialScout] %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Skills
        self.harvester = SourceHarvesterSkill()
        self.price_extractor = PriceExtractorSkill()
        self.quality_assessor = DataQualityAssessorSkill()
        self.duplicate_detector = DuplicateDetectorSkill()

        # State tracking
        self.state = WorkflowState.PLANNING
        self.execution_log = []

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute CommercialScout workflow.

        Context requires:
        - source_url: str
        - brand: str
        - max_results: int (optional)
        """
        self.logger.info("🚀 Starting CommercialScout Workflow")
        self.logger.info(f"   Brand: {context.get('brand')}")

        try:
            # STEP 1: HARVEST
            self.state = WorkflowState.EXECUTING
            self.logger.info("📥 STEP 1: Harvesting from source...")

            success, harvest_result = self.harvester.execute(context)
            if not success:
                self.logger.error(f"❌ Harvest failed: {harvest_result}")
                self.state = WorkflowState.FAILED
                return {'success': False, 'error': harvest_result}

            products = harvest_result['products']
            self.logger.info(f"✅ Harvested {len(products)} products")

            # STEP 2: EXTRACT PRICES
            self.logger.info("💰 STEP 2: Extracting and normalizing prices...")
            price_normalized_products = []

            for product in products:
                success, price_result = self.price_extractor.execute({
                    'product_data': product
                })

                if success:
                    product['prices'] = price_result['prices']
                    product['price_confidence'] = price_result['confidence']
                    price_normalized_products.append(product)
                else:
                    self.logger.warning(
                        f"⚠️  Price extraction failed for {product.get('name')}")

            self.logger.info(
                f"✅ Extracted prices for {len(price_normalized_products)} products")

            # STEP 3: QUALITY ASSESSMENT
            self.logger.info("🔎 STEP 3: Assessing data quality...")
            quality_results = []

            for product in price_normalized_products:
                success, quality_result = self.quality_assessor.execute({
                    'product_data': product
                })

                if success and quality_result['is_usable']:
                    product['quality'] = quality_result
                    quality_results.append(product)
                else:
                    self.logger.warning(
                        f"⚠️  Quality check failed: {product.get('name')}")

            self.logger.info(
                f"✅ {len(quality_results)} products passed quality check")

            # STEP 4: DUPLICATE DETECTION
            self.logger.info("🔄 STEP 4: Detecting duplicates...")
            success, dedup_result = self.duplicate_detector.execute({
                'products': quality_results,
                'compare_against': []
            })

            if success:
                final_products = dedup_result['unique_products']
                self.logger.info(
                    f"✅ {len(final_products)} unique products after deduplication")
            else:
                final_products = quality_results

            # STEP 5: VALIDATION
            self.state = WorkflowState.VALIDATING
            self.logger.info("✔️  STEP 5: Final validation...")

            # Validate all products have critical fields
            valid_products = [
                p for p in final_products
                if all(field in p for field in ['name', 'brand', 'prices'])
            ]

            self.logger.info(
                f"✅ {len(valid_products)} products passed final validation")

            # COMPLETION
            self.state = WorkflowState.COMPLETE
            self.logger.info("✨ CommercialScout Workflow COMPLETE")

            return {
                'success': True,
                'workflow': 'CommercialScout',
                'products': valid_products,
                'total_harvested': len(products),
                'total_processed': len(valid_products),
                'quality_metrics': {
                    'harvest_rate': len(products) / max(context.get('max_results', 10), 1),
                    'quality_pass_rate': len(quality_results) / len(products) if products else 0,
                    'dedup_rate': len(final_products) / len(quality_results) if quality_results else 0,
                    'final_valid_rate': len(valid_products) / len(products) if products else 0
                }
            }

        except Exception as e:
            self.state = WorkflowState.FAILED
            self.logger.error(f"❌ Workflow failed: {str(e)}")
            return {'success': False, 'error': str(e)}

class OfficialVerifierWorkflow:
    """
    OfficialVerifier Workflow: MATCH -> ENRICH -> VALIDATE

    This workflow matches products to official brands, enriches with
    manufacturer data, and validates completeness.
    """

    def __init__(self):
        self.logger = logging.getLogger("OfficialVerifierWorkflow")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - [OfficialVerifier] %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Skills
        self.brand_matcher = BrandMatcherSkill()
        self.image_fetcher = ImageFetcherSkill()
        self.spec_enricher = SpecificationEnricherSkill()
        self.completeness_checker = DataCompletenessCheckerSkill()

        self.state = WorkflowState.PLANNING

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute OfficialVerifier workflow.

        Context requires:
        - products: List[dict]
        - taxonomy: List[str]
        """
        self.logger.info("🚀 Starting OfficialVerifier Workflow")
        self.logger.info(f"   Products: {len(context.get('products', []))}")

        try:
            products = context.get('products', [])
            taxonomy = context.get('taxonomy', [])

            if not products:
                return {'success': False, 'error': 'No products provided'}

            # STEP 1: BRAND MATCHING
            self.state = WorkflowState.EXECUTING
            self.logger.info("🔤 STEP 1: Matching brands to taxonomy...")

            brand_matched = []
            for product in products:
                success, match_result = self.brand_matcher.execute({
                    'brand_name': product.get('brand', ''),
                    'taxonomy': taxonomy
                })

                if success:
                    product['brand_match'] = match_result
                    product['verified_brand'] = match_result['matched_brand']
                    brand_matched.append(product)
                else:
                    self.logger.warning(
                        f"⚠️  Brand match failed: {product.get('brand')}")

            self.logger.info(
                f"✅ {len(brand_matched)} products matched to taxonomy")

            # STEP 2: IMAGE FETCHING
            self.logger.info("🖼️  STEP 2: Fetching official images...")

            image_enriched = []
            for product in brand_matched:
                success, image_result = self.image_fetcher.execute({
                    'product_name': product.get('name'),
                    'brand': product.get('verified_brand'),
                    'fallback_url': product.get('image_url')
                })

                if success:
                    product['image_url'] = image_result['image_url']
                    product['image_source'] = image_result['source']
                    product['image_quality'] = image_result['quality']
                    image_enriched.append(product)
                else:
                    self.logger.warning(
                        f"⚠️  Image fetch failed: {product.get('name')}")

            self.logger.info(
                f"✅ Fetched images for {len(image_enriched)} products")

            # STEP 3: SPECIFICATION ENRICHMENT
            self.logger.info("📊 STEP 3: Enriching specifications...")

            spec_enriched = []
            for product in image_enriched:
                success, enriched_data = self.spec_enricher.execute({
                    'product_data': product
                })

                if success:
                    spec_enriched.append(enriched_data)
                else:
                    self.logger.warning(
                        f"⚠️  Spec enrichment failed: {product.get('name')}")

            self.logger.info(
                f"✅ Enriched specifications for {len(spec_enriched)} products")

            # STEP 4: COMPLETENESS VALIDATION
            self.state = WorkflowState.VALIDATING
            self.logger.info("✔️  STEP 4: Validating completeness...")

            complete_products = []
            for product in spec_enriched:
                success, completeness_result = self.completeness_checker.execute({
                    'product_data': product
                })

                if success:
                    product['completeness'] = completeness_result
                    # Accept products if they have completeness >= 65% (relaxed threshold for enriched data)
                    if completeness_result['completeness_score'] >= 0.65:
                        complete_products.append(product)
                    else:
                        self.logger.warning(
                            f"⚠️  Low completeness: {product.get('name')} ({completeness_result['completeness_score']:.1%})")
                else:
                    self.logger.warning(
                        f"⚠️  Completeness check failed: {product.get('name')}")

            self.logger.info(
                f"✅ {len(complete_products)} products are complete")

            # COMPLETION
            self.state = WorkflowState.COMPLETE
            self.logger.info("✨ OfficialVerifier Workflow COMPLETE")

            return {
                'success': True,
                'workflow': 'OfficialVerifier',
                'products': complete_products,
                'total_input': len(products),
                'total_verified': len(complete_products),
                'metrics': {
                    'brand_match_rate': len(brand_matched) / len(products) if products else 0,
                    'image_enrich_rate': len(image_enriched) / len(brand_matched) if brand_matched else 0,
                    'spec_enrich_rate': len(spec_enriched) / len(image_enriched) if image_enriched else 0,
                    'completeness_rate': len(complete_products) / len(spec_enriched) if spec_enriched else 0
                }
            }

        except Exception as e:
            self.state = WorkflowState.FAILED
            self.logger.error(f"❌ Workflow failed: {str(e)}")
            return {'success': False, 'error': str(e)}

class ExternalValidatorWorkflow:
    """
    ExternalValidator Workflow: AUDIT -> RISK -> CONSISTENCY -> REPORT

    This workflow performs comprehensive compliance auditing, risk assessment,
    consistency validation, and generates detailed audit reports.
    """

    def __init__(self):
        self.logger = logging.getLogger("ExternalValidatorWorkflow")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - [ExternalValidator] %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Skills
        self.compliance_auditor = ComplianceAuditorSkill()
        self.risk_assessor = RiskAssessorSkill()
        self.consistency_validator = ConsistencyValidatorSkill()
        self.report_generator = AuditReportGeneratorSkill()

        self.state = WorkflowState.PLANNING

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute ExternalValidator workflow.

        Context requires:
        - products: List[dict]
        - taxonomy: List[str]
        """
        self.logger.info("🚀 Starting ExternalValidator Workflow")
        self.logger.info(f"   Products: {len(context.get('products', []))}")

        try:
            products = context.get('products', [])
            taxonomy = context.get('taxonomy', [])

            if not products:
                return {'success': False, 'error': 'No products provided'}

            approved_products = []
            rejected_products = []
            review_products = []

            # PROCESS EACH PRODUCT
            self.state = WorkflowState.EXECUTING

            for product in products:
                self.logger.info(f"\n📋 Auditing: {product.get('name')}")

                # STEP 1: COMPLIANCE AUDIT
                compliance_success, compliance_result = self.compliance_auditor.execute({
                    'product_data': product,
                    'taxonomy': taxonomy,
                    'audit_level': 'standard'
                })

                if not compliance_success:
                    self.logger.error(
                        f"  ❌ Compliance audit error: {compliance_result}")
                    rejected_products.append(product)
                    continue

                # STEP 2: RISK ASSESSMENT
                risk_success, risk_result = self.risk_assessor.execute({
                    'product_data': product
                })

                if not risk_success:
                    self.logger.error(
                        f"  ❌ Risk assessment error: {risk_result}")
                    review_products.append(product)
                    continue

                # STEP 3: CONSISTENCY VALIDATION
                consistency_success, consistency_result = self.consistency_validator.execute({
                    'product_data': product
                })

                if not consistency_success:
                    self.logger.error(
                        f"  ❌ Consistency check error: {consistency_result}")
                    review_products.append(product)
                    continue

                # STEP 4: GENERATE AUDIT REPORT
                self.state = WorkflowState.VALIDATING

                report_success, audit_report = self.report_generator.execute({
                    'compliance_result': compliance_result,
                    'risk_result': risk_result,
                    'consistency_result': consistency_result,
                    'product_data': product
                })

                if not report_success:
                    self.logger.error(
                        f"  ❌ Report generation error: {audit_report}")
                    review_products.append(product)
                    continue

                # CATEGORIZE PRODUCT
                final_status = audit_report.get('final_status')
                product['audit_report'] = audit_report

                if final_status == 'APPROVED':
                    self.logger.info(f"  ✅ APPROVED")
                    approved_products.append(product)
                elif final_status == 'REJECTED':
                    self.logger.info(f"  🛑 REJECTED")
                    rejected_products.append(product)
                else:
                    self.logger.info(f"  ⚠️  NEEDS REVIEW")
                    review_products.append(product)

            # COMPLETION
            self.state = WorkflowState.COMPLETE
            self.logger.info(f"\n✨ ExternalValidator Workflow COMPLETE")
            self.logger.info(f"  ✅ Approved: {len(approved_products)}")
            self.logger.info(f"  🛑 Rejected: {len(rejected_products)}")
            self.logger.info(f"  ⚠️  Review: {len(review_products)}")

            return {
                'success': True,
                'workflow': 'ExternalValidator',
                'approved': approved_products,
                'rejected': rejected_products,
                'needs_review': review_products,
                'total_audited': len(products),
                'metrics': {
                    'approval_rate': len(approved_products) / len(products) if products else 0,
                    'rejection_rate': len(rejected_products) / len(products) if products else 0,
                    'review_rate': len(review_products) / len(products) if products else 0
                }
            }

        except Exception as e:
            self.state = WorkflowState.FAILED
            self.logger.error(f"❌ Workflow failed: {str(e)}")
            return {'success': False, 'error': str(e)}
