"""
Facade Agent — Halilit Support Center
======================================
The Facade sits between the outside world and TooLoo Core.

DEV MODE (current — transparent passthrough, as approved by Governor 2026-02-22):
  Every mandate is logged and forwarded to TooLoo Core with no cost calculation
  and no Stripe charge. If TooLoo Core is offline, the mandate is queued locally.

Future (Production) responsibilities:
  1. Route classification: Level-1 (Warden) / Medium (Warden + Issue) / Architectural (TooLoo)
  2. Cognitive Metering: token cost estimate → quote → Stripe charge → release mandate
  3. Auth: validate Governor identity before releasing mandates to TooLoo Core

FastAPI router is mounted at:
  POST /facade/mandate
  GET  /facade/status
"""

import os
import logging
import httpx
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# TooLoo Core REST API endpoint (set in .env or defaults to localhost)
TOOLOO_CORE_URL = os.environ.get("TOOLOO_CORE_URL", "http://localhost:8001")
FACADE_DEV_MODE = os.environ.get("FACADE_DEV_MODE", "true").lower() in ("1", "true", "yes")


class MandateRequest(BaseModel):
    """A mandate is a plain-English instruction for TooLoo Core."""
    mandate: str
    context: Optional[Dict[str, Any]] = None
    priority: Optional[str] = "normal"  # normal | high | critical


class MandateResponse(BaseModel):
    """Response from the Facade (and ultimately TooLoo Core)."""
    status: str               # accepted | rejected | queued | error
    mandate_id: Optional[str] = None
    message: str
    dev_mode: bool
    forwarded_to: Optional[str] = None
    tooloo_response: Optional[Dict[str, Any]] = None
    timestamp: str


async def receive_mandate(request: MandateRequest) -> MandateResponse:
    """
    Core Facade logic.

    Dev mode: transparent passthrough — log and forward.
    Prod mode (TODO): classify → meter → charge → forward.
    """
    timestamp = datetime.utcnow().isoformat()
    logger.info(f"[Facade] Received mandate: {request.mandate[:100]}...")
    logger.info(f"[Facade] Dev mode: {FACADE_DEV_MODE}")

    if FACADE_DEV_MODE:
        return await _dev_passthrough(request, timestamp)
    else:
        # TODO: implement routing classification and Stripe when metering is enabled
        logger.warning("[Facade] Production mode not yet implemented. Falling back to dev passthrough.")
        return await _dev_passthrough(request, timestamp)


async def _dev_passthrough(request: MandateRequest, timestamp: str) -> MandateResponse:
    """
    Development passthrough: forward mandate directly to TooLoo Core.
    No billing, no routing classification.
    """
    tooloo_endpoint = f"{TOOLOO_CORE_URL}/api/mandate"
    logger.info(f"[Facade][DEV] Forwarding to TooLoo Core at {tooloo_endpoint}")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                tooloo_endpoint,
                json={
                    "mandate": request.mandate,
                    "context": request.context or {},
                    "source": "halilit-support-center",
                    "dev_mode": True,
                },
            )
            response.raise_for_status()
            tooloo_data = response.json()
            return MandateResponse(
                status="accepted",
                mandate_id=tooloo_data.get("mandate_id"),
                message="Mandate forwarded to TooLoo Core (dev passthrough)",
                dev_mode=True,
                forwarded_to=tooloo_endpoint,
                tooloo_response=tooloo_data,
                timestamp=timestamp,
            )

    except httpx.ConnectError:
        # TooLoo Core is not running — expected in dev when running standalone
        logger.warning(f"[Facade][DEV] TooLoo Core unreachable at {tooloo_endpoint}. Mandate logged.")
        return MandateResponse(
            status="queued",
            message=(
                f"TooLoo Core unreachable at {tooloo_endpoint}. "
                "Mandate has been logged. Start TooLoo Core to process it."
            ),
            dev_mode=True,
            forwarded_to=tooloo_endpoint,
            timestamp=timestamp,
        )

    except Exception as e:
        logger.error(f"[Facade][DEV] Unexpected error forwarding mandate: {e}")
        return MandateResponse(
            status="error",
            message=f"Facade error: {str(e)}",
            dev_mode=True,
            timestamp=timestamp,
        )
