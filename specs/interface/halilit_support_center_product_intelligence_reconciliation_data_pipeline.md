# Spec: Halilit Support Center Product Intelligence Reconciliation Data Pipeline
**Target:** data_pipeline/hsc_product_intelligence_reconciliation.py

## Overview
This data pipeline reconciles product intelligence data (e.g., usage metrics, feature adoption) from various internal sources with customer support interactions logged in the Halilit Support Center. The goal is to provide support agents with a unified view of a customer's product usage history and identify potential product-related issues proactively. This pipeline processes data daily and stores the reconciled information in a structured format suitable for consumption by the Halilit Support Center frontend.

## Requirements
-   The pipeline must ingest data from the following sources:
    -   Product Usage Analytics Database (PostgreSQL, schema `product_analytics`): Stores daily product usage metrics (e.g., feature usage counts, active users, session durations) at the customer and product level.
    -   Halilit Support Center Database (PostgreSQL, schema `support_center`): Stores support ticket data, including customer ID, ticket creation/resolution timestamps, ticket subject, description, and agent notes.
-   The pipeline must perform data cleaning and transformation to ensure data consistency and accuracy.
-   The pipeline must identify potential product-related support issues based on correlations between product usage patterns and support ticket submissions.  This includes flagging customers with recent drops in feature usage, increased error rates, or usage patterns known to precede support requests.
-   The pipeline must output the reconciled data into a dedicated PostgreSQL table (schema `reconciled_data`, table `customer_product_intelligence`).
-   The pipeline must be designed for daily execution at 00:00 UTC.
-   The pipeline must be implemented using Python 3.11+ and utilize libraries such as `psycopg2` for database interaction, `pandas` for data manipulation, and `FastAPI` for optional health check endpoint.
-   The pipeline must log its execution status, including start time, end time, number of records processed, and any errors encountered.

## Data Contract

**Input Data:**

*   **Product Usage Analytics Database (product_analytics.daily_usage):**

    | Column Name       | Data Type | Description                                                 | Example                               |
    | ----------------- | --------- | ----------------------------------------------------------- | ------------------------------------- |
    | customer_id       | INTEGER   | Unique identifier for the customer                        | 12345                               |
    | product_id        | INTEGER   | Unique identifier for the product                          | 67890                               |
    | usage_date        | DATE      | Date of usage                                               | 2024-10-27                            |
    | feature_a_usage   | INTEGER   | Number of times feature A was used                           | 15                                  |
    | feature_b_usage   | INTEGER   | Number of times feature B was used                           | 22                                  |
    | active_session_ms | INTEGER   | Total active session time in milliseconds                 | 3600000 (1 hour)                      |
    | error_count       | INTEGER   | Number of errors encountered during product usage          | 2                                   |

*   **Halilit Support Center Database (support_center.tickets):**

    | Column Name   | Data Type | Description                                     | Example                               |
    | ------------- | --------- | ----------------------------------------------- | ------------------------------------- |
    | ticket_id     | INTEGER   | Unique identifier for the support ticket        | 1                                   |
    | customer_id   | INTEGER   | Unique identifier for the customer                | 12345                               |
    | created_at    | TIMESTAMP | Timestamp when the ticket was created           | 2024-10-26 10:00:00+00                |
    | resolved_at   | TIMESTAMP | Timestamp when the ticket was resolved          | 2024-10-26 14:00:00+00                |
    | subject       | TEXT      | Subject of the support ticket                  | "Feature A not working"             |
    | description   | TEXT      | Description of the support ticket                | "User reports Feature A is broken..." |
    | agent_notes   | TEXT      | Notes added by the support agent              | "Issue resolved by clearing cache"  |

**Output Data (reconciled_data.customer_product_intelligence):**

| Column Name                       | Data Type   | Description                                                                                                                                | Example                              |
| --------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| customer_id                       | INTEGER     | Unique identifier for the customer                                                                                                       | 12345                              |
| product_id                        | INTEGER     | Unique identifier for the product                                                                                                         | 67890                              |
| last_usage_date                   | DATE        | Last date the product was used                                                                                                               | 2024-10-27                           |
| average_feature_usage_past_7_days | FLOAT       | Average usage of all features combined over the past 7 days                                                                              | 17.5                               |
| error_count_past_7_days           | INTEGER     | Total number of errors encountered in the past 7 days                                                                                   | 5                                  |
| ticket_count_past_30_days         | INTEGER     | Number of support tickets submitted in the past 30 days                                                                                   | 2                                  |
| last_ticket_subject               | TEXT        | Subject of the most recent support ticket                                                                                                    | "Feature A not working"            |
| potential_issue_flag              | BOOLEAN     | Flag indicating potential product-related issue based on heuristics (e.g., significant drop in usage, increased error rate).          | TRUE                               |
| last_updated_at                   | TIMESTAMP   | Timestamp when this record was last updated                                                                                             | 2024-10-28 00:00:00+00             |

## Behavior Scenarios

-   **Scenario:** New Customer with High Error Rate
    -   Input: `product_analytics.daily_usage` shows a new customer (customer_id=99999) with a consistently high `error_count` (e.g., > 10) over the past week.  `support_center.tickets` shows no tickets from this customer.
    -   Outcome: `reconciled_data.customer_product_intelligence` should have a new row for customer_id=99999 with `potential_issue_flag` set to TRUE and `error_count_past_7_days` matching the total error count from `product_analytics.daily_usage`.  `ticket_count_past_30_days` should be 0, and `last_ticket_subject` should be NULL.

-   **Scenario:** Existing Customer Submits a Ticket
    -   Input: An existing customer (customer_id=12345) submits a new support ticket (`support_center.tickets`). `product_analytics.daily_usage` data for this customer remains unchanged.
    -   Outcome: The `reconciled_data.customer_product_intelligence` row for customer_id=12345 should have its `ticket_count_past_30_days` incremented. The `last_ticket_subject` should be updated to the subject of the newly created ticket. The `last_updated_at` timestamp should be updated.

-   **Scenario:** Customer Usage Drops Significantly
    -   Input: `product_analytics.daily_usage` shows a significant drop (e.g., > 50%) in `feature_a_usage` and `feature_b_usage` for an existing customer (customer_id=54321) compared to the previous week's average.  `support_center.tickets` shows no recent tickets related to feature usage problems.
    -   Outcome: The `reconciled_data.customer_product_intelligence` row for customer_id=54321 should have its `potential_issue_flag` set to TRUE. `average_feature_usage_past_7_days` should reflect the lower usage.

-   **Scenario:**  No Data Available for a Customer
    -   Input: A customer exists in `support_center.tickets` but no corresponding records exist in `product_analytics.daily_usage`.
    -   Outcome:  A row for this customer should still be created in `reconciled_data.customer_product_intelligence`. All product-usage related fields such as `last_usage_date`, `average_feature_usage_past_7_days`, and `error_count_past_7_days` should be set to `NULL`. The  `potential_issue_flag` should be set to `FALSE`. The `ticket_count_past_30_days` and `last_ticket_subject` should reflect the values derived from the `support_center.tickets` table.

## Out of Scope
-   Real-time data processing (this pipeline is designed for daily batch processing).
-   Advanced machine learning models for issue prediction (the current implementation relies on simple heuristics).
-   Detailed root cause analysis of product issues.
-   User interface for viewing the reconciled data (this is handled by the Halilit Support Center frontend, which is a separate project).
-   Data retention policies for the `reconciled_data.customer_product_intelligence` table.
