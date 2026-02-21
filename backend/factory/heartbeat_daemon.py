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
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Optional schedule import — graceful fallback so the daemon still works if
# the 'schedule' package is not yet installed.
# ---------------------------------------------------------------------------
try:
    import schedule as _schedule  # type: ignore
    _SCHEDULE_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SCHEDULE_AVAILABLE = False
    _schedule = None  # type: ignore

# ---------------------------------------------------------------------------
# Optional Active Sonar import — graceful fallback
# ---------------------------------------------------------------------------
try:
    from backend.factory.active_sonar import execute_sonar_sweep  # type: ignore
    _SONAR_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SONAR_AVAILABLE = False

    def execute_sonar_sweep() -> dict:  # type: ignore[misc]
        print("   ⚠️  active_sonar not importable — sonar sweep skipped.")
        return {}

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
# Optional Darwin Agent import — graceful fallback if LLM is unavailable
# ---------------------------------------------------------------------------
try:
    from backend.factory.darwin_agent import initiate_darwin_experiment  # type: ignore
    _DARWIN_AVAILABLE = True
except ImportError:  # pragma: no cover
    _DARWIN_AVAILABLE = False

    # type: ignore[misc]
    def initiate_darwin_experiment(*_args: Any, **_kwargs: Any) -> str:
        return "[Darwin Agent not available — no GEMINI_API_KEY or import error]"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DATA_DIR = ROOT_DIR / "backend" / "data"
BRANDS_DIR = DATA_DIR / "brands"
SNAPSHOT_PATH = DATA_DIR / "heartbeat_snapshot.json"
HEARTBEAT_PATH = ROOT_DIR / "HEARTBEAT.md"

DIVIDER = "=" * 62

# How often to run a Darwin Experiment (in days).
# Set to 0 to disable automatic Darwin experiments.
DARWIN_CYCLE_DAYS: int = int(os.environ.get("DARWIN_CYCLE_DAYS", "7"))

# File that tracks when the last Darwin experiment ran.
_DARWIN_STATE_PATH = ROOT_DIR / "backend" / "data" / "darwin_last_run.txt"

# Default hypothesis pool — the Heartbeat picks one unless DARWIN_HYPOTHESIS
# env var is set by the operator.
_DEFAULT_HYPOTHESES = [
    "The catalog's product normalization pass makes too many redundant dict copies — a lazy iterator pattern might reduce peak memory.",
    "The JIT agent re-reads spec files from disk on every request — an LRU in-process cache could eliminate most of that I/O.",
    "SQLite is used for brand data but the access pattern is pure key-value — a shelve or LMDB store might be faster for cold reads.",
    "The frontend bundles all cockpit components eagerly — React.lazy() code-splitting on ProductDetailView could reduce initial JS parse time.",
    "The product graph is rebuilt from scratch on every server start — persisting it as a compact adjacency list JSON could cut startup latency.",
]


# ---------------------------------------------------------------------------
# 1. CATALOG DELTA SCAN
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Darwin Protocol helpers
# ---------------------------------------------------------------------------

def _darwin_due() -> bool:
    """Returns True if a Darwin Experiment is due based on DARWIN_CYCLE_DAYS."""
    if DARWIN_CYCLE_DAYS <= 0:
        return False
    if not _DARWIN_STATE_PATH.exists():
        return True
    try:
        last_run_ts = float(_DARWIN_STATE_PATH.read_text().strip())
        elapsed_days = (datetime.now().timestamp() - last_run_ts) / 86400
        return elapsed_days >= DARWIN_CYCLE_DAYS
    except Exception:
        return True  # Treat corrupt state as "due"


def _record_darwin_run() -> None:
    """Stamp the current time as the last Darwin run."""
    _DARWIN_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _DARWIN_STATE_PATH.write_text(
        str(datetime.now().timestamp()), encoding="utf-8")


def run_darwin_protocol() -> dict[str, Any]:
    """
    Runs a Darwin Experiment if one is due.
    Returns a summary dict for inclusion in HEARTBEAT.md.
    """
    result: dict[str, Any] = {
        "ran": False,
        "hypothesis": "",
        "proposal_written": False,
        "output_snippet": "",
        "error": "",
    }

    if not _darwin_due():
        return result

    print("   🧬 Darwin Experiment is due — activating Darwin Agent…")

    import random
    hypothesis = os.environ.get(
        "DARWIN_HYPOTHESIS",
        random.choice(_DEFAULT_HYPOTHESES),
    )
    result["hypothesis"] = hypothesis

    try:
        plan_md = initiate_darwin_experiment(hypothesis, run_in_cell=False)
        result["ran"] = True
        result["output_snippet"] = plan_md[:800]
        proposal_path = ROOT_DIR / "PARADIGM_SHIFT_PROPOSAL.md"
        result["proposal_written"] = proposal_path.exists()
        _record_darwin_run()
        print("   ✅ Darwin experiment complete.")
    except Exception as exc:
        result["error"] = str(exc)
        print(f"   ❌ Darwin experiment error: {exc}")

    return result


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
        print(
            f"   ✅ No schema changes detected ({len(current)} files scanned).")
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
    darwin_result: dict[str, Any] | None = None,
) -> None:
    """Write a concise HEARTBEAT.md to the project root."""
    icon = _STATUS_ICON.get(scan_result.get("status", "error"), "⚪")
    delta_lines: list[str] = []

    if scan_result["new"]:
        delta_lines.append(f"- **New:** {', '.join(scan_result['new'][:10])}")
    if scan_result["changed"]:
        delta_lines.append(
            f"- **Modified:** {len(scan_result['changed'])} file(s)")
    if scan_result["removed"]:
        delta_lines.append(
            f"- **Removed:** {', '.join(scan_result['removed'][:5])}")

    delta_section = "\n".join(
        delta_lines) if delta_lines else "_No changes detected._"

    # --- Darwin Protocol section ---
    if darwin_result and darwin_result.get("ran"):
        proposal_notice = (
            "\n> 🚨 **PARADIGM_SHIFT_PROPOSAL.md** has been written. Open it for the full report."
            if darwin_result.get("proposal_written") else ""
        )
        darwin_section = (
            f"## 3. Darwin Protocol (Architectural Red Team)\n\n"
            f"✅ Experiment ran.{proposal_notice}\n"
            f"**Hypothesis explored:** _{darwin_result.get('hypothesis', 'N/A')}_\n"
        )
    elif darwin_result and darwin_result.get("error"):
        darwin_section = (
            f"## 3. Darwin Protocol (Architectural Red Team)\n\n"
            f"⚠️ Experiment failed: `{darwin_result['error']}`\n"
        )
    elif darwin_result is not None and not darwin_result.get("ran"):
        darwin_section = (
            "## 3. Darwin Protocol (Architectural Red Team)\n\n"
            "_Not due yet. Next experiment scheduled per `DARWIN_CYCLE_DAYS` setting._\n"
        )
    else:
        darwin_section = ""

    darwin_divider = "\n---\n" if darwin_section else ""

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
{darwin_divider}{darwin_section}
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
      3. Darwin Protocol (architectural self-disruption — weekly cadence)
      4. Write HEARTBEAT.md
    """
    start = datetime.now()
    timestamp = start.strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{DIVIDER}")
    print(f"  🫀  HEARTBEAT IGNITED  —  {timestamp}")
    print(DIVIDER)

    # — Step 1: Catalog delta scan —
    print("\n🔍 [1/4] Data Scout: Catalog Delta Scan")
    try:
        scan_result = run_catalog_delta_scan()
    except Exception as exc:  # pragma: no cover
        print(f"   ❌ Scan error: {exc}")
        scan_result = {"total_files": 0, "new": [],
                       "changed": [], "removed": [], "status": "error"}

    # — Step 2: Tech Lead briefing —
    print("\n🧠 [2/4] Tech Lead: Compiling DAILY_BRIEFING.md")
    briefing_ok = False
    if _TECH_LEAD_AVAILABLE:
        try:
            generate_morning_briefing()
            briefing_ok = True
        except Exception as exc:  # pragma: no cover
            print(f"   ❌ Briefing error: {exc}")
    else:
        generate_morning_briefing()  # runs the placeholder

    # — Step 3: Darwin Protocol (weekly architectural experiment) —
    print("\n🧬 [3/4] Darwin Protocol: Architectural Red Team")
    darwin_result: dict[str, Any] = {
        "ran": False, "hypothesis": "", "proposal_written": False, "error": ""}
    try:
        darwin_result = run_darwin_protocol()
    except Exception as exc:  # pragma: no cover
        darwin_result["error"] = str(exc)
        print(f"   ❌ Darwin Protocol error: {exc}")

    # — Step 4: Write HEARTBEAT.md —
    print("\n📝 [4/4] Writing HEARTBEAT.md")
    elapsed = (datetime.now() - start).total_seconds()
    try:
        write_heartbeat_md(timestamp, scan_result,
                           briefing_ok, elapsed, darwin_result)
    except Exception as exc:  # pragma: no cover
        print(f"   ❌ Failed to write HEARTBEAT.md: {exc}")

    print(f"\n{DIVIDER}")
    print(f"  💤  Heartbeat cycle complete — {elapsed:.1f}s")
    print(DIVIDER + "\n")


# ---------------------------------------------------------------------------
# Persistent daemon: Active Sonar + nightly heartbeat via schedule
# ---------------------------------------------------------------------------

def run_heartbeat() -> None:
    """Persistent daemon entry-point.

    Schedules:
      • Active Sonar sweep every 5 minutes (stack health ping).
      • Full nightly heartbeat once per day (catalog scan + briefing).

    Runs the nightly heartbeat immediately on startup so the Operator
    gets instant output, then enters the cron loop.
    """
    if not _SCHEDULE_AVAILABLE:
        print("❌ 'schedule' package not found. Install it with: pip install schedule")
        print("   Falling back to a single nightly heartbeat run.")
        run_nightly_heartbeat()
        return

    print(f"\n{'🫀' * 5}  HEARTBEAT DAEMON ONLINE  {'🫀' * 5}")
    print("📡 Active Sonar sweeping every 5 minutes.")
    print("🌙 Nightly heartbeat scheduled daily at 03:00.\n")

    # Run the nightly heartbeat immediately on startup
    run_nightly_heartbeat()

    # Run first sonar sweep immediately too
    execute_sonar_sweep()

    # Schedule recurring tasks
    _schedule.every(5).minutes.do(execute_sonar_sweep)
    _schedule.every().day.at("03:00").do(run_nightly_heartbeat)

    while True:
        _schedule.run_pending()
        time.sleep(1)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Halilit Dark Factory — Heartbeat Daemon"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as a persistent daemon with Active Sonar (every 5 min) + nightly heartbeat.",
    )
    args = parser.parse_args()

    if args.daemon:
        run_heartbeat()
    else:
        run_nightly_heartbeat()
