# Spec: Catalog Organizer Service

**Target:** services/catalog_organizer.py

## Overview
This service is responsible for organizing and categorizing data received from Halilit's dark factory production line. It takes raw data, cleans and transforms it, and then assigns it to appropriate categories based on predefined rules, and stores the organized data for later retrieval and analysis.

## Requirements
- [x] Must receive raw data from the production line in JSON format via a defined API endpoint.
- [x] Must validate the incoming data against a predefined schema to ensure data integrity.
- [x] Must clean the data by removing duplicates, handling missing values (e.g., replacing with `None`), and standardizing formats.
- [x] Must categorize the data based on a configurable rule set (e.g., product type, manufacturing date, defect type).
- [x] Must store the organized and categorized data in a structured format (e.g., database, data lake).  For now, we will store it in memory.
- [x] Must provide an API endpoint to retrieve data based on category and time range.
- [x] Must log all operations, including data validation errors, categorization decisions, and storage events.
- [x] Must be able to handle high volumes of data with minimal latency.
- [x] Must use environment variables to configure the service, including database connection details and rule set location.
- [x] The categorization rule set should be easily updatable without requiring service restarts.

## Data Contract

**API Endpoint:** `/catalog/organize` (POST)

**Request Body:**

```json
{
  "raw_data": [
    {
      "product_id": "string",
      "timestamp": "string (ISO 8601 format)",
      "sensor_readings": {
        "temperature": "number",
        "pressure": "number",
        "vibration": "number"
      },
      "defect_code": "string (optional)"
    }
  ]
}
```

**Response Body (Success - 200 OK):**

```json
{
  "status": "success",
  "message": "Data successfully organized and stored."
}
```

**Response Body (Error - 400 Bad Request):**

```json
{
  "status": "error",
  "message": "Data validation failed.",
  "errors": [
    "Error message 1",
    "Error message 2"
  ]
}
```

**API Endpoint:** `/catalog/retrieve` (GET)

**Request Parameters:**

- `category`: `string` (e.g., "electronics", "mechanical", "defective") - Required
- `start_time`: `string` (ISO 8601 format) - Required
- `end_time`: `string` (ISO 8601 format) - Required

**Response Body (Success - 200 OK):**

```json
{
  "status": "success",
  "data": [
    {
      "product_id": "string",
      "timestamp": "string (ISO 8601 format)",
      "sensor_readings": {
        "temperature": "number",
        "pressure": "number",
        "vibration": "number"
      },
      "defect_code": "string (optional)",
      "category": "string"
    }
  ]
}
```

**Response Body (Error - 400 Bad Request):**

```json
{
  "status": "error",
  "message": "Invalid request parameters."
}
```

**Response Body (Error - 404 Not Found):**

```json
{
  "status": "error",
  "message": "No data found for the specified criteria."
}
```

## Behavior Scenarios

- **Scenario:** Successful data organization.
  - Input:  POST request to `/catalog/organize` with valid JSON data conforming to the data contract.
  - Outcome:  Service validates the data, categorizes it (based on hardcoded rules for this version), stores it in memory, and returns a 200 OK response with `{"status": "success", "message": "Data successfully organized and stored."}`.

- **Scenario:** Data validation failure.
  - Input:  POST request to `/catalog/organize` with invalid JSON data (e.g., missing `product_id`, incorrect timestamp format).
  - Outcome:  Service detects the validation error, returns a 400 Bad Request response with `{"status": "error", "message": "Data validation failed.", "errors": [...]}` containing specific error messages.

- **Scenario:** Successful data retrieval.
  - Input:  GET request to `/catalog/retrieve` with valid parameters (e.g., `category=electronics&start_time=2024-01-01T00:00:00Z&end_time=2024-01-02T00:00:00Z`).
  - Outcome:  Service retrieves the data from memory matching the criteria, and returns a 200 OK response with `{"status": "success", "data": [...]}` containing the matching data.

- **Scenario:** No data found for retrieval.
  - Input: GET request to `/catalog/retrieve` with parameters that do not match any stored data.
  - Outcome: Service returns a 404 Not Found response with `{"status": "error", "message": "No data found for the specified criteria."}`.

- **Scenario:** Invalid request parameters for retrieval.
    - Input: GET request to `/catalog/retrieve` with missing `start_time`.
    - Outcome: Service returns a 400 Bad Request response with `{"status": "error", "message": "Invalid request parameters."}`.

## Out of Scope
- [Persistence of organized data to a database or data lake (this will be handled in a future iteration).]
- [Dynamic configuration of categorization rules (rules are hardcoded for now).]
- [Authentication and authorization for API endpoints.]
- [Detailed error logging to an external service (only basic logging is implemented).]

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
