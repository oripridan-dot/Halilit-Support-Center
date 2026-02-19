import { useState, useEffect } from 'react';

/**
 * Returns a debounced copy of `value` that only updates after `delay` ms
 * of inactivity.  Used by useImageRefresh and any component that needs to
 * throttle rapid state changes before triggering expensive side-effects.
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
