# Spec: Integrate `useDebounceThrottle` Hook for Enhanced Search Debounce
**Version:** 1.0
**Component:** `frontend/src/components/views/InventoryView.tsx`

## Purpose

To replace the existing custom debounce implementation in `InventoryView.tsx` with the reusable `useDebounceThrottle` hook, simplifying the component and improving code maintainability. This directly addresses the "Speed of Service" business goal by ensuring efficient search functionality.

## Requirements

1.  **Import `useDebounceThrottle`:** Import the `useDebounceThrottle` hook from `frontend/src/hooks/useDebounceThrottle.ts` into `InventoryView.tsx`.
2.  **Replace Custom Debounce:** Remove the existing custom debounce logic related to the `filterText` state variable. This includes the `useEffect` hook and any related state variables or helper functions.
3.  **Implement `useDebounceThrottle`:** Utilize the `useDebounceThrottle` hook to debounce the `setFilterText` function. Set the `debounceWait` parameter to 150ms and the `throttleWait` parameter to 0. The throttle is not required here, so we set it to zero to disable.
4.  **Update Filter Logic:** Update the search logic in `InventoryView.tsx` to use the debounced `setFilterText` function. This will ensure that the search query is only updated after the debounce time has elapsed.
5.  **Preserve Initial State:** The `initialCfpFilter` and `searchQuery` from the `navigationStore` must be applied after the debounced search is applied so the initial search term is not lost.
6.  **No Functional Changes:** Ensure that the refactoring does not introduce any functional changes to the search behavior of the Inventory grid. The search results must be the same before and after the refactoring.
7. **Remove `enhanced_inventory_search_debounce_with_throttle.md` and `interface/integrate_usedebouncethrottle_hook_for_enhanced_search_debou.md`:** These files are no longer needed.

## Behavior Scenarios

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

## Stitch UI Prompt
```text
// Target Component: InventoryView
// Description:  Refactor InventoryView.tsx to use the 'useDebounceThrottle' hook instead of the old useEffect implementation.
// Layout: The main layout should remain the same. No changes to the visual structure.
// Visual Style:  Maintain the existing dark theme (slate-900 background, blue-500 accents).  No visual changes are needed.
//
// Key Tasks:
// 1. Replace the old implementation that uses useEffect to update the state variable filterText with the new implementation that uses the 'useDebounceThrottle' hook to update the state variable filterText. The debounce time must be 150 ms.
// 2. The new `setFilterText` should be called in the text input's onChange handler.
//
// Keep all other visual elements and styling identical to the existing component.
// Use Tailwind CSS classes from slate-900, blue-500 scale.
// The goal is to improve search performance by using debouncing.
// Ensure all code is correct TypeScript.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
