# Spec: Search Debounce Data Pipeline

**Target:** data_pipeline/search_debounce.py

## Overview
This data pipeline script implements a debounce mechanism for search queries. It consumes a stream of search query strings, filters out rapid consecutive duplicates, and outputs a stream of debounced search queries that can then be used to trigger downstream actions like hitting a search API.  This prevents overwhelming downstream systems with many near-identical searches performed in quick succession by the user.

## Requirements
- The script must accept a stream of search query strings as input.  The precise input mechanism (e.g., reading from a file, a queue, or standard input) is to be configurable via environment variables.
- The script must filter out consecutive duplicate search queries.  For example, if the input stream contains "apple", "apple", "orange", "orange", the output stream should contain "apple", "orange".
- The script must implement a debounce mechanism. If a search query appears, and then another different query appears within a configurable time window (debounce time), the initial query should be dropped. If no other query appears within the debounce time, the initial query is emitted. The debounce time should be configurable via an environment variable.
- The output stream of debounced search queries must be written to a configurable output location (e.g., a file, a queue, or standard output) defined via environment variables.
- The script must handle errors gracefully and log them appropriately.
- The script must be configurable via environment variables.
- The script should be idempotent, meaning if it crashes and restarts it should not double process messages already processed. It should leverage file based state storage for this.
- The script should log to STDOUT using structured logging.

## Data Contract
**Input:** A stream of strings (search queries).  The precise format depends on the input mechanism (see below).

**Output:** A stream of strings (debounced search queries). The precise format depends on the output mechanism (see below).

**Configuration (Environment Variables):**

| Variable Name              | Type     | Description                                                                                                                                                                                                    | Default Value |
| -------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| `INPUT_TYPE`              | string  | The type of input source.  Valid values are "file", "stdin", "kafka".                                                                                                                                             | "stdin"       |
| `INPUT_FILE`              | string  | The path to the input file, if `INPUT_TYPE` is "file".                                                                                                                                                       |               |
| `KAFKA_BROKER`             | string  | The Kafka broker address, if `INPUT_TYPE` is "kafka".                                                                                                                                                             |               |
| `KAFKA_TOPIC`              | string  | The Kafka topic to read from, if `INPUT_TYPE` is "kafka".                                                                                                                                                          |               |
| `OUTPUT_TYPE`             | string  | The type of output destination.  Valid values are "file", "stdout", "kafka".                                                                                                                                         | "stdout"      |
| `OUTPUT_FILE`             | string  | The path to the output file, if `OUTPUT_TYPE` is "file".                                                                                                                                                      |               |
| `OUTPUT_KAFKA_BROKER`        | string  | The Kafka broker address, if `OUTPUT_TYPE` is "kafka".                                                                                                                                                            |               |
| `OUTPUT_KAFKA_TOPIC`       | string  | The Kafka topic to write to, if `OUTPUT_TYPE` is "kafka".                                                                                                                                                         |               |
| `DEBOUNCE_TIME_MS`        | integer | The debounce time in milliseconds.                                                                                                                                                                                | 500           |
| `STATE_FILE`         | string  | The path to store persistent state, for resuming the pipeline if it restarts.     |  "search_debounce_state.json"         |
## Behavior Scenarios
- **Scenario:** Basic Debounce
  - Input: Stream: "apple", "apple", "orange", "orange", "banana", "kiwi" (with arrival times spaced such that debounce occurs)
  - Outcome: Output Stream: "apple", "orange", "banana", "kiwi"

- **Scenario:** Rapid Duplicate Suppression & Debounce
  - Input: Stream: "apple", "apple", "apple", "orange", "orange", "orange", "banana", "kiwi" (all within the debounce time of each other).
  - Outcome: Output Stream:  Only the first occurence of each distinct term within debounce_time.

- **Scenario:** Debounce Timeout
  - Input: Stream: "apple", (wait 1000ms), "orange" (debounce time is 500ms).
  - Outcome: Output Stream: "apple", "orange"

- **Scenario:** File Input/Output
  - Input: `INPUT_TYPE=file`, `INPUT_FILE=input.txt`, `OUTPUT_TYPE=file`, `OUTPUT_FILE=output.txt`. `input.txt` contains "apple\napple\norange\n".
  - Outcome: `output.txt` contains "apple\norange\n" (after debounce and deduplication).

- **Scenario:** Kafka Input/Output
  - Input: `INPUT_TYPE=kafka`, `KAFKA_BROKER=kafka:9092`, `KAFKA_TOPIC=input-topic`, `OUTPUT_TYPE=kafka`, `OUTPUT_KAFKA_BROKER=kafka:9092`, `OUTPUT_KAFKA_TOPIC=output-topic`. Messages "apple", "orange" sent to `input-topic`.
  - Outcome: Messages "apple", "orange" sent to `output-topic` (after debounce and deduplication, assuming sufficient time between messages).

- **Scenario:** Restart after Crash
  - Input: Initial Stream: "apple", "orange", "banana", crash; Restart: "kiwi", "grape". (`STATE_FILE` properly configured.)
  - Outcome: Output Stream: "apple", "orange", "banana", "kiwi", "grape" (No duplicates of apple/orange/banana due to state file.)

## Out of Scope
- Implementation of the Kafka brokers themselves. This spec assumes they exist and are accessible.
- Detailed error handling beyond logging (e.g., retry mechanisms for Kafka).
- Dynamic configuration updates (the script reads environment variables only at startup).
