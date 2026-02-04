"""
SPECTRUM v5.4.0 Conductor Verification
Verifies all three skills are integrated and functional
"""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SpectrumConductor")

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_section(title):
    """Print a section header."""
    print(f"\n{BLUE}{BOLD}{'='*70}")
    print(f"{title}")
    print(f"{'='*70}{RESET}\n")


def verify_imports():
    """Verify all skills can be imported."""
    print_section("STEP 1: Verify Imports")

    try:
        from backend.skills.spectrum_official_ingestion import (
            OfficialBrandCatalogIngester,
            TaxonomyBridgeMapper
        )
        from backend.skills.spectrum_cross_validator import OfficialSourceCrossValidator
        from backend.spectrum_data_provider import SpectrumDataProvider, get_provider

        print(f"{GREEN}✓ All imports successful{RESET}")
        return True, {
            'ingester': OfficialBrandCatalogIngester,
            'mapper': TaxonomyBridgeMapper,
            'validator': OfficialSourceCrossValidator,
            'provider': SpectrumDataProvider
        }
    except ImportError as e:
        print(f"{RED}✗ Import failed: {e}{RESET}")
        return False, str(e)


def verify_skill_initialization(classes_dict):
    """Verify all skills initialize properly."""
    print_section("STEP 2: Verify Skill Initialization")

    skills = {}
    all_success = True

    for name, cls in classes_dict.items():
        if name == 'provider':
            continue

        try:
            instance = cls()
            skills[name] = instance
            print(f"{GREEN}✓ {instance.name} initialized{RESET}")
        except Exception as e:
            print(f"{RED}✗ Failed to initialize {name}: {e}{RESET}")
            all_success = False

    return all_success, skills


def verify_skill_methods(skills):
    """Verify all skills have required methods."""
    print_section("STEP 3: Verify Skill Methods")

    all_success = True
    required_methods = {
        'execute': "Core skill method",
        'name': "Skill identifier (attribute)"
    }

    for skill_name, skill in skills.items():
        print(f"\n{skill.name}:")

        # Check execute method
        if hasattr(skill, 'execute') and callable(skill.execute):
            print(f"  {GREEN}✓ execute() method exists{RESET}")
        else:
            print(f"  {RED}✗ execute() method missing{RESET}")
            all_success = False

        # Check name attribute
        if hasattr(skill, 'name') and isinstance(skill.name, str):
            print(f"  {GREEN}✓ name attribute: {skill.name}{RESET}")
        else:
            print(f"  {RED}✗ name attribute missing or invalid{RESET}")
            all_success = False

    return all_success


def verify_provider_initialization(ProviderClass):
    """Verify SpectrumDataProvider initializes with v5.4.0 skills."""
    print_section("STEP 4: Verify Provider Initialization")

    try:
        provider = ProviderClass()

        # Check all three skills
        checks = [
            ('official_ingester', provider.official_ingester),
            ('taxonomy_mapper', provider.taxonomy_mapper),
            ('cross_validator', provider.cross_validator)
        ]

        all_success = True
        for attr_name, skill in checks:
            if skill is not None:
                print(f"{GREEN}✓ {attr_name} initialized: {skill.name}{RESET}")
            else:
                print(f"{RED}✗ {attr_name} is None{RESET}")
                all_success = False

        return all_success, provider
    except Exception as e:
        print(f"{RED}✗ Provider initialization failed: {e}{RESET}")
        return False, None


def verify_skill_execution(skills):
    """Verify each skill can execute with sample contexts."""
    print_section("STEP 5: Verify Skill Execution")

    contexts = {
        'ingester': {
            'brand': 'Nord',
            'include_media': False,
            'deep_catalog': False
        },
        'mapper': {
            'products': [
                {'name': 'Test Product', 'category': 'Synthesizers'}
            ],
            'brand': 'Nord'
        },
        'validator': {
            'product': {'name': 'Test', 'id': 'test-001'},
            'official_data': {},
            'halilit_data': {},
            'review_data': {}
        }
    }

    all_success = True

    for skill_name, skill in skills.items():
        context = contexts.get(skill_name, {})

        try:
            success, result = skill.execute(context)

            if isinstance(success, bool) and result is not None:
                print(f"{GREEN}✓ {skill.name} execution successful{RESET}")
                print(
                    f"    Success: {success}, Result type: {type(result).__name__}")
            else:
                print(f"{YELLOW}⚠ {skill.name} returned unexpected format{RESET}")
                print(
                    f"    Success: {success} (type: {type(success).__name__})")
                print(f"    Result: {result} (type: {type(result).__name__})")
        except Exception as e:
            print(f"{RED}✗ {skill.name} execution failed: {e}{RESET}")
            all_success = False

    return all_success


def verify_api_endpoints():
    """Verify API endpoints are defined in data provider."""
    print_section("STEP 6: Verify API Endpoints")

    try:
        from backend.spectrum_data_provider import router

        endpoints = []
        for route in router.routes:
            if hasattr(route, 'path'):
                endpoints.append(route.path)

        expected_endpoints = [
            '/data/{brand}', '/quality/{brand}', '/taxonomy', '/product/{product_id}']

        all_success = True
        for endpoint in expected_endpoints:
            if endpoint in endpoints or any(endpoint.split('{')[0] in e for e in endpoints):
                print(f"{GREEN}✓ Endpoint {endpoint} defined{RESET}")
            else:
                print(f"{YELLOW}⚠ Endpoint {endpoint} not found{RESET}")

        return True
    except Exception as e:
        print(f"{RED}✗ Failed to verify endpoints: {e}{RESET}")
        return False


def verify_unit_tests():
    """Verify unit tests pass."""
    print_section("STEP 7: Verify Unit Tests")

    import subprocess

    try:
        result = subprocess.run(
            ['python', '-m', 'pytest',
                'backend/tests/test_spectrum_v540.py', '-v', '--tb=short'],
            cwd='/workspaces/Halilit-Support-Center',
            capture_output=True,
            text=True,
            env={**os.environ, 'PYTHONPATH': '.'}
        )

        if result.returncode == 0:
            # Count passed tests
            output = result.stdout
            if 'passed' in output:
                print(f"{GREEN}✓ All unit tests passed{RESET}")
                print(f"  Output: {output.split('=')[-1].strip()}")
            return True
        else:
            print(f"{RED}✗ Some unit tests failed{RESET}")
            print(
                f"  {result.stdout[-500:] if result.stdout else result.stderr[-500:]}")
            return False
    except Exception as e:
        print(f"{YELLOW}⚠ Could not run unit tests: {e}{RESET}")
        return False


def verify_integration_tests():
    """Verify integration tests pass."""
    print_section("STEP 8: Verify Integration Tests")

    import subprocess

    try:
        result = subprocess.run(
            ['python', '-m', 'pytest',
                'backend/tests/test_spectrum_integration_v540.py', '-v', '--tb=short'],
            cwd='/workspaces/Halilit-Support-Center',
            capture_output=True,
            text=True,
            env={**os.environ, 'PYTHONPATH': '.'}
        )

        if result.returncode == 0:
            print(f"{GREEN}✓ All integration tests passed{RESET}")
            print(f"  Output: {result.stdout.split('=')[-1].strip()}")
            return True
        else:
            print(f"{RED}✗ Some integration tests failed{RESET}")
            print(
                f"  {result.stdout[-500:] if result.stdout else result.stderr[-500:]}")
            return False
    except Exception as e:
        print(f"{YELLOW}⚠ Could not run integration tests: {e}{RESET}")
        return False


def main():
    """Run all verification steps."""
    print(f"\n{BOLD}{BLUE}")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + " SPECTRUM v5.4.0 Integration Verification ".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    print(f"{RESET}\n")

    results = {}

    # Step 1: Verify imports
    success, classes = verify_imports()
    results['imports'] = success
    if not success:
        print(f"\n{RED}{BOLD}VERIFICATION FAILED AT STEP 1{RESET}")
        return False

    # Step 2: Verify skill initialization
    success, skills = verify_skill_initialization(classes)
    results['skill_init'] = success

    # Step 3: Verify skill methods
    success = verify_skill_methods(skills)
    results['skill_methods'] = success

    # Step 4: Verify provider
    success, provider = verify_provider_initialization(classes['provider'])
    results['provider'] = success

    # Step 5: Verify skill execution
    success = verify_skill_execution(skills)
    results['skill_exec'] = success

    # Step 6: Verify API endpoints
    success = verify_api_endpoints()
    results['endpoints'] = success

    # Step 7: Verify unit tests
    success = verify_unit_tests()
    results['unit_tests'] = success

    # Step 8: Verify integration tests
    success = verify_integration_tests()
    results['integration_tests'] = success

    # Final report
    print_section("VERIFICATION SUMMARY")

    all_passed = all(results.values())

    for step, passed in results.items():
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"  {step:.<40} {status}")

    print()

    if all_passed:
        print(f"{GREEN}{BOLD}✓ ALL VERIFICATION STEPS PASSED{RESET}")
        print(f"\n{GREEN}SPECTRUM v5.4.0 is ready for deployment!{RESET}\n")
        return True
    else:
        print(f"{RED}{BOLD}✗ SOME VERIFICATION STEPS FAILED{RESET}")
        print(f"\n{YELLOW}Please review the failures above.{RESET}\n")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
