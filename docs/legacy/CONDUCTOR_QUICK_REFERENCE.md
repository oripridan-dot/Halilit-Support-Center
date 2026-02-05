# Conductor Orchestrator - Quick Reference (v6.0)

## 🚀 Start the System (1 Command)

```bash
python3 run_conductor_orchestrator.py
```

That's it. Everything else happens automatically.

---

## 📊 What's Running Now?

```
✅ Data Watcher        → backend/data/brands/** auto-rebuilds on change
✅ Code Watcher        → frontend/src/** enforces standards
✅ Error Detector      → Watches for failures
✅ Trinity Swarm       → Ready to auto-fix issues
✅ Git Hook            → Blocks bad commits
```

---

## 💾 Add a Product (Safe Way)

```python
from backend.conductor_orchestrator import ConductorOrchestrator

orch = ConductorOrchestrator()

# This validates schema automatically
success, msg = orch._dal_add_product(
    brand="Moog",
    name="Minimoog V3",
    price_il=2499,
    price_eilat=2299
)

if success:
    print("✅ Product added & library auto-rebuilt")
else:
    print(f"❌ Error: {msg}")
```

---

## 🔍 Check System Health

```bash
# While orchestrator is running, type:
conductor🚀> status

# Output shows:
# - Remediation tasks
# - Pending fixes
# - Active watchers
```

---

## 🛑 How the Git Hook Works

```bash
# Try to commit bad code
git add .
git commit -m "test"

# Hook automatically runs conductor verification
# If bad → ❌ Commit BLOCKED
# If good → ✅ Commit ALLOWED
```

---

## 🎯 Remediation (Auto-fixes)

These happen automatically when errors are detected:

| Error Type       | Agent       | Action                            |
| ---------------- | ----------- | --------------------------------- |
| Missing image    | Scout       | Searches for URL, updates JSON    |
| Import error     | Dev         | Adds missing imports, fixes types |
| Schema violation | Dev         | Corrects JSON structure           |
| Data corruption  | Maintenance | Validates & rebuilds              |

---

## 📝 Available DAL Commands

```python
# List products
success, products = orch._dal_list_products()

# Validate JSON file
success, msg = orch._dal_validate_schema("file.json")

# Export search index
success, path = orch._dal_export_index()
```

---

## 🚨 Troubleshooting

### "Watcher not detecting changes"

```bash
# Restart orchestrator
# Kill: Ctrl+C
# Start: python3 run_conductor_orchestrator.py
```

### "Git hook not running"

```bash
# Reinstall hook:
python3 run_conductor_orchestrator.py
# Look for: "✅ Git hook installed"
```

### "Remediation tasks stuck"

```bash
# Check logs
tail -f conductor_orchestrator.log

# Restart orchestrator
python3 run_conductor_orchestrator.py
```

---

## 📚 Learn More

Read the full guide: [CONDUCTOR_ORCHESTRATOR_GUIDE.md](CONDUCTOR_ORCHESTRATOR_GUIDE.md)

---

## 🎉 Summary

| Feature            | Before             | After                       |
| ------------------ | ------------------ | --------------------------- |
| **Add product**    | Manual edit JSON   | CLI command, auto-validated |
| **Rebuild search** | Manual run command | Auto-trigger on data change |
| **Fix errors**     | Manual debugging   | Auto-dispatch agents        |
| **Deploy safely**  | Hope for best      | Git hook blocks bad code    |

**Your Conductor is now a 24/7 autonomous manager.** 🚀
