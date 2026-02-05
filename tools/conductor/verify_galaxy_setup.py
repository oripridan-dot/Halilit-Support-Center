#!/usr/bin/env python
"""
Galaxy System Verification Script
Checks that all components of the Galaxy Data Protocol are operational.
"""

import json
import sys
from pathlib import Path

def check_backend_files():
    """Verify backend pipeline files exist."""
    print("\n" + "="*60)
    print("🔍 BACKEND VERIFICATION")
    print("="*60)

    backend_dir = Path("/workspaces/Halilit-Support-Center/backend")

    files_to_check = [
        "pipeline/__init__.py",
        "pipeline/data_refinery.py",
        "tests/test_galaxy_refinery.py",
    ]

    all_exist = True
    for file in files_to_check:
        file_path = backend_dir / file
        exists = file_path.exists() and file_path.stat().st_size > 0
        status = "✅" if exists else "❌"
        print(f"{status} {file} ({file_path.stat().st_size if exists else 0} bytes)")
        all_exist = all_exist and exists

    return all_exist

def check_frontend_files():
    """Verify frontend core files exist and are not empty."""
    print("\n" + "="*60)
    print("🎨 FRONTEND VERIFICATION")
    print("="*60)

    frontend_dir = Path("/workspaces/Halilit-Support-Center/frontend")

    critical_files = [
        "package.json",
        "vite.config.ts",
        "index.html",
        "src/main.tsx",
        "src/App.tsx",
        "src/types/galaxy.ts",
        "src/types/galaxy-schema.ts",
        "src/hooks/useGalaxyData.ts",
    ]

    all_exist = True
    for file in critical_files:
        file_path = frontend_dir / file
        exists = file_path.exists() and file_path.stat().st_size > 0
        status = "✅" if exists else "❌"
        size = file_path.stat().st_size if exists else 0
        print(f"{status} {file} ({size} bytes)")
        all_exist = all_exist and exists

    return all_exist

def check_data_files():
    """Verify data files exist and are valid JSON."""
    print("\n" + "="*60)
    print("📊 DATA FILES VERIFICATION")
    print("="*60)

    frontend_dir = Path("/workspaces/Halilit-Support-Center/frontend")
    data_file = frontend_dir / "public" / "data" / "galaxy_db.json"

    if not data_file.exists():
        print(f"❌ galaxy_db.json not found at {data_file}")
        return False

    try:
        with open(data_file) as f:
            data = json.load(f)

        # Validate structure
        required_keys = {'generatedAt', 'version',
                         'stats', 'products', 'categories'}
        if not required_keys.issubset(data.keys()):
            print(
                f"❌ Missing keys in galaxy_db.json: {required_keys - data.keys()}")
            return False

        file_size = data_file.stat().st_size
        product_count = len(data.get('products', []))
        brand_count = data.get('stats', {}).get('brandsCount', 0)

        print(f"✅ galaxy_db.json ({file_size} bytes)")
        print(f"   - Products: {product_count}")
        print(f"   - Brands: {brand_count}")
        print(f"   - Categories: {len(data.get('categories', {}))}")
        print(f"   - Generated: {data.get('generatedAt')}")
        print(f"   - Version: {data.get('version')}")

        return True
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def check_imports():
    """Verify that Python modules can be imported."""
    print("\n" + "="*60)
    print("🐍 PYTHON IMPORTS VERIFICATION")
    print("="*60)

    try:
        sys.path.insert(0, "/workspaces/Halilit-Support-Center")

        # Try importing the refinery
        from backend.pipeline.data_refinery import DataRefinery
        print("✅ backend.pipeline.data_refinery.DataRefinery")

        # Create an instance to verify it works
        refinery = DataRefinery()
        print("✅ DataRefinery instantiation successful")

        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_typescript_types():
    """Verify TypeScript type definitions are valid."""
    print("\n" + "="*60)
    print("📝 TYPESCRIPT TYPES VERIFICATION")
    print("="*60)

    type_files = [
        "/workspaces/Halilit-Support-Center/frontend/src/types/galaxy.ts",
        "/workspaces/Halilit-Support-Center/frontend/src/types/galaxy-schema.ts",
    ]

    all_ok = True
    for file in type_files:
        file_path = Path(file)
        exists = file_path.exists() and file_path.stat().st_size > 0
        status = "✅" if exists else "❌"
        name = file_path.name

        if exists:
            with open(file_path) as f:
                content = f.read()
                has_exports = "export" in content
                has_interfaces = "interface" in content
                status = "✅" if (has_exports and has_interfaces) else "⚠️"

        print(f"{status} {name}")
        all_ok = all_ok and exists

    return all_ok

def main():
    """Run all verification checks."""
    print("\n" + "╔" + "="*58 + "╗")
    print("║  🚀 GALAXY DATA PROTOCOL - SYSTEM VERIFICATION 🚀       ║")
    print("╚" + "="*58 + "╝")

    checks = [
        ("Backend Files", check_backend_files),
        ("Frontend Files", check_frontend_files),
        ("Data Files", check_data_files),
        ("Python Imports", check_imports),
        ("TypeScript Types", check_typescript_types),
    ]

    results = {}
    for name, check_fn in checks:
        try:
            results[name] = check_fn()
        except Exception as e:
            print(f"\n❌ {name} check failed: {e}")
            results[name] = False

    # Final report
    print("\n" + "="*60)
    print("📋 VERIFICATION REPORT")
    print("="*60)

    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    all_passed = all(results.values())

    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED - SYSTEM READY FOR DEPLOYMENT 🎉")
        print("="*60)
        print("\n📚 Next steps:")
        print("  1. cd frontend && npm install")
        print("  2. cd frontend && npm run dev")
        print("  3. Open http://localhost:5173")
        print("\n")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED - PLEASE FIX ABOVE ISSUES")
        print("="*60 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
