import uuid
import logging
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

# Assuming the project structure places these files as specified
from backend.services.improvement_cycle import ImprovementCycleService

# Data Models - Directly from the specification
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

# Initialize FastAPI app and service
app = FastAPI()
cycle_service = ImprovementCycleService()

# Configure logging (basic console logging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Endpoints

@app.post("/cycles", status_code=status.HTTP_201_CREATED, response_model=CycleResponse)
async def start_cycle(request: StartCycleRequest):
    """Starts a new improvement cycle."""
    try:
        total_rounds = request.total_rounds
        if total_rounds is None:
            total_rounds = 5  # Default value as per the spec
        cycle_state = cycle_service.start_cycle(total_rounds)
        return cycle_state
    except ValueError as e:
        logger.error(f"Bad Request: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error starting cycle: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


@app.post("/cycles/{cycle_id}/advance", response_model=CycleResponse)
async def advance_cycle(cycle_id: str):
    """Advances the improvement cycle to the next round."""
    try:
        cycle_state = cycle_service.advance_cycle(cycle_id)
        return cycle_state
    except KeyError:
        logger.warning(f"Cycle not found: {cycle_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
    except ValueError as e:
        logger.error(f"Bad Request: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error advancing cycle: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@app.get("/cycles/{cycle_id}", response_model=CycleResponse)
async def get_cycle(cycle_id: str):
    """Retrieves the current state of the improvement cycle."""
    try:
        cycle_state = cycle_service.get_cycle(cycle_id)
        return cycle_state
    except KeyError:
        logger.warning(f"Cycle not found: {cycle_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
    except Exception as e:
        logger.exception(f"Unexpected error retrieving cycle: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")