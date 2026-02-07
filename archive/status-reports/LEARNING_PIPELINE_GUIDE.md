# 🧠 Agent Learning Pipeline - v7.2

## Complete Guide to Trinity Swarm Intelligence Growth

### Overview

The Conductor + Trinity Swarm implements a **closed-loop learning system** where agents continuously improve through:

1. **Decision Recording** - Every action is logged with reasoning
2. **Feedback Collection** - Outcomes are captured and analyzed
3. **Learning Signals** - Patterns inform future decisions
4. **Verification Gates** - Security and quality checks prevent errors

---

## Architecture Layers

### Layer 1: Decision Making (Trinity Swarm)

```
CommercialScout → OfficialVerifier → ExternalValidator
      ↓                ↓                    ↓
   [Harvest]       [Enrich]            [Audit]
   confidence      confidence          confidence
      ↓                ↓                    ↓
   Decision Log + Reasoning Trace + Verification Rules
```

**Each agent records:**

- Input data with context
- Decision output with rationale
- Confidence score (0-100)
- Execution timestamp
- Status (pending/approved/rejected)

### Layer 2: Feedback Engine

Captures outcomes about decisions:

- **VALIDATION_PASS**: Decision was correct
- **CORRECTION**: Agent made an error (includes fix)
- **DECISION_OVERRIDE**: Human overrode the decision
- **EDGE_CASE**: Unexpected scenario encountered
- **PERFORMANCE**: Speed/efficiency metrics

### Layer 3: Audit System

Comprehensive logging of all operations:

- Agent actions with execution time
- Verification gate results
- Security events with threat levels
- Approval/rejection decisions with rationale
- Error recovery attempts

### Layer 4: Analysis & Reporting

Intelligence metrics about agent performance:

- **Pipeline Accuracy**: Percentage of approved decisions
- **Agent Confidence**: Self-assessed confidence vs. actual accuracy
- **Common Errors**: Error types grouped by frequency
- **Bottlenecks**: Where the pipeline struggles
- **Improvement Areas**: Specific focus points for each agent

---

## Usage: CLI Commands

### 1. View Agent Learning Progress

```bash
python3 backend/conductor_main.py learning
```

Output shows:

- Each agent's accuracy percentage
- Number of approved vs. rejected decisions
- Common mistakes identified
- Specific improvement areas
- Confidence calibration metrics

### 2. View Audit Trail

```bash
python3 backend/conductor_main.py audit --limit 100
```

Shows:

- Recent operations (last 100 by default)
- Execution times
- Success/failure status
- Agent name for each action

### 3. Security Audit Report

```bash
python3 backend/conductor_main.py security
```

Displays:

- Critical security events
- Threat levels
- Recent security findings
- Risk assessment

### 4. Performance Metrics

```bash
python3 backend/conductor_main.py performance
```

Shows:

- Success rates by agent
- Average execution time
- Total operations performed
- Efficiency metrics

---

## Usage: REST API Endpoints

### Health & Learning Endpoints

#### Get Pipeline Health

```bash
curl http://localhost:8000/api/learning/health
```

Response:

```json
{
  "status": "healthy",
  "data": {
    "pipeline_accuracy": 85.2,
    "total_decisions": 2435,
    "agents": {
      "CommercialScout": {
        "accuracy": 82.1,
        "confidence": 88.5,
        ...
      }
    }
  }
}
```

#### Get Agent Learning Summary

```bash
curl http://localhost:8000/api/learning/agents/CommercialScout/learning
```

#### View Audit Trail

```bash
curl http://localhost:8000/api/learning/audit/trail?agent_name=OfficialVerifier&limit=50
```

#### Get Security Status

```bash
curl http://localhost:8000/api/learning/audit/security
```

#### Get Performance Metrics

```bash
curl http://localhost:8000/api/learning/performance
```

#### View Edge Cases

```bash
curl http://localhost:8000/api/learning/edge-cases
```

#### Submit Feedback

```bash
curl -X POST "http://localhost:8000/api/learning/feedback/{decision_id}?feedback_type=correction&explanation=Missing+field&impact_score=75"
```

#### View Learning Manifest (Perfection Map)

```bash
curl http://localhost:8000/api/learning/manifest
```

Response shows:

```json
{
  "perfection_map": {
    "overall_accuracy": {
      "current": 85.2,
      "target": 98.0,
      "progress_percent": 86.9
    },
    "agents": {
      "CommercialScout": {
        "current_accuracy": 82,
        "target_accuracy": 95,
        "path_to_perfection": {
          "phase_1_foundations": "Complete",
          "phase_2_refinement": "In Progress",
          "phase_3_mastery": "Pending"
        }
      }
    }
  }
}
```

---

## The Perfection Map: Path to 98% Accuracy

### Phase 1: Foundations (70% → 85%)

**Goal**: Each agent makes correct decisions majority of the time

Checklist:

- ✅ Agent produces valid output
- ✅ Decision includes reasoning
- ✅ Confidence score is calibrated
- ✅ Common error types identified

### Phase 2: Refinement (85% → 95%)

**Goal**: Handle most edge cases, minimize common errors

Focus Areas:

- Fix identified error patterns
- Handle discovered edge cases
- Improve confidence calibration
- Reduce false positives

### Phase 3: Mastery (95% → 98%+)

**Goal**: Near-perfect performance on known scenarios

Requirements:

- Edge case database built
- Error recovery routines optimized
- Verification gates tuned
- Human-in-loop feedback integrated

---

## How Learning Manifests in the Pipeline

### 1. Auto-Detection of Error Patterns

```
Decision 1: Cat misclassified as Dog (Confidence: 92%)
  ↓ Feedback: CORRECTION (impact: 70)
  ↓ Analysis: "Vision model confused by lighting"

Decision 100-150: Similar pattern identified
  ↓ Recommendation: "Retrain agent on low-light images"
```

### 2. Confidence Calibration

```
Agent claims 95% confidence on decisions
Actual accuracy on those decisions: 82%
  ↓ Recommendation: "Lower confidence threshold when accuracy is uncertain"
```

### 3. Edge Case Tracking

```
Unusual input: Product with no images
  ↓ Handled by: Error recovery routine
  ↓ Logged as: EDGE_CASE
  ↓ Resolution: Flag for manual review
```

### 4. Security Learning

```
Suspicious: Duplicate product IDs
  ↓ Verification gate: BLOCKED
  ↓ Logged as: SECURITY event
  ↓ Learning: Add uniqueness check to intake
```

---

## Key Files

| File                                   | Purpose                                 |
| -------------------------------------- | --------------------------------------- |
| `backend/agents/feedback_engine.py`    | Records decisions and collects feedback |
| `backend/agents/audit_system.py`       | Comprehensive operation logging         |
| `backend/agents/learning_endpoints.py` | REST API for insights                   |
| `backend/conductor_main.py`            | CLI commands for reporting              |
| `backend/logs/feedback/`               | Decision & feedback history             |
| `backend/logs/audit/`                  | Audit event logs                        |

---

## Integration With Conductor

The Conductor orchestrates the entire learning loop:

```python
# In conductor_main.py::ingest_brand()

1. Load raw data
   ↓
2. Run Trinity Swarm
   - agents.record_decision() for each action
   ↓
3. Verify results
   - audit_logger.log_verification() for each gate
   ↓
4. Save to database
   ↓
5. Collect feedback (manual or automatic)
   - feedback_engine.submit_feedback()
   ↓
6. Generate insights
   - feedback_engine.get_pipeline_health_report()
   ↓
7. Display recommendations
   - Show improvement areas
```

---

## Quality Standards (PerfectionMap)

Every agent strives toward these perfection standards:

### Accuracy Metrics

- **Minimum Passing**: 70% accuracy
- **Good Performance**: 85% accuracy
- **Excellent**: 95% accuracy
- **Target (Perfection)**: 98%+ accuracy

### Confidence Alignment

- Claimed confidence should match actual accuracy
- Example: 80% confidence → should be correct 80% of the time

### Response Time

- Harvest: < 2 seconds per product
- Enrich: < 1 second per product
- Validate: < 0.5 seconds per product

### Error Recovery

- All failures should trigger recovery attempts
- Recovery success rate target: 90%+

---

## Example: Complete Learning Flow

### Scenario: CommercialScout Encounters Edge Case

```
1. [DECISION] CommercialScout harvests product
   - Input: Product listing with no price
   - Output: Product draft (confidence: 45%)
   - Reasoning: "Missing critical field, low confidence"

2. [AUDIT] Operation logged
   - Category: AGENT_ACTION
   - Status: partial
   - Execution: 1.2s

3. [VERIFICATION] ExternalValidator reviews
   - Result: BLOCKED (missing price)
   - Violation: "Price required for approval"
   - Status: REJECTED

4. [FEEDBACK] System logs edge case
   - Type: EDGE_CASE
   - Impact: 60 (important but handled)
   - Correction: "Implement 'price required' gate"

5. [LEARNING] Summary generated
   - Type: "Missing price field"
   - Frequency: 23 occurrences
   - Recommendation: "Add price scraping fallback"

6. [IMPROVEMENT] Next time CommercialScout runs:
   - Confidence on similar cases: reduced to 30%
   - Gate strength: VERIFY PRICE EARLY
   - Error recovery: Try alternative price sources
```

---

## Monitoring Agent Health

### Daily Checks

```bash
# Check overall pipeline
python3 backend/conductor_main.py learning

# Review audit trail
python3 backend/conductor_main.py audit --limit 200

# Security status
python3 backend/conductor_main.py security
```

### Weekly Deep Dives

```bash
# API call to get edge cases
curl "http://localhost:8000/api/learning/edge-cases" | jq

# View common errors
curl "http://localhost:8000/api/learning/agents/CommercialScout/learning" | jq '.summary.common_errors'
```

### Intervention Points

If accuracy drops below 70%:

1. Review recent decisions
2. Identify systematic error
3. Submit correction feedback
4. Monitor confidence calibration

---

## Architecture Guarantee

**The Learning Pipeline Ensures:**

✅ **Traceability**: Every decision has an audit trail
✅ **Accountability**: Errors are logged with context
✅ **Improvability**: Feedback closes the learning loop
✅ **Security**: All operations verified and logged
✅ **Transparency**: Metrics accessible via API & CLI
✅ **Growth**: Agents demonstrably improve over time

---

## Next Steps

1. **Run the pipeline**: `python3 backend/conductor_main.py build`
2. **Check health**: `python3 backend/conductor_main.py learning`
3. **Monitor metrics**: Watch `/api/learning/health` in real-time
4. **Submit feedback**: Use `/api/learning/feedback/{id}` endpoint
5. **Iterate**: Repeat to drive toward perfection (98%+)

---

_The Conductor + Trinity Swarm v7.2 - Where agents learn, improve, and perfect._
