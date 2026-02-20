import { useEffect, useRef } from 'react';

/**
 * useDebounce — fires `callback` after `delay` ms of inactivity.
 * Deps array mirrors useEffect convention.
 */
export function useDebounce(
    callback: () => void,
    delay: number,
    deps: React.DependencyList
): void {
    const callbackRef = useRef(callback);

    // Keep callback ref current so stale closures don't cause bugs
    useEffect(() => {
        callbackRef.current = callback;
    });

    useEffect(() => {
        const handler = setTimeout(() => {
            callbackRef.current();
        }, delay);

        return () => clearTimeout(handler);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [delay, ...deps]);
}
