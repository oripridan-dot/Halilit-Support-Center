# Spec: Enhanced Inventory Search Debounce with Throttle

**Version:** 1.3
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
    -   **Outcome:** The Inventory grid updates only once, 150ms after the paste action is complete, AND 300ms since the last API call.
3.  **Scenario:** User clears the search input.
    -   **Outcome:** After 150ms, AND 300ms since the last API call, the Inventory grid updates to show the full inventory.
4.  **Scenario:** User navigates to the inventory screen with a pre-filled search term.
    -   **Precondition:** `navigationStore.searchQuery` is set to "Fender".
    -   **Outcome:** After 150ms of loading, AND 300ms since the last API call, the Inventory grid is filtered to "Fender".

## Stitch UI Prompt
```text
// Target Component: InventoryView (specifically the search input)
// Description: Modify the search input in InventoryView to incorporate both debounce and throttle.

// Layout: The InventoryView uses a Flexbox layout for the search input and other filters. The search input should be positioned at the top, spanning the full width available.

// Visual Style:
// - Dark mode: Use Tailwind CSS classes to maintain the dark theme.
// - Input field: slate-900 background, slate-300 text, rounded corners, a subtle border, and appropriate padding.
// - Focus state: A blue-500 outline on focus.

// Component Hierarchy:
// - The search input is a direct child of a div element using Flexbox.
// - Ensure proper spacing between the search input and other elements using Tailwind CSS margin or padding classes.

// Data Slots:
// - The search input's value is bound to the `filterText` state variable.
// - The placeholder text is "Search by SKU, Brand, or Name".

// Instructions:
// 1. Implement debouncing using a custom hook (useDebouncedValue) with a debounce time of 150ms.
// 2. Implement throttling using useRef and setTimeout within a custom hook (useThrottledValue) with a throttle time of 300ms.
// 3. Ensure that the API call to useConductorCatalog with the searchQuery parameter is only triggered after both the debounced value changes and the throttle time has elapsed.
// 4. Apply the initialCfpFilter and searchQuery from the navigationStore after the debounced search is applied to maintain initial state.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
