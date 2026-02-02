# DevAgent v3.0 - Getting Started

## 🚀 Instant Start (3 Steps)

### 1. Start Backend Server

```bash
cd /workspaces/Halilit-Support-Center
PYTHONPATH=. python3 backend/server.py
```

**DevAgent v3.0 starts automatically** and begins tracking context immediately!

### 2. Verify Context Tracking

```bash
# Check context directory exists
ls -la .devagent/

# Expected output:
# context.json              # Project state
# history.jsonl            # Development history
```

### 3. Test Context API

```bash
# Get context summary
curl http://localhost:8000/api/context/summary

# Get recent history
curl http://localhost:8000/api/context/history?limit=5

# Analyze consistency
curl -X POST http://localhost:8000/api/context/analyze
```

---

## 🎯 What's Happening Automatically

### When DevAgent Starts

✅ Creates `.devagent/` directory  
✅ Initializes `context.json` with project rules  
✅ Sets up `history.jsonl` for event logging  
✅ Integrates with all DevAgent operations

### During Development

**Every action is logged:**

```python
# Error detected → logs "error"
# Fix suggested → logs "fix"
# Fix validated → logs "validation"
# Fix applied → logs "fix-applied"
# Docs updated → logs "documentation"
```

**No manual intervention needed!**

---

## 📊 View Your Context

### Command Line

```bash
# Pretty print context
cat .devagent/context.json | python3 -m json.tool

# View last 10 history entries
tail -10 .devagent/history.jsonl | python3 -m json.tool
```

### API Endpoints

```bash
# Context summary (formatted)
curl http://localhost:8000/api/context/summary

# Output:
# ╔═══════════════════════════════════════╗
# ║   DEVELOPMENT CONTEXT SUMMARY         ║
# ╚═══════════════════════════════════════╝
#
# Project: Halilit Support Center
# Version: 5.1.0-v2
# Total Entries: 42
# Consistency Score: 90%
```

---

## 🔍 Common Operations

### 1. Check Consistency Before Committing

```bash
curl -X POST http://localhost:8000/api/context/check-consistency \
  -H "Content-Type: application/json" \
  -d '{
    "proposed_change": "Add new authentication endpoint",
    "files": ["backend/server.py"]
  }'
```

**Response:**

```json
{
  "is_consistent": true,
  "consistency_score": 95,
  "violations": [],
  "recommendation": "approve",
  "reasoning": "Follows established FastAPI patterns"
}
```

### 2. Get Refactoring Suggestions

```bash
curl -X POST http://localhost:8000/api/context/suggest-refactoring \
  -H "Content-Type: application/json" \
  -d '{"file_path": "backend/agents/dev_agent.py"}'
```

**Response:**

```json
{
  "refactoring_plans": [
    {
      "priority": "medium",
      "type": "consistency",
      "description": "Extract validation logic into separate method",
      "affected_files": ["backend/agents/dev_agent.py"],
      "reasoning": "DRY principle - validation logic repeated 3 times"
    }
  ]
}
```

### 3. Analyze Development Patterns

```bash
curl -X POST http://localhost:8000/api/context/analyze
```

**Response:**

```json
{
  "consistency_score": 90,
  "patterns_detected": [
    "React 18 + TypeScript",
    "Python + FastAPI",
    "Pydantic v2 models"
  ],
  "inconsistencies": ["Mixed naming convention in module X"],
  "suggestions": ["Standardize naming across codebase"],
  "related_context": ["Previous decision: Use snake_case for Python"]
}
```

### 4. Log Important Decisions

```bash
curl -X POST http://localhost:8000/api/context/log \
  -H "Content-Type: application/json" \
  -d '{
    "type": "decision",
    "content": "Switched from REST to WebSockets for real-time features",
    "files_affected": ["backend/server.py", "frontend/src/api/socket.ts"],
    "tags": ["architecture", "real-time"],
    "metadata": {
      "reasoning": "Better performance for live updates",
      "alternatives_considered": ["Polling", "Server-Sent Events"]
    }
  }'
```

---

## 📝 Context File Structure

### `.devagent/context.json`

```json
{
  "project_name": "Halilit Support Center",
  "version": "5.1.0-v2",
  "last_updated": "2026-02-02T21:10:37",
  "total_entries": 42,
  "active_patterns": ["React 18 + TypeScript", "Python + FastAPI"],
  "recent_decisions": [
    {
      "id": "1770066637267",
      "timestamp": "2026-02-02T21:10:37",
      "content": "Use Gemini 2.0 Flash for all agents"
    }
  ],
  "file_history": {
    "backend/agents/dev_agent.py": ["id1", "id2", "id3"]
  },
  "consistency_rules": {
    "naming": "camelCase for TS, snake_case for Python",
    "imports": "Absolute for cross-module",
    "testing": "Test before committing"
  }
}
```

### `.devagent/history.jsonl` (JSONL format)

```json
{"id": "1770066637266", "timestamp": "2026-02-02T21:10:37", "type": "prompt", "content": "Add context management", "files_affected": ["backend/agents/context_manager.py"], "tags": ["feature"], "metadata": {}}
{"id": "1770066637267", "timestamp": "2026-02-02T21:10:38", "type": "response", "content": "Created ContextManager", "files_affected": ["backend/agents/context_manager.py"], "tags": ["implementation"], "metadata": {}}
```

---

## 🛠️ Customization

### Edit Consistency Rules

```bash
nano .devagent/context.json
```

Find `"consistency_rules"` and modify:

```json
{
  "consistency_rules": {
    "naming": "Your naming convention",
    "imports": "Your import style",
    "testing": "Your testing requirements",
    "documentation": "Your doc standards",
    "custom_rule": "Your custom requirement"
  }
}
```

**DevAgent will enforce these rules automatically!**

---

## 📈 Monitoring Development Health

### Daily Check Script

```bash
#!/bin/bash
# daily_health_check.sh

echo "📊 Development Health Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get context summary
curl -s http://localhost:8000/api/context/summary

# Analyze consistency
ANALYSIS=$(curl -s -X POST http://localhost:8000/api/context/analyze)
SCORE=$(echo $ANALYSIS | jq -r '.consistency_score')

echo ""
echo "Consistency Score: $SCORE%"

if [ "$SCORE" -lt 80 ]; then
    echo "⚠️ Consistency below 80% - Review needed"
fi

# Get high-priority refactorings
REFACTORINGS=$(curl -s -X POST http://localhost:8000/api/context/suggest-refactoring)
HIGH_PRIORITY=$(echo $REFACTORINGS | jq '[.refactoring_plans[] | select(.priority == "high")] | length')

echo "High-priority refactorings: $HIGH_PRIORITY"
```

---

## 🎓 Learning from Context

### View Development Patterns

```python
from backend.agents.context_manager import ContextManager

context = ContextManager()
history = context.get_recent_history(100)

# Find common error patterns
errors = [h for h in history if h.type == "error"]
error_types = {}
for error in errors:
    error_type = error.metadata.get("error_type", "unknown")
    error_types[error_type] = error_types.get(error_type, 0) + 1

print("Most common errors:")
for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  {error_type}: {count} occurrences")
```

### Track Development Velocity

```python
# Count fixes per day
from collections import defaultdict
from datetime import datetime

fixes_by_day = defaultdict(int)
for entry in history:
    if entry.type == "fix-applied":
        day = datetime.fromisoformat(entry.timestamp).date()
        fixes_by_day[day] += 1

print("Fixes per day:")
for day, count in sorted(fixes_by_day.items()):
    print(f"  {day}: {count} fixes")
```

---

## 🚦 Integration with CI/CD

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check consistency before allowing commit
RESULT=$(curl -s -X POST http://localhost:8000/api/context/check-consistency \
  -H "Content-Type: application/json" \
  -d "{
    \"proposed_change\": \"$(git log -1 --pretty=%B)\",
    \"files\": [\"$(git diff --cached --name-only | tr '\n' ',' | sed 's/,$//')\"]
  }")

RECOMMENDATION=$(echo $RESULT | jq -r '.recommendation')

if [ "$RECOMMENDATION" == "reject" ]; then
    echo "❌ Commit rejected: Consistency violations detected"
    echo $RESULT | jq -r '.violations[]'
    exit 1
fi

if [ "$RECOMMENDATION" == "review" ]; then
    echo "⚠️ Warning: Manual review recommended"
    echo $RESULT | jq -r '.reasoning'
    read -p "Continue anyway? (y/N): " confirm
    if [ "$confirm" != "y" ]; then
        exit 1
    fi
fi

echo "✅ Consistency check passed"
```

---

## 🆘 Troubleshooting

### DevAgent Not Logging Context

**Check 1:** Is `.devagent/` directory created?

```bash
ls -la .devagent/
```

**Check 2:** Is DevAgent initialized?

```python
from backend.agents.dev_agent import DevAgent
agent = DevAgent()
print(hasattr(agent, 'context_manager'))  # Should be True
```

**Check 3:** Are permissions correct?

```bash
chmod -R u+rw .devagent/
```

### Context File Corrupted

**Backup first:**

```bash
cp .devagent/context.json .devagent/context.json.backup
```

**Reinitialize:**

```python
from backend.agents.context_manager import ContextManager
manager = ContextManager()
manager._initialize_context()
```

### History File Too Large

**Archive old entries:**

```bash
# Keep last 1000 entries
tail -1000 .devagent/history.jsonl > .devagent/history_recent.jsonl
mv .devagent/history.jsonl .devagent/history_$(date +%Y%m%d).jsonl
mv .devagent/history_recent.jsonl .devagent/history.jsonl
```

---

## 🎉 You're Ready!

DevAgent v3.0 is now managing your development context automatically!

**What happens next:**

1. ✅ Every error is logged
2. ✅ Every fix is tracked
3. ✅ Every decision is recorded
4. ✅ Consistency is monitored
5. ✅ Documentation stays current
6. ✅ Patterns are detected
7. ✅ Refactorings are suggested

**No manual work required - it just works!** 🎯✨

---

## 📚 Learn More

- [DEVAGENT_V3_CONTEXT.md](./DEVAGENT_V3_CONTEXT.md) - Complete guide
- [DEVAGENT_V3_QUICKREF.md](./DEVAGENT_V3_QUICKREF.md) - Quick reference
- [DEVAGENT_V2.md](./DEVAGENT_V2.md) - Auto-fix features
- [ADK_ARCHITECTURE.md](./ADK_ARCHITECTURE.md) - System architecture

**Questions?** Check the context:

```bash
curl http://localhost:8000/api/context/summary
```
