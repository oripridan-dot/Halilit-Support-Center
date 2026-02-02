/**
 * Component Utility Types
 * 
 * Standardized types for component development following COMPONENT_STANDARDS.ts
 */

/**
 * Base props all components should extend
 */
export interface BaseComponentProps {
    className?: string;
}

/**
 * Standard event handler type
 * Use this pattern for all event callbacks
 */
export type EventHandler<T = unknown> = (value: T) => void | Promise<void>;

/**
 * Re-export AsyncResult from communicationProtocol for consistency
 * All data-fetching hooks use this pattern
 */
export type { AsyncResult } from "../lib/communicationProtocol";
export { createAsyncResult } from "../lib/communicationProtocol";

export interface FilterOptions {
    search?: string;
    page?: number;
    pageSize?: number;
}

export interface PaginationInfo {
    page: number;
    pageSize: number;
    total: number;
}
