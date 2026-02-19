# Spec: Product Sourcing Badge Component

**Target:** src/components/ProductDetail/SourcingBadge.tsx

## Overview
This component displays a badge indicating the sourcing information for a specific product. The badge's text and appearance will dynamically change based on data retrieved from the backend regarding the product's origin and ethical sourcing practices.  It enhances transparency and provides crucial information to the end user.

## Requirements
- The component must fetch sourcing data from the `/products/{product_id}/sourcing` backend endpoint.
- The component must display a badge with text reflecting the product's sourcing status.  Possible statuses are: "Ethically Sourced", "Partially Sourced", "Unknown Sourcing".
- The badge must have a distinct visual representation for each status (color-coded).
    - "Ethically Sourced":  Background color: `bg-green-500`, Text color: `text-white`
    - "Partially Sourced": Background color: `bg-yellow-500`, Text color: `text-slate-900`
    - "Unknown Sourcing": Background color: `bg-red-500`, Text color: `text-white`
- The component must handle loading and error states gracefully, displaying appropriate indicators.
- The component should be reusable and accept a `productId` prop of type `string`.
- The component should use `react-query` for data fetching and caching.

## Data Contract

**API Endpoint:** `GET /products/{product_id}/sourcing`

**Request:**

*   Path Parameter: `product_id` (string, required). Example: `"product123"`

**Response:**

```json
{
  "status": "Ethically Sourced" | "Partially Sourced" | "Unknown Sourcing"
}
```

**Error Response:**

Standard HTTP error codes (400, 404, 500) with a JSON body:

```json
{
  "detail": "Error message"
}
```

## Behavior Scenarios

- **Scenario:** Initial Load - Loading State
  - Input: Component is mounted with `productId="product456"`.
  - Outcome: The component displays a loading indicator (e.g., a spinner or placeholder text "Loading...").

- **Scenario:** Successful Fetch - Ethically Sourced
  - Input: The API returns `{ "status": "Ethically Sourced" }`.
  - Outcome: The component displays a badge with the text "Ethically Sourced", with a green background (`bg-green-500`) and white text (`text-white`).

- **Scenario:** Successful Fetch - Partially Sourced
  - Input: The API returns `{ "status": "Partially Sourced" }`.
  - Outcome: The component displays a badge with the text "Partially Sourced", with a yellow background (`bg-yellow-500`) and dark slate text (`text-slate-900`).

- **Scenario:** Successful Fetch - Unknown Sourcing
  - Input: The API returns `{ "status": "Unknown Sourcing" }`.
  - Outcome: The component displays a badge with the text "Unknown Sourcing", with a red background (`bg-red-500`) and white text (`text-white`).

- **Scenario:** API Error - Product Not Found
  - Input: The API returns a 404 error with the message "Product not found".
  - Outcome: The component displays an error message "Sourcing information unavailable."

- **Scenario:** API Error - Server Error
  - Input: The API returns a 500 error with the message "Internal Server Error".
  - Outcome: The component displays an error message "Failed to retrieve sourcing information."

## Out of Scope
- Styling beyond the specified background and text colors is out of scope.
- The backend implementation of the `/products/{product_id}/sourcing` endpoint is out of scope. This spec assumes that endpoint exists and returns the documented data contract.
- Caching strategies beyond what `react-query` provides by default.
