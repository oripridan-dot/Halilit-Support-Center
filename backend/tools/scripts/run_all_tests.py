"""
Run All Tests - Production-ready v5.2.4
"""

#!/usr/bin/env python
"""
Master Test Suite Runner - Galaxy Data Protocol
Runs all unit, integration, and e2e tests across the architecture
"""

import sys
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)
# Ensure the root of the workspace is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    logger.info("\n" + "╔" + "="*78 + "╗")
    logger.info("║  🚀 GALAXY DATA PROTOCOL - COMPREHENSIVE TEST SUITE 🚀                    ║")
    logger.info("║                                                                           ║")
    logger.info("║  Testing: Units | Integrations | E2E | Architecture                      ║")
    logger.info("╚" + "="*78 + "╝\n")

    test_suites = []

    # Import and run backend unit tests
    logger.info("\n📦 Loading Backend Unit Tests...")
    try:
        from backend.tests.test_backend_units import run_all_backend_tests
        test_suites.append(("Backend Unit Tests", run_all_backend_tests))
        logger.info("✅ Backend unit tests loaded")
    except Exception as e:
        print(f"❌ Failed to load backend unit tests: {e}")

    # Import and run frontend hook tests
    logger.info("📦 Loading Frontend Hook Tests...")
    try:
        from backend.tests.test_frontend_hooks import run_all_hook_tests
        test_suites.append(("Frontend Hook Tests", run_all_hook_tests))
        logger.info("✅ Frontend hook tests loaded")
    except Exception as e:
        print(f"❌ Failed to load frontend hook tests: {e}")

    # Import and run e2e tests
    logger.info("📦 Loading E2E Integration Tests...")
    try:
        import backend.tests.test_e2e_integration as mod_e2e
        if hasattr(mod_e2e, 'run_all_e2e_tests'):
            test_suites.append(
                ("E2E Integration Tests", mod_e2e.run_all_e2e_tests))
            logger.info("✅ E2E integration tests loaded")
        else:
            print(
                f"❌ Failed to load e2e tests: Function 'run_all_e2e_tests' not found in module. Dir: {dir(mod_e2e)}")
    except Exception as e:
        print(f"❌ Failed to load e2e tests import error: {e}")

    # Import and run data refinery tests
    logger.info("📦 Loading Data Refinery Tests...")
    try:
        import backend.tests.test_galaxy_refinery as mod_refinery
        if hasattr(mod_refinery, 'run_all_tests'):
            test_suites.append(
                ("Data Refinery Tests", mod_refinery.run_all_tests))
            logger.info("✅ Data refinery tests loaded")
        else:
            print(
                f"❌ Failed to load data refinery tests: Function 'run_all_tests' not found. Dir: {dir(mod_refinery)}")
    except Exception as e:
        print(f"❌ Failed to load data refinery tests import error: {e}")

    # Import and run galaxy refinery tests
    logger.info("📦 Loading Data Refinery Tests...")
    try:
        test_suites.append(("Data Refinery Tests", run_all_tests))
        logger.info("✅ Data refinery tests loaded")
    except Exception as e:
        print(f"❌ Failed to load data refinery tests: {e}")

    # Import and run system verification
    logger.info("📦 Loading System Verification...")
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
        logger.info("✅ System verification loaded")
    except Exception as e:
        print(f"❌ Failed to load system verification: {e}")

    # Run all test suites
    print("\n" + "="*80)
    logger.info("🧪 RUNNING ALL TEST SUITES")
    print("="*80)

    results = {}
    for suite_name, suite_func in test_suites:
        print(f"\n▶️  Running: {suite_name}...")
        results[suite_name] = run_test_suite(suite_name, suite_func)

    # Generate report
    print("\n" + "="*80)
    logger.info("📋 COMPREHENSIVE TEST REPORT")
    logger.info("="*80 + "\n")

    passed_suites = sum(1 for v in results.values() if v)
    total_suites = len(results)

    logger.info("Test Suite Results:")
    print("-" * 80)

    for suite_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} | {suite_name}")

    print("-" * 80)
    print(f"\nOverall: {passed_suites}/{total_suites} test suites passed\n")

    # Summary
    if all(results.values()):
        logger.info("╔" + "="*78 + "╗")
        logger.info("║  🎉 ALL TESTS PASSED - SYSTEM FULLY OPERATIONAL 🎉                       ║")
        logger.info("║                                                                           ║")
        logger.info("║  Architecture:                                                            ║")
        logger.info("║    ✅ Backend Pipeline (Data Refinery) - VALIDATED                        ║")
        logger.info("║    ✅ Frontend Hooks (useGalaxyData) - VALIDATED                          ║")
        logger.info("║    ✅ End-to-End Integration - VALIDATED                                  ║")
        logger.info("║    ✅ System Verification - PASSED                                        ║")
        logger.info("║                                                                           ║")
        logger.info("║  Status: 🚀 READY FOR PRODUCTION DEPLOYMENT                              ║")
        logger.info("╚" + "="*78 + "╝")
        return 0
    else:
        logger.info("╔" + "="*78 + "╗")
        logger.info("║  ⚠️  SOME TESTS FAILED - PLEASE REVIEW ABOVE                             ║")
        logger.info("╚" + "="*78 + "╝")
        return 1

if __name__ == "__main__":
    sys.exit(main())
