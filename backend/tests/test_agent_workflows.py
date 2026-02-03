"""
Comprehensive Test Suite for Trinity Swarm Agents & Workflows

Tests all skills and workflows to ensure:
- Skills execute without errors
- Workflow states transition correctly
- Output validation and consistency
- Error handling and fallbacks
- Integration between agents

Run: python3 -m pytest backend/tests/test_agent_workflows.py -v
                                                                or: python3 backend/tests/test_agent_workflows.py
"""

from backend.agents.agent_workflows import (
                                                                CommercialScoutWorkflow, OfficialVerifierWorkflow,
                                                                ExternalValidatorWorkflow
)
from backend.skills.external_validator_skills import (
                                                                ComplianceAuditorSkill, RiskAssessorSkill,
                                                                ConsistencyValidatorSkill, AuditReportGeneratorSkill
)
from backend.skills.official_verifier_skills import (
                                                                BrandMatcherSkill, ImageFetcherSkill,
                                                                SpecificationEnricherSkill, DataCompletenessCheckerSkill
)
from backend.skills.commercial_scout_skills import (
                                                                SourceHarvesterSkill, PriceExtractorSkill,
                                                                DataQualityAssessorSkill, DuplicateDetectorSkill
)
import unittest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class TestCommercialScoutSkills(unittest.TestCase):
                                                                """Test CommercialScout skills"""

                                                                def setUp(self):
                                                                                                                                self.harvester = SourceHarvesterSkill()
                                                                                                                                self.price_extractor = PriceExtractorSkill()
                                                                                                                                self.quality_assessor = DataQualityAssessorSkill()
                                                                                                                                self.duplicate_detector = DuplicateDetectorSkill()

                                                                def test_source_harvester_basic(self):
                                                                                                                                """Test basic source harvesting"""
                                                                                                                                context = {
                                                                                                                                                                                                'source_url': 'https://halilit.com',
                                                                                                                                                                                                'brand': 'Nord',
                                                                                                                                                                                                'max_results': 5
                                                                                                                                }
                                                                                                                                success, result = self.harvester.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertIn('products', result)
                                                                                                                                self.assertGreater(len(result['products']), 0)
                                                                                                                                self.assertEqual(result['brand'], 'Nord')
                                                                                                                                print("✅ test_source_harvester_basic PASSED")

                                                                def test_source_harvester_missing_context(self):
                                                                                                                                """Test harvester with missing context"""
                                                                                                                                context = {'source_url': 'https://halilit.com'}
                                                                                                                                success, result = self.harvester.execute(context)

                                                                                                                                self.assertFalse(success)
                                                                                                                                self.assertIn('Missing required', result)
                                                                                                                                print("✅ test_source_harvester_missing_context PASSED")

                                                                def test_price_extractor_valid(self):
                                                                                                                                """Test price extraction from valid data"""
                                                                                                                                context = {
                                                                                                                                                                                                'product_data': {
                                                                                                                                                                                                                                                                'name': 'Nord Piano 5',
                                                                                                                                                                                                                                                                'price_raw_il': '18500',
                                                                                                                                                                                                                                                                'price_raw_eilat': '15811'
                                                                                                                                                                                                }
                                                                                                                                }
                                                                                                                                success, result = self.price_extractor.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertIn('prices', result)
                                                                                                                                self.assertIn('price_il', result['prices'])
                                                                                                                                self.assertIn('price_eilat', result['prices'])
                                                                                                                                self.assertGreater(result['prices']['price_il'],
                                                                                                                                                                                                                                                                                                                                                                                                                                result['prices']['price_eilat'])
                                                                                                                                print("✅ test_price_extractor_valid PASSED")

                                                                def test_price_extractor_ratio_validation(self):
                                                                                                                                """Test price ratio validation"""
                                                                                                                                context = {
                                                                                                                                                                                                'product_data': {
                                                                                                                                                                                                                                                                'name': 'Test Product',
                                                                                                                                                                                                                                                                'price_raw_il': '10000',
                                                                                                                                                                                                                                                                'price_raw_eilat': '8300'  # 17% discount
                                                                                                                                                                                                }
                                                                                                                                }
                                                                                                                                success, result = self.price_extractor.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertTrue(result['ratio_valid'])
                                                                                                                                print("✅ test_price_extractor_ratio_validation PASSED")

                                                                def test_quality_assessor(self):
                                                                                                                                """Test data quality assessment"""
                                                                                                                                context = {
                                                                                                                                                                                                'product_data': {
                                                                                                                                                                                                                                                                'name': 'Test Product',
                                                                                                                                                                                                                                                                'brand': 'Nord',
                                                                                                                                                                                                                                                                'price_il': 18500,
                                                                                                                                                                                                                                                                'price_eilat': 15811,
                                                                                                                                                                                                                                                                'source_url': 'https://example.com'
                                                                                                                                                                                                },
                                                                                                                                                                                                'source_reliability': 0.95
                                                                                                                                }
                                                                                                                                success, result = self.quality_assessor.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertIn('quality_score', result)
                                                                                                                                self.assertIn('tier', result)
                                                                                                                                self.assertIn('is_usable', result)
                                                                                                                                self.assertGreaterEqual(result['quality_score'], 0.7)
                                                                                                                                print("✅ test_quality_assessor PASSED")

                                                                def test_duplicate_detector_unique(self):
                                                                                                                                """Test duplicate detection with unique products"""
                                                                                                                                products = [
                                                                                                                                                                                                {'name': 'Nord Piano 5', 'brand': 'Nord', 'price_il': 18500},
                                                                                                                                                                                                {'name': 'Roland FP-90X', 'brand': 'Roland', 'price_il': 25000},
                                                                                                                                                                                                {'name': 'Yamaha P-515', 'brand': 'Yamaha', 'price_il': 15000}
                                                                                                                                ]

                                                                                                                                context = {'products': products}
                                                                                                                                success, result = self.duplicate_detector.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertEqual(len(result['unique_products']), 3)
                                                                                                                                self.assertEqual(result['duplicate_count'], 0)
                                                                                                                                print("✅ test_duplicate_detector_unique PASSED")

class TestOfficialVerifierSkills(unittest.TestCase):
                                                                """Test OfficialVerifier skills"""

                                                                def setUp(self):
                                                                                                                                self.brand_matcher = BrandMatcherSkill()
                                                                                                                                self.image_fetcher = ImageFetcherSkill()
                                                                                                                                self.spec_enricher = SpecificationEnricherSkill()
                                                                                                                                self.completeness_checker = DataCompletenessCheckerSkill()

                                                                def test_brand_matcher_exact(self):
                                                                                                                                """Test exact brand matching"""
                                                                                                                                context = {
                                                                                                                                                                                                'brand_name': 'Nord',
                                                                                                                                                                                                'taxonomy': ['Nord', 'Roland', 'Yamaha', 'Korg']
                                                                                                                                }
                                                                                                                                success, result = self.brand_matcher.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertEqual(result['matched_brand'], 'Nord')
                                                                                                                                self.assertEqual(result['match_type'], 'exact')
                                                                                                                                self.assertEqual(result['confidence'], 1.0)
                                                                                                                                print("✅ test_brand_matcher_exact PASSED")

                                                                def test_brand_matcher_alias(self):
                                                                                                                                """Test alias brand matching"""
                                                                                                                                context = {
                                                                                                                                                                                                'brand_name': 'nord',
                                                                                                                                                                                                'taxonomy': ['Nord', 'Roland', 'Yamaha']
                                                                                                                                }
                                                                                                                                success, result = self.brand_matcher.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertEqual(result['matched_brand'], 'Nord')
                                                                                                                                self.assertEqual(result['match_type'], 'alias')
                                                                                                                                print("✅ test_brand_matcher_alias PASSED")

                                                                def test_brand_matcher_invalid(self):
                                                                                                                                """Test brand matching failure"""
                                                                                                                                context = {
                                                                                                                                                                                                'brand_name': 'UnknownBrand',
                                                                                                                                                                                                'taxonomy': ['Nord', 'Roland', 'Yamaha'],
                                                                                                                                                                                                'strict_match': True
                                                                                                                                }
                                                                                                                                success, result = self.brand_matcher.execute(context)

                                                                                                                                self.assertFalse(success)
                                                                                                                                print("✅ test_brand_matcher_invalid PASSED")

                                                                def test_image_fetcher(self):
                                                                                                                                """Test image fetching"""
                                                                                                                                context = {
                                                                                                                                                                                                'product_name': 'Piano 5',
                                                                                                                                                                                                'brand': 'Nord'
                                                                                                                                }
                                                                                                                                success, result = self.image_fetcher.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertIn('image_url', result)
                                                                                                                                self.assertIn('source', result)
                                                                                                                                self.assertIn('quality', result)
                                                                                                                                print("✅ test_image_fetcher PASSED")

                                                                def test_spec_enricher(self):
                                                                                                                                """Test specification enrichment"""
                                                                                                                                product = {
                                                                                                                                                                                                'name': 'Nord Piano 5',
                                                                                                                                                                                                'brand': 'Nord'
                                                                                                                                }
                                                                                                                                context = {'product_data': product}
                                                                                                                                success, result = self.spec_enricher.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertIn('specifications', result)
                                                                                                                                self.assertTrue(result.get('enriched'))
                                                                                                                                print("✅ test_spec_enricher PASSED")

                                                                def test_completeness_checker_complete(self):
                                                                                                                                """Test completeness checking for complete data"""
                                                                                                                                product = {
                                                                                                                                                                                                'name': 'Test Product',
                                                                                                                                                                                                'brand': 'Nord',
                                                                                                                                                                                                'price_il': 18500,
                                                                                                                                                                                                'price_eilat': 15811,
                                                                                                                                                                                                'image_url': 'https://example.com/image.jpg',
                                                                                                                                                                                                'source_url': 'https://halilit.com'
                                                                                                                                }
                                                                                                                                context = {'product_data': product}
                                                                                                                                success, result = self.completeness_checker.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertTrue(result['is_complete'])
                                                                                                                                self.assertTrue(result['can_publish'])
                                                                                                                                print("✅ test_completeness_checker_complete PASSED")

                                                                def test_completeness_checker_incomplete(self):
                                                                                                                                """Test completeness checking for incomplete data"""
                                                                                                                                product = {
                                                                                                                                                                                                'name': 'Test Product',
                                                                                                                                                                                                'brand': 'Nord'
                                                                                                                                                                                                # Missing price_il, price_eilat, image_url, source_url
                                                                                                                                }
                                                                                                                                context = {'product_data': product}
                                                                                                                                success, result = self.completeness_checker.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertFalse(result['is_complete'])
                                                                                                                                self.assertFalse(result['can_publish'])
                                                                                                                                self.assertGreater(len(result['critical_missing']), 0)
                                                                                                                                print("✅ test_completeness_checker_incomplete PASSED")

class TestExternalValidatorSkills(unittest.TestCase):
                                                                """Test ExternalValidator skills"""

                                                                def setUp(self):
                                                                                                                                self.compliance_auditor = ComplianceAuditorSkill()
                                                                                                                                self.risk_assessor = RiskAssessorSkill()
                                                                                                                                self.consistency_validator = ConsistencyValidatorSkill()
                                                                                                                                self.report_generator = AuditReportGeneratorSkill()

                                                                def test_compliance_auditor_approved(self):
                                                                                                                                """Test compliance audit that approves product"""
                                                                                                                                product = {
                                                                                                                                                                                                'id': '123',
                                                                                                                                                                                                'name': 'Nord Piano 5',
                                                                                                                                                                                                'brand': 'Nord',
                                                                                                                                                                                                'price_il': 18500,
                                                                                                                                                                                                'price_eilat': 15811,
                                                                                                                                                                                                'image_url': 'https://example.com/image.jpg'
                                                                                                                                }
                                                                                                                                context = {
                                                                                                                                                                                                'product_data': product,
                                                                                                                                                                                                'taxonomy': ['Nord', 'Roland', 'Yamaha']
                                                                                                                                }
                                                                                                                                success, result = self.compliance_auditor.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertEqual(result['status'], 'APPROVED')
                                                                                                                                self.assertTrue(result['is_approvable'])
                                                                                                                                self.assertEqual(len(result['violations']), 0)
                                                                                                                                print("✅ test_compliance_auditor_approved PASSED")

                                                                def test_compliance_auditor_rejected(self):
                                                                                                                                """Test compliance audit that rejects product"""
                                                                                                                                product = {
                                                                                                                                                                                                'id': '456',
                                                                                                                                                                                                'name': 'Unknown Product',
                                                                                                                                                                                                'brand': 'UnknownBrand',
                                                                                                                                                                                                'price_il': 100,  # Invalid price ratio
                                                                                                                                                                                                'price_eilat': 150,  # Eilat more expensive than IL
                                                                                                                                                                                                'image_url': ''  # Missing image
                                                                                                                                }
                                                                                                                                context = {
                                                                                                                                                                                                'product_data': product,
                                                                                                                                                                                                'taxonomy': ['Nord', 'Roland', 'Yamaha']
                                                                                                                                }
                                                                                                                                success, result = self.compliance_auditor.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertEqual(result['status'], 'REJECTED')
                                                                                                                                self.assertFalse(result['is_approvable'])
                                                                                                                                self.assertGreater(len(result['violations']), 0)
                                                                                                                                print("✅ test_compliance_auditor_rejected PASSED")

                                                                def test_risk_assessor(self):
                                                                                                                                """Test risk assessment"""
                                                                                                                                product = {
                                                                                                                                                                                                'id': '789',
                                                                                                                                                                                                'name': 'Test Product',
                                                                                                                                                                                                'brand': 'Nord',
                                                                                                                                                                                                'price_il': 18500,
                                                                                                                                                                                                'price_eilat': 15811,
                                                                                                                                                                                                'image_url': 'https://example.com/image.jpg',
                                                                                                                                                                                                'source_url': 'https://halilit.com'
                                                                                                                                }
                                                                                                                                context = {'product_data': product}
                                                                                                                                success, result = self.risk_assessor.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertIn('overall_risk_score', result)
                                                                                                                                self.assertIn('risk_level', result)
                                                                                                                                self.assertIn('dimension_scores', result)
                                                                                                                                self.assertGreaterEqual(result['overall_risk_score'], 0)
                                                                                                                                self.assertLessEqual(result['overall_risk_score'], 100)
                                                                                                                                print("✅ test_risk_assessor PASSED")

                                                                def test_consistency_validator_valid(self):
                                                                                                                                """Test consistency validation for valid data"""
                                                                                                                                product = {
                                                                                                                                                                                                'name': 'Nord Piano 5',
                                                                                                                                                                                                'brand': 'Nord',
                                                                                                                                                                                                'price_il': 18500,
                                                                                                                                                                                                'price_eilat': 15811,
                                                                                                                                                                                                'image_url': 'https://example.com/image.jpg'
                                                                                                                                }
                                                                                                                                context = {'product_data': product}
                                                                                                                                success, result = self.consistency_validator.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertTrue(result['is_consistent'])
                                                                                                                                self.assertTrue(result['can_publish'])
                                                                                                                                print("✅ test_consistency_validator_valid PASSED")

                                                                def test_consistency_validator_invalid(self):
                                                                                                                                """Test consistency validation for invalid data"""
                                                                                                                                product = {
                                                                                                                                                                                                'name': 'Test Product',
                                                                                                                                                                                                'brand': 'Nord',
                                                                                                                                                                                                'price_il': 15811,
                                                                                                                                                                                                'price_eilat': 18500,  # Eilat more than IL (invalid)
                                                                                                                                                                                                'image_url': 'not-a-url'  # Invalid URL
                                                                                                                                }
                                                                                                                                context = {'product_data': product}
                                                                                                                                success, result = self.consistency_validator.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertFalse(result['is_consistent'])
                                                                                                                                self.assertGreater(len(result['inconsistencies']), 0)
                                                                                                                                print("✅ test_consistency_validator_invalid PASSED")

                                                                def test_audit_report_generator(self):
                                                                                                                                """Test comprehensive audit report generation"""
                                                                                                                                product = {
                                                                                                                                                                                                'id': '999',
                                                                                                                                                                                                'name': 'Nord Piano 5',
                                                                                                                                                                                                'brand': 'Nord',
                                                                                                                                                                                                'price_il': 18500,
                                                                                                                                                                                                'price_eilat': 15811,
                                                                                                                                                                                                'image_url': 'https://example.com/image.jpg'
                                                                                                                                }

                                                                                                                                # First get compliance, risk, consistency results
                                                                                                                                comp_success, comp_result = self.compliance_auditor.execute({
                                                                                                                                                                                                'product_data': product,
                                                                                                                                                                                                'taxonomy': ['Nord', 'Roland']
                                                                                                                                })

                                                                                                                                risk_success, risk_result = self.risk_assessor.execute({
                                                                                                                                                                                                'product_data': product
                                                                                                                                })

                                                                                                                                cons_success, cons_result = self.consistency_validator.execute({
                                                                                                                                                                                                'product_data': product
                                                                                                                                })

                                                                                                                                # Generate report
                                                                                                                                context = {
                                                                                                                                                                                                'compliance_result': comp_result,
                                                                                                                                                                                                'risk_result': risk_result,
                                                                                                                                                                                                'consistency_result': cons_result,
                                                                                                                                                                                                'product_data': product
                                                                                                                                }
                                                                                                                                success, report = self.report_generator.execute(context)

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertIn('final_status', report)
                                                                                                                                self.assertIn('overall_risk_score', report)
                                                                                                                                self.assertIn('recommendation', report)
                                                                                                                                self.assertIn('report_summary', report)
                                                                                                                                print("✅ test_audit_report_generator PASSED")

class TestAgentWorkflows(unittest.TestCase):
                                                                """Test complete agent workflows"""

                                                                def test_commercial_scout_workflow(self):
                                                                                                                                """Test CommercialScout complete workflow"""
                                                                                                                                workflow = CommercialScoutWorkflow()

                                                                                                                                context = {
                                                                                                                                                                                                'source_url': 'https://halilit.com',
                                                                                                                                                                                                'brand': 'Nord',
                                                                                                                                                                                                'max_results': 5
                                                                                                                                }

                                                                                                                                result = workflow.execute(context)

                                                                                                                                self.assertTrue(result['success'])
                                                                                                                                self.assertIn('products', result)
                                                                                                                                self.assertGreater(len(result['products']), 0)
                                                                                                                                self.assertIn('quality_metrics', result)
                                                                                                                                self.assertEqual(result['workflow'], 'CommercialScout')
                                                                                                                                print("✅ test_commercial_scout_workflow PASSED")

                                                                def test_official_verifier_workflow(self):
                                                                                                                                """Test OfficialVerifier complete workflow"""
                                                                                                                                workflow = OfficialVerifierWorkflow()

                                                                                                                                products = [
                                                                                                                                                                                                {
                                                                                                                                                                                                                                                                'name': 'Nord Piano 5',
                                                                                                                                                                                                                                                                'brand': 'Nord',
                                                                                                                                                                                                                                                                'price_il': 18500,
                                                                                                                                                                                                                                                                'price_eilat': 15811
                                                                                                                                                                                                },
                                                                                                                                                                                                {
                                                                                                                                                                                                                                                                'name': 'Roland FP-90X',
                                                                                                                                                                                                                                                                'brand': 'Roland',
                                                                                                                                                                                                                                                                'price_il': 25000,
                                                                                                                                                                                                                                                                'price_eilat': 21250
                                                                                                                                                                                                }
                                                                                                                                ]

                                                                                                                                context = {
                                                                                                                                                                                                'products': products,
                                                                                                                                                                                                'taxonomy': ['Nord', 'Roland', 'Yamaha', 'Korg']
                                                                                                                                }

                                                                                                                                result = workflow.execute(context)

                                                                                                                                self.assertTrue(result['success'])
                                                                                                                                self.assertIn('products', result)
                                                                                                                                self.assertIn('metrics', result)
                                                                                                                                self.assertEqual(result['workflow'], 'OfficialVerifier')
                                                                                                                                print("✅ test_official_verifier_workflow PASSED")

                                                                def test_external_validator_workflow(self):
                                                                                                                                """Test ExternalValidator complete workflow"""
                                                                                                                                workflow = ExternalValidatorWorkflow()

                                                                                                                                products = [
                                                                                                                                                                                                {
                                                                                                                                                                                                                                                                'id': '1',
                                                                                                                                                                                                                                                                'name': 'Nord Piano 5',
                                                                                                                                                                                                                                                                'brand': 'Nord',
                                                                                                                                                                                                                                                                'price_il': 18500,
                                                                                                                                                                                                                                                                'price_eilat': 15811,
                                                                                                                                                                                                                                                                'image_url': 'https://example.com/nord.jpg'
                                                                                                                                                                                                },
                                                                                                                                                                                                {
                                                                                                                                                                                                                                                                'id': '2',
                                                                                                                                                                                                                                                                'name': 'Invalid Product',
                                                                                                                                                                                                                                                                'brand': 'Unknown',
                                                                                                                                                                                                                                                                'price_il': 1000,
                                                                                                                                                                                                                                                                'price_eilat': 2000,  # Invalid ratio
                                                                                                                                                                                                                                                                'image_url': ''
                                                                                                                                                                                                }
                                                                                                                                ]

                                                                                                                                context = {
                                                                                                                                                                                                'products': products,
                                                                                                                                                                                                'taxonomy': ['Nord', 'Roland', 'Yamaha']
                                                                                                                                }

                                                                                                                                result = workflow.execute(context)

                                                                                                                                self.assertTrue(result['success'])
                                                                                                                                self.assertIn('approved', result)
                                                                                                                                self.assertIn('rejected', result)
                                                                                                                                self.assertIn('needs_review', result)
                                                                                                                                self.assertIn('metrics', result)
                                                                                                                                self.assertEqual(result['workflow'], 'ExternalValidator')
                                                                                                                                print("✅ test_external_validator_workflow PASSED")

                                                                def test_end_to_end_trinity_swarm(self):
                                                                                                                                """Test complete Trinity Swarm pipeline"""
                                                                                                                                print("\n" + "="*70)
                                                                                                                                print("🚀 END-TO-END TRINITY SWARM TEST")
                                                                                                                                print("="*70)

                                                                                                                                # Use manually enriched test products that simulate the harvest pipeline
                                                                                                                                scout_products = [
                                                                                                                                                                                                {
                                                                                                                                                                                                                                                                'name': 'Nord Piano 5',
                                                                                                                                                                                                                                                                'brand': 'Nord',
                                                                                                                                                                                                                                                                'price_il': 18500,
                                                                                                                                                                                                                                                                'price_eilat': 15811,
                                                                                                                                                                                                                                                                'prices': {'price_il': 18500, 'price_eilat': 15811},
                                                                                                                                                                                                                                                                'source_url': 'https://halilit.com/nord-piano-5',
                                                                                                                                                                                                                                                                'quality': {'quality_score': 0.92, 'tier': 'HIGH', 'is_usable': True}
                                                                                                                                                                                                }
                                                                                                                                ]

                                                                                                                                # Step 2: OfficialVerifier (enrichment and validation)
                                                                                                                                print("\n2️⃣  OfficialVerifier Enrichment Phase...")
                                                                                                                                verifier_workflow = OfficialVerifierWorkflow()
                                                                                                                                verifier_result = verifier_workflow.execute({
                                                                                                                                                                                                'products': scout_products,
                                                                                                                                                                                                'taxonomy': ['Nord', 'Roland', 'Yamaha', 'Korg', 'Moog']
                                                                                                                                })
                                                                                                                                self.assertTrue(verifier_result['success'])
                                                                                                                                # Note: Products with completeness >= 65% will pass through
                                                                                                                                print(
                                                                                                                                                                                                f"   ✅ Processed {len(verifier_result['products'])} products through enrichment")

                                                                                                                                # Step 3: ExternalValidator - use manually prepared complete products
                                                                                                                                print("\n3️⃣  ExternalValidator Audit Phase...")
                                                                                                                                complete_products = [
                                                                                                                                                                                                {
                                                                                                                                                                                                                                                                'id': '1',
                                                                                                                                                                                                                                                                'name': 'Nord Piano 5',
                                                                                                                                                                                                                                                                'brand': 'Nord',
                                                                                                                                                                                                                                                                'price_il': 18500,
                                                                                                                                                                                                                                                                'price_eilat': 15811,
                                                                                                                                                                                                                                                                'image_url': 'https://example.com/nord.jpg',
                                                                                                                                                                                                                                                                'source_url': 'https://halilit.com/nord-piano-5',
                                                                                                                                                                                                                                                                'specifications': {'warranty': '2 years'}
                                                                                                                                                                                                }
                                                                                                                                ]

                                                                                                                                validator_workflow = ExternalValidatorWorkflow()
                                                                                                                                validator_result = validator_workflow.execute({
                                                                                                                                                                                                'products': complete_products,
                                                                                                                                                                                                'taxonomy': ['Nord', 'Roland', 'Yamaha', 'Korg', 'Moog']
                                                                                                                                })
                                                                                                                                self.assertTrue(validator_result['success'])
                                                                                                                                self.assertGreater(len(validator_result['approved']), 0)
                                                                                                                                print(f"   ✅ Approved: {len(validator_result['approved'])}")
                                                                                                                                print(f"   🛑 Rejected: {len(validator_result['rejected'])}")
                                                                                                                                print(f"   ⚠️  Review: {len(validator_result['needs_review'])}")

                                                                                                                                print("\n" + "="*70)
                                                                                                                                print("✨ END-TO-END TEST COMPLETE")
                                                                                                                                print("="*70)

def run_tests():
                                                                """Run all tests with formatted output"""
                                                                print("\n" + "="*70)
                                                                print("🧪 TRINITY SWARM COMPREHENSIVE TEST SUITE")
                                                                print("="*70)

                                                                loader = unittest.TestLoader()
                                                                suite = unittest.TestSuite()

                                                                # Add test suites
                                                                suite.addTests(loader.loadTestsFromTestCase(TestCommercialScoutSkills))
                                                                suite.addTests(loader.loadTestsFromTestCase(TestOfficialVerifierSkills))
                                                                suite.addTests(loader.loadTestsFromTestCase(TestExternalValidatorSkills))
                                                                suite.addTests(loader.loadTestsFromTestCase(TestAgentWorkflows))

                                                                # Run tests
                                                                runner = unittest.TextTestRunner(verbosity=2)
                                                                result = runner.run(suite)

                                                                # Print summary
                                                                print("\n" + "="*70)
                                                                print("📊 TEST SUMMARY")
                                                                print("="*70)
                                                                print(f"Tests run: {result.testsRun}")
                                                                print(
                                                                                                                                f"✅ Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
                                                                print(f"❌ Failures: {len(result.failures)}")
                                                                print(f"⚠️  Errors: {len(result.errors)}")
                                                                print("="*70 + "\n")

                                                                return result.wasSuccessful()

if __name__ == '__main__':
                                                                success = run_tests()
                                                                sys.exit(0 if success else 1)
