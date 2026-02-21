# Spec: Automated Strategy Evolution Proposal Generation
**Target:** backend/services/strategy_evolution.py

## Overview
This service automates the generation of strategy evolution proposals. Given a set of performance metrics and historical strategy data, it analyzes potential improvements and suggests concrete modifications to the existing strategy. The service focuses on identifying weaknesses in the current strategy, exploring alternative approaches based on historical data, and proposing specific, actionable changes with predicted performance improvements.

## Requirements
- The service must accept a strategy ID, a time window, and a set of relevant performance metrics as input.
- The service must retrieve the current strategy definition and historical performance data for the specified strategy ID.
- The service must analyze the historical data to identify periods of underperformance.
- The service must explore alternative strategy parameters based on historical data and domain-specific heuristics.
- The service must generate a ranked list of proposed strategy modifications, along with predicted performance improvements for each modification.
- The service must provide a confidence score for each proposed modification, indicating the likelihood of achieving the predicted performance improvement.
- The service must log all inputs, outputs, and intermediate calculations for auditing and debugging purposes.
- The service must handle potential errors gracefully, providing informative error messages.
- The service must be deployable as a FastAPI endpoint.
- The service should integrate with existing monitoring and alerting systems to notify stakeholders of any performance degradation.

## Data Contract

**Request (POST /strategy_evolution/propose):**

```json
{
  "strategy_id": int,
  "time_window_start": str,  // ISO 8601 timestamp
  "time_window_end": str,    // ISO 8601 timestamp
  "metrics": list[str]       // List of metric names to consider
}
```

**Response (200 OK):**

```json
{
  "proposals": list[
    {
      "modification": str,        // Description of the proposed modification
      "predicted_improvement": float, // Predicted performance improvement (e.g., % increase in profit)
      "confidence": float,          // Confidence score (0.0-1.0)
      "rationale": str              // Explanation of why this modification is proposed
    }
  ]
}
```

**Error Response (400 Bad Request):**

```json
{
  "error": str  // Error message describing the problem
}
```

## Behavior Scenarios

- **Scenario:** Successful Proposal Generation
  - Input: `{"strategy_id": 123, "time_window_start": "2024-01-01T00:00:00Z", "time_window_end": "2024-01-31T23:59:59Z", "metrics": ["profit", " Sharpe_ratio"]}`
  - Outcome: Returns a 200 OK response with a list of strategy evolution proposals, each containing a modification description, predicted improvement, confidence score, and rationale.  The proposals are ranked by predicted improvement, highest first.

- **Scenario:** Invalid Strategy ID
  - Input: `{"strategy_id": 999, "time_window_start": "2024-01-01T00:00:00Z", "time_window_end": "2024-01-31T23:59:59Z", "metrics": ["profit"]}` (where strategy 999 does not exist)
  - Outcome: Returns a 400 Bad Request response with `{"error": "Strategy with ID 999 not found"}`.

- **Scenario:** Invalid Time Window
  - Input: `{"strategy_id": 123, "time_window_start": "2024-01-31T00:00:00Z", "time_window_end": "2024-01-01T23:59:59Z", "metrics": ["profit"]}` (start date after end date)
  - Outcome: Returns a 400 Bad Request response with `{"error": "Invalid time window: start date must be before end date"}`.

- **Scenario:** Missing Metrics
  - Input: `{"strategy_id": 123, "time_window_start": "2024-01-01T00:00:00Z", "time_window_end": "2024-01-31T23:59:59Z", "metrics": []}`
  - Outcome: Returns a 400 Bad Request response with `{"error": "At least one metric must be specified"}`.

- **Scenario:** Internal Error During Analysis
  - Input: `{"strategy_id": 123, "time_window_start": "2024-01-01T00:00:00Z", "time_window_end": "2024-01-31T23:59:59Z", "metrics": ["profit", "Sharpe_ratio"]}` (where an unexpected error occurs during the analysis phase)
  - Outcome: Returns a 500 Internal Server Error response with `{"error": "Internal server error: Unable to generate proposals"}` and logs the full exception details.

## Out of Scope
- Implementation of the strategy execution engine.
- Visualization of the proposed changes.
- User interface for interacting with the service.
- Real-time strategy monitoring.
