# Spec: Enhanced Search Debounce for Halilit Support Center

**Target:** `data_pipeline/scripts/enhanced_search_debounce.py`

## Overview
This script aims to improve the efficiency of search operations within the Halilit Support Center by implementing a debouncing mechanism. This will prevent excessive queries from being sent to the backend when users rapidly type or modify search terms, reducing server load and improving responsiveness.

## Requirements
- The script must read search query logs from a specified input file.
- The script must identify potentially debounced queries based on proximity in time (configurable threshold).
- The script must output a file containing the original queries and a flag indicating whether they were likely debounced.
- The script must be configurable with a time window parameter (in seconds) to define the debouncing threshold.
- The script must log the number of total queries processed, and the number of queries identified as likely debounced.
- The script must be robust and handle potential errors such as malformed log entries gracefully.
- The script should be designed to be easily integrated into an existing data pipeline.

## Data Contract
**Input (Search Query Logs):**

Each line in the input file represents a search query. The structure of each line is a JSON string containing at least the timestamp and the search query.

```json
{
  "timestamp": "2024-10-27T10:00:00.000Z",
  "query": "broken halilit toy"
}
```

**Output (Debounced Query Analysis):**

The output is a JSONL (JSON Lines) file, where each line is a JSON object containing the original log entry and a boolean flag indicating whether the query was likely debounced.

```json
{
  "timestamp": "2024-10-27T10:00:00.000Z",
  "query": "broken halilit toy",
  "debounced": true
}
```

**Configuration:**

The script should accept the following configuration parameters:

- `input_file` (str): Path to the input log file.
- `output_file` (str): Path to the output JSONL file.
- `debounce_threshold` (float): Time window in seconds within which queries are considered debounced (e.g., 0.5 seconds).

## Behavior Scenarios
- **Scenario:** Basic Debouncing
  - Input:  `input.log` containing:
    ```json
    {"timestamp": "2024-10-27T10:00:00.000Z", "query": "ha"}
    {"timestamp": "2024-10-27T10:00:00.200Z", "query": "hal"}
    {"timestamp": "2024-10-27T10:00:00.400Z", "query": "hali"}
    {"timestamp": "2024-10-27T10:00:00.600Z", "query": "halil"}
    {"timestamp": "2024-10-27T10:00:05.000Z", "query": "halilit"}
    ```
  - Configuration: `debounce_threshold = 0.5`
  - Outcome: `output.jsonl` should contain:
    ```json
    {"timestamp": "2024-10-27T10:00:00.000Z", "query": "ha", "debounced": true}
    {"timestamp": "2024-10-27T10:00:00.200Z", "query": "hal", "debounced": true}
    {"timestamp": "2024-10-27T10:00:00.400Z", "query": "hali", "debounced": true}
    {"timestamp": "2024-10-27T10:00:00.600Z", "query": "halil", "debounced": false}
    {"timestamp": "2024-10-27T10:00:05.000Z", "query": "halilit", "debounced": false}
    ```

- **Scenario:** No Debouncing
  - Input:  `input.log` containing:
    ```json
    {"timestamp": "2024-10-27T10:00:00.000Z", "query": "toy"}
    {"timestamp": "2024-10-27T10:00:05.000Z", "query": "toys"}
    ```
  - Configuration: `debounce_threshold = 0.5`
  - Outcome: `output.jsonl` should contain:
    ```json
    {"timestamp": "2024-10-27T10:00:00.000Z", "query": "toy", "debounced": false}
    {"timestamp": "2024-10-27T10:00:05.000Z", "query": "toys", "debounced": false}
    ```

- **Scenario:** Empty Input File
  - Input: `input.log` is empty
  - Configuration: `debounce_threshold = 0.5`
  - Outcome: `output.jsonl` should be empty, script should log that 0 queries were processed and 0 were debounced, without raising an exception.

- **Scenario:** Malformed JSON Log Entry
  - Input: `input.log` contains:
    ```json
    {"timestamp": "2024-10-27T10:00:00.000Z", "query": "correct"}
    {"timestamp": "2024-10-27T10:00:01.000Z", "invalid": "json}
    {"timestamp": "2024-10-27T10:00:02.000Z", "query": "another correct"}
    ```
  - Configuration: `debounce_threshold = 0.5`
  - Outcome: `output.jsonl` should contain the valid entries with appropriate `debounced` flags. The invalid entry should be skipped and logged as an error, and not cause the script to terminate.

## Out of Scope
- This script does not handle the actual throttling or blocking of queries. It only identifies potential debounced queries.
- This script does not interact with the search API directly. It only analyzes log files.
- Real-time debouncing within the application is out of scope. This script analyzes historical data.
