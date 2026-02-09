# Phase 8.0b: Performance Validation & Stress Testing

**Status**: 🔄 IN PROGRESS  
**Target Date**: February 17, 2026  
**Duration**: 8 days (Week 2)  
**Effort**: 15-20 hours

---

## 📋 Objectives

### Primary Goals

1. **Validate Performance**: Confirm 30x+ throughput improvement (1,000 products in <1 hour)
2. **Stress Testing**: Verify system stability under 100+ concurrent tasks
3. **Data Integrity**: Ensure zero data loss during processing
4. **Recovery Testing**: Validate failure handling & auto-recovery
5. **Production Readiness**: Confirm system ready for gradual cutover

---

## 🎯 Testing Schedule (Week of Feb 10-17, 2026)

### Day 1-2: Performance Baseline (Feb 10-11)

- [ ] Run parallel v7.6 vs v8.0 on 10 brands (12 hours total)
- [ ] Measure latency, throughput, accuracy
- [ ] Document baseline metrics
- [ ] Generate comparison report

### Day 3-4: Stress Testing (Feb 12-13)

- [ ] Sync 100, 500, 1,000 products concurrently
- [ ] Monitor CPU, memory, network, disk usage
- [ ] Identify bottlenecks & optimization opportunities
- [ ] Test worker scaling behavior

### Day 5: Data Integrity (Feb 14)

- [ ] Validate product data integrity
- [ ] Test failure scenarios (worker crash, Redis down, PostgreSQL down)
- [ ] Verify audit log completeness
- [ ] Confirm no duplicate products or data loss

### Day 6: Recovery & Monitoring (Feb 15)

- [ ] Test worker restart & recovery
- [ ] Validate queue persistence after outages
- [ ] Set up production monitoring (Prometheus, alerts)
- [ ] Create troubleshooting runbooks

### Day 7: Load Testing (Feb 16)

- [ ] Simulate production load (sustained throughput)
- [ ] Test with real brands & product data
- [ ] Measure 95th/99th percentile latencies
- [ ] Identify resource limits

### Day 8: Cutover Planning (Feb 17)

- [ ] Generate final validation report
- [ ] Plan gradual migration strategy (10% → 50% → 100%)
- [ ] Create production deployment guide
- [ ] Prepare rollback procedures

---

## 🧪 Test Scenarios

### Scenario 1: Baseline Performance (v7.6 vs v8.0)

**Setup**:

```bash
python3 backend/tests/test_parallel_v7_v8.py \
  --brands "Roland,Yamaha,Korg,Audio-Technica,Ampeg,Arturia" \
  --mode correctness \
  --timeout 1800
```

**Expected Results**:
| Metric | v7.6 | v8.0 | Target |
|--------|------|------|--------|
| 1 product | 90s | 90s | Same latency |
| 10 products | 900s | 180s | 5x faster |
| 100 products | 9,000s | 1,200s | 7.5x faster |
| Accuracy | 100% | 100% | Match exactly |

**Success Criteria**:

- ✅ v8.0 at least 5x faster than v7.6
- ✅ 100% product count accuracy match
- ✅ No errors or timeouts
- ✅ Consistent results across multiple runs

---

### Scenario 2: Concurrent Load (Stress Test)

**Test 1: 10 Concurrent Harvests**

```bash
for brand in Roland Yamaha Korg Audio-Technica Ampeg Arturia \
              Ashdown Alesis Akai Amphion; do
  curl -X POST http://localhost:8000/api/v8/tasks/harvest/$brand &
done; wait

# Monitor with
python3 backend/scripts/monitor_workers.py --watch
```

**Test 2: 100 Concurrent Products (via single big sync)**

```bash
# Queue batch sync for large brand
curl -X POST "http://localhost:8000/api/v8/tasks/batch-sync?brand=Roland&product_ids=1,2,3,...,100"

# Monitor queue depth
redis-cli -u redis://localhost:6379/0 LLEN harvest
redis-cli -u redis://localhost:6379/0 LLEN enrich
redis-cli -u redis://localhost:6379/0 LLEN validate
```

**Test 3: 1,000 Product Sync (Ultimate Stress)**

```bash
python3 << 'EOF'
import requests
import time

brands = ['Roland', 'Yamaha', 'Korg', 'Audio-Technica', 'Ampeg']
task_ids = []

print("🚀 Queueing 1,000 products across 5 brands...")
start = time.time()

for brand in brands:
  # Queue harvest
  resp = requests.post(f"http://localhost:8000/api/v8/tasks/harvest/{brand}")
  task_ids.append(resp.json()['task_id'])

# Wait for completion
completed = 0
while completed < len(task_ids):
  time.sleep(5)
  for task_id in task_ids:
    resp = requests.get(f"http://localhost:8000/api/v8/tasks/result/{task_id}")
    if resp.json()['ready']:
      completed += 1
  print(f"Progress: {completed}/{len(task_ids)} tasks")

elapsed = time.time() - start
print(f"\n✅ Completed in {elapsed:.0f} seconds ({elapsed/60:.1f} minutes)")
print(f"Throughput: {1000 / elapsed:.1f} products/second")
EOF
```

**Resource Monitoring** (during tests):

```bash
# Terminal 1: Docker containers
docker stats --no-stream

# Terminal 2: Redis memory usage
redis-cli -u redis://localhost:6379/0 INFO memory

# Terminal 3: PostgreSQL connections
psql postgresql://halilit_user@localhost/halilit_tasks \
  -c "SELECT count(*) FROM pg_stat_activity;"

# Terminal 4: Worker health
watch -n 2 "python3 backend/scripts/monitor_workers.py"

# Terminal 5: System resources
watch -n 2 "free -h && df -h && ps aux | grep celery"
```

**Success Criteria**:

- ✅ All 10 harvests complete within 30 minutes
- ✅ Queue depths remain manageable (< 10,000)
- ✅ Workers stay healthy (no crashes/timeouts)
- ✅ Redis memory usage < 1GB
- ✅ PostgreSQL handles all connections
- ✅ CPU usage < 80% sustained

---

### Scenario 3: Data Integrity Validation

**Test: Complete Audit Trail**

```sql
-- Check all tasks were recorded
SELECT COUNT(*) as total_tasks,
       COUNT(CASE WHEN status='success' THEN 1 END) as successful,
       COUNT(CASE WHEN status='failure' THEN 1 END) as failed
FROM task_audit_log;

-- Check for missing products
SELECT brand, COUNT(*) as product_count
FROM product_enrichment_history
GROUP BY brand
ORDER BY product_count DESC;

-- Verify no duplicates
SELECT product_id, COUNT(*) as count
FROM product_enrichment_history
GROUP BY product_id
HAVING COUNT(*) > 1;

-- Check audit log completeness
SELECT
  started_at::date,
  COUNT(*) as tasks,
  SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) as success,
  ROUND(100.0 * SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM task_audit_log
GROUP BY started_at::date
ORDER BY started_at DESC;
```

**Success Criteria**:

- ✅ 100% task success rate
- ✅ Zero duplicate products
- ✅ All enrichment stages present
- ✅ Audit trail matches expected results
- ✅ No missing or orphaned tasks

---

### Scenario 4: Failure Recovery

**Test 1: Worker Crash Recovery**

```bash
# Queue a long-running harvest
curl -X POST http://localhost:8000/api/v8/tasks/harvest/Roland

# Kill the harvest worker
docker-compose kill worker_harvest

# Wait 5 seconds, restart
sleep 5
docker-compose up -d worker_harvest

# Monitor recovery
watch -n 1 "redis-cli -u redis://localhost:6379/0 LLEN harvest"

# Verify task completes successfully
curl http://localhost:8000/api/v8/tasks/result/{task_id}
```

**Test 2: Redis Down Recovery**

```bash
# Queue multiple tasks
for brand in Roland Yamaha Korg; do
  curl -X POST http://localhost:8000/api/v8/tasks/harvest/$brand
done

# Bring down Redis
docker-compose stop redis

# Wait 30 seconds
sleep 30

# Restart Redis
docker-compose up -d redis

# Verify:
# 1. Tasks still in queue
# 2. Workers resume processing
# 3. Results are retrievable
```

**Test 3: PostgreSQL Down Recovery**

```bash
# Similar flow
# 1. Queue tasks
# 2. Stop PostgreSQL
# 3. Verify in-memory processing continues (Redis still works)
# 4. Restart PostgreSQL
# 5. Verify audit log is complete
```

**Success Criteria**:

- ✅ Tasks survive worker failures (auto-retry)
- ✅ Queue persists Redis outages
- ✅ Audit log persists PostgreSQL recovery
- ✅ No tasks lost during failures
- ✅ Auto-recovery within 1 minute

---

## 📊 Metrics to Collect

### Performance Metrics

```python
metrics = {
    'harvest': {
        'duration_seconds': float,
        'product_count': int,
        'products_per_second': float,
        'success_rate': float,
    },
    'enrich': {
        'duration_seconds': float,
        'items_per_second': float,
    },
    'validate': {
        'duration_seconds': float,
        'items_per_second': float,
        'avg_risk_score': float,
    },
    'pipeline': {
        'total_duration_seconds': float,
        'bottleneck_stage': str,
    }
}
```

### Resource Metrics

```python
resources = {
    'redis': {
        'memory_used_mb': float,
        'memory_max_mb': float,
        'connected_clients': int,
    },
    'postgresql': {
        'active_connections': int,
        'disk_used_mb': float,
        'query_latency_ms': float,
    },
    'workers': {
        'cpu_percent': float,
        'memory_percent': float,
        'active_tasks': int,
        'failed_tasks': int,
    },
    'api': {
        'response_time_ms': float,
        'error_rate_percent': float,
    }
}
```

---

## 📝 Reporting

### Daily Standup Report (Template)

```
Date: [DATE]
Phase: Phase 8.0b Performance Validation
Status: [IN PROGRESS | COMPLETE]

Tests Run:
- [ ] Performance Baseline (v7.6 vs v8.0)
- [ ] Stress Test (10/100/1,000 concurrent)
- [ ] Data Integrity
- [ ] Failure Recovery
- [ ] Load Test

Key Metrics:
- v8.0 Throughput: X products/minute (Target: 25+ products/minute for 1,000 items)
- Success Rate: X% (Target: 99%+)
- Worker Health: X workers active (Target: 5 healthy)
- Resource Usage: CPU X%, Memory Y%, Disk Z%

Issues Found:
1. [Issue] → [Status: Open/In Progress/Resolved]
2. [Issue] → [Status: Open/In Progress/Resolved]

Blockers:
- None / [List blockers]

Next Steps:
- [ ] [Task 1]
- [ ] [Task 2]

Notes:
[Any additional observations]
```

---

## ✅ Acceptance Criteria (Phase 8.0b Complete)

### Performance ✅

- [ ] v8.0 achieves 30x+ throughput improvement vs v7.6
- [ ] 1,000 products sync in < 1 hour
- [ ] 100+ concurrent tasks supported
- [ ] Sub-second latency for task queueing

### Reliability ✅

- [ ] 99.5%+ task success rate (auto-retry working)
- [ ] Zero data loss during normal operations
- [ ] Zero data loss during failure scenarios
- [ ] Workers recover from crashes within 1 minute

### Resource Efficiency ✅

- [ ] Redis memory < 1GB for 1,000 concurrent items
- [ ] PostgreSQL handles all connections without issues
- [ ] CPU usage < 80% sustained
- [ ] No memory leaks on workers

### Observability ✅

- [ ] Flower shows all workers & queues accurately
- [ ] PostgreSQL audit log captures 100% of tasks
- [ ] Monitoring script works reliably
- [ ] All errors are logged with full context

### Documentation ✅

- [ ] Testing report with all metrics
- [ ] Gradual cutover plan (10% → 100%)
- [ ] Production deployment guide
- [ ] Troubleshooting runbook

---

## 🚀 Go/No-Go Decision (Feb 17)

### Go Criteria

✅ All acceptance criteria met  
✅ No critical issues remaining  
✅ Performance targets hit  
✅ Team confidence: HIGH

### No-Go Criteria (Roll back to v7.6)

❌ Data loss detected  
❌ >1% task failure rate  
❌ Resource exhaustion crash  
❌ Unresolvable performance issues

---

## 📞 Support & Contacts

**On-Call During Testing**:

- Backend: [Team contact]
- DevOps: [Team contact]
- Database: [Team contact]

**Escalation Path**:

1. Try automated recovery (restart workers/services)
2. Contact on-call engineer
3. Escalate to tech lead if unresolved after 15 min

---

## 📚 Related Documentation

- [Phase 8.0 Main Spec](PHASE_8.0_TASK_QUEUE_MIGRATION.md)
- [Quick Start Guide](PHASE_8.0_QUICK_START.md)
- [File Reference](PHASE_8.0_FILES_GUIDE.md)
- [Testing Framework](backend/tests/test_parallel_v7_v8.py)

---

**Last Updated**: February 9, 2026  
**Next Milestone**: Feb 17 - Go/No-Go Decision for Production Cutover
