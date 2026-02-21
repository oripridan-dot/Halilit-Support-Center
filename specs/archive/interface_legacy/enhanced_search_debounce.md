# Spec: Enhanced Search Debounce

**Target:** src/components/SearchInput.tsx

## Overview
This specification outlines the implementation of a debounced search input component for the Halilit Support Center's Dark Factory interface. The goal is to reduce unnecessary API calls by delaying the search execution until the user has stopped typing for a specified duration, improving performance and conserving resources.

## Requirements
- The component should be a reusable React component written in TypeScript.
- The component should use Tailwind CSS for styling, adhering to the dark theme (slate-900/blue-500 palette).
- The component should accept a callback function as a prop, which will be executed after the debounce delay.
- The component should implement a debounce mechanism with a configurable delay.  The default delay should be 300ms.
- The component should visually indicate when it is actively waiting for the debounce delay.
- The component should include an accessible label for the search input.
- The component should handle empty search queries gracefully (no API call).

## Data Contract
```typescript
interface SearchInputProps {
  onSearch: (query: string) => void;
  debounceDelay?: number; // Optional debounce delay in milliseconds. Defaults to 300ms.
  placeholder?: string; // Optional placeholder text for the input field. Defaults to "Search...".
  ariaLabel: string; // Required aria-label for accessibility.
}
```

## Behavior Scenarios
- **Scenario:** Initial Load
  - Input: Component is mounted with `onSearch` prop, `ariaLabel="Search for Parts"`.
  - Outcome: A search input field is rendered with placeholder "Search...", aria-label "Search for Parts", and debounce delay of 300ms. The input field's value is empty.

- **Scenario:** Typing a Query (short pause)
  - Input: User types "Halilit" with a pause of 100ms between each character.
  - Outcome: The `onSearch` function is NOT called after typing "H", "Ha", "Hal", "Hali", "Halil", "Halili", "Halilit" due to the short pauses.

- **Scenario:** Typing a Query (long pause)
  - Input: User types "Halilit" and then pauses for 500ms.
  - Outcome: The `onSearch` function is called with the query "Halilit" 300ms (the debounce delay) after the last keypress.

- **Scenario:** Clearing the Input
  - Input: User types "Halilit" and then clears the input field (e.g., by deleting all characters).
  - Outcome: The `onSearch` function is called with an empty string ("") 300ms after the last keypress (delete).

- **Scenario:** Debounce Delay Customization
  - Input: Component is mounted with `onSearch` prop and `debounceDelay={500}`. User types "Halilit" and then pauses for 600ms.
  - Outcome: The `onSearch` function is called with the query "Halilit" 500ms after the last keypress.

- **Scenario:** Input Field Styling and Accessibility
  - Input: Component is rendered with `ariaLabel="Find a product"`, `placeholder="Enter product name"`.
  - Outcome: The input field has the specified placeholder text and aria-label. The input field is styled according to Tailwind CSS dark theme (slate-900 background, blue-500 focus ring).

## Out of Scope
- Integration with a specific search API. The `onSearch` prop provides the query; how it's used is outside the component's scope.
- Advanced search features such as auto-completion or suggestions.
- Error handling within the `onSearch` function.

```typescript
// src/components/SearchInput.tsx
import React, { useState, useCallback, useEffect } from 'react';

interface SearchInputProps {
  onSearch: (query: string) => void;
  debounceDelay?: number;
  placeholder?: string;
  ariaLabel: string;
}

const SearchInput: React.FC<SearchInputProps> = ({ onSearch, debounceDelay = 300, placeholder = "Search...", ariaLabel }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isWaiting, setIsWaiting] = useState(false);

  const debouncedSearch = useCallback(
    (query: string) => {
      setIsWaiting(true); // Indicate waiting state
      const timer = setTimeout(() => {
        onSearch(query);
        setIsWaiting(false); // Reset waiting state after call
      }, debounceDelay);

      return () => clearTimeout(timer);
    },
    [onSearch, debounceDelay]
  );

  useEffect(() => {
    if (searchTerm.length === 0) {
        const timerId = debouncedSearch("");
        return () => timerId();
    } else {
        const timerId = debouncedSearch(searchTerm);
        return () => timerId();
    }
  }, [searchTerm, debouncedSearch]);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  return (
    <div className="relative">
      <input
        type="text"
        className="w-full px-4 py-2 bg-slate-900 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200"
        placeholder={placeholder}
        aria-label={ariaLabel}
        value={searchTerm}
        onChange={handleChange}
        disabled={isWaiting}
      />
       {isWaiting && (
         <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
           <svg className="animate-spin h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
             <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
             <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
           </svg>
         </div>
       )}
    </div>
  );
};

export default SearchInput;
```
