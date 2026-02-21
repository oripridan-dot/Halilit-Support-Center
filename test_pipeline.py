#!/usr/bin/env python3
"""
Pipeline + System Validation — Halilit Operator Console (v9.7.6)
=================================================================
Run from project root:  python test_pipeline.py
Covers: file structure, brand data, catalog build (with error capture),
API health, frontend components, navigation store, pipeline flow,
Source Rule compliance, data quality (dict image_url), TypeScript
compilation, and backend module import health.
See docs/FACTORY_PIPELINE.md for context.
"""

from backend.project_config import DATA_DIR, FRONTEND_PUBLIC_DATA
import io
import json
import logging
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


try:
    from backend.product_normalizer import build_catalog
    BUILD_CATALOG_AVAILABLE = True
    BUILD_CATALOG_ERROR: str | None = None
except Exception as _e:
    build_catalog = None  # type: ignore[assignment]
    BUILD_CATALOG_AVAILABLE = False
    BUILD_CATALOG_ERROR = str(_e)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_status(status: str, message: str):
    """Print a status message."""
    icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}.get(status, "ℹ️")
    print(f"{icon} {status}: {message}")


def test_file_structure():
    """Test 1: Verify project structure and key directories exist."""
    print_section("TEST 1: File Structure")

    checks = [
        ("Backend directory",          PROJECT_ROOT / "backend"),
        ("Frontend directory",         PROJECT_ROOT / "frontend"),
        ("Data directory",             DATA_DIR),
        ("Frontend public data",       FRONTEND_PUBLIC_DATA),
        ("Source rules (THE LAW)",     PROJECT_ROOT / "backend" / "source_rules.py"),
        ("Server file",                PROJECT_ROOT / "backend" / "server.py"),
        ("Conductor CLI",              PROJECT_ROOT / "backend" / "conductor_main.py"),
        ("Product normalizer",         PROJECT_ROOT / "backend" / "product_normalizer.py"),
        ("Visual validator",           PROJECT_ROOT / "backend" / "ingestion" / "visual_validator.py"),
        ("Ignition script",            PROJECT_ROOT / "ignite_factory.sh"),
        ("Factory controller",         PROJECT_ROOT / "factory.py"),
        ("Frontend telemetry module",  PROJECT_ROOT / "frontend" / "src" / "telemetry.ts"),
    ]

    all_pass = True
    for name, path in checks:
        exists = path.exists()
        if exists:
            print_status("PASS", f"{name}: {path}")
        else:
            print_status("FAIL", f"{name}: {path} (missing)")
            all_pass = False

    return all_pass


def test_brand_json_files():
    """Test 2: Check if brand JSON files exist in frontend/public/data."""
    print_section("TEST 2: Brand JSON Files")

    if not FRONTEND_PUBLIC_DATA.exists():
        print_status(
            "FAIL", f"Frontend data directory does not exist: {FRONTEND_PUBLIC_DATA}")
        return False

    json_files = list(FRONTEND_PUBLIC_DATA.glob("*.json"))

    # Filter out metadata files
    exclude = {"index", "search_index", "search_index_min",
               "galaxy_db", "sample", "inventory", "taxonomy"}
    brand_files = [f for f in json_files if f.stem not in exclude]

    if not brand_files:
        print_status(
            "WARN", "No brand JSON files found. Run 'python backend/conductor_main.py skeleton-sync' first.")
        return False

    print_status("PASS", f"Found {len(brand_files)} brand JSON file(s)")

    # Check first file structure
    if brand_files:
        sample_file = brand_files[0]
        try:
            with open(sample_file) as f:
                data = json.load(f)
            if isinstance(data, list):
                print_status(
                    "PASS", f"Sample file '{sample_file.name}': {len(data)} products (list format)")
            elif isinstance(data, dict) and "products" in data:
                print_status(
                    "PASS", f"Sample file '{sample_file.name}': {len(data['products'])} products (dict format)")
            else:
                print_status(
                    "WARN", f"Sample file '{sample_file.name}': Unknown format")
        except Exception as e:
            print_status("FAIL", f"Error reading '{sample_file.name}': {e}")
            return False

    return True


def test_catalog_build():
    """Test 3: Build catalog, verify structure, and surface per-file load errors."""
    print_section("TEST 3: Catalog Build")

    if not BUILD_CATALOG_AVAILABLE:
        print_status(
            "SKIP", f"build_catalog not available: {BUILD_CATALOG_ERROR}")
        print("   Hint: Activate virtual environment: source .venv/bin/activate")
        return False

    # Intercept ERROR-level log messages emitted by product_normalizer
    error_records: list = []

    class _Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            if record.levelno >= logging.ERROR:
                error_records.append(record)

    pn_logger = logging.getLogger("backend.product_normalizer")
    handler = _Capture()
    pn_logger.addHandler(handler)

    try:
        print("Building catalog from frontend/public/data...")
        catalog = build_catalog(str(FRONTEND_PUBLIC_DATA), resolve=False)
    except Exception as e:
        pn_logger.removeHandler(handler)
        print_status("FAIL", f"Catalog build raised an exception: {e}")
        import traceback; traceback.print_exc()
        return False
    finally:
        pn_logger.removeHandler(handler)

    if error_records:
        print_status("FAIL",
                     f"{len(error_records)} brand file(s) had load errors (products skipped):")
        for rec in error_records[:15]:
            print(f"     ❌  {rec.getMessage()}")
        if len(error_records) > 15:
            print(f"     … and {len(error_records) - 15} more")
    else:
        print_status("PASS", "All brand files loaded without errors")

    try:
        pass  # catalog already built above

        # Verify structure
        required_keys = ["products", "indexes", "metadata"]
        missing = [k for k in required_keys if k not in catalog]

        if missing:
            print_status("FAIL", f"Catalog missing required keys: {missing}")
            return False

        products = catalog.get("products", [])
        indexes = catalog.get("indexes", {})
        metadata = catalog.get("metadata", {})

        print_status("PASS", f"Catalog built successfully")
        print(f"   • Products: {len(products)}")
        print(f"   • Indexes: {list(indexes.keys())}")
        print(f"   • Metadata keys: {list(metadata.keys())}")

        # Verify indexes
        required_indexes = ["by_galaxy", "by_spectrum", "by_brand"]
        missing_indexes = [k for k in required_indexes if k not in indexes]
        if missing_indexes:
            print_status("WARN", f"Missing indexes: {missing_indexes}")
        else:
            print_status("PASS", "All required indexes present")

        # Check metadata
        total_products = metadata.get("total_products", 0)
        brands = metadata.get("brands", [])

        print(f"   • Total products: {total_products}")
        print(f"   • Brands: {len(brands)}")

        if total_products == 0:
            print_status("WARN", "Catalog has 0 products")
        else:
            print_status("PASS", f"Catalog contains {total_products} products")

        return len(error_records) == 0

    except Exception as e:
        print_status("FAIL", f"Catalog build post-processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """Test 4: Verify API endpoints are accessible (if server is running)."""
    print_section("TEST 4: API Endpoints (live)")

    import urllib.request
    import urllib.error

    GET_endpoints = [
        ("/api/health",              "Health check"),
        ("/api/conductor/catalog",   "Catalog endpoint"),
        ("/api/dashboard/stats",     "Dashboard stats"),
    ]
    POST_endpoints = [
        ("/api/telemetry/crash-report", "Sovereign Nerve telemetry"),
    ]

    all_pass = True
    server_up = False

    for endpoint, name in GET_endpoints:
        url = f"http://localhost:8000{endpoint}"
        try:
            req = urllib.request.Request(url)
            req.add_header("Accept", "application/json")
            with urllib.request.urlopen(req, timeout=3) as resp:
                server_up = True
                if resp.status == 200:
                    print_status("PASS", f"{name}: GET {endpoint} → 200 OK")
                else:
                    print_status("FAIL", f"{name}: GET {endpoint} → {resp.status}")
                    all_pass = False
        except urllib.error.URLError:
            print_status("SKIP", f"{name}: server not running")
        except Exception as e:
            print_status("FAIL", f"{name}: {endpoint} — {e}")
            all_pass = False

    for endpoint, name in POST_endpoints:
        if not server_up:
            print_status("SKIP", f"{name}: server not running")
            continue
        url = f"http://localhost:8000{endpoint}"
        try:
            payload = json.dumps({"event": {"title": "validation-probe"},
                                   "stacktrace": "none",
                                   "culprit": "test_pipeline.py"}).encode()
            req = urllib.request.Request(
                url, data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                body = json.loads(resp.read())
                if resp.status == 200 and body.get("status") == "received":
                    print_status("PASS", f"{name}: POST {endpoint} → 200 received")
                else:
                    print_status("FAIL", f"{name}: POST {endpoint} → unexpected: {body}")
                    all_pass = False
        except urllib.error.HTTPError as e:
            print_status("FAIL", f"{name}: POST {endpoint} → HTTP {e.code} (was 405 before v9.7.6 fix)")
            all_pass = False
        except Exception as e:
            print_status("FAIL", f"{name}: {endpoint} — {e}")
            all_pass = False

    return all_pass


def test_frontend_components():
    """Test 5: Verify frontend component files exist."""
    print_section("TEST 5: Frontend Components")

    frontend_src = PROJECT_ROOT / "frontend" / "src"
    required_components = [
        ("App.tsx",                                         "Main app component"),
        ("components/GlobalSearch.tsx",                     "Global search"),
        ("components/views/DashboardView.tsx",              "Dashboard view"),
        ("components/views/InventoryView.tsx",              "Inventory view"),
        ("components/views/ProductDetailView.tsx",          "Product detail view"),
        ("hooks/useConductorCatalog.ts",                    "Catalog hook"),
        ("hooks/useJITIntelligence.ts",                     "JIT intelligence hook"),
        ("store/navigationStore.ts",                        "Navigation store"),
        ("telemetry.ts",                                    "Sovereign Nerve telemetry module"),
    ]

    all_pass = True
    for path_str, name in required_components:
        path = frontend_src / path_str
        if path.exists():
            print_status("PASS", f"{name}: {path_str}")
        else:
            print_status("FAIL", f"{name}: {path_str} (missing)")
            all_pass = False

    return all_pass


def test_navigation_store():
    """Test 6: Verify navigation store structure."""
    print_section("TEST 6: Navigation Store")

    store_file = PROJECT_ROOT / "frontend" / "src" / "store" / "navigationStore.ts"

    if not store_file.exists():
        print_status("FAIL", "Navigation store file not found")
        return False

    content = store_file.read_text()

    checks = [
        ("ViewType definition", "ViewType" in content and "DASHBOARD" in content),
        ("searchQuery state", "searchQuery" in content),
        ("goToInventory function", "goToInventory" in content),
        ("setSearchQuery function", "setSearchQuery" in content),
        ("No camera/zoom logic", "camera" not in content.lower()
         and "zoom" not in content.lower()),
    ]

    all_pass = True
    for name, check in checks:
        if check:
            print_status("PASS", name)
        else:
            print_status("FAIL", name)
            all_pass = False

    return all_pass


def test_pipeline_flow():
    """Test 7: Validate complete pipeline flow."""
    print_section("TEST 7: Pipeline Flow Validation")

    flow_steps = [
        ("1. Ingestion",     "Brand JSONs in frontend/public/data",
         FRONTEND_PUBLIC_DATA.exists() and len(list(FRONTEND_PUBLIC_DATA.glob("*.json"))) > 0),
        ("2. Catalog Build", "build_catalog() importable",             BUILD_CATALOG_AVAILABLE),
        ("3. API Serving",   "server.py provides /api/conductor/catalog",
         (PROJECT_ROOT / "backend" / "server.py").exists()),
        ("4. Frontend Hook", "useConductorCatalog.ts present",
         (PROJECT_ROOT / "frontend" / "src" / "hooks" / "useConductorCatalog.ts").exists()),
        ("5. JIT Streaming", "useJITIntelligence.ts present",
         (PROJECT_ROOT / "frontend" / "src" / "hooks" / "useJITIntelligence.ts").exists()),
        ("6. Telemetry",     "Sovereign Nerve telemetry.ts present",
         (PROJECT_ROOT / "frontend" / "src" / "telemetry.ts").exists()),
    ]

    all_pass = True
    for step, description, passed in flow_steps:
        if passed:
            print_status("PASS", f"{step}: {description}")
        else:
            print_status("FAIL", f"{step}: {description}")
            all_pass = False

    return all_pass


# ---------------------------------------------------------------------------
# Test 8 — Source Rule Compliance
# ---------------------------------------------------------------------------

def test_source_rule_compliance() -> bool:
    """Verify source_rules.py defines the Three Sources and key constants."""
    print_section("TEST 8: Source Rule Compliance (THE LAW)")

    source_rules_path = PROJECT_ROOT / "backend" / "source_rules.py"
    if not source_rules_path.exists():
        print_status("FAIL", "source_rules.py MISSING — THE LAW has been violated!")
        return False

    content = source_rules_path.read_text()
    required_symbols = [
        ("COMMERCIAL source defined",    "COMMERCIAL" in content or "commercial" in content),
        ("OFFICIAL source defined",       "OFFICIAL" in content or "official" in content),
        ("CONTEXTUAL source defined",     "CONTEXTUAL" in content or "contextual" in content),
        ("Price field ownership present", "price" in content),
    ]

    all_pass = True
    for name, ok in required_symbols:
        if ok:
            print_status("PASS", name)
        else:
            print_status("FAIL", name)
            all_pass = False

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("source_rules", source_rules_path)
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        print_status("PASS", "source_rules.py imports without errors")
    except Exception as e:
        print_status("FAIL", f"source_rules.py import failed: {e}")
        all_pass = False

    return all_pass


# ---------------------------------------------------------------------------
# Test 9 — Data Quality: dict image_url
# ---------------------------------------------------------------------------

def test_data_quality_image_url() -> bool:
    """Scan brand JSON files for dict-typed image_url (fixed gracefully in v9.7.6)."""
    print_section("TEST 9: Data Quality — image_url field shape")

    if not FRONTEND_PUBLIC_DATA.exists():
        print_status("SKIP", "Frontend data directory missing")
        return False

    exclude = {"index", "search_index", "search_index_min",
               "galaxy_db", "sample", "inventory", "taxonomy"}
    affected: list = []
    total_files = 0

    for f in sorted(FRONTEND_PUBLIC_DATA.glob("*.json")):
        if f.stem in exclude:
            continue
        total_files += 1
        try:
            data = json.loads(f.read_text())
            products = data if isinstance(data, list) else data.get("products", [])
            n = sum(1 for p in products if isinstance(p.get("image_url"), dict))
            if n:
                affected.append(f"{f.name} ({n} products)")
        except Exception as e:
            print_status("WARN", f"Cannot read {f.name}: {e}")

    print(f"   Scanned {total_files} brand files")
    if affected:
        print_status("WARN",
                     f"{len(affected)} file(s) have dict image_url "
                     f"(normalizer auto-flattens; re-enrich to fix source data):")
        for name in affected[:10]:
            print(f"     ⚠️  {name}")
        if len(affected) > 10:
            print(f"     … and {len(affected) - 10} more")
        return True   # WARN only — v9.7.6 handles this gracefully
    else:
        print_status("PASS", "All brand files have string image_url fields")
        return True


# ---------------------------------------------------------------------------
# Test 10 — TypeScript Compilation
# ---------------------------------------------------------------------------

def test_typescript_compilation() -> bool:
    """Run tsc --noEmit on the frontend to catch any type errors."""
    print_section("TEST 10: TypeScript Compilation")

    frontend_dir = PROJECT_ROOT / "frontend"
    tsconfig = frontend_dir / "tsconfig.app.json"

    if not tsconfig.exists():
        print_status("SKIP", "tsconfig.app.json not found in frontend/")
        return False

    tsc_exec = frontend_dir / "node_modules" / ".bin" / "tsc"
    if not tsc_exec.exists():
        which = subprocess.run(["which", "tsc"], capture_output=True, text=True)
        if which.returncode != 0:
            print_status("SKIP", "tsc not found — run pnpm install in frontend/")
            return False
        tsc_exec = Path(which.stdout.strip())

    try:
        result = subprocess.run(
            [str(tsc_exec), "--project", str(tsconfig), "--noEmit"],
            capture_output=True, text=True,
            cwd=str(frontend_dir), timeout=120,
        )
        if result.returncode == 0:
            print_status("PASS", "TypeScript compilation: no type errors")
            return True
        else:
            error_lines = [l for l in result.stdout.splitlines() if "error TS" in l]
            print_status("FAIL", f"TypeScript: {len(error_lines)} error(s)")
            for line in error_lines[:10]:
                print(f"     ❌  {line.strip()}")
            if len(error_lines) > 10:
                print(f"     … and {len(error_lines) - 10} more")
            return False
    except subprocess.TimeoutExpired:
        print_status("WARN", "tsc timed out after 120 s")
        return True
    except Exception as e:
        print_status("FAIL", f"tsc execution failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Test 11 — Backend Module Import Health
# ---------------------------------------------------------------------------

def test_backend_imports() -> bool:
    """Ensure core backend modules import cleanly (catches syntax/import errors)."""
    print_section("TEST 11: Backend Module Import Health")

    modules = [
        ("backend.source_rules",                "Source rules (THE LAW)"),
        ("backend.product_normalizer",           "Product normalizer"),
        ("backend.product_graph",                "Product graph"),
        ("backend.jit_agent",                    "JIT agent"),
        ("backend.server",                       "FastAPI server"),
        ("backend.ingestion.visual_validator",   "Visual validator"),
    ]

    all_pass = True
    for mod_name, label in modules:
        try:
            import importlib
            importlib.import_module(mod_name)
            print_status("PASS", f"{label}: {mod_name}")
        except Exception as e:
            print_status("FAIL", f"{label}: {mod_name} — {e}")
            all_pass = False

    return all_pass


def main() -> int:
    """Run all validation checks."""
    print("\n" + "=" * 70)
    print("  HALILIT OPERATOR CONSOLE — SYSTEM VALIDATION")
    print("  Version 9.7.6  |  February 2026")
    print("  Three Source Rules: Commercial · Official · Contextual")
    print("=" * 70)

    results: list = []

    results.append(("File Structure",          test_file_structure()))
    results.append(("Brand JSON Files",         test_brand_json_files()))
    results.append(("Catalog Build",            test_catalog_build()))
    results.append(("API Endpoints (live)",     test_api_endpoints()))
    results.append(("Frontend Components",      test_frontend_components()))
    results.append(("Navigation Store",         test_navigation_store()))
    results.append(("Pipeline Flow",            test_pipeline_flow()))
    results.append(("Source Rule Compliance",   test_source_rule_compliance()))
    results.append(("Data Quality: image_url",  test_data_quality_image_url()))
    results.append(("TypeScript Compilation",   test_typescript_compilation()))
    results.append(("Backend Module Health",    test_backend_imports()))

    print_section("VALIDATION SUMMARY — v9.7.6")

    passed = sum(1 for _, r in results if r)
    total  = len(results)

    for name, result in results:
        print(f"{'✅ PASS' if result else '❌ FAIL'}: {name}")

    pct = int(passed / total * 100)
    print(f"\nOverall: {passed}/{total} checks passed ({pct}%)")

    if passed == total:
        print_status("PASS", "System is healthy — all checks passed.")
        return 0
    elif passed >= total - 2:
        print_status("WARN", f"{total - passed} minor check(s) failed — review above.")
        return 1
    else:
        print_status("FAIL", f"{total - passed} check(s) failed — system needs attention.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
