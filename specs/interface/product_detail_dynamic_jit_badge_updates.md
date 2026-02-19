# Spec: Product Detail - Dynamic JIT Badge Updates
**Target:** `src/components/ProductDetail/JITBadge.tsx`

## Overview
This component displays a badge on the product detail page indicating whether a product is manufactured using a Just-In-Time (JIT) process. The badge's text and appearance should dynamically update based on real-time data received from the backend, reflecting the product's current JIT status.

## Requirements
- The component must fetch the JIT status of the product from the `/api/products/{product_id}/jit_status` endpoint.
- The component must display a badge with text indicating either "JIT Enabled" or "JIT Disabled".
- The badge's color should be green for "JIT Enabled" and red for "JIT Disabled".
- The component must re-fetch the JIT status every 5 seconds.
- The component should handle loading and error states gracefully.
- The component must be implemented using React 18, TypeScript, and Tailwind CSS, adhering to the dark theme using slate-900 and blue-500 palette.

## Data Contract
**API Endpoint:** `/api/products/{product_id}/jit_status` (GET)

**Request:**
- Method: GET
- Headers: `Content-Type: application/json`
- Path Parameters:
    - `product_id`: string (UUID)

**Response (Success - 200 OK):**
```json
{
  "jit_enabled": boolean,
  "last_updated": string (ISO 8601 timestamp)
}
```

**Response (Error - 500 Internal Server Error):**
```json
{
  "detail": "string"
}
```

## Behavior Scenarios
- **Scenario:** Initial Load - JIT Enabled
  - Input: Component mounts, API returns `{"jit_enabled": true, "last_updated": "2024-10-27T10:00:00Z"}`
  - Outcome: The component displays a green badge with the text "JIT Enabled".

- **Scenario:** Initial Load - JIT Disabled
  - Input: Component mounts, API returns `{"jit_enabled": false, "last_updated": "2024-10-27T10:00:00Z"}`
  - Outcome: The component displays a red badge with the text "JIT Disabled".

- **Scenario:** JIT Status Changes from Disabled to Enabled
  - Input: Initial state is JIT Disabled. After 5 seconds, the API returns `{"jit_enabled": true, "last_updated": "2024-10-27T10:00:05Z"}`.
  - Outcome: The badge changes from red with "JIT Disabled" to green with "JIT Enabled".

- **Scenario:** API Error
  - Input: Component mounts, API returns a 500 Internal Server Error with `{"detail": "Database connection error"}`.
  - Outcome: The component displays an error message (e.g., "Error fetching JIT status") in a visually distinct manner (e.g., using a red color and an error icon). Subsequent retries should continue to handle errors gracefully.

- **Scenario:** API returns 404 Not Found
    - Input: Component mounts, API returns a 404 Not Found.
    - Outcome: Component displays nothing.

## Out of Scope
- User authentication and authorization.
- Persistence of JIT status (handled by the backend).
- Detailed styling beyond basic color and text.
- Alternative loading/error display implementations (beyond a basic message).
