# Spec: Enhanced Inventory Search Debounce with Throttle

**Version:** 1.5
**Component:** `frontend/src/components/views/InventoryView.tsx`

## Purpose
To enhance the search input debounce in the Inventory Master, improving performance and reducing unnecessary API calls. This directly addresses the "Speed of Service" business goal by integrating a throttling mechanism for improved efficiency and ensuring the initial state is preserved. This enhancement will leverage a dedicated, well-tested `useDebounce` hook and implement a throttling mechanism.

## Requirements
1.  **Debounce Input:** The `filterText` state variable, which is updated by the search input field, MUST be debounced.
2.  **Debounce Time:** The debounce time MUST be set to a maximum of 150 milliseconds.
3.  **Throttling:** Implement a throttling mechanism to prevent excessive API calls during rapid typing, with a throttle time of 300ms. The debounced value should only be processed if a certain time (300ms) has passed since the last API call.
4.  **Preserve Initial State:** The `initialCfpFilter` and `searchQuery` from the `navigationStore` must be applied to the search *after* the component has mounted, and *before* any user input is applied, so the initial search term is not lost.  This means using a `useEffect` hook with an empty dependency array to apply the initial state once on component mount.
5.  **Implementation:** Use a pre-built, tested `useDebounce` hook that accepts both a value and a delay. Ensure the hook is imported and used correctly.
6.  **API Call Trigger:** The API call to `useConductorCatalog` with the `searchQuery` parameter MUST only be triggered after both the debounced value changes and the throttle time has elapsed.
7.  **No Intermediate Updates:** The Inventory grid MUST NOT re-render with intermediate filter values before the debounce and throttle times have elapsed.
8.  **Existing Code Integrity:** Any modifications must retain the existing functionality and styling of the InventoryView component.

## Behavior Scenarios
1.  **Scenario:** User types "Roland" quickly in the search input.
    -   **Outcome:** The Inventory grid does not update with each keystroke.
    -   **Outcome:** After 150ms of inactivity, the Inventory grid updates to show results for "Roland".
2.  **Scenario:** User pastes a long SKU into the search input.
    -   **Outcome:** The Inventory grid updates only once, 150ms after the paste action is complete.
3.  **Scenario:** User clears the search input.
    -   **Outcome:** After 150ms, the Inventory grid updates to show the full inventory.
4.  **Scenario:** User navigates to the inventory screen with a pre-filled search term from `navigationStore`.
    -   **Precondition:** `navigationStore.searchQuery` is set to "Fender".
    -   **Outcome:** The `initialCfpFilter` and `searchQuery` from the `navigationStore` are applied on initial component mount via `useEffect` before any debounce logic is applied. After 150ms of loading, the Inventory grid is filtered to "Fender".
5.  **Scenario:** A user rapidly types a search query and then immediately navigates away from the InventoryView.
    * **Outcome:** No further API calls related to the search are made after the user navigates away. Any pending debounced calls are cancelled.

## Stitch UI Prompt
```text
// Target Component: InventoryView
// Description: Enhance the existing search input with debounce and throttle.

// Layout: The existing InventoryView component has a search input field. Maintain the existing layout.
// Visual Style: Keep the existing dark mode Tailwind CSS styling (slate-900 background, blue-500 accents).
// Data Slots:  Connect the search input field to a state variable called `filterText`. This state variable will be debounced and throttled. The `initialCfpFilter` and `searchQuery` from the `navigationStore` must be applied via `useEffect` on mount before `filterText` has any effect.

// Instructions:

// 1. Import and use a `useDebounce` hook.
// 2. Update the `filterText` state variable when the user types in the search input.
// 3. Apply `initialCfpFilter` and `searchQuery` from `navigationStore` on initial component mount.
// 4. Debounce the `filterText` state variable with a debounce time of 150ms.
// 5. Implement a throttling mechanism with a throttle time of 300ms.
// 6. Only trigger the API call to `useConductorCatalog` when both the debounced value changes and the throttle time has elapsed.
// 7. Ensure that the Inventory grid does not re-render with intermediate filter values before the debounce and throttle times have elapsed.
// 8. Any modifications must retain the existing functionality and styling of the InventoryView component.
// 9. Handle the scenario when a user types a search query and immediately navigates away from the InventoryView.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
