# Spec: MCP Data Cache Refresh Script
**Target:** data_pipeline/scripts/refresh_mcp_cache.py

## Overview
This script will refresh the Material Composition Profile (MCP) data cache used by the Halilit Support Center. It fetches the latest MCP data from the internal data lake, transforms it into a suitable format, and stores it in a persistent data store for efficient retrieval by other services. This script is intended to be run on a scheduled basis, ensuring the data cache remains up-to-date.

## Requirements
- The script must be written in Python 3.11 or higher.
- The script must fetch MCP data from the internal data lake (location to be determined via environment variable `DATA_LAKE_MCP_PATH`).
- The script must transform the data into a suitable format for storage and retrieval (detailed below).
- The script must store the transformed data in a persistent data store (e.g., a PostgreSQL database accessible via an environment variable `DATABASE_URL`).
- The script must log all errors and warnings to a centralized logging system.
- The script must be idempotent; running it multiple times should not lead to inconsistent data.
- The script must be configurable via environment variables.
- The script must include proper error handling for network outages, data format errors, and database connection failures.
- The script must track the last update timestamp and store it alongside the data.

## Data Contract
The MCP data from the data lake is assumed to be in a CSV format (though this may be subject to change; the script should be easily adaptable). The CSV is expected to have the following columns: `material_id`, `composition_name`, `element`, `percentage`, `unit`. The persistent data store will hold a table named `mcp_cache` with the following schema:

```sql
CREATE TABLE IF NOT EXISTS mcp_cache (
    material_id VARCHAR(255) NOT NULL,
    composition_name VARCHAR(255) NOT NULL,
    element VARCHAR(255) NOT NULL,
    percentage FLOAT NOT NULL,
    unit VARCHAR(255) NOT NULL,
    last_updated TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
    PRIMARY KEY (material_id, composition_name, element)
);
```

The transformed data, ready for insertion into the `mcp_cache` table, will be a list of dictionaries. Each dictionary will represent a row in the table.

## Behavior Scenarios
- **Scenario:** Successful Data Refresh
  - Input: Data lake contains new MCP data. `DATABASE_URL` and `DATA_LAKE_MCP_PATH` are properly configured.
  - Outcome: The `mcp_cache` table in the database is updated with the new MCP data. A log entry indicating successful completion is written.

- **Scenario:** Data Lake Unavailable
  - Input: The data lake is temporarily unavailable. `DATABASE_URL` and `DATA_LAKE_MCP_PATH` are properly configured.
  - Outcome: An error is logged, and the script exits gracefully. The existing data in the `mcp_cache` table remains unchanged. An alert should be triggered in the monitoring system.

- **Scenario:** Database Unavailable
  - Input: The database is temporarily unavailable. `DATABASE_URL` and `DATA_LAKE_MCP_PATH` are properly configured.
  - Outcome: An error is logged, and the script exits gracefully. The existing data in the `mcp_cache` table remains unchanged. An alert should be triggered in the monitoring system.

- **Scenario:** Invalid Data Format in Data Lake
  - Input: The data in the data lake has an unexpected format (e.g., missing columns, incorrect data types). `DATABASE_URL` and `DATA_LAKE_MCP_PATH` are properly configured.
  - Outcome: An error is logged, indicating the data format issue. The script exits gracefully. The existing data in the `mcp_cache` table remains unchanged. An alert should be triggered in the monitoring system.

- **Scenario:** No Changes in Data Lake
  - Input: The data in the data lake is the same as the data currently in the `mcp_cache`. `DATABASE_URL` and `DATA_LAKE_MCP_PATH` are properly configured.
  - Outcome: The script skips the update process and logs a message indicating that no changes were found. The `last_updated` timestamp in `mcp_cache` remains unchanged for all unchanged rows.

## Out of Scope
- This spec does not cover the scheduling of the script. A separate system (e.g., cron, Airflow) will be responsible for running the script at regular intervals.
- This spec does not define the exact format of the log entries (this will be handled by the centralized logging system).
- This spec does not cover the initial creation of the `mcp_cache` table. It is assumed the table already exists.
- This spec does not cover any UI component that presents this data.
