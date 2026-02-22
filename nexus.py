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


# ── Core commands ─────────────────────────────────────────────────────────────

def review_changes(auto_mode: bool = False) -> bool:
    """Review uncommitted changes and decide whether to commit or revert.

    Returns True if changes were committed (or there were none),
    False if the user chose to revert.
    """
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True
    )
    diff = result.stdout.strip()

    if not diff:
        return True  # nothing to review

    print_box("Uncommitted Changes", diff)

    if auto_mode:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(
            ["git", "commit", "-m", "chore: auto-commit via Nexus CLI"],
            check=True,
        )
        return True

    choice = input("Commit changes? [y / reject]: ").strip().lower()
    if choice == "reject":
        subprocess.run(["git", "restore", "."], check=True)
        return False

    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: commit via Nexus CLI"],
        check=True,
    )
    return True


def execute_swarm(mandate: str, target_repo: Optional[str] = None) -> None:
    """Forward a mandate to TooLoo Core (stub — real routing via start-tooloo.sh)."""
    print_box("Nexus → TooLoo Core", f"Mandate: {mandate}")
    print("Run ./start-tooloo.sh to connect TooLoo Core to this repository.")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Halilit Nexus CLI")
    sub = parser.add_subparsers(dest="cmd")

    review_p = sub.add_parser("review", help="Review and commit/revert changes")
    review_p.add_argument("--auto", action="store_true", help="Auto-commit without prompt")

    swarm_p = sub.add_parser("swarm", help="Send a mandate to TooLoo Core")
    swarm_p.add_argument("mandate", help="Plain-English instruction")

    args = parser.parse_args()

    if args.cmd == "review":
        ok = review_changes(auto_mode=args.auto)
        sys.exit(0 if ok else 1)
    elif args.cmd == "swarm":
        execute_swarm(args.mandate)
    else:
        parser.print_help()
