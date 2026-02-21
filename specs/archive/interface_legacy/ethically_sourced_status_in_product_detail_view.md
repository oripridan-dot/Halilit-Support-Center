# Spec: Ethically Sourced Status in Product Detail View

**Version:** 1.0
**Component:** `src/components/ProductDetail/SourcingBadge.tsx`

## 1. Purpose

To display the ethical sourcing status of a product within the Product Detail View, enhancing transparency and empowering operators to make informed decisions. The current `Product Detail Sourcing Badge` only covers `internal`, `external`, or `unknown` sourcing. This spec extends the sourcing badge to specifically include `Ethically Sourced` status, supporting a more granular view.

## 2. Requirements

1. **Data Source:** Fetch ethical sourcing data from the `/api/products/{product_id}/sourcing` endpoint. The endpoint must return a JSON response containing the ethical sourcing status.
2. **Badge Display:** The `SourcingBadge` component MUST display the appropriate badge based on the `status` field received from the API.
3. **Supported Statuses:** The component MUST support the following ethical sourcing statuses:
   - `"Ethically Sourced"`: Display a green badge with the text "Ethically Sourced".
   - `"Partially Sourced"`: Display a yellow badge with the text "Partially Sourced".
   - `"Unknown Sourcing"`: Display a red badge with the text "Sourcing Unknown".
4.  **Loading State:**  While fetching data from the API, display a loading indicator.
5.  **Error Handling:**  If the API request fails, display an error message.
6.  **Styling:** Use Tailwind CSS to style the badges consistently with the dark theme, ensuring proper color contrast for readability. The text should be slate-900 for yellow badges and white for green and red badges.
7. **API Endpoint:** A new `/api/products/{product_id}/sourcing` endpoint is required. The `status` field MUST return one of the values specified in Requirement 3.
8. **Accessibility:** Ensure the badge is accessible to users with disabilities, providing appropriate ARIA attributes and sufficient color contrast.

## 3. Data Contract

**API Endpoint:** `/api/products/{product_id}/sourcing` (GET)

**Request:**

- Path Parameter: `product_id` (string) - The ID of the product.

**Response (Success - 200 OK):**

```json
{
  "status": "Ethically Sourced" | "Partially Sourced" | "Unknown Sourcing"
}
```

**Response (Error - 500 Internal Server Error):**

```json
{
  "detail": "string" // Error message
}
```

## 4. Behavior Scenarios

1. **Scenario:** Product A has `ethical_sourcing: "Ethically Sourced"`.
   - Input: The API returns `{"status": "Ethically Sourced"}`.
   - Outcome: The `SourcingBadge` displays a green badge with the text "Ethically Sourced".
2. **Scenario:** Product B has `ethical_sourcing: "Partially Sourced"`.
   - Input: The API returns `{"status": "Partially Sourced"}`.
   - Outcome: The `SourcingBadge` displays a yellow badge with the text "Partially Sourced".
3. **Scenario:** Product C has `ethical_sourcing: "Unknown Sourcing"`.
   - Input: The API returns `{"status": "Unknown Sourcing"}`.
   - Outcome: The `SourcingBadge` displays a red badge with the text "Sourcing Unknown".
4. **Scenario:** The API returns an error.
   - Input: The API returns a 500 error with the message `{"detail": "Failed to retrieve sourcing information."}`.
   - Outcome: The `SourcingBadge` displays an error message: "Sourcing information unavailable."
5. **Scenario:** The API is loading.
   - Input: The API request is in progress.
   - Outcome: The `SourcingBadge` displays "Loading..."

## Stitch UI Prompt

```text
// Target Component: SourcingBadge
// Description: Displays a badge indicating the sourcing status of a product
// Layout: Inline element, rendered within a product detail view
// Style: Dark mode, Tailwind CSS
// Visual Hierarchy: Secondary importance, badge should be noticeable but not distracting
// Data Slots:
//  - status: string ("Ethically Sourced", "Partially Sourced", "Unknown Sourcing", "Loading", "Error")
// States:
//  - Ethically Sourced: Badge with green background and white text.
//  - Partially Sourced: Badge with yellow background and dark text.
//  - Unknown Sourcing: Badge with red background and white text.
//  - Loading: Badge with gray background and gray text, displaying "Loading...".
//  - Error: Badge with red background and white text, displaying "Sourcing information unavailable.".
// Tailwind CSS Classes:
//  - General: inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium
//  - Ethically Sourced: bg-green-500 text-white
//  - Partially Sourced: bg-yellow-500 text-slate-900
//  - Unknown Sourcing: bg-red-500 text-white
//  - Loading: bg-zinc-700 text-zinc-300
// Spacing: No specific spacing requirements
// Accessibility: Ensure sufficient color contrast for readability

// Example:  If status is "Ethically Sourced", the generated code should resemble:

<span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-green-500 text-white">
  Ethically Sourced
</span>
```

## Verification Commands

- `pnpm tsc --noEmit`
- `pnpm run lint`
- `pytest backend/tests/test_api.py -v` (Add a pytest to verify the API endpoint returns the correct data.)
