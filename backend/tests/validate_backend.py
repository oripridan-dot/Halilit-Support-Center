#!/usr/bin/env python3
"""
BACKEND VALIDATION SUITE
Comprehensive tests for all Python refinery components
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Setup paths
# __file__ is backend/tests/validate_backend.py
# parent is backend/tests
# parent.parent is backend
# parent.parent.parent is workspace root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.append(str(BACKEND_DIR))


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
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def pass_test(self, name: str, message: str = ""):
        self.passed.append((name, message))
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} {name}")
        if message:
            print(f"  {message}")

    def fail_test(self, name: str, message: str = ""):
        self.failed.append((name, message))
        print(f"{Colors.FAIL}✗{Colors.ENDC} {name}")
        if message:
            print(f"  {message}")

    def warn_test(self, name: str, message: str = ""):
        self.warnings.append((name, message))
        print(f"{Colors.WARNING}⚠{Colors.ENDC} {name}")
        if message:
            print(f"  {message}")

    def summary(self):
        total = len(self.passed) + len(self.failed) + len(self.warnings)
        pass_pct = (len(self.passed) / total * 100) if total > 0 else 0

        print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"RESULTS: {Colors.OKGREEN}{len(self.passed)} passed{Colors.ENDC}, "
              f"{Colors.FAIL}{len(self.failed)} failed{Colors.ENDC}, "
              f"{Colors.WARNING}{len(self.warnings)} warnings{Colors.ENDC}")
        print(f"Pass Rate: {Colors.BOLD}{pass_pct:.1f}%{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

        return len(self.failed) == 0

# =============================================================================
# TEST SUITE 1: DATA STRUCTURE VALIDATION
# =============================================================================


def test_data_files(results: TestResult):
    """Validate JSON data files structure and completeness"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}TEST 1: DATA FILE VALIDATION{Colors.ENDC}")
    print("-" * 60)

    data_dir = ROOT_DIR / "frontend" / "public" / "data"
    brand_files = list(data_dir.glob("*.json"))

    if not brand_files:
        results.fail_test("Data files exist",
                          f"No JSON files found in {data_dir}")
        return

    results.pass_test("Data directory exists",
                      f"Found {len(brand_files)} files")

    required_files = {"adam-audio.json", "amphion.json", "warm-audio.json",
                      "bespeco.json", "drumdots.json", "fzone.json", "index.json"}
    found_files = {f.name for f in brand_files}

    if required_files.issubset(found_files):
        results.pass_test("All brand files present",
                          f"✓ {len(required_files)} files")
    else:
        missing = required_files - found_files
        results.fail_test("All brand files present", f"Missing: {missing}")

    # Validate each brand file
    for brand_file in [f for f in brand_files if f.name != "index.json"]:
        try:
            with open(brand_file) as f:
                data = json.load(f)

            # Check structure
            if "brand_identity" not in data or "products" not in data:
                results.fail_test(f"{brand_file.name} structure",
                                  "Missing brand_identity or products")
                continue

            products = data["products"]
            if not isinstance(products, list) or len(products) == 0:
                results.fail_test(f"{brand_file.name} products",
                                  "Products not a non-empty list")
                continue

            results.pass_test(f"{brand_file.name} structure",
                              f"{len(products)} products")

            # Validate each product
            for i, product in enumerate(products):
                required_fields = {"id", "name",
                                   "brand", "category", "pill_data"}
                if not all(field in product for field in required_fields):
                    missing = required_fields - set(product.keys())
                    results.fail_test(f"{brand_file.name} product[{i}] fields",
                                      f"Missing: {missing}")
                    continue

                # Validate pill_data
                pill = product.get("pill_data", {})
                pill_required = {"ui_meta", "specs",
                                 "context_meta", "commercial_meta"}
                if not all(field in pill for field in pill_required):
                    missing = pill_required - set(pill.keys())
                    results.warn_test(f"{brand_file.name} product[{i}] pill_data",
                                      f"Missing: {missing}")

                # Validate specs
                specs = pill.get("specs", {})
                if not isinstance(specs, dict) or len(specs) == 0:
                    results.warn_test(f"{brand_file.name} product[{i}] specs",
                                      "Empty or invalid specs")

        except json.JSONDecodeError as e:
            results.fail_test(f"{brand_file.name} JSON validity", str(e))
        except Exception as e:
            results.fail_test(f"{brand_file.name} loading", str(e))

    # Validate index
    try:
        with open(data_dir / "index.json") as f:
            index = json.load(f)

        if "brands" in index and isinstance(index["brands"], list):
            results.pass_test("index.json structure",
                              f"{len(index['brands'])} brands")

            if len(index["brands"]) == 6:
                results.pass_test("All 6 brands in index", "✓")
            else:
                results.warn_test(
                    "Brand count", f"Expected 6, got {len(index['brands'])}")
        else:
            results.fail_test("index.json structure",
                              "Missing or invalid brands array")

    except Exception as e:
        results.fail_test("index.json loading", str(e))

# =============================================================================
# TEST SUITE 2: PRODUCT DATA COMPLETENESS
# =============================================================================


def test_product_completeness(results: TestResult):
    """Validate that all products have complete data"""
    print(
        f"\n{Colors.HEADER}{Colors.BOLD}TEST 2: PRODUCT DATA COMPLETENESS{Colors.ENDC}")
    print("-" * 60)

    data_dir = ROOT_DIR / "frontend" / "public" / "data"
    brand_files = [f for f in data_dir.glob(
        "*.json") if f.name != "index.json"]

    min_specs = 7
    min_sources = 2
    min_pros = 3

    for brand_file in brand_files:
        with open(brand_file) as f:
            data = json.load(f)

        for product in data.get("products", []):
            product_id = f"{brand_file.stem}/{product.get('id', 'unknown')}"
            pill = product.get("pill_data", {})

            # Test specs
            specs = pill.get("specs", {})
            spec_count = len(specs)
            if spec_count >= min_specs:
                results.pass_test(f"{product_id} specs",
                                  f"{spec_count} specs ✓")
            else:
                results.warn_test(f"{product_id} specs",
                                  f"{spec_count} specs (min: {min_specs})")

            # Test sources
            sources = pill.get("context_meta", {}).get("sources_of_truth", [])
            source_count = len(sources)
            if source_count >= min_sources:
                results.pass_test(f"{product_id} sources",
                                  f"{source_count} sources ✓")
            else:
                results.warn_test(
                    f"{product_id} sources", f"{source_count} sources (min: {min_sources})")

            # Test pros/cons/tips
            context = pill.get("context_meta", {})
            pros = context.get("pros", [])
            cons = context.get("cons", [])
            tips = context.get("tips", [])

            if len(pros) >= min_pros:
                results.pass_test(f"{product_id} pros", f"{len(pros)} pros ✓")
            else:
                results.warn_test(f"{product_id} pros",
                                  f"{len(pros)} pros (min: {min_pros})")

            # Test validation pipeline
            pipeline = pill.get("validation_pipeline", {})
            required_steps = {"step1_official", "step2_commercial", "step3_context",
                              "step4_cross_validation", "step5_published"}
            if required_steps.issubset(set(pipeline.keys())):
                results.pass_test(f"{product_id} pipeline", f"5 steps ✓")
            else:
                missing = required_steps - set(pipeline.keys())
                results.fail_test(f"{product_id} pipeline",
                                  f"Missing steps: {missing}")

            # Test confidence score
            confidence = pill.get("ui_meta", {}).get("y_axis_score", 0)
            if 50 <= confidence <= 100:
                results.pass_test(f"{product_id} confidence",
                                  f"Score: {confidence}/100")
            else:
                results.fail_test(f"{product_id} confidence",
                                  f"Invalid score: {confidence}")

            # Test badges
            badges = pill.get("ui_meta", {}).get("badges", [])
            if "DIAMOND" in badges:
                results.pass_test(f"{product_id} badge", "DIAMOND ✓")
            else:
                results.warn_test(f"{product_id} badge",
                                  f"Expected DIAMOND, got {badges}")

# =============================================================================
# TEST SUITE 3: VALIDATION PIPELINE INTEGRITY
# =============================================================================


def test_validation_pipeline(results: TestResult):
    """Validate the 5-step refinery pipeline structure"""
    print(
        f"\n{Colors.HEADER}{Colors.BOLD}TEST 3: VALIDATION PIPELINE INTEGRITY{Colors.ENDC}")
    print("-" * 60)

    data_dir = ROOT_DIR / "frontend" / "public" / "data"
    brand_files = [f for f in data_dir.glob(
        "*.json") if f.name != "index.json"]

    step_names = ["step1_official", "step2_commercial", "step3_context",
                  "step4_cross_validation", "step5_published"]
    required_fields = {"status", "data_quality", "timestamp"}

    for brand_file in brand_files:
        with open(brand_file) as f:
            data = json.load(f)

        for product in data.get("products", []):
            product_id = f"{brand_file.stem}/{product.get('id', 'unknown')}"
            pipeline = product.get("pill_data", {}).get(
                "validation_pipeline", {})

            for step_name in step_names:
                if step_name not in pipeline:
                    results.fail_test(
                        f"{product_id} has {step_name}", "Missing step")
                    continue

                step = pipeline[step_name]

                # Validate status
                valid_statuses = {"complete", "partial", "pending", "failed"}
                status = step.get("status")
                if status in valid_statuses:
                    results.pass_test(
                        f"{product_id} {step_name} status", status)
                else:
                    results.fail_test(f"{product_id} {step_name} status",
                                      f"Invalid: {status}")

                # Validate quality
                quality = step.get("data_quality", 0)
                if 0 <= quality <= 100:
                    results.pass_test(
                        f"{product_id} {step_name} quality", f"{quality}%")
                else:
                    results.fail_test(f"{product_id} {step_name} quality",
                                      f"Out of range: {quality}")

                # Validate timestamp
                timestamp = step.get("timestamp")
                if timestamp and isinstance(timestamp, str) and "T" in timestamp:
                    results.pass_test(
                        f"{product_id} {step_name} timestamp", timestamp[:10])
                else:
                    results.warn_test(f"{product_id} {step_name} timestamp",
                                      "Invalid or missing")

# =============================================================================
# TEST SUITE 4: SOURCE ATTRIBUTION
# =============================================================================


def test_source_attribution(results: TestResult):
    """Validate source of truth tracking and verification"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}TEST 4: SOURCE ATTRIBUTION{Colors.ENDC}")
    print("-" * 60)

    data_dir = ROOT_DIR / "frontend" / "public" / "data"
    brand_files = [f for f in data_dir.glob(
        "*.json") if f.name != "index.json"]

    valid_types = {"manufacturer", "expert",
                   "review", "community", "verified_retailer"}

    for brand_file in brand_files:
        with open(brand_file) as f:
            data = json.load(f)

        for product in data.get("products", []):
            product_id = f"{brand_file.stem}/{product.get('id', 'unknown')}"
            sources = product.get("pill_data", {}).get(
                "context_meta", {}).get("sources_of_truth", [])

            if not sources:
                results.warn_test(f"{product_id} sources", "No sources found")
                continue

            for i, source in enumerate(sources):
                source_name = source.get("name", "Unknown")
                source_type = source.get("type", "unknown")
                verified = source.get("verified", False)

                if source_type in valid_types:
                    results.pass_test(
                        f"{product_id} source[{i}] type", source_type)
                else:
                    results.warn_test(f"{product_id} source[{i}] type",
                                      f"Unknown: {source_type}")

                if verified:
                    results.pass_test(f"{product_id} source[{i}] verification",
                                      f"{source_name} verified")
                else:
                    results.warn_test(f"{product_id} source[{i}] verification",
                                      f"{source_name} unverified")

                confidence = source.get("confidence", 0)
                if 0 <= confidence <= 100:
                    results.pass_test(f"{product_id} source[{i}] confidence",
                                      f"{confidence}%")
                else:
                    results.fail_test(f"{product_id} source[{i}] confidence",
                                      f"Invalid: {confidence}")

# =============================================================================
# TEST SUITE 5: DATA TYPE VALIDATION
# =============================================================================


def test_data_types(results: TestResult):
    """Validate data types match expected schema"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}TEST 5: DATA TYPE VALIDATION{Colors.ENDC}")
    print("-" * 60)

    data_dir = ROOT_DIR / "frontend" / "public" / "data"
    brand_files = [f for f in data_dir.glob(
        "*.json") if f.name != "index.json"]

    for brand_file in brand_files:
        with open(brand_file) as f:
            data = json.load(f)

        # Validate brand_identity types
        brand = data.get("brand_identity", {})
        if isinstance(brand.get("id"), str):
            results.pass_test(f"{brand_file.stem} brand.id type", "string ✓")

        if isinstance(brand.get("product_count"), int):
            results.pass_test(
                f"{brand_file.stem} brand.product_count type", "int ✓")

        # Validate product types
        for product in data.get("products", []):
            product_id = f"{brand_file.stem}/{product.get('id', 'unknown')}"

            if isinstance(product.get("price"), (int, float, type(None))):
                results.pass_test(f"{product_id} price type", "number/null ✓")
            else:
                results.fail_test(f"{product_id} price type",
                                  f"Got {type(product.get('price'))}")

            # Validate pill_data.specs types
            specs = product.get("pill_data", {}).get("specs", {})
            for spec_key, spec_val in specs.items():
                if isinstance(spec_val, (str, int, float, bool)):
                    pass  # Valid
                else:
                    results.warn_test(f"{product_id} spec '{spec_key}' type",
                                      f"Unexpected: {type(spec_val)}")

            # Validate lists
            pros = product.get("pill_data", {}).get(
                "context_meta", {}).get("pros", [])
            if isinstance(pros, list) and all(isinstance(p, str) for p in pros):
                results.pass_test(f"{product_id} pros type", f"list[str] ✓")

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================


def run_all_tests():
    """Run complete backend validation suite"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔" + "="*58 + "╗")
    print("║     HALILIT SUPPORT CENTER - BACKEND VALIDATION SUITE     ║")
    print("╚" + "="*58 + "╝")
    print(f"{Colors.ENDC}")

    results = TestResult()

    test_data_files(results)
    test_product_completeness(results)
    test_validation_pipeline(results)
    test_source_attribution(results)
    test_data_types(results)

    success = results.summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
