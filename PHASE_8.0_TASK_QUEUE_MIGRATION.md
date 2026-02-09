# Phase 8.0: Asynchronous Task Queue Migration
## Scaling the Trinity Swarm for 1,000+ Product Sync Operations

**Status**: Specification & Implementation Roadmap  
**Target Release**: v8.0  
**Estimated Effort**: 40-60 hours  
**Risk Level**: Medium (architectural change, but well-isolated)

---

## 📋 Executive Summary

The current FastAPI server processes batch product ingestions **synchronously**, which creates bottlenecks when syncing large catalogs (1,000+ products). This phase introduces **asynchronous task queue infrastructure** to:

- **Decouple** frontend requests from backend processing
- **Parallelize** agent work (Trinity Swarm agents run concurrently)
- **Improve** user feedback with real-time progress updates
- **Scale** to enterprise-grade throughput (100+ concurrent ingestions)

---

## 🔧 Architecture Overview

### Current State (Synchronous - v7.6)
```
Frontend Request
  ↓
[CommercialScout: Scrape] → Blocking (10-30s)
  ↓
[OfficialVerifier: Enrich] → Blocking (20-50s)
  ↓
[ExternalValidator: Audit] → Blocking (15-30s)
  ↓
Response to Frontend (60-110s total)
```

**Problems**:
- FastAPI server blocks during processing
- One product sync = one HTTP request lifecycle
- No persistence of state across failures
- Limited retry capability

### Proposed State (Asynchronous - v8.0)
```
Frontend Request → Queue Task (IMMEDIATE)
  ↓
Task Broker (Redis/Celery)
  ├─ [CommercialScout] (Worker 1)
  ├─ [OfficialVerifier] (Worker 2)
  ├─ [ExternalValidator] (Worker 3)
  └─ [Learning Feedback] (Worker 4)
  ↓
Persistent Result Storage
  ↓
Real-time Updates to Frontend (WebSocket/SSE)
```

**Benefits**:
- Non-blocking FastAPI endpoints
- Parallel processing of 100+ products
- Persistent task state & retry on failure
- Graceful error handling
- Production-grade reliability

---

## 📦 Technology Stack

### Task Queue & Broker
| Component | Selection | Rationale |
|-----------|-----------|-----------|
| **Message Broker** | Redis | Fast, supports priority queues, in-memory with persistence |
| **Task Queue** | Celery | Mature, distributed, supports worker scaling |
| **Result Backend** | PostgreSQL + Redis | Durability + speed for task results |
| **Monitoring** | Flower | Celery monitoring dashboard |

### Infrastructure Requirements
```yaml
Services:
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes: [redis_data:/data]

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: halilit_tasks
      POSTGRES_PASSWORD: secure_password
    volumes: [postgres_data:/var/lib/postgresql/data]

  flower:
    image: mher/flower
    ports: ["5555:5555"]
    environment:
      CELERY_BROKER_URL: redis://redis:6379/0
```

---

## 🏗️ Implementation Plan

### Phase 8.0a: Infrastructure Setup (Week 1)

#### Step 1: Install Dependencies
```bash
pip install celery==5.3.0 redis==5.0.0 flower==2.0.1
```

#### Step 2: Create Celery Configuration
**File**: `backend/celery_config.py`
```python
import os
from celery import Celery
from kombu import Exchange, Queue

# Initialize Celery application
celery_app = Celery('halilit')

# Configuration
celery_app.conf.update(
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task configuration
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3400,  # 56 min soft limit
    
    # Routing
    task_routes={
        'backend.tasks.harvest.*': {'queue': 'harvest'},
        'backend.tasks.enrich.*': {'queue': 'enrich'},
        'backend.tasks.validate.*': {'queue': 'validate'},
        'backend.tasks.learn.*': {'queue': 'learn'},
    },
    
    # Queues
    task_queues=(
        Queue('harvest', Exchange('tasks'), routing_key='harvest.*'),
        Queue('enrich', Exchange('tasks'), routing_key='enrich.*'),
        Queue('validate', Exchange('tasks'), routing_key='validate.*'),
        Queue('learn', Exchange('tasks'), routing_key='learn.*'),
        Queue('default'),
    ),
)
```

#### Step 3: Create Task Definitions
**File**: `backend/tasks.py`
```python
from celery import shared_task, Task
from celery_config import celery_app
from backend.unified_agent_orchestrator_v76 import CommercialAgent, OfficialAgent, ContextualAgent
import logging

logger = logging.getLogger(__name__)

class AgentTask(Task):
    """Base task with error handling and logging"""
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        logger.warning(f"Task {task_id} retrying after {exc}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed: {exc}")

@shared_task(base=AgentTask, bind=True)
def harvest_brand_products(self, brand: str, task_id: str) -> dict:
    """
    Harvest products from Halilit for a brand.
    
    Args:
        brand: Brand name (e.g., "Roland")
        task_id: Unique task identifier for tracking
    
    Returns:
        List of ProductDraft objects from CommercialScout
    """
    try:
        self.update_state(state='PROGRESS', meta={'status': 'harvesting', 'brand': brand})
        
        agent = CommercialAgent()
        products = agent.harvest(brand)
        
        logger.info(f"✅ Harvested {len(products)} products for {brand}")
        return {
            'status': 'success',
            'brand': brand,
            'product_count': len(products),
            'products': products
        }
    except Exception as e:
        logger.error(f"❌ Harvest failed for {brand}: {e}")
        raise

@shared_task(base=AgentTask, bind=True)
def enrich_product(self, product_draft: dict, learned_insights: list = None) -> dict:
    """
    Enrich a product with official specs and documentation.
    
    Args:
        product_draft: Raw product data from CommercialScout
        learned_insights: Insights from learning system
    
    Returns:
        Enriched product with official data
    """
    try:
        self.update_state(state='PROGRESS', meta={'status': 'enriching'})
        
        agent = OfficialAgent()
        enriched = agent.enrich(product_draft, learned_insights)
        
        return {
            'status': 'success',
            'enriched_product': enriched
        }
    except Exception as e:
        logger.error(f"❌ Enrichment failed: {e}")
        raise

@shared_task(base=AgentTask, bind=True)
def validate_product(self, product: dict) -> dict:
    """
    Validate and audit a product for compliance & quality.
    
    Args:
        product: Complete product data
    
    Returns:
        AuditReport with risk score
    """
    try:
        self.update_state(state='PROGRESS', meta={'status': 'validating'})
        
        agent = ContextualAgent()
        audit_report = agent.audit(product)
        
        return {
            'status': 'success',
            'audit_report': audit_report.model_dump()
        }
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        raise

@shared_task
def record_learning_feedback(product_id: str, feedback: dict) -> dict:
    """Record feedback for learning system"""
    return {'status': 'success', 'product_id': product_id}
```

### Phase 8.0b: FastAPI Integration (Week 2)

#### Step 1: Create Task Endpoints
**File**: `backend/api/task_router.py`
```python
from fastapi import APIRouter, BackgroundTasks
from celery.result import AsyncResult
from backend.tasks import harvest_brand_products, enrich_product, validate_product
import uuid

router = APIRouter(prefix="/api/tasks", tags=["async-tasks"])

@router.post("/harvest/{brand}")
async def queue_harvest(brand: str):
    """Queue a brand harvest task"""
    task_id = str(uuid.uuid4())
    task = harvest_brand_products.apply_async(
        args=(brand, task_id),
        task_id=task_id,
        queue='harvest'
    )
    
    return {
        'task_id': task_id,
        'status': task.state,
        'result_url': f'/api/tasks/result/{task_id}'
    }

@router.get("/result/{task_id}")
async def get_task_result(task_id: str):
    """Get task result and status"""
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        'task_id': task_id,
        'status': result.state,
        'result': result.result if result.ready() else None,
        'progress': result.info if result.state == 'PROGRESS' else None
    }

@router.post("/batch-sync")
async def queue_batch_sync(brand: str, product_ids: list = None):
    """
    Queue a complete sync pipeline for products:
    Harvest → Enrich → Validate
    """
    task_chain = [
        harvest_brand_products.s(brand),
        enrich_product.s(),  # Input from previous task
        validate_product.s(),
    ]
    
    workflow = celery.chain(task_chain)
    result = workflow.apply_async(queue='default')
    
    return {
        'workflow_id': result.id,
        'status': 'queued',
        'stages': ['harvest', 'enrich', 'validate']
    }
```

#### Step 2: WebSocket for Real-time Updates
**File**: `backend/api/websocket_manager.py`
```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Set
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
    
    async def connect(self, task_id: str, websocket: WebSocket):
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)
    
    async def disconnect(self, task_id: str, websocket: WebSocket):
        if task_id in self.active_connections:
            self.active_connections[task_id].remove(websocket)
    
    async def broadcast_task_update(self, task_id: str, update: dict):
        """Send task progress update to all connected clients"""
        if task_id in self.active_connections:
            for connection in self.active_connections[task_id]:
                try:
                    await connection.send_json(update)
                except Exception as e:
                    print(f"WebSocket broadcast error: {e}")

manager = ConnectionManager()

@app.websocket("/ws/task/{task_id}")
async def websocket_task_monitor(websocket: WebSocket, task_id: str):
    await manager.connect(task_id, websocket)
    try:
        while True:
            # Poll task status and send updates
            result = AsyncResult(task_id)
            update = {
                'task_id': task_id,
                'status': result.state,
                'progress': result.info,
                'timestamp': datetime.now().isoformat()
            }
            
            await manager.broadcast_task_update(task_id, update)
            await asyncio.sleep(1)  # Poll every second
    except WebSocketDisconnect:
        await manager.disconnect(task_id, websocket)
```

### Phase 8.0c: Worker Configuration (Week 2)

#### Worker Startup Scripts
**File**: `backend/run_workers.sh`
```bash
#!/bin/bash

# Start Celery workers for each queue
celery -A backend.celery_config worker \
  --loglevel=info \
  --queues=harvest \
  --concurrency=4 \
  --hostname=harvest-worker@%h &

celery -A backend.celery_config worker \
  --loglevel=info \
  --queues=enrich \
  --concurrency=6 \
  --hostname=enrich-worker@%h &

celery -A backend.celery_config worker \
  --loglevel=info \
  --queues=validate \
  --concurrency=4 \
  --hostname=validate-worker@%h &

# Start Flower monitoring
celery -A backend.celery_config flower \
  --port=5555 \
  --broker=redis://localhost:6379/0 &

wait
```

---

## 🚦 Migration Strategy

### Stage 1: Parallel Run (v7.6 + v8.0)
- Keep existing synchronous endpoints
- Add new async endpoints alongside
- Run both in production for 2-4 weeks
- Monitor for issues

### Stage 2: Gradual Cutover (v8.0a)
- Redirect 10% of traffic to async
- Monitor performance & error rates
- Gradually increase to 100%

### Stage 3: Legacy Cleanup (v8.0b)
- Remove old synchronous endpoints
- Consolidate to queue-based pipeline

---

## 📊 Performance Expectations

### Throughput Improvement
| Metric | v7.6 (Sync) | v8.0 (Async) | Gain |
|--------|-----------|-------------|------|
| 1 product | 90 seconds | 90 seconds* | - |
| 100 products | 9,000 seconds (2.5h) | 300 seconds (5m) | **30x** |
| 1,000 products | 90,000 seconds (25h) | 2,000 seconds (33m) | **45x** |

*Latency per product unchanged; throughput scales with workers

### Resource Efficiency
| Resource | v7.6 | v8.0 |
|----------|------|------|
| FastAPI Worker RAM | 500 MB | 300 MB (non-blocking) |
| Peak CPU | 100% (blocked) | 40% (async) |
| Concurrent Products | ~2 | ~100+ |

---

## ⚠️ Risk Mitigation

### Potential Issues & Mitigations

| Issue | Mitigation |
|-------|-----------|
| Redis/Celery outage | Fallback to sync mode; persistent queues in PostgreSQL |
| Task timeout | Implement checkpoints; allow resumable tasks |
| Memory leaks in workers | Configure worker recycling; memory monitoring |
| Task duplication | Idempotency keys in database; deduplication logic |

---

## 🔄 Backward Compatibility

- **v8.0 supports both** sync and async clients
- Frontend can use either endpoint
- Gradual migration path for consuming services

---

## 📝 Acceptance Criteria

- [ ] Redis + Celery running in Docker Compose
- [ ] Task endpoints responding with task IDs
- [ ] WebSocket real-time updates functioning
- [ ] Worker concurrency handling 100+ tasks
- [ ] Retry logic tested and working
- [ ] Flower dashboard operational
- [ ] Performance tests showing 30x+ improvement
- [ ] Zero data loss during processing
- [ ] All unit + integration tests passing

---

## 🎯 Success Metrics

By end of Phase 8.0:
- ✅ Sync 1,000 products in < 1 hour (vs 25h currently)
- ✅ Support 100+ concurrent ingestions
- ✅ < 1% task failure rate with auto-retry
- ✅ Full observability via Flower + logs

---

## 📚 Additional Resources

- [Celery Documentation](https://docs.celeryproject.io/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Redis Best Practices](https://redis.io/docs/management/persistence/)
- [Task Queue Architecture Patterns](https://martinfowler.com/articles/patterns-of-distributed-systems/)

---

## 📞 Questions & Next Steps

1. **Should we start with Phase 8.0a infrastructure?** → Recommend yes; provides foundation
2. **What's the timeline?** → 4-6 weeks for full rollout
3. **Fallback plan if something breaks?** → Revert to sync endpoints; no data loss

---

**Document Version**: 8.0-spec-20260209  
**Last Updated**: February 9, 2026  
**Next Review**: After Phase 7.7 completion (mid-February 2026)
