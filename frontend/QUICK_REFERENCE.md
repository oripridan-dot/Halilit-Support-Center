# Quick Reference: Communication Standards

## For Quick Implementation

### 1. Creating a Data-Fetching Hook

```typescript
import { useCallback, useEffect, useState } from "react";
import {
  createAsyncResult,
  type AsyncResult,
} from "../lib/communicationProtocol";

export const useMyData = (id: string): AsyncResult<MyData> => {
  const [data, setData] = useState<MyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const retry = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetch(`/api/${id}`);
      if (!result.ok) throw new Error(`HTTP ${result.status}`);
      setData(await result.json());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Unknown error"));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    retry();
  }, [id, retry]);

  return createAsyncResult(data, loading, error, retry);
};
```

**Usage:**

```typescript
const { data, loading, error, isReady, retry } = useMyData(id);

if (error) return <ErrorComponent message={error.message} onRetry={retry} />;
if (loading) return <Loading />;
if (!isReady) return <Empty />;
return <DisplayData data={data} />;
```

### 2. Creating a Component with Events

```typescript
import { EventHandler, BaseComponentProps } from "../lib/communicationProtocol";

interface MyComponentProps extends BaseComponentProps {
  items: Item[];
  on?: {
    select?: EventHandler<Item>;
    error?: EventHandler<Error>;
  };
}

export const MyComponent: React.FC<MyComponentProps> = ({
  items,
  on,
  className,
}) => {
  const handleSelect = useCallback((item: Item) => {
    try {
      on?.select?.(item);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      on?.error?.(error);
    }
  }, [on]);

  return (
    <div className={className}>
      {items.map(item => (
        <button key={item.id} onClick={() => handleSelect(item)}>
          {item.name}
        </button>
      ))}
    </div>
  );
};
```

**Usage:**

```typescript
<MyComponent
  items={items}
  on={{
    select: (item) => console.log('Selected:', item),
    error: (error) => console.error('Error:', error.message),
  }}
/>
```

### 3. Creating a Store with Actions

```typescript
import { create } from "zustand";

interface MyStoreState {
  items: Item[];
  selectedId: string | null;
  error: Error | null;

  // Actions
  addItem: (item: Item) => void;
  selectItem: (id: string) => void;
  removeItem: (id: string) => void;
  clearError: () => void;
}

export const useMyStore = create<MyStoreState>((set) => ({
  items: [],
  selectedId: null,
  error: null,

  addItem: (item: Item) => {
    if (!item.id) {
      set({ error: new Error("Invalid item") });
      return;
    }
    set((state) => ({
      items: [...state.items, item],
      error: null,
    }));
  },

  selectItem: (id: string) => {
    set((state) => ({
      selectedId: id,
      error: state.items.some((i) => i.id === id)
        ? null
        : new Error("Item not found"),
    }));
  },

  removeItem: (id: string) => {
    set((state) => ({
      items: state.items.filter((i) => i.id !== id),
      selectedId: state.selectedId === id ? null : state.selectedId,
    }));
  },

  clearError: () => set({ error: null }),
}));
```

**Usage:**

```typescript
const { items, selectedId, error, addItem, selectItem } = useMyStore();

// In components:
<button onClick={() => addItem(newItem)}>Add</button>
<button onClick={() => selectItem(item.id)}>Select</button>

{error && <ErrorDisplay message={error.message} />}
```

### 4. Error Boundary Component

```typescript
interface ErrorDisplayProps extends BaseComponentProps {
  message: string;
  onRetry?: () => void;
  recoverable?: boolean;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  message,
  onRetry,
  recoverable = true,
  className,
}) => (
  <div className={`error-boundary ${className}`}>
    <div className="error-message">{message}</div>
    {recoverable && onRetry && (
      <button onClick={onRetry} className="retry-button">
        Retry
      </button>
    )}
  </div>
);
```

### 5. Memoization Best Practices

```typescript
export const ComplexComponent: React.FC<Props> = ({
  items,
  onSelect,
  filterValue,
}) => {
  // Memoize expensive computations
  const sorted = useMemo(() => {
    return items
      .filter(item => item.name.includes(filterValue))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [items, filterValue]);

  // Memoize callbacks passed to children
  const handleSelectItem = useCallback((item: Item) => {
    onSelect?.(item);
  }, [onSelect]);

  // Only update when dependencies change
  useEffect(() => {
    // Do something with sorted items
  }, [sorted]);

  return <div>{/* render sorted */}</div>;
};
```

## Pattern Checklist

```
Before submitting a component:

☐ Component is functional with hooks (no class components)
☐ Props interface defined and extends BaseComponentProps
☐ All data hooks return AsyncResult<T>
☐ Error states handled with retry capability
☐ Loading states properly handled
☐ All callbacks use EventHandler<T> type
☐ useEffect has complete dependency array
☐ Expensive calculations use useMemo
☐ Callbacks passed to children use useCallback
☐ No unused variables (autofix with prettier)
```

## Import Statements

```typescript
// For communication types
import {
  type AsyncResult,
  type EventHandler,
  type BaseComponentProps,
  createAsyncResult,
  createErrorInfo,
} from "../lib/communicationProtocol";

// For state management
import { create } from "zustand";

// For React
import { useCallback, useEffect, useMemo, useState } from "react";

// For navigation
import { useNavigationStore } from "../store/navigationStore";
```

## Common Patterns by Use Case

### When fetching data:

Use `AsyncResult<T>` hook pattern with `retry()`

### When handling user input:

Use `EventHandler<T>` in component props

### When managing app state:

Use Zustand store with validated actions

### When displaying errors:

Use `createErrorInfo()` and error boundary

### When expensive calculation:

Use `useMemo()` with proper dependencies

### When passing callbacks:

Use `useCallback()` with proper dependencies

---

This quick reference covers 95% of common development tasks.
For detailed patterns, see COMPONENT_STANDARDS.ts
