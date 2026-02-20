"""
Improvement Cycle Service — v4.0 (Bio-Swarm + Mutation Engine Integration)
===========================================================================
Manages multi-round improvement cycles with shared Blackboard context,
per-round agent role assignments, cycle rewind capability, and real-time
Server-Sent Events (SSE) streaming for the Operator Console.

v4.0 upgrades:
  - Models defined inline (no circular import)
  - After each cycle completes, automatically triggers the Mutation Engine
    to analyse agent performance and evolve the swarm's DNA
  - Exposes /fitness endpoint to query the Fitness Ledger
  - POST /mutate to force a mutation event

Architecture Pillars:
  - Pillar 3 inner-loop: feedback_note carries error context between rounds.
  - Pillar 5 telemetry:  SSE endpoint /cycles/{id}/stream broadcasts live.
  - Pillar 6 evolution:  Mutation Engine fires when cycle completes.
"""

import asyncio
import uuid
import json
import logging
import time
from pathlib import Path
from typing import Optional, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent.parent
_SPECS_TEMP = _ROOT / "specs" / "temp"

# ---------------------------------------------------------------------------
# Data Models (defined here — avoid circular imports)
# ---------------------------------------------------------------------------

class StartCycleRequest(BaseModel):
    total_rounds: Optional[int] = Field(default=5, ge=1, le=20)
    goal: Optional[str] = Field(default="", description="Human-readable cycle goal")
    genome_id: Optional[str] = Field(default="", description="Optional genome ID")
    auto_mutate: bool = Field(default=True, description="Trigger Mutation Engine on completion")


class CycleResponse(BaseModel):
    cycle_id: str
    current_round: int
    total_rounds: int
    completed: bool
    goal: str = ""
    fitness_snapshot: dict = Field(default_factory=dict)


class ImprovementCycleState(BaseModel):
    cycle_id: str
    current_round: int = 0
    total_rounds: int = 5
    completed: bool = False
    goal: str = ""
    genome_id: str = ""
    auto_mutate: bool = True
    started_at: float = Field(default_factory=time.time)
    feedback_notes: list = Field(default_factory=list)

    def snapshot(self) -> dict:
        return {
            "cycle_id": self.cycle_id,
            "current_round": self.current_round,
            "total_rounds": self.total_rounds,
            "completed": self.completed,
            "goal": self.goal,
        }


# ---------------------------------------------------------------------------
# Blackboard helper
# ---------------------------------------------------------------------------

def create_blackboard(task_id: str, goal: str, agents: list) -> Path:
    """Create a Task-Force Blackboard markdown file in specs/temp/."""
    specs_temp = _ROOT / "specs" / "temp"
    specs_temp.mkdir(parents=True, exist_ok=True)
    bb_path = specs_temp / f"task_force_{task_id}.md"
    content = f"""# Task-Force Blackboard: {task_id}

**Goal:** {goal}
**Agents:** {', '.join(agents)}
**Status:** In Progress

---

## Round 1 — Steerer: Architecture Contract
*(pending)*

---

## Round 2 — Builder: Implementation Notes
*(pending)*

---

## Round 3 — Watchdog: Review & Feedback
*(pending)*

---

## API Contracts
*(agents append here)*

## Blockers / Escalations
*(agents append here)*
"""
    bb_path.write_text(content, encoding="utf-8")
    return bb_path


# ---------------------------------------------------------------------------
# In-Memory Store
# ---------------------------------------------------------------------------
cycle_store: dict = {}


# ---------------------------------------------------------------------------
# Mutation Engine integration (lazy import)
# ---------------------------------------------------------------------------

def _trigger_mutation_engine(since_ts: float, verbose: bool = False) -> list:
    try:
        import sys as _sys
        _factory_dir = _ROOT / "backend" / "factory"
        if str(_factory_dir) not in _sys.path:
            _sys.path.insert(0, str(_factory_dir))
        from mutation_engine import run_mutation_cycle  # noqa
        results = run_mutation_cycle(since_ts=since_ts, force_mutate=False, verbose=verbose)
        return [
            {"agent": r.agent, "heuristic": r.heuristic, "target": r.target,
             "confidence": r.confidence, "generation": r.generation}
            for r in results
        ]
    except Exception as exc:
        logging.getLogger(__name__).warning(f"Mutation Engine skipped: {exc}")
        return []


def _get_fitness_snapshot() -> dict:
    try:
        import sys as _sys
        _factory_dir = _ROOT / "backend" / "factory"
        if str(_factory_dir) not in _sys.path:
            _sys.path.insert(0, str(_factory_dir))
        from mutation_engine import FitnessLedger  # noqa
        ledger = FitnessLedger()
        return {
            af.agent: {"score": af.score, "generation": af.generation,
                       "runs": af.total_runs, "mutations": af.mutation_count}
            for af in ledger.all_agents()
        }
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class ImprovementCycleService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    async def start_cycle(self, request: StartCycleRequest) -> CycleResponse:
        total_rounds = request.total_rounds or 5
        cycle_id = str(uuid.uuid4())
        state = ImprovementCycleState(
            cycle_id=cycle_id, total_rounds=total_rounds,
            goal=request.goal or "", genome_id=request.genome_id or "",
            auto_mutate=request.auto_mutate,
        )
        cycle_store[cycle_id] = state
        self.logger.info(f"Started cycle {cycle_id} with {total_rounds} rounds")
        return CycleResponse(
            cycle_id=state.cycle_id, current_round=state.current_round,
            total_rounds=state.total_rounds, completed=state.completed,
            goal=state.goal, fitness_snapshot=_get_fitness_snapshot(),
        )

    async def advance_cycle(self, cycle_id: str, feedback_note: str = "") -> CycleResponse:
        if cycle_id not in cycle_store:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
        state = cycle_store[cycle_id]
        if state.completed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cycle already completed")
        if feedback_note:
            state.feedback_notes.append(feedback_note)
        state.current_round += 1
        if state.current_round >= state.total_rounds:
            state.completed = True
            self.logger.info(f"Cycle {cycle_id} COMPLETE")
            if state.auto_mutate:
                mutations = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: _trigger_mutation_engine(since_ts=state.started_at),
                )
                if mutations:
                    self.logger.info(f"  {len(mutations)} mutation(s) applied.")
        else:
            self.logger.info(f"Advanced cycle {cycle_id} to round {state.current_round}")
        return CycleResponse(
            cycle_id=state.cycle_id, current_round=state.current_round,
            total_rounds=state.total_rounds, completed=state.completed,
            goal=state.goal, fitness_snapshot=_get_fitness_snapshot(),
        )

    async def get_cycle_state(self, cycle_id: str) -> CycleResponse:
        if cycle_id not in cycle_store:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
        state = cycle_store[cycle_id]
        return CycleResponse(
            cycle_id=state.cycle_id, current_round=state.current_round,
            total_rounds=state.total_rounds, completed=state.completed,
            goal=state.goal, fitness_snapshot=_get_fitness_snapshot(),
        )

    async def rewind_cycle(self, cycle_id: str) -> CycleResponse:
        if cycle_id not in cycle_store:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
        state = cycle_store[cycle_id]
        if state.current_round > 0:
            state.current_round -= 1
            state.completed = False
        self.logger.info(f"Cycle {cycle_id} rewound to round {state.current_round}")
        return CycleResponse(
            cycle_id=state.cycle_id, current_round=state.current_round,
            total_rounds=state.total_rounds, completed=state.completed,
            goal=state.goal, fitness_snapshot=_get_fitness_snapshot(),
        )


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(title="Improvement Cycle Service", version="4.0.0")
service = ImprovementCycleService()


@app.post("/cycles", status_code=status.HTTP_201_CREATED, response_model=CycleResponse)
async def start_cycle_endpoint(request: StartCycleRequest):
    try:
        return await service.start_cycle(request)
    except HTTPException:
        raise
    except Exception as exc:
        logging.exception("Error starting cycle")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@app.post("/cycles/{cycle_id}/advance", response_model=CycleResponse)
async def advance_cycle_endpoint(cycle_id: str, feedback_note: str = ""):
    try:
        return await service.advance_cycle(cycle_id, feedback_note=feedback_note)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@app.post("/cycles/{cycle_id}/rewind", response_model=CycleResponse)
async def rewind_cycle_endpoint(cycle_id: str):
    try:
        return await service.rewind_cycle(cycle_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@app.get("/cycles/{cycle_id}", response_model=CycleResponse)
async def get_cycle_state_endpoint(cycle_id: str):
    try:
        return await service.get_cycle_state(cycle_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@app.get("/cycles/{cycle_id}/stream")
async def stream_cycle_events(cycle_id: str):
    """Pillar 5 — SSE: stream cycle state changes to the frontend."""
    if cycle_id not in cycle_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")

    async def event_generator():
        last_round = -1
        for _ in range(120):
            await asyncio.sleep(0.5)
            state = cycle_store.get(cycle_id)
            if state is None:
                break
            if state.current_round != last_round:
                last_round = state.current_round
                yield f"data: {json.dumps(state.snapshot())}\n\n"
            if state.completed:
                yield 'data: {"event": "completed"}\n\n'
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/fitness")
async def get_fitness_report():
    """Return current Fitness Ledger for all agents."""
    return _get_fitness_snapshot()


@app.post("/mutate")
async def force_mutation():
    """Force a Mutation Engine run outside of the normal OODA cycle."""
    mutations = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: _trigger_mutation_engine(since_ts=0, verbose=False),
    )
    return {"mutations_applied": len(mutations), "mutations": mutations}
