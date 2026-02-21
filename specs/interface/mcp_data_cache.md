# Spec: MCP Data Cache

**Target:** `data_pipeline/mcp_data_cache.py`

## Overview
This data pipeline script is responsible for caching Material Control Program (MCP) data from the Halilit ERP system into a local, queryable data store. This cached data will be used by other services to optimize response times and reduce load on the ERP system. The script will use a configurable polling interval to keep the cache up-to-date.

## Requirements
- [x] The script must connect to the Halilit ERP system to retrieve MCP data.
- [x] The script must use environment variables for configuration, including:
    - [x] `ERP_API_URL`: The URL of the Halilit ERP API endpoint.
    - [x] `ERP_API_KEY`: API key for authentication with the ERP system.
    - [x] `CACHE_POLLING_INTERVAL`:  Interval in seconds between data refresh attempts (default: 600 seconds).
    - [x] `CACHE_FILE_PATH`: Path to the local cache file (default: `./mcp_data_cache.json`).
- [x] The script must store the cached data in a JSON file.
- [x] The script must implement error handling and logging.  All errors must be logged with sufficient detail to diagnose issues.
- [x] The script must implement a mechanism to prevent concurrent execution.
- [x] The script must include a health check endpoint (returns HTTP 200 OK) that can be used to verify it's running and the last successful cache update time.
- [x]  The script must load data from the cache file on startup if it exists.
- [x] The script must handle schema changes in the ERP API response gracefully, logging warnings for unexpected fields but continuing to operate.
- [x]  Data from the ERP must overwrite the local cache file atomically to avoid partial data writes in case of interruption.
- [x]  The script must support full and incremental updates from the ERP. By default, it does full updates. Implement functionality to support ERP systems that support incremental updates by checking for a `last_updated_timestamp` and querying for records modified after that timestamp. This incremental update feature must be togglable via `ENABLE_INCREMENTAL_UPDATES` environment variable (default: false).

## Data Contract
**ERP API Response (example):**

```json
[
  {
    "material_code": "MAT001",
    "description": "Product A",
    "quantity": 100,
    "location": "Warehouse 1",
    "last_updated": "2024-10-26T10:00:00Z"
  },
  {
    "material_code": "MAT002",
    "description": "Product B",
    "quantity": 50,
    "location": "Warehouse 2",
    "last_updated": "2024-10-26T10:30:00Z"
  }
]
```

**Cached Data (JSON file):**

```json
{
  "last_updated_timestamp": "2024-10-26T10:30:00Z",
  "data": [
    {
      "material_code": "MAT001",
      "description": "Product A",
      "quantity": 100,
      "location": "Warehouse 1",
      "last_updated": "2024-10-26T10:00:00Z"
    },
    {
      "material_code": "MAT002",
      "description": "Product B",
      "quantity": 50,
      "location": "Warehouse 2",
      "last_updated": "2024-10-26T10:30:00Z"
    }
  ]
}
```

## Behavior Scenarios
- **Scenario:** Initial Cache Population
  - Input: Script starts with an empty or non-existent cache file.
  - Outcome: Script fetches all MCP data from the ERP API, stores it in the cache file, and sets the `last_updated_timestamp` to the most recent `last_updated` value from the ERP data (or the current timestamp if ERP data does not contain this field).

- **Scenario:** Regular Cache Refresh (Full Update)
  - Input: `CACHE_POLLING_INTERVAL` has elapsed, and `ENABLE_INCREMENTAL_UPDATES` is false.
  - Outcome: Script fetches all MCP data from the ERP API, overwrites the cache file with the new data, and updates the `last_updated_timestamp`.

- **Scenario:** Regular Cache Refresh (Incremental Update)
  - Input: `CACHE_POLLING_INTERVAL` has elapsed, and `ENABLE_INCREMENTAL_UPDATES` is true. A `last_updated_timestamp` exists in the cache file.
  - Outcome: Script queries the ERP API for records where `last_updated` is greater than the `last_updated_timestamp` in the cache file.  Merges new/updated records with existing cache. If a record in ERP matches an existing `material_code` it is replaced, otherwise appended.  Removes any records in the cache that are *not* returned from the ERP to handle deletions.  Updates `last_updated_timestamp` to the most recent `last_updated` value from the ERP data. If no data is returned from ERP, the existing cached data is kept and `last_updated_timestamp` is updated to the current timestamp.

- **Scenario:** ERP API Unavailable
  - Input: Script attempts to fetch data from the ERP API, but the API is unavailable (e.g., network error, server error).
  - Outcome: Script logs an error message, retries after `CACHE_POLLING_INTERVAL` seconds.  Retains the last known good cache data.

- **Scenario:** ERP API Returns an Error
  - Input: Script attempts to fetch data from the ERP API, but the API returns an error code (e.g., 500, 401).
  - Outcome: Script logs an error message including the status code and response from the ERP API, and retries after `CACHE_POLLING_INTERVAL` seconds. Retains the last known good cache data.

- **Scenario:** Invalid Cache File
  - Input: The cache file exists but is corrupted or contains invalid JSON.
  - Outcome: Script logs a warning message, deletes the corrupted cache file, and performs a full data refresh from the ERP API.

- **Scenario:** Configuration Missing
  - Input: One or more required environment variables (e.g., `ERP_API_URL`, `ERP_API_KEY`) are missing.
  - Outcome: The script logs a critical error message and exits.

- **Scenario:** Health Check
  - Input: A GET request is made to `/healthz`
  - Outcome: The script returns an HTTP 200 OK status code and a JSON payload containing the status (`"ok"`) and the `last_updated_timestamp` from the cache file, or `null` if the cache has never been updated.
  ```json
  {
      "status": "ok",
      "last_updated_timestamp": "2024-10-26T10:30:00Z"
  }
  ```

## Out of Scope
- [Data validation and transformation beyond basic type conversion.]
- [Authorization and authentication beyond API key management.]
- [Detailed monitoring and alerting beyond basic error logging.]
- [Support for different ERP systems besides Halilit.]
