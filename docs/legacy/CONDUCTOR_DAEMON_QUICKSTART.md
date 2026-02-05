# Conductor Daemon Quick Start Guide

## What is the Conductor Daemon?

The **Conductor Daemon** is an active AI assistant for your codebase. Instead of running passive verification scripts, it:

- 🔄 **Monitors files** in real-time and auto-fixes violations
- 🤖 **Coordinates agents** from the Trinity Swarm to perform complex tasks
- 🔀 **Syncs data** bidirectionally between backend and frontend
- 📊 **Provides a CLI** for issuing natural language commands

**TL;DR:** Your codebase learns and fixes itself.

---

## Installation

### 1. Install watchdog (for file monitoring)

```bash
pip install watchdog
```

### 2. Verify installation

```bash
python3 -c "import watchdog; print('✓ watchdog installed')"
```

---

## Running the Daemon

### Start Interactive Mode

```bash
cd /workspaces/Halilit-Support-Center
python3 backend/conductor_daemon.py
```

You should see:

```
🚀 CONDUCTOR DAEMON STARTING
======================================================================
Verifying Spectrum skills...
✅ All skills verified and ready

✓ Event processor thread started
👁️  Watching: /workspaces/Halilit-Support-Center/backend
👁️  Watching: /workspaces/Halilit-Support-Center/frontend/src
✓ File watcher started
✓ Event processor loop started

conductor> _
```

### Stop the Daemon

```
conductor> exit
```

---

## Available Commands

### `status`

Shows daemon health and stats:

```
conductor> status
Conductor Daemon Status
  Running: True
  Event Queue Size: 0
  File Watcher: 🟢 Active
  Standards Rules: 2
  Watched Paths: 2
```

### `verify`

Run a full verification sweep:

```
conductor> verify
✓ Verification queued
[Daemon processes in background]
```

### `sync`

Synchronize data between backend and frontend:

```
conductor> sync
✓ Data sync queued
🔄 BIDIRECTIONAL SYNC
⇒ Backend → Frontend Sync
  ✓ Updated: frontend/public/data/brands.json
  ✓ Updated: frontend/public/data/taxonomy.json
⇐ Frontend → Backend Sync
  ✓ In sync: backend/data/brands/index.json
```

### `fix`

Run auto-fix sweep for all standards violations:

```
conductor> fix
Running auto-fix sweep...
Checking rule: ReactComponentRule
Checking rule: PythonTypeHintRule
✓ Auto-fix sweep complete
```

### `help`

Show all available commands:

```
conductor> help
Available Commands:
  verify    - Run full verification sweep
  sync      - Sync data between backend and frontend
  fix       - Run auto-fix for all standards violations
  status    - Show daemon status
  help      - Show this help message
  exit      - Stop the daemon and exit
```

---

## Auto-Fix in Action

### Example 1: React Component Without Imports

**File Created:** `frontend/src/components/MyComponent.tsx`

```tsx
// Incomplete file
export default function MyComponent() {
  return <div>Hello</div>;
}
```

**What Happens:**

1. Daemon detects file creation
2. `ReactComponentRule` checks it
3. Missing: `import React from 'react'`
4. Daemon auto-fixes:
   ```tsx
   import React from "react";
   // Incomplete file
   export default function MyComponent() {
     return <div>Hello</div>;
   }
   ```
5. Log: `✅ Fixed React imports in frontend/src/components/MyComponent.tsx`

### Example 2: Python Function Without Type Hints

**File Modified:** `backend/mymodule.py`

```python
def process_data(data):
    return data * 2
```

**What Happens:**

1. Daemon detects file modification
2. `PythonTypeHintRule` checks it
3. Missing return type hint
4. Daemon logs warning (manual fix recommended):
   ```
   ⚠️  backend/mymodule.py needs type hints (manual review recommended)
   ```

---

## Coordinator Commands (Natural Language)

The daemon can understand simple commands:

```
conductor> harvest Roland
🤖 Command: harvest Roland
📤 Task submitted: CommercialScout_0_1701234567
   Command: harvest
   Priority: NORMAL
🚀 Executing task: CommercialScout_0_1701234567
   → Harvesting data for: Roland
✓ Task completed: CommercialScout_0_1701234567
```

Available patterns:

- `harvest [brand]` - Harvest product data
- `verify [products]` - Verify product data
- `audit [products]` - Audit for compliance
- `enrich [product_id]` - Enrich product details
- `check risks [product_id]` - Check risk score

---

## Data Sync Deep Dive

### How It Works

The daemon maintains **mappings** between backend and frontend files:

```
backend/data/brands/index.json
         ↕ (bidirectional)
frontend/public/data/brands.json
```

### Sync Directions

#### Backend → Frontend (Primary)

- **When:** File saved in `backend/data/`
- **What:** Copies data to frontend
- **Why:** Backend is source of truth

```
conductor> sync
⇒ Backend → Frontend Sync
✓ Updated: frontend/public/data/brands.json
```

#### Frontend → Backend (Capture Edits)

- **When:** Admin edits in UI
- **What:** Saves changes back to backend
- **Why:** Persist UI edits to permanent storage

```
⇐ Frontend → Backend Sync
✓ Updated: backend/data/brands/index.json
```

### Conflict Resolution

If both sides changed:

1. Daemon detects via checksums
2. Takes frontend version as "latest"
3. Creates backup of backend version
4. Logs conflict for review

```
Conflict detected:
  File: brands.json
  Backend last modified: 2025-02-04 10:30
  Frontend last modified: 2025-02-04 10:35
→ Using frontend version
→ Backup created: brands.json.backup
```

---

## Configuration

Edit `backend/conductor_config.ini`:

### Enable/Disable Features

```ini
[daemon]
enabled = true
run_mode = "interactive"

[file_watcher]
enabled = true
debounce_delay = 0.5

[standards]
auto_fix_enabled = true
auto_fix_mode = "warn"  # or "auto" for silent

[agent_coordination]
enabled = true
```

### Change Watch Paths

```ini
[file_watcher]
watch_paths = [
    "backend/",
    "frontend/src/",
    "custom/path/"
]
```

---

## Troubleshooting

### Daemon won't start

```bash
# Check Python version (3.8+)
python3 --version

# Check imports
python3 -c "from backend.conductor_daemon import ConductorDaemon"
```

### File watcher not detecting changes

```bash
# Check watchdog is installed
pip install watchdog

# Restart daemon
# (Some filesystems/editors require full restart)
```

### Auto-fix broke something

```bash
# Check logs
tail -50 conductor_daemon.log

# Undo with git
git checkout frontend/src/MyComponent.tsx
```

### Sync showing conflicts

```bash
# View sync history
conductor> status

# Check daemon logs for details
tail conductor_daemon.log | grep -i conflict

# Manually review conflicting files
```

---

## Advanced Usage

### Access Agent Coordinator Directly

```python
from backend.agent_coordinator import SwarmCommander

commander = SwarmCommander()
result = commander.execute_command("harvest data for Moog")
print(result)
# Output: {
#   "success": True,
#   "agent": "CommercialScout",
#   "command": "harvest",
#   "result": {"harvested_products": 42},
#   "task_id": "CommercialScout_0_..."
# }
```

### Access Data Synchronizer Directly

```python
from backend.data_synchronizer import DataSynchronizer

sync = DataSynchronizer()
record1, record2 = sync.sync_bidirectional()
status = sync.get_sync_status()
print(status)
# Output: {
#   "last_sync_id": "b2f_...",
#   "status": "success",
#   "files_synced": 3,
#   "timestamp": "2025-02-04T10:30:00"
# }
```

### Create Custom Standards Rule

```python
from backend.conductor_daemon import StandardsRule

class MyCustomRule(StandardsRule):
    def applies_to(self, file_path: str) -> bool:
        return file_path.endswith('.custom')

    def check(self, file_path: str) -> tuple[bool, List[str]]:
        # Your validation logic
        return True, []

    def fix(self, file_path: str) -> bool:
        # Your auto-fix logic
        return True

# Add to daemon
daemon = ConductorDaemon()
daemon.standards_rules.append(MyCustomRule())
```

---

## Monitoring

### Real-Time Logs

```bash
# Follow log file
tail -f conductor_daemon.log

# Filter for specific events
tail -f conductor_daemon.log | grep "✓\|✗\|⚠️"

# View only errors
tail -f conductor_daemon.log | grep ERROR
```

### Event Queue Stats

The daemon maintains a priority queue:

```
Event Queue Size: 5
  - 2 HIGH priority events
  - 3 NORMAL priority events
```

---

## Integration with Your Workflow

### Option 1: Keep Running in Terminal

```bash
# Terminal 1: Run daemon
python3 backend/conductor_daemon.py

# Terminal 2: Do your work normally
# Daemon automatically fixes issues as you save
```

### Option 2: Background Daemon (Coming Soon)

```bash
# Run in background
nohup python3 backend/conductor_daemon.py > conductor.log 2>&1 &

# Check status
conductor status

# Kill when done
conductor stop
```

### Option 3: GitHub Actions (Coming Soon)

Automatically run verification and auto-fix on commits:

```yaml
on: [push, pull_request]
jobs:
  conductor-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Conductor Verification
        run: python3 backend/conductor_daemon.py verify
```

---

## Next Steps

1. **Test locally** (5 min):

   ```bash
   python3 backend/conductor_daemon.py
   conductor> status
   conductor> exit
   ```

2. **Make a change** (5 min):
   - Create a new file in `frontend/src/`
   - Watch daemon auto-fix it
   - Check logs

3. **Try sync** (5 min):

   ```bash
   conductor> sync
   # Watch data mirror to frontend
   ```

4. **Run agent command** (5 min):

   ```bash
   conductor> verify
   # Watch agents run
   ```

5. **Customize** (ongoing):
   - Add your own rules to `standards_rules`
   - Add custom commands to `command_map`
   - Tune config in `conductor_config.ini`

---

## Support

**Need help?** Check:

- `conductor_daemon.log` for detailed logs
- `docs/CONDUCTOR_DAEMON_ARCHITECTURE.md` for architecture
- `backend/conductor_daemon.py` docstrings for code reference
- GitHub issues (create one with daemon logs)

**Want to contribute?**

- Add new `StandardsRule` implementations
- Create custom agent coordinators
- Build monitoring dashboard
- Write tests for new features

---

**Happy coding! 🚀 Your code now fixes itself.**
