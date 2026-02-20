/**
 * Alias of useDebounce — named useDebounceValue for compatibility with
 * components that import by this name (e.g. InventoryView).
 *
 * Returns a debounced copy of `value` that only updates after `delay` ms
 * of inactivity. Debounce delay for search inputs should be ≤ 150 ms per
 * the Master Plan Speed of Service requirement.
 */
export { useDebounce as useDebounceValue } from './useDebounce';
