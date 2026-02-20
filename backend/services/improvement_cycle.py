"""
Improvement Cycle Service — v3.0 (Autonomous Loop + SSE Telemetry)

Manages multi-round improvement cycles with shared Blackboard context,
per-round agent role assignments, cycle rewind capability, and real-time
Server-Sent Events (SSE) streaming for the Operator Console.

Architecture Pillars:
  - Pillar 3 inner-loop: feedback_note carries error context between rounds.
  - Pillar 5 telemetry:  SSE endpoint /cycles/{id}/stream; EventBus broadcasts
    state changes so the frontend "Factory Diagnostics" view updates live.
"""

import asyncio
import uuid
import json
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent.parent
_SPECS_TEMP = _ROOT / "specs" / "temp"

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------
from backend.services import (
    ImprovementCycleState,
    StartCycleRequest,
    CycleResponse,
)

# ---------------------------------------------------------------------------
# In-Memory Data Store (Temporary)
# ---------------------------------------------------------------------------
cycle_store = {}

# ---------------------------------------------------------------------------
# Service Implementation
# ---------------------------------------------------------------------------
class ImprovementCycleService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def start_cycle(self, request: StartCycleRequest) -> CycleResponse:
        total_rounds = request.total_rounds if request.total_rounds else 5
        cycle_id = str(uuid.uuid4())
        state = ImprovementCycleState(
            cycle_id=cycle_id, total_rounds=total_rounds
        )
        cycle_store[cycle_id] = state
        self.logger.info(f"Started cycle {cycle_id} with {total_rounds} rounds")
        return CycleResponse(
            cycle_id=state.cycle_id,
            current_round=state.current_round,
            total_rounds=state.total_rounds,
            completed=state.completed,
        )

    async def advance_cycle(self, cycle_id: str) -> CycleResponse:
        if cycle_id not in cycle_store:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")

        state: ImprovementCycleState = cycle_store[cycle_id]

        if state.completed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cycle is already completed")

        if state.current_round < state.total_rounds:
            state.current_round += 1
            if state.current_round == state.total_rounds:
                state.completed = True
            self.logger.info(f"Advanced cycle {cycle_id} to round {state.current_round}")
            return CycleResponse(
                cycle_id=state.cycle_id,
                current_round=state.current_round,
                total_rounds=state.total_rounds,
                completed=state.completed,
            )
        else:
            state.completed = True
            self.logger.info(f"Cycle {cycle_id} completed")
            return CycleResponse(
                cycle_id=state.cycle_id,
                current_round=state.current_round,
                total_rounds=state.total_rounds,
                completed=state.completed,
            )

    async def get_cycle_state(self, cycle_id: str) -> CycleResponse:
        if cycle_id not in cycle_store:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")

        state: ImprovementCycleState = cycle_store[cycle_id]
        self.logger.info(f"Retrieved state for cycle {cycle_id}")
        return CycleResponse(
            cycle_id=state.cycle_id,
            current_round=state.current_round,
            total_rounds=state.total_rounds,
            completed=state.completed,
        )

# ---------------------------------------------------------------------------
# FastAPI App Integration
# ---------------------------------------------------------------------------
app = FastAPI()
service = ImprovementCycleService()

@app.post("/cycles", status_code=status.HTTP_201_CREATED, response_model=CycleResponse)
async def start_cycle_endpoint(request: StartCycleRequest):
    try:
        return await service.start_cycle(request)
    except Exception as e:
        logging.exception("Error starting cycle")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.post("/cycles/{cycle_id}/advance", response_model=CycleResponse)
async def advance_cycle_endpoint(cycle_id: str):
    try:
        return await service.advance_cycle(cycle_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.exception("Error advancing cycle")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/cycles/{cycle_id}", response_model=CycleResponse)
async def get_cycle_state_endpoint(cycle_id: str):
    try:
        return await service.get_cycle_state(cycle_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.exception("Error getting cycle state")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))