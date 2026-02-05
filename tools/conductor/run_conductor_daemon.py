#!/usr/bin/env python3
"""
Conductor Daemon Launcher
Transforms the Conductor from a passive verification script into an active, always-on system orchestrator.

Architecture Overview:
  • File Watcher: Monitors filesystem changes in backend/ and frontend/src/
  • Event Dispatcher: Routes events to appropriate handlers with priority queueing
  • Standards Enforcer: Auto-applies code standards and fixes violations
  • Agent Coordinator: Dispatches complex tasks to Trinity Swarm agents
  • Self-Healing: Automatically fixes common issues without human intervention
  • Data Governance: Ensures all writes go through validated Data Access Layer

Execution Modes:
  • Background Daemon: python run_conductor_daemon.py
  • Interactive CLI: python run_conductor_daemon.py --interactive
  • Watch Only: python run_conductor_daemon.py --watch-only
  • Verification Only: python run_conductor_daemon.py --verify-once
"""

from backend.conductor_daemon import ConductorDaemon, COLORS
import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def setup_logging(log_file: str = "conductor_daemon.log", verbose: bool = False) -> logging.Logger:
    """Configure logging for the daemon"""
    log_level = logging.DEBUG if verbose else logging.INFO

    # Create log directory if it doesn't exist
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger("ConductorDaemon")


def print_banner(logger: logging.Logger):
    """Print the Conductor banner"""
    banner = f"""
{COLORS['BOLD']}{COLORS['CYAN']}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║            🌌 HALILIT SUPPORT CENTER - CONDUCTOR DAEMON 🌌           ║
║                    v5.4.0 - Autonomous Manager                       ║
║                                                                      ║
║  Transforming Passive Verification into Active System Orchestration  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{COLORS['RESET']}

{COLORS['GREEN']}✓ Conductor Daemon Starting...{COLORS['RESET']}

Key Features Enabled:
  • 🔍 Real-time File Monitoring (watchdog)
  • 🤖 Autonomic Agent Dispatch (Trinity Swarm)
  • 🛡️  Automatic Standards Enforcement
  • 💾 Data Governance with Schema Validation
  • 🚫 Pre-commit Deployment Gatekeeper
  • 📊 Spectrum Pipeline Verification
  • 🔄 Bi-directional Data Synchronization

Architecture Components:
  1. File Watcher Service (Monitors filesystem changes)
  2. Event Dispatcher (Routes events to handlers)
  3. Standards Enforcer (Auto-applies code standards)
  4. Agent Coordinator (Delegates to Trinity Swarm)
  5. Data Access Layer (Validated writes only)
  6. Git Pre-commit Hook (Blocks imperfect commits)

{COLORS['YELLOW']}Run with --help for advanced options{COLORS['RESET']}

"""
    logger.info(banner)


def main():
    """Main entry point for the Conductor Daemon"""

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Conductor Daemon: Transform your codebase into a self-healing, AI-powered system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_conductor_daemon.py                    # Run in background mode
  python run_conductor_daemon.py --interactive      # Interactive CLI mode
  python run_conductor_daemon.py --watch-only       # Only watch files, no agent dispatch
  python run_conductor_daemon.py --verify-once      # Single verification run
  python run_conductor_daemon.py --verbose          # Detailed logging
        """
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive CLI mode (default: background mode)"
    )

    parser.add_argument(
        "--watch-only", "-w",
        action="store_true",
        help="Only watch files, skip agent dispatch and auto-fixes"
    )

    parser.add_argument(
        "--verify-once", "-v",
        action="store_true",
        help="Run a single verification pass and exit"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging"
    )

    parser.add_argument(
        "--log-file",
        default="conductor_daemon.log",
        help="Path to log file (default: conductor_daemon.log)"
    )

    parser.add_argument(
        "--watch-paths",
        nargs="+",
        default=["backend", "frontend/src"],
        help="Paths to watch (default: backend frontend/src)"
    )

    parser.add_argument(
        "--no-agent-dispatch",
        action="store_true",
        help="Disable Trinity Swarm agent dispatch (for testing)"
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.log_file, args.verbose)

    # Print banner
    print_banner(logger)

    # Validate watch paths
    for path in args.watch_paths:
        if not os.path.isdir(path):
            logger.warning(f"⚠️  Watch path does not exist: {path}")

    # Create daemon instance
    logger.info(
        f"{COLORS['CYAN']}Initializing Conductor Daemon...{COLORS['RESET']}")

    try:
        daemon = ConductorDaemon(
            watched_paths=args.watch_paths,
            enable_agent_dispatch=not args.no_agent_dispatch,
            watch_only=args.watch_only
        )
    except Exception as e:
        logger.error(
            f"{COLORS['RED']}Failed to initialize daemon: {e}{COLORS['RESET']}")
        return 1

    # Handle different execution modes
    try:
        if not daemon.start():
            logger.error(
                f"{COLORS['RED']}Failed to start daemon{COLORS['RESET']}")
            return 1

        logger.info(
            f"{COLORS['GREEN']}✓ Conductor Daemon started successfully{COLORS['RESET']}")

        if args.verify_once:
            # Single verification pass
            logger.info(
                f"\n{COLORS['BLUE']}Running single verification pass...{COLORS['RESET']}")
            daemon.run_verification_pass()
            logger.info(
                f"{COLORS['GREEN']}✓ Verification complete{COLORS['RESET']}")
            daemon.stop()
            return 0

        elif args.interactive:
            # Interactive CLI mode
            logger.info(
                f"\n{COLORS['MAGENTA']}Entering interactive mode. Type 'help' for commands.{COLORS['RESET']}")
            daemon.run_interactive()
            return 0

        else:
            # Background daemon mode
            logger.info(
                f"\n{COLORS['YELLOW']}Daemon running in background. Press Ctrl+C to stop.{COLORS['RESET']}")
            daemon.run_background()
            return 0

    except KeyboardInterrupt:
        logger.info(
            f"\n{COLORS['YELLOW']}Keyboard interrupt received{COLORS['RESET']}")
        daemon.stop()
        return 0
    except Exception as e:
        logger.error(
            f"{COLORS['RED']}Unexpected error: {e}{COLORS['RESET']}", exc_info=True)
        daemon.stop()
        return 1


if __name__ == '__main__':
    sys.exit(main())
