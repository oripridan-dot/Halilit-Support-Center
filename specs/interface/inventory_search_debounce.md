# Spec: Inventory Search Debounce

**Version:** 1.0
**Component:** `frontend/src/components/views/InventoryView.tsx`

## 1. Purpose

To debounce the search input in the Inventory Master, improving performance and reducing unnecessary API calls, thus contributing to the "Speed of Service" business goal.

## 2. Requirements

1.  **Debounce Input:** The `filterText` state variable, which is updated by the search input field, MUST be debounced.
2.  **Debounce Time:** The debounce time MUST be set to a maximum of 150 milliseconds.
3.  **Implementation:** Use `useDebouncedValue` hook or equivalent to debounce the input.
4.  **API Call Trigger:** The API call to `useConductorCatalog` with the `searchQuery` parameter MUST only be triggered after the debounced value changes.
5.  **No Intermediate Updates:** The Inventory grid MUST NOT re-render with intermediate filter values before the debounce time has elapsed.
6.  **Preserve Initial State:** The `initialCfpFilter` and `searchQuery` from the `navigationStore` must be applied after the debounced search is applied so the initial search term is not lost.

## 3. Behavior Scenarios

1.  **Scenario:** User types "Roland" quickly in the search input.
    *   **Outcome:** The Inventory grid does not update with each keystroke.
    *   **Outcome:** After 150ms of inactivity, the Inventory grid updates to show results for "Roland".
2.  **Scenario:** User pastes a long SKU into the search input.
    *   **Outcome:** The Inventory grid updates only once, 150ms after the paste action is complete.
3.  **Scenario:** User clears the search input.
    *   **Outcome:** After 150ms, the Inventory grid updates to show the full inventory.
4. **Scenario:** User navigates to the inventory screen with a pre-filled search term.
    *   **Precondition:** `navigationStore.searchQuery` is set to "Fender".
    *   **Outcome:** After 150ms of loading, the Inventory grid is filtered to "Fender".
