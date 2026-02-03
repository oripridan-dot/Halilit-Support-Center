/**
 * COMPONENT STANDARDIZATION GUIDE
 *
 * This file documents the standardized patterns all components must follow
 * for perfect system sync and communication.
 */

/**
 * ============================================================================
 * RULE 1: FUNCTIONAL COMPONENTS WITH HOOKS
 * ============================================================================
 *
 * All components must be functional React components using hooks.
 * Avoid class components except for Error Boundaries.
 *
 * @example
 * export const MyComponent: React.FC<MyProps> = ({ prop1 }) => {
 *   return <div>{prop1}</div>;
 * };
 */

/**
 * ============================================================================
 * RULE 2: PROP TYPING WITH INTERFACES
 * ============================================================================
 *
 * All component props must be defined in an interface.
 * Use "Props" or "{ComponentName}Props" naming convention.
 * Always extend BaseComponentProps for styling.
 *
 * @example
 * interface MyComponentProps extends BaseComponentProps {
 *   title: string;
 *   onSelect?: (item: Item) => void;
 *   loading?: boolean;
 * }
 *
 * export const MyComponent: React.FC<MyComponentProps> = ({
 *   title,
 *   onSelect,
 *   loading,
 *   className,
 * }) => { ... }
 */

/**
 * ============================================================================
 * RULE 3: DATA FETCHING WITH STANDARDIZED ASYNC HOOKS
 * ============================================================================
 *
 * All hooks that fetch data MUST return AsyncResult<T>:
 * - data: The actual data (null while loading)
 * - loading: Boolean flag
 * - error: Error object or null
 * - isReady: Convenience flag (data && !loading && !error)
 * - retry: Function to retry failed operations
 *
 * @example
 * export const useMyData = (id: string): AsyncResult<MyData> => {
 *   const [data, setData] = useState<MyData | null>(null);
 *   const [loading, setLoading] = useState(true);
 *   const [error, setError] = useState<Error | null>(null);
 *
 *   const retry = useCallback(async () => {
 *     setLoading(true);
 *     try {
 *       const result = await fetch(...);
 *       setData(result);
 *       setError(null);
 *     } catch (err) {
 *       setError(err instanceof Error ? err : new Error('Unknown error'));
 *     } finally {
 *       setLoading(false);
 *     }
 *   }, [id]);
 *
 *   useEffect(() => { retry(); }, [id, retry]);
 *
 *   return createAsyncResult(data, loading, error, retry);
 * };
 */

/**
 * ============================================================================
 * RULE 4: STATE MANAGEMENT WITH ZUSTAND ACTIONS
 * ============================================================================
 *
 * All store mutations must be wrapped in action functions.
 * Never call `set()` directly from components.
 * Always validate inputs to actions.
 *
 * @example
 * export const useMyStore = create<MyStore>((set) => ({
 *   items: [],
 *
 *   addItem: (item: Item) => {
 *     if (!item.id) throw new Error('Invalid item');
 *     set(state => ({
 *       items: [...state.items, item]
 *     }));
 *   },
 *
 *   removeItem: (id: string) => {
 *     set(state => ({
 *       items: state.items.filter(i => i.id !== id)
 *     }));
 *   }
 * }));
 *
 * // In components:
 * const addItem = useMyStore(state => state.addItem);
 * addItem(newItem); // Never directly call set()
 */

/**
 * ============================================================================
 * RULE 5: EVENT HANDLERS WITH STANDARD SIGNATURES
 * ============================================================================
 *
 * All event callbacks should follow EventHandler<T> pattern.
 * Never pass raw functions without typing.
 * Always provide handlers as optional props.
 *
 * @example
 * interface MyComponentProps {
 *   on?: {
 *     select?: EventHandler<Item>;
 *     change?: EventHandler<string>;
 *     error?: EventHandler<Error>;
 *   };
 * }
 *
 * export const MyComponent: React.FC<MyComponentProps> = ({
 *   on,
 * }) => {
 *   const handleSelect = (item: Item) => {
 *     on?.select?.(item);
 *   };
 *
 *   return <div onClick={() => handleSelect(item)}>...</div>;
 * };
 */

/**
 * ============================================================================
 * RULE 6: ERROR HANDLING IN ALL COMPONENTS
 * ============================================================================
 *
 * Always check for error states and display user-friendly messages.
 * Provide retry/recovery options when possible.
 * Use ErrorBoundary for unexpected errors.
 *
 * @example
 * export const MyComponent: React.FC<MyProps> = ({ on }) => {
 *   const { data, loading, error, retry } = useMyData();
 *
 *   if (error) {
 *     return (
 *       <div className="error-state">
 *         <p>{error.message}</p>
 *         <button onClick={retry}>Retry</button>
 *       </div>
 *     );
 *   }
 *
 *   if (loading) {
 *     return <div>Loading...</div>;
 *   }
 *
 *   return <div>{data}</div>;
 * };
 */

/**
 * ============================================================================
 * RULE 7: PROP DRILLING PREVENTION WITH CONTEXT
 * ============================================================================
 *
 * For deeply nested components sharing state, use React Context.
 * Create a custom hook for accessing context values.
 * Never pass 5+ props through intermediate components.
 *
 * @example
 * const MyContext = createContext<MyContextValue | undefined>(undefined);
 *
 * export const MyContextProvider: React.FC<{ children: ReactNode }> = ({
 *   children,
 * }) => (
 *   <MyContext.Provider value={{}}>
 *     {children}
 *   </MyContext.Provider>
 * );
 *
 * export const useMyContext = () => {
 *   const context = useContext(MyContext);
 *   if (!context) {
 *     throw new Error('useMyContext must be used within MyContextProvider');
 *   }
 *   return context;
 * };
 */

/**
 * ============================================================================
 * RULE 8: MEMOIZATION FOR PERFORMANCE
 * ============================================================================
 *
 * Use useMemo for expensive computations.
 * Use useCallback for event handler callbacks passed to children.
 * Avoid premature optimization; only memoize when necessary.
 *
 * @example
 * export const MyComponent: React.FC<MyProps> = ({ items, onSelect }) => {
 *   // Memoize expensive calculation
 *   const sorted = useMemo(() => {
 *     return items.sort((a, b) => a.name.localeCompare(b.name));
 *   }, [items]);
 *
 *   // Memoize callback to avoid child re-renders
 *   const handleSelect = useCallback((item: Item) => {
 *     onSelect?.(item);
 *   }, [onSelect]);
 *
 *   return renderContent();
 * };
 */

/**
 * ============================================================================
 * RULE 9: DEPENDENCY ARRAYS IN EFFECTS
 * ============================================================================
 *
 * Always include all dependencies in useEffect dependency arrays.
 * Never ignore ESLint warnings about missing dependencies.
 * Use useCallback to wrap functions if they're dependencies.
 *
 * @example
 * // WRONG - missing 'value' dependency
 * useEffect(() => {
 *   console.log(value);
 * }, []); // ESLint error!
 *
 * // CORRECT
 * useEffect(() => {
 *   console.log(value);
 * }, [value]);
 *
 * // CORRECT - wrap in useCallback if used in dependencies
 * const fetchData = useCallback(async () => {
 *   const res = await fetch(`/api/${id}`);
 *   return res.json();
 * }, [id]);
 *
 * useEffect(() => {
 *   fetchData();
 * }, [fetchData]);
 */

/**
 * ============================================================================
 * RULE 10: COMPONENT FILE STRUCTURE
 * ============================================================================
 *
 * Organize component files in this order:
 * 1. Imports
 * 2. Types/Interfaces
 * 3. Helper functions & constants
 * 4. Main component
 * 5. Subcomponents (if small)
 * 6. Export statements
 *
 * @example
 * // MyComponent.tsx
 * import React, { useMemo } from 'react';
 *
 * interface MyComponentProps extends BaseComponentProps {
 *   items: Item[];
 * }
 *
 * const calculateTotal = (items: Item[]): number => {
 *   return items.reduce((sum, item) => sum + item.value, 0);
 * };
 *
 * export const MyComponent: React.FC<MyComponentProps> = ({
 *   items,
 *   className,
 * }) => {
 *   const total = useMemo(() => calculateTotal(items), [items]);
 *   return renderResult(className, total);
 * };
 */

/**
 * ============================================================================
 * QUICK CHECKLIST FOR EVERY COMPONENT
 * ============================================================================
 *
 * BEFORE SUBMITTING ANY COMPONENT, VERIFY:
 * - Component is a functional component with hooks
 * - Props are typed in an interface
 * - All data fetching uses AsyncResult pattern
 * - All callbacks are typed with EventHandler
 * - Error states are handled and displayed
 * - Loading states are handled
 * - useEffect has all dependencies listed
 * - Expensive computations use useMemo
 * - Event handlers use useCallback when passed to children
 * - No console.error calls (use proper error handling)
 */
