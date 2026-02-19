import logging
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

# In-memory data store for improvement cycles
cycles = {}

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImprovementCycleState(BaseModel):
    cycle_id: str = Field(..., description="Unique identifier for the improvement cycle.")
    current_round: int = Field(1, ge=1, description="The current round of the cycle.")
    total_rounds: int = Field(5, ge=1, description="The total number of rounds in the cycle.")
    completed: bool = Field(False, description="Whether the cycle is completed.")


class StartCycleRequest(BaseModel):
    total_rounds: Optional[int] = Field(5, ge=1, description="The total number of rounds for the new cycle (optional). Defaults to 5.")


class CycleResponse(BaseModel):
    cycle_id: str = Field(..., description="Unique identifier for the improvement cycle.")
    current_round: int = Field(..., description="The current round of the cycle.")
    total_rounds: int = Field(..., description="The total number of rounds in the cycle.")
    completed: bool = Field(..., description="Whether the cycle is completed.")


@app.post("/cycles", status_code=201, response_model=CycleResponse)
async def start_cycle(request: Optional[StartCycleRequest] = None):
    """Starts a new improvement cycle."""
    cycle_id = str(uuid4())
    total_rounds = request.total_rounds if request else 5
    cycle = ImprovementCycleState(
        cycle_id=cycle_id,
        total_rounds=total_rounds,
        current_round=1,
        completed=False
    )
    cycles[cycle_id] = cycle
    logger.info(f"Started new cycle with id {cycle_id}, total rounds {total_rounds}")
    return CycleResponse(**cycle.dict())


@app.post("/cycles/{cycle_id}/advance", response_model=CycleResponse)
async def advance_cycle(cycle_id: str):
    """Advances the improvement cycle to the next round."""
    cycle = cycles.get(cycle_id)
    if not cycle:
        logger.warning(f"Cycle with id {cycle_id} not found")
        raise HTTPException(status_code=404, detail="Cycle not found")

    if cycle.completed:
        logger.warning(f"Cycle with id {cycle_id} is already completed")
        raise HTTPException(status_code=400, detail="Cycle is already completed")

    if cycle.current_round >= cycle.total_rounds:
        cycle.completed = True
        logger.info(f"Cycle with id {cycle_id} completed")
    else:
        cycle.current_round += 1
        logger.info(
            f"Advanced cycle with id {cycle_id} to round {cycle.current_round}")

    cycles[cycle_id] = cycle
    return CycleResponse(**cycle.dict())


@app.get("/cycles/{cycle_id}", response_model=CycleResponse)
async def get_cycle(cycle_id: str):
    """Retrieves the current state of the improvement cycle."""
    cycle = cycles.get(cycle_id)
    if not cycle:
        logger.warning(f"Cycle with id {cycle_id} not found")
        raise HTTPException(status_code=404, detail="Cycle not found")

    return CycleResponse(**cycle.dict())