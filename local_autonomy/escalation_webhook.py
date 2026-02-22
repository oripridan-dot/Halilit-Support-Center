"""
Escalation Webhook — Halilit Support Center
=============================================
Fires an HTTP webhook to TooLoo Core when the Warden encounters an issue
that exceeds its autonomous repair capability.

Escalation levels (TOOLOO_MASTER_PLAN.md Chapter 2):
  Level-1  (< 50 lines)    → Warden fixes autonomously — no webhook
  Medium   (50-500 lines)  → Warden opens GitHub Issue [Needs Review] — no webhook
  Arch/P0  (> 500 lines    → THIS module fires: POST to TooLoo Core
           or architectural)

TooLoo Core endpoint: {TOOLOO_CORE_URL}/api/escalation
Payload schema: { source, issue_summary, severity, context, timestamp }
"""

import os
import logging
import httpx
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

TOOLOO_CORE_URL = os.environ.get("TOOLOO_CORE_URL", "http://localhost:8001")
ESCALATION_ENDPOINT = f"{TOOLOO_CORE_URL}/api/escalation"


async def fire_escalation(
    issue_summary: str,
    severity: str = "architectural",
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Fire an escalation webhook to TooLoo Core.

    Args:
        issue_summary: Plain-English description of the problem.
        severity: one of 'medium' | 'architectural' | 'p0'
        context: Optional dict with error traces, module paths, relevant file contents, etc.

    Returns:
        TooLoo Core acknowledgement response, or an error dict if unreachable.
    """
    payload = {
        "source": "halilit-support-center",
        "issue_summary": issue_summary,
        "severity": severity,
        "context": context or {},
        "timestamp": datetime.utcnow().isoformat(),
    }

    logger.warning(f"[Escalation] Firing to TooLoo Core [{severity}]: {issue_summary[:80]}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(ESCALATION_ENDPOINT, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info(f"[Escalation] TooLoo Core acknowledged: {result}")
            return {"status": "sent", "tooloo_response": result}

    except httpx.ConnectError:
        logger.error(
            f"[Escalation] TooLoo Core unreachable at {ESCALATION_ENDPOINT}. "
            "Start TooLoo Core to process this escalation."
        )
        return {
            "status": "queued",
            "message": f"TooLoo Core unreachable at {ESCALATION_ENDPOINT}.",
            "payload": payload,
        }

    except Exception as e:
        logger.error(f"[Escalation] Unexpected error: {e}")
        return {"status": "error", "error": str(e), "payload": payload}
