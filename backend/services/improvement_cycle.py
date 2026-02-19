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


class ImprovementCycleState(BaseModel):
    cycle_id: str = Field(...,
                          description="Unique identifier for the improvement cycle.")
    current_round: int = Field(
        1, ge=1, description="The current round of the cycle.")
    total_rounds: int = Field(
        3, ge=1, description="The total number of rounds in the cycle.")
    completed: bool = Field(
        False, description="Whether the cycle is completed.")
    # Task-Force extensions
    blackboard_file: str = Field(
        "", description="Path to the shared Blackboard context file for this cycle.")
    round_roles: list[str] = Field(
        default_factory=lambda: ["steerer", "builder", "watchdog"],
        description="Which agent role is responsible for each round (index = round-1)."
    )
    responsible_agent: str = Field(
        "", description="Agent role responsible for the CURRENT round.")
    # Pillar 3: feedback_note carries error context from sandbox → next Builder round
    feedback_note: str = Field(
        "", description="Error or feedback injected into the next round's Builder context.")
    # Pillar 5: telemetry phase for the Operator Console live view
    telemetry_status: str = Field(
        "idle",
        description="Phase: idle | planning | building | verifying | reviewing | done | failed"
    )
    # --- v9.7.0 Autonomy (canonical aliases used by Task Force dispatcher) ---
    active_agent: Optional[str] = Field(
        None,
        description="Agent currently assigned to this round (alias for responsible_agent; "
                    "set by the task_force dispatcher)."
    )
    error_context: Optional[str] = Field(
        None,
        description="Raw AST/Compiler error fed into the current round (alias for feedback_note; "
                    "populated by the Sandbox executor after a compile failure)."
    )


class StartCycleRequest(BaseModel):
    total_rounds: Optional[int] = Field(
        3, ge=1, description="The total number of rounds for the new cycle (optional). Defaults to 3.")
    # Task-Force extensions (optional — plain improve cycles don't need them)
    blackboard_file: Optional[str] = Field(
        "", description="Path to the shared Blackboard file (set by task_force dispatcher).")
    round_roles: Optional[list[str]] = Field(
        default=None,
        description="Agent roles per round. Defaults to ['steerer', 'builder', 'watchdog']."
    )


class CycleResponse(BaseModel):
    cycle_id: str = Field(...,
                          description="Unique identifier for the improvement cycle.")
    current_round: int = Field(...,
                               description="The current round of the cycle.")
    total_rounds: int = Field(...,
                              description="The total number of rounds in the cycle.")
    completed: bool = Field(..., description="Whether the cycle is completed.")
    blackboard_file: str = Field(
        "", description="Path to the Blackboard file.")
    round_roles: list[str] = Field(default_factory=list)
    responsible_agent: str = Field(
        "", description="Agent responsible for the current round.")
    feedback_note: str = Field(
        "", description="Error or feedback note for the next round.")
    telemetry_status: str = Field(
        "idle", description="Current pipeline phase.")
    active_agent: Optional[str] = Field(
        None, description="Agent assigned to the current round.")
    error_context: Optional[str] = Field(
        None, description="Compiler/runtime error for the current round.")


# ---------------------------------------------------------------------------
# SSE Event Bus (Pillar 5 — Real-Time Telemetry)
# ---------------------------------------------------------------------------

class EventBus:
    """
    In-process publish/subscribe bus for Server-Sent Events.

    Each cycle gets its own subscriber queue. Subscribers are async generators
    that yield SSE-formatted strings when events arrive.

    Usage::
        bus = EventBus()
        bus.publish(cycle_id, {"status": "building", "round": 2})
        async for event in bus.subscribe(cycle_id):
            ...  # FastAPI StreamingResponse
    """

    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue]] = {}

    def _get_queues(self, cycle_id: str) -> list[asyncio.Queue]:
        return self._queues.setdefault(cycle_id, [])

    def publish(self, cycle_id: str, payload: dict) -> None:
        """Publish an event to all subscribers of a cycle (thread-safe via call_soon_threadsafe)."""
        data = json.dumps(payload)
        for q in list(self._get_queues(cycle_id)):
            try:
                # asyncio.Queue.put_nowait works from sync code if we're in the right loop
                q.put_nowait(data)
            except asyncio.QueueFull:
                pass  # drop if consumer is slow

    async def subscribe(self, cycle_id: str, timeout: float = 300.0):
        """
        Async generator that yields SSE-formatted event strings.
        Automatically removes itself from the queue list on disconnect.
        """
        q: asyncio.Queue = asyncio.Queue(maxsize=50)
        self._get_queues(cycle_id).append(q)
        try:
            import time as _time
            deadline = _time.monotonic() + timeout
            while True:
                remaining = max(0.0, deadline - _time.monotonic())
                if remaining <= 0:
                    yield "data: {\"type\": \"timeout\"}\n\n"
                    break
                try:
                    data = await asyncio.wait_for(q.get(), timeout=min(remaining, 30.0))
                    yield f"data: {data}\n\n"
                    # Send a keepalive comment every 25 s even if no events
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            queues = self._get_queues(cycle_id)
            if q in queues:
                queues.remove(q)


_event_bus = EventBus()


# ---------------------------------------------------------------------------
# In-process cycle registry (no external DB required)
# ---------------------------------------------------------------------------

class ImprovementCycleService:
    """
    Manages active improvement cycles in memory.
    Each cycle tracks its round, total rounds, and optional Task-Force metadata.
    """

    def __init__(self) -> None:
        self._cycles: dict[str, ImprovementCycleState] = {}

    def _resolve_responsible(self, state: ImprovementCycleState) -> str:
        roles = state.round_roles
        if roles and len(roles) >= state.current_round:
            return roles[state.current_round - 1]
        return ""

    def _emit(self, state: ImprovementCycleState) -> None:
        """Broadcast the current state to SSE subscribers (Pillar 5)."""
        _event_bus.publish(state.cycle_id, {
            "cycle_id": state.cycle_id,
            "round": state.current_round,
            "total": state.total_rounds,
            "agent": state.responsible_agent,
            "status": state.telemetry_status,
            "completed": state.completed,
            "feedback": state.feedback_note[:200] if state.feedback_note else "",
        })

    def start_cycle(
        self,
        total_rounds: int = 3,
        blackboard_file: str = "",
        round_roles: list[str] | None = None,
    ) -> ImprovementCycleState:
        if total_rounds < 1:
            raise ValueError("total_rounds must be >= 1")
        roles = round_roles or ["steerer", "builder", "watchdog"]
        cycle_id = str(uuid.uuid4())
        state = ImprovementCycleState(
            cycle_id=cycle_id,
            current_round=1,
            total_rounds=total_rounds,
            completed=False,
            blackboard_file=blackboard_file,
            round_roles=roles,
            telemetry_status="planning",
        )
        state.responsible_agent = self._resolve_responsible(state)
        self._cycles[cycle_id] = state
        self._emit(state)
        return state

    def advance_cycle(
        self,
        cycle_id: str,
        feedback_note: str = "",
        telemetry_status: str = "",
    ) -> ImprovementCycleState:
        """Advance to the next round.  Optionally carry a feedback_note (error text)
        into the next round for the Builder to act on (Pillar 3)."""
        if cycle_id not in self._cycles:
            raise KeyError(f"Cycle {cycle_id!r} not found")
        state = self._cycles[cycle_id]
        if state.completed:
            raise ValueError(f"Cycle {cycle_id!r} is already completed")
        if state.current_round >= state.total_rounds:
            state.completed = True
            state.telemetry_status = "done"
        else:
            state.current_round += 1
            if telemetry_status:
                state.telemetry_status = telemetry_status
        state.feedback_note = feedback_note
        state.responsible_agent = self._resolve_responsible(state)
        self._emit(state)
        return state

    def rewind_cycle(self, cycle_id: str, to_round: int, feedback_note: str = "") -> ImprovementCycleState:
        """Rewinds the cycle to a previous round (e.g. Watchdog → back to Builder)."""
        if cycle_id not in self._cycles:
            raise KeyError(f"Cycle {cycle_id!r} not found")
        state = self._cycles[cycle_id]
        if state.completed:
            raise ValueError(f"Cannot rewind a completed cycle ({cycle_id!r})")
        if to_round < 1 or to_round > state.current_round:
            raise ValueError(
                f"to_round must be between 1 and {state.current_round}, got {to_round}"
            )
        state.current_round = to_round
        state.completed = False
        state.feedback_note = feedback_note
        state.telemetry_status = "building"  # rewound → back to building
        state.responsible_agent = self._resolve_responsible(state)
        self._emit(state)
        return state

    def set_telemetry_status(self, cycle_id: str, status: str) -> None:
        """Update the telemetry_status without advancing the round. Emits SSE event."""
        if cycle_id not in self._cycles:
            return
        self._cycles[cycle_id].telemetry_status = status
        self._emit(self._cycles[cycle_id])

    def get_cycle(self, cycle_id: str) -> ImprovementCycleState:
        if cycle_id not in self._cycles:
            raise KeyError(f"Cycle {cycle_id!r} not found")
        return self._cycles[cycle_id]


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

# Initialize FastAPI app and service
app = FastAPI()
cycle_service = ImprovementCycleService()

# Configure logging (basic console logging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------


@app.post("/cycles", status_code=status.HTTP_201_CREATED, response_model=CycleResponse)
async def start_cycle(request: StartCycleRequest):
    """Starts a new improvement cycle (optionally with Task-Force metadata)."""
    try:
        total_rounds = request.total_rounds or 3
        cycle_state = cycle_service.start_cycle(
            total_rounds=total_rounds,
            blackboard_file=request.blackboard_file or "",
            round_roles=request.round_roles,
        )
        return cycle_state
    except ValueError as e:
        logger.error(f"Bad Request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error starting cycle: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred.")


@app.post("/cycles/{cycle_id}/advance", response_model=CycleResponse)
async def advance_cycle(cycle_id: str, request: Optional["AdvanceRequest"] = None):
    """
    Advances the improvement cycle to the next round (or marks it completed).

    Accepts an optional JSON body::

        { "feedback_note": "Your code failed with: ...", "telemetry_status": "building" }

    The feedback_note is stored on the state so the next Builder round can
    read it as error context (Pillar 3 — Autonomous Execution Sandbox).
    """
    try:
        note = request.feedback_note if request else ""
        ts = request.telemetry_status if request else ""
        cycle_state = cycle_service.advance_cycle(
            cycle_id, feedback_note=note, telemetry_status=ts)
        return cycle_state
    except KeyError:
        logger.warning(f"Cycle not found: {cycle_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
    except ValueError as e:
        logger.error(f"Bad Request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error advancing cycle: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred.")


class AdvanceRequest(BaseModel):
    feedback_note: str = Field(
        "", description="Error text or feedback for the next Builder round.")
    telemetry_status: str = Field(
        "", description="Optional phase label update.")


# Forward-reference resolution (used by Optional["AdvanceRequest"] above)
advance_cycle.__annotations__["request"] = Optional[AdvanceRequest]


class RewindRequest(BaseModel):
    to_round: int = Field(..., ge=1, description="Round number to rewind to.")
    feedback_note: str = Field(
        "", description="Gatekeeper rejection notes for the Builder.")


@app.post("/cycles/{cycle_id}/rewind", response_model=CycleResponse)
async def rewind_cycle(cycle_id: str, request: RewindRequest):
    """
    Rewinds the cycle to a previous round.
    Used by the Watchdog/Gatekeeper to send work back to the Builder when it fails review.
    Carries an optional feedback_note so the Builder knows exactly what to fix.
    """
    try:
        cycle_state = cycle_service.rewind_cycle(
            cycle_id, request.to_round, feedback_note=request.feedback_note
        )
        return cycle_state
    except KeyError:
        logger.warning(f"Cycle not found: {cycle_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
    except ValueError as e:
        logger.error(f"Bad Request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error rewinding cycle: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred.")


@app.get("/cycles/{cycle_id}", response_model=CycleResponse)
async def get_cycle(cycle_id: str):
    """Retrieves the current state of the improvement cycle."""
    try:
        cycle_state = cycle_service.get_cycle(cycle_id)
        return cycle_state
    except KeyError:
        logger.warning(f"Cycle not found: {cycle_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
    except Exception as e:
        logger.exception(f"Unexpected error retrieving cycle: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred.")


@app.get("/cycles/{cycle_id}/stream")
async def stream_cycle(cycle_id: str):
    """
    Server-Sent Events stream for a cycle (Pillar 5 — Real-Time Telemetry).

    Connect from the frontend::

        const src = new EventSource(`/cycles/${id}/stream`);
        src.onmessage = (e) => console.log(JSON.parse(e.data));

    Each event is a JSON object matching CycleResponse shape.
    """
    # Verify cycle exists before streaming
    try:
        cycle_service.get_cycle(cycle_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")

    async def _generator():
        async for chunk in _event_bus.subscribe(cycle_id):
            yield chunk

    return StreamingResponse(
        _generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/cycles/{cycle_id}/telemetry")
async def update_telemetry(cycle_id: str, body: dict):
    """
    Lightweight endpoint to update the telemetry_status without advancing the round.
    Agents call this to push live phase updates to the Operator Console.

    Body: { "status": "verifying" }
    """
    new_status = body.get("status", "")
    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing 'status' field")
    try:
        cycle_service.set_telemetry_status(cycle_id, new_status)
        return {"ok": True, "status": new_status}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ---------------------------------------------------------------------------
# Blackboard helpers (used by Task-Force dispatcher in nexus.py)
# ---------------------------------------------------------------------------

def create_blackboard(task_id: str, goal: str, agents: list[str]) -> Path:
    """
    Creates the shared Blackboard Markdown file for a Task-Force.
    Returns the absolute path to the file.
    """
    _SPECS_TEMP.mkdir(parents=True, exist_ok=True)
    bb_path = _SPECS_TEMP / f"task_force_{task_id}.md"
    content = f"""# Task-Force Blackboard: {task_id}

**Goal:** {goal}
**Agents:** {', '.join(agents)}

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
