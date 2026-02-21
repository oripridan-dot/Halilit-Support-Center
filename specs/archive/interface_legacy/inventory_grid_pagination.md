# Spec: Inventory Grid Pagination

**Target:** src/components/InventoryGrid/InventoryGridPagination.tsx

## Overview
This component provides pagination controls for the Inventory Grid, allowing users to navigate through pages of inventory items. It displays the current page number and the total number of pages, and provides buttons for navigating to the next, previous, first, and last pages.

## Requirements
- Must display the current page number and total number of pages.
- Must provide buttons to navigate to the previous page, next page, first page, and last page.
- The "previous" and "first" page buttons should be disabled on the first page.
- The "next" and "last" page buttons should be disabled on the last page.
- Clicking a pagination button must trigger a callback function that updates the current page number in the parent component.
- The component must be visually styled to fit within the dark theme of the Halilit Support Center.
- Should handle edge cases where totalItems is zero or negative.
- The page size is fixed at 25 items per page. This value is an internal constant.

## Data Contract

**Props:**

```typescript
interface InventoryGridPaginationProps {
  currentPage: number;
  totalItems: number;
  onPageChange: (page: number) => void;
}
```

- `currentPage`: The current page number (1-indexed).  Type: `number`.
- `totalItems`: The total number of inventory items. Type: `number`.
- `onPageChange`: A callback function that is called when the user clicks a pagination button.  It receives the new page number (1-indexed) as an argument. Type: `(page: number) => void`.

## Behavior Scenarios

- **Scenario:** Initial Load - First Page
  - Input: `currentPage = 1`, `totalItems = 50`
  - Outcome:
    - Displayed text: "Page 1 of 2"
    - "Previous" and "First" buttons are disabled.
    - "Next" and "Last" buttons are enabled.

- **Scenario:** Navigating to Next Page
  - Input: `currentPage = 1`, `totalItems = 50`, User clicks "Next"
  - Outcome: `onPageChange(2)` is called.

- **Scenario:** Navigating to Last Page
  - Input: `currentPage = 1`, `totalItems = 50`, User clicks "Last"
  - Outcome: `onPageChange(2)` is called.

- **Scenario:** Navigating to Previous Page
  - Input: `currentPage = 2`, `totalItems = 50`, User clicks "Previous"
  - Outcome: `onPageChange(1)` is called.

- **Scenario:** Navigating to First Page
  - Input: `currentPage = 2`, `totalItems = 50`, User clicks "First"
  - Outcome: `onPageChange(1)` is called.

- **Scenario:** On Last Page
  - Input: `currentPage = 2`, `totalItems = 50`
  - Outcome:
    - Displayed text: "Page 2 of 2"
    - "Next" and "Last" buttons are disabled.
    - "Previous" and "First" buttons are enabled.

- **Scenario:** No Items
  - Input: `currentPage = 1`, `totalItems = 0`
  - Outcome:
    - Displayed text: "Page 1 of 1"
    - All buttons are disabled.

- **Scenario:** One Item
  - Input: `currentPage = 1`, `totalItems = 1`
  - Outcome:
    - Displayed text: "Page 1 of 1"
    - All buttons are disabled.

- **Scenario:** Total Items Less Than Page Size
  - Input: `currentPage = 1`, `totalItems = 20`
  - Outcome:
    - Displayed text: "Page 1 of 1"
    - All buttons are disabled.

- **Scenario:** Invalid Current Page
    - Input: `currentPage = -1`, `totalItems = 50`
    - Outcome: `currentPage` is defaulted to 1 internally. Displayed text: "Page 1 of 2".  "Previous" and "First" buttons are disabled.  "Next" and "Last" buttons are enabled.

- **Scenario:** Invalid Total Items
    - Input: `currentPage = 1`, `totalItems = -10`
    - Outcome: `totalItems` is defaulted to 0 internally.  Displayed text: "Page 1 of 1". All buttons are disabled.

## Out of Scope
- Styling of the Inventory Grid itself.
- Fetching the inventory data.
- Error handling beyond the defaulting of invalid `currentPage` or `totalItems` values.
