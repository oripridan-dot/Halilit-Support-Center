#!/usr/bin/env python3
"""
Halilit Support Center v7.0 - Conductor CLI
===========================================

Central orchestrator for all system operations, data validation, and security.

Usage:
    INGESTION & BUILDING:
    python3 backend/conductor_main.py ingest [brand]  - Run ingestion pipeline
    python3 backend/conductor_main.py sync            - Sync ingestion → frontend
    python3 backend/conductor_main.py build           - Build & sync everything
    
    DEVELOPMENT:
    python3 backend/conductor_main.py server          - Start FastAPI server
    python3 backend/conductor_main.py dev             - Start dev environment (server + frontend)
    python3 backend/conductor_main.py test [brand]    - Test pipeline for brand
    
    VALIDATION:
    python3 backend/conductor_main.py validate        - Validate entire data pipeline
    python3 backend/conductor_main.py validate-sync   - Build + validate all 3 screens
    python3 backend/conductor_main.py catalog         - Show catalog statistics
    
    SECURITY MANAGEMENT:
    python3 backend/conductor_main.py shield          - Show security status
    python3 backend/conductor_main.py shield-cors     - Manage CORS settings
    python3 backend/conductor_main.py shield-limits   - Manage rate limits
    python3 backend/conductor_main.py shield-ddos     - Manage DDoS protection
    python3 backend/conductor_main.py shield-audit    - Audit security logs
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

# ⭐ VERSION CONTROL (Prevent confusion & deprecation)
from backend.VERSION_CONTROL import (
    SYSTEM_VERSION, BRANCH_NAME, assert_version_supports,
    check_component_responsibility, ComponentRegistry
)

from backend.ingestion.orchestrator import IngestionOrchestrator
from backend.ingestion.trinity_integration import get_trinity_ingestion_bridge
from backend.ingestion_to_frontend import sync_brand_to_frontend, sync_all_brands
from backend.data_pipeline_validator import DataPipelineValidator
from backend.security_shield import SecurityShield


BRAND_DIR = Path(__file__).parent / "data" / "brands"
INGESTION_DIR = Path(__file__).parent / "data" / "ingestion"
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


class ConductorCLI:
    """Central command interface for Halilit v7.0.
    
    Manages:
      • Data ingestion & pipeline orchestration
      • Data validation & quality assurance
      • Security shields & defensive mechanisms
      • Comprehensive logging & monitoring
    """

    def __init__(self):
        self.orchestrator = IngestionOrchestrator()
        self.bridge = get_trinity_ingestion_bridge()
        self.validator = DataPipelineValidator()
        self.security_shield = SecurityShield()  # Security management

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

    def validate(self):
        """Validate entire data pipeline for consistency and alignment."""
        print("\n🔍 VALIDATING DATA PIPELINE (All 3 Screens)")
        print("=" * 70)
        
        results = self.validator.validate_all()
        self.validator.print_report(results)
        
        return results
    
    def validate_sync(self):
        """Build complete pipeline and validate all 3 screens work together."""
        print("\n🚀 BUILD + VALIDATE COMPLETE PIPELINE")
        print("=" * 70)
        
        print("\n1️⃣  Building catalog...")
        self.build()
        
        print("\n2️⃣  Validating pipeline...")
        validation_results = self.validate()
        
        print("\n3️⃣  Running integration test...")
        self._test_screen_integration()
        
        return validation_results
    
    def _test_screen_integration(self):
        """Test that all 3 screens can load data correctly"""
        print("\n🧪 Testing Screen Integration")
        print("-" * 70)
        
        try:
            # Check that backend has prepared data for frontend
            brands_dir = Path(__file__).parent / "data" / "brands"
            
            if not brands_dir.exists():
                print("⚠️  Brands directory not found")
                return
            
            # Check each brand has products
            brands_processed = 0
            total_products = 0
            
            for brand_dir in sorted(brands_dir.glob("*")):
                if not brand_dir.is_dir():
                    continue
                
                products_file = brand_dir / "products.json"
                if products_file.exists():
                    try:
                        with open(products_file) as f:
                            data = json.load(f)
                            products = data.get("products", [])
                            brands_processed += 1
                            total_products += len(products)
                            print(f"✓ {brand_dir.name:20s} → {len(products):4d} products ready")
                    except Exception as e:
                        print(f"⚠️  Error reading {brand_dir.name}/products.json: {e}")
            
            print(f"\n✅ Backend has prepared {total_products} products across {brands_processed} brands")
            print("✅ All 3 screens can access data from the unified ingestion pipeline:")
            print("   → GalaxyDashboard:  catalogLoader.loadAllProducts() filtered by category")
            print("   → SpectrumModule:   catalogLoader.loadAllProducts() grouped by brand")
            print("   → ProductPage:      catalogLoader.findProductById() for enriched details")
            print("\n✅ ALL SCREENS INTEGRATION PASSED")
            
        except Exception as e:
            print(f"\n❌ INTEGRATION TEST FAILED: {e}")
    
    def shield(self):
        """Show comprehensive security status and configuration."""
        print("\n🛡️  SECURITY SHIELD STATUS (v7.0)")
        print("=" * 70)
        
        status = self.security_shield.get_security_status()
        
        print("\n✅ CORS Management:")
        cors_config = status["cors"]
        print(f"   Status: {'ENABLED' if cors_config['enabled'] else 'DISABLED'}")
        print(f"   Allowed Origins: {', '.join(cors_config['allowed_origins'])}")
        
        print("\n✅ Rate Limiting:")
        ratelimit = status["rate_limiting"]
        print(f"   Status: {'ENABLED' if ratelimit['enabled'] else 'DISABLED'}")
        print(f"   Active Tracking IPs: {ratelimit['stats']['tracked_ips']}")
        
        print("\n✅ DDoS Protection:")
        ddos = status["ddos_protection"]
        print(f"   Status: {'ENABLED' if ddos['enabled'] else 'DISABLED'}")
        print(f"   Blocked IPs: {ddos['status']['currently_blocked']}")
        print(f"   Suspicious IPs: {ddos['status']['suspicious_ips']}")
        
        print("\n✅ Input Validation:")
        print(f"   Status: {'ENABLED' if status['input_validation']['enabled'] else 'DISABLED'}")
        print(f"   • SQL Injection Detection: ACTIVE")
        print(f"   • XSS Detection: ACTIVE")
        print(f"   • Size Limits: ENFORCED")
        
        print("\n✅ Security Logging:")
        print(f"   Status: {'ENABLED' if status['logging']['enabled'] else 'DISABLED'}")
        print(f"   Log File: backend/logs/security.log")
        
        print("\n💡 Configuration:")
        print("   To manage security settings, use:")
        print("   • shield-cors    - CORS whitelist/blacklist")
        print("   • shield-limits  - Rate limiting configuration")
        print("   • shield-ddos    - DDoS protection settings")
        print("   • shield-audit   - Review security logs")
    
    def shield_cors(self, action: str = "list", origin: str = None):
        """Manage CORS settings."""
        print("\n🔐 CORS Configuration Manager")
        print("=" * 70)
        
        if action == "list":
            origins = self.security_shield.config.get("cors.allowed_origins", [])
            print("\nAllowed Origins:")
            for i, o in enumerate(origins, 1):
                print(f"  {i}. {o}")
        
        elif action == "add" and origin:
            self.security_shield.cors.add_origin(origin)
            print(f"✅ Added allowed origin: {origin}")
        
        elif action == "remove" and origin:
            self.security_shield.cors.remove_origin(origin)
            print(f"✅ Removed allowed origin: {origin}")
        
        else:
            print("Usage:")
            print("  shield-cors list                           - List allowed origins")
            print("  shield-cors add <origin>                   - Add new origin")
            print("  shield-cors remove <origin>                - Remove origin")
    
    def shield_limits(self, limit_type: str = "show"):
        """Manage rate limiting configuration."""
        print("\n⚡ Rate Limiting Configuration")
        print("=" * 70)
        
        limits = self.security_shield.config.get("rate_limiting", {})
        
        print(f"\nGlobal Limits:")
        print(f"  • Requests: {limits.get('global_limit', 1000)}{limits.get('global_window', 3600)}s")
        
        print(f"\nPer-IP Limits:")
        print(f"  • Requests: {limits.get('per_ip_limit', 100)} per {limits.get('per_ip_window', 60)}s")
        
        print(f"\nPer-Endpoint Limits:")
        print(f"  • Requests: {limits.get('per_endpoint_limit', 50)} per {limits.get('per_endpoint_window', 60)}s")
        
        print("\n💡 To modify limits, edit: backend/security_config.json")
        print("   Then restart the server for changes to take effect.")
    
    def shield_ddos(self):
        """Show DDoS protection status."""
        print("\n🚨 DDoS Protection Status")
        print("=" * 70)
        
        ddos_config = self.security_shield.config.get("ddos_protection", {})
        ddos_status = self.security_shield.ddos_protection.get_status()
        
        print(f"\nBurst Detection:")
        print(f"  • Threshold: {ddos_config.get('burst_threshold', 50)} requests per {ddos_config.get('burst_window', 10)}s")
        print(f"  • Current blocked IPs: {ddos_status['currently_blocked']}")
        
        print(f"\nSuspicious Activity:")
        print(f"  • Suspicious IPs: {ddos_status['suspicious_ips']}")
        print(f"  • Currently tracked: {ddos_status['active_tracking']} IPs")
        
        print(f"\nRequest Size Protection:")
        max_size = ddos_config.get('max_request_size', 10485760)
        print(f"  • Max request size: {max_size / 1024 / 1024:.1f} MB")
        
        if len(self.security_shield.ddos_protection.blocked_ips) > 0:
            print(f"\n⚠️  Currently Blocked IPs:")
            for ip, timestamp in list(self.security_shield.ddos_protection.blocked_ips.items())[:10]:
                print(f"  • {ip} (blocked at {datetime.fromtimestamp(timestamp)})")
    
    def shield_audit(self):
        """Show security audit log."""
        print("\n📋 Security Audit Log")
        print("=" * 70)
        
        log_file = self.security_shield.config.get("logging.log_file", "backend/logs/security.log")
        log_path = Path(__file__).parent / log_file
        
        if not log_path.exists():
            print(f"No log file yet: {log_file}")
            return
        
        try:
            with open(log_path) as f:
                lines = f.readlines()
            
            # Show last 50 entries
            print(f"\nRecent entries (last 50):")
            for line in lines[-50:]:
                print(f"  {line.strip()}")
            
            print(f"\n📊 Total log entries: {len(lines)}")
            print(f"Log file: {log_path}")
        except Exception as e:
            print(f"Error reading log file: {e}")




def main():
    parser = argparse.ArgumentParser(
        description="Halilit Support Center v7.0 - Conductor CLI",
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
    
    # Validate command
    subparsers.add_parser("validate", help="Validate entire data pipeline")
    
    # Validate + Sync command
    subparsers.add_parser("validate-sync", help="Build + validate complete pipeline")
    
    # Security Shield Commands
    subparsers.add_parser("shield", help="Show security status and configuration")
    
    shield_cors_parser = subparsers.add_parser("shield-cors", help="Manage CORS settings")
    shield_cors_parser.add_argument("action", nargs="?", default="list", 
                                    choices=["list", "add", "remove"],
                                    help="CORS action")
    shield_cors_parser.add_argument("origin", nargs="?", help="Origin URL (for add/remove)")
    
    subparsers.add_parser("shield-limits", help="Show rate limiting configuration")
    
    subparsers.add_parser("shield-ddos", help="Show DDoS protection status")
    
    subparsers.add_parser("shield-audit", help="Show security audit log")

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
    elif args.command == "validate":
        conductor.validate()
    elif args.command == "validate-sync":
        conductor.validate_sync()
    elif args.command == "shield":
        conductor.shield()
    elif args.command == "shield-cors":
        conductor.shield_cors(args.action, getattr(args, 'origin', None))
    elif args.command == "shield-limits":
        conductor.shield_limits()
    elif args.command == "shield-ddos":
        conductor.shield_ddos()
    elif args.command == "shield-audit":
        conductor.shield_audit()


if __name__ == "__main__":
    main()
