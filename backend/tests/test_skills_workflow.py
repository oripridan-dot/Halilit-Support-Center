import sys
import os

# backend/tests/test_skills_workflow.py
"""
Comprehensive Test Suite for Skills & Workflow Architecture

Tests the safety guardrails that prevent catastrophic file operations.
"""

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class TestBaseSkill(unittest.TestCase):
                """Tests for BaseSkill abstract class."""

                def test_validate_context_success(self):
                                """Test that context validation passes with all required keys."""
                                class DummySkill(BaseSkill):
                                                def execute(self, context):
                                                                return True, "dummy"

                                skill = DummySkill()
                                context = {'key1': 'value1', 'key2': 'value2'}
                                valid, error = skill.validate_context(context, ['key1', 'key2'])

                                self.assertTrue(valid)
                                self.assertEqual(error, "")

                def test_validate_context_failure(self):
                                """Test that context validation fails with missing keys."""
                                class DummySkill(BaseSkill):
                                                def execute(self, context):
                                                                return True, "dummy"

                                skill = DummySkill()
                                context = {'key1': 'value1'}
                                valid, error = skill.validate_context(
                                                context, ['key1', 'key2', 'key3'])

                                self.assertFalse(valid)
                                self.assertIn('key2', error)
                                self.assertIn('key3', error)

class TestReactComponentBuilder(unittest.TestCase):
                """Tests for ReactComponentBuilder skill."""

                def setUp(self):
                                """Create temporary directory for test files."""
                                self.temp_dir = tempfile.mkdtemp()
                                self.skill = ReactComponentBuilder()

                def tearDown(self):
                                """Clean up temporary files."""
                                import shutil
                                if os.path.exists(self.temp_dir):
                                                shutil.rmtree(self.temp_dir)

                def test_build_valid_component_success(self):
                                """Test building a valid React component."""
                                valid_component = """import React from 'react';

export const TestComponent = () => {
                return <div>Test Component</div>;
};
"""
                                file_path = os.path.join(self.temp_dir, 'TestComponent.tsx')

                                success, result = self.skill.execute({
                                                'file_path': file_path,
                                                'code_content': valid_component,
                                                'create_backup': False
                                })

                                self.assertTrue(success)
                                self.assertIsInstance(result, dict)
                                self.assertEqual(result['status'], 'verified')
                                self.assertGreater(result['size_bytes'], 0)
                                self.assertTrue(os.path.exists(file_path))

                def test_empty_content_rejected(self):
                                """Test that empty content is rejected (THE CRITICAL GUARDRAIL)."""
                                file_path = os.path.join(self.temp_dir, 'EmptyComponent.tsx')

                                success, result = self.skill.execute({
                                                'file_path': file_path,
                                                'code_content': ''
                                })

                                self.assertFalse(success)
                                self.assertIn('empty', result.lower())
                                self.assertFalse(os.path.exists(file_path))

                def test_missing_react_import_rejected(self):
                                """Test that components without React import are rejected."""
                                invalid_component = """export const NoImportComponent = () => {
                return <div>Missing React import</div>;
};
"""
                                file_path = os.path.join(self.temp_dir, 'NoImport.tsx')

                                success, result = self.skill.execute({
                                                'file_path': file_path,
                                                'code_content': invalid_component
                                })

                                self.assertFalse(success)
                                self.assertIn('React import', result)
                                self.assertFalse(os.path.exists(file_path))

                def test_missing_export_rejected(self):
                                """Test that components without export statement are rejected."""
                                invalid_component = """import React from 'react';

const NoExportComponent = () => {
                return <div>Missing export</div>;
};
"""
                                file_path = os.path.join(self.temp_dir, 'NoExport.tsx')

                                success, result = self.skill.execute({
                                                'file_path': file_path,
                                                'code_content': invalid_component
                                })

                                self.assertFalse(success)
                                self.assertIn('export', result.lower())
                                self.assertFalse(os.path.exists(file_path))

                def test_content_too_small_rejected(self):
                                """Test that unrealistically small files are rejected."""
                                tiny_component = """import React from 'react';
export const T = () => <div/>;
"""
                                file_path = os.path.join(self.temp_dir, 'Tiny.tsx')

                                success, result = self.skill.execute({
                                                'file_path': file_path,
                                                'code_content': tiny_component
                                })

                                self.assertFalse(success)
                                self.assertIn('too small', result.lower())

                def test_backup_creation(self):
                                """Test that existing files are backed up before overwrite."""
                                file_path = os.path.join(self.temp_dir, 'Existing.tsx')

                                # Create initial file
                                original_content = """import React from 'react';
export const OriginalComponent = () => <div>Original</div>;
"""
                                with open(file_path, 'w') as f:
                                                f.write(original_content)

                                # Overwrite with new content
                                new_content = """import React from 'react';
export const UpdatedComponent = () => <div>Updated</div>;
"""
                                success, result = self.skill.execute({
                                                'file_path': file_path,
                                                'code_content': new_content,
                                                'create_backup': True
                                })

                                self.assertTrue(success)

                                # Check backup was created
                                backup_path = f"{file_path}.backup"
                                self.assertTrue(os.path.exists(backup_path))

                                with open(backup_path, 'r') as f:
                                                backup_content = f.read()
                                self.assertEqual(backup_content, original_content)

                def test_rollback_on_verification_failure(self):
                                """Test that corrupt files are rolled back."""
                                # This is a more advanced test that would require mocking file operations
                                # to simulate a write that creates a 0-byte file
                                pass

class TestTypeScriptModuleBuilder(unittest.TestCase):
                """Tests for TypeScriptModuleBuilder skill."""

                def setUp(self):
                                """Create temporary directory for test files."""
                                self.temp_dir = tempfile.mkdtemp()
                                self.skill = TypeScriptModuleBuilder()

                def tearDown(self):
                                """Clean up temporary files."""
                                import shutil
                                if os.path.exists(self.temp_dir):
                                                shutil.rmtree(self.temp_dir)

                def test_build_valid_typescript_module(self):
                                """Test building a valid TypeScript module."""
                                valid_module = """export interface TestInterface {
                id: string;
                name: string;
}

export const testFunction = (data: TestInterface): string => {
                return data.name;
};
"""
                                file_path = os.path.join(self.temp_dir, 'test.ts')

                                success, result = self.skill.execute({
                                                'file_path': file_path,
                                                'code_content': valid_module
                                })

                                self.assertTrue(success)
                                self.assertTrue(os.path.exists(file_path))
                                self.assertGreater(result['size_bytes'], 0)

                def test_invalid_extension_rejected(self):
                                """Test that non-TypeScript extensions are rejected."""
                                file_path = os.path.join(self.temp_dir, 'test.js')

                                success, result = self.skill.execute({
                                                'file_path': file_path,
                                                'code_content': 'export const test = "test";'
                                })

                                self.assertFalse(success)
                                self.assertIn('extension', result.lower())

class TestFeatureBuildWorkflow(unittest.TestCase):
                """Tests for FeatureBuildWorkflow."""

                def setUp(self):
                                """Create temporary directory for test files."""
                                self.temp_dir = tempfile.mkdtemp()
                                self.workflow = FeatureBuildWorkflow(max_retries=2)

                def tearDown(self):
                                """Clean up temporary files."""
                                import shutil
                                if os.path.exists(self.temp_dir):
                                                shutil.rmtree(self.temp_dir)

                def test_successful_feature_build(self):
                                """Test a complete successful workflow execution."""
                                component_code = """import React from 'react';

export const WorkflowTestComponent = () => {
                return (
                                <div className="p-4 bg-slate-900">
                                                <h1 className="text-blue-500">Workflow Test</h1>
                                </div>
                );
};
"""

                                feature_spec = {
                                                'name': 'Workflow Test Feature',
                                                'files': [
                                                                {
                                                                                'path': os.path.join(self.temp_dir, 'WorkflowTest.tsx'),
                                                                                'content': component_code,
                                                                                'type': 'react'
                                                                }
                                                ]
                                }

                                success = self.workflow.run_feature_build(feature_spec)

                                self.assertTrue(success)
                                self.assertEqual(self.workflow.current_state, WorkflowState.COMPLETE)
                                self.assertTrue(os.path.exists(feature_spec['files'][0]['path']))

                def test_workflow_fails_on_invalid_content(self):
                                """Test that workflow fails when content is invalid."""
                                invalid_code = ""  # Empty code

                                feature_spec = {
                                                'name': 'Invalid Feature',
                                                'files': [
                                                                {
                                                                                'path': os.path.join(self.temp_dir, 'Invalid.tsx'),
                                                                                'content': invalid_code,
                                                                                'type': 'react'
                                                                }
                                                ]
                                }

                                success = self.workflow.run_feature_build(feature_spec)

                                self.assertFalse(success)
                                self.assertEqual(self.workflow.current_state, WorkflowState.FAILED)

                def test_workflow_retries_on_failure(self):
                                """Test that workflow retries failed builds."""
                                # This would require more sophisticated mocking
                                # to simulate a transient failure that succeeds on retry
                                pass

                def test_workflow_state_transitions(self):
                                """Test that workflow transitions through correct states."""
                                component_code = """import React from 'react';

export const StateTestComponent = () => {
                return <div>State Test</div>;
};
"""

                                feature_spec = {
                                                'name': 'State Transition Test',
                                                'files': [
                                                                {
                                                                                'path': os.path.join(self.temp_dir, 'StateTest.tsx'),
                                                                                'content': component_code,
                                                                                'type': 'react'
                                                                }
                                                ]
                                }

                                success = self.workflow.run_feature_build(feature_spec)

                                self.assertTrue(success)

                                # Check state history
                                self.assertGreater(len(self.workflow.state_history), 0)

                                # Verify expected state flow
                                states = [transition['to']
                                                                        for transition in self.workflow.state_history]
                                self.assertIn('PLANNING', states)
                                self.assertIn('CODING', states)
                                self.assertIn('VERIFYING', states)
                                self.assertIn('COMPLETE', states)

def run_tests():
                """Run all tests with detailed output."""
                # Create test suite
                loader = unittest.TestLoader()
                suite = unittest.TestSuite()

                # Add test classes
                suite.addTests(loader.loadTestsFromTestCase(TestBaseSkill))
                suite.addTests(loader.loadTestsFromTestCase(TestReactComponentBuilder))
                suite.addTests(loader.loadTestsFromTestCase(TestTypeScriptModuleBuilder))
                suite.addTests(loader.loadTestsFromTestCase(TestFeatureBuildWorkflow))

                # Run tests
                runner = unittest.TextTestRunner(verbosity=2)
                result = runner.run(suite)

                # Print summary
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

if __name__ == '__main__':
                success = run_tests()
                sys.exit(0 if success else 1)
