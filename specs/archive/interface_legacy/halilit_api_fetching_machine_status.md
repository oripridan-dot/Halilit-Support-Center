# Spec: Halilit API - Fetching Machine Status

**Target:** backend/halilit_api/machines.py

## Overview
This service defines the API endpoint and data model for retrieving real-time status information for machines in the Halilit dark factory. It uses FastAPI and Pydantic to ensure data validation and type safety.  The data is fetched from the internal Halilit machine data source (assumed to be accessible).

## Requirements
- [x] Implement a FastAPI endpoint `/machines/{machine_id}/status` that accepts a `machine_id` (string) as a path parameter.
- [x] Define a Pydantic model `MachineStatus` to represent the structure of the machine status data.
- [x] The `MachineStatus` model should include fields for:
    - `machine_id` (str): Unique identifier of the machine.
    - `status` (str): Current operational status (e.g., "Running", "Idle", "Error").
    - `production_rate` (float, optional):  Units produced per hour (can be None if not applicable).
    - `error_code` (str, optional):  Error code, if applicable (can be None).
    - `last_updated` (datetime): Timestamp of the last status update (timezone-aware).
- [x] The endpoint should return a JSON response representing the `MachineStatus` for the given machine ID.
- [x] Handle the case where the machine ID is not found. Return a 404 error with a descriptive message.
- [x] Implement error handling for unexpected exceptions during data retrieval, returning a 500 error with a generic error message.
- [x] Ensure all timestamps are timezone-aware (UTC).

## Data Contract

**Request:**

```
GET /machines/{machine_id}/status
```

Path Parameter:
- `machine_id` (str): The unique identifier of the machine to retrieve status for.

**Response (Success - 200 OK):**

```json
{
  "machine_id": "string",
  "status": "string",
  "production_rate": "float | null",
  "error_code": "string | null",
  "last_updated": "datetime"
}
```

Example:
```json
{
  "machine_id": "MCHN-001",
  "status": "Running",
  "production_rate": 120.5,
  "error_code": null,
  "last_updated": "2024-10-27T10:00:00+00:00"
}
```

**Response (Error - 404 Not Found):**

```json
{
  "detail": "Machine with ID '{machine_id}' not found."
}
```

**Response (Error - 500 Internal Server Error):**

```json
{
  "detail": "Internal server error."
}
```

## Behavior Scenarios

- **Scenario:** Successful retrieval of machine status.
  - Input: `GET /machines/MCHN-001/status`
  - Outcome: Returns a 200 OK response with the `MachineStatus` for `MCHN-001`.  The `last_updated` field contains a timezone-aware timestamp.

- **Scenario:** Machine ID not found.
  - Input: `GET /machines/NON-EXISTENT-ID/status`
  - Outcome: Returns a 404 Not Found response with the message "Machine with ID 'NON-EXISTENT-ID' not found.".

- **Scenario:** Machine is in an error state.
  - Input: `GET /machines/MCHN-002/status` (where MCHN-002 is in an error state)
  - Outcome: Returns a 200 OK response with the `MachineStatus` for `MCHN-002`. The `status` field should be "Error", the `error_code` field should contain a relevant error code (e.g., "E101"), and `production_rate` may be `null`.

- **Scenario:** Internal data source error.
    - Input: Simulate a failure when accessing the Halilit machine data source. Then, `GET /machines/MCHN-003/status`.
    - Outcome: Returns a 500 Internal Server Error response with the message "Internal server error.".

## Out of Scope
- Authentication and authorization.
- Data source implementation details (assumed to exist).
- Monitoring and logging.
-  Deployment configurations.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
