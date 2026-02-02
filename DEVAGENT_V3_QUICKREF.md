# DevAgent v3.0 Quick Reference

## 🎯 One-Line Summary

**DevAgent v3.0 = Error Fixer + Context Manager + Proactive Developer**

---

## 📂 Directory Structure

```
.devagent/
├── history.jsonl              # Complete development history
├── context.json              # Current project state
└── consistency_rules.json    # Project-specific rules
```

---

## 🚀 Quick Commands

### Test Context Manager

```bash
python3 backend/agents/context_manager.py
```

### View Context Summary

```bash
curl http://localhost:8000/api/context/summary
```

### Check Recent History

```bash
curl http://localhost:8000/api/context/history?limit=10
```

### Analyze Consistency

```bash
curl -X POST http://localhost:8000/api/context/analyze
```

### Get Refactoring Suggestions

```bash
curl -X POST http://localhost:8000/api/context/suggest-refactoring \
  -H "Content-Type: application/json" \
  -d '{"file_path": "backend/agents/dev_agent.py"}'
```

---

## 💻 Python API

### Log Context Entry

```python
from backend.agents.context_manager import ContextManager

context = ContextManager()

# Log a decision
context.log_entry(
    "decision",
    "Switched to FastAPI for better async support",
    files_affected=["backend/server.py"],
    tags=["architecture", "backend"]
)
```

### Analyze Context

```python
analysis = context.analyze_context()
print(f"Consistency Score: {analysis.consistency_score}%")
print(f"Patterns: {', '.join(analysis.patterns_detected)}")
print(f"Issues: {', '.join(analysis.inconsistencies)}")
```

### Check Consistency

```python
result = context.check_consistency(
    "Add new authentication endpoint",
    files=["backend/server.py", "frontend/src/Login.tsx"]
)

if result["recommendation"] == "approve":
    print("✅ Change is consistent")
else:
    print(f"⚠️ Issues: {result['violations']}")
```

### Suggest Refactoring

```python
plans = context.suggest_refactoring("backend/agents/dev_agent.py")
for plan in plans:
    if plan.priority == "high":
        print(f"🔧 {plan.description}")
        print(f"   Reasoning: {plan.reasoning}")
```

### Update Documentation

```python
doc_updates = context.update_documentation(
    "Added new validation method",
    files_affected=["backend/agents/dev_agent.py"]
)
# Returns which docs to update and how
```

---

## 🔌 API Endpoints

| Endpoint                           | Method | Purpose                       |
| ---------------------------------- | ------ | ----------------------------- |
| `/api/context/summary`             | GET    | Get formatted context summary |
| `/api/context/history`             | GET    | Get recent history entries    |
| `/api/context/analyze`             | POST   | Analyze consistency           |
| `/api/context/check-consistency`   | POST   | Validate proposed change      |
| `/api/context/suggest-refactoring` | POST   | Get refactoring suggestions   |
| `/api/context/log`                 | POST   | Log context entry             |

---

## 📊 Context Entry Types

| Type            | Purpose              | Example                    |
| --------------- | -------------------- | -------------------------- |
| `prompt`        | User requests        | "Add error handling"       |
| `response`      | Agent responses      | "Added try-catch block"    |
| `fix`           | Bug fixes            | "Fixed null pointer"       |
| `refactor`      | Code improvements    | "Extracted method"         |
| `decision`      | Architecture choices | "Use FastAPI over Flask"   |
| `error`         | Caught errors        | "TypeError in component X" |
| `documentation` | Doc updates          | "Updated README"           |

---

## 🎨 DevAgent Integration

DevAgent **automatically logs context** for every operation:

### Error Analysis

```python
# Automatic logging:
# 1. Log error detection
# 2. Log fix suggestion
# 3. Log fix application (if auto-applied)
# 4. Check if docs need updating
```

### Complete Workflow

```
Error Detected
    ↓ (logs "error")
AI Analyzes
    ↓ (logs "fix")
Validates Fix
    ↓ (logs "validation")
Applies Fix
    ↓ (logs "fix-applied")
Updates Docs
    ↓ (logs "documentation")
Context Updated ✓
```

---

## 🧪 Testing Checklist

- [ ] Context manager creates `.devagent/` directory
- [ ] History entries logged correctly
- [ ] Context analysis returns consistency score
- [ ] Refactoring suggestions generated
- [ ] Documentation updates suggested
- [ ] Consistency check validates changes

---

## 📈 Metrics to Track

```python
# Get development metrics
history = context.get_recent_history(100)

# Error count
errors = [h for h in history if h.type == "error"]
print(f"Errors: {len(errors)}")

# Fix success rate
fixes = [h for h in history if h.type == "fix-applied"]
success_rate = len(fixes) / len(errors) * 100 if errors else 100
print(f"Fix Rate: {success_rate}%")

# Consistency trend
analysis = context.analyze_context()
print(f"Consistency: {analysis.consistency_score}%")
```

---

## 🔐 Configuration

### Edit Consistency Rules

```bash
nano .devagent/consistency_rules.json
```

```json
{
  "naming": "camelCase for TS, snake_case for Python",
  "imports": "Absolute for cross-module",
  "testing": "Test new features before committing",
  "documentation": "Update docs immediately",
  "errors": "All errors captured by DevAgent"
}
```

### Context Retention Settings

```python
# In context_manager.py
MAX_HISTORY_ENTRIES = 10000  # Keep last 10k
AUTO_ARCHIVE_DAYS = 90       # Archive after 90 days
```

---

## 🚦 Status Indicators

### Consistency Scores

- **90-100**: Excellent consistency ✅
- **75-89**: Good, minor issues ⚠️
- **60-74**: Needs attention 🔶
- **< 60**: Critical inconsistencies ❌

### Recommendation Actions

- **approve**: Change is consistent ✅
- **review**: Manual review needed ⚠️
- **reject**: Violates project rules ❌

### Refactoring Priority

- **high**: Critical, do ASAP 🔴
- **medium**: Important, schedule 🟡
- **low**: Nice to have 🟢

---

## 💡 Best Practices

### 1. Log Important Decisions

```python
context.log_entry(
    "decision",
    "Why we made this choice",
    tags=["architecture"],
    metadata={"alternatives_considered": ["Option A", "Option B"]}
)
```

### 2. Run Consistency Checks Before Commits

```python
# Pre-commit hook
result = context.check_consistency(commit_message, changed_files)
if result["recommendation"] != "approve":
    print("⚠️ Consistency issues detected")
    exit(1)
```

### 3. Weekly Refactoring Review

```python
# Every Monday
plans = context.suggest_refactoring()
high_priority = [p for p in plans if p.priority == "high"]
# Create GitHub issues for high-priority items
```

### 4. Track Context Summary

```bash
# Add to daily standup
curl http://localhost:8000/api/context/summary
```

---

## 🔄 Migration from v2.0

DevAgent v3.0 is **backward compatible**:

- All v2.0 features (auto-fix, validation) still work
- Context logging happens automatically
- No code changes needed in existing files
- Just start using context API endpoints

**New in v3.0**:

- Context tracking (automatic)
- Consistency analysis (API endpoint)
- Refactoring suggestions (API endpoint)
- Auto-documentation (automatic)
- Pre-commit validation (API endpoint)

---

## 🆘 Troubleshooting

### Context Not Logging

```python
# Check if context manager initialized
print(dev_agent.context_manager.context_file)
# Should print: /workspaces/Halilit-Support-Center/.devagent/context.json
```

### Consistency Score Always 0

```python
# Re-analyze context
analysis = context.analyze_context()
# Check for API errors in response
```

### History File Too Large

```bash
# Archive old entries
cd .devagent
tail -n 1000 history.jsonl > history_recent.jsonl
mv history.jsonl history_archive_$(date +%Y%m%d).jsonl
mv history_recent.jsonl history.jsonl
```

---

## 📚 See Also

- [DEVAGENT_V3_CONTEXT.md](./DEVAGENT_V3_CONTEXT.md) - Full v3.0 documentation
- [DEVAGENT_V2.md](./DEVAGENT_V2.md) - v2.0 auto-fix features
- [ADK_ARCHITECTURE.md](./ADK_ARCHITECTURE.md) - System architecture
- [README.md](./README.md) - Project overview

---

**Quick Start**: Run `python3 backend/agents/context_manager.py` to test!

**v3.0 is LIVE** - Context tracking starts automatically when DevAgent initializes. 🎯✨
