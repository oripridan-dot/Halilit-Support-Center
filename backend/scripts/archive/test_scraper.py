#!/usr/bin/env python3
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Starting scraper test...")
print(f"Python: {sys.version}")
print(f"CWD: {os.getcwd()}")

try:
    import playwright
    print(f"✓ Playwright installed: {playwright.__version__}")
except ImportError as e:
    print(f"✗ Playwright not available: {e}")
    sys.exit(1)

try:
    from playwright.async_api import async_playwright
    print("✓ Playwright async API available")
except ImportError as e:
    print(f"✗ Playwright async API not available: {e}")
    sys.exit(1)

print("\nAll dependencies OK. Ready to run full scraper.")
print("\nTo run the full scraper, execute:")
print("  python3 extract_all_product_urls.py")
