"""
Halilit Support Center — Nexus CLI
===================================
Lightweight steering gate: review uncommitted changes, optionally
commit them, or revert. Mirrors the TooLoo-core nexus.py interface
so test_core.py::TestNexusCLI passes.
"""
from __future__ import annotations

import subprocess
import sys
from typing import Optional


# ── Helpers ───────────────────────────────────────────────────────────────────

def print_box(title: str, body: str = "", width: int = 60) -> None:
    """Print a simple ASCII box around a message."""
    border = "─" * (width - 2)
    print(f"╭{border}╮")
    print(f"│  {title:<{width - 4}}│")
    if body:
        for line in body.splitlines():
            print(f"│  {line:<{width - 4}}│")
    print(f"╰{border}╯")


# ── Core Gate ─────────────────────────────────────────────────────────────────

def review_changes(auto_mode: bool = False) -> bool:
    """Inspect the working tree and decide what to do with changes.

    Returns:
        True  — changes committed (or nothing to commit)
        False — changes reverted
    """
    status_result = subprocess.run(
        ["git", "status", "--porcelain"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    diff = (status_result.stdout or "").strip()

    if not diff:
        return True  # Nothing pending — clean slate

    print_box("Pending Changes Detected", diff[:500])

    if auto_mode:
        # Non-interactive: stage and commit automatically
        subprocess.run(["git", "add", "-A"], check=False)
        subprocess.run(
            ["git", "commit", "-m", "chore(auto): nexus auto-commit"],
            check=False,
        )
        return True

    # Interactive mode
    choice = input("Commit changes? [y / reject]: ").strip().lower()
    if choice in ("y", "yes"):
        subprocess.run(["git", "add", "-A"], check=False)
        subprocess.run(
            ["git", "commit", "-m", "chore(manual): nexus manual commit"],
            check=False,
        )
        return True
    else:
        # Revert all staged and unstaged changes
        subprocess.run(["git", "restore", "--staged", "."], check=False)
        subprocess.run(["git", "restore", "."], check=False)
        return False


# ── Swarm Executor ────────────────────────────────────────────────────────────

def execute_swarm(mandate: str = "", dry_run: bool = False) -> Optional[str]:
    """Placeholder for TooLoo swarm execution.

    In dev mode (FACADE_DEV_MODE=true) this is a no-op that logs the mandate.
    A live implementation would POST to the Façade endpoint.
    """
    if dry_run:
        return f"[dry-run] mandate received: {mandate}"
    print_box("Swarm Execution", f"mandate={mandate}\n(dev passthrough — no-op)")
    return None


# ── CLI Entry Point ────────────────────────────────────────────────────────────

def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Halilit Nexus CLI")
    sub = parser.add_subparsers(dest="command")

    review_p = sub.add_parser("review", help="Review and optionally commit changes")
    review_p.add_argument("--auto", action="store_true", help="Auto-commit without prompting")

    swarm_p = sub.add_parser("swarm", help="Dispatch a mandate to TooLoo core")
    swarm_p.add_argument("mandate", nargs="?", default="", help="Mandate text")
    swarm_p.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.command == "review":
        ok = review_changes(auto_mode=args.auto)
        sys.exit(0 if ok else 1)
    elif args.command == "swarm":
        execute_swarm(args.mandate, dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    _main()
