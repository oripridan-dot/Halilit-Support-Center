# 🧠 Agent Memory & Learning System v5.1

## Overview

The **Agent Memory System** enables all agents in the Trinity Swarm to **learn from every action** and **continuously improve** their performance through AI-powered pattern analysis.

## Key Features

### 1. **Functional Memory**

- Every agent action is recorded in `.agent_memory/learning_history.jsonl`
- Persistent storage survives restarts
- Full context of inputs, outputs, success/failure, confidence

### 2. **AI-Powered Pattern Analysis**

- Gemini 2.0 Flash analyzes learning records
- Extracts common successful patterns
- Identifies anti-patterns (what not to do)
- Context-specific recommendations

### 3. **Contextual Advice**

- Agents query past learning before acting
- AI generates advice based on similar past situations
- References what worked and what failed

### 4. **Self-Improvement**

- Agents identify their own weak areas
- Suggest specific improvements
- Track improvement over time

### 5. **Cross-Agent Learning**

- All agents (DevAgent, CommercialScout, OfficialVerifier, ExternalValidator)
- Shared memory infrastructure
- Agent-specific insights

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AGENT ACTION                         │
│  (analyze_error, validate, harvest, enrich, audit)      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              MemoryAwareMixin.learn_from_action()       │
│  • Records input/output                                  │
│  • Success/failure                                       │
│  • Confidence score                                      │
│  • Patterns learned                                      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│          .agent_memory/learning_history.jsonl            │
│  (Append-only log of all learning records)               │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│         AgentMemory.analyze_patterns()                   │
│  • Uses Gemini AI to find patterns                       │
│  • Generates AgentInsight objects                        │
│  • Cached in insights.json                               │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│         Next Action Gets Contextual Advice               │
│  • Agent queries memory before acting                    │
│  • AI suggests optimal approach                          │
│  • References past successes/failures                    │
└─────────────────────────────────────────────────────────┘
```

## Data Models

### LearningRecord

```python
{
    "id": "DevAgent_2026-02-02T15:30:00",
    "timestamp": "2026-02-02T15:30:00",
    "agent_name": "DevAgent",
    "action_type": "analyze_error",
    "input_summary": "TypeError: Cannot read properties of null",
    "output_summary": "Fixed by adding optional chaining",
    "success": true,
    "confidence": 95,
    "outcome_quality": 90,  # Validated later
    "patterns_learned": ["null-safety", "optional-chaining"],
    "mistakes_avoided": ["direct-property-access"],
    "improvement_suggestions": ["Add TypeScript strict mode"]
}
```

### AgentInsight

```python
{
    "pattern": "null-safety-with-optional-chaining",
    "frequency": 15,
    "success_rate": 0.93,
    "contexts": ["React hooks", "Zustand stores", "API data"],
    "recommended_approach": "Always use ?. for optional properties",
    "anti_patterns": ["Direct property access", "Manual null checks"]
}
```

## API Endpoints

### Get Agent Statistics

```bash
GET /api/memory/stats/{agent_name}

curl http://localhost:8000/api/memory/stats/DevAgent

Response:
{
    "total_actions": 47,
    "success_rate": 0.89,
    "avg_confidence": 88.5,
    "insights_count": 5,
    "recent_patterns": [
        "null-safety",
        "hooks-before-return",
        "async-state-handling"
    ]
}
```

### Get Contextual Advice

```bash
GET /api/memory/advice/{agent_name}?task={task_description}

curl "http://localhost:8000/api/memory/advice/DevAgent?task=Fix%20React%20hooks%20violation"

Response:
{
    "advice": "Based on 12 similar cases, move all hooks (useState, useEffect) before any conditional returns. Success rate: 95%. Avoid early returns before hooks - this caused 3 past failures."
}
```

### Get Learned Patterns

```bash
GET /api/memory/insights/{agent_name}

curl http://localhost:8000/api/memory/insights/DevAgent

Response:
{
    "insights": [
        {
            "pattern": "hooks-must-be-first",
            "frequency": 8,
            "success_rate": 1.0,
            "contexts": ["React components"],
            "recommended_approach": "Declare all hooks at component top",
            "anti_patterns": ["Conditional hooks", "Early returns before hooks"]
        }
    ]
}
```

### Get Improvement Suggestions

```bash
GET /api/memory/improvements/{agent_name}

curl http://localhost:8000/api/memory/improvements/DevAgent

Response:
{
    "improvements": [
        "Improve async-error-handling (current success: 75%) - Add try-catch for all async operations",
        "Increase decision confidence (current avg: 82%) - Gather more context before acting"
    ]
}
```

### Get All Agents Memory

```bash
GET /api/memory/all-agents

curl http://localhost:8000/api/memory/all-agents

Response:
{
    "DevAgent": { ... },
    "CommercialScout": { ... },
    "OfficialVerifier": { ... },
    "ExternalValidator": { ... }
}
```

## Usage in Code

### For Agent Developers

Every agent inherits from `MemoryAwareMixin`:

```python
from backend.agents.agent_memory import MemoryAwareMixin

class MyAgent(MemoryAwareMixin):
    def __init__(self):
        super().__init__()
        self.name = "MyAgent"  # Required for memory

    def do_something(self, input_data):
        # Get advice from past learning
        advice = self.get_advice_for("Processing similar data")
        print(f"💡 Memory advice: {advice}")

        # Do the work
        result = self.process(input_data)
        success = result.is_valid
        confidence = result.confidence

        # Record this action for learning
        self.learn_from_action(
            action_type="process",
            input_data=input_data,
            output_data=result,
            success=success,
            confidence=confidence,
            patterns=["data-processing", "validation"]
        )

        return result
```

### Automatic Learning in DevAgent

DevAgent now automatically learns from every action:

```python
# In analyze_error()
fix_suggestion = self.generate_fix(error)

# AUTOMATIC: Learn from this action
self.learn_from_action(
    action_type="analyze_error",
    input_data=error.model_dump(),
    output_data=fix_suggestion.model_dump(),
    success=fix_suggestion.confidence > 70,
    confidence=fix_suggestion.confidence,
    patterns=fix_suggestion.related_patterns
)
```

### Automatic Learning in Trinity Swarm

All agents (CommercialScout, OfficialVerifier, ExternalValidator) inherit from updated `AgentBase`:

```python
# In think() method
response = self.ai_generate(prompt)

# AUTOMATIC: Learn from every thought
self.learn_from_action(
    action_type="think",
    input_data=prompt[:200],
    output_data=response[:200],
    success=len(response) > 0,
    confidence=95,
    patterns=["gemini-response"]
)
```

## Learning Flow Example

### Scenario: DevAgent Fixes a React Hook Violation

1. **User encounters error**:

   ```
   TypeError: Cannot read properties of null (reading 'subscribe')
   ```

2. **DevAgent analyzes** (first time):
   - No prior learning available
   - Generates fix with 85% confidence
   - Records learning: `["null-safety", "react-hooks"]`

3. **Similar error occurs** (second time):
   - DevAgent queries memory: "React hook error with null"
   - Memory returns: "Past success: Use optional chaining ?."
   - DevAgent generates fix with 95% confidence (learned!)
   - Records learning again

4. **After 10 similar fixes**:
   - Pattern analysis triggers
   - AI extracts insight: "Always use ?. for store subscriptions"
   - Success rate: 95%
   - DevAgent now gives this advice proactively

5. **Next occurrence**:
   - DevAgent checks memory BEFORE fixing
   - Sees: "This pattern has 95% success with ?. approach"
   - Applies known solution immediately
   - Fix confidence: 98%

## Memory Persistence

### Storage Location

```
.agent_memory/
├── learning_history.jsonl    # All learning records (append-only)
└── insights.json              # Extracted patterns (updated periodically)
```

### Backup Strategy

```bash
# Backup memory
cp -r .agent_memory .agent_memory.backup

# Export for analysis
cat .agent_memory/learning_history.jsonl | jq . > memory_export.json
```

### Retention Policy

- **learning_history.jsonl**: Keep last 10,000 records
- **insights.json**: Keep all insights (they're already distilled)
- **Auto-archive**: Records older than 90 days moved to archive

## Performance Metrics

### Expected Improvements Over Time

| Metric            | Initial | After 20 Actions | After 100 Actions |
| ----------------- | ------- | ---------------- | ----------------- |
| Success Rate      | 75%     | 85%              | 93%               |
| Avg Confidence    | 80%     | 87%              | 92%               |
| Response Time     | 2.5s    | 2.0s             | 1.5s              |
| User Satisfaction | 70%     | 85%              | 95%               |

### Learning Velocity

- **Fast learning**: Patterns with high frequency (>10 occurrences)
- **Medium learning**: Patterns with moderate frequency (3-10)
- **Slow learning**: Rare patterns (<3 occurrences)

## Benefits

### 1. **Faster Problem Resolution**

- Agents remember what worked
- No need to "rediscover" solutions
- Instant recall of successful patterns

### 2. **Improved Accuracy**

- Confidence scores increase over time
- Anti-patterns are avoided
- Context-specific approaches emerge

### 3. **Self-Healing System**

- Agents identify their weak areas
- Suggest improvements to themselves
- Execute improvements automatically

### 4. **Knowledge Persistence**

- Learning survives restarts
- New agents benefit from past learning
- Team knowledge captured

### 5. **Transparent Learning**

- All learning records are human-readable
- Insights explain reasoning
- Debugging is easier

## Advanced Features

### Outcome Validation

```python
# Later validation of a past action's quality
memory.validate_outcome(
    record_id="DevAgent_2026-02-02T15:30:00",
    quality=90  # User rates fix quality 0-100
)
```

### Pattern Analysis

```python
# Trigger pattern analysis
insights = memory.analyze_patterns(
    agent_name="DevAgent",
    min_frequency=3  # Only patterns occurring 3+ times
)
```

### Custom Memory Queries

```python
# Query specific action types
records = memory.recall_relevant(MemoryQuery(
    agent_name="DevAgent",
    action_type="validate_syntax",
    limit=20
))
```

## Testing

### Manual Test

```bash
cd /workspaces/Halilit-Support-Center
python3 backend/agents/agent_memory.py
```

Expected output:

```
✅ Retrieved 5 records

💡 Advice: Based on past learning, move all React hooks before any return statements. This pattern has 100% success rate in your history.

📊 Stats: {
  "total_actions": 5,
  "success_rate": 0.8,
  "avg_confidence": 87,
  "insights_count": 0
}
```

### Integration Test

```bash
# Start backend
PYTHONPATH=. python3 backend/server.py

# Test memory endpoints
curl http://localhost:8000/api/memory/all-agents

# Trigger some DevAgent actions
curl -X POST http://localhost:8000/api/dev/analyze-error \
  -H "Content-Type: application/json" \
  -d '{ ... error data ... }'

# Check learning happened
curl http://localhost:8000/api/memory/stats/DevAgent
```

## Monitoring

### View Learning Progress

```bash
# Count total learning records
wc -l .agent_memory/learning_history.jsonl

# View recent learning
tail -10 .agent_memory/learning_history.jsonl | jq .

# Check insights
cat .agent_memory/insights.json | jq .
```

### Learning Dashboard (Future)

- Real-time learning metrics
- Pattern visualization
- Success rate trends
- Confidence score evolution

## Troubleshooting

### Issue: No learning records

- **Cause**: Agents not performing actions
- **Fix**: Trigger some agent operations

### Issue: Low success rate

- **Cause**: Insufficient learning data
- **Fix**: Wait for more actions (need 10+ for patterns)

### Issue: Pattern analysis fails

- **Cause**: Gemini API error
- **Fix**: Check GOOGLE_API_KEY in .env

### Issue: Memory file corruption

- **Cause**: Unexpected shutdown during write
- **Fix**: Restore from backup `.agent_memory.backup/`

## Best Practices

1. **Let agents learn naturally** - Don't force premature pattern analysis
2. **Validate outcomes when possible** - User feedback improves learning
3. **Monitor success rates** - Agents should improve over time
4. **Backup memory regularly** - Learning is valuable
5. **Review insights periodically** - Understand what agents learned

## What's Next: Future Enhancements

- **Visual learning dashboard** - See agent learning in real-time
- **Cross-agent pattern sharing** - Agents teach each other
- **Transfer learning** - Import learning from other projects
- **A/B testing** - Compare different approaches automatically
- **Reinforcement learning** - Agents optimize strategies
- **Natural language queries** - "Show me all failures related to React hooks"

---

## Integration Status

✅ **DevAgent**: Full integration with learning
✅ **Trinity Swarm**: All agents (CommercialScout, OfficialVerifier, ExternalValidator)
✅ **API Endpoints**: 5 memory endpoints live
✅ **Documentation**: Complete
✅ **Testing**: Manual and integration tests ready

## Learn More

- [backend/agents/agent_memory.py](../backend/agents/agent_memory.py) - Full implementation
- [backend/server.py](../backend/server.py) - API endpoints
- [DEVAGENT_V3_CONTEXT.md](./DEVAGENT_V3_CONTEXT.md) - Context management system

---

**Agent Memory System v5.1** - Every action is a lesson, every lesson makes us better. 🧠✨
