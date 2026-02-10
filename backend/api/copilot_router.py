"""
CopilotKit Chat Router — Placeholder

Currently non-functional. CopilotKit integration requires:
1. pip install copilotkit
2. Wiring Trinity Swarm agents into the SDK
3. Frontend <CopilotKit> provider

This router gracefully degrades when copilotkit is not installed.
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

try:
    from copilotkit.integrations.fastapi import CopilotKitSDK

    sdk = CopilotKitSDK(agents=[], commands={})

    @router.post("/copilot/chat")
    async def chat(request: Request):
        return await sdk.handle_request(request)

    logger.info("CopilotKit SDK loaded (no agents configured yet)")
except ImportError:
    logger.info("CopilotKit not installed — chat endpoint disabled")

    @router.post("/copilot/chat")
    async def chat_unavailable(request: Request):
        return JSONResponse(
            status_code=503,
            content={"error": "CopilotKit not installed",
                     "status": "unavailable"}
        )
