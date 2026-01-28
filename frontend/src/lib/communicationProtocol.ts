/**
 * STANDARDIZED COMMUNICATION PROTOCOL v1.0
 * 
 * This file defines the unified patterns for component communication across the app.
 * All components MUST follow these patterns for perfect system sync.
 * 
 * Principles:
 * 1. **Single Source of Truth**: All data flows through zustand store or hooks
 * 2. **Typed Events**: All events are strictly typed via interfaces
 * 3. **Unidirectional Data**: Props down, actions up (via store or callbacks)
 * 4. **Error Handling**: All async operations have error boundaries
 * 5. **Loading States**: All data fetching includes loading/error states
 * 6. **Consistency**: All similar operations use the same patterns
 */

// ============================================================================
// 1. ASYNC DATA LOADING PATTERN - For all hooks that fetch data
// ============================================================================

export interface AsyncState<T> {
    /** The actual data payload */
    data: T | null;
    /** Is currently loading */
    loading: boolean;
    /** Error message if failed, null otherwise */
    error: Error | null;
    /** Retry function for failed operations */
    retry: () => void;
}

export interface AsyncResult<T> extends AsyncState<T> {
    /** Is data ready (loaded and no error) */
    isReady: boolean;
}

/**
 * Standard hook return type for all data-fetching hooks
 * @example
 * const { data: products, loading, error, isReady } = useMyData()
 */
export type UseAsyncReturn<T> = AsyncResult<T>;

// ============================================================================
// 2. EVENT HANDLER PATTERN - For all component callbacks
// ============================================================================

/**
 * Standard event handler signature for actions
 * All callbacks should follow this pattern for consistency
 */
export type EventHandler<TPayload = void> = (payload: TPayload) => void | Promise<void>;

/**
 * Standard event handler with multiple potential values
 * Used when a handler can dispatch different event types
 */
export interface EventDispatcher {
    dispatch<T = unknown>(type: string, payload?: T): void | Promise<void>;
}

// ============================================================================
// 3. COMPONENT PROPS PATTERN - For all components
// ============================================================================

/**
 * Base props all interactive components should have
 */
export interface BaseComponentProps {
    /** CSS class for styling */
    className?: string;
    /** Optional test ID for testing */
    "data-testid"?: string;
}

/**
 * Props for components that emit events
 */
export interface EmitterComponentProps<TEvents extends Record<string, unknown>>
    extends BaseComponentProps {
    /** Event handlers for this component */
    on?: {
        [K in keyof TEvents]?: EventHandler<TEvents[K]>;
    };
}

/**
 * Props for data-consuming components
 */
export interface DataConsumerComponentProps<T> extends BaseComponentProps {
    /** The data to display */
    data: T | null;
    /** Is currently loading */
    loading?: boolean;
    /** Error that occurred */
    error?: Error | null;
}

// ============================================================================
// 4. STORE MUTATION PATTERN - For zustand stores
// ============================================================================

/**
 * Standard pattern for store actions
 * All state changes should be wrapped in action methods
 */
export interface StoreAction<TPayload = void, TReturn = void> {
    (payload: TPayload): TReturn;
}

/**
 * Standard error handler for store operations
 */
export type StoreErrorHandler = (error: Error, context: string) => void;

// ============================================================================
// 5. FORM & INPUT PATTERN - For form components
// ============================================================================

/**
 * Standard form state structure
 */
export interface FormState<TData> {
    /** Current form values */
    values: TData;
    /** Validation errors per field */
    errors: Record<keyof TData, string | null>;
    /** Fields that have been touched/interacted with */
    touched: Record<keyof TData, boolean>;
    /** Is form being submitted */
    submitting: boolean;
}

/**
 * Standard form handlers
 */
export interface FormHandlers<TData> {
    /** Handle field value change */
    handleChange: (field: keyof TData, value: unknown) => void;
    /** Handle field blur */
    handleBlur: (field: keyof TData) => void;
    /** Handle form reset */
    handleReset: () => void;
    /** Handle form submission */
    handleSubmit: (data: TData) => Promise<void>;
}

// ============================================================================
// 6. NAVIGATION PATTERN - For navigation-related components
// ============================================================================

/**
 * Standard navigation event payload
 */
export interface NavigationPayload {
    target: string;
    params?: Record<string, unknown>;
    replace?: boolean;
}

/**
 * Standard navigation handler
 */
export type NavigationHandler = EventHandler<NavigationPayload>;

// ============================================================================
// 7. MODAL/OVERLAY PATTERN - For modal components
// ============================================================================

/**
 * Standard modal state and handlers
 */
export interface ModalState {
    isOpen: boolean;
    data?: unknown;
}

export interface ModalHandlers {
    open: (data?: unknown) => void;
    close: () => void;
    toggle: () => void;
}

// ============================================================================
// 8. LIST SELECTION PATTERN - For lists with selected items
// ============================================================================

/**
 * Standard list selection state
 */
export interface ListSelectionState<T> {
    /** Currently selected item(s) */
    selected: T | T[] | null;
    /** All selectable items */
    items: T[];
    /** Is multi-select enabled */
    multiSelect: boolean;
}

export interface ListSelectionHandlers<T> {
    /** Select single item */
    select: (item: T) => void;
    /** Toggle item (for multi-select) */
    toggle: (item: T) => void;
    /** Clear selection */
    clear: () => void;
}

// ============================================================================
// 9. FILTER PATTERN - For filtering/searching
// ============================================================================

/**
 * Standard filter state
 */
export interface FilterState {
    /** Active filter values */
    active: string[];
    /** Available filter options */
    available: string[];
}

export interface FilterHandlers {
    /** Toggle a filter on/off */
    toggle: (filter: string) => void;
    /** Set multiple filters */
    set: (filters: string[]) => void;
    /** Clear all filters */
    clear: () => void;
}

// ============================================================================
// 10. ERROR BOUNDARY PATTERN - For error handling
// ============================================================================

/**
 * Standard error info structure
 */
export interface ErrorInfo {
    message: string;
    code?: string;
    context?: string;
    timestamp: number;
    recoverable: boolean;
}

/**
 * Error handler function signature
 */
export type ErrorBoundaryHandler = (error: ErrorInfo) => void;

// ============================================================================
// VALIDATION HELPERS - To ensure all code follows the protocol
// ============================================================================

/**
 * Validates that a hook returns AsyncState pattern
 */
export function validateAsyncReturn<T>(value: unknown): value is AsyncResult<T> {
    if (typeof value !== "object" || value === null) return false;
    const obj = value as Record<string, unknown>;
    return (
        typeof obj.data === "object" &&
        typeof obj.loading === "boolean" &&
        (obj.error === null || obj.error instanceof Error) &&
        typeof obj.isReady === "boolean" &&
        typeof obj.retry === "function"
    );
}

/**
 * Creates a standard async result from parts
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

/**
 * Common function to create error info
 */
export function createErrorInfo(
    message: string,
    code?: string,
    context?: string,
    recoverable: boolean = true,
): ErrorInfo {
    return {
        message,
        code,
        context,
        timestamp: Date.now(),
        recoverable,
    };
}
