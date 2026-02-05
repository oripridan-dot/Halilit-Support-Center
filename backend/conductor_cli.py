#!/usr/bin/env python3
"""
Conductor CLI - Command-line interface for the Conductor system

Provides a unified CLI for managing all aspects of the Conductor:
  • Starting the daemon
  • Data operations (add, update, validate)
  • Verification and repairs
  • Git hook installation
  • System status and diagnostics

Usage:
  conductor daemon              # Start the daemon
  conductor daemon --interactive # Interactive mode
  conductor add-product --brand="Roland" --name="Juno-X"
  conductor validate --scope=galaxy
  conductor verify --once
  conductor status
  conductor hooks install
  conductor export-index
"""

import sys
import os
import argparse
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ConductorCLI")

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[36m"
BOLD = "\033[1m"
RESET = "\033[0m"


class ConductorCLI:
    """Main CLI handler"""

    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.tools_dir = self.repo_root / "tools"

    def run_daemon(self, args):
        """Start the Conductor Daemon"""
        print(f"\n{BOLD}{CYAN}Starting Conductor Daemon...{RESET}\n")

        cmd = ["python3", "run_conductor_daemon.py"]

        if args.interactive:
            cmd.append("--interactive")
        if args.watch_only:
            cmd.append("--watch-only")
        if args.verify_once:
            cmd.append("--verify-once")
        if args.verbose:
            cmd.append("--verbose")

        try:
            result = subprocess.run(cmd, cwd=str(self.repo_root))
            return result.returncode
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Daemon stopped{RESET}")
            return 0
        except Exception as e:
            logger.error(f"Failed to start daemon: {e}")
            return 1

    def add_product(self, args):
        """Add a product via Data Access Layer"""
        from backend.conductor_dal import DataAccessLayer

        dal = DataAccessLayer()
        success, message = dal.add_product(
            brand=args.brand,
            name=args.name,
            price_il=args.price_il,
            price_eilat=args.price_eilat,
            image_url=args.image_url,
            source_url=args.source_url
        )

        print(f"{message}")
        return 0 if success else 1

    def validate(self, args):
        """Validate data or schema"""
        from backend.conductor_dal import DataAccessLayer

        dal = DataAccessLayer()

        if args.scope == "all" or args.scope == "galaxy":
            print(f"\n{BLUE}Validating galaxy schema...{RESET}\n")
            success, report = dal.validate_all()

            print(f"\n{json.dumps(report, indent=2)}")
            return 0 if success else 1
        else:
            logger.error(f"Unknown scope: {args.scope}")
            return 1

    def export(self, args):
        """Export data in various formats"""
        from backend.conductor_dal import DataAccessLayer

        dal = DataAccessLayer()
        success, data = dal.export(args.format)

        if success:
            if args.format == "json":
                print(json.dumps(data, indent=2))
            else:
                print(data)
            return 0
        else:
            print(f"{RED}Export failed: {data}{RESET}")
            return 1

    def verify(self, args):
        """Run verification"""
        print(f"\n{BLUE}Running verification...{RESET}\n")

        cmd = ["python3", "run_conductor_daemon.py", "--verify-once"]
        if args.verbose:
            cmd.append("--verbose")

        try:
            result = subprocess.run(cmd, cwd=str(self.repo_root))
            return result.returncode
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return 1

    def install_hooks(self, args):
        """Install git pre-commit hook"""
        print(f"\n{BLUE}Installing Git pre-commit hook...{RESET}\n")

        hook_source = self.tools_dir / "pre-commit-hook"
        hook_dest = self.repo_root / ".git" / "hooks" / "pre-commit"

        if not hook_source.exists():
            print(f"{RED}Hook file not found: {hook_source}{RESET}")
            return 1

        try:
            # Create hooks directory if needed
            hook_dest.parent.mkdir(parents=True, exist_ok=True)

            # Copy hook
            with open(hook_source, 'r') as f:
                content = f.read()

            with open(hook_dest, 'w') as f:
                f.write(content)

            # Make executable
            os.chmod(hook_dest, 0o755)

            print(f"{GREEN}✓ Git hook installed successfully{RESET}")
            print(f"  Location: {hook_dest}")
            print(f"  Commits will now require Conductor approval\n")
            return 0

        except Exception as e:
            print(f"{RED}Failed to install hook: {e}{RESET}")
            return 1

    def uninstall_hooks(self, args):
        """Uninstall git pre-commit hook"""
        print(f"\n{BLUE}Uninstalling Git pre-commit hook...{RESET}\n")

        hook_dest = self.repo_root / ".git" / "hooks" / "pre-commit"

        try:
            if hook_dest.exists():
                hook_dest.unlink()
                print(f"{GREEN}✓ Git hook removed{RESET}")
                print(f"  Commits will no longer require Conductor approval\n")
            else:
                print(f"{YELLOW}Hook not found{RESET}\n")
            return 0
        except Exception as e:
            print(f"{RED}Failed to uninstall hook: {e}{RESET}")
            return 1

    def show_status(self, args):
        """Show system status"""
        print(f"\n{BOLD}{CYAN}Conductor System Status{RESET}\n")

        status_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'components': {
                'daemon': self._check_daemon(),
                'daemon_file': self._check_file('run_conductor_daemon.py'),
                'dal': self._check_file('backend/conductor_dal.py'),
                'orchestrator': self._check_file('backend/conductor_orchestrator.py'),
                'git_hook': self._check_git_hook(),
                'watchdog': self._check_watchdog(),
            },
            'paths': {
                'repo_root': str(self.repo_root),
                'backend': str(self.repo_root / 'backend'),
                'frontend': str(self.repo_root / 'frontend'),
            }
        }

        print(json.dumps(status_info, indent=2))
        return 0

    def _check_daemon(self) -> bool:
        """Check if daemon is running"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "run_conductor_daemon"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False

    def _check_file(self, relative_path: str) -> Dict[str, Any]:
        """Check if a file exists and has content"""
        file_path = self.repo_root / relative_path
        return {
            'exists': file_path.exists(),
            'size_bytes': file_path.stat().st_size if file_path.exists() else 0,
            'path': str(file_path)
        }

    def _check_git_hook(self) -> Dict[str, Any]:
        """Check git hook status"""
        hook_path = self.repo_root / ".git" / "hooks" / "pre-commit"
        return {
            'installed': hook_path.exists(),
            'executable': os.access(hook_path, os.X_OK) if hook_path.exists() else False,
            'path': str(hook_path)
        }

    def _check_watchdog(self) -> Dict[str, Any]:
        """Check watchdog library"""
        try:
            import watchdog
            try:
                from importlib.metadata import version
                watchdog_version = version('watchdog')
            except:
                watchdog_version = "6.0.0+"
            return {
                'available': True,
                'version': watchdog_version
            }
        except ImportError:
            return {
                'available': False,
                'version': None,
                'message': 'Install with: pip install watchdog'
            }


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description=f"{BOLD}Conductor CLI{RESET} - Autonomous system orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  Daemon Management:
    conductor daemon                      # Start background daemon
    conductor daemon --interactive        # Interactive mode
    conductor daemon --verify-once        # Single verification

  Data Operations:
    conductor add-product \\
      --brand="Roland" \\
      --name="Juno-X" \\
      --price-il=15000

    conductor validate --scope=galaxy
    conductor export --format=json

  System Management:
    conductor verify
    conductor status
    conductor hooks install
    conductor hooks uninstall

For more help:
    conductor <command> --help
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command')

    # Daemon command
    daemon_parser = subparsers.add_parser(
        'daemon', help='Start the Conductor Daemon')
    daemon_parser.add_argument(
        '--interactive', '-i', action='store_true', help='Interactive mode')
    daemon_parser.add_argument(
        '--watch-only', '-w', action='store_true', help='Watch-only mode')
    daemon_parser.add_argument(
        '--verify-once', '-v', action='store_true', help='Single verification')
    daemon_parser.add_argument(
        '--verbose', action='store_true', help='Verbose logging')
    daemon_parser.set_defaults(
        func=lambda args: ConductorCLI().run_daemon(args))

    # Add product command
    add_parser = subparsers.add_parser('add-product', help='Add a product')
    add_parser.add_argument('--brand', required=True, help='Brand name')
    add_parser.add_argument('--name', required=True, help='Product name')
    add_parser.add_argument('--price-il', type=float,
                            required=True, help='Price in Israel')
    add_parser.add_argument('--price-eilat', type=float, help='Price in Eilat')
    add_parser.add_argument('--image-url', help='Image URL')
    add_parser.add_argument('--source-url', help='Source URL')
    add_parser.set_defaults(func=lambda args: ConductorCLI().add_product(args))

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate data')
    validate_parser.add_argument(
        '--scope', choices=['galaxy', 'all'], default='galaxy', help='Validation scope')
    validate_parser.set_defaults(
        func=lambda args: ConductorCLI().validate(args))

    # Export command
    export_parser = subparsers.add_parser('export', help='Export data')
    export_parser.add_argument(
        '--format', choices=['json', 'csv'], default='json', help='Export format')
    export_parser.set_defaults(func=lambda args: ConductorCLI().export(args))

    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Run verification')
    verify_parser.add_argument(
        '--verbose', action='store_true', help='Verbose logging')
    verify_parser.set_defaults(func=lambda args: ConductorCLI().verify(args))

    # Hooks command
    hooks_parser = subparsers.add_parser('hooks', help='Manage git hooks')
    hooks_subparsers = hooks_parser.add_subparsers(dest='hooks_command')

    install_hooks = hooks_subparsers.add_parser(
        'install', help='Install git hook')
    install_hooks.set_defaults(
        func=lambda args: ConductorCLI().install_hooks(args))

    uninstall_hooks = hooks_subparsers.add_parser(
        'uninstall', help='Uninstall git hook')
    uninstall_hooks.set_defaults(
        func=lambda args: ConductorCLI().uninstall_hooks(args))

    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    status_parser.set_defaults(
        func=lambda args: ConductorCLI().show_status(args))

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if not hasattr(args, 'func'):
        parser.print_help()
        return 1

    try:
        return args.func(args)
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
