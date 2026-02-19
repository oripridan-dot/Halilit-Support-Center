"""
Improvement Cycle Service — v2.0 (Multi-Disciplinary Task-Force Support)

Manages multi-round improvement cycles with shared Blackboard context,
per-round agent role assignments, and cycle rewind capability.
"""

import uuid
import json
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
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
        )
        state.responsible_agent = self._resolve_responsible(state)
        self._cycles[cycle_id] = state
        return state

    def advance_cycle(self, cycle_id: str) -> ImprovementCycleState:
        if cycle_id not in self._cycles:
            raise KeyError(f"Cycle {cycle_id!r} not found")
        state = self._cycles[cycle_id]
        if state.completed:
            raise ValueError(f"Cycle {cycle_id!r} is already completed")
        if state.current_round >= state.total_rounds:
            state.completed = True
        else:
            state.current_round += 1
        state.responsible_agent = self._resolve_responsible(state)
        return state

    def rewind_cycle(self, cycle_id: str, to_round: int) -> ImprovementCycleState:
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
        state.responsible_agent = self._resolve_responsible(state)
        return state

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
async def advance_cycle(cycle_id: str):
    """Advances the improvement cycle to the next round (or marks it completed)."""
    try:
        cycle_state = cycle_service.advance_cycle(cycle_id)
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


class RewindRequest(BaseModel):
    to_round: int = Field(..., ge=1, description="Round number to rewind to.")


@app.post("/cycles/{cycle_id}/rewind", response_model=CycleResponse)
async def rewind_cycle(cycle_id: str, request: RewindRequest):
    """
    Rewinds the cycle to a previous round.
    Used by the Watchdog to send work back to the Builder when it fails review.
    """
    try:
        cycle_state = cycle_service.rewind_cycle(cycle_id, request.to_round)
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
