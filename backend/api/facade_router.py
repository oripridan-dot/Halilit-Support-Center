"""
Facade Router — FastAPI Router
================================
Mounts the Facade Agent at POST /facade/mandate inside the existing FastAPI app (backend/server.py).

Wired in via:
  from backend.api.facade_router import router as facade_router
  app.include_router(facade_router, prefix="/facade", tags=["Facade"])
"""

import os
import logging
from fastapi import APIRouter
from local_autonomy.facade_agent import MandateRequest, MandateResponse, receive_mandate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/mandate",
    response_model=MandateResponse,
    summary="Submit a mandate to TooLoo Core via the Facade",
)
async def facade_mandate(request: MandateRequest) -> MandateResponse:
    """
    Receive a plain-English mandate and forward it to TooLoo Core.

    **Dev mode** (FACADE_DEV_MODE=true, the default):
    - Logs the mandate
    - Forwards directly to TooLoo Core at TOOLOO_CORE_URL/api/mandate
    - Returns TooLoo's response, or a 'queued' status if TooLoo Core is offline

    **Production mode** (future — when metering is enabled):
    - Classifies the mandate (Level-1 / Medium / Architectural)
    - Calculates token cost estimate and returns a quote
    - Governor approves → Stripe charges → TooLoo Core is invoked
    """
    logger.info(f"[FacadeRouter] POST /facade/mandate — '{request.mandate[:60]}...'")
    return await receive_mandate(request)


@router.get("/status", summary="Facade health and mode status")
async def facade_status():
    """Returns the current Facade configuration and operational mode."""
    return {
        "status": "ok",
        "dev_mode": os.environ.get("FACADE_DEV_MODE", "true").lower() in ("1", "true", "yes"),
        "tooloo_core_url": os.environ.get("TOOLOO_CORE_URL", "http://localhost:8001"),
        "version": "0.1.0-scaffold",
        "endpoints": {
            "mandate": "POST /facade/mandate",
            "status": "GET /facade/status",
        },
    }
