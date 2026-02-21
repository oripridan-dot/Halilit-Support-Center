# Spec: MCP Data Cache Pipeline

**Target:** data_pipeline/mcp_data_cache.py

## Overview
This data pipeline script retrieves Machine Control Program (MCP) data from internal sources, transforms it, and caches it in a format suitable for the Halilit Support Center's dark factory monitoring system. The cache ensures efficient access to frequently used MCP data, minimizing reliance on live queries to source systems.

## Requirements
- [x] Must retrieve MCP data from the internal database (defined as `INTERNAL_DB_CONNECTION_STRING`).
- [x] Must transform the raw MCP data into a standardized, application-specific data model (defined below).
- [x] Must cache the transformed data in a Redis instance, keyed by `mcp:{mcp_id}` where `mcp_id` is the MCP ID.
- [x] Must use a configurable expiry time for the cached data (default: 24 hours, configurable via env variable `MCP_CACHE_EXPIRY_SECONDS`).
- [x] Must include error handling and logging for data retrieval, transformation, and caching operations.
- [x] Must be idempotent - re-running the script should not cause data duplication or inconsistencies.
- [x] Must log the number of MCP records retrieved, transformed, and cached.
- [x] Must use environment variables for configuration (database connection string, Redis connection details).
- [x] Must only fetch MCP data updated in the last 30 days.
- [x] Must respect the "Three Source Rule".

## Data Contract

### MCP Data Model (Pydantic)
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MCPData(BaseModel):
    mcp_id: str  # Unique identifier for the MCP
    part_number: str
    revision: str
    program_name: str
    status: str # e.g., "Active", "Inactive", "Deprecated"
    last_updated: datetime
    required_tools: list[str] # List of tool IDs
    estimated_cycle_time_seconds: Optional[float] = None # Estimated time to run the program
    notes: Optional[str] = None # Any additional notes or comments

```

### Input (Environment Variables)
- `INTERNAL_DB_CONNECTION_STRING`: Database connection string for the internal data source.
- `REDIS_HOST`: Redis host.
- `REDIS_PORT`: Redis port.
- `REDIS_DB`: Redis database number.
- `MCP_CACHE_EXPIRY_SECONDS`: Cache expiry time in seconds (default: 86400).

### Output (Redis)
- Key: `mcp:{mcp_id}`
- Value: JSON string representation of the `MCPData` object.

## Behavior Scenarios

- **Scenario:** Initial run with empty Redis cache.
  - Input: Empty Redis database.
  - Outcome: MCP data fetched from the internal database, transformed, and cached in Redis. Logs will indicate the number of records processed.

- **Scenario:** MCP data already exists in Redis cache.
  - Input: Redis database contains cached MCP data.
  - Outcome: Script checks for MCP records updated in the last 30 days. Updated records are re-fetched, transformed, and cached, overwriting the existing data. No errors should occur.  Logs will indicate the number of records processed.

- **Scenario:** Database connection fails.
  - Input: Invalid database connection string.
  - Outcome: Script logs an error message and exits gracefully. No data is cached in Redis.

- **Scenario:** Redis connection fails.
  - Input: Invalid Redis connection details.
  - Outcome: Script logs an error message and exits gracefully. No data is cached in Redis.

- **Scenario:** Transformation fails due to invalid data.
  - Input: Database contains MCP records with missing or invalid data.
  - Outcome: The script logs a warning message, skips the problematic record, and continues processing other records. Invalid records are not cached in Redis.

## Out of Scope
- [x] Real-time data synchronization between the source database and the cache. This script is intended for periodic updates.
- [x] Authentication for accessing the Redis instance (assumes Redis is configured without authentication or that credentials are provided via connection string).
- [x] Monitoring and alerting for the pipeline's execution.
- [x] Initial database setup and schema creation.
- [x] Versioning of the MCP data model.
