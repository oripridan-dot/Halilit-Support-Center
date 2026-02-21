# Spec: Proposal Verdict Data Pipeline

**Target:** data_pipeline/proposal_verdict.py

## Overview
This script processes data from Halilit's data sources to determine a verdict (Approve/Reject) for a given proposal. This verdict is based on a predefined set of rules evaluating proposal attributes against current factory capacity and material availability. The script outputs a JSON file containing the proposal ID and the determined verdict.

## Requirements
- The script must connect to the Halilit database to retrieve proposal details, factory capacity, and material availability data.
- The script must implement a rule engine to evaluate proposals based on predefined rules. These rules will consider factors such as the quantity of materials required, the current factory capacity, and the proposal's priority.
- The script must output a JSON file containing the proposal ID and the verdict (Approved or Rejected).
- The script must handle database connection errors gracefully and log any errors encountered.
- The script must be configurable via environment variables (database connection details, rule configuration file path).
- The script must adhere to the Three Source Rule; all data originates from Halilit's defined data sources.

## Data Contract

**Input:**
*   Proposal ID (integer) - Passed as a command line argument.
*   Database: Access to Halilit's database containing proposal details, factory capacity, and material availability.
*   Rule Configuration File: A JSON file defining the rules for evaluating proposals. Example:

    ```json
    [
        {
            "rule_id": "capacity_check",
            "description": "Check if factory capacity is sufficient",
            "type": "capacity",
            "threshold": 0.8, // Max capacity utilization
            "weight": 0.6
        },
        {
            "rule_id": "material_availability",
            "description": "Check if required materials are available",
            "type": "material",
            "material_codes": ["ALU101", "STL202"],
            "weight": 0.4
        }
    ]
    ```

**Output:**

*   JSON file: `proposal_verdict_{proposal_id}.json`

    ```json
    {
        "proposal_id": 123,
        "verdict": "Approved" // Or "Rejected"
    }
    ```

## Behavior Scenarios

- **Scenario:** Proposal Approved due to sufficient capacity and material availability.
  - Input: `proposal_id = 123`. Database contains data indicating ample factory capacity and required materials are in stock. Rule configuration specifies that capacity utilization should be below 80% and all materials are available.
  - Outcome: A JSON file `proposal_verdict_123.json` is created with content `{"proposal_id": 123, "verdict": "Approved"}`.

- **Scenario:** Proposal Rejected due to insufficient capacity.
  - Input: `proposal_id = 456`. Database contains data indicating factory capacity is already at 95%, exceeding the rule threshold of 80%.
  - Outcome: A JSON file `proposal_verdict_456.json` is created with content `{"proposal_id": 456, "verdict": "Rejected"}`.

- **Scenario:** Proposal Rejected due to material shortage.
  - Input: `proposal_id = 789`. Database indicates that material "ALU101" is out of stock. The rule configuration specifies that "ALU101" and "STL202" must be available.
  - Outcome: A JSON file `proposal_verdict_789.json` is created with content `{"proposal_id": 789, "verdict": "Rejected"}`.

- **Scenario:** Invalid Proposal ID.
  - Input: `proposal_id = 999`. Database does not contain a proposal with ID 999.
  - Outcome: The script logs an error message "Proposal with ID 999 not found." and exits. No JSON file is created.

- **Scenario:** Database connection error.
  - Input: Invalid database credentials are provided via environment variables.
  - Outcome: The script logs an error message "Failed to connect to database." and exits. No JSON file is created.

## Out of Scope
-  User interface for viewing the verdict.
-  Integration with notification systems.
-  Real-time updates to factory capacity or material availability. This script runs on-demand.
-  Detailed explanation of the rejection reason beyond "Approved" or "Rejected".
