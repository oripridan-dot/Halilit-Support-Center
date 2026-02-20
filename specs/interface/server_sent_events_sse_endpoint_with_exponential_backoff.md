# Spec: Server-Sent Events (SSE) Endpoint with Exponential Backoff

**Target:** `backend/app/api/endpoints/sse.py`

## Overview
This specification defines a FastAPI endpoint that streams data to clients using Server-Sent Events (SSE) with an exponential backoff retry mechanism. The SSE stream will provide real-time updates on the status of automated manufacturing processes within the Halilit Dark Factory, sourcing data from the internal MES (Manufacturing Execution System).

## Requirements
- The endpoint should be accessible via `GET /api/v1/sse`.
- The endpoint should return a `text/event-stream` content type.
- Each SSE event should include a `data` field containing a JSON-serialized representation of a manufacturing process status update.
- Each SSE event should include a `retry` field specifying the reconnection time in milliseconds using exponential backoff. The initial retry value should be 2 seconds, increasing by a factor of 2 with each failed connection attempt, up to a maximum of 30 seconds (30000ms).
- The data streamed should represent the status of different machines and processes on the factory floor. This data should be fetched from the internal MES system.
- The endpoint should handle potential errors gracefully, logging them and attempting to reconnect to the MES data source.
- The SSE stream should continue indefinitely, providing updates as they become available from the MES.
- The endpoint should use asynchronous operations to avoid blocking the server.

## Data Contract

**API Endpoint:** `GET /api/v1/sse`

**Response (SSE Event):**

```json
{
  "event": "process_update",
  "data": {
    "machine_id": "string",
    "process_name": "string",
    "status": "string",
    "timestamp": "datetime"
  },
  "retry": "integer"
}
```

Where:

*   `machine_id`: Unique identifier for the machine.
*   `process_name`: Name of the manufacturing process.
*   `status`: Current status of the process (e.g., "running", "idle", "error").
*   `timestamp`: Timestamp of the status update.
*   `retry`: Reconnection time in milliseconds.

## Behavior Scenarios

- **Scenario:** Initial Connection and Data Stream
  - Input: Client connects to `GET /api/v1/sse`.
  - Outcome: The server establishes an SSE connection. The server sends SSE events with `data` containing process updates from the MES system.  The initial `retry` value is set to 2000 (2 seconds).

- **Scenario:** MES Data Source Unreachable
  - Input: The server fails to retrieve data from the MES system.
  - Outcome: The server logs the error. The server does *not* close the SSE connection. The server sends an empty SSE data event to keep the connection alive with incrementing retry until max value is achieved.

- **Scenario:** Client Disconnects
  - Input: Client closes the SSE connection.
  - Outcome: The server closes the SSE connection on its end and stops sending events to that client.

- **Scenario:** Connection Loss and Exponential Backoff
  - Input: Client loses connection to the SSE stream. Client attempts to reconnect.
  - Outcome: The server receives the reconnection attempt. The server provides process updates, the reconnection time increases to 4000, 8000, 16000, and caps at 30000 for subsequent failures.

## Out of Scope
- Authentication and authorization for accessing the SSE endpoint. This will be handled by a separate middleware.
-  The specific implementation of the MES data retrieval. The code will include a function `get_mes_data()` which is called every iteration. This returns a list of dicts.
- Metrics and monitoring of the SSE stream.
