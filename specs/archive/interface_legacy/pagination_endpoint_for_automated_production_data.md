# Spec: Pagination Endpoint for Automated Production Data

**Target:** backend/app/api/endpoints/production_data.py

## Overview
This specification defines a paginated API endpoint for retrieving production data from the Halilit Dark Factory's automated systems. This endpoint will allow clients to efficiently fetch subsets of production records, reducing the load on both the server and the client, and improving the user experience when dealing with large datasets.

## Requirements
- The endpoint must return production data in a paginated format.
- The endpoint must support query parameters for pagination: `page` (integer, default=1) and `page_size` (integer, default=10).
- The endpoint must return a JSON response containing:
    - `items`: A list of production data records for the current page.
    - `total`: The total number of production data records.
    - `page`: The current page number.
    - `page_size`: The number of items per page.
- Production data records must include, at a minimum:
    - `timestamp`:  ISO 8601 formatted timestamp of the event.
    - `machine_id`:  Unique identifier for the machine that generated the event.
    - `event_type`:  String indicating the type of event (e.g., "start", "stop", "error", "measurement").
    - `data`:  A dictionary containing event-specific data (e.g., temperature, pressure, cycle time).
- The endpoint must return HTTP status code 200 (OK) on success.
- The endpoint must handle invalid `page` and `page_size` values gracefully (e.g., return an error or default to valid values).
- The endpoint must be secured with appropriate authentication and authorization mechanisms (details to be defined in a separate security specification).
- The endpoint must use the existing Halilit Dark Factory data model.

## Data Contract

**Request:**

*   Method: GET
*   Path: `/production_data`
*   Query Parameters:
    *   `page`: `int` (optional, default: 1).  The page number to retrieve.  Must be greater than or equal to 1.
    *   `page_size`: `int` (optional, default: 10).  The number of items to return per page.  Must be between 1 and 100 (inclusive).

**Response (Success - 200 OK):**

```json
{
  "items": [
    {
      "timestamp": "2024-10-27T10:00:00Z",
      "machine_id": "machine-001",
      "event_type": "start",
      "data": {}
    },
    {
      "timestamp": "2024-10-27T10:00:05Z",
      "machine_id": "machine-001",
      "event_type": "measurement",
      "data": {
        "temperature": 25.5
      }
    }
  ],
  "total": 1000,
  "page": 1,
  "page_size": 10
}
```

**Error Handling:**

*   Invalid `page` or `page_size` values should result in a 400 Bad Request response with a JSON body explaining the error.  For example:

```json
{
  "detail": "Invalid page_size. Must be between 1 and 100."
}
```

## Behavior Scenarios

- **Scenario:** Request first page with default page size.
  - Input: `GET /production_data`
  - Outcome: Returns the first 10 production data records (if available), `page` is 1, `page_size` is 10, and `total` reflects the total number of records in the system.

- **Scenario:** Request second page with a custom page size.
  - Input: `GET /production_data?page=2&page_size=20`
  - Outcome: Returns records 21-40 (if available), `page` is 2, `page_size` is 20, and `total` reflects the total number of records in the system.

- **Scenario:** Request an invalid page size.
  - Input: `GET /production_data?page=1&page_size=0`
  - Outcome: Returns a 400 Bad Request with a JSON body indicating that the `page_size` is invalid.

- **Scenario:** Request a page beyond the last page.
  - Input: `GET /production_data?page=1000&page_size=10` (assuming only 995 total records)
  - Outcome: Returns an empty list for `items`, `page` is 1000, `page_size` is 10, and `total` reflects the total number of records in the system.

## Out of Scope
- Database schema definition. It is assumed that the data model is already defined and accessible.
- Authentication and authorization implementation details. This will be covered by a separate security specification.
- Specific error logging or monitoring mechanisms.
- Caching strategies for the endpoint.
- The specific logic for retrieving production data records from the database.  This is assumed to be handled by a separate data access layer.
