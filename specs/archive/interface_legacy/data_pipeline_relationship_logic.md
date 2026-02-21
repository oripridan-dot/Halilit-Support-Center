# Spec: Data Pipeline - Relationship Logic

**Target:** data_pipeline/relationship_logic.py

## Overview
This script automates the creation and management of relationship records within the Halilit Support Center database. It identifies potential relationships between support tickets based on shared attributes (e.g., customer ID, asset serial number, error codes) and automatically creates relationship records in a specified database table if a defined confidence threshold is met. This improves ticket resolution efficiency by linking related incidents.

## Requirements
- The script must connect to the Halilit Support Center database using credentials stored securely (e.g., environment variables).
- The script must retrieve all open support tickets from the database.
- The script must implement configurable logic to determine potential relationships between tickets, considering attributes like customer ID, asset serial number, and error codes.
- The script must calculate a confidence score for each potential relationship based on the matching attributes and their assigned weights.
- The script must only create relationship records in the database if the confidence score exceeds a configurable threshold.
- The script must log all actions, including successful relationship creation and instances where the confidence threshold was not met, using a standardized logging format.
- The script must be designed to run as a scheduled task (e.g., using cron or a task scheduler) on a regular basis (e.g., hourly).
- The script should avoid creating duplicate relationship records. Before creating a new relationship, it must check if the relationship already exists in the database.
- The script must handle potential errors gracefully, including database connection errors, data retrieval errors, and data insertion errors.
- Configuration parameters (database credentials, relationship logic weights, confidence threshold) must be configurable via a `.env` file or similar mechanism.

## Data Contract

**Input:**
- Data from the Halilit Support Center database, specifically the `support_tickets` table.  The table is assumed to have at least the following columns:
  - `ticket_id` (INTEGER, primary key)
  - `customer_id` (INTEGER, foreign key to `customers` table)
  - `asset_serial_number` (TEXT, nullable)
  - `error_code` (TEXT, nullable)
  - `description` (TEXT)
  - `status` (TEXT, e.g., "Open", "Closed")
  - `created_at` (TIMESTAMP)

**Output:**
- Inserted rows into the `ticket_relationships` table in the Halilit Support Center database. The table is assumed to have the following columns:
  - `relationship_id` (INTEGER, primary key, autoincrement)
  - `ticket_id_1` (INTEGER, foreign key to `support_tickets.ticket_id`)
  - `ticket_id_2` (INTEGER, foreign key to `support_tickets.ticket_id`)
  - `confidence_score` (FLOAT)
  - `created_at` (TIMESTAMP, defaults to current timestamp)

## Behavior Scenarios

- **Scenario:** Two open tickets share the same `customer_id` and `asset_serial_number`, and the combined weight of these matching attributes exceeds the confidence threshold.
  - Input: Two `support_tickets` records:
    - Ticket 1: `ticket_id=1`, `customer_id=123`, `asset_serial_number="ABC123"`, `error_code=NULL`, `status="Open"`
    - Ticket 2: `ticket_id=2`, `customer_id=123`, `asset_serial_number="ABC123"`, `error_code="XYZ"`, `status="Open"`
  - Outcome: A new `ticket_relationships` record is created: `ticket_id_1=1`, `ticket_id_2=2`, `confidence_score` > threshold. A log entry indicating successful relationship creation is written.

- **Scenario:** Two open tickets share only the same `customer_id`, and the weight of this matching attribute is below the confidence threshold.
  - Input: Two `support_tickets` records:
    - Ticket 1: `ticket_id=3`, `customer_id=456`, `asset_serial_number="DEF456"`, `error_code=NULL`, `status="Open"`
    - Ticket 2: `ticket_id=4`, `customer_id=456`, `asset_serial_number="GHI789"`, `error_code=NULL`, `status="Open"`
  - Outcome: No new `ticket_relationships` record is created. A log entry indicating that the confidence threshold was not met is written.

- **Scenario:** Two open tickets share the same `customer_id` and `asset_serial_number`, but a relationship record already exists between these tickets.
  - Input: Two `support_tickets` records:
    - Ticket 1: `ticket_id=5`, `customer_id=789`, `asset_serial_number="JKL012"`, `error_code=NULL`, `status="Open"`
    - Ticket 2: `ticket_id=6`, `customer_id=789`, `asset_serial_number="JKL012"`, `error_code="XYZ"`, `status="Open"`
  - A `ticket_relationships` record already exists: `ticket_id_1=5`, `ticket_id_2=6`
  - Outcome: No new `ticket_relationships` record is created. A log entry indicating that the relationship already exists is written.

- **Scenario:** Database connection fails.
  - Input: Attempt to connect to the Halilit Support Center database fails.
  - Outcome: An error message is logged. The script exits gracefully without creating any relationship records.

## Out of Scope
- This specification does not cover the initial creation or schema definition of the `support_tickets` and `ticket_relationships` database tables.
- This specification does not cover the implementation of the scheduled task that executes this script.
- This specification does not cover the user interface or API endpoint to view the created relationships.
- Configuration of logging levels and output destinations is not defined in this document.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
