# Search Behavior Scenarios

## Goal
Define expected outcomes for search and navigation. Used for Playwright or manual acceptance tests. We verify *behavior*, not code.

## Scenarios

### Scenario 1: User searches for SKU
- **Action:** User types exact SKU in Global Search (e.g. Command-K or header search).
- **Outcome:** Exact match appears in results.
- **Outcome:** User selects result → Detail View opens for that product.

### Scenario 2: User searches for brand + keyword
- **Action:** User types e.g. "Roland keyboard".
- **Outcome:** Results show products matching "Roland" and "keyboard" (brand + text).
- **Outcome:** Selecting a result opens Detail View.

### Scenario 3: User filters in Inventory then opens product
- **Action:** User is on Inventory Master, applies brand filter, clicks a row.
- **Outcome:** Product Detail opens with correct product. Tabs load; JIT data loads; Verified badges appear when applicable.

### Scenario 4: No results
- **Action:** User searches for a string that matches no product.
- **Outcome:** "No results" or empty state. No crash.

### Scenario 5: Direct navigation to product
- **Action:** User lands on Product Detail via URL or deep link (e.g. /product/123).
- **Outcome:** Product 123 loads. If not found, 404 Product screen with "Back to Search".

## Verification
- Run these as Playwright tests against the built app.
- Pass = all outcomes observed. Fail = at least one outcome missing; fix spec or implementation.
