"""
INTEGRATION TEST SUITE
Tests data flow from backend to frontend and component integration
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

# Color codes for console output


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TestResult:
    """Track test results with colored output"""

    def __init__(self):
        self.passed: List[Dict[str, str]] = []
        self.failed: List[Dict[str, str]] = []
        self.warnings: List[Dict[str, str]] = []

    def pass_test(self, name: str, message: str = '') -> None:
        self.passed.append({'name': name, 'message': message})
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} {name}")
        if message:
            print(f"  {message}")

    def fail_test(self, name: str, message: str = '') -> None:
        self.failed.append({'name': name, 'message': message})
        print(f"{Colors.FAIL}✗{Colors.ENDC} {name}")
        if message:
            print(f"  {message}")

    def warn_test(self, name: str, message: str = '') -> None:
        self.warnings.append({'name': name, 'message': message})
        print(f"{Colors.WARNING}⚠{Colors.ENDC} {name}")
        if message:
            print(f"  {message}")

    def print_summary(self) -> int:
        """Print summary and return exit code"""
        total = len(self.passed) + len(self.failed) + len(self.warnings)
        pass_pct = (
            (len(self.passed) / total * 100) if total > 0 else 0
        )

        print(
            f"\n{Colors.BOLD}{'=' * 60}{Colors.ENDC}"
        )
        print(
            f"RESULTS: {Colors.OKGREEN}{len(self.passed)} passed{Colors.ENDC}, "
            f"{Colors.FAIL}{len(self.failed)} failed{Colors.ENDC}, "
            f"{Colors.WARNING}{len(self.warnings)} warnings{Colors.ENDC}"
        )
        print(f"Pass Rate: {Colors.BOLD}{pass_pct:.1f}%{Colors.ENDC}")
        print(f"{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")

        return 0 if len(self.failed) == 0 else 1


class IntegrationTestSuite:
    """Comprehensive integration tests"""

    def __init__(self):
        self.results = TestResult()
        self.workspace_root = Path(__file__).parent.parent.parent
        self.data_dir = (
            self.workspace_root / 'frontend' / 'public' / 'data'
        )

    def test_data_flow_backend_to_frontend(self) -> None:
        """Test that backend data correctly flows to frontend"""
        print(
            f"\n{Colors.HEADER}{Colors.BOLD}TEST 1: BACKEND → FRONTEND DATA FLOW{Colors.ENDC}"
        )
        print('-' * 60)

        # Verify data files exist
        data_files = list(self.data_dir.glob('*.json'))
        if not data_files:
            self.results.fail_test(
                'Data files exist',
                f"No JSON files in {self.data_dir}",
            )
            return

        self.results.pass_test(
            'Data files exist', f"{len(data_files)} files ✓")

        # Load and validate each file
        valid_files = 0
        for file_path in data_files:
            if file_path.name == 'index.json':
                continue

            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                if 'brand_identity' in data and 'products' in data:
                    valid_files += 1
                else:
                    self.results.warn_test(
                        f"{file_path.name} structure",
                        "Missing brand_identity or products",
                    )
            except json.JSONDecodeError as e:
                self.results.fail_test(
                    f"{file_path.name} JSON", f"Invalid JSON: {e}"
                )
            except Exception as e:
                self.results.fail_test(
                    f"{file_path.name} parsing", str(e)
                )

        if valid_files > 0:
            self.results.pass_test(
                'Valid brand files', f"{valid_files} files with proper structure ✓"
            )

    def test_product_data_completeness(self) -> None:
        """Test that all products have required data fields"""
        print(
            f"\n{Colors.HEADER}{Colors.BOLD}TEST 2: PRODUCT DATA COMPLETENESS{Colors.ENDC}"
        )
        print('-' * 60)

        required_fields = ['id', 'name', 'brand', 'category', 'pill_data']
        required_pill_fields = [
            'id',
            'official_name',
            'ui_meta',
            'specs',
            'context_meta',
            'commercial_meta',
        ]

        total_products = 0
        complete_products = 0

        for file_path in self.data_dir.glob('*.json'):
            if file_path.name == 'index.json':
                continue

            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                products = data.get('products', [])
                for product in products:
                    total_products += 1

                    # Check required fields
                    has_all_fields = all(
                        field in product for field in required_fields
                    )
                    if not has_all_fields:
                        self.results.warn_test(
                            f"{file_path.name}/{product.get('id', 'unknown')}",
                            "Missing required fields",
                        )
                        continue

                    # Check pill_data fields
                    pill_data = product.get('pill_data', {})
                    has_pill_fields = all(
                        field in pill_data for field in required_pill_fields
                    )
                    if has_pill_fields:
                        complete_products += 1
                    else:
                        self.results.warn_test(
                            f"{file_path.name}/{product.get('id')} pill_data",
                            "Missing pill_data fields",
                        )
            except Exception as e:
                self.results.fail_test(
                    f"{file_path.name} loading", str(e)
                )

        if total_products > 0:
            completeness = (
                (complete_products / total_products) * 100
                if total_products > 0
                else 0
            )
            if completeness >= 80:
                self.results.pass_test(
                    'Product completeness',
                    f"{complete_products}/{total_products} complete ({completeness:.1f}%) ✓",
                )
            else:
                self.results.warn_test(
                    'Product completeness',
                    f"{complete_products}/{total_products} complete ({completeness:.1f}%)",
                )

    def test_component_data_binding(self) -> None:
        """Test that component props match data structure"""
        print(
            f"\n{Colors.HEADER}{Colors.BOLD}TEST 3: COMPONENT DATA BINDING{Colors.ENDC}"
        )
        print('-' * 60)

        for file_path in self.data_dir.glob('*.json'):
            if file_path.name == 'index.json':
                continue

            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                for product in data.get('products', []):
                    pill_data = product.get('pill_data', {})

                    # Test ProductSpecs binding
                    specs = pill_data.get('specs', {})
                    if isinstance(specs, dict) and len(specs) > 0:
                        self.results.pass_test(
                            f"{product.get('id')} specs",
                            f"{len(specs)} specs available ✓",
                        )
                    else:
                        self.results.warn_test(
                            f"{product.get('id')} specs",
                            "No specs or invalid format",
                        )

                    # Test ConfidenceBadge binding
                    ui_meta = pill_data.get('ui_meta', {})
                    score = ui_meta.get('y_axis_score')
                    badges = ui_meta.get('badges', [])
                    sources = (
                        pill_data.get('context_meta', {})
                        .get('sources_of_truth', [])
                    )

                    if (
                        isinstance(score, (int, float))
                        and badges
                        and sources
                    ):
                        self.results.pass_test(
                            f"{product.get('id')} badge data",
                            f"Score: {score}, Badges: {len(badges)}, Sources: {len(sources)} ✓",
                        )
                    else:
                        self.results.warn_test(
                            f"{product.get('id')} badge data",
                            "Missing or invalid badge data",
                        )

                    # Test ValidationPipeline binding
                    pipeline = pill_data.get('validation_pipeline', {})
                    steps = [
                        'step1_official',
                        'step2_commercial',
                        'step3_context',
                        'step4_cross_validation',
                        'step5_published',
                    ]
                    pipeline_complete = all(
                        step in pipeline for step in steps
                    )

                    if pipeline_complete:
                        self.results.pass_test(
                            f"{product.get('id')} pipeline",
                            "All 5 steps present ✓",
                        )
                    else:
                        missing = [s for s in steps if s not in pipeline]
                        self.results.warn_test(
                            f"{product.get('id')} pipeline",
                            f"Missing: {missing}",
                        )
            except Exception as e:
                self.results.fail_test(
                    f"{file_path.name} binding test", str(e)
                )

    def test_data_type_consistency(self) -> None:
        """Test that all data types match expected types"""
        print(
            f"\n{Colors.HEADER}{Colors.BOLD}TEST 4: DATA TYPE CONSISTENCY{Colors.ENDC}"
        )
        print('-' * 60)

        type_errors = 0
        type_checks = 0

        for file_path in self.data_dir.glob('*.json'):
            if file_path.name == 'index.json':
                continue

            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                for product in data.get('products', []):
                    pill_data = product.get('pill_data', {})

                    # Check ui_meta types
                    ui_meta = pill_data.get('ui_meta', {})
                    if 'y_axis_score' in ui_meta:
                        type_checks += 1
                        if not isinstance(ui_meta['y_axis_score'], (int, float)):
                            type_errors += 1
                            self.results.warn_test(
                                f"{product.get('id')} y_axis_score",
                                f"Expected number, got {type(ui_meta['y_axis_score']).__name__}",
                            )

                    # Check badges type
                    if 'badges' in ui_meta:
                        type_checks += 1
                        if not isinstance(ui_meta['badges'], list):
                            type_errors += 1
                            self.results.warn_test(
                                f"{product.get('id')} badges",
                                f"Expected list, got {type(ui_meta['badges']).__name__}",
                            )

                    # Check pipeline data_quality types
                    pipeline = pill_data.get('validation_pipeline', {})
                    for step_name, step_data in pipeline.items():
                        type_checks += 1
                        quality = step_data.get('data_quality')
                        if not isinstance(quality, (int, float)):
                            type_errors += 1
                            self.results.warn_test(
                                f"{product.get('id')} {step_name} quality",
                                f"Expected number, got {type(quality).__name__}",
                            )
            except Exception as e:
                self.results.fail_test(
                    f"{file_path.name} type checking", str(e)
                )

        if type_checks > 0 and type_errors == 0:
            self.results.pass_test(
                'Data type consistency',
                f"All {type_checks} type checks passed ✓",
            )
        elif type_errors > 0:
            self.results.warn_test(
                'Data type consistency',
                f"{type_errors} type mismatches found",
            )

    def test_validation_pipeline_integrity(self) -> None:
        """Test that validation pipelines are properly structured"""
        print(
            f"\n{Colors.HEADER}{Colors.BOLD}TEST 5: VALIDATION PIPELINE INTEGRITY{Colors.ENDC}"
        )
        print('-' * 60)

        valid_statuses = ['complete', 'partial', 'pending', 'failed']
        steps = [
            'step1_official',
            'step2_commercial',
            'step3_context',
            'step4_cross_validation',
            'step5_published',
        ]

        pipeline_integrity_score = 0
        total_pipelines = 0

        for file_path in self.data_dir.glob('*.json'):
            if file_path.name == 'index.json':
                continue

            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                for product in data.get('products', []):
                    pipeline = (
                        product.get('pill_data', {})
                        .get('validation_pipeline', {})
                    )

                    if not pipeline:
                        continue

                    total_pipelines += 1
                    pipeline_valid = True

                    for step in steps:
                        if step not in pipeline:
                            pipeline_valid = False
                            self.results.warn_test(
                                f"{product.get('id')} {step}",
                                "Step missing from pipeline",
                            )
                            continue

                        step_data = pipeline[step]

                        # Check status
                        status = step_data.get('status')
                        if status not in valid_statuses:
                            pipeline_valid = False
                            self.results.warn_test(
                                f"{product.get('id')} {step} status",
                                f"Invalid status: {status}",
                            )

                        # Check data_quality
                        quality = step_data.get('data_quality')
                        if not isinstance(quality, (int, float)):
                            pipeline_valid = False
                        elif not (0 <= quality <= 100):
                            pipeline_valid = False
                            self.results.warn_test(
                                f"{product.get('id')} {step} quality",
                                f"Quality out of range: {quality}",
                            )

                    if pipeline_valid:
                        pipeline_integrity_score += 1
            except Exception as e:
                self.results.fail_test(
                    f"{file_path.name} pipeline integrity", str(e)
                )

        if total_pipelines > 0:
            integrity_pct = (
                (pipeline_integrity_score / total_pipelines) * 100
            )
            if integrity_pct >= 80:
                self.results.pass_test(
                    'Pipeline integrity',
                    f"{pipeline_integrity_score}/{total_pipelines} valid ({integrity_pct:.1f}%) ✓",
                )
            else:
                self.results.warn_test(
                    'Pipeline integrity',
                    f"{pipeline_integrity_score}/{total_pipelines} valid ({integrity_pct:.1f}%)",
                )

    def test_source_attribution(self) -> None:
        """Test that sources are properly attributed"""
        print(
            f"\n{Colors.HEADER}{Colors.BOLD}TEST 6: SOURCE ATTRIBUTION${Colors.ENDC}"
        )
        print('-' * 60)

        valid_source_types = [
            'manufacturer',
            'review',
            'expert',
            'community',
            'verified_retailer',
        ]
        total_sources = 0
        valid_sources = 0

        for file_path in self.data_dir.glob('*.json'):
            if file_path.name == 'index.json':
                continue

            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                for product in data.get('products', []):
                    sources = (
                        product.get('pill_data', {})
                        .get('context_meta', {})
                        .get('sources_of_truth', [])
                    )

                    for source in sources:
                        total_sources += 1
                        source_type = source.get('type')

                        if source_type in valid_source_types:
                            confidence = source.get('confidence')
                            if (
                                isinstance(confidence, (int, float))
                                and 0 <= confidence <= 100
                            ):
                                valid_sources += 1
                            else:
                                self.results.warn_test(
                                    f"{product.get('id')} source confidence",
                                    f"Invalid confidence: {confidence}",
                                )
                        else:
                            self.results.warn_test(
                                f"{product.get('id')} source type",
                                f"Invalid type: {source_type}",
                            )
            except Exception as e:
                self.results.fail_test(
                    f"{file_path.name} source attribution", str(e)
                )

        if total_sources > 0:
            source_pct = (valid_sources / total_sources) * 100
            if source_pct >= 80:
                self.results.pass_test(
                    'Source attribution',
                    f"{valid_sources}/{total_sources} valid ({source_pct:.1f}%) ✓",
                )
            else:
                self.results.warn_test(
                    'Source attribution',
                    f"{valid_sources}/{total_sources} valid ({source_pct:.1f}%)",
                )

    def run_all(self) -> int:
        """Run all integration tests"""
        print(
            f"\n{Colors.BOLD}{Colors.HEADER}\n╔{'=' * 58}╗\n║     HALILIT - INTEGRATION TEST SUITE{' ' * 19}║\n╚{'=' * 58}╝\n{Colors.ENDC}"
        )

        self.test_data_flow_backend_to_frontend()
        self.test_product_data_completeness()
        self.test_component_data_binding()
        self.test_data_type_consistency()
        self.test_validation_pipeline_integrity()
        self.test_source_attribution()

        return self.results.print_summary()


if __name__ == '__main__':
    suite = IntegrationTestSuite()
    exit(suite.run_all())
