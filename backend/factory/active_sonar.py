"""
active_sonar.py — Halilit Dark Factory | Active Sonar Sweep
============================================================
Proactive synthetic monitoring: pings the entire stack from core to
external edges on a scheduled basis and immediately triggers the
Sovereign Telemetry Reflex Arc if any target goes dark.

Targets checked on every sweep:
  1. Core Backend   — /api/health/deep  (deep organ check)
  2. Frontend Edge  — Vite dev server   (or built static)
  3. External Edge  — halilit.com       (the data-source origin)

On failure, process_production_error() is invoked instantly so the
Telemetry Agent can draft a HOTFIX_PROPOSAL_*.md before a human user
even notices the outage.

Usage (standalone sweep):
  python -m backend.factory.active_sonar

Normally called by heartbeat_daemon.py via schedule.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path bootstrap — works whether run directly or imported
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

import requests  # noqa: E402  (after sys.path patch)

# ---------------------------------------------------------------------------
# Graceful Telemetry import — never crash the sweep if agent is missing
# ---------------------------------------------------------------------------
try:
    from backend.factory.telemetry_agent import process_production_error
    _TELEMETRY_AVAILABLE = True
except ImportError:
    _TELEMETRY_AVAILABLE = False

    def process_production_error(payload: dict) -> str:  # type: ignore[misc]
        print("   ⚠️  telemetry_agent not importable — hotfix draft skipped.")
        return ""

# ---------------------------------------------------------------------------
# Sweep targets
# ---------------------------------------------------------------------------
TARGETS: dict[str, str] = {
    "Core Backend":                  "http://localhost:8000/api/health/deep",
    "Frontend Edge":                 "http://localhost:5173/",
    "External Dependency (Halilit)": "https://www.halilit.com/",
}

TIMEOUT_S: int = 5


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def execute_sonar_sweep() -> dict[str, bool]:
    """Ping every target in TARGETS and trigger the Reflex Arc on failure.

    Returns:
        A dict mapping target name → True (online) / False (offline).
    """
    print("\n" + "🌊" * 10)
    print("📡 INITIATING ACTIVE SONAR SWEEP...")

    results: dict[str, bool] = {}

    for name, url in TARGETS.items():
        try:
            response = requests.get(url, timeout=TIMEOUT_S)
            if response.status_code >= 400:
                raise Exception(f"HTTP {response.status_code}")
            print(f"   ✅ {name} [{url}]: ONLINE")
            results[name] = True
        except Exception as exc:
            print(f"   ❌ {name} [{url}]: OFFLINE or TIMEOUT ({exc})")
            results[name] = False

            # ── Reflex Arc — instantly hand off to Telemetry Agent ──────────
            payload = {
                "event": {
                    "title": f"Active Sonar Failure: {name} is unreachable",
                    "level": "critical",
                    "environment": "production",
                    "culprit": url,
                },
                "stacktrace": (
                    f"Target: {url}\n"
                    f"Error: {exc}\n"
                    "This was detected autonomously by the Active Sonar sweep."
                ),
                "project_name": "Halilit",
            }
            process_production_error(payload)

    print("🌊" * 10 + "\n")
    return results


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    execute_sonar_sweep()
