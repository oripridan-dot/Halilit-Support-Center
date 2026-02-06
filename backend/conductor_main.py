#!/usr/bin/env python3
"""
Halilit Support Center v6.0 - Conductor CLI

Central orchestrator for all system operations.

Usage:
    python3 backend/conductor_main.py ingest [brand]  - Run ingestion pipeline
    python3 backend/conductor_main.py sync            - Sync ingestion → frontend
    python3 backend/conductor_main.py build           - Build & sync everything
    python3 backend/conductor_main.py server          - Start FastAPI server
    python3 backend/conductor_main.py dev             - Start dev environment (server + frontend)
    python3 backend/conductor_main.py test [brand]    - Test pipeline for brand
    python3 backend/conductor_main.py catalog         - Show catalog statistics
"""

from datetime import datetime
from pathlib import Path
import subprocess
import json
import argparse
import sys
import os

# Add project root to sys.path before importing backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ingestion.orchestrator import IngestionOrchestrator
from backend.ingestion.trinity_integration import get_trinity_ingestion_bridge
from backend.ingestion_to_frontend import sync_brand_to_frontend, sync_all_brands


BRAND_DIR = Path(__file__).parent / "data" / "brands"
INGESTION_DIR = Path(__file__).parent / "data" / "ingestion"
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


class ConductorCLI:
    """Central command interface for Halilit v6.0."""

    def __init__(self):
        self.orchestrator = IngestionOrchestrator()
        self.bridge = get_trinity_ingestion_bridge()

    def ingest(self, brand: str = None):
        """Run ingestion pipeline for a brand or all brands."""
        print("🚀 Starting v6.0 Ingestion Pipeline")
        print("=" * 70)

        if brand:
            brands = [brand]
        else:
            # Find all brands
            brands = [d.name for d in BRAND_DIR.iterdir() if d.is_dir()]

        for b in brands:
            print(f"\n📊 Processing: {b}")
            result = self.bridge.process_brand_pipeline(b)
            if result.get("success"):
                metrics = result.get("metrics", {})
                print(
                    f"  ✓ {metrics.get('approved_count', 0)} products approved")
            else:
                errors = result.get("errors", [])
                print(
                    f"  ✗ Failed: {errors[0] if errors else 'Unknown error'}")

        print("\n" + "=" * 70)
        print("✅ Ingestion pipeline complete")

    def sync(self):
        """Sync ingestion output to frontend."""
        print("🔄 Syncing ingestion → frontend")
        print("=" * 70)
        results = sync_all_brands()
        success_count = sum(1 for v in results.values() if v)
        print(f"\n✅ Synced {success_count}/{len(results)} brands")

    def build(self):
        """Full build: ingest + sync."""
        print("🏗️  Building complete v6.0 catalog")
        print("=" * 70)

        self.ingest()
        self.sync()

        print("\n✅ Build complete!")

    def server(self):
        """Start the FastAPI server."""
        print("🚀 Starting FastAPI server")
        print("📖  http://localhost:8000/docs")
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "backend.server:app",
             "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(Path(__file__).parent.parent)
        )

    def dev(self):
        """Start full development environment."""
        print("⚡ Starting Halilit v6.0 Development Environment")
        print("=" * 70)
        print("🎨 Frontend: http://localhost:5173")
        print("📖 Backend:  http://localhost:8000/docs")
        print("")

        # Start backend in background
        backend_proc = subprocess.Popen(
            [sys.executable, "backend/server.py"],
            cwd=str(Path(__file__).parent.parent)
        )

        # Start frontend
        print("Starting frontend...")
        frontend_proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(FRONTEND_DIR)
        )

        try:
            print("\n✅ Both servers running. Press Ctrl+C to stop.")
            backend_proc.wait()
            frontend_proc.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping servers...")
            backend_proc.terminate()
            frontend_proc.terminate()

    def test(self, brand: str = "Nord"):
        """Test ingestion pipeline for a brand."""
        print(f"🧪 Testing ingestion for: {brand}")
        print("=" * 70)

        result = self.bridge.process_brand_pipeline(brand)

        if result.get("success"):
            print(f"✅ Test passed!")
            metrics = result.get("metrics", {})
            print(f"  • Products: {metrics.get('total_count', 0)}")
            print(f"  • Approved: {metrics.get('approved_count', 0)}")
            quality = result.get("quality_report", {})
            print(
                f"  • Quality: {quality.get('overall_quality_score', 0):.1f}%")
        else:
            errors = result.get("errors", [])
            print(f"✗ Test failed:")
            print(f"  {errors[0] if errors else 'Unknown error'}")

    def catalog(self):
        """Show catalog statistics."""
        print("📊 Catalog Statistics")
        print("=" * 70)

        # Count files
        brands = {}
        if INGESTION_DIR.exists():
            for brand_dir in (INGESTION_DIR / "products").iterdir():
                if brand_dir.is_dir():
                    # Find the latest approved_*.json file
                    approved_files = sorted(brand_dir.glob(
                        "approved_*.json"), reverse=True)
                    if approved_files:
                        try:
                            with open(approved_files[0]) as f:
                                data = json.load(f)
                            products = data.get("products", data) if isinstance(
                                data, dict) else data
                            brands[brand_dir.name] = len(products)
                        except:
                            brands[brand_dir.name] = 0
                    else:
                        brands[brand_dir.name] = 0

        print("\nBrands:")
        total_products = 0
        for brand, count in sorted(brands.items()):
            print(f"  • {brand.title()}: {count} products")
            total_products += count

        print(
            f"\n📈 Total: {total_products} products across {len(brands)} brands")
        print(f"🌌 Galaxies: 6 (Guitars, Drums, Keys, Studio, DJ, Utility)")


def main():
    parser = argparse.ArgumentParser(
        description="Halilit Support Center v6.0 - Conductor CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Ingest command
    ingest_parser = subparsers.add_parser(
        "ingest", help="Run ingestion pipeline")
    ingest_parser.add_argument(
        "brand", nargs="?", help="Brand to ingest (optional)")

    # Sync command
    subparsers.add_parser("sync", help="Sync ingestion → frontend")

    # Build command
    subparsers.add_parser("build", help="Full build: ingest + sync")

    # Server command
    subparsers.add_parser("server", help="Start FastAPI server")

    # Dev command
    subparsers.add_parser("dev", help="Start dev environment")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test ingestion")
    test_parser.add_argument(
        "brand", nargs="?", default="Nord", help="Brand to test")

    # Catalog command
    subparsers.add_parser("catalog", help="Show catalog statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    conductor = ConductorCLI()

    if args.command == "ingest":
        conductor.ingest(args.brand)
    elif args.command == "sync":
        conductor.sync()
    elif args.command == "build":
        conductor.build()
    elif args.command == "server":
        conductor.server()
    elif args.command == "dev":
        conductor.dev()
    elif args.command == "test":
        conductor.test(args.brand)
    elif args.command == "catalog":
        conductor.catalog()


if __name__ == "__main__":
    main()
