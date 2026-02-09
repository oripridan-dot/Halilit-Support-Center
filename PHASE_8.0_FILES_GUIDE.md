# Phase 8.0 Infrastructure Files Guide

This guide documents all files created/modified for Phase 8.0 (Async Task Queue Migration).

---

## 🎯 Quick Navigation

**New Endpoints**: See `backend/api/task_router.py`  
**Start Infrastructure**: Run `bash backend/scripts/setup_infrastructure.sh`  
**Monitor Workers**: Run `python3 backend/scripts/monitor_workers.py`  
**Run Tests**: Run `python3 backend/tests/test_parallel_v7_v8.py`  
**Full Documentation**: See `PHASE_8.0_TASK_QUEUE_MIGRATION.md` and `PHASE_8.0_QUICK_START.md`

---

## 📁 File Reference

### Core Infrastructure

#### `backend/celery_config.py` (160 lines)

**Purpose**: Celery application configuration  
**What it does**:

- Initializes Celery app with Redis broker
- Configures result backend (Redis)
- Defines task routing (harvest/enrich/validate/learn queues)
- Sets up retry policies & time limits
- Configures worker prefetch & acknowledgment settings

**Key Functions**:

- `celery_app`: Global Celery application instance
- `health_check()`: Check broker connectivity

**Used by**: All workers and FastAPI endpoints

---

#### `backend/tasks.py` (420 lines)

**Purpose**: Celery task definitions  
**What it does**:

- Defines distributed tasks for Trinity Swarm agents
- Implements retry logic & error handling
- Provides progress tracking for long-running tasks

**Key Tasks**:

- `harvest_brand_products()`: CommercialScout agent task
- `enrich_product()`: OfficialVerifier agent task
- `validate_product()`: ExternalValidator agent task
- `record_learning_feedback()`: Learning system task
- `sync_brand_pipeline()`: Full pipeline orchestration

**Error Handling**:

- Automatic retry (3x with exponential backoff)
- Soft time limits (56 min) with graceful timeouts
- Hard time limits (1h) for safety
- Detailed error logging

---

### FastAPI Integration

#### `backend/api/task_router.py` (380 lines)

**Purpose**: FastAPI endpoints for async task management  
**What it does**:

- Exposes REST API endpoints for queuing tasks
- Provides result retrieval & status monitoring
- Includes task cancellation & health checks
- Debug endpoints for development

**Endpoints**:

```
POST   /api/v8/tasks/harvest/{brand}      Queue harvest
GET    /api/v8/tasks/result/{task_id}     Get result (blocking)
GET    /api/v8/tasks/status/{task_id}     Get status (non-blocking)
POST   /api/v8/tasks/batch-sync           Queue full pipeline
DELETE /api/v8/tasks/cancel/{task_id}     Cancel task
GET    /api/v8/tasks/health               Broker health
WS     /api/v8/tasks/debug/active-tasks   Debug info
```

**Integration**: Include router in `backend/server.py`:

```python
from backend.api.task_router import router as task_router
app.include_router(task_router)
```

---

#### `backend/api/websocket_manager.py` (330 lines)

**Purpose**: Real-time WebSocket updates for tasks  
**What it does**:

- Manages WebSocket connections
- Broadcasts task status updates to subscribers
- Implements connection pooling
- Handles client disconnections gracefully

**WebSocket Endpoint**:

```
WS /ws/tasks/{task_id}
```

**Message Format**:

```json
{
  "type": "task_status",
  "task_id": "uuid",
  "data": {
    "state": "PROGRESS",
    "progress": "enriching",
    "meta": {...}
  },
  "timestamp": "2026-02-09T12:34:56.789123"
}
```

**Key Classes**:

- `TaskConnectionManager`: Manages all WebSocket connections
- `connection_manager`: Global instance (use in routes)

---

### Docker & Infrastructure

#### `docker-compose.yml` (200 lines)

**Purpose**: Complete development/production stack  
**Services**:

- `redis`: Message broker & cache (Redis 7-alpine)
- `postgres`: Results backend & audit log (PostgreSQL 15-alpine)
- `flower`: Worker monitoring dashboard (Flower 2.0)
- `worker_harvest`: Web scraping worker (concurrency=2)
- `worker_enrich_1`, `worker_enrich_2`: Agent processing workers (concurrency=3 each)
- `worker_validate`: Compliance audit worker (concurrency=2)
- `worker_learn`: Learning system worker (concurrency=1)

**Key Features**:

- Health checks for each service
- Volume persistence for Redis & PostgreSQL
- Flexible environment configuration
- Logging configuration (10MB max per file)

**Usage**:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f <service_name>

# Stop all
docker-compose down
```

---

#### `Dockerfile` (25 lines)

**Purpose**: Container image for workers & API  
**What it does**:

- Builds on Python 3.11-slim
- Installs system dependencies
- Installs Python packages from requirements.txt
- Sets working directory & Python path

**Build**:

```bash
docker build -t halilit:v8.0 .
```

---

#### `backend/config/init_db.sql` (140 lines)

**Purpose**: PostgreSQL initialization script  
**What it does**:

- Creates tables for task results
- Sets up audit logging tables
- Initializes enrichment history tracking
- Creates learning feedback tables
- Defines monitoring metrics tables
- Creates useful views (success rate, recent failures, etc.)

**Key Tables**:

- `celery_taskmeta`: Celery result storage
- `task_audit_log`: Task execution audit trail
- `product_enrichment_history`: Enrichment tracking
- `learning_feedback`: User corrections & learnings
- `worker_health_metrics`: Worker performance data
- `sync_progress`: Real-time sync progress tracking

**Usage**:

```bash
# Auto-initialized by docker-compose
# Or manually:
psql postgresql://user@localhost/halilit_tasks < backend/config/init_db.sql
```

---

### Scripts & Tools

#### `backend/scripts/start_workers.sh` (120 lines)

**Purpose**: Start Celery workers locally  
**What it does**:

- Validates Redis connectivity
- Sets up Python environment
- Starts 4 specialized workers (or 1 combined worker)
- Logs worker processes & PIDs

**Modes**:

```bash
# 4 specialized workers (recommended)
bash backend/scripts/start_workers.sh

# Single combined worker
bash backend/scripts/start_workers.sh --single-worker

# Debug logging
bash backend/scripts/start_workers.sh --debug
```

**Output**: Shows worker names, PIDs, and Flower dashboard URL

---

#### `backend/scripts/monitor_workers.py` (350 lines)

**Purpose**: Real-time worker monitoring & health checks  
**What it does**:

- Displays active workers & their status
- Shows queue assignments
- Tracks active tasks
- Checks for alert conditions
- Supports continuous monitoring

**Modes**:

```bash
# One-time snapshot
python3 backend/scripts/monitor_workers.py

# Continuous monitoring (updates every 5 seconds)
python3 backend/scripts/monitor_workers.py --watch

# Export as JSON
python3 backend/scripts/monitor_workers.py --json
```

**Output Fields**:

- Worker name & status (ACTIVE/IDLE)
- Pool concurrency & active tasks
- Assigned queues
- Alert conditions

---

#### `backend/scripts/setup_infrastructure.sh` (190 lines)

**Purpose**: One-command infrastructure setup  
**What it does**:

- Checks Docker/Docker Compose availability
- Creates .env file if missing
- Starts Redis, PostgreSQL, Flower in Docker
- Waits for services to be healthy
- Installs Python dependencies
- Optionally starts workers

**Modes**:

```bash
# Full setup (services + dependencies + workers)
bash backend/scripts/setup_infrastructure.sh

# Services only (no workers)
bash backend/scripts/setup_infrastructure.sh --services

# Start workers only
bash backend/scripts/setup_infrastructure.sh --workers

# Stop all services
bash backend/scripts/setup_infrastructure.sh --stop
```

**Output**: Lists service endpoints (Redis, PostgreSQL, Flower URLs)

---

### Testing

#### `backend/tests/test_parallel_v7_v8.py` (480 lines)

**Purpose**: Parallel validation of v7.6 vs v8.0  
**What it does**:

- Runs harvest/enrich/validate on both versions simultaneously
- Compares accuracy (product count match)
- Measures performance delta
- Generates detailed comparison reports
- Saves results to JSON

**Classes**:

- `V76TestRunner`: Runs synchronous agents (baseline)
- `V80TestRunner`: Runs async Celery tasks
- `TestCoordinator`: Orchestrates parallel execution
- `ExecutionMetrics`: Tracks operation metrics
- `ComparisonResult`: Compares v7.6 vs v8.0

**Usage**:

```bash
# Test 3 brands
python3 backend/tests/test_parallel_v7_v8.py \
  --brands "Roland,Yamaha,Korg"

# Perf testing mode
python3 backend/tests/test_parallel_v7_v8.py \
  --mode=perf \
  --timeout=300

# Results saved to logs/test_results_v7_v8.json
```

**Output**: Comparison table + JSON report

---

### Configuration

#### `.env.example`

**Purpose**: Environment variable template  
**Variables**:

- Celery broker & result backend URLs
- PostgreSQL credentials
- Flower authentication
- API server settings
- Gemini API key
- Worker concurrency settings
- Feature flags

**Usage**:

```bash
cp .env.example .env
# Edit .env with your values
```

---

## 🔄 Data Flow Architecture

```
User Request (Web/API)
  ↓
FastAPI Server (backend/server.py)
  ↓
Task Router (/api/v8/tasks/*)
  ├─ Validate input
  ├─ Generate task_id (UUID)
  ├─ Queue to Redis via Celery
  └─ Return {task_id, status_url, result_url}
  ↓
Redis Broker (in-memory queue)
  ├─ harvest queue
  ├─ enrich queue
  ├─ validate queue
  └─ learn queue
  ↓
Celery Workers (specialized)
  ├─ Worker A (harvest): CommercialScout.harvest()
  ├─ Worker B (enrich): OfficialVerifier.enrich()
  ├─ Worker C (validate): ExternalValidator.audit()
  └─ Worker D (learn): LearningSystem.record()
  ↓
Result Storage
  ├─ Redis: Fast cache (1h TTL)
  └─ PostgreSQL: Persistent store + audit log
  ↓
Client Polling / WebSocket
  ├─ GET /api/v8/tasks/result/{task_id}
  └─ WS /ws/tasks/{task_id}
```

---

## 📊 Queue Routing Strategy

| Queue    | Worker            | Task                       | Concurrency | Purpose                            |
| -------- | ----------------- | -------------------------- | ----------- | ---------------------------------- |
| harvest  | harvest_worker    | harvest_brand_products()   | 2           | Web scraping (rate-limit friendly) |
| enrich   | enrich_worker 1-2 | enrich_product()           | 3 each      | Gemini agent processing            |
| validate | validate_worker   | validate_product()         | 2           | Compliance auditing                |
| learn    | learn_worker      | record_learning_feedback() | 1           | Background learning system         |
| feedback | learn_worker      | (same worker)              | 1           | User feedback collection           |
| default  | learn_worker      | fallback                   | 1           | Any unrouted tasks                 |

**Total Capacity**: ~11 concurrent tasks (horizontally scalable)

---

## 🔌 Integration Checklist

To fully integrate Phase 8.0 into the application:

- [ ] Include `task_router` in `backend/server.py`
- [ ] Add WebSocket route in `backend/server.py`
- [ ] Update frontend to use new `/api/v8/tasks/*` endpoints
- [ ] Add WebSocket client to frontend for real-time updates
- [ ] Update frontend product sync flow to use new async API
- [ ] Add task status UI (progress bars, completion indicators)
- [ ] Document API changes for consuming services
- [ ] Set up Flower dashboard access
- [ ] Create runbooks for common troubleshooting scenarios
- [ ] Plan gradual cutover from v7.6 sync endpoints

---

## 🎓 Learning Resources

**Celery**:

- [Official Docs](https://docs.celeryproject.io/)
- [Best Practices](https://docs.celeryproject.io/en/stable/getting-started/first-steps-with-celery.html)

**Redis**:

- [Redis CLI](https://redis.io/commands/)
- [Persistence Guide](https://redis.io/docs/management/persistence/)

**Task Queues**:

- [Martin Fowler: Task Queue Pattern](https://martinfowler.com/articles/patterns-of-distributed-systems/)
- [Scaling with Queues](https://www.youtube.com/watch?v=8lzJvAI4N5A)

---

## 📞 Support & Questions

If you encounter issues:

1. **Check logs**: `docker-compose logs <service>`
2. **Monitor status**: `python3 backend/scripts/monitor_workers.py`
3. **Review docs**: `PHASE_8.0_TASK_QUEUE_MIGRATION.md`
4. **Run tests**: `python3 backend/tests/test_parallel_v7_v8.py`

---

**Last Updated**: February 9, 2026  
**Phase**: 8.0a (Infrastructure) ✅ Complete  
**Next**: 8.0b (Performance Validation) ⏳ Feb 17, 2026
