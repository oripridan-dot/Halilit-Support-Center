# Phase 8.0c: Gradual Cutover Strategy (Feb 17-Mar 2)

## 🎯 Objective

Transition production traffic from v7.6 (synchronous) to v8.0 (async queue) with **zero downtime** and ability to rollback instantly at any stage.

**Success Criteria**:

- All traffic successfully migrated to v8.0
- Zero data loss during cutover
- < 1% error rate during all phases
- Team confidence HIGH for permanent switch

---

## 📋 Pre-Cutover Checklist (Feb 17)

### Infrastructure Readiness

- [ ] Phase 8.0b testing PASSED (all 25+ acceptance criteria met)
- [ ] Production database backed up
- [ ] Monitoring & alerting configured
- [ ] On-call rotation established
- [ ] Rollback procedures documented & tested

### Feature Flags

```bash
# Deploy feature flag system
cd backend
python3 scripts/setup_feature_flags.py

# Flags needed:
# - "v8.0_enabled": false (disable if needed)
# - "v8.0_traffic_percent": 0 (start at 0%)
# - "v8.0_error_threshold": 0.01 (1% error rate limit)
# - "fallback_to_v7.6": true (emergency switch)
```

### Dashboard & Alerts

- [ ] Grafana/Prometheus configured with v7.6 vs v8.0 metrics
- [ ] PagerDuty alerts: task success rate, API latency, database connections
- [ ] Slack notifications: traffic migration milestones
- [ ] Hourly comparison reports (v7.6 vs v8.0)

### Team Preparation

- [ ] Runbook trained and distributed
- [ ] On-call engineer briefed
- [ ] Rollback drill executed
- [ ] Stakeholder notification email sent

---

## 🚀 Phase 8.0c Timeline

### Week 1: Cautious Ramp (Feb 17-23)

#### **Feb 17 - CUTOVER DECISION POINT**

**Go/No-Go Decision Criteria** (from Phase 8.0b):

```
CUTOVER-READY if:
✅ All 4 test scenarios passed
✅ 30x+ throughput improvement validated
✅ 100+ concurrent task capacity proven
✅ Zero data loss confirmed
✅ All monitoring dashboards green
✅ Team confidence HIGH
```

**Decision Process** (2 hours):

1. Stakeholders review Phase 8.0b final report (30 min)
2. Engineering lead validates readiness (30 min)
3. Team votes go/no-go (15 min)
4. If GO: proceed to Feb 17 afternoon
5. If NO-GO: schedule review meeting, identify blockers

---

#### **Feb 17 Afternoon - PHASE 1: 5% Traffic (Canary)**

**Duration**: 24 hours  
**Goal**: Validate basic functionality in production  
**Actions**:

```bash
# 1. Verify current state
curl http://localhost:8000/api/v8/tasks/health
# Expected: {"broker": "ok", "workers": 5}

# 2. Enable feature flag
python3 backend/scripts/set_feature_flag.py v8.0_enabled true

# 3. Route 5% of harvest API calls to v8.0
python3 backend/scripts/set_feature_flag.py v8.0_traffic_percent 5

# 4. Start monitoring
# - Real-time Grafana dashboard
# - Hourly comparison report
# - Slack notifications enabled
```

**Monitoring** (every 1 hour, 24h on-call):

```bash
# Metric 1: Error rate
SELECT 100*COUNT(DISTINCT task_id)
  / (SELECT COUNT(*) FROM task_audit_log WHERE created_at > NOW() - INTERVAL '1 hour')
FROM task_audit_log
WHERE status='failure' AND created_at > NOW() - INTERVAL '1 hour';

# Metric 2: Compare v7.6 vs v8.0
SELECT version, COUNT(*), AVG(duration_seconds), STDDEV(duration_seconds)
FROM task_audit_log
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY version;

# Metric 3: Queue depth
SELECT queue_name, pending_count, active_count
FROM current_queue_depths;
```

**Success Criteria for Phase 1**:

- ✅ 5% traffic processed with > 99% success
- ✅ Average latency < 2 seconds
- ✅ No duplicate products detected
- ✅ No data loss
- ✅ Worker health stable
- ✅ PostgreSQL connections normal

**What to Watch For**:

- Task timeout (> 1 hour) → Check worker concurrency
- High error rate → Check logs, may indicate environment issue
- Memory spike → Check Redis/PostgreSQL
- API latency spike → Check worker load

---

#### **Feb 18 AM - DECISION POINT 1**

**Review Phase 1 Results**:

```markdown
Metrics to Check:

- [ ] Success rate: **\_**% (target: > 99%)
- [ ] Error rate trend: **\_** (target: < 1%)
- [ ] Avg latency: **\_** ms (target: < 2000ms)
- [ ] P99 latency: **\_** ms (target: < 5000ms)
- [ ] Worker health: **\_** (target: HEALTHY)
- [ ] Database health: **\_** (target: HEALTHY)
- [ ] Any critical issues? NO / YES → describe

Recommendation:

- [ ] PROCEED to 10% (if all metrics green)
- [ ] EXTEND PHASE 1 (if metrics marginal but trending good)
- [ ] ROLLBACK (if any critical issues)
```

---

#### **Feb 18 - PHASE 2: 10% Traffic**

```bash
python3 backend/scripts/set_feature_flag.py v8.0_traffic_percent 10
```

**Duration**: 48 hours  
**Goal**: Validate at moderate load  
**Monitoring**: Same as Phase 1, but with tighter thresholds

**Success Criteria**:

- ✅ > 99.5% success rate
- ✅ No database deadlocks
- ✅ No worker exhaustion
- ✅ Audit trail complete

---

#### **Feb 20 AM - DECISION POINT 2**

Same review template as Decision Point 1. If metrics are excellent:

- **Proceed to 25%** (Feb 20)

---

### Week 2: Moderate Ramp (Feb 23-Mar 2)

#### **Feb 20 - PHASE 3: 25% Traffic**

```bash
python3 backend/scripts/set_feature_flag.py v8.0_traffic_percent 25
```

**Duration**: 48 hours  
**Goal**: Validate at 25% production load  
**Changes**:

- Reduce on-call interval to 30 min checks
- Auto-scaling may engage

---

#### **Feb 22 - DECISION POINT 3: 50% Traffic**

```bash
python3 backend/scripts/set_feature_flag.py v8.0_traffic_percent 50
```

**Duration**: 48 hours  
**Goal**: Validate at 50% load (majority of traffic)  
**Changes**:

- Both v7.6 and v8.0 equally loaded
- Watch for v7.6 degradation
- Start planning permanent switch

---

#### **Feb 24 - DECISION POINT 4: 75% Traffic**

```bash
python3 backend/scripts/set_feature_flag.py v8.0_traffic_percent 75
```

**Duration**: 24 hours  
**Goal**: Mostly v8.0 traffic, v7.6 support only

---

#### **Feb 25 - PHASE FINAL: 100% Traffic (FULL CUTOVER)**

```bash
python3 backend/scripts/set_feature_flag.py v8.0_traffic_percent 100
```

**Actions**:

1. Route all traffic to v8.0
2. Keep v7.6 running as fallback (not receiving traffic)
3. Monitor closely for 24 hours
4. Document final metrics

**Success Criteria**:

- ✅ 100% of traffic successfully processed
- ✅ Zero downtime during cutover
- ✅ All data integrity maintained
- ✅ User-facing latency improved

---

#### **Feb 26 - STABILIZATION PERIOD**

**48-Hour Observation** (keep on-call, 30-min checks):

- Hourly health reports
- User feedback collection
- Database performance analysis

**If Stable**:

- Remove v7.6 from active routing
- Archive v7.6 database for reference
- Update documentation to reflect v8.0 as standard

**If Issues Detected**:

- Trigger rollback procedure (see below)
- Document issues
- Return to Phase 8.0b analysis

---

## 🔄 Rollback Procedure

### Instant Rollback (Any Phase)

```bash
# IMMEDIATE: Route all traffic back to v7.6
python3 backend/scripts/set_feature_flag.py v8.0_traffic_percent 0
python3 backend/scripts/set_feature_flag.py fallback_to_v7.6 true

# Verify
curl http://localhost:8000/api/v7.6/tasks/health

# Notify stakeholders
python3 backend/scripts/send_alert.py "ROLLBACK TRIGGERED: Switching to v7.6"

# Investigate
# 1. Check logs
tail -100 logs/*.log | grep ERROR
# 2. Review metrics
cat logs/phase8c_metrics.json
# 3. Database consistency check
psql -c "SELECT COUNT(DISTINCT product_id) FROM product_enrichment_history;"
```

### Root Cause Analysis (72 hours)

```markdown
# Rollback Report

## What Happened

[Describe the failure]

## When It Happened

[Timestamp of first error]

## Impact

- Traffic affected: **\_**%
- Errors: \_\_\_\_
- Data loss: YES / NO

## Root Cause

[Analysis from logs and metrics]

## Fix Required

[What needs to be fixed in Phase 8.1]

## Prevention

[How we prevent this next time]
```

---

## 📊 Monitoring During Cutover

### Critical Metrics (Check every 30 min)

```sql
-- Success rate by hour
SELECT
  DATE_TRUNC('hour', created_at) as hour,
  version,
  COUNT(*) as total,
  SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
  100.0 * SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) / COUNT(*) as rate
FROM task_audit_log
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY 1, 2
ORDER BY 1 DESC;

-- Latency by version
SELECT
  version,
  COUNT(*) as count,
  AVG(duration_seconds) as avg_latency,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_seconds) as p95,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY duration_seconds) as p99,
  MAX(duration_seconds) as max_latency
FROM task_audit_log
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY version;

-- Error analysis
SELECT
  error_type,
  COUNT(*) as count,
  COUNT(DISTINCT brand) as brands_affected
FROM task_audit_log
WHERE status = 'failure' AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY 1
ORDER BY 2 DESC;
```

### Dashboard Setup

**Grafana Panels** (create in advance):

1. **Traffic Distribution**: Pie chart of v7.6 vs v8.0
2. **Success Rate**: Line graph by version (1h resolution)
3. **Latency**: Box plot of p50/p95/p99
4. **Error Rate**: Stacked area by error type
5. **Worker Health**: Status of all workers
6. **Database**: Connections, slow queries, deadlocks

### Alert Thresholds

```yaml
# PagerDuty/Prometheus alerts
rules:
  - name: HighErrorRate
    condition: error_rate > 0.01 # 1%
    severity: CRITICAL
    action: Page on-call engineer

  - name: HighLatency
    condition: p99_latency > 5000 # 5 seconds
    severity: WARNING
    action: Notify in Slack

  - name: WorkerDown
    condition: active_workers < 3
    severity: CRITICAL
    action: Page on-call engineer

  - name: DBConnections
    condition: pg_connections > 80 # of 100
    severity: WARNING
    action: Notify in Slack
```

---

## 📞 Escalation & Communication

### Daily Standup (10:00 AM EST)

**Participants**: Engineering lead, on-call engineer, product manager

**Talking Points**:

```markdown
- Current traffic percentage: \_\_\_%
- Success rate (last 24h): \_\_\_%
- Any incidents: YES / NO
- Next decision point: [Phase Y]
- Go/No-Go decision: ****\_\_\_****
- Actions: [list required actions]
```

### Notification Templates

**Phase Start** (Post to #product):

```
🚀 Phase 8.0c PHASE [N]: [X]% Traffic Migration [DATE]
Starting [TIME]. Expect normal user experience.
On-call: [Name]. Monitoring at [dashboard-url].
```

**Issue Detected** (Post to #incidents):

```
⚠️  Phase 8.0c: Error rate spike detected
Severity: [P1/P2/P3]
Details: [description]
Action: [immediate action taken]
Status: [investigating / identified / resolved]
```

**Rollback Alert** (Post to #product + #incidents):

```
🔴 ROLLBACK TRIGGERED: Phase 8.0c
Reason: [brief description]
Time: [timestamp]
Impact: [minimal / moderate / significant]
Next Steps: [root cause analysis scheduled]
```

---

## ✅ Phase 8.0c Success Checklist

**Cutover Complete** (all items checked):

- [ ] 100% traffic on v8.0 for 48+ hours
- [ ] Success rate > 99.5% sustained
- [ ] No data loss detected
- [ ] Monitoring shows improvement over v7.6
- [ ] Zero unplanned rollbacks
- [ ] Team confidence HIGH for permanent switch
- [ ] Documentation updated
- [ ] Stakeholder sign-off received

---

## 🎓 Learning & Optimization (Phase 8.1)

After successful cutover, perform:

1. **Performance Analysis**
   - Identify bottlenecks in v8.0
   - Tune worker concurrency
   - Optimize database queries

2. **Cost Analysis**
   - Compare resource usage v7.6 vs v8.0
   - Validate cost savings from async
   - Identify optimization opportunities

3. **Feature Expansion**
   - Extend to other product types
   - Add priority queue support
   - Implement cancellation UI

4. **Reliability Hardening**
   - Add circuit breaker for agent failures
   - Improve retry logic
   - Add more observability metrics

---

## 📋 Appendix: Feature Flag API

```python
# Set traffic percentage
python3 backend/scripts/set_feature_flag.py v8.0_traffic_percent 50

# Check current value
python3 backend/scripts/get_feature_flag.py v8.0_traffic_percent
# Output: 50

# Emergency disable
python3 backend/scripts/set_feature_flag.py v8.0_enabled false

# Check all flags
python3 backend/scripts/list_feature_flags.py
# Output:
# v8.0_enabled: true
# v8.0_traffic_percent: 50
# v8.0_error_threshold: 0.01
# fallback_to_v7.6: true
```

---

## 📞 Support Contacts

| Role             | Name    | Phone   | Slack     |
| ---------------- | ------- | ------- | --------- |
| Engineering Lead | [Name]  | [Phone] | @[handle] |
| On-Call Rotation | [Daily] | [Phone] | @on-call  |
| Product Manager  | [Name]  | [Phone] | @[handle] |
| DevOps Lead      | [Name]  | [Phone] | @[handle] |

---

**Status**: Ready for execution after Phase 8.0b completion  
**Last Updated**: [DATE]  
**Owner**: Engineering Team
