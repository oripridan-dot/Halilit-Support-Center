# Spec: Improvement Process Cycle - Backend Service
**Target:** backend/services/improvement_cycle.py

## Overview
This service manages the lifecycle of an improvement process, consisting of a defined number of rounds. The service provides endpoints to start, advance, and retrieve the status of an improvement cycle. This service will interact with a hypothetical data source (to be defined later, stubbed as an in-memory data structure) to persist the state of the cycle. The number of rounds is configurable upon cycle initiation.

## Requirements
- The service must allow starting a new improvement cycle with a specified number of rounds (defaulting to 5).
- The service must track the current round of the improvement cycle.
- The service must provide an endpoint to advance to the next round.
- Advancing beyond the final round should result in an error.
- The service must provide an endpoint to retrieve the current round and total number of rounds of the improvement cycle.
- The service should handle concurrent requests gracefully.
- The cycle state should be persisted between requests. We will use a simple in-memory data structure for now, but a proper database backend will need to be integrated later.
- The service must include comprehensive error handling and logging.

## Data Contract

**Pydantic Models:**

```python
from pydantic import BaseModel, Field
from typing import Optional

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
```

**API Endpoints:**

- **POST /cycles**: Starts a new improvement cycle.
  - Request Body: `StartCycleRequest`
  - Response Body: `CycleResponse` (with the initial state)
  - Status Codes:
    - 201 Created: Cycle started successfully.
    - 400 Bad Request: Invalid input data.

- **POST /cycles/{cycle_id}/advance**: Advances the improvement cycle to the next round.
  - Request Body: None
  - Response Body: `CycleResponse` (with the updated state)
  - Status Codes:
    - 200 OK: Cycle advanced successfully.
    - 404 Not Found: Cycle with the specified ID not found.
    - 400 Bad Request: Cycle is already completed.

- **GET /cycles/{cycle_id}**: Retrieves the current state of the improvement cycle.
  - Request Body: None
  - Response Body: `CycleResponse`
  - Status Codes:
    - 200 OK: Cycle state retrieved successfully.
    - 404 Not Found: Cycle with the specified ID not found.

## Behavior Scenarios

- **Scenario:** Start a new improvement cycle with default rounds.
  - Input: `POST /cycles` with empty request body.
  - Outcome: A new cycle is created with `total_rounds = 5` and `current_round = 1`.  The `CycleResponse` is returned with a unique `cycle_id`.

- **Scenario:** Start a new improvement cycle with a specified number of rounds.
  - Input: `POST /cycles` with `StartCycleRequest = {"total_rounds": 3}`.
  - Outcome: A new cycle is created with `total_rounds = 3` and `current_round = 1`. The `CycleResponse` is returned with a unique `cycle_id`.

- **Scenario:** Advance the cycle to the next round.
  - Input: `POST /cycles/{cycle_id}/advance` (where `{cycle_id}` is a valid cycle ID) and the current round is 1.
  - Outcome: The `current_round` is incremented to 2 and the `CycleResponse` is returned with the updated state.

- **Scenario:** Attempt to advance a non-existent cycle.
  - Input: `POST /cycles/{cycle_id}/advance` (where `{cycle_id}` does not exist).
  - Outcome: A 404 Not Found error is returned.

- **Scenario:** Attempt to advance a completed cycle.
  - Input: `POST /cycles/{cycle_id}/advance` (where `{cycle_id}` refers to a cycle where `current_round` equals `total_rounds`).
  - Outcome: A 400 Bad Request error is returned.

- **Scenario:** Retrieve the state of an existing cycle.
  - Input: `GET /cycles/{cycle_id}` (where `{cycle_id}` is a valid cycle ID).
  - Outcome: The `CycleResponse` is returned with the current state of the cycle.

- **Scenario:** Retrieve the state of a non-existent cycle.
  - Input: `GET /cycles/{cycle_id}` (where `{cycle_id}` does not exist).
  - Outcome: A 404 Not Found error is returned.

## Out of Scope
- Authentication and authorization.
- Detailed logging configuration. (Basic logging to console is acceptable.)
- Integration with any specific database.  The service should use a simple in-memory data store for now (e.g., a Python dictionary). Persistence is out of scope for this iteration.
- UI components for interacting with this API.
- Asynchronous task execution.
- Metrics and monitoring.
