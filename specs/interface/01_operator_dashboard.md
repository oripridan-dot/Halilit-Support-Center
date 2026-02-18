# Operator Dashboard Specification

## Goal
Mission Control (Dashboard) gives the operator at-a-glance metrics and quick actions. No decorative or "game" elements.

## Layout
- **Header:** Title "Mission Control"; optional last-updated timestamp.
- **Key Metrics (Cards or Strip):**
  - Total products in catalog.
  - Products missing price (Call for Price count).
  - Last ingestion run status (success/fail, date).
  - Optional: Top brands count.
- **Quick Actions:**
  - "Open Inventory Master" (navigate to Inventory).
  - "Run Ingestion" or "Data Pipeline" (if applicable).
- **No:** Galaxy, Spectrum, 3D, or gamified visualizations.

## Data Requirements
- Source: Backend `/api/dashboard/stats` or equivalent (counts from `learned_taxonomy.json` or DB).
- Loading: Skeleton or spinner until data loads.
- Error: Toast or inline message; do not crash.

## Behavior Scenarios
- **Scenario:** Page loads.
  - **Outcome:** Metrics resolve and display within 2s or show loading state.
- **Scenario:** Ingestion has never run.
  - **Outcome:** "Last run" shows "Never" or "—"; no error.
