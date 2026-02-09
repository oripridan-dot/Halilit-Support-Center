# Phase 8.0b: Quick Test Reference

## 🚀 Quick Start (5 minutes)

### Pre-flight Check

```bash
# 1. Ensure Docker services are running
docker-compose up -d

# 2. Verify broker health
curl http://localhost:8000/api/v8/tasks/health

# 3. Check Flower dashboard
open http://localhost:5555
```

### Run All Tests (2-3 hours)

```bash
python3 backend/scripts/phase8b_stress_test.py --all --output logs/full_report.txt
```

### Run Individual Tests

**Baseline Comparison (15 min)**

```bash
python3 backend/scripts/phase8b_stress_test.py --baseline
```

**Stress Testing (60 min - 10, 50, 100 concurrent)**

```bash
python3 backend/scripts/phase8b_stress_test.py --stress
```

**Data Integrity Check (10 min)**

```bash
python3 backend/scripts/phase8b_stress_test.py --integrity
```

**Failure Recovery (30 min)**

```bash
python3 backend/scripts/phase8b_stress_test.py --recovery
```

---

## 📊 Real-time Monitoring

### Terminal: Worker Status

```bash
python3 backend/scripts/monitor_workers.py --watch
```

### Terminal: Flower Dashboard

```bash
open http://localhost:5555
Login: admin / flower_password_change_me
```

### Terminal: PostgreSQL Audit Log

```bash
# Success rate by brand
psql postgresql://halilit_user@localhost:5432/halilit_tasks -c \
  "SELECT * FROM audit_brand_success_rate;"

# Recent failures
psql postgresql://halilit_user@localhost:5432/halilit_tasks -c \
  "SELECT * FROM recent_failures LIMIT 10;"

# Current queue status
psql postgresql://halilit_user@localhost:5432/halilit_tasks -c \
  "SELECT * FROM current_queue_depths;"
```

### Terminal: Redis Memory

```bash
redis-cli INFO memory

# Check key count
redis-cli DBSIZE

# Monitor in real-time
redis-cli MONITOR
```

---

## 📈 Performance Targets (Expected Results)

| Test       | Metric         | Target           | Status     |
| ---------- | -------------- | ---------------- | ---------- |
| Baseline   | v8.0 vs v7.6   | 15-30x faster    | ⏳ Pending |
| Stress 10  | Latency        | < 500ms avg      | ⏳ Pending |
| Stress 50  | Throughput     | 10+ tasks/sec    | ⏳ Pending |
| Stress 100 | Success rate   | > 99%            | ⏳ Pending |
| Integrity  | Duplicates     | 0 detected       | ⏳ Pending |
| Recovery   | Worker restart | < 2 min recovery | ⏳ Pending |

---

## 🔧 Troubleshooting

### "Connection refused" on API calls

```bash
# Check if FastAPI is running
curl http://localhost:8000/docs

# If not, restart
docker-compose restart fastapi
```

### "Redis connection error"

```bash
# Check Redis
docker-compose logs redis

# Restart
docker-compose restart redis
```

### "PostgreSQL connection error"

```bash
# Check database
docker-compose logs postgres

# Reset database
docker-compose down
docker-compose up -d postgres
python3 backend/config/init_db.sql  # Run schema
```

### "Tasks not progressing"

```bash
# Check if workers are running
python3 backend/scripts/monitor_workers.py

# Restart all workers
docker-compose restart worker_harvest worker_enrich_1 worker_enrich_2 worker_validate worker_learn
```

---

## 📋 Daily Test Checklist

**Morning (Pre-test)**

- [ ] Docker services healthy (health check passes)
- [ ] Flower dashboard accessible (localhost:5555)
- [ ] PostgreSQL database has clean schema
- [ ] Worker concurrency correct (see monitor_workers.py)
- [ ] Redis memory < 100MB

**During Test**

- [ ] Monitor worker CPU/memory in a separate terminal
- [ ] Check PostgreSQL query logs for errors
- [ ] Watch for Redis memory growth
- [ ] Keep Flower tab open for visual monitoring
- [ ] Note any anomalies in logs

**Evening (Post-test)**

- [ ] Collect metrics from logs/phase8b_metrics.json
- [ ] Export audit log: `SELECT * FROM task_audit_log INTO OUTFILE 'audit.csv'`
- [ ] Archive logs: `tar czf logs/day-N.tar.gz logs/*.log`
- [ ] Document any issues or observations
- [ ] Share metrics with team

---

## 🎯 Daily Test Template (Copy & Customize)

```markdown
# Day [N] Test Results

## Tests Run

- [ ] Baseline (15 min)
- [ ] Stress 10 (15 min)
- [ ] Stress 50 (15 min)
- [ ] Stress 100 (15 min)
- [ ] Integrity (10 min)

## Key Metrics

- **Baseline Improvement**: \_\_\_ x faster
- **p99 Latency (Stress 100)**: \_\_\_ ms
- **Throughput (Stress 100)**: \_\_\_ tasks/sec
- **Success Rate**: \_\_\_\_%
- **Duplicate Products**: \_\_\_
- **Worker Restarts**: \_\_\_

## Resource Used

- **Peak CPU**: \_\_\_\_%
- **Peak Memory**: \_\_\_\_%
- **Redis Memory**: \_\_\_ MB
- **PostgreSQL Connections**: \_\_\_

## Issues Encountered

- [ ] None
- [ ] [Describe issues]

## Recommendations

[Any changes needed?]

## Decision

- [ ] Continue to next level
- [ ] Fix and retry
- [ ] Escalate

**Tested by**: [Name]  
**Date**: [Date]  
**Status**: ✅ PASS / ⚠️ NEEDS REVIEW / ❌ FAILED
```

---

## 📞 Support & Escalation

**Log Locations**:

```
logs/
  ├── phase8b_metrics.json      # All metrics as JSON
  ├── celery-harvest.log        # Harvest worker
  ├── celery-enrich.log         # Enrich workers
  ├── celery-validate.log       # Validate worker
  └── docker-compose.log        # Docker output
```

**Quick Diagnostics**:

```bash
# View last 100 errors
tail -100 logs/*.log | grep ERROR

# Count by error type
grep ERROR logs/*.log | awk -F: '{print $NF}' | sort | uniq -c

# Export metrics
cat logs/phase8b_metrics.json | python3 -m json.tool
```

**When to Escalate**:

- More than 1% of tasks failing
- Database constraint violations
- Worker crashes without restart
- Memory usage > 2GB
- API response time > 10 seconds
- PostgreSQL showing deadlocks

---

## ✅ Success Criteria

**Go for Cutover** (All must pass):

- ✅ Baseline: v8.0 is 15x+ faster than v7.6
- ✅ Stress 100: > 99% success rate
- ✅ Stress 100: < 1s average latency
- ✅ Integrity: 0 duplicate products
- ✅ Recovery: Worker/Redis restart < 2 min
- ✅ Monitoring: All dashboards functional
- ✅ Documentation: Cutover runbook complete

**No-Go (Any failure triggers review)**:

- ❌ Data loss or corruption detected
- ❌ Success rate < 95% under stress
- ❌ Worker exhaustion or deadlock
- ❌ PostgreSQL connection pool exhausted
- ❌ Unable to recover from infrastructure failure

---

**Next**: After all tests pass, proceed to [Phase 8.0c: Gradual Cutover](PHASE_8.0c_GRADUAL_CUTOVER.md)
