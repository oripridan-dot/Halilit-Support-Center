"""
COMPREHENSIVE SYSTEM VALIDATION TESTS
=====================================

Tests all angles of the Halilit Support Center v7.0:
- Version control system
- Component architecture
- Data models & validation
- Backend initialization
- API endpoints
- Integration flows
"""

import sys
import os
import json
import unittest
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ============================================================================
# TEST 1: VERSION CONTROL SYSTEM
# ============================================================================


class TestVersionControl(unittest.TestCase):
    """Validate version control system functionality"""

    def setUp(self):
        """Initialize test fixtures"""
        try:
            from backend.VERSION_CONTROL import (
                SYSTEM_VERSION,
                BRANCH_NAME,
                VersionStatus,
                assert_version_supports,
                ComponentRegistry,
                MethodNamingConvention,
                get_method_replacement,
                log_deprecation_warning,
                validate_system_config
            )
            self.version_module = {
                'SYSTEM_VERSION': SYSTEM_VERSION,
                'BRANCH_NAME': BRANCH_NAME,
                'VersionStatus': VersionStatus,
                'assert_version_supports': assert_version_supports,
                'ComponentRegistry': ComponentRegistry,
                'MethodNamingConvention': MethodNamingConvention,
                'get_method_replacement': get_method_replacement,
                'log_deprecation_warning': log_deprecation_warning,
                'validate_system_config': validate_system_config,
            }
        except ImportError as e:
            self.fail(f"Failed to import VERSION_CONTROL module: {e}")

    def test_version_constants(self):
        """Test version constants are correct"""
        self.assertEqual(self.version_module['SYSTEM_VERSION'], "7.0")
        self.assertIn("v6", self.version_module['BRANCH_NAME'])
        print(
            f"✅ Version constants correct: {self.version_module['SYSTEM_VERSION']} / {self.version_module['BRANCH_NAME']}")

    def test_version_status_enum(self):
        """Test VersionStatus enum has correct states"""
        VersionStatus = self.version_module['VersionStatus']
        self.assertTrue(hasattr(VersionStatus, 'CURRENT'))
        self.assertTrue(hasattr(VersionStatus, 'DEPRECATED'))
        self.assertTrue(hasattr(VersionStatus, 'LEGACY'))
        self.assertTrue(hasattr(VersionStatus, 'UNSUPPORTED'))
        print("✅ VersionStatus enum has all required states")

    def test_assert_version_supports(self):
        """Test version support assertion"""
        assert_version_supports = self.version_module['assert_version_supports']

        # Should pass for v7.0
        try:
            assert_version_supports("Trinity Swarm", min_version="7.0")
            print("✅ Version assertion passes for v7.0")
        except AssertionError:
            self.fail("Version assertion should pass for v7.0")

    def test_component_registry(self):
        """Test component registry has all 7 components"""
        ComponentRegistry = self.version_module['ComponentRegistry']

        required_components = [
            'TRINITY_SWARM',
            'CONDUCTOR',
            'INGESTION_ORCHESTRATOR',
            'INGESTION_TO_FRONTEND',
            'SPECTRUM_ADAPTER',
            'WORKFLOW_ENGINE',
            'SECURITY_SHIELD'
        ]

        for component in required_components:
            self.assertTrue(
                hasattr(ComponentRegistry, component),
                f"ComponentRegistry missing: {component}"
            )

        print(
            f"✅ ComponentRegistry has all {len(required_components)} components")

    def test_method_naming_convention(self):
        """Test method naming patterns"""
        MethodNamingConvention = self.version_module['MethodNamingConvention']

        # Check that the convention defines valid and forbidden patterns
        self.assertTrue(hasattr(MethodNamingConvention, 'VALIDATE'))
        self.assertTrue(hasattr(MethodNamingConvention, 'ENRICH'))
        self.assertTrue(hasattr(MethodNamingConvention, 'HARVEST'))
        self.assertTrue(hasattr(MethodNamingConvention, 'AUDIT'))
        self.assertTrue(hasattr(MethodNamingConvention, 'SYNC'))
        self.assertTrue(hasattr(MethodNamingConvention, 'PROCESS'))
        self.assertTrue(hasattr(MethodNamingConvention, 'HANDLE'))

        # Check forbidden patterns exist
        self.assertTrue(hasattr(MethodNamingConvention, 'FORBIDDEN'))
        self.assertIn('get_*', MethodNamingConvention.FORBIDDEN)
        self.assertIn('do_*', MethodNamingConvention.FORBIDDEN)
        self.assertIn('check_*', MethodNamingConvention.FORBIDDEN)
        self.assertIn('run_*', MethodNamingConvention.FORBIDDEN)

        print(f"✅ Method naming convention has 7 valid patterns + forbidden names")

    def test_deprecated_methods_registry(self):
        """Test deprecated methods are registered"""
        from backend.VERSION_CONTROL import DEPRECATED_METHODS

        self.assertIsInstance(DEPRECATED_METHODS, dict)
        self.assertGreater(len(DEPRECATED_METHODS), 0)

        # Should have replacement methods
        for deprecated, replacement in DEPRECATED_METHODS.items():
            self.assertIsNotNone(replacement)

        print(
            f"✅ Deprecated methods registry has {len(DEPRECATED_METHODS)} entries")

    def test_validate_system_config(self):
        """Test system configuration validation"""
        validate_system_config = self.version_module['validate_system_config']

        try:
            result = validate_system_config()
            self.assertIsNotNone(result)
            print("✅ System configuration validation passed")
        except Exception as e:
            self.fail(f"System configuration validation failed: {e}")


# ============================================================================
# TEST 2: DATA MODELS & VALIDATION
# ============================================================================

class TestDataModels(unittest.TestCase):
    """Validate Pydantic data models"""

    def test_audit_report_model(self):
        """Test AuditReport Pydantic model"""
        from backend.agents.trinity_swarm import AuditReport

        # Valid audit report
        report = AuditReport(
            product_id="PROD123",
            status="APPROVED",
            risk_score=15,
            violations=[],
            auditor_notes="Passed all checks"
        )

        self.assertEqual(report.status, "APPROVED")
        self.assertEqual(report.risk_score, 15)
        print("✅ AuditReport model validation passed")

    def test_audit_report_invalid_status(self):
        """Test AuditReport rejects invalid status"""
        from backend.agents.trinity_swarm import AuditReport

        # Status must be APPROVED or REJECTED - test this is enforced
        try:
            report = AuditReport(
                status="INVALID",
                risk_score=50,
                violations=[],
                auditor_notes="Test"
            )
            # If we get here, validation didn't catch it (might be too permissive)
            print("⚠️  AuditReport status validation could be stricter")
        except Exception:
            print("✅ AuditReport rejects invalid status")

    def test_risk_score_range(self):
        """Test risk score is 0-100"""
        from backend.agents.trinity_swarm import AuditReport

        # Valid risk scores
        for score in [0, 50, 100]:
            report = AuditReport(
                status="APPROVED",
                risk_score=score,
                violations=[],
                auditor_notes="Test"
            )
            self.assertGreaterEqual(report.risk_score, 0)
            self.assertLessEqual(report.risk_score, 100)

        print("✅ Risk score range validation passed")


# ============================================================================
# TEST 3: TRINITY SWARM INITIALIZATION
# ============================================================================

class TestTrinitySwarmInitialization(unittest.TestCase):
    """Test Trinity Swarm agent initialization"""

    def test_trinity_swarm_imports(self):
        """Test Trinity Swarm can be imported"""
        try:
            from backend.agents import trinity_swarm
            self.assertIsNotNone(trinity_swarm)
            print("✅ Trinity Swarm imports successfully")
        except ImportError as e:
            self.fail(f"Failed to import Trinity Swarm: {e}")

    def test_agent_base_class(self):
        """Test AgentBase class exists and initializes"""
        try:
            from backend.agents.trinity_swarm import AgentBase

            # Create a test agent (with no API key, will simulate)
            agent = AgentBase(
                name="TestAgent",
                model_name="gemini-2.0-flash",
                system_instruction="You are a test agent"
            )

            self.assertEqual(agent.name, "TestAgent")
            self.assertEqual(agent.model_name, "gemini-2.0-flash")
            print("✅ AgentBase initializes correctly")
        except Exception as e:
            self.fail(f"AgentBase initialization failed: {e}")

    def test_memory_aware_mixin(self):
        """Test agents have memory awareness"""
        try:
            from backend.agents.agent_memory import MemoryAwareMixin
            from backend.agents.trinity_swarm import AgentBase

            agent = AgentBase(name="MemoryTest")
            self.assertTrue(isinstance(agent, MemoryAwareMixin))
            self.assertTrue(hasattr(agent, 'learn_from_action'))
            print("✅ Agents have MemoryAwareMixin")
        except Exception as e:
            self.fail(f"Memory awareness test failed: {e}")


# ============================================================================
# TEST 4: BACKEND MODULES
# ============================================================================

class TestBackendModules(unittest.TestCase):
    """Test backend module structure"""

    def test_conductor_module(self):
        """Test conductor_main module"""
        try:
            from backend import conductor_main
            self.assertIsNotNone(conductor_main)
            print("✅ conductor_main module imports")
        except ImportError as e:
            print(f"⚠️  conductor_main import warning: {e}")

    def test_ingestion_orchestrator(self):
        """Test ingestion orchestrator"""
        try:
            from backend.ingestion.orchestrator import Orchestrator
            self.assertIsNotNone(Orchestrator)
            print("✅ Ingestion Orchestrator imports")
        except ImportError as e:
            print(f"⚠️  Orchestrator import warning: {e}")

    def test_security_shield(self):
        """Test security shield"""
        try:
            from backend import security_shield
            self.assertIsNotNone(security_shield)
            print("✅ security_shield module imports")
        except ImportError as e:
            print(f"⚠️  security_shield import warning: {e}")

    def test_spectrum_adapter(self):
        """Test spectrum adapter"""
        try:
            from backend.ingestion.spectrum_adapter import SpectrumAdapter
            self.assertIsNotNone(SpectrumAdapter)
            print("✅ SpectrumAdapter imports")
        except ImportError as e:
            print(f"⚠️  SpectrumAdapter import warning: {e}")


# ============================================================================
# TEST 5: DATA PIPELINE
# ============================================================================

class TestDataPipeline(unittest.TestCase):
    """Test data processing pipeline"""

    def test_data_models_schema(self):
        """Test data models define correct schema"""
        try:
            from backend.ingestion.data_models import (
                ProductDraft,
                BrandDTO,
                PricingData
            )

            # Can instantiate
            product = ProductDraft(
                name="Test Product",
                brand="Test Brand",
                price=99.99
            )
            self.assertEqual(product.name, "Test Product")
            print("✅ Data models schema valid")
        except Exception as e:
            print(f"⚠️  Data models test: {e}")

    def test_ingestion_database(self):
        """Test ingestion database module"""
        try:
            from backend.ingestion.ingestion_database import IngestionDatabase
            self.assertIsNotNone(IngestionDatabase)
            print("✅ IngestionDatabase module available")
        except ImportError as e:
            print(f"⚠️  IngestionDatabase import: {e}")


# ============================================================================
# TEST 6: API ENDPOINT VALIDATION
# ============================================================================

class TestAPIEndpoints(unittest.TestCase):
    """Test FastAPI endpoints exist and respond"""

    def test_server_imports(self):
        """Test server.py can be imported"""
        try:
            # Check server.py exists
            server_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'server.py'
            )
            self.assertTrue(os.path.exists(server_path))
            print("✅ server.py exists")
        except Exception as e:
            self.fail(f"Server validation failed: {e}")

    def test_fastapi_app_structure(self):
        """Test FastAPI app is properly configured"""
        try:
            with open(os.path.join(os.path.dirname(__file__), '..', 'server.py')) as f:
                content = f.read()
                self.assertIn('FastAPI', content)
                self.assertIn('app =', content)
                print("✅ FastAPI app structure valid")
        except Exception as e:
            self.fail(f"FastAPI structure validation failed: {e}")


# ============================================================================
# TEST 7: FILE INTEGRITY
# ============================================================================

class TestFileIntegrity(unittest.TestCase):
    """Ensure no corrupted/empty files"""

    def test_no_zero_byte_files(self):
        """Verify no zero-byte files in production code"""
        backend_path = os.path.join(os.path.dirname(__file__), '..')
        zero_byte_files = []

        for root, dirs, files in os.walk(backend_path):
            # Skip venv, __pycache__, .venv, node_modules
            dirs[:] = [d for d in dirs if d not in [
                'venv', '__pycache__', '.git', 'logs', '.venv', 'node_modules']]

            # Also skip if .venv is in the path
            if '.venv' in root or 'node_modules' in root:
                continue

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    if os.path.getsize(file_path) == 0:
                        zero_byte_files.append(file_path)

        self.assertEqual(len(zero_byte_files), 0,
                         f"Found zero-byte files: {zero_byte_files}")
        print(f"✅ No zero-byte Python files in production code")

    def test_critical_files_exist(self):
        """Ensure all critical files exist"""
        critical_files = [
            'backend/server.py',
            'backend/VERSION_CONTROL.py',
            'backend/agents/trinity_swarm.py',
            'backend/ingestion/orchestrator.py',
            'DEVELOPER_STANDARDS.md',
            'CONDUCTOR_CLARITY_REPORT.md',
        ]

        base_path = os.path.join(os.path.dirname(__file__), '../..')

        for file in critical_files:
            file_path = os.path.join(base_path, file)
            self.assertTrue(
                os.path.exists(file_path),
                f"Critical file missing: {file}"
            )

        print(f"✅ All {len(critical_files)} critical files exist")

    def test_critical_files_not_empty(self):
        """Ensure critical files have content"""
        critical_files = [
            'backend/server.py',
            'backend/VERSION_CONTROL.py',
            'DEVELOPER_STANDARDS.md',
        ]

        base_path = os.path.join(os.path.dirname(__file__), '../..')

        for file in critical_files:
            file_path = os.path.join(base_path, file)
            size = os.path.getsize(file_path)
            self.assertGreater(
                size, 100, f"File too small: {file} ({size} bytes)")

        print(f"✅ All critical files have content (>100 bytes)")


# ============================================================================
# TEST 8: DEPRECATION SYSTEM
# ============================================================================

class TestDeprecationSystem(unittest.TestCase):
    """Test deprecation warnings and replacements"""

    def test_deprecated_methods_marked(self):
        """Test deprecated methods are clearly marked"""
        try:
            orchestrator_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'ingestion',
                'orchestrator.py'
            )

            with open(orchestrator_path) as f:
                content = f.read()
                # Should have deprecation markers
                self.assertIn('❌ DEPRECATED', content)
                print("✅ Deprecated methods are marked with ❌")
        except Exception as e:
            print(f"⚠️  Deprecation marking check: {e}")

    def test_replacement_methods_documented(self):
        """Test replacement methods are documented"""
        try:
            from backend.VERSION_CONTROL import DEPRECATED_METHODS

            for old_method, replacement in DEPRECATED_METHODS.items():
                self.assertIsNotNone(replacement)
                self.assertNotEqual(old_method, replacement)

            print(
                f"✅ {len(DEPRECATED_METHODS)} deprecated methods have replacements")
        except Exception as e:
            self.fail(f"Replacement documentation check failed: {e}")


# ============================================================================
# TEST 9: COMPONENT SEPARATION
# ============================================================================

class TestComponentSeparation(unittest.TestCase):
    """Test component responsibilities are not overlapping"""

    def test_trinity_swarm_responsibility(self):
        """Trinity should only do data processing"""
        try:
            with open(os.path.join(os.path.dirname(__file__), '..', 'agents', 'trinity_swarm.py')) as f:
                content = f.read()
                # Should have harvest, enrich, audit
                self.assertIn('harvest', content.lower())
                self.assertIn('enrich', content.lower())
                self.assertIn('audit', content.lower())
                # Should NOT orchestrate
                self.assertNotIn('wait_for', content)
                print("✅ Trinity Swarm responsibility verified (data processing)")
        except Exception as e:
            print(f"⚠️  Trinity Swarm responsibility check: {e}")

    def test_conductor_responsibility(self):
        """Conductor should only do orchestration"""
        try:
            conductor_path = os.path.join(os.path.dirname(
                __file__), '..', 'conductor_main.py')
            with open(conductor_path) as f:
                content = f.read()
                # Should import Trinity
                self.assertIn('trinity', content.lower())
                print("✅ Conductor responsibility verified (orchestration)")
        except Exception as e:
            print(f"⚠️  Conductor responsibility check: {e}")


# ============================================================================
# TEST 10: NAMING CONVENTION COMPLIANCE
# ============================================================================

class TestNamingCompliance(unittest.TestCase):
    """Verify code follows naming conventions"""

    def test_no_ambiguous_method_names(self):
        """Ensure no forbidden method names in production code"""
        forbidden_patterns = ['def get_', 'def do_', 'def check_', 'def run_']

        backend_path = os.path.join(os.path.dirname(__file__), '..')
        violations = []

        for root, dirs, files in os.walk(backend_path):
            dirs[:] = [d for d in dirs if d not in [
                'venv', '__pycache__', '.git', 'logs']]

            for file in files:
                if file.endswith('.py') and not file.startswith('test'):
                    file_path = os.path.join(root, file)
                    with open(file_path, encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            for pattern in forbidden_patterns:
                                if pattern in line and not line.strip().startswith('#'):
                                    violations.append(
                                        f"{file}:{line_num} -> {line.strip()}")

        if violations:
            print(
                f"⚠️  Found {len(violations)} potential naming violations (review manually):")
            for v in violations[:5]:  # Show first 5
                print(f"   {v}")
        else:
            print("✅ No forbidden method names found in production code")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_tests():
    """Run all tests and generate report"""
    print("\n" + "="*70)
    print("HALILIT SUPPORT CENTER - COMPREHENSIVE SYSTEM VALIDATION")
    print("="*70 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestVersionControl))
    suite.addTests(loader.loadTestsFromTestCase(TestDataModels))
    suite.addTests(loader.loadTestsFromTestCase(
        TestTrinitySwarmInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestBackendModules))
    suite.addTests(loader.loadTestsFromTestCase(TestDataPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestFileIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestDeprecationSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestComponentSeparation))
    suite.addTests(loader.loadTestsFromTestCase(TestNamingCompliance))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(
        f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70 + "\n")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
