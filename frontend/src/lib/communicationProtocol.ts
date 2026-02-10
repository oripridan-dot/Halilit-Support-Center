/**
 * Communication Protocol v2.0 — Simplified
 *
 * Only exports actually used in the codebase are retained.
 * Unused interfaces (FormState, ModalState, ListSelectionState,
 * FilterState, EventDispatcher, etc.) have been removed.
 */

// ============================================================================
// ASYNC DATA LOADING PATTERN
// ============================================================================

export interface AsyncState<T> {
    data: T | null;
    loading: boolean;
    error: Error | null;
    retry: () => void;
}

export interface AsyncResult<T> extends AsyncState<T> {
    isReady: boolean;
}

/**
 * Creates a standard async result from parts.
 */
export function createAsyncResult<T>(
    data: T | null,
    loading: boolean,
    error: Error | null,
    retry: () => void,
): AsyncResult<T> {
    return {
        data,
        loading,
        error,
        isReady: !loading && error === null && data !== null,
        retry,
    };
}

// ============================================================================
// COMPONENT PROPS PATTERN (kept for componentUtils re-export)
// ============================================================================

export interface BaseComponentProps {
    className?: string;
    "data-testid"?: string;
}

export type EventHandler<TPayload = void> = (payload: TPayload) => void | Promise<void>;
