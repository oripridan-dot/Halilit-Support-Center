# Spec: Skeleton Data Proposal Script
**Target:** data_pipeline/scripts/skeleton_data_proposal.py

## Overview
This script proposes a skeleton data structure (JSON schema) for a new sensor type based on analyzing existing sensor data files within the Halilit Dark Factory data lake. The script aims to automate the initial schema creation process, ensuring consistency and reducing manual effort.

## Requirements
- The script must accept a sensor type (string) as input.
- The script must locate sample data files for the specified sensor type within the data lake.  Assume a well-defined directory structure: `/data/{sensor_type}/{date}/{filename}.json`.
- The script must analyze a configurable number of sample data files (default: 5) for the specified sensor type to infer the data structure.
- The script must infer the data type of each field based on the observed data (e.g., string, integer, float, boolean, list, dictionary).
- The script must generate a JSON schema (draft-07) representing the proposed skeleton data structure. This schema should include `type` and, where applicable, `description` fields.
- The script must handle missing fields gracefully, marking them as optional (nullable) in the schema.
- The script must output the generated JSON schema to the console in a human-readable format (e.g., with indentation).
- The script must log any errors encountered during the process, including file read errors and type inference failures.
- The script must validate the generated JSON schema against the draft-07 specification before outputting it.

## Data Contract

**Input (Command Line Argument):**

- `sensor_type`: string (e.g., "temperature", "pressure", "vibration")

**Output (Console):**

- JSON schema (string, formatted with indentation) representing the proposed data structure. Example:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "timestamp": {
      "type": "string",
      "description": "Timestamp of the measurement"
    },
    "value": {
      "type": "number",
      "description": "Sensor reading value"
    },
    "unit": {
      "type": "string",
      "description": "Unit of measurement",
      "nullable": true
    }
  },
  "required": [
    "timestamp",
    "value"
  ]
}
```

## Behavior Scenarios

- **Scenario:** Valid Sensor Type and Data
  - Input: `python skeleton_data_proposal.py temperature` and the data lake contains `/data/temperature/2024-10-26/temp_sensor_1.json`, `/data/temperature/2024-10-26/temp_sensor_2.json` ... with valid temperature data.
  - Outcome: A valid JSON schema is generated and printed to the console, representing the structure of the temperature sensor data.

- **Scenario:** Sensor Type with Missing Data Files
  - Input: `python skeleton_data_proposal.py humidity` and the data lake contains no files under `/data/humidity/`.
  - Outcome: An error message is logged indicating that no data files were found for the humidity sensor type, and the script exits gracefully without generating a schema.

- **Scenario:** Data Files with Inconsistent Schemas
  - Input: `python skeleton_data_proposal.py pressure` and the data lake contains `/data/pressure/2024-10-26/pressure_sensor_1.json` with fields `timestamp`, `value`, and `unit`, and `/data/pressure/2024-10-26/pressure_sensor_2.json` with fields `time`, `reading`, and `scale`.
  - Outcome: The generated JSON schema includes all fields observed across the analyzed files (`timestamp`, `value`, `unit`, `time`, `reading`, `scale`), and indicates which fields are nullable (optional) based on their presence in each file.

- **Scenario:** Invalid JSON Data in Files
  - Input: `python skeleton_data_proposal.py vibration` and `/data/vibration/2024-10-26/vibration_sensor_1.json` contains invalid JSON.
  - Outcome: An error is logged indicating that the file could not be parsed, and the script continues processing other files (up to the configured number of sample files).

## Out of Scope
-  This script does not handle data cleaning or transformation. It only infers the existing data structure.
-  The script does not support complex data types like nested arrays beyond simple lists of primitive types (string, number, boolean).
- The script does not include any UI components for displaying the generated schema. This is a command-line utility.
-  Detailed error reporting beyond logging a message is out of scope.
- Data versioning is not handled.
- Authentication/authorization for data access is not covered here.
