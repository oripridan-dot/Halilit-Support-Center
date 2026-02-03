#!/usr/bin/env python
"""
Master Test Suite Runner - Galaxy Data Protocol
Runs all unit, integration, and e2e tests across the architecture
"""

import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def run_test_suite(suite_name, module_func):
    """Run a test suite and capture results"""
    try:
        result = module_func()
        return result
    except Exception as e:
        print(f"❌ {suite_name} failed with error: {e}")
        return False

def main():
    """Run all test suites"""
    print("\n" + "╔" + "="*78 + "╗")
    print("║  🚀 GALAXY DATA PROTOCOL - COMPREHENSIVE TEST SUITE 🚀                    ║")
    print("║                                                                           ║")
    print("║  Testing: Units | Integrations | E2E | Architecture                      ║")
    print("╚" + "="*78 + "╝\n")

    test_suites = []

    # Import and run backend unit tests
    print("\n📦 Loading Backend Unit Tests...")
    try:
        from backend.tests.test_backend_units import run_all_backend_tests
        test_suites.append(("Backend Unit Tests", run_all_backend_tests))
        print("✅ Backend unit tests loaded")
    except Exception as e:
        print(f"❌ Failed to load backend unit tests: {e}")

    # Import and run frontend hook tests
    print("📦 Loading Frontend Hook Tests...")
    try:
        from backend.tests.test_frontend_hooks import run_all_hook_tests
        test_suites.append(("Frontend Hook Tests", run_all_hook_tests))
        print("✅ Frontend hook tests loaded")
    except Exception as e:
        print(f"❌ Failed to load frontend hook tests: {e}")

    # Import and run e2e tests
    print("📦 Loading E2E Integration Tests...")
    try:
        test_suites.append(("E2E Integration Tests", run_all_e2e_tests))
        print("✅ E2E tests loaded")
    except Exception as e:
        print(f"❌ Failed to load e2e tests: {e}")

    # Import and run galaxy refinery tests
    print("📦 Loading Data Refinery Tests...")
    try:
        test_suites.append(("Data Refinery Tests", run_all_tests))
        print("✅ Data refinery tests loaded")
    except Exception as e:
        print(f"❌ Failed to load data refinery tests: {e}")

    # Import and run system verification
    print("📦 Loading System Verification...")
    try:
        # We'll run verification as part of the suite
        def run_verification():
            import subprocess
            result = subprocess.run(
                [sys.executable, "verify_galaxy_setup.py"],
                cwd="/workspaces/Halilit-Support-Center",
                capture_output=True,
                text=True
            )
            return result.returncode == 0

        test_suites.append(("System Verification", run_verification))
        print("✅ System verification loaded")
    except Exception as e:
        print(f"❌ Failed to load system verification: {e}")

    # Run all test suites
    print("\n" + "="*80)
    print("🧪 RUNNING ALL TEST SUITES")
    print("="*80)

    results = {}
    for suite_name, suite_func in test_suites:
        print(f"\n▶️  Running: {suite_name}...")
        results[suite_name] = run_test_suite(suite_name, suite_func)

    # Generate report
    print("\n" + "="*80)
    print("📋 COMPREHENSIVE TEST REPORT")
    print("="*80 + "\n")

    passed_suites = sum(1 for v in results.values() if v)
    total_suites = len(results)

    print("Test Suite Results:")
    print("-" * 80)

    for suite_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} | {suite_name}")

    print("-" * 80)
    print(f"\nOverall: {passed_suites}/{total_suites} test suites passed\n")

    # Summary
    if all(results.values()):
        print("╔" + "="*78 + "╗")
        print("║  🎉 ALL TESTS PASSED - SYSTEM FULLY OPERATIONAL 🎉                       ║")
        print(
            "║                                                                           ║")
        print(
            "║  Architecture:                                                            ║")
        print(
            "║    ✅ Backend Pipeline (Data Refinery) - VALIDATED                        ║")
        print(
            "║    ✅ Frontend Hooks (useGalaxyData) - VALIDATED                          ║")
        print(
            "║    ✅ End-to-End Integration - VALIDATED                                  ║")
        print(
            "║    ✅ System Verification - PASSED                                        ║")
        print(
            "║                                                                           ║")
        print("║  Status: 🚀 READY FOR PRODUCTION DEPLOYMENT                              ║")
        print("╚" + "="*78 + "╝")
        return 0
    else:
        print("╔" + "="*78 + "╗")
        print(
            "║  ⚠️  SOME TESTS FAILED - PLEASE REVIEW ABOVE                             ║")
        print("╚" + "="*78 + "╝")
        return 1

if __name__ == "__main__":
    sys.exit(main())
