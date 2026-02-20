# Spec: Enhanced Inventory Search Debounce with Throttle

**Version:** 1.0
**Component:** `frontend/src/components/views/InventoryView.tsx`

## Purpose
To enhance the search input debounce in the Inventory Master, improving performance and reducing unnecessary API calls, and ensuring the initial state is not lost when a debounced value is applied. This directly addresses the "Speed of Service" business goal and integrates a throttling mechanism for improved efficiency.

## Requirements
1.  **Debounce Input:** The `filterText` state variable, which is updated by the search input field, MUST be debounced.
2.  **Debounce Time:** The debounce time MUST be set to a maximum of 150 milliseconds.
3.  **Throttling:** Implement a throttling mechanism to prevent excessive API calls during rapid typing, with a throttle time of 300ms. The debounced value should only be processed if a certain time (300ms) has passed since the last API call.
4.  **Preserve Initial State:** The `initialCfpFilter` and `searchQuery` from the `navigationStore` must be applied after the debounced search is applied so the initial search term is not lost.
5.  **Implementation:** Use `useDebouncedValue` hook for debouncing. Implement a separate throttling mechanism using `useRef` and `setTimeout` within a custom hook.
6.  **API Call Trigger:** The API call to `useConductorCatalog` with the `searchQuery` parameter MUST only be triggered after both the debounced value changes and the throttle time has elapsed.
7.  **No Intermediate Updates:** The Inventory grid MUST NOT re-render with intermediate filter values before the debounce and throttle times have elapsed.

## Behavior Scenarios
1.  **Scenario:** User types "Roland" quickly in the search input.
    -   **Outcome:** The Inventory grid does not update with each keystroke.
    -   **Outcome:** After 150ms of inactivity, and 300ms since last api call, the Inventory grid updates to show results for "Roland".
2.  **Scenario:** User pastes a long SKU into the search input.
    -   **Outcome:** The Inventory grid updates only once, 150ms after the paste action is complete, if 300ms have elapsed since the last API call.
3.  **Scenario:** User clears the search input.
    -   **Outcome:** After 150ms, and 300ms since last api call, the Inventory grid updates to show the full inventory.
4.  **Scenario:** User navigates to the inventory screen with a pre-filled search term.
    -   **Precondition:** `navigationStore.searchQuery` is set to "Fender".
    -   **Outcome:** After 150ms of loading, the Inventory grid is filtered to "Fender".
5. **Scenario:** API call takes longer than the throttle time.
    - **Precondition:** The API is delayed due to network conditions.
    - **Outcome:** The next debounced value is not processed until the previous API call returns, ensuring API calls are not made faster than the throttle time.

## Stitch UI Prompt
```text
// Target Component: InventoryView
// Description: A React component for displaying and filtering a product inventory grid.
// Layout: Bento Grid with a search input and a table displaying product information.
// Visual Style: Dark mode, Tailwind CSS, slate-900 background, blue-500 accents.
// Data Slots:
// - Product Rows: Each row displays product information (name, brand, price, stock) based on the filtered catalog data. Use placeholder data for now.
// - Search Input: A text input field for filtering the product list by name, brand, or SKU.
// - Brand Filter Dropdown: A dropdown to filter by brand.
// - Category Filter Dropdown: A dropdown to filter by category.
// - CfP Toggle: A toggle to filter by Call for Price items only.
// Component Hierarchy:
// - InventoryView (root)
//   - Search Input
//   - Brand Filter Dropdown
//   - Category Filter Dropdown
//   - CfP Toggle
//   - Product Table
//     - Table Header (sortable columns)
//     - Table Rows (product data)
// Spacing: Use Tailwind CSS spacing utilities (e.g., p-4, m-2, space-x-2, space-y-2) for consistent spacing between elements.  Use dark mode Tailwind color tokens for consistent styling (e.g. slate-900, blue-500, zinc-700). Ensure accessibility by providing labels for form elements.
// Functionality: Implement debounced search and throttle API calls.

// Search Input:
// - Use the Search icon from lucide-react inside the search input.
// - Placeholder text: "Search products..."
// - Styling: Use Tailwind CSS for styling, including rounded corners, dark background, and appropriate text color.

// Dropdowns:
// - Use the Select component from react-select for brand and category filters.
// - Placeholder text: "Select Brand..." and "Select Category..."
// - Styling: Use Tailwind CSS for styling, including rounded corners, dark background, and appropriate text color.

// CfP Toggle:
// - Use a simple checkbox input for the CfP toggle.
// - Label: "Call for Price Only"
// - Styling: Use Tailwind CSS for styling, including rounded corners, dark background, and appropriate text color.

// Product Table:
// - Use a simple HTML table to display product information.
// - Columns: Name, Brand, Price, Stock
// - Styling: Use Tailwind CSS for styling, including striped rows, dark background, and appropriate text color.
// - Implement sorting for each column (Name, Brand, Price) using ChevronUp and ChevronDown icons from lucide-react.
// - Implement a "Call for Price" indicator with a Phone icon from lucide-react for products with a price of null or 0.
// - Implement Stock badges for "In Stock", "Out of Stock", and "Unknown" stock status. Use Package icon from lucide-react in the badge.

// Data Slots:
// - Each product row should have the following data slots:
//   - Product Name: "Product Name Placeholder"
//   - Brand: "Brand Name Placeholder"
//   - Price: "₪999.99"
//   - Stock: "In Stock", "Out of Stock", or "Unknown"

// Use Tailwind color tokens (e.g., slate-900, blue-500, zinc-700) for consistent styling.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
