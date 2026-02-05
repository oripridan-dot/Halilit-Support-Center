#!/usr/bin/env python3
"""
Conductor Orchestrator Launcher

The simplest way to run the maximized Conductor system.
This script starts the autonomous orchestrator that will:

1. Monitor your data files and auto-rebuild the search index
2. Watch your code and enforce standards automatically
3. Detect errors and dispatch Trinity Swarm agents to fix them
4. Block bad commits with a pre-commit git hook

Usage:
    python3 run_conductor_orchestrator.py

The orchestrator will run in the foreground and display status updates.
Press Ctrl+C to stop gracefully.
"""

from backend.conductor_orchestrator import ConductorOrchestrator, logger
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Launch the Conductor Orchestrator"""
    print("\n" + "=" * 80)
    print("🚀 Conductor Orchestrator v6.0 - Active System Manager")
    print("=" * 80)
    print("\nStarting autonomous orchestration system...\n")

    orchestrator = ConductorOrchestrator()

    # Start the orchestrator
    if not orchestrator.start():
        print("❌ Failed to start orchestrator")
        return 1

    # Interactive shell
    try:
        while orchestrator.running:
            try:
                # Small delay to prevent busy-waiting
                import time
                time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n\nShutting down gracefully...")
                orchestrator.stop()
                break
    except Exception as e:
        print(f"Error: {e}")
        orchestrator.stop()
        return 1

    print("\n✅ Conductor Orchestrator stopped successfully")
    return 0


if __name__ == '__main__':
    sys.exit(main())
