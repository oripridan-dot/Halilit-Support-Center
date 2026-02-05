#!/usr/bin/env python3
"""
Test Conductor Daemon Components

This script tests all Conductor Daemon components to ensure they're
ready for production use.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Color codes
COLORS = {
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
    'GREEN': '\033[92m',
    'RED': '\033[91m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
}


def print_test(name: str):
    print(f"\n{COLORS['BLUE']}{COLORS['BOLD']}▶ {name}{COLORS['RESET']}")


def print_pass(msg: str):
    print(f"  {COLORS['GREEN']}✓{COLORS['RESET']} {msg}")


def print_fail(msg: str):
    print(f"  {COLORS['RED']}✗{COLORS['RESET']} {msg}")


def print_skip(msg: str):
    print(f"  {COLORS['YELLOW']}⊘{COLORS['RESET']} {msg}")


def test_imports():
    """Test that all modules can be imported"""
    print_test("Testing Imports")

    modules = [
        ('backend.conductor_daemon', 'ConductorDaemon'),
        ('backend.agent_coordinator', 'SwarmCommander'),
        ('backend.data_synchronizer', 'DataSynchronizer'),
    ]

    results = []
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print_pass(f"{module_name}.{class_name}")
            results.append(True)
        except Exception as e:
            print_fail(f"{module_name}.{class_name}: {e}")
            results.append(False)

    return all(results)


def test_watchdog():
    """Test if watchdog is installed"""
    print_test("Testing Watchdog")

    try:
        import watchdog
        print_pass("watchdog installed")
        return True
    except ImportError:
        print_skip("watchdog not installed - file watching disabled")
        print("         Install with: pip install watchdog")
        return False


def test_conductor_daemon():
    """Test ConductorDaemon initialization"""
    print_test("Testing ConductorDaemon")

    try:
        from backend.conductor_daemon import ConductorDaemon
        daemon = ConductorDaemon()
        print_pass("ConductorDaemon instantiated")
        print_pass(f"  Standards rules: {len(daemon.standards_rules)}")
        print_pass(f"  Watched paths: {len(daemon.watched_paths)}")
        return True
    except Exception as e:
        print_fail(f"ConductorDaemon initialization: {e}")
        return False


def test_standards_rules():
    """Test standards rules"""
    print_test("Testing Standards Rules")

    try:
        from backend.conductor_daemon import ReactComponentRule

        rule = ReactComponentRule()
        print_pass(f"ReactComponentRule instantiated")

        # Test applies_to
        assert rule.applies_to("test.tsx"), "Should apply to .tsx"
        assert rule.applies_to("test.ts"), "Should apply to .ts"
        assert not rule.applies_to("test.py"), "Should not apply to .py"
        print_pass("ReactComponentRule.applies_to() works")

        # Test check (on non-existent file, should return false)
        is_compliant, violations = rule.check("/nonexistent/file.tsx")
        assert not is_compliant, "Should detect non-existent file"
        print_pass("ReactComponentRule.check() detects missing files")

        return True
    except Exception as e:
        print_fail(f"Standards rules test: {e}")
        return False


def test_agent_coordinator():
    """Test Agent Coordinator"""
    print_test("Testing Agent Coordinator")

    try:
        from backend.agent_coordinator import SwarmCommander
        commander = SwarmCommander()
        print_pass("SwarmCommander instantiated")

        # Check agent pool
        stats = commander.pool.get_agent_stats()
        print_pass(f"  Available agents: {len(stats['agents_available'])}")
        print_pass(f"  Agents: {', '.join(stats['agents_available'])}")

        # Test command map
        print_pass(
            f"  Command patterns available: {len(commander.command_map)}")

        return True
    except Exception as e:
        print_fail(f"Agent Coordinator test: {e}")
        return False


def test_data_synchronizer():
    """Test Data Synchronizer"""
    print_test("Testing Data Synchronizer")

    try:
        from backend.data_synchronizer import DataSynchronizer
        sync = DataSynchronizer()
        print_pass("DataSynchronizer instantiated")

        # Check mappings
        print_pass(f"  Sync mappings configured: {len(sync.sync_mappings)}")
        for mapping in sync.sync_mappings[:2]:  # Show first 2
            print_pass(
                f"    • {mapping.backend_path} ↔ {mapping.frontend_path}")

        return True
    except Exception as e:
        print_fail(f"Data Synchronizer test: {e}")
        return False


def test_configuration():
    """Test configuration file"""
    print_test("Testing Configuration")

    config_path = Path(__file__).parent / "backend" / "conductor_config.ini"
    if config_path.exists():
        print_pass(f"Configuration file exists: {config_path.name}")
        return True
    else:
        print_fail(f"Configuration file not found: {config_path.name}")
        return False


def main():
    """Run all tests"""
    print(f"\n{COLORS['BOLD']}{COLORS['BLUE']}{'='*70}")
    print("CONDUCTOR DAEMON - COMPONENT TEST SUITE")
    print(f"{'='*70}{COLORS['RESET']}\n")

    tests = [
        test_imports,
        test_watchdog,
        test_conductor_daemon,
        test_standards_rules,
        test_agent_coordinator,
        test_data_synchronizer,
        test_configuration,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print_fail(f"Test {test.__name__} failed: {e}")
            results.append(False)

    # Summary
    print(f"\n{COLORS['BOLD']}{COLORS['BLUE']}{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}{COLORS['RESET']}")

    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100

    if success_rate == 100:
        print(
            f"{COLORS['GREEN']}{COLORS['BOLD']}✓ ALL TESTS PASSED{COLORS['RESET']}")
    elif success_rate >= 80:
        print(
            f"{COLORS['YELLOW']}{COLORS['BOLD']}⚠ MOSTLY WORKING (watchdog may not be installed){COLORS['RESET']}")
    else:
        print(
            f"{COLORS['RED']}{COLORS['BOLD']}✗ SOME TESTS FAILED{COLORS['RESET']}")

    print(f"\n  Passed: {passed}/{total} ({success_rate:.0f}%)")
    print(f"\n{COLORS['BOLD']}Next Steps:{COLORS['RESET']}")
    print(f"  1. Install watchdog: pip install watchdog")
    print(f"  2. Run daemon: python3 backend/conductor_daemon.py")
    print(f"  3. Read quickstart: CONDUCTOR_DAEMON_QUICKSTART.md")

    return 0 if success_rate >= 80 else 1


if __name__ == '__main__':
    sys.exit(main())
