# Spec: Proposal Verdict Update Data Pipeline

**Target:** data_pipeline/proposal_verdict_update.py

## Overview
This data pipeline script updates proposal verdicts in the Halilit Support Center database based on information received from an external scoring service. It retrieves proposal IDs and associated verdicts from a defined data source (currently a CSV file, but designed for future integration with other sources) and updates the corresponding records in the database. The script prioritizes data integrity and efficient processing of large datasets.

## Requirements
- The script must read proposal IDs and verdicts from a configurable data source (initially a CSV file).
- The script must validate the structure and data types of the input data. Specifically, it expects a CSV file with columns "proposal_id" (integer) and "verdict" (string, limited to "accepted" or "rejected").
- The script must connect to the Halilit Support Center database using defined credentials (loaded from environment variables).
- The script must update the "verdict" column in the "proposals" table based on the received data, matching on "proposal_id".
- The script must handle potential database errors gracefully, logging errors and continuing with the remaining records.
- The script must log all successful updates and any errors encountered.
- The script must be configurable to accept different data source types in the future (e.g., JSON file, API endpoint).
- The script must be idempotent: running it multiple times with the same input should result in the same database state.
- The script must be executable via command line.
- The script should implement a dry-run mode where it reports the intended changes without actually applying them to the database.

## Data Contract

**Input Data (CSV):**

```csv
proposal_id,verdict
123,accepted
456,rejected
789,accepted
```

**Environment Variables:**

- `DATABASE_HOST`: The hostname or IP address of the database server.
- `DATABASE_PORT`: The port number of the database server.
- `DATABASE_NAME`: The name of the database.
- `DATABASE_USER`: The username for connecting to the database.
- `DATABASE_PASSWORD`: The password for connecting to the database.
- `INPUT_FILE_PATH`: Path to the CSV input file.

**Database Table: `proposals`**

| Column       | Data Type | Constraints  |
|--------------|-----------|--------------|
| proposal_id  | INTEGER   | PRIMARY KEY  |
| verdict      | VARCHAR(20)|              |
| ...          | ...       | ...          |

## Behavior Scenarios

- **Scenario:** Successful update
  - Input: CSV file with valid proposal IDs and verdicts. Database contains matching proposal IDs with potentially outdated verdicts.
  - Outcome: The script connects to the database, updates the verdicts in the `proposals` table, and logs successful update messages.

- **Scenario:** Invalid proposal ID
  - Input: CSV file contains a proposal ID that does not exist in the database.
  - Outcome: The script logs an error message indicating that the proposal ID was not found and continues processing other records.

- **Scenario:** Invalid verdict
  - Input: CSV file contains a verdict that is not "accepted" or "rejected".
  - Outcome: The script logs an error message indicating the invalid verdict and skips updating that record.

- **Scenario:** Database connection error
  - Input: Invalid database credentials or database server unavailable.
  - Outcome: The script logs an error message and exits.

- **Scenario:** Dry-run mode
  - Input: The script is executed with the `--dry-run` flag.
  - Outcome: The script reads the input data, validates it, and prints the intended updates to the console without modifying the database.

- **Scenario:** Empty input file
  - Input: CSV file exists but is empty.
  - Outcome: The script logs a message indicating that no proposals were found in the input file and exits gracefully.

- **Scenario:** `proposal_id` column is missing in the CSV
  - Input: CSV file does not contain the `proposal_id` column.
  - Outcome: The script logs an error and exits, indicating that the required column is missing.

- **Scenario:** `verdict` column is missing in the CSV
  - Input: CSV file does not contain the `verdict` column.
  - Outcome: The script logs an error and exits, indicating that the required column is missing.

## Out of Scope
- Implementing a user interface for running the script.
- Defining specific alerting or monitoring mechanisms.
- Automatic scheduling of the script. This is assumed to be handled by an external scheduler.
- Detailed error handling for network interruptions *during* database updates (beyond basic try/except).
