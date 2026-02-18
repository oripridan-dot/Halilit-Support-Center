import sys
import subprocess
import shutil
import os
from pathlib import Path

# --- CONFIGURATION ---
ROOT = Path(__file__).parent
FRONTEND = ROOT / "frontend"
BACKEND = ROOT / "backend"
SPECS = ROOT / "specs"

def log(msg): print(f"🏭 [FACTORY] {msg}")

def setup_factory():
    """Establishes the Dark Factory folder structure."""
    log("Initializing Factory Layout...")

    # 1. Create Spec Directories
    SPECS.mkdir(exist_ok=True)
    (SPECS / "data").mkdir(exist_ok=True)
    (SPECS / "ui").mkdir(exist_ok=True)
    (SPECS / "scenarios").mkdir(exist_ok=True)

    # 2. Migrate Agent Skills (Blueprints)
    skills_dir = BACKEND / "agent_skills"
    if skills_dir.exists():
        log("Migrating agent skills to Specs...")
        for file in skills_dir.glob("*.md"):
            shutil.move(str(file), str(SPECS / "data" / file.name))
        shutil.rmtree(skills_dir)
        log("✅ Agent Skills moved to /specs/data")

    # 3. Create Default UI Spec if missing
    ui_spec = SPECS / "ui" / "operator_console.md"
    if not ui_spec.exists():
        ui_spec.write_text("""# Operator Console UI Spec
- Theme: Dark Zinc
- Layout: Sidebar + Header + Content
- Views: Dashboard, Inventory (Grid), Product Detail (Tabs)
""")
        log("✅ Created default UI Spec")

def purge_legacy():
    """Removes all code related to the old 'Game/Galaxy' interface."""
    log("Purging Legacy 'Visual OS' modules...")

    removals = [
        FRONTEND / "src/components/views/GalaxyDashboard.tsx",
        FRONTEND / "src/components/views/SpectrumModule.tsx",
        FRONTEND / "src/components/views/arena",
        FRONTEND / "src/components/views/galaxy",
        FRONTEND / "src/components/v0",
        FRONTEND / "public/assets/bg", # Heavy background images
    ]

    for path in removals:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            log(f"🗑️ Deleted legacy artifact: {path.name}")
        else:
            log(f"🤷 {path.name} already gone.")

def build_backend():
    """Runs the Conductor to generate the Golden Catalog."""
    log("Starting Production Line: Data Ingestion...")
    try:
        # Install requirements if needed
        req_file = BACKEND / "requirements.txt"
        if req_file.exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(req_file)], cwd=BACKEND, check=False)

        # Run Conductor
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BACKEND)
        subprocess.run([sys.executable, "conductor_main.py", "rebuild-catalog"], cwd=BACKEND, env=env, check=True)
        log("✅ Data Build Complete.")
    except subprocess.CalledProcessError as e:
        log(f"❌ Data Build Failed: {e}")
        sys.exit(1)

def run_agent_builder(spec_name):
    """Activates the Builder Agent to implement a spec."""
    log(f"Assigning Builder to Spec: {spec_name}...")
    name = spec_name if spec_name.endswith(".md") else f"{spec_name}.md"
    spec_path = SPECS / "ui" / name

    if not spec_path.exists():
        log(f"❌ Spec {name} not found in {SPECS}/ui")
        sys.exit(1)

    agent_script = BACKEND / "factory" / "builder_agent.py"
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(BACKEND), str(BACKEND / "factory")])

    result = subprocess.run(
        [sys.executable, str(agent_script), str(spec_path.resolve())],
        cwd=BACKEND,
        env=env,
        capture_output=True,
        text=True,
    )

    print(result.stdout)
    if result.stderr:
        print("ERR:", result.stderr)
    if result.returncode != 0:
        sys.exit(result.returncode)

def start_system():
    """Launches the consolidated Operator Console."""
    log("🚀 Launching Factory Output...")

    # Start Backend API
    api = subprocess.Popen([sys.executable, "-m", "uvicorn", "server:app", "--reload", "--port", "8000"], cwd=BACKEND)

    # Start Frontend
    try:
        subprocess.run(["npm", "run", "dev"], cwd=FRONTEND, check=True)
    except KeyboardInterrupt:
        log("Shutting down...")
        api.terminate()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python factory.py [init|setup|purge|build|implement <spec>|start]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "init" or cmd == "setup":
        setup_factory()
        purge_legacy()
    elif cmd == "purge":
        purge_legacy()
    elif cmd == "build":
        build_backend()
    elif cmd == "implement":
        if len(sys.argv) < 3:
            log("❌ implement requires a spec name (e.g. InventoryGrid.md)")
            sys.exit(1)
        run_agent_builder(sys.argv[2])
    elif cmd == "start":
        start_system()
    else:
        print(f"Unknown command: {cmd}")
