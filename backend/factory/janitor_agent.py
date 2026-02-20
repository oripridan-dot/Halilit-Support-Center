"""
JANITOR AGENT — backend/factory/janitor_agent.py
=================================================
The Excretory System of the Bio-Swarm.

Every synthesis cycle generates metabolic waste:
  - specs/temp/          ← Task-force blackboards, steerer scratch pads
  - frontend/**/*.backup.* ← Safety copies written by the Builder before patching
  - backend/data/ai_cache/ ← LLM response cache (keep last N days)
  - factory_logs/        ← Old factory run logs (keep last N days)
  - backend/logs/        ← Backend stdout logs (keep last N days)

`metabolic_flush()` is called automatically after every successful Review
Gate commit (wired in nexus.py).  It can also be run standalone:

    python backend/factory/janitor_agent.py [--dry-run] [--silent]
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# How many days of AI-cache and log files to keep
CACHE_TTL_DAYS = 7
LOG_TTL_DAYS = 14

# Directories that are safe to wipe entirely on each flush
TEMP_DIRS: list[Path] = [
    ROOT_DIR / "specs" / "temp",
]

# Glob patterns inside frontend/src that are always safe to remove
BACKUP_PATTERNS: list[str] = [
    "*.backup.*",    # *.backup.tsx, *.backup.ts, etc.
    "*.bak",
    "*.orig",
]

# Time-bounded cache dirs: delete files older than CACHE_TTL_DAYS
CACHE_DIRS: list[Path] = [
    ROOT_DIR / "backend" / "data" / "ai_cache",
]

# Time-bounded log dirs: delete files older than LOG_TTL_DAYS
LOG_DIRS: list[Path] = [
    ROOT_DIR / "factory_logs",
    ROOT_DIR / "backend" / "logs",
    ROOT_DIR / "logs",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _remove(path: Path, dry_run: bool, silent: bool) -> int:
    """Delete a single file. Returns 1 on success, 0 if dry-run or error."""
    if dry_run:
        if not silent:
            print(f"   [DRY-RUN] would delete: {path.relative_to(ROOT_DIR)}")
        return 0
    try:
        path.unlink()
        if not silent:
            print(f"   🧹 Deleted: {path.relative_to(ROOT_DIR)}")
        return 1
    except OSError as exc:
        if not silent:
            print(f"   ⚠️  Could not delete {path.name}: {exc}")
        return 0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def metabolic_flush(dry_run: bool = False, silent: bool = False) -> int:
    """
    The Excretory System — safely removes metabolic waste.

    Args:
        dry_run: If True, only report what *would* be deleted without touching disk.
        silent:  If True, suppress all output (useful for automated pipelines).

    Returns:
        Number of files actually deleted (0 in dry-run mode).
    """
    if not silent:
        width = 60
        print("\n" + "=" * width)
        suffix = " [DRY-RUN]" if dry_run else ""
        print(f"🚽  METABOLIC FLUSH — Garbage Collection{suffix}")
        print("=" * width)

    total_cleared = 0

    # ── 1. Temp phenotypes (task-force blackboards, steerer scratch)  ────────
    for temp_dir in TEMP_DIRS:
        if not temp_dir.exists():
            continue
        flushed = 0
        for file in sorted(temp_dir.glob("*")):
            if file.is_file() and file.name not in (".gitkeep", ".gitignore"):
                total_cleared += _remove(file, dry_run, silent)
                flushed += 1
        if flushed and not silent:
            print(
                f"   📂 {temp_dir.relative_to(ROOT_DIR)}: {flushed} temp file(s) cleared")

    # ── 2. Builder backup files in frontend/src  ─────────────────────────────
    frontend_src = ROOT_DIR / "frontend" / "src"
    if frontend_src.exists():
        backup_count = 0
        for pattern in BACKUP_PATTERNS:
            for file in frontend_src.rglob(pattern):
                total_cleared += _remove(file, dry_run, silent)
                backup_count += 1
        if backup_count and not silent:
            print(f"   📂 frontend/src: {backup_count} backup file(s) cleared")

    # ── 3. Stale AI-cache entries (older than CACHE_TTL_DAYS)  ───────────────
    cache_threshold = datetime.now() - timedelta(days=CACHE_TTL_DAYS)
    for cache_dir in CACHE_DIRS:
        if not cache_dir.exists():
            continue
        stale = 0
        for file in cache_dir.glob("*.json"):
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if mtime < cache_threshold:
                total_cleared += _remove(file, dry_run, silent)
                stale += 1
        if stale and not silent:
            print(
                f"   📂 {cache_dir.relative_to(ROOT_DIR)}: "
                f"{stale} cache file(s) older than {CACHE_TTL_DAYS}d cleared"
            )

    # ── 4. Old log files (older than LOG_TTL_DAYS)  ──────────────────────────
    log_threshold = datetime.now() - timedelta(days=LOG_TTL_DAYS)
    for log_dir in LOG_DIRS:
        if not log_dir.exists():
            continue
        old_logs = 0
        for file in log_dir.glob("*"):
            if not file.is_file():
                continue
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if mtime < log_threshold and file.suffix in (".log", ".txt", ".json", ""):
                total_cleared += _remove(file, dry_run, silent)
                old_logs += 1
        if old_logs and not silent:
            print(
                f"   📂 {log_dir.relative_to(ROOT_DIR)}: "
                f"{old_logs} log file(s) older than {LOG_TTL_DAYS}d cleared"
            )

    # ── Summary  ──────────────────────────────────────────────────────────────
    if not silent:
        if total_cleared > 0 or dry_run:
            verb = "would remove" if dry_run else "removed"
            print(
                f"\n✅  Flush complete — {total_cleared} waste artifact(s) {verb}.")
        else:
            print("\n✨  System is clean. No metabolic waste found.")
        print("=" * 60 + "\n")

    return total_cleared


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _dry = "--dry-run" in sys.argv or "-n" in sys.argv
    _sil = "--silent" in sys.argv or "-s" in sys.argv
    count = metabolic_flush(dry_run=_dry, silent=_sil)
    sys.exit(0)
