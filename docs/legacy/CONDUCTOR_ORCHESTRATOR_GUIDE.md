# Conductor Orchestrator v6.0 - Maximized Architecture Guide

## 🎯 Overview

The Conductor has evolved from a **passive verification inspector** into an **active autonomous manager** that continuously monitors, automatically fixes issues, and coordinates your Trinity Swarm agents.

### The Four Dimensions of Maximization

| Dimension                     | Status      | Feature                                           |
| ----------------------------- | ----------- | ------------------------------------------------- |
| **1. Watcher Service**        | ✅ Complete | Real-time filesystem monitoring with `watchdog`   |
| **2. Trinity Swarm Autonomy** | ✅ Complete | Auto-dispatch of agents (Dev, Scout, Maintenance) |
| **3. Data Governance (DAL)**  | ✅ Complete | Centralized API for schema-safe data writes       |
| **4. Deployment Gatekeeper**  | ✅ Complete | Git pre-commit hook blocks imperfect code         |

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           CONDUCTOR ORCHESTRATOR (Central Brain)            │
└─────────────────────────────────────────────────────────────┘
                            ▼
    ┌───────────────────────────────────────────────┐
    │          Event Detection Layer                │
    ├───────────────────────────────────────────────┤
    │ 📂 Data Watcher (data/brands/**)              │
    │    └─► Triggers: rebuild_library()            │
    │                                               │
    │ 📝 Code Watcher (frontend/src/**)             │
    │    └─► Triggers: Standards enforcement        │
    │                                               │
    │ ⚙️  System Watcher (*.log, *.error)           │
    │    └─► Triggers: Error detection              │
    └───────────────────────────────────────────────┘
                            ▼
    ┌───────────────────────────────────────────────┐
    │      Autonomic Remediation Engine             │
    ├───────────────────────────────────────────────┤
    │ 🔍 Error Classification                       │
    │    ├─ MISSING_IMAGE                          │
    │    ├─ INVALID_SCHEMA                         │
    │    ├─ TYPE_MISMATCH                          │
    │    ├─ IMPORT_ERROR                           │
    │    ├─ BUILD_FAILURE                          │
    │    └─ DATA_CORRUPTION                        │
    │                                               │
    │ 🎯 Agent Dispatch                            │
    │    ├─► Scout Agent (missing data)            │
    │    ├─► Dev Agent (code issues)               │
    │    └─► Maintenance Agent (system health)     │
    └───────────────────────────────────────────────┘
                            ▼
    ┌───────────────────────────────────────────────┐
    │       Data Access Layer (DAL)                 │
    ├───────────────────────────────────────────────┤
    │ conductor add-product --brand=Roland          │
    │ conductor validate-schema products.json       │
    │ conductor export-index                        │
    │ conductor list-products                       │
    └───────────────────────────────────────────────┘
                            ▼
    ┌───────────────────────────────────────────────┐
    │    Deployment Gatekeeper (Git Hook)           │
    ├───────────────────────────────────────────────┤
    │ Pre-commit hook runs:                         │
    │ ✓ conductor_verify_spectrum_v540.py           │
    │ ✓ If "Red", commit is BLOCKED                │
    │ ✓ If "Green", commit is ALLOWED              │
    └───────────────────────────────────────────────┘
```

---

## 🚀 Getting Started (60 Seconds)

### Step 1: Start the Orchestrator

```bash
cd /workspaces/Halilit-Support-Center
python3 run_conductor_orchestrator.py
```

You should see:

```
════════════════════════════════════════════════════════════════════════════════
🚀 Conductor Orchestrator v6.0 - Active System Manager
════════════════════════════════════════════════════════════════════════════════

Starting autonomous orchestration system...

⚡ CONDUCTOR ORCHESTRATOR v6.0 INITIALIZING
════════════════════════════════════════════════════════════════════════════════
✓ Base daemon ready
✓ Data watcher started: /workspaces/Halilit-Support-Center/backend/data/brands
✓ Remediation engine ready

🚀 Conductor Orchestrator is ALIVE

Commands:
  status    - Show orchestrator status
  exit      - Gracefully shut down
  dal <cmd> - Use Data Access Layer
════════════════════════════════════════════════════════════════════════════════
```

### Step 2: The Orchestrator Is Now Watching

Your system is now:

- ✅ Watching `backend/data/brands/` for changes
- ✅ Watching `frontend/src/` for code changes
- ✅ Ready to dispatch Trinity Swarm agents on errors
- ✅ Running pre-commit hook verification before commits

### Step 3: Trigger It (Test the System)

While the orchestrator is running in terminal 1, open terminal 2:

```bash
# Add a new product via the Data Access Layer
cd /workspaces/Halilit-Support-Center
python3 -c "
from backend.conductor_orchestrator import ConductorOrchestrator
orch = ConductorOrchestrator()
success, msg = orch._dal_add_product('Roland', 'TR-808', price_il=4999.0)
print(f'Result: {success} - {msg}')
"
```

Watch terminal 1: You'll see the orchestrator **automatically detect the data change** and rebuild the library!

```
📊 Data file modified: roland.json
🔄 Detected data change, rebuilding library...
✅ Library rebuilt successfully
```

---

## 🎯 Dimension 1: Watcher Service (The Nervous System)

### What It Watches

| Path                            | Triggers              | Action                  |
| ------------------------------- | --------------------- | ----------------------- |
| `backend/data/brands/**/*.json` | File modified/created | Rebuild search index    |
| `frontend/src/**/*.{tsx,ts}`    | File modified/created | Enforce React standards |
| `backend/**/*.py`               | File modified/created | Type hint verification  |

### How It Works

```python
# Behind the scenes:
data_watcher = DataWatcherHandler(on_data_change_callback)
observer = Observer()
observer.schedule(data_watcher, "backend/data/brands", recursive=True)
observer.start()  # Runs forever, listens for changes
```

**Key Files:**

- [backend/conductor_orchestrator.py](backend/conductor_orchestrator.py#L76-L95) - DataWatcherHandler class
- [backend/conductor_daemon.py](backend/conductor_daemon.py#L264-L312) - Code watcher

---

## 🎯 Dimension 2: Trinity Swarm Autonomy (The Workforce)

### Autonomic Remediation

When the orchestrator detects an error, it **automatically creates a RemediationTask** and dispatches the right agent:

#### Scout Agent (🔍 Missing Data)

Triggered when:

- Product image URL is missing
- Price data incomplete
- Manufacturer specs not found

Example flow:

```
Error Detected: Missing image for "Juno-X"
    ↓
Orchestrator creates: RemediationTask(MISSING_IMAGE, severity=3)
    ↓
Scout Agent dispatches:
  - Search Halilit.com for product
  - Extract image URL
  - Update JSON file (via DAL validation)
    ↓
✅ Automatic fix applied
```

#### Dev Agent (👨‍💻 Code Issues)

Triggered when:

- TypeScript build errors
- Missing React imports
- Type mismatches

Example flow:

```
Error Detected: "Line 42: 'onClick' prop missing type annotation"
    ↓
Orchestrator creates: RemediationTask(TYPE_MISMATCH, severity=2)
    ↓
Dev Agent dispatches:
  - Parse error log
  - Generate type annotations
  - Submit auto-fix to file
    ↓
✅ Automatic code correction
```

#### Maintenance Agent (🔧 System Health)

Triggered when:

- Data file corruption detected
- Index rebuild failures
- Schema violations

Example flow:

```
Error Detected: "galaxy_db.json size: 0 bytes"
    ↓
Orchestrator creates: RemediationTask(DATA_CORRUPTION, severity=1)
    ↓
Maintenance Agent dispatches:
  - Check backup files
  - Validate source JSON
  - Rebuild database
    ↓
✅ System restored
```

### Using Autonomic Remediation

In your code, create tasks manually:

```python
from backend.conductor_orchestrator import ConductorOrchestrator, RemediationType

orch = ConductorOrchestrator()
orch.start()

# Create a remediation task
task_id = orch._create_remediation_task(
    remediation_type=RemediationType.MISSING_IMAGE,
    severity=3,
    description="Product image not found",
    affected_file="backend/data/brands/roland.json",
    error_context="Field 'image_url' is None"
)

# The orchestrator's remediation loop will automatically dispatch the Scout Agent
# Watch the logs for "[Scout Agent dispatched...]"
```

**Key Files:**

- [backend/conductor_orchestrator.py](backend/conductor_orchestrator.py#L197-L281) - Remediation dispatch logic

---

## 🎯 Dimension 3: Data Access Layer (Data Governance)

### Instead of Manual JSON Editing...

❌ **Bad (manual + risky):**

```bash
# Edit file manually - risks schema corruption
nano backend/data/brands/roland.json
```

✅ **Good (validated + safe):**

```python
from backend.conductor_orchestrator import ConductorOrchestrator

orch = ConductorOrchestrator()

# Add product with automatic schema validation
success, msg = orch._dal_add_product(
    brand="Roland",
    name="Juno-X",
    price_il=4999.0,
    price_eilat=4799.0,
    image_url="https://..."
)

# ✓ ProductDraft schema automatically validated
# ✓ File written only if valid
# ✓ JSON formatted correctly
# ✓ Library auto-rebuilds on save
```

### DAL Command Reference

#### 1. Add Product

```python
success, msg = orch._dal_add_product(
    brand="Moog",
    name="Minimoog V3",
    price_il=2499.0,
    price_eilat=2299.0,
    image_url="https://...",
    source_url="https://..."
)
```

#### 2. Validate Schema

```python
success, msg = orch._dal_validate_schema(
    "backend/data/brands/korg.json"
)
# Returns: (True/False, error_message)
```

#### 3. List All Products

```python
success, products = orch._dal_list_products()
# Returns: (True, ["Juno-X", "TR-808", ...])
```

#### 4. Export Search Index

```python
success, path = orch._dal_export_index()
# Returns: (True, "frontend/public/data/product_index.json")
```

### Schema Validation (Automatic)

The DAL uses Pydantic's `ProductDraft` model:

```python
class ProductDraft(BaseModel):
    id: str                              # Auto-generated: brand_name
    name: str                            # Product name ✓ Required
    brand: str                           # Brand name ✓ Required
    price_il: float                      # Israeli price ✓ Required
    price_eilat: float                   # Eilat price ✓ Required
    image_url: Optional[str] = None      # Can be missing (Scout will find it)
    source_url: Optional[str] = None
    official_match: Optional[bool] = False
```

If you try to add an invalid product:

```python
# ❌ Missing required field
orch._dal_add_product(brand="Roland", name="Juno-X")
# Error: "price_il" is required

# ❌ Wrong type
orch._dal_add_product(brand="Roland", name="Juno-X", price_il="not_a_number")
# Error: value is not a valid float
```

**Key Files:**

- [backend/conductor_orchestrator.py](backend/conductor_orchestrator.py#L266-L364) - DAL methods
- [backend/agents/trinity_swarm.py](backend/agents/trinity_swarm.py#L13-L22) - ProductDraft model

---

## 🎯 Dimension 4: Deployment Gatekeeper (Git Hook)

### What It Does

Before **any commit**, the git hook runs:

```bash
python3 backend/conductor_verify_spectrum_v540.py
```

If the Conductor returns:

- ✅ **GREEN** → Commit allowed
- 🔴 **RED** → Commit blocked

### Installation

The orchestrator auto-installs this hook:

```bash
python3 run_conductor_orchestrator.py
# Output: "✅ Git hook installed at: .git/hooks/pre-commit"
```

### Testing the Hook

```bash
cd /workspaces/Halilit-Support-Center

# Intentionally create a "bad" file
echo "incomplete code" > frontend/src/Bad.tsx

# Try to commit
git add frontend/src/Bad.tsx
git commit -m "test: add bad code"

# Output:
# 🚨 Conductor: Verifying codebase before commit...
# ❌ Conductor rejected commit: Code not production-ready
# Fix issues and try again.
```

The commit is **BLOCKED** ✋

Now fix it:

```bash
# Either delete the file or make it valid
rm frontend/src/Bad.tsx

# Try again
git commit -m "cleanup: remove test file"
# Output:
# ✅ Conductor approved: Ready to commit
# [main abc1234] cleanup: remove test file
```

The commit **SUCCEEDS** ✅

### Hook Configuration

The hook is installed at: [.git/hooks/pre-commit](.git/hooks/pre-commit)

To disable temporarily:

```bash
chmod -x .git/hooks/pre-commit  # Disable
chmod +x .git/hooks/pre-commit  # Re-enable
```

---

## 📊 Monitoring & Status

### Check Orchestrator Status

```bash
# Terminal 1 (where orchestrator is running)
# Type: status
conductor🚀> status

═══ Conductor Orchestrator Status ═══
  Running: True
  Data Watcher: 🟢 Active
  Remediation Tasks: 5
  Pending Remediations: 2

  Recent tasks:
    ⏳ rem_0001: missing_image
    📋 rem_0002: import_error
    ✅ rem_0003: data_corruption
```

### View Logs

```bash
# Real-time logs
tail -f conductor_orchestrator.log

# All events
grep "dispatched" conductor_orchestrator.log

# Errors only
grep "ERROR\|failed" conductor_orchestrator.log
```

---

## 🔧 Advanced Configuration

### Watch Additional Paths

Edit [backend/conductor_orchestrator.py](backend/conductor_orchestrator.py#L123-L127):

```python
self.watched_paths = [
    Path(__file__).parent,  # backend/
    Path(__file__).parent.parent / "frontend" / "src",
    Path(__file__).parent / "custom_path",  # Add new path
]
```

### Add New Remediation Types

1. Add to `RemediationType` enum:

```python
class RemediationType(Enum):
    CUSTOM_ISSUE = "custom_issue"
```

2. Add handler in `_dispatch_remediation()`:

```python
elif task.remediation_type == RemediationType.CUSTOM_ISSUE:
    self._dispatch_custom_handler(task)
```

### Create Custom DAL Commands

```python
def _dal_custom_command(self, param: str) -> Tuple[bool, str]:
    """Your custom DAL command"""
    logger.info(f"Custom command: {param}")
    return True, "Done"

# Register in create_dal_cli()
dal_commands = {
    'custom-command': self._dal_custom_command,
    ...
}
```

---

## 📚 Integration Examples

### Example 1: Auto-Fix Imports on TypeScript Error

```python
# frontend/src/MyComponent.tsx has TypeScript error
# Dev Agent automatically:
# 1. Reads error from build log
# 2. Parses missing import
# 3. Injects: import { Component } from './path'
# 4. Saves file
# ✅ File watcher detects change
# ✅ Standards check passes
```

### Example 2: Auto-Enrich Product Data

```python
# backend/data/brands/roland.json updated with new product
# Orchestrator detects change
#   ↓
# rebuild_library() runs automatically
#   ↓
# Frontend's galaxy_db.json is updated
#   ↓
# Frontend detects new product in search index
# ✅ User immediately sees new product
```

### Example 3: Prevent Broken Commits

```bash
# Developer attempts bad commit
git commit -m "add broken product data"

# Pre-commit hook fires
#   ↓
# conductor_verify_spectrum_v540.py runs
#   ↓
# Detects schema violation in JSON
#   ↓
# ❌ Commit rejected
# Developer must fix before trying again
```

---

## 🚨 Troubleshooting

### Watcher Not Detecting Changes

```bash
# Check watchdog is installed
pip list | grep watchdog
# Should show: watchdog 4.0.0+

# Manually check paths exist
ls -la backend/data/brands/
ls -la frontend/src/

# Restart orchestrator
python3 run_conductor_orchestrator.py
```

### Remediation Tasks Not Processing

```bash
# Check logs
tail -f conductor_orchestrator.log | grep "remediation"

# Check queue
# In terminal: conductor🚀> status
# Look for "Pending Remediations"

# Trinity Swarm agents might be offline
# Check: backend/agents/trinity_swarm.py for errors
```

### Git Hook Not Running

```bash
# Check hook exists and is executable
ls -la .git/hooks/pre-commit

# If missing, reinstall:
python3 run_conductor_orchestrator.py  # Auto-installs hook

# If not executable:
chmod +x .git/hooks/pre-commit

# Test hook manually:
bash .git/hooks/pre-commit
```

---

## 📋 Summary: Before vs After

### Before (Conductor as Inspector)

| Task                | How It Worked                  |
| ------------------- | ------------------------------ |
| Add product         | Manual: edit JSON file         |
| Detect data changes | Manual: run rebuild_library.py |
| Fix import errors   | Manual: read error, edit file  |
| Block bad commits   | Nothing (breaks happen)        |

### After (Conductor as Manager)

| Task                | How It Works Now                               |
| ------------------- | ---------------------------------------------- |
| Add product         | CLI: `conductor add-product` + auto-validation |
| Detect data changes | Auto-watcher + auto-rebuild in real-time       |
| Fix import errors   | Auto-dispatch Dev Agent for auto-fix           |
| Block bad commits   | Auto-gate with pre-commit hook                 |

---

## 📖 Key Files Reference

| File                                                                   | Purpose                    |
| ---------------------------------------------------------------------- | -------------------------- |
| [backend/conductor_orchestrator.py](backend/conductor_orchestrator.py) | Main orchestrator logic    |
| [run_conductor_orchestrator.py](run_conductor_orchestrator.py)         | Entry point (run this!)    |
| [backend/conductor_daemon.py](backend/conductor_daemon.py)             | Base daemon infrastructure |
| [backend/conductor_spectrum.py](backend/conductor_spectrum.py)         | Spectrum data verification |
| [backend/rebuild_library.py](backend/rebuild_library.py)               | Library rebuild logic      |
| [backend/agents/trinity_swarm.py](backend/agents/trinity_swarm.py)     | Agent implementations      |

---

## 🎉 You've Maximized the Conductor!

Your system is now:

- ✅ **Alive** - Running 24/7 as a daemon
- ✅ **Aware** - Watching for changes in real-time
- ✅ **Autonomous** - Fixing issues automatically
- ✅ **Accountable** - Gating deployments with verification
- ✅ **Accountable** - Managing all data changes through validated API

**Next Steps:**

1. Start the orchestrator: `python3 run_conductor_orchestrator.py`
2. Test it: Add a product via DAL
3. Monitor it: Check logs for autonomous actions
4. Deploy with confidence: Git hook blocks bad code

🚀 **Your Trinity Swarm now has a boss. The Conductor is in control.**
