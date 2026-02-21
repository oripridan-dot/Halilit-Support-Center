"""
SHADOW CELL — Super Sandbox Manager (backend/factory/shadow_cell.py)
=====================================================================
The Darwin Protocol's physical laboratory.

Creates a completely isolated, ephemeral duplicate of the entire repository
outside the main workspace. The Shadow Cell is:

  • ISOLATED — No .git history, no node_modules, no .venv. Cannot pollute
               the live codebase.
  • MUTABLE   — Darwin Agent can violently rip apart its architecture,
               rewrite files, install packages, and run benchmarks inside
               it without ever touching production code.
  • EPHEMERAL — Destroyed after every experiment. Hard drive footprint is
               transient by design.

Usage:
    from backend.factory.shadow_cell import spin_up_shadow_cell, execute_shadow_benchmark, destroy_shadow_cell

    path = spin_up_shadow_cell()
    result = execute_shadow_benchmark("python backend/tests/benchmark_catalog.py")
    destroy_shadow_cell()

    # Or as a context manager:
    with ShadowCell() as cell:
        cell.run("python bench.py")
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
# Place the shadow cell entirely OUTSIDE the main repo to avoid
# Vite hot-reload, watcherd, and Git index collisions.
SHADOW_DIR = ROOT_DIR.parent / "halilit_shadow_cell"

# Directories / files too large or irrelevant to clone
_IGNORE_PATTERNS = shutil.ignore_patterns(
    ".git",
    "node_modules",
    ".venv",
    ".venv*",
    "venv",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "galaxy_db.json",
    "factory_logs",
    "halilit_shadow_cell",  # safety: never self-nest
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
    "*.egg-info",
    "playwright-report",
    "test-results",
)

MARKER_FILE = SHADOW_DIR / ".shadow_cell_marker"


# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------

def spin_up_shadow_cell(force: bool = True) -> str:
    """
    Creates a pristine, isolated clone of the main codebase for
    radical architectural experiments.

    Args:
        force: If True and a shadow cell already exists, destroy it first
               and create a fresh one. If False, reuse if already present.

    Returns:
        Absolute path to the shadow cell root as a string.
    """
    _banner("🔬 SPINNING UP SHADOW CELL (SUPER SANDBOX)...")

    if SHADOW_DIR.exists():
        if force:
            print(f"   ♻️  Destroying stale Shadow Cell at {SHADOW_DIR} …")
            shutil.rmtree(SHADOW_DIR)
        else:
            if MARKER_FILE.exists():
                print(f"   ♻️  Reusing existing Shadow Cell at {SHADOW_DIR}")
                return str(SHADOW_DIR)
            # Marker file missing — treat as corrupted, rebuild
            shutil.rmtree(SHADOW_DIR)

    t0 = time.time()
    print(f"   📁 Cloning {ROOT_DIR} → {SHADOW_DIR}")
    shutil.copytree(ROOT_DIR, SHADOW_DIR, ignore=_IGNORE_PATTERNS)

    # Drop a marker so we can cheaply detect a valid cell
    MARKER_FILE.write_text(
        f"halilit_shadow_cell\nsource={ROOT_DIR}\ncreated={time.time():.0f}\n",
        encoding="utf-8",
    )

    elapsed = time.time() - t0
    print(f"   ✅ Shadow Cell initialized at: {SHADOW_DIR}  ({elapsed:.1f}s)")
    _print_dir_size(SHADOW_DIR)
    return str(SHADOW_DIR)


def execute_shadow_benchmark(
    test_command: str,
    timeout: int = 300,
    env_extras: dict[str, str] | None = None,
) -> dict[str, str | int]:
    """
    Runs a benchmark command INSIDE the Shadow Cell and returns structured output.

    Args:
        test_command: Shell command to execute (relative to shadow cell root).
        timeout:      Max seconds before the process is killed (default 300).
        env_extras:   Extra environment variables to inject.

    Returns:
        Dict with keys: stdout, stderr, returncode, command.
    """
    if not SHADOW_DIR.exists():
        raise RuntimeError(
            "Shadow Cell does not exist. Call spin_up_shadow_cell() first."
        )

    print(f"   ⏱️  Benchmarking: {test_command}")
    env = {**os.environ, **(env_extras or {})}
    # Exclude the live venv from PATH so shadow runs in its own context
    env.pop("VIRTUAL_ENV", None)

    try:
        result = subprocess.run(
            test_command,
            cwd=SHADOW_DIR,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return {
            "command": test_command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "command": test_command,
            "stdout": "",
            "stderr": f"TIMEOUT after {timeout}s",
            "returncode": -1,
        }


def destroy_shadow_cell() -> None:
    """Terminates the experiment matrix and reclaims disk space."""
    if SHADOW_DIR.exists():
        shutil.rmtree(SHADOW_DIR)
        print("   💥 Shadow Cell destroyed.")
    else:
        print("   ℹ️  No Shadow Cell to destroy.")


def shadow_cell_status() -> dict[str, object]:
    """Returns a dict describing the current state of the shadow cell."""
    exists = SHADOW_DIR.exists() and MARKER_FILE.exists()
    size_mb = _dir_size_mb(SHADOW_DIR) if SHADOW_DIR.exists() else 0.0
    return {
        "exists": exists,
        "path": str(SHADOW_DIR),
        "size_mb": round(size_mb, 1),
        "marker_present": MARKER_FILE.exists() if SHADOW_DIR.exists() else False,
    }


# ---------------------------------------------------------------------------
# Context Manager
# ---------------------------------------------------------------------------

class ShadowCell:
    """
    Context manager for scoped Shadow Cell lifecycle.

    Usage:
        with ShadowCell() as cell:
            cell.run("python benchmark.py")
    """

    def __init__(self, force: bool = True) -> None:
        self._force = force
        self.path: str = ""

    def __enter__(self) -> "ShadowCell":
        self.path = spin_up_shadow_cell(force=self._force)
        return self

    def __exit__(self, *_: object) -> None:
        destroy_shadow_cell()

    def run(self, command: str, timeout: int = 300) -> dict[str, str | int]:
        """Execute a command inside the cell and return output dict."""
        return execute_shadow_benchmark(command, timeout=timeout)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _banner(msg: str) -> None:
    print("\n" + "🧬" * 10)
    print(msg)


def _dir_size_mb(path: Path) -> float:
    total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    return total / (1024 * 1024)


def _print_dir_size(path: Path) -> None:
    try:
        mb = _dir_size_mb(path)
        print(f"   📦 Shadow Cell size: {mb:.1f} MB")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Shadow Cell Manager")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("up", help="Spin up a Shadow Cell")
    sub.add_parser("down", help="Destroy the Shadow Cell")
    sub.add_parser("status", help="Print Shadow Cell status")
    bench = sub.add_parser("bench", help="Run a benchmark inside the cell")
    bench.add_argument("command", nargs=argparse.REMAINDER)

    args = parser.parse_args()
    if args.cmd == "up":
        spin_up_shadow_cell()
    elif args.cmd == "down":
        destroy_shadow_cell()
    elif args.cmd == "status":
        import json
        print(json.dumps(shadow_cell_status(), indent=2))
    elif args.cmd == "bench":
        cmd = " ".join(args.command)
        result = execute_shadow_benchmark(cmd)
        print(result["stdout"])
        if result["stderr"]:
            print("STDERR:", result["stderr"], file=sys.stderr)
    else:
        parser.print_help()
