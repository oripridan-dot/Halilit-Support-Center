"""
API Router for Enhanced Pipeline Management

Provides REST endpoints for:
- Triggering pipeline runs (background or synchronous)
- Checking pipeline health and status
- Viewing run history and telemetry
- Managing the AI response cache
- Viewing available catalog snapshots

All endpoints are prefixed with /api/pipeline.

Usage:
    # In server.py:
    from backend.api.pipeline_router import router as pipeline_router
    app.include_router(pipeline_router, tags=["Pipeline"])
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("PipelineRouter")

router = APIRouter(prefix="/api/pipeline", tags=["Pipeline"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class PipelineRunRequest(BaseModel):
    """Request to trigger a pipeline run."""
    brand: Optional[str] = Field(
        None, description="Brand name to process (looks up URLs from Golden List)"
    )
    urls: Optional[List[str]] = Field(
        None, description="Specific URLs to harvest"
    )
    force_harvest: bool = Field(
        False, description="Force re-fetch even if fingerprints say unchanged"
    )
    skip_images: bool = Field(
        False, description="Skip image optimization phase"
    )


class PipelineRunResponse(BaseModel):
    """Response from triggering a pipeline run."""
    run_id: str
    status: str
    message: str


# ---------------------------------------------------------------------------
# Lazy singleton — don't import at module level to avoid circular imports
# ---------------------------------------------------------------------------

_pipeline = None


def _get_pipeline():
    """Lazy-init the enhanced pipeline singleton."""
    global _pipeline
    if _pipeline is None:
        from backend.ingestion.enhanced_pipeline import get_enhanced_pipeline
        _pipeline = get_enhanced_pipeline()
    return _pipeline


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/run", response_model=PipelineRunResponse)
async def trigger_pipeline_run(
    request: PipelineRunRequest,
    background_tasks: BackgroundTasks,
):
    """
    Trigger a pipeline run in the background.

    The pipeline will execute all 7 phases asynchronously.
    Use GET /api/pipeline/status to check progress.
    """
    pipeline = _get_pipeline()

    def _run():
        try:
            result = pipeline.run(
                brand=request.brand,
                urls=request.urls,
                force_harvest=request.force_harvest,
                skip_images=request.skip_images,
                trigger="api",
            )
            logger.info(
                f"Background pipeline completed: "
                f"{result.get('products_out', 0)} products"
            )
        except Exception as e:
            logger.error(f"Background pipeline failed: {e}")

    background_tasks.add_task(_run)

    return PipelineRunResponse(
        run_id="pending",
        status="started",
        message=(
            f"Pipeline run started in background"
            f"{' for brand: ' + request.brand if request.brand else ''}"
        ),
    )


@router.post("/run/sync")
async def trigger_pipeline_run_sync(request: PipelineRunRequest):
    """
    Trigger a pipeline run synchronously (waits for completion).

    WARNING: This blocks the request until the pipeline finishes.
    Use /run for background execution in production.
    """
    pipeline = _get_pipeline()

    try:
        result = pipeline.run(
            brand=request.brand,
            urls=request.urls,
            force_harvest=request.force_harvest,
            skip_images=request.skip_images,
            trigger="api_sync",
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def pipeline_status():
    """
    Get pipeline health and component status.

    Returns:
    - Pipeline health (healthy/degraded/unhealthy)
    - Last run info
    - Cache stats and size
    - Harvest stats
    - Phase performance averages
    """
    pipeline = _get_pipeline()
    return pipeline.get_status()


@router.get("/history")
async def pipeline_history(
    limit: int = Query(
        10, ge=1, le=100, description="Number of runs to return"),
):
    """Get recent pipeline run history."""
    pipeline = _get_pipeline()
    return {
        "runs": pipeline.get_history(limit=limit),
        "total_available": len(pipeline.telemetry._runs),
    }


@router.get("/health")
async def pipeline_health():
    """
    Quick health check endpoint.

    Returns a simple status suitable for monitoring/load balancers.
    """
    pipeline = _get_pipeline()
    health = pipeline.telemetry.get_health_status()
    return {
        "status": health.get("status", "unknown"),
        "last_success": health.get("last_success"),
        "recent_success_rate": health.get("recent_success_rate"),
    }


@router.get("/cache/stats")
async def cache_stats():
    """Get AI response cache statistics."""
    pipeline = _get_pipeline()
    return {
        "stats": pipeline.ai_cache.get_stats(),
        "size": pipeline.ai_cache.get_cache_size(),
    }


@router.post("/cache/clear")
async def clear_cache(
    operation: Optional[str] = Query(
        None, description="Operation namespace to clear (e.g., 'enrich'). Omit to clear all."
    ),
):
    """Clear AI response cache entries."""
    pipeline = _get_pipeline()
    pipeline.ai_cache.clear(operation=operation)
    return {
        "status": "cleared",
        "operation": operation or "all",
    }


@router.get("/snapshots")
async def list_snapshots():
    """List available catalog snapshots for rollback."""
    pipeline = _get_pipeline()
    return {
        "snapshots": pipeline.publisher.get_available_snapshots(),
    }


@router.post("/rollback")
async def rollback_catalog(
    version: Optional[str] = Query(
        None, description="Version to rollback to. Omit for latest snapshot."
    ),
):
    """Rollback catalog to a previous version."""
    pipeline = _get_pipeline()
    success = pipeline.publisher.rollback(target_version=version)
    if success:
        return {"status": "rolled_back", "version": version or "latest"}
    raise HTTPException(
        status_code=404,
        detail="No snapshot available for rollback",
    )


@router.get("/phase-averages")
async def phase_averages(
    limit: int = Query(
        10, ge=1, le=50, description="Number of runs to average"),
):
    """Get average performance metrics per pipeline phase."""
    pipeline = _get_pipeline()
    return pipeline.telemetry.get_phase_averages(limit=limit)
