"""
FastAPI Task Router for Halilit Support Center v8.5

Provides async HTTP endpoints for queuing and monitoring distributed tasks:
- POST /api/v8/tasks/harvest/{brand} - Queue harvest
- GET /api/v8/tasks/result/{task_id} - Get task result
- POST /api/v8/tasks/batch-sync - Start complete sync pipeline
- GET /api/v8/tasks/status/{task_id} - Real-time task status
- DELETE /api/v8/tasks/cancel/{task_id} - Cancel pending task
"""

from fastapi import APIRouter, HTTPException, Query
from celery.result import AsyncResult
from celery.exceptions import TimeoutError
from typing import Dict, List, Optional, Any
import uuid
import logging
from datetime import datetime

# Import Celery app and tasks
from backend.celery_config import celery_app
from backend.tasks import (
    harvest_brand_products,
    enrich_product,
    validate_product,
    record_learning_feedback,
    sync_brand_pipeline,
)

logger = logging.getLogger(__name__)

# Create router with v8 prefix
router = APIRouter(prefix="/api/v8/tasks", tags=["async-tasks-v8"])


# ============================================================================
# Response Models (Pydantic-based)
# ============================================================================

class TaskQueuedResponse:
    """Response when task is successfully queued"""

    def __init__(self, task_id: str, status: str, queue_name: str):
        self.task_id = task_id
        self.status = status
        self.queue_name = queue_name
        self.result_url = f'/api/v8/tasks/result/{task_id}'
        self.status_url = f'/api/v8/tasks/status/{task_id}'
        self.queued_at = datetime.utcnow().isoformat()


class TaskStatusResponse:
    """Real-time task status response"""

    def __init__(self, task_id: str, result: AsyncResult):
        self.task_id = task_id
        self.state = result.state
        self.ready = result.ready()
        self.successful = result.successful() if result.ready() else None
        self.failed = result.failed() if result.ready() else None

        # Progress data (PROGRESS state)
        if result.state == 'PROGRESS':
            self.progress = result.info.get(
                'status') if isinstance(result.info, dict) else None
            self.meta = result.info if isinstance(result.info, dict) else {}
        else:
            self.progress = None
            self.meta = {}

        # Result data (FAILURE, SUCCESS)
        if result.ready():
            if result.successful():
                try:
                    self.result = result.get(timeout=1)
                except TimeoutError:
                    self.result = None
            else:
                self.result = None
                self.error = str(
                    result.info) if result.info else 'Unknown error'
        else:
            self.result = None
            self.error = None


# ============================================================================
# HARVEST ENDPOINTS
# ============================================================================

@router.post("/harvest/{brand}")
async def queue_harvest(brand: str) -> Dict[str, Any]:
    """
    Queue a brand harvest task (CommercialScout).

    Returns immediately with task ID for polling/websocket updates.

    Path Parameters:
    - brand: Brand name (e.g., "Roland", "Yamaha")

    Response:
    {
        "task_id": "uuid-string",
        "status": "PENDING",
        "queue_name": "harvest",
        "result_url": "/api/v8/tasks/result/{task_id}",
        "status_url": "/api/v8/tasks/status/{task_id}",
        "queued_at": "2026-02-09T12:34:56.789123"
    }

    Example:
    $ curl -X POST http://localhost:8000/api/v8/tasks/harvest/Roland
    """
    try:
        task_id = str(uuid.uuid4())

        logger.info(
            f"📋 Queueing harvest for brand: {brand} (task_id={task_id})")

        # Queue task with explicit routing
        task = harvest_brand_products.apply_async(
            args=(brand, task_id),
            task_id=task_id,
            queue='harvest',
            priority=9,  # High priority
            retry=True,
            retry_policy={
                'max_retries': 3,
                'interval_start': 1,
                'interval_step': 0.2,
                'interval_max': 0.2,
            }
        )

        response = TaskQueuedResponse(
            task_id=task_id,
            status=task.state,
            queue_name='harvest'
        )

        return {
            'task_id': response.task_id,
            'status': response.status,
            'queue_name': response.queue_name,
            'result_url': response.result_url,
            'status_url': response.status_url,
            'queued_at': response.queued_at
        }

    except Exception as e:
        logger.error(f"❌ Failed to queue harvest: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to queue harvest: {str(e)}")


@router.get("/result/{task_id}")
async def get_harvest_result(task_id: str, poll_interval: int = Query(1, ge=1, le=60)) -> Dict[str, Any]:
    """
    Get harvest task result (blocking, with timeout).

    Path Parameters:
    - task_id: Task UUID

    Query Parameters:
    - poll_interval: Polling interval in seconds (default 1, max 60)

    Response:
    {
        "task_id": "uuid",
        "state": "SUCCESS|FAILURE|PENDING|PROGRESS",
        "result": {...} or null,
        "error": "error message" or null,
        "ready": true/false
    }

    Example:
    $ curl http://localhost:8000/api/v8/tasks/result/task-uuid-here
    """
    try:
        result = AsyncResult(task_id, app=celery_app)

        logger.debug(
            f"📊 Fetching result for task {task_id}: state={result.state}")

        response = TaskStatusResponse(task_id, result)

        return {
            'task_id': response.task_id,
            'state': response.state,
            'ready': response.ready,
            'successful': response.successful,
            'failed': response.failed,
            'result': response.result,
            'error': response.error,
            'progress': response.progress,
            'meta': response.meta
        }

    except Exception as e:
        logger.error(f"❌ Failed to fetch result: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch result: {str(e)}")


# ============================================================================
# BATCH SYNC ENDPOINTS
# ============================================================================

@router.post("/batch-sync")
async def queue_batch_sync(brand: str, product_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Queue a complete sync pipeline for a brand:
    Harvest → Enrich → Validate → Learn

    Query Parameters:
    - brand: Brand name to sync
    - product_ids: Optional list of specific product IDs to enrich (if not harvesting)

    Response:
    {
        "sync_id": "uuid",
        "brand": "brand-name",
        "workflow_id": "celery-task-id",
        "status": "queued",
        "stages": ["harvest", "enrich", "validate", "learn"],
        "queued_at": "2026-02-09T12:34:56.789123"
    }

    Example:
    $ curl -X POST "http://localhost:8000/api/v8/tasks/batch-sync?brand=Roland"
    """
    try:
        sync_id = str(uuid.uuid4())

        logger.info(
            f"🔗 Queueing batch sync for brand: {brand} (sync_id={sync_id})")

        # Use sync_brand_pipeline task to orchestrate the workflow
        task = sync_brand_pipeline.apply_async(
            args=(brand, sync_id),
            queue='default',
            priority=8,
        )

        return {
            'sync_id': sync_id,
            'brand': brand,
            'workflow_id': task.id,
            'status': 'queued',
            'stages': ['harvest', 'enrich', 'validate', 'learn'],
            'queued_at': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Failed to queue batch sync: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to queue batch sync: {str(e)}")


# ============================================================================
# STATUS MONITORING ENDPOINTS
# ============================================================================

@router.get("/status/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get real-time task status without blocking.

    Perfect for frontend polling or WebSocket updates.

    Path Parameters:
    - task_id: Task UUID

    Response:
    {
        "task_id": "uuid",
        "state": "PENDING|PROGRESS|SUCCESS|FAILURE|RETRY",
        "ready": false,
        "progress": "enriching" or null,
        "meta": {...}
    }

    States:
    - PENDING: Waiting in queue
    - PROGRESS: Currently processing
    - SUCCESS: Completed successfully
    - FAILURE: Failed (check error field)
    - RETRY: Retrying after failure

    Example:
    $ curl http://localhost:8000/api/v8/tasks/status/task-uuid-here
    """
    try:
        result = AsyncResult(task_id, app=celery_app)
        response = TaskStatusResponse(task_id, result)

        return {
            'task_id': response.task_id,
            'state': response.state,
            'ready': response.ready,
            'failed': response.failed,
            'progress': response.progress,
            'meta': response.meta,
            'queued_url': f'/api/v8/tasks/result/{task_id}'
        }

    except Exception as e:
        logger.error(f"❌ Failed to fetch status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch status: {str(e)}")


# ============================================================================
# TASK CONTROL ENDPOINTS
# ============================================================================

@router.delete("/cancel/{task_id}")
async def cancel_task(task_id: str) -> Dict[str, Any]:
    """
    Cancel a pending or running task.

    Note: Currently running tasks cannot be cancelled immediately
    (requires graceful shutdown implementation).

    Path Parameters:
    - task_id: Task UUID

    Response:
    {
        "task_id": "uuid",
        "cancelled": true/false,
        "state": "REVOKED" or current state
    }

    Example:
    $ curl -X DELETE http://localhost:8000/api/v8/tasks/cancel/task-uuid-here
    """
    try:
        task = AsyncResult(task_id, app=celery_app)

        if task.state == 'SUCCESS' or task.state == 'FAILURE':
            return {
                'task_id': task_id,
                'cancelled': False,
                'state': task.state,
                'error': 'Cannot cancel completed task'
            }

        # Revoke the task
        celery_app.control.revoke(task_id, terminate=True)

        logger.info(f"🛑 Cancelled task: {task_id}")

        return {
            'task_id': task_id,
            'cancelled': True,
            'state': 'REVOKED'
        }

    except Exception as e:
        logger.error(f"❌ Failed to cancel task: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to cancel task: {str(e)}")


# ============================================================================
# QUEUE STATS ENDPOINTS
# ============================================================================

@router.get("/health")
async def celery_health() -> Dict[str, Any]:
    """
    Check Celery broker and worker health.

    Response:
    {
        "broker": "connected|disconnected",
        "workers": {...},
        "queues": {...},
        "timestamp": "..."
    }

    Example:
    $ curl http://localhost:8000/api/v8/tasks/health
    """
    try:
        # Check broker connectivity
        inspect_result = celery_app.control.inspect()

        if inspect_result is None:
            return {
                'broker': 'disconnected',
                'workers': {},
                'queues': {},
                'error': 'No workers available',
                'timestamp': datetime.utcnow().isoformat()
            }

        # Get active workers
        stats = inspect_result.stats()
        active_workers = list(stats.keys()) if stats else []

        return {
            'broker': 'connected',
            'workers': {'active': len(active_workers), 'names': active_workers},
            'queues': {
                'harvest': 'enabled',
                'enrich': 'enabled',
                'validate': 'enabled',
                'learn': 'enabled',
                'default': 'enabled',
            },
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            'broker': 'error',
            'workers': {},
            'queues': {},
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }


# ============================================================================
# DEBUG ENDPOINTS (Development only)
# ============================================================================

@router.get("/debug/active-tasks")
async def debug_active_tasks() -> Dict[str, Any]:
    """
    [DEBUG] List all active/pending tasks across all workers.

    NOTE: Only enable in development!

    Example:
    $ curl http://localhost:8000/api/v8/tasks/debug/active-tasks
    """
    try:
        inspect_result = celery_app.control.inspect()

        if inspect_result is None:
            return {'error': 'No workers available'}

        active = inspect_result.active()

        return {
            'active_tasks': active,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Debug failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Expose router for inclusion in main FastAPI app
__all__ = ['router']
