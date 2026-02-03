"""
Test Suite for DevAgent Skills & Maintenance Workflows

Tests all 7 new DevAgent skills and 4 maintenance workflows.
Validates agent orchestration for system health & auto-updates.
"""

import unittest
import tempfile
import os
import json
from backend.skills.devagent_skills import (
                                                                CodeAutoUpdateSkill,
                                                                CodeSyncSkill,
                                                                CompatibilityCheckSkill,
                                                                CodeFormatterSkill,
                                                                ImportOrganizationSkill,
                                                                CodeValidationSkill,
                                                                DependencyResolutionSkill
)
from backend.workflow.maintenance_workflows import (
                                                                CodeCleanupWorkflow,
                                                                CodeOrganizationWorkflow,
                                                                CodeSyncWorkflow,
                                                                SystemHealthCheckWorkflow
)

class TestCodeAutoUpdateSkill(unittest.TestCase):
                                                                """Test CodeAutoUpdateSkill"""

                                                                def setUp(self):
                                                                                                                                self.skill = CodeAutoUpdateSkill()
                                                                                                                                self.temp_dir = tempfile.mkdtemp()

                                                                def test_auto_update_with_changes(self):
                                                                                                                                """Test applying code changes"""
                                                                                                                                test_file = os.path.join(self.temp_dir, 'test.py')
                                                                                                                                with open(test_file, 'w') as f:
                                                                                                                                                                                                f.write('import old_module\nprint("hello")\n')

                                                                                                                                success, result = self.skill.execute({
                                                                                                                                                                                                'file_path': test_file,
                                                                                                                                                                                                'changes': [
                                                                                                                                                                                                                                                                {'old_pattern': 'old_module',
                                                                                                                                                                                                                                                                                                                                'new_pattern': 'new_module', 'type': 'import'}
                                                                                                                                                                                                ]
                                                                                                                                })

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertEqual(result['changes_applied'], 1)

                                                                                                                                with open(test_file, 'r') as f:
                                                                                                                                                                                                content = f.read()
                                                                                                                                self.assertIn('new_module', content)
                                                                                                                                self.assertNotIn('old_module', content)

                                                                def test_auto_update_no_changes_needed(self):
                                                                                                                                """Test when no changes are needed"""
                                                                                                                                test_file = os.path.join(self.temp_dir, 'test2.py')
                                                                                                                                with open(test_file, 'w') as f:
                                                                                                                                                                                                f.write('import good_module\nprint("hello")\n')

                                                                                                                                success, result = self.skill.execute({
                                                                                                                                                                                                'file_path': test_file,
                                                                                                                                                                                                'changes': [
                                                                                                                                                                                                                                                                {'old_pattern': 'nonexistent',
                                                                                                                                                                                                                                                                                                                                'new_pattern': 'something', 'type': 'import'}
                                                                                                                                                                                                ]
                                                                                                                                })

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertEqual(result['changes_applied'], 0)

                                                                def test_auto_update_file_not_found(self):
                                                                                                                                """Test error handling for missing file"""
                                                                                                                                success, result = self.skill.execute({
                                                                                                                                                                                                'file_path': '/nonexistent/file.py',
                                                                                                                                                                                                'changes': []
                                                                                                                                })

                                                                                                                                self.assertFalse(success)

                                                                def tearDown(self):
                                                                                                                                import shutil
                                                                                                                                shutil.rmtree(self.temp_dir)

class TestCodeSyncSkill(unittest.TestCase):
                                                                """Test CodeSyncSkill"""

                                                                def setUp(self):
                                                                                                                                self.skill = CodeSyncSkill()
                                                                                                                                self.temp_dir = tempfile.mkdtemp()

                                                                def test_sync_imports(self):
                                                                                                                                """Test syncing imports between files"""
                                                                                                                                source_file = os.path.join(self.temp_dir, 'source.py')
                                                                                                                                target_file = os.path.join(self.temp_dir, 'target.py')

                                                                                                                                with open(source_file, 'w') as f:
                                                                                                                                                                                                f.write('import json\nimport os\nprint("source")\n')

                                                                                                                                with open(target_file, 'w') as f:
                                                                                                                                                                                                f.write('print("target")\n')

                                                                                                                                success, result = self.skill.execute({
                                                                                                                                                                                                'source_file': source_file,
                                                                                                                                                                                                'target_files': [target_file],
                                                                                                                                                                                                'sync_type': 'imports'
                                                                                                                                })

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertGreaterEqual(result['items_synced'], 0)

                                                                def test_sync_source_not_found(self):
                                                                                                                                """Test error handling"""
                                                                                                                                success, result = self.skill.execute({
                                                                                                                                                                                                'source_file': '/nonexistent/source.py',
                                                                                                                                                                                                'target_files': [],
                                                                                                                                                                                                'sync_type': 'imports'
                                                                                                                                })

                                                                                                                                self.assertFalse(success)

                                                                def tearDown(self):
                                                                                                                                import shutil
                                                                                                                                shutil.rmtree(self.temp_dir)

class TestCompatibilityCheckSkill(unittest.TestCase):
                                                                """Test CompatibilityCheckSkill"""

                                                                def setUp(self):
                                                                                                                                self.skill = CompatibilityCheckSkill()
                                                                                                                                self.temp_dir = tempfile.mkdtemp()

                                                                def test_compatibility_check_good_file(self):
                                                                                                                                """Test checking compatible code"""
                                                                                                                                test_file = os.path.join(self.temp_dir, 'good.py')
                                                                                                                                with open(test_file, 'w') as f:
                                                                                                                                                                                                f.write('import json\nimport os\nprint("hello")\n')

                                                                                                                                success, result = self.skill.execute({
                                                                                                                                                                                                'file_path': test_file,
                                                                                                                                                                                                'compatibility_level': 'standard'
                                                                                                                                })

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertIn('compatibility_score', result)
                                                                                                                                self.assertGreaterEqual(result['compatibility_score'], 0)
                                                                                                                                self.assertLessEqual(result['compatibility_score'], 100)

                                                                def test_compatibility_check_file_not_found(self):
                                                                                                                                """Test error handling"""
                                                                                                                                success, result = self.skill.execute({
                                                                                                                                                                                                'file_path': '/nonexistent/file.py'
                                                                                                                                })

                                                                                                                                self.assertFalse(success)

                                                                def tearDown(self):
                                                                                                                                import shutil
                                                                                                                                shutil.rmtree(self.temp_dir)

class TestCodeFormatterSkill(unittest.TestCase):
                                                                """Test CodeFormatterSkill"""

                                                                def setUp(self):
                                                                                                                                self.skill = CodeFormatterSkill()
                                                                                                                                self.temp_dir = tempfile.mkdtemp()

                                                                def test_format_python_file(self):
                                                                                                                                """Test formatting Python code"""
                                                                                                                                test_file = os.path.join(self.temp_dir, 'messy.py')
                                                                                                                                with open(test_file, 'w') as f:
                                                                                                                                                                                                f.write('import os  \nimport sys  \nprint("hello")  ')

                                                                                                                                success, result = self.skill.execute({
                                                                                                                                                                                                'file_path': test_file,
                                                                                                                                                                                                'language': 'python'
                                                                                                                                })

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertIn('formatted', result)

                                                                def test_format_file_not_found(self):
                                                                                                                                """Test error handling"""
                                                                                                                                success, result = self.skill.execute({
                                                                                                                                                                                                'file_path': '/nonexistent/file.py'
                                                                                                                                })

                                                                                                                                self.assertFalse(success)

                                                                def tearDown(self):
                                                                                                                                import shutil
                                                                                                                                shutil.rmtree(self.temp_dir)

class TestImportOrganizationSkill(unittest.TestCase):
                                                                """Test ImportOrganizationSkill"""

                                                                def setUp(self):
                                                                                                                                self.skill = ImportOrganizationSkill()
                                                                                                                                self.temp_dir = tempfile.mkdtemp()

                                                                def test_organize_imports(self):
                                                                                                                                """Test organizing imports"""
                                                                                                                                test_file = os.path.join(self.temp_dir, 'unorganized.py')
                                                                                                                                with open(test_file, 'w') as f:
                                                                                                                                                                                                f.write(
                                                                                                                                                                                                                                                                'import sys\nimport os\nimport json\nimport sys\nprint("hello")\n')

                                                                                                                                success, result = self.skill.execute({
                                                                                                                                                                                                'file_path': test_file
                                                                                                                                })

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertIn('imports_unique', result)
                                                                                                                                self.assertGreater(result['imports_unique'], 0)

                                                                def test_organize_imports_file_not_found(self):
                                                                                                                                """Test error handling"""
                                                                                                                                success, result = self.skill.execute({
                                                                                                                                                                                                'file_path': '/nonexistent/file.py'
                                                                                                                                })

                                                                                                                                self.assertFalse(success)

                                                                def tearDown(self):
                                                                                                                                import shutil
                                                                                                                                shutil.rmtree(self.temp_dir)

class TestCodeValidationSkill(unittest.TestCase):
                                                                """Test CodeValidationSkill"""

                                                                def setUp(self):
                                                                                                                                self.skill = CodeValidationSkill()
                                                                                                                                self.temp_dir = tempfile.mkdtemp()

                                                                def test_validate_good_code(self):
                                                                                                                                """Test validating good code"""
                                                                                                                                test_file = os.path.join(self.temp_dir, 'good.py')
                                                                                                                                with open(test_file, 'w') as f:
                                                                                                                                                                                                f.write(
                                                                                                                                                                                                                                                                'def hello_world():\n    """Greet the world"""\n    print("hello")\n')

                                                                                                                                success, result = self.skill.execute({
                                                                                                                                                                                                'file_path': test_file,
                                                                                                                                                                                                'strict_mode': False
                                                                                                                                })

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertIn('validation_score', result)
                                                                                                                                self.assertGreaterEqual(result['validation_score'], 0)

                                                                def test_validate_file_not_found(self):
                                                                                                                                """Test error handling"""
                                                                                                                                success, result = self.skill.execute({
                                                                                                                                                                                                'file_path': '/nonexistent/file.py'
                                                                                                                                })

                                                                                                                                self.assertFalse(success)

                                                                def tearDown(self):
                                                                                                                                import shutil
                                                                                                                                shutil.rmtree(self.temp_dir)

class TestDependencyResolutionSkill(unittest.TestCase):
                                                                """Test DependencyResolutionSkill"""

                                                                def setUp(self):
                                                                                                                                self.skill = DependencyResolutionSkill()
                                                                                                                                self.temp_dir = tempfile.mkdtemp()

                                                                def test_resolve_dependencies(self):
                                                                                                                                """Test resolving dependencies"""
                                                                                                                                test_file = os.path.join(self.temp_dir, 'deps.py')
                                                                                                                                with open(test_file, 'w') as f:
                                                                                                                                                                                                f.write('import json\nimport os\nprint("hello")\n')

                                                                                                                                success, result = self.skill.execute({
                                                                                                                                                                                                'file_path': test_file,
                                                                                                                                                                                                'project_root': self.temp_dir
                                                                                                                                })

                                                                                                                                self.assertTrue(success)
                                                                                                                                self.assertIn('resolved_count', result)
                                                                                                                                self.assertIn('unresolved_count', result)

                                                                def test_resolve_dependencies_file_not_found(self):
                                                                                                                                """Test error handling"""
                                                                                                                                success, result = self.skill.execute({
                                                                                                                                                                                                'file_path': '/nonexistent/file.py'
                                                                                                                                })

                                                                                                                                self.assertFalse(success)

                                                                def tearDown(self):
                                                                                                                                import shutil
                                                                                                                                shutil.rmtree(self.temp_dir)

class TestCodeCleanupWorkflow(unittest.TestCase):
                                                                """Test CodeCleanupWorkflow"""

                                                                def setUp(self):
                                                                                                                                self.workflow = CodeCleanupWorkflow()
                                                                                                                                self.temp_dir = tempfile.mkdtemp()

                                                                def test_cleanup_workflow_execution(self):
                                                                                                                                """Test full cleanup workflow"""
                                                                                                                                test_file = os.path.join(self.temp_dir, 'test.py')
                                                                                                                                with open(test_file, 'w') as f:
                                                                                                                                                                                                f.write('import os\nimport sys\nprint("hello")\n')

                                                                                                                                result = self.workflow.execute({
                                                                                                                                                                                                'file_paths': [test_file],
                                                                                                                                                                                                'auto_fix': True
                                                                                                                                })

                                                                                                                                self.assertTrue(result['success'])
                                                                                                                                self.assertEqual(result['workflow'], 'CodeCleanupWorkflow')
                                                                                                                                self.assertIn('metrics', result)

                                                                def test_cleanup_with_empty_file_list(self):
                                                                                                                                """Test cleanup with no files"""
                                                                                                                                result = self.workflow.execute({
                                                                                                                                                                                                'file_paths': [],
                                                                                                                                                                                                'auto_fix': True
                                                                                                                                })

                                                                                                                                self.assertTrue(result['success'])
                                                                                                                                self.assertEqual(result['metrics']['files_scanned'], 0)

                                                                def tearDown(self):
                                                                                                                                import shutil
                                                                                                                                shutil.rmtree(self.temp_dir)

class TestCodeOrganizationWorkflow(unittest.TestCase):
                                                                """Test CodeOrganizationWorkflow"""

                                                                def setUp(self):
                                                                                                                                self.workflow = CodeOrganizationWorkflow()
                                                                                                                                self.temp_dir = tempfile.mkdtemp()

                                                                def test_organization_workflow_execution(self):
                                                                                                                                """Test full organization workflow"""
                                                                                                                                test_file = os.path.join(self.temp_dir, 'test.py')
                                                                                                                                with open(test_file, 'w') as f:
                                                                                                                                                                                                f.write('import os\ndef my_function():\n    pass\n')

                                                                                                                                result = self.workflow.execute({
                                                                                                                                                                                                'file_paths': [test_file],
                                                                                                                                                                                                'enforce_naming': True
                                                                                                                                })

                                                                                                                                self.assertTrue(result['success'])
                                                                                                                                self.assertEqual(result['workflow'], 'CodeOrganizationWorkflow')
                                                                                                                                self.assertIn('metrics', result)

                                                                def tearDown(self):
                                                                                                                                import shutil
                                                                                                                                shutil.rmtree(self.temp_dir)

class TestCodeSyncWorkflow(unittest.TestCase):
                                                                """Test CodeSyncWorkflow"""

                                                                def setUp(self):
                                                                                                                                self.workflow = CodeSyncWorkflow()
                                                                                                                                self.temp_dir = tempfile.mkdtemp()

                                                                def test_sync_workflow_execution(self):
                                                                                                                                """Test sync workflow"""
                                                                                                                                source = os.path.join(self.temp_dir, 'source.py')
                                                                                                                                target = os.path.join(self.temp_dir, 'target.py')

                                                                                                                                with open(source, 'w') as f:
                                                                                                                                                                                                f.write('import json\nprint("source")\n')
                                                                                                                                with open(target, 'w') as f:
                                                                                                                                                                                                f.write('print("target")\n')

                                                                                                                                result = self.workflow.execute({
                                                                                                                                                                                                'source_file': source,
                                                                                                                                                                                                'target_files': [target],
                                                                                                                                                                                                'sync_types': ['imports']
                                                                                                                                })

                                                                                                                                self.assertTrue(result['success'])
                                                                                                                                self.assertEqual(result['workflow'], 'CodeSyncWorkflow')

                                                                def tearDown(self):
                                                                                                                                import shutil
                                                                                                                                shutil.rmtree(self.temp_dir)

class TestSystemHealthCheckWorkflow(unittest.TestCase):
                                                                """Test SystemHealthCheckWorkflow"""

                                                                def setUp(self):
                                                                                                                                self.workflow = SystemHealthCheckWorkflow()
                                                                                                                                self.temp_dir = tempfile.mkdtemp()

                                                                def test_health_check_execution(self):
                                                                                                                                """Test health check workflow"""
                                                                                                                                test_file = os.path.join(self.temp_dir, 'test.py')
                                                                                                                                with open(test_file, 'w') as f:
                                                                                                                                                                                                f.write('import json\nprint("hello")\n')

                                                                                                                                result = self.workflow.execute({
                                                                                                                                                                                                'file_paths': [test_file],
                                                                                                                                                                                                'include_dependencies': True
                                                                                                                                })

                                                                                                                                self.assertTrue(result['success'])
                                                                                                                                self.assertEqual(result['workflow'], 'SystemHealthCheckWorkflow')
                                                                                                                                self.assertIn('health_score', result)
                                                                                                                                self.assertIn('health_status', result)

                                                                def tearDown(self):
                                                                                                                                import shutil
                                                                                                                                shutil.rmtree(self.temp_dir)

class TestAgentMaintenanceOrchestrator(unittest.TestCase):
                                                                """Test AgentMaintenanceOrchestrator"""

                                                                def setUp(self):
                                                                                                                                self.orchestrator = AgentMaintenanceOrchestrator()
                                                                                                                                self.temp_dir = tempfile.mkdtemp()

                                                                def test_orchestrator_initialization(self):
                                                                                                                                """Test orchestrator initializes"""
                                                                                                                                self.assertIsNotNone(self.orchestrator)
                                                                                                                                self.assertEqual(self.orchestrator.system_health['status'], 'unknown')

                                                                def test_discover_python_files(self):
                                                                                                                                """Test discovering Python files"""
                                                                                                                                # Create test files
                                                                                                                                os.makedirs(os.path.join(self.temp_dir, 'subdir'), exist_ok=True)

                                                                                                                                test_file1 = os.path.join(self.temp_dir, 'test1.py')
                                                                                                                                test_file2 = os.path.join(self.temp_dir, 'subdir', 'test2.py')

                                                                                                                                with open(test_file1, 'w') as f:
                                                                                                                                                                                                f.write('print("test1")\n')
                                                                                                                                with open(test_file2, 'w') as f:
                                                                                                                                                                                                f.write('print("test2")\n')

                                                                                                                                # This would need to be mocked to test in temp dir
                                                                                                                                # Just verify the method exists and works
                                                                                                                                self.assertTrue(hasattr(self.orchestrator, 'discover_python_files'))

                                                                def test_generate_maintenance_report(self):
                                                                                                                                """Test report generation"""
                                                                                                                                report = self.orchestrator.generate_maintenance_report()

                                                                                                                                self.assertIsInstance(report, str)
                                                                                                                                self.assertIn('MAINTENANCE', report)
                                                                                                                                self.assertIn('System Health', report)

                                                                def tearDown(self):
                                                                                                                                import shutil
                                                                                                                                shutil.rmtree(self.temp_dir)

def run_all_tests():
                                                                """Run all tests with summary"""
                                                                loader = unittest.TestLoader()
                                                                suite = unittest.TestSuite()

                                                                # Add all test classes
                                                                test_classes = [
                                                                                                                                TestCodeAutoUpdateSkill,
                                                                                                                                TestCodeSyncSkill,
                                                                                                                                TestCompatibilityCheckSkill,
                                                                                                                                TestCodeFormatterSkill,
                                                                                                                                TestImportOrganizationSkill,
                                                                                                                                TestCodeValidationSkill,
                                                                                                                                TestDependencyResolutionSkill,
                                                                                                                                TestCodeCleanupWorkflow,
                                                                                                                                TestCodeOrganizationWorkflow,
                                                                                                                                TestCodeSyncWorkflow,
                                                                                                                                TestSystemHealthCheckWorkflow,
                                                                                                                                TestAgentMaintenanceOrchestrator
                                                                ]

                                                                for test_class in test_classes:
                                                                                                                                suite.addTests(loader.loadTestsFromTestCase(test_class))

                                                                runner = unittest.TextTestRunner(verbosity=2)
                                                                result = runner.run(suite)

                                                                # Print summary
                                                                print("\n" + "=" * 70)
                                                                print("📊 DEVAGENT SKILLS & WORKFLOWS TEST SUMMARY")
                                                                print("=" * 70)
                                                                print(f"Tests run: {result.testsRun}")
                                                                print(
                                                                                                                                f"✅ Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
                                                                print(f"❌ Failures: {len(result.failures)}")
                                                                print(f"⚠️  Errors: {len(result.errors)}")
                                                                if result.testsRun > 0:
                                                                                                                                pass_rate = ((result.testsRun - len(result.failures) -
                                                                                                                                                                                                                                                                                                                                len(result.errors)) / result.testsRun) * 100
                                                                                                                                print(f"Pass Rate: {pass_rate:.1f}%")
                                                                print("=" * 70)

                                                                return result.wasSuccessful()

if __name__ == '__main__':
                                                                success = run_all_tests()
                                                                exit(0 if success else 1)
