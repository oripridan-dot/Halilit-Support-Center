# backend/api/streams.py

import asyncio
import json
import logging
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from backend.unified_learning_system_v76 import LearningSystem

logger = logging.getLogger("LearningStream")
router = APIRouter()
ls = LearningSystem()


@router.get("/api/stream/learning")
async def stream_learning_updates(request: Request):
    """
    SSE Endpoint that streams new insights from the Learning System 
    as they are discovered during bulk processing.
    """
    logger.info("🆕 Client connected to learning stream")

    async def event_generator():
        # Track the last insight we sent to avoid duplicates
        last_seen_id = None

        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                logger.info("👋 Client disconnected from learning stream")
                break

            try:
                # 1. Poll the Learning System for the latest insight
                latest_insight = ls.get_most_recent_insight()

                if latest_insight:
                    # Use a unique identifier for the insight if available, else construct a simple hash/id
                    insight_id = latest_insight.get(
                        'pattern_id') or latest_insight.get('insight')

                    if insight_id != last_seen_id:
                        last_seen_id = insight_id

                        logger.info(
                            f"📡 Pushing insight: {latest_insight.get('brand')} - {latest_insight.get('insight')[:30]}...")

                        # 2. Format the payload for the Zustand store
                        yield {
                            "event": "message",
                            "data": json.dumps({
                                "type": "LEARNING_INSIGHT",
                                "brand": latest_insight.get('brand'),
                                "insight": latest_insight.get('insight'),
                                "timestamp": latest_insight.get('created_at'),
                                # Using pattern_id as key
                                "productId": latest_insight.get('pattern_id')
                            })
                        }
            except Exception as e:
                logger.error(f"Error in stream generator: {e}")

            # Wait briefly before polling again to save CPU
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
