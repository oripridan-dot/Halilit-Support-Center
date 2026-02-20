# Spec: Enhanced Inventory Search Debounce with Throttle

**Version:** 1.4
**Component:** `frontend/src/components/views/InventoryView.tsx`

## Purpose
To enhance the search input debounce in the Inventory Master, improving performance and reducing unnecessary API calls. This directly addresses the "Speed of Service" business goal by integrating a throttling mechanism for improved efficiency and ensuring the initial state is preserved. This enhancement will leverage a dedicated, well-tested `useDebounce` hook and implement a throttling mechanism.

## Requirements
1.  **Debounce Input:** The `filterText` state variable, which is updated by the search input field, MUST be debounced.
2.  **Debounce Time:** The debounce time MUST be set to a maximum of 150 milliseconds.
3.  **Throttling:** Implement a throttling mechanism to prevent excessive API calls during rapid typing, with a throttle time of 300ms. The debounced value should only be processed if a certain time (300ms) has passed since the last API call.
4.  **Preserve Initial State:** The `initialCfpFilter` and `searchQuery` from the `navigationStore` must be applied after the debounced search is applied so the initial search term is not lost.
5.  **Implementation:** Use a pre-built, tested `useDebounce` hook that accepts both a value and a delay.
6.  **API Call Trigger:** The API call to `useConductorCatalog` with the `searchQuery` parameter MUST only be triggered after both the debounced value changes and the throttle time has elapsed.
7.  **No Intermediate Updates:** The Inventory grid MUST NOT re-render with intermediate filter values before the debounce and throttle times have elapsed.
8.  **Existing Code Integrity:** Any modifications must retain the existing functionality and styling of the InventoryView component.

## Behavior Scenarios
1.  **Scenario:** User types "Roland" quickly in the search input.
    -   **Outcome:** The Inventory grid does not update with each keystroke.
    -   **Outcome:** After 150ms of inactivity, AND 300ms since the last API call, the Inventory grid updates to show results for "Roland".
2.  **Scenario:** User pastes a long SKU into the search input.
    -   **Outcome:** The Inventory grid updates only once, 150ms after the paste action is complete, AND 300ms since the last API call.
3.  **Scenario:** User clears the search input.
    -   **Outcome:** After 150ms, AND 300ms since the last API call, the Inventory grid updates to show the full inventory.
4.  **Scenario:** User navigates to the inventory screen with a pre-filled search term and CfP filter.
    -   **Precondition:** `navigationStore.searchQuery` is set to "Fender" and `navigationStore.initialCfpFilter` is `true`.
    -   **Outcome:** After 150ms of loading, the Inventory grid is filtered to "Fender" with the CfP filter applied.
5.  **Scenario:** Rapid typing with a rate faster than 300ms
    -   **Action:** The user types with a rate of 1 character every 100ms, for a total of 5 characters.
    -   **Outcome:** After the initial 150ms debounce, the API is called. The subsequent keystrokes do NOT trigger API calls until 300ms have passed since the last API call.

## Stitch UI Prompt
```text
// Target Component: InventoryView.tsx (search input)
// Description: Modify the search input within the InventoryView component to integrate debouncing and throttling to improve performance.
// Layout: The search input is typically located within a header or filter section of the InventoryView.
// Visual Style: Adhere to the existing dark theme of the Halilit Support Center (slate-900 background, blue-500 accents). The search input should have a similar style to other inputs in the application (rounded corners, dark background, light text).
//
// Data Slots:
// - searchInputValue: string (The current value of the search input). This value is updated as the user types.
//
// Instructions:
// 1.  Locate the search input element within the InventoryView component.
// 2.  Wrap the search input's `onChange` event handler with a debouncing function that waits 150ms after the last keystroke before updating the `filterText` state variable. This hook is already available: useDebounce(value, delay)
// 3. Implement a throttling mechanism using `useRef` and `setTimeout` to limit API calls to once every 300ms.
// 4.  Ensure that the initial state of the search input (taken from `navigationStore.searchQuery` and `navigationStore.initialCfpFilter`) is correctly applied.
// 5. Maintain existing Tailwind CSS classes.
// Component Hierarchy:
// InventoryView
//  |- Header/Filter Section
//   |- Search Input (modified)
// Spacing: Maintain existing spacing around the search input.

```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
