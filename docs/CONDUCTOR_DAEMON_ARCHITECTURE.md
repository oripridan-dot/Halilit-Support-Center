# Conductor Daemon: Active AI Assistant Architecture

## Overview

The **Conductor Daemon** transforms the Conductor from a passive verification tool into an **active, event-driven AI assistant** that works alongside developers. It monitors your codebase in real-time, enforces standards automatically, coordinates agent teams, and keeps data synchronized across the full stack.

---

## Core Components

### 1. **Conductor Daemon** (`conductor_daemon.py`)

**Role:** Core orchestrator and event processor

**Key Features:**

- **File Watcher:** Monitors file changes using `watchdog` library
- **Event Queue:** Priority-based event processing
- **Standards Enforcer:** Auto-fixes code standards violations
- **Agent Coordinator:** Routes complex tasks to Trinity Swarm agents

**Architecture:**

```
File Change Event
    ↓
ConductorEventHandler (Debouncer)
    ↓
PriorityQueue
    ↓
EventProcessor (Background Thread)
    ↓
Standards Rules / Handlers
    ↓
Auto-Fix or Escalate to Agent
```

**Verification:** Can run standalone in three modes:

- `background` - Silent file monitoring
- `interactive` - CLI command interface
- `api` - HTTP server mode (future)

---

### 2. **Agent Coordinator** (`agent_coordinator.py`)

**Role:** Swarm commander that orchestrates Trinity Swarm agents

**Key Classes:**

- **`AgentPool`** - Manages CommercialScout, OfficialVerifier, ExternalValidator
- **`SwarmCommander`** - Natural language interface
- **`AgentTask`** - Task model with priority and status tracking

**Workflow:**

```
Natural Language Command
    ↓
SwarmCommander.execute_command()
    ↓
Pattern Matching → Agent + Command
    ↓
AgentPool.submit_task()
    ↓
Task Execution with Error Handling
    ↓
Result + Learning Callback
```

**Example Usage:**

```python
commander = SwarmCommander()
result = commander.execute_command("harvest data for Roland")
# Output: {"success": True, "agent": "CommercialScout", "task_id": "..."}
```

---

### 3. **Data Synchronizer** (`data_synchronizer.py`)

**Role:** Guardian of Truth - Bi-directional data sync

**Sync Modes:**

1. **Backend → Frontend (Primary)**
   - Backend is source of truth
   - Pushes schema, data, configs to frontend

2. **Frontend → Backend (Capture Edits)**
   - Captures admin UI changes
   - Persists to backend with backups

3. **Bidirectional (Merge)**
   - Runs both directions
   - Resolves conflicts by timestamp

**Mappings Example:**

```
backend/data/brands/index.json    → frontend/public/data/brands.json
backend/data/taxonomy.json         → frontend/public/data/taxonomy.json
backend/spectrum_data_provider.py → frontend/src/api/spectrumClient.ts
```

**Features:**

- **Checksums:** Prevents unnecessary updates
- **Backups:** Auto-backup before overwrite
- **Index Rebuild:** Regenerates search indexes
- **Conflict Detection:** Logs conflicts for manual review

---

### 4. **Standards Rules** (Extensible)

Currently Implemented:

#### `ReactComponentRule`

Enforces React/TypeScript component standards:

- Required imports: `import React from 'react'`
- Export statement present
- File size > 100 bytes (prevents 0-byte corruption)

#### `PythonTypeHintRule`

Enforces Python type hints for backend:

- All functions must have return type hints
- Checks for basic type annotation coverage

**Extending Standards:**

```python
class MyRule(StandardsRule):
    def applies_to(self, file_path: str) -> bool:
        return file_path.endswith('.ext')

    def check(self, file_path: str) -> tuple[bool, List[str]]:
        # Return (is_compliant, violations)
        pass

    def fix(self, file_path: str) -> bool:
        # Auto-fix violations
        pass
```

---

## Execution Flows

### Flow 1: File Save → Auto-Check → Auto-Fix

```
Developer saves App.tsx
            ↓
FileSystemEvent (modified)
            ↓
ConductorEventHandler.on_modified()
            ↓
Debounce check (prevent spam)
            ↓
PriorityQueue.put(DaemonEvent)
            ↓
EventProcessor thread picks up event
            ↓
ReactComponentRule.check()
            ↓
Missing React import detected?
    ├─ YES → ReactComponentRule.fix() → Auto-inject
    └─ NO  → All good, continue
            ↓
Verification complete
```

**Result:** Developer is never blocked; violations are fixed silently.

---

### Flow 2: Natural Language Command → Agent Execution

```
User types: "harvest data for Moog"
            ↓
SwarmCommander.execute_command()
            ↓
Pattern match: "harvest" → CommercialScout.harvest
            ↓
AgentPool.submit_task(
    agent_name="CommercialScout",
    command="harvest",
    parameters={"brand": "Moog"},
    priority=NORMAL
)
            ↓
AgentTask created and queued
            ↓
AgentPool.execute_task()
            ↓
CommercialScout.harvest("Moog")
            ↓
Result returned with task_id
```

**Result:** Agent runs autonomously; Conductor monitors and can escalate failures.

---

### Flow 3: Bi-Directional Data Sync

```
trigger_sync() or file_change detected
            ↓
DataSynchronizer.sync_bidirectional()
            ↓
Phase 1: Backend → Frontend
    ├─ Read: backend/data/brands/index.json
    ├─ Transform (if needed)
    ├─ Write: frontend/public/data/brands.json
    ├─ Update checksums
    └─ Log changes
            ↓
Phase 2: Frontend → Backend
    ├─ Read: frontend/public/data/brands.json
    ├─ Compare checksums
    ├─ If changed, backup backend file
    ├─ Write: backend/data/brands/index.json
    └─ Log sync record
            ↓
Rebuild search indexes
            ↓
SyncRecord with summary
```

**Result:** Full stack data consistency without manual intervention.

---

## Configuration

See `conductor_config.ini` for all settings:

```ini
[daemon]
enabled = true
run_mode = "interactive"
log_level = "INFO"

[file_watcher]
enabled = true
debounce_delay = 0.5
watch_paths = ["backend/", "frontend/src/"]

[standards]
auto_fix_enabled = true
auto_fix_mode = "warn"  # or "auto" for silent fixes

[agent_coordination]
enabled = true
agents = ["CommercialScout", "OfficialVerifier", ...]

[data_sync]
enabled = true
sync_direction = "both"
sync_trigger = "auto"
```

---

## Deployment Phases

### Phase 1: Local Development (Current)

✅ Running daemon in interactive mode
✅ File watcher + auto-fix
✅ Agent coordination framework

### Phase 2: Background Daemon

- [ ] Systemd service for Linux
- [ ] LaunchAgent for macOS
- [ ] Silent auto-fix without user prompts
- [ ] Real-time file monitoring

### Phase 3: Natural Language Interface

- [ ] Full NLP command parsing (not just patterns)
- [ ] Multi-turn conversations with agents
- [ ] Context memory between commands
- [ ] Dashboard UI for monitoring

### Phase 4: CI/CD Integration

- [ ] GitHub Actions workflow
- [ ] Auto-fix commits on verification failure
- [ ] Merge gate enforcement
- [ ] Automated rollback on critical issues

### Phase 5: Advanced Features

- [ ] Slack/Email notifications
- [ ] Performance analytics
- [ ] Predictive auto-fix suggestions
- [ ] Custom rule marketplace

---

## Quick Start

### 1. Install Dependencies

```bash
cd /workspaces/Halilit-Support-Center
pip install watchdog
```

### 2. Start the Daemon

```bash
python3 backend/conductor_daemon.py
```

Expected output:

```
🚀 CONDUCTOR DAEMON STARTING
======================================================================
Verifying Spectrum skills...
✅ All skills verified and ready

✓ Event processor thread started
👁️ Watching: /workspaces/Halilit-Support-Center/backend
✓ File watcher started
✓ Event processor loop started

conductor> _
```

### 3. Interactive Commands

```
conductor> status          # Show daemon status
conductor> verify          # Run verification sweep
conductor> sync            # Sync backend ↔ frontend data
conductor> fix             # Run auto-fix sweep
conductor> help            # Show all commands
conductor> exit            # Stop daemon
```

### 4. Test File Auto-Fix

```bash
# In another terminal
echo "// invalid React file" > frontend/src/test.tsx
# Watch daemon automatically fix it
```

### 5. Test Data Sync

```
conductor> sync
```

Will show:

```
🔄 BIDIRECTIONAL SYNC
======================================================================
⇒ Backend → Frontend Sync
  Mappings to sync: 3
----------------------------------------------------------------------
✓ Updated: frontend/public/data/brands.json
✓ Updated: frontend/public/data/taxonomy.json
...
```

---

## Integration with Trinity Swarm

The Conductor becomes the **interface** to your agents:

```python
# Before: Direct agent instantiation
scout = CommercialScout()
scout.harvest("brand")

# After: Via Conductor
commander = SwarmCommander()
result = commander.execute_command("harvest Roland")
# Conductor monitors, logs, auto-retries, escalates
```

---

## File Structure

```
backend/
├── conductor_daemon.py          ⭐ Main daemon + event processor
├── agent_coordinator.py         ⭐ Swarm commander interface
├── data_synchronizer.py         ⭐ Bi-directional sync engine
├── conductor_config.ini         ⭐ Configuration file
├── conductor_spectrum.py        (existing - data verification)
├── conductor_verify_spectrum_v540.py (existing - skill verification)
└── ...
```

---

## Monitoring & Debugging

### Daemon Logs

```bash
tail -f conductor_daemon.log
```

### Event Queue Status

```
conductor> status
```

Shows:

- Event queue size
- File watcher status
- Number of rules
- Watched paths

### Sync History

```python
sync = DataSynchronizer()
print(sync.get_sync_status())
# Output: {"last_sync_id": "...", "status": "success", ...}
```

---

## Next Steps

1. **Test locally:** Run daemon and modify a file to see auto-fix in action
2. **Customize Rules:** Add your own `StandardsRule` implementations
3. **Extend Commands:** Add new patterns to `SwarmCommander.command_map`
4. **Hook into CI:** Create GitHub Action that runs verification
5. **Dashboard:** Build monitoring UI (future phase)

---

## FAQ

**Q: Does this replace my manual verification runs?**
A: Yes, mostly. The daemon catches issues in real-time. You still run manual `verify` commands for full sweeps.

**Q: What if auto-fix breaks something?**
A: Each fix is logged. The daemon tracks what changed and can roll back if needed. Always have version control.

**Q: Can agents run in parallel?**
A: Yes, `AgentPool` supports concurrent task execution. Current implementation is sequential for safety.

**Q: How does it handle file conflicts?**
A: `DataSynchronizer` logs conflicts with timestamps. Admin reviews conflicts manually or via rules.

---

## Architecture Decision Record (ADR)

| Aspect                  | Decision              | Rationale                               |
| ----------------------- | --------------------- | --------------------------------------- |
| **Event Model**         | Priority Queue        | Ensures critical issues processed first |
| **Auto-Fix Safety**     | Debouncing + Logging  | Prevents cascade failures               |
| **Agent Execution**     | Sequential (Phase 1)  | Safe default; parallel in Phase 2       |
| **Data Sync Direction** | Backend-authoritative | Single source of truth principle        |
| **Config Format**       | INI                   | Human-readable, easy to version control |

---

**Status:** ✅ Phase 1 Complete - Ready for Local Testing
