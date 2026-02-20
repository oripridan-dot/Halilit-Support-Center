"""
heartbeat_daemon.py — Halilit Dark Factory | Proactive Heartbeat Layer
=======================================================================
Inspired by the OpenClaw "Heartbeat" architecture pattern.

This module acts as the lightweight, standalone entry point for the
nightly autonomous sweep. It is called by night_shift.sh (or a cron
job) and orchestrates:

  1. CATALOG DELTA SCAN  — checks for new / changed product schemas in
                           the Halilit data directory via fast mtime
                           comparison against the last snapshot.
  2. TECH LEAD BRIEFING  — invokes generate_morning_briefing() to produce
                           DAILY_BRIEFING.md via the LLM Tech Lead agent.
  3. HEARTBEAT LOG       — writes HEARTBEAT.md to the project root so the
                           Operator has an instant status overview on
                           startup without opening the IDE.

Security note (anti-OpenClaw):
  This daemon never downloads or executes external skill files. All code
  paths are local and pre-audited. No dynamic eval, no ClawHub.

Usage:
  python backend/factory/heartbeat_daemon.py

  Or via night_shift.sh (automatic cron wrapper).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Path bootstrap — works whether this file is run directly or imported
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

# ---------------------------------------------------------------------------
# Optional Tech Lead import — graceful fallback if LLM is unavailable
# ---------------------------------------------------------------------------
try:
    from backend.factory.tech_lead_agent import generate_morning_briefing  # type: ignore
    _TECH_LEAD_AVAILABLE = True
except ImportError:  # pragma: no cover
    _TECH_LEAD_AVAILABLE = False

    def generate_morning_briefing() -> None:  # type: ignore[misc]
        print("   ⚠️  tech_lead_agent not importable — briefing skipped.")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DATA_DIR = ROOT_DIR / "backend" / "data"
BRANDS_DIR = DATA_DIR / "brands"
SNAPSHOT_PATH = DATA_DIR / "heartbeat_snapshot.json"
HEARTBEAT_PATH = ROOT_DIR / "HEARTBEAT.md"

DIVIDER = "=" * 62


# ---------------------------------------------------------------------------
# 1. CATALOG DELTA SCAN
# ---------------------------------------------------------------------------

def _collect_mtimes(directory: Path) -> dict[str, float]:
    """Return {relative_path: mtime} for all .json files under *directory*."""
    mtimes: dict[str, float] = {}
    if not directory.exists():
        return mtimes
    for p in directory.rglob("*.json"):
        key = p.relative_to(ROOT_DIR).as_posix()
        mtimes[key] = p.stat().st_mtime
    return mtimes


def run_catalog_delta_scan() -> dict[str, Any]:
    """
    Compare current .json mtimes in backend/data/brands/ against last
    snapshot. Returns a summary dict consumed by the heartbeat logger.
    """
    print("   📂 Scanning brand JSON files for schema changes...")
    current = _collect_mtimes(BRANDS_DIR)

    if SNAPSHOT_PATH.exists():
        try:
            previous: dict[str, float] = json.loads(SNAPSHOT_PATH.read_text())
        except json.JSONDecodeError:
            previous = {}
    else:
        previous = {}

    new_files = sorted(set(current) - set(previous))
    changed = sorted(
        k for k in (set(current) & set(previous)) if current[k] != previous[k]
    )
    removed = sorted(set(previous) - set(current))

    # Persist new snapshot
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(json.dumps(current, indent=2), encoding="utf-8")

    result: dict[str, Any] = {
        "total_files": len(current),
        "new": new_files,
        "changed": changed,
        "removed": removed,
        "status": "delta_detected" if (new_files or changed or removed) else "clean",
    }

    if result["status"] == "clean":
        print(f"   ✅ No schema changes detected ({len(current)} files scanned).")
    else:
        if new_files:
            print(f"   🆕 New files     : {len(new_files)}")
            for f in new_files[:5]:
                print(f"        + {f}")
            if len(new_files) > 5:
                print(f"        … and {len(new_files) - 5} more")
        if changed:
            print(f"   🔄 Modified files : {len(changed)}")
        if removed:
            print(f"   🗑️  Removed files  : {len(removed)}")

    return result


# ---------------------------------------------------------------------------
# 2. HEARTBEAT.md WRITER
# ---------------------------------------------------------------------------

_STATUS_ICON = {"clean": "🟢", "delta_detected": "🟡", "error": "🔴"}


def write_heartbeat_md(
    timestamp: str,
    scan_result: dict[str, Any],
    briefing_ok: bool,
    elapsed_s: float,
) -> None:
    """Write a concise HEARTBEAT.md to the project root."""
    icon = _STATUS_ICON.get(scan_result.get("status", "error"), "⚪")
    delta_lines: list[str] = []

    if scan_result["new"]:
        delta_lines.append(f"- **New:** {', '.join(scan_result['new'][:10])}")
    if scan_result["changed"]:
        delta_lines.append(f"- **Modified:** {len(scan_result['changed'])} file(s)")
    if scan_result["removed"]:
        delta_lines.append(f"- **Removed:** {', '.join(scan_result['removed'][:5])}")

    delta_section = "\n".join(delta_lines) if delta_lines else "_No changes detected._"

    content = f"""\
# 🫀 Halilit Dark Factory — Heartbeat Log

**Last Autonomous Sweep:** `{timestamp}`
**Elapsed:** `{elapsed_s:.1f}s`
**Overall Status:** {icon} `{scan_result.get("status", "unknown").upper()}`

---

## 1. Catalog Delta Scan

- **Files Scanned:** {scan_result.get("total_files", 0)} brand JSON files
{delta_section}

## 2. Tech Lead Briefing

{"✅ `DAILY_BRIEFING.md` compiled — open it for the full morning briefing." if briefing_ok else "⚠️ Briefing skipped (LLM unavailable or import error). Check `DAILY_BRIEFING.md` for raw heuristics fallback."}

---

> 🏭 Dark Factory is primed and awaiting Operator commands.
> Open `DAILY_BRIEFING.md` for the full strategic briefing.
"""
    HEARTBEAT_PATH.write_text(content, encoding="utf-8")
    print(f"   📝 HEARTBEAT.md written → {HEARTBEAT_PATH}")


# ---------------------------------------------------------------------------
# 3. MAIN ORCHESTRATOR
# ---------------------------------------------------------------------------

def run_nightly_heartbeat() -> None:
    """
    Full heartbeat cycle:
      1. Catalog delta scan
      2. Tech Lead morning briefing (DAILY_BRIEFING.md)
      3. Write HEARTBEAT.md
    """
    start = datetime.now()
    timestamp = start.strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{DIVIDER}")
    print(f"  🫀  HEARTBEAT IGNITED  —  {timestamp}")
    print(DIVIDER)

    # — Step 1: Catalog delta scan —
    print("\n🔍 [1/3] Data Scout: Catalog Delta Scan")
    try:
        scan_result = run_catalog_delta_scan()
    except Exception as exc:  # pragma: no cover
        print(f"   ❌ Scan error: {exc}")
        scan_result = {"total_files": 0, "new": [], "changed": [], "removed": [], "status": "error"}

    # — Step 2: Tech Lead briefing —
    print("\n🧠 [2/3] Tech Lead: Compiling DAILY_BRIEFING.md")
    briefing_ok = False
    if _TECH_LEAD_AVAILABLE:
        try:
            generate_morning_briefing()
            briefing_ok = True
        except Exception as exc:  # pragma: no cover
            print(f"   ❌ Briefing error: {exc}")
    else:
        generate_morning_briefing()  # runs the placeholder

    # — Step 3: Write HEARTBEAT.md —
    print("\n📝 [3/3] Writing HEARTBEAT.md")
    elapsed = (datetime.now() - start).total_seconds()
    try:
        write_heartbeat_md(timestamp, scan_result, briefing_ok, elapsed)
    except Exception as exc:  # pragma: no cover
        print(f"   ❌ Failed to write HEARTBEAT.md: {exc}")

    print(f"\n{DIVIDER}")
    print(f"  💤  Heartbeat cycle complete — {elapsed:.1f}s")
    print(DIVIDER + "\n")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_nightly_heartbeat()
