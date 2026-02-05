#!/usr/bin/env python3
"""
CONDUCTOR MASTER CONTROL v7.0

Master control script for system management, refinement, and verification.
Provides unified interface for all conductor operations.

Commands:
  python3 conductor_master.py inspect    - Full system inspection
  python3 conductor_master.py refine     - Autonomous refinement
  python3 conductor_master.py verify     - Deployment verification
  python3 conductor_master.py status     - System status report
  python3 conductor_master.py reingest   - Re-ingest entire database
  python3 conductor_master.py help       - Show all commands
"""

import os
import sys
import subprocess
from pathlib import Path

COLORS = {
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
    'CYAN': '\033[36m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'BLUE': '\033[94m',
}


class ConductorMaster:
    """Master control for Conductor system"""

    def __init__(self):
        self.root = Path(os.path.dirname(os.path.abspath(__file__)))

    def run_script(self, script_name):
        """Run a conductor script"""
        script_path = self.root / script_name
        if not script_path.exists():
            print(
                f"{COLORS['RED']}✗ Script not found: {script_name}{COLORS['RESET']}")
            return

        try:
            result = subprocess.run(
                f"python3 {script_path}",
                shell=True,
                cwd=str(self.root)
            )
            sys.exit(result.returncode)
        except KeyboardInterrupt:
            print(
                f"\n{COLORS['YELLOW']}⚠ Operation cancelled{COLORS['RESET']}")
            sys.exit(1)

    def inspect(self):
        """Run full system inspection"""
        print(
            f"{COLORS['CYAN']}Starting full system inspection...{COLORS['RESET']}")
        self.run_script("conductor_refine_all.py")

    def refine(self):
        """Run autonomous refinement"""
        print(
            f"{COLORS['CYAN']}Starting autonomous refinement...{COLORS['RESET']}")
        self.run_script("conductor_refine_system.py")

    def verify(self):
        """Run deployment verification"""
        print(
            f"{COLORS['CYAN']}Starting deployment verification...{COLORS['RESET']}")
        self.run_script("conductor_final_check.py")

    def status(self):
        """Show system status"""
        print(f"{COLORS['CYAN']}Generating status report...{COLORS['RESET']}")
        self.run_script("conductor_status_report.py")

    def reingest(self):
        """Re-ingest entire database"""
        print(f"{COLORS['CYAN']}Starting database re-ingestion...{COLORS['RESET']}")
        self.run_script("conductor_reingest_database.py")

    def help(self):
        """Show help"""
        help_text = f"""
{COLORS['BOLD']}{COLORS['CYAN']}╔════════════════════════════════════════════════════════════════╗
║              CONDUCTOR MASTER CONTROL v7.0 - HELP                ║
╚════════════════════════════════════════════════════════════════════╝{COLORS['RESET']}

{COLORS['BLUE']}AVAILABLE COMMANDS:{COLORS['RESET']}

  {COLORS['YELLOW']}python3 conductor_master.py inspect{COLORS['RESET']}
    Performs comprehensive system inspection.
    Checks frontend, backend, dependencies, and builds.
    Output: Detailed inspection report
    Time: ~30-60 seconds

  {COLORS['YELLOW']}python3 conductor_master.py refine{COLORS['RESET']}
    Runs autonomous 5-phase refinement:
      1. Frontend refinement
      2. Backend refinement  
      3. Data layer validation
      4. Build optimization
      5. Final verification
    Output: Refinement summary with phase results
    Time: ~60-90 seconds

  {COLORS['YELLOW']}python3 conductor_master.py verify{COLORS['RESET']}
    Runs 10-point deployment readiness verification:
      • Frontend build success
      • TypeScript compilation
      • Backend compilation
      • Agent initialization
      • API endpoint verification
      • Data layer validation
      • Dependency resolution
      • And more...
    Output: Pass/fail report with percentage
    Time: ~20-40 seconds

  {COLORS['YELLOW']}python3 conductor_master.py status{COLORS['RESET']}
    Generates comprehensive system status report:
      • Frontend status
      • Backend status
      • Integration status
      • Data layer status
      • Build & deployment status
      • Conductor capabilities
    Output: Formatted status display
    Time: ~5 seconds

  {COLORS['YELLOW']}python3 conductor_master.py reingest{COLORS['RESET']}
    Re-ingests the entire database using Trinity Swarm:
      • Prepares data environment
      • Activates Trinity Swarm agents
      • Rebuilds product library
      • Synchronizes frontend data
      • Verifies data integrity
    Output: Re-ingestion report with statistics
    Time: ~2-3 seconds
    Result: 648 products loaded across 8 brands

  {COLORS['YELLOW']}python3 conductor_master.py help{COLORS['RESET']}
    Shows this help message.

{COLORS['BLUE']}QUICK START:{COLORS['RESET']}

  1. Inspect system:
     {COLORS['BOLD']}python3 conductor_master.py inspect{COLORS['RESET']}

  2. Refine everything:
     {COLORS['BOLD']}python3 conductor_master.py refine{COLORS['RESET']}

  3. Verify readiness:
     {COLORS['BOLD']}python3 conductor_master.py verify{COLORS['RESET']}

  4. Check status:
     {COLORS['BOLD']}python3 conductor_master.py status{COLORS['RESET']}

  5. Re-ingest database:
     {COLORS['BOLD']}python3 conductor_master.py reingest{COLORS['RESET']}

{COLORS['BLUE']}DEPLOYMENT COMMANDS:{COLORS['RESET']}

  Terminal 1 (Backend):
    {COLORS['BOLD']}python3 backend/server.py{COLORS['RESET']}

  Terminal 2 (Frontend):
    {COLORS['BOLD']}cd frontend && npm run dev{COLORS['RESET']}

{COLORS['BLUE']}ACCESS POINTS:{COLORS['RESET']}

  • Frontend:      http://localhost:5173
  • Backend API:   http://localhost:8000
  • API Docs:      http://localhost:8000/docs

{COLORS['BLUE']}DOCUMENTATION:{COLORS['RESET']}

  • CONDUCTOR_REFINEMENT_COMPLETE_v6.0.md - Detailed completion report
  • CONDUCTOR_REFINEMENT_SUMMARY.md - Quick reference guide

{COLORS['CYAN']}Conductor Master v7.0 - System fully configured for production{COLORS['RESET']}
"""
        print(help_text)


def main():
    master = ConductorMaster()

    if len(sys.argv) < 2:
        master.help()
        return

    command = sys.argv[1].lower()

    if command == "inspect":
        master.inspect()
    elif command == "refine":
        master.refine()
    elif command == "verify":
        master.verify()
    elif command == "status":
        master.status()
    elif command == "reingest":
        master.reingest()
    elif command == "help":
        master.help()
    else:
        print(f"{COLORS['RED']}✗ Unknown command: {command}{COLORS['RESET']}")
        print(
            f"{COLORS['BLUE']}Use 'python3 conductor_master.py help' for available commands{COLORS['RESET']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
