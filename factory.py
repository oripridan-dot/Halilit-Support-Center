#!/usr/bin/env python3
"""
THE DARK FACTORY SUPERVISOR
---------------------------
This script acts as the "Foreman". It coordinates the agents (scripts)
to ensure the Output (App) matches the Input (Specs).
"""
import os
import sys
import json
import subprocess
from pathlib import Path
import time

# --- CONFIGURATION ---
ROOT_DIR = Path(__file__).parent
SPECS_DIR = ROOT_DIR / "specs"
BACKEND_DIR = ROOT_DIR / "backend"
DATA_ARTIFACT = BACKEND_DIR / "data" / "learned_taxonomy.json"


def log(step, msg, status="INFO"):
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARN": "⚠️", "FAIL": "❌", "WORK": "⚙️"}
    print(f"{icons.get(status, '')} [{step}] {msg}")


def read_spec(spec_name):
    """Reads a markdown spec to understand success criteria."""
    spec_path = SPECS_DIR / spec_name
    if not spec_path.exists():
        log("SPEC", f"Missing specification: {spec_name}", "FAIL")
        sys.exit(1)
    return spec_path.read_text()


def run_agent_conductor(mode="rebuild-catalog"):
    """Hires the Conductor Agent to ingest data."""
    log("AGENT", f"Conductor starting task: {mode}...", "WORK")
    start = time.time()

    # Run the existing conductor script
    cmd = [sys.executable, "conductor_main.py", mode]
    result = subprocess.run(cmd, cwd=BACKEND_DIR, capture_output=True, text=True)

    if result.returncode != 0:
        log("AGENT", "Conductor crashed!", "FAIL")
        print(result.stderr)
        sys.exit(1)

    duration = round(time.time() - start, 2)
    log("AGENT", f"Conductor finished in {duration}s", "SUCCESS")


def quality_control_data():
    """Validates the artifact against the 'Data Spec'."""
    log("QC", "Inspecting data artifacts...", "WORK")

    if not DATA_ARTIFACT.exists():
        log("QC", "Critical Artifact Missing: learned_taxonomy.json", "FAIL")
        return False

    try:
        with open(DATA_ARTIFACT) as f:
            data = json.load(f)

        # Example QC Rule from Spec: "Catalog must not be empty"
        count = 0
        if isinstance(data, list):
            count = len(data)
        elif isinstance(data, dict):
            count = sum(len(v) for v in data.values())

        if count < 100:
            log("QC", f"Catalog too small ({count} items). Rejecting batch.", "FAIL")
            return False

        log("QC", f"Artifact Approved: {count} items ready for distribution.", "SUCCESS")
        return True
    except Exception as e:
        log("QC", f"Corrupt Artifact: {e}", "FAIL")
        return False


def boot_console():
    """Starts the Operator Console."""
    log("OPS", "Booting System...", "WORK")

    # 1. Start Backend API
    api_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--port", "8000"],
        cwd=BACKEND_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    log("OPS", "API Server Online (Port 8000)", "SUCCESS")

    # 2. Start Frontend
    log("OPS", "Frontend Interface Launching...", "INFO")
    subprocess.run(["npm", "run", "dev"], cwd=ROOT_DIR / "frontend")


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "start"

    if action == "build":
        # 1. Read Spec
        # spec = read_spec("01_ingestion.md")
        # 2. Run Agent
        run_agent_conductor("rebuild-catalog")
        # 3. QC Output
        if not quality_control_data():
            sys.exit(1)

    elif action == "start":
        if not quality_control_data():
            log("OPS", "Data stale. Running auto-build...", "WARN")
            run_agent_conductor("rebuild-catalog")
        boot_console()

    elif action == "purge":
        # The Cleanup Crew
        log("CLEAN", "Removing legacy 'Galaxy' debris...", "WORK")
        paths_to_delete = [
            "frontend/src/components/views/GalaxyDashboard.tsx",
            "frontend/src/components/views/SpectrumModule.tsx",
            "frontend/src/components/views/arena",
            "frontend/src/components/views/galaxy",
            "frontend/src/components/v0",
            "frontend/public/assets/bg",
        ]
        for p in paths_to_delete:
            path = ROOT_DIR / p
            if path.exists():
                subprocess.run(["rm", "-rf", str(path)])
                log("CLEAN", f"Deleted {p}", "INFO")
        log("CLEAN", "Factory Floor Clean.", "SUCCESS")

    else:
        log("OPS", f"Unknown action: {action}. Use: build | start | purge", "FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
