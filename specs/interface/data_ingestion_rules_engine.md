# Spec: Data Ingestion Rules Engine
**Target:** data_pipeline/ingestion_rules.py

## Overview
This specification defines the rules engine responsible for validating and transforming raw data ingested from various sources into a standardized format suitable for further processing within the Halilit Support Center's data pipeline. The engine will apply a series of configurable rules to each incoming data record, ensuring data quality and consistency.

## Requirements
- Implement a Python class `IngestionRulesEngine` with a method `apply_rules(data: dict) -> dict`.
- The `apply_rules` method must iterate through a configurable list of rules defined as dictionaries within a JSON file (`config/ingestion_rules.json`).
- Each rule must specify:
  - `field`: The field in the input data to which the rule applies.
  - `type`: The data type to which the field should be cast (e.g., "string", "integer", "float", "boolean", "datetime").
  - `required`: A boolean indicating whether the field is required.
  - `validation`: A dictionary containing validation parameters, which may include:
    - `min`: Minimum value (for numeric types).
    - `max`: Maximum value (for numeric types).
    - `pattern`: Regular expression pattern (for string types).
    - `values`: A list of allowed values (for string or numeric types).
  - `transformation`: An optional dictionary specifying how to transform the field, including:
    - `mapping`: A dictionary mapping input values to output values.
    - `format`: A string specifying the desired datetime format (e.g., "%Y-%m-%d").
- The engine should raise `ValueError` exceptions with descriptive messages if any rule fails validation.
- The engine should log all successful and failed rule applications using the `logging` module.
- The configuration file path (`config/ingestion_rules.json`) must be configurable as an argument to the `IngestionRulesEngine` class constructor.
- The output `dict` must only contain fields defined in at least one rule.

## Data Contract

**Input Data (example):**

```json
{
  "ticket_id": "12345",
  "customer_email": "test@example.com",
  "priority": "high",
  "created_at": "2024-01-01T10:00:00Z"
}
```

**Rules Configuration (config/ingestion_rules.json example):**

```json
[
  {
    "field": "ticket_id",
    "type": "integer",
    "required": true,
    "validation": {
      "min": 10000,
      "max": 99999
    }
  },
  {
    "field": "customer_email",
    "type": "string",
    "required": true,
    "validation": {
      "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    }
  },
  {
    "field": "priority",
    "type": "string",
    "required": true,
    "validation": {
      "values": ["low", "medium", "high"]
    },
    "transformation": {
      "mapping": {
        "low": "LOW",
        "medium": "MEDIUM",
        "high": "HIGH"
      }
    }
  },
  {
    "field": "created_at",
    "type": "datetime",
    "required": true,
    "transformation": {
      "format": "%Y-%m-%d %H:%M:%S"
    }
  },
  {
    "field": "resolution_time",
    "type": "float",
    "required": false
  }
]
```

**Output Data (example, after applying the rules above):**

```json
{
  "ticket_id": 12345,
  "customer_email": "test@example.com",
  "priority": "HIGH",
  "created_at": "2024-01-01 10:00:00"
}
```

## Behavior Scenarios
- **Scenario:** Valid Input Data
  - Input: `{"ticket_id": "12345", "customer_email": "test@example.com", "priority": "high", "created_at": "2024-01-01T10:00:00Z"}`
  - Outcome: The data should be transformed according to the rules and returned in the correct format. The output should be `{"ticket_id": 12345, "customer_email": "test@example.com", "priority": "HIGH", "created_at": "2024-01-01 10:00:00"}`.

- **Scenario:** Invalid Ticket ID (out of range)
  - Input: `{"ticket_id": "1", "customer_email": "test@example.com", "priority": "high", "created_at": "2024-01-01T10:00:00Z"}`
  - Outcome: A `ValueError` should be raised with a message indicating the `ticket_id` is out of range.

- **Scenario:** Invalid Email Format
  - Input: `{"ticket_id": "12345", "customer_email": "invalid-email", "priority": "high", "created_at": "2024-01-01T10:00:00Z"}`
  - Outcome: A `ValueError` should be raised with a message indicating the `customer_email` has an invalid format.

- **Scenario:** Invalid Priority Value
  - Input: `{"ticket_id": "12345", "customer_email": "test@example.com", "priority": "critical", "created_at": "2024-01-01T10:00:00Z"}`
  - Outcome: A `ValueError` should be raised with a message indicating the `priority` value is not allowed.

- **Scenario:** Missing Required Field
  - Input: `{"customer_email": "test@example.com", "priority": "high", "created_at": "2024-01-01T10:00:00Z"}`
  - Outcome: A `ValueError` should be raised with a message indicating the `ticket_id` field is required.

- **Scenario:** Input data with fields missing from rule config.
  - Input: `{"ticket_id": "12345", "customer_email": "test@example.com", "priority": "high", "created_at": "2024-01-01T10:00:00Z", "extra_field": "some_value"}`
  - Outcome:  The data should be transformed according to the rules and returned in the correct format, excluding "extra_field". The output should be `{"ticket_id": 12345, "customer_email": "test@example.com", "priority": "HIGH", "created_at": "2024-01-01 10:00:00"}`.

- **Scenario:** Empty Input Data
  - Input: `{}`
  - Outcome: A `ValueError` should be raised if any of the rules defined are required.

## Out of Scope
- Data source integration. This engine only validates and transforms data provided as input.
- Error handling beyond raising `ValueError` exceptions.  Specific logging configuration is assumed to be handled by the caller.
- Complex transformations beyond type casting, regular expression matching, allowed value checking, and datetime formatting, or value mapping.
- Implementing custom validation functions. Validation is limited to min/max range, regex patterns, and allowed values.
