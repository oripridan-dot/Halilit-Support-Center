# Spec: Enhanced Inventory Search Debounce with Throttle

**Version:** 1.2
**Component:** `frontend/src/components/views/InventoryView.tsx`

## Purpose
To enhance the search input debounce in the Inventory Master, improving performance and reducing unnecessary API calls. This directly addresses the "Speed of Service" business goal by integrating a throttling mechanism for improved efficiency and ensuring the initial state is preserved.

## Requirements
1.  **Debounce Input:** The `filterText` state variable, which is updated by the search input field, MUST be debounced.
2.  **Debounce Time:** The debounce time MUST be set to a maximum of 150 milliseconds.
3.  **Throttling:** Implement a throttling mechanism to prevent excessive API calls during rapid typing, with a throttle time of 300ms. The debounced value should only be processed if a certain time (300ms) has passed since the last API call.
4.  **Preserve Initial State:** The `initialCfpFilter` and `searchQuery` from the `navigationStore` must be applied after the debounced search is applied so the initial search term is not lost.
5.  **Implementation:** Use `useDebouncedValue` hook for debouncing. Implement a separate throttling mechanism using `useRef` and `setTimeout` within a custom hook (e.g., `useThrottledValue`).
6.  **API Call Trigger:** The API call to `useConductorCatalog` with the `searchQuery` parameter MUST only be triggered after both the debounced value changes and the throttle time has elapsed.
7.  **No Intermediate Updates:** The Inventory grid MUST NOT re-render with intermediate filter values before the debounce and throttle times have elapsed.

## Behavior Scenarios
1.  **Scenario:** User types "Roland" quickly in the search input.
    -   **Outcome:** The Inventory grid does not update with each keystroke.
    -   **Outcome:** After 150ms of inactivity, AND 300ms since the last API call, the Inventory grid updates to show results for "Roland".
2.  **Scenario:** User pastes a long SKU into the search input.
    -   **Outcome:** The Inventory grid updates only once, 150ms after the paste action is complete and 300ms since the last API call.
3.  **Scenario:** User clears the search input.
    -   **Outcome:** After 150ms and 300ms since the last api call, the Inventory grid updates to show the full inventory.
4. **Scenario:** User navigates to the inventory screen with a pre-filled search term and CfP filter.
    -   **Precondition:** `navigationStore.searchQuery` is set to "Fender" and `navigationStore.initialCfpFilter` is true.
    *   **Outcome:** After 150ms of loading, the Inventory grid is filtered to "Fender" and the CfP filter is enabled.

## Stitch UI Prompt

```text
// Target Component: InventoryView (search input and grid)
// Description: Implement enhanced debounce and throttling for the inventory search input.
// Layout: The InventoryView consists of a search input field, a CfP filter toggle, and an inventory grid.
// Visual Style: Use Tailwind CSS for styling, adhering to the dark theme (slate-900 background, blue-500 accents).
//   - The search input should have a dark background (slate-800), light text (zinc-300), and a subtle border (zinc-700).
//   - The CfP filter toggle should use blue-500 for the active state and zinc-500 for the inactive state.
//   - The inventory grid rows should have a dark background (slate-900) and light text (zinc-200).
//
// Component Hierarchy:
//   - InventoryView
//     - SearchInput (with debounced and throttled input)
//     - CfPFilterToggle
//     - InventoryGrid
//
// Data Slots:
//   - SearchInput:
//     - Placeholder: "Search by SKU, Brand, or Name..."
//   - CfPFilterToggle:
//     - Label: "Call for Price Only"
//   - InventoryGrid:
//     - Product Data (from useConductorCatalog hook)
//       - product.id (SKU)
//       - product.name (Product Name)
//       - product.brand (Brand)
//       - product.price (Price)
//       - product.stock (Stock Level)
//
// Spacing: Use Tailwind CSS spacing utilities (e.g., p-4, m-2, gap-2) to create appropriate spacing between elements.
// Interaction:
//   - The search input should update the inventory grid after a 150ms debounce and 300ms throttle.
//   - The CfP filter toggle should immediately update the inventory grid.
//
// Custom Hooks:
//   - Implement a `useThrottledValue` hook that takes a value and a delay as input and returns a throttled value.
//     - Use `useRef` to store the last API call timestamp.
//     - Use `setTimeout` to implement the throttling logic.
//   - Implement `useDebouncedValue`
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
