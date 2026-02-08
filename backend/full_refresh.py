#!/usr/bin/env python3
"""
FULL REFRESH SCRIPT
Conducts a full data replacement with freshly scraped data and visual validations.
"""

from backend.conductor_main import ConductorCLI
import sys
import os
import shutil
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    print("🚀 STARTING FULL DATA REFRESH WITH VISUAL VALIDATION...")

    conductor = ConductorCLI()

    # Target Brands for high-impact refresh
    brands = ['Nord', 'Moog', 'Sequential', 'Arturia']

    print(f"Targeting Brands: {', '.join(brands)}")

    # 3. Process
    for brand in brands:
        print(f"\n==================================================")
        print(f"🌊 REFRESHING BRAND: {brand}")
        print(f"==================================================")
        try:
            # full_build calls ingest + sync to frontend
            conductor.full_build(brand)
        except Exception as e:
            print(f"❌ Failed to ingest {brand}: {e}")
            import traceback
            traceback.print_exc()

    print("\n✅ FULL REFRESH SEQUENCE COMPLETE.")


if __name__ == "__main__":
    main()
