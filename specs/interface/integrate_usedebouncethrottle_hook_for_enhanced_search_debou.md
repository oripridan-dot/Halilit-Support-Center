# Spec: Integrate useDebounceThrottle hook for enhanced search debounce
**Version:** 1.0
**Component:** `frontend/src/hooks/useDebounceThrottle.ts`

## Purpose

To create a reusable hook that provides both debouncing and throttling functionalities. This hook can be used in the Inventory Search component and other areas to enhance performance and user experience by limiting the rate at which functions are executed. This will replace `enhanced_inventory_search_debounce_with_throttle.md`, and will be simpler.

## Requirements

-   Create a custom hook `useDebounceThrottle(func: Function, debounceWait: number, throttleWait: number)` that accepts a function, a debounce wait time in milliseconds, and a throttle wait time in milliseconds as input.
-   The hook MUST return a debounced and throttled version of the input function.
-   The debouncing functionality MUST prevent the function from being called more than once in the specified debounce wait time.
-   The throttling functionality MUST ensure that the function is called at most once in the specified throttle wait time, even if the debounced function is called multiple times within the debounce wait time.
-   The hook must be implemented using React 18 with TypeScript.
-   The hook must handle cases where either the debounce or throttle wait time is set to 0, effectively disabling that functionality.
-   The hook must be generic and reusable across different components and functions.

## Behavior Scenarios

-   **Scenario:** Function is called multiple times within the debounce wait time.
    -   Input: `debounceWait = 300`, `throttleWait = 500`, function is called 5 times within 300ms.
    -   Outcome: The function is executed only once, 300ms after the last call.

-   **Scenario:** Function is called multiple times, exceeding the debounce wait time but within the throttle wait time.
    -   Input: `debounceWait = 300`, `throttleWait = 500`, function is called every 200ms for 600ms.
    -   Outcome: The function is executed twice, roughly 500ms apart.

-   **Scenario:** Debounce wait time is 0, throttle wait time is non-zero.
    -   Input: `debounceWait = 0`, `throttleWait = 500`, function is called multiple times.
    -   Outcome: The function is throttled, executing at most once every 500ms.

-   **Scenario:** Throttle wait time is 0, debounce wait time is non-zero.
    -   Input: `debounceWait = 300`, `throttleWait = 0`, function is called multiple times.
    -   Outcome: The function is debounced, executing only after 300ms of inactivity.

-   **Scenario:** Both debounce and throttle wait times are 0.
    -   Input: `debounceWait = 0`, `throttleWait = 0`, function is called multiple times.
    -   Outcome: The function is executed immediately on each call.

## Implementation Notes

1.  Leverage existing `lodash` or similar utility library for debounce and throttle implementations, if appropriate.
2.  Ensure that the returned function has the same signature as the input function.
3.  Provide clear documentation and examples for how to use the hook.

## Stitch UI Prompt
N/A - this is a hook, not a UI component.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- `pytest backend/tests/test_hooks.py -v`
