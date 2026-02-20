# Spec: Enhanced Inventory Search Debounce with Throttle

**Version:** 1.1
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
    -   **Outcome:** The Inventory grid updates only once, 150ms after the paste action is complete, and 300ms since last api call.
3.  **Scenario:** User clears the search input.
    -   **Outcome:** After 150ms of inactivity, and 300ms since last api call, the Inventory grid updates to show the full inventory.
4.  **Scenario:** Initial state with CFP filter enabled. User types "Roland" quickly in the search input.
    -   **Precondition:** `navigationStore.initialCfpFilter` is set to `true`.
    -   **Outcome:** The Inventory grid loads with the initial CFP filter enabled.
    -   **Outcome:** The Inventory grid does not update with each keystroke.
    -   **Outcome:** After 150ms of inactivity, and 300ms since last api call, the Inventory grid updates to show results for "Roland" with the CFP filter still enabled.
5.  **Scenario:** User navigates to the inventory screen with a pre-filled search term.
    *   **Precondition:** `navigationStore.searchQuery` is set to "Fender".
    *   **Outcome:** After 150ms of loading, and 300ms since the component mounted, the Inventory grid is filtered to "Fender".

## Stitch UI Prompt

```
// Component: InventoryView (search input)
// Goal: Generate Tailwind CSS + React code for a search input field inside the InventoryView
//       that integrates debouncing (150ms) and throttling (300ms) to reduce API calls.

// Layout:
// - Use a Flexbox layout to position the search input.
// - Add clear button at the end of the search input using lucide-react XCircle icon.

// Style:
// - Dark mode (slate-900 background, blue-500 accents).
// - Use Tailwind CSS classes for styling.
// - Input field: rounded corners, padding, dark text color.

// Data Slots:
// - `placeholder`: "Search inventory..."
// - `searchValue`: [Current search string] (Controlled component).
// - Ensure accessibility (aria-label).

// Component Hierarchy:
// Flexbox Container
//   Input Field
//   Clear Button (Conditional rendering if searchValue is not empty)

// Spacing: Use Tailwind spacing classes (e.g., `mx-2`, `my-1`) for consistent spacing.

// Special Instructions:
// - Implement debouncing using a custom hook with setTimeout.
// - Implement throttling using a useRef and setTimeout.
// - Use a state variable called `filterText` to store the current search input value.
// - The `onChange` event handler should update the `filterText` state.
// - The API call to `useConductorCatalog` with the `searchQuery` parameter should only be triggered
//   after both the debounced value changes and the throttle time has elapsed.
// - Preserve initial state (`navigationStore.initialCfpFilter` and `navigationStore.searchQuery`).
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
