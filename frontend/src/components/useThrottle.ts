import { useEffect, useRef } from 'react';

/**
 * useThrottle — fires `callback` at most once every `interval` ms.
 * Deps array mirrors useEffect convention.
 */
export function useThrottle(
    callback: () => void,
    interval: number,
    deps: React.DependencyList
): void {
    const lastRunRef = useRef<number>(0);
    const callbackRef = useRef(callback);
    const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    // Keep callback ref current
    useEffect(() => {
        callbackRef.current = callback;
    });

    useEffect(() => {
        const now = Date.now();
        const remaining = interval - (now - lastRunRef.current);

        if (remaining <= 0) {
            if (timerRef.current) {
                clearTimeout(timerRef.current);
                timerRef.current = null;
            }
            lastRunRef.current = now;
            callbackRef.current();
        } else {
            timerRef.current = setTimeout(() => {
                lastRunRef.current = Date.now();
                timerRef.current = null;
                callbackRef.current();
            }, remaining);
        }

        return () => {
            if (timerRef.current) {
                clearTimeout(timerRef.current);
            }
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [interval, ...deps]);
}
