import { useCallback, useRef } from 'react';

interface UseDebounceThrottleOptions {
    debounceWait: number;
    throttleWait: number;
}

export function useDebounceThrottle<T extends (...args: any[]) => any>(
    func: T,
    debounceWait: number,
    throttleWait: number
): T {
    const timeoutRef = useRef<NodeJS.Timeout | null>(null);
    const lastCallTimeRef = useRef<number>(0);
    const throttledArgsRef = useRef<any[] | null>(null);
    const throttledResultRef = useRef<any>(null);

    const debouncedThrottled = useCallback(
        (...args: Parameters<T>): void => {
            const now = Date.now();
            const shouldThrottle = throttleWait > 0 && now - lastCallTimeRef.current < throttleWait;

            if (shouldThrottle) {
                throttledArgsRef.current = args;
                return;
            }

            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }

            if (throttleWait > 0) {
                lastCallTimeRef.current = now;
            }

            const execute = () => {
                throttledResultRef.current = func(...(throttledArgsRef.current || args));
                throttledArgsRef.current = null;
                if (throttleWait > 0) {
                    lastCallTimeRef.current = Date.now();
                }
            };


            if (debounceWait > 0) {
                timeoutRef.current = setTimeout(() => {
                    execute();
                }, debounceWait);
            } else {
                execute();
            }
        },
        [func, debounceWait, throttleWait]
    ) as T;

    return debouncedThrottled;
}