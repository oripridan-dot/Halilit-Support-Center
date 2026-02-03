# Quick Start: Using the Integrated System

## 🚀 Start the Server

```bash
cd /workspaces/Halilit-Support-Center
python3 backend/server.py
```

Expected output:

```
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
...
Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 📡 Available Endpoints

### **Health & Status**

```bash
# Check system health
curl -X POST http://localhost:8000/api/maintenance/health-check

# Get orchestrator status
curl -X GET http://localhost:8000/api/maintenance/orchestrator-status
```

### **Code Maintenance (Individual Operations)**

```bash
# Cleanup code (remove dead code, unused imports)
curl -X POST http://localhost:8000/api/maintenance/code-cleanup

# Organize code (enforce naming, structure)
curl -X POST http://localhost:8000/api/maintenance/organize-code

# Synchronize code (sync imports, exports)
curl -X POST http://localhost:8000/api/maintenance/sync-code
```

### **Full Automation (5-Phase Cycle)**

```bash
# Run complete maintenance cycle
curl -X POST http://localhost:8000/api/maintenance/full-cycle
```

Response includes:

- Phase 1: Initial Health Check
- Phase 2: Code Cleanup
- Phase 3: Code Organization
- Phase 4: Code Sync
- Phase 5: Final Health Check

### **Reporting**

```bash
# Generate comprehensive maintenance report
curl -X POST http://localhost:8000/api/maintenance/report
```

---

## 🐍 Python Usage

### **In Your Code**

```python
from backend import SystemHealthCheckWorkflow, CodeCleanupWorkflow
from backend.agents.maintenance_orchestrator import AgentMaintenanceOrchestrator

# Initialize orchestrator
orchestrator = AgentMaintenanceOrchestrator()

# Option 1: Run individual workflows
health_workflow = SystemHealthCheckWorkflow()
success, result = health_workflow.execute({})
print(f"Health Score: {result['health_score']}")

# Option 2: Run full cycle
cleanup_workflow = CodeCleanupWorkflow()
success, cleanup_result = cleanup_workflow.execute({})
print(f"Files Formatted: {cleanup_result['files_formatted']}")

# Option 3: Use orchestrator directly
report = orchestrator.run_full_maintenance()
```

### **In FastAPI Route**

```python
from fastapi import FastAPI
from backend import CodeCleanupWorkflow

app = FastAPI()

@app.post("/my-cleanup")
async def my_cleanup():
    workflow = CodeCleanupWorkflow()
    success, result = workflow.execute({})
    return {"success": success, "details": result}
```

---

## 📊 Expected Results

### **Health Check Response**

```json
{
  "success": true,
  "health_score": 95.0,
  "health_status": "HEALTHY",
  "details": {
    "files_scanned": 16,
    "valid_files": 16,
    "invalid_files": 0
  }
}
```

### **Code Cleanup Response**

```json
{
  "success": true,
  "files_scanned": 10,
  "issues_found": 0,
  "files_formatted": 10,
  "validation_score": 100
}
```

### **Full Cycle Response**

```json
{
  "phase_1_health_check": {
    "success": true,
    "health_score": 100.0,
    "status": "HEALTHY"
  },
  "phase_2_cleanup": {
    "success": true,
    "files_formatted": 10,
    "validation_score": 100
  },
  "phase_3_organization": {
    "success": true,
    "files_fixed": 10,
    "organization_score": 100.0
  },
  "phase_4_sync": {
    "success": true,
    "files_synced": 5,
    "sync_score": 90.0
  },
  "phase_5_final_health": {
    "success": true,
    "health_score": 95.0,
    "status": "HEALTHY"
  },
  "maintenance_report": {
    "total_phases": 5,
    "phases_completed": 5,
    "status": "COMPLETE",
    "message": "System is now healthy and synchronized"
  }
}
```

---

## 🧪 Testing the Integration

### **Test 1: Verify Server Starts**

```bash
python3 -c "from backend.server import app; print(f'✅ {len(app.routes)} endpoints available')"
```

Expected: `✅ 34 endpoints available`

### **Test 2: Run Health Check**

```bash
curl -s -X POST http://localhost:8000/api/maintenance/health-check | python3 -m json.tool
```

Expected: `"success": true` and health score

### **Test 3: Run Full Cycle**

```bash
curl -s -X POST http://localhost:8000/api/maintenance/full-cycle | python3 -m json.tool
```

Expected: All 5 phases complete successfully

---

## 🎯 Common Tasks

### **Monitor System Health (Every Hour)**

```bash
#!/bin/bash
# health_monitor.sh

while true; do
  echo "[$(date)] Running health check..."
  curl -s -X POST http://localhost:8000/api/maintenance/health-check | jq '.health_score'
  echo "Next check in 1 hour..."
  sleep 3600
done
```

### **Run Daily Maintenance**

```bash
#!/bin/bash
# daily_maintenance.sh

echo "Starting daily maintenance cycle..."
curl -X POST http://localhost:8000/api/maintenance/full-cycle | jq '.maintenance_report'
echo "Daily maintenance complete!"
```

### **Check Code Organization**

```python
from backend import CodeOrganizationWorkflow

workflow = CodeOrganizationWorkflow()
success, result = workflow.execute({})

if result['organization_score'] >= 90:
    print("✅ Code is well organized")
else:
    print(f"⚠️ Organization score: {result['organization_score']}%")
    print(f"Files to fix: {result['files_fixed']}")
```

---

## 📚 Integrated Components

### **Agents**

- `TrinitySwarm`: CommercialScout, OfficialVerifier, ExternalValidator
- `DevAgent`: Autonomous code maintenance
- `AgentMaintenanceOrchestrator`: Central coordination

### **Skills** (19 Total)

- 12 Trinity Swarm skills for data processing
- 7 DevAgent skills for code maintenance

### **Workflows** (8 Total)

- 4 Trinity Swarm workflows
- 4 DevAgent maintenance workflows

### **APIs** (34 Endpoints)

- 26 existing endpoints
- 8 new maintenance endpoints

---

## 🔧 Troubleshooting

### **"ImportError: cannot import from backend"**

```bash
# Solution: Set PYTHONPATH
export PYTHONPATH=/workspaces/Halilit-Support-Center:$PYTHONPATH
python3 backend/server.py
```

### **"No API endpoint found"**

```bash
# Verify server is running
curl http://localhost:8000/health

# Check available endpoints
curl http://localhost:8000/openapi.json | jq '.paths | keys'
```

### **"Health check returns 0%"**

This is normal - initial scan may find optimization opportunities. Run cleanup:

```bash
curl -X POST http://localhost:8000/api/maintenance/code-cleanup
```

---

## 📖 Full Documentation

- **INTEGRATION_COMPLETE.md** - Complete integration details
- **DEVAGENT_ENHANCEMENT.md** - DevAgent capabilities
- **TRINITY_SWARM_COMPLETE.md** - Trinity Swarm architecture
- **SYSTEM_READINESS.md** - Deployment info
- **RELEASE_NOTES_v5.1.md** - Version details

---

## ✅ You're All Set!

The Trinity Swarm + DevAgent system is fully integrated and ready to use:

✅ Server starts easily with `python3 backend/server.py`
✅ 8 new maintenance endpoints available
✅ Full automation with 5-phase cycle
✅ Complete health monitoring
✅ Production-ready code

**Start now**:

```bash
cd /workspaces/Halilit-Support-Center
python3 backend/server.py
```

Then in another terminal:

```bash
curl -X POST http://localhost:8000/api/maintenance/full-cycle
```

Enjoy! 🎉
