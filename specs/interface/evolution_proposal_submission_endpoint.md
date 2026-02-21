# Spec: Evolution Proposal Submission Endpoint

**Target:** backend/app/api/endpoints/evolution_proposals.py

## Overview
This specification details the API endpoint responsible for receiving, validating, and storing evolution proposals submitted by users of the Halilit Support Center. This endpoint will be used to integrate evolution strategies proposed by shop floor workers into the simulation system.

## Requirements
- The API endpoint must accept a JSON payload conforming to the `EvolutionProposal` data contract.
- The endpoint must validate the incoming data, returning a 422 error with detailed validation errors if the proposal is invalid.
- Upon successful validation, the endpoint must store the evolution proposal data in the designated database table (`evolution_proposals`).
- The endpoint must return a 201 Created response with the ID of the newly created evolution proposal.
- The endpoint must authenticate the user submitting the proposal. Authentication will be handled via bearer token authentication.
- The endpoint must log all successful submissions, including the user ID, timestamp, and proposal details.
- The database schema for `evolution_proposals` is assumed to already exist. It will contain at least fields matching the Pydantic model.

## Data Contract

**Request Body (JSON):**

```typescript
interface EvolutionProposal {
    title: string; // Max length: 255
    description: string;
    strategy_json: string; // JSON string representing the proposed evolution strategy
    justification: string; // Justification for the proposal
    impact_assessment: string; // Description of the expected impact
    proposed_by: string; // User ID of the proposer (automatically populated server-side, but included for completeness in schema)
}
```

**Pydantic Model:**

```python
from pydantic import BaseModel, constr
from typing import Dict, Any
from datetime import datetime

class EvolutionProposal(BaseModel):
    title: constr(max_length=255)
    description: str
    strategy_json: str  # JSON string representing the proposed evolution strategy
    justification: str
    impact_assessment: str
    proposed_by: str | None = None # Automatically populated server-side.
    created_at: datetime | None = None #Automatically populated server-side.
    id: int | None = None # Auto incrementing, populated server-side

```

**Response (201 Created):**

```json
{
    "id": 123  // The ID of the newly created evolution proposal
}
```

**Error Response (422 Unprocessable Entity):**

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "title"
      ],
      "msg": "string does not satisfy constraints",
      "type": "value_error.str.max_length",
      "ctx": {
        "limit_value": 255
      }
    }
  ]
}
```

## Behavior Scenarios

- **Scenario:** Successful Submission
  - Input: Valid `EvolutionProposal` JSON payload, authenticated user with ID "user123".
  - Outcome:
    - The proposal data is stored in the `evolution_proposals` table.
    - A 201 Created response is returned with the ID of the new proposal.
    - A log entry is created indicating the successful submission.

- **Scenario:** Invalid Title (Too Long)
  - Input: `EvolutionProposal` JSON payload with a `title` field exceeding 255 characters.
  - Outcome:
    - A 422 Unprocessable Entity response is returned with a detailed error message indicating the title length violation.
    - No data is stored in the `evolution_proposals` table.

- **Scenario:** Missing Description
  - Input: `EvolutionProposal` JSON payload missing the `description` field.
  - Outcome:
    - A 422 Unprocessable Entity response is returned with a detailed error message indicating the missing field.
    - No data is stored in the `evolution_proposals` table.

- **Scenario:** Unauthenticated Request
  - Input: Valid `EvolutionProposal` JSON payload, but no authentication token provided.
  - Outcome:
    - A 401 Unauthorized response is returned.
    - No data is stored in the `evolution_proposals` table.

- **Scenario:** Empty strategy_json string
  - Input: Valid `EvolutionProposal` JSON payload, including strategy_json "", authenticated user with ID "user123".
  - Outcome:
    - The proposal data is stored in the `evolution_proposals` table.
    - A 201 Created response is returned with the ID of the new proposal.
    - A log entry is created indicating the successful submission.

## Out of Scope
- Database schema creation or modification.
- Authentication provider details.
- Detailed validation logic for `strategy_json` contents. It is assumed to be a valid JSON format, but the specific schema of the JSON is not validated.
- Error handling beyond basic validation and logging.
- Rate limiting.
