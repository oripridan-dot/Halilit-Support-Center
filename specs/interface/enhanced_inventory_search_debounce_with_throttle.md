# Spec: Enhanced Inventory Search Debounce with Throttle
**Target:** frontend/src/components/InventorySearch.tsx

## Overview
This specification outlines the implementation of an enhanced inventory search component featuring both debounce and throttle mechanisms to optimize search performance and reduce unnecessary API calls to the Halilit Support Center backend.  The component will allow users to search for inventory items by name or description, incorporating debounce to prevent rapid, successive requests during typing, and throttle to limit the maximum request frequency, improving the user experience and backend system load.

## Requirements
- The component should provide a text input field for users to enter search queries.
- The search functionality should incorporate a debounce mechanism with a delay of 300ms, preventing rapid requests while the user is typing.
- The search functionality should also incorporate a throttle mechanism, limiting the maximum request frequency to once every 500ms, even if the debounced function is triggered more frequently.
- The component should display a loading indicator while a search request is in progress.
- The component should call the `/api/inventory/search` endpoint with the search query as a parameter.
- The component should display the search results in a clear and concise manner. Assume the results are simply a list of strings (inventory item names).
- The component should handle the case where no search results are found, displaying an appropriate message.
- The component should use Tailwind CSS for styling, adhering to the dark theme (slate-900 background, blue-500 primary action color).
- The component must be implemented using React 18 and TypeScript.
- The component should be self-contained and reusable within the Halilit Support Center application.

## Data Contract

**Input Props:**

```typescript
interface InventorySearchProps {
  onResults: (results: string[]) => void; // Callback function to pass search results to the parent component.
  onError: (error: string) => void; // Callback function to handle errors during the search process.
}
```

**API Request:**

*   Endpoint: `/api/inventory/search`
*   Method: `GET`
*   Query Parameters:
    *   `query: string` - The search query entered by the user.

**API Response:**

*   Success (200 OK):

```json
{
  "results": ["Item A", "Item B", "Item C"]
}
```

*   Failure (400 Bad Request - e.g., invalid query):

```json
{
  "detail": "Invalid search query."
}
```

*   Failure (500 Internal Server Error):

```json
{
  "detail": "Internal server error."
}
```

## Behavior Scenarios

- **Scenario:** User types "widget" quickly.
  - Input: User types "widget" in the search input field, with characters entered rapidly.
  - Outcome: The debounce mechanism waits 300ms after the last character is typed. The throttle mechanism ensures that only one API call is made within a 500ms window. If the user types "widget", then pauses for > 300ms, then continues typing " 123", the search will be triggered for both terms (widget and widget 123), but separated by at least 500ms.

- **Scenario:** User types a query, receives results.
  - Input: User types "halilit" and pauses.  `/api/inventory/search?query=halilit` returns `{"results": ["Halilit X1", "Halilit Y2"]}`.
  - Outcome: The `onResults` callback is called with `["Halilit X1", "Halilit Y2"]`. The parent component displays "Halilit X1" and "Halilit Y2" as the search results.

- **Scenario:** User types a query, receives no results.
  - Input: User types "nonexistent" and pauses. `/api/inventory/search?query=nonexistent` returns `{"results": []}`.
  - Outcome: The `onResults` callback is called with `[]`. The parent component displays "No results found."

- **Scenario:** API returns an error.
  - Input: User types "error" and pauses. `/api/inventory/search?query=error` returns a 500 Internal Server Error with `{"detail": "Simulated server error"}`.
  - Outcome: The `onError` callback is called with `"Simulated server error"`. The parent component displays an error message indicating the search failed.

- **Scenario:** Rapid typing exceeding throttle limit
  - Input: User continuously types with very short pauses between characters.
  - Outcome: The search API is called no more frequently than once every 500ms, ensuring the throttle limit is respected even with the debounced function triggering more often. The loading indicator is displayed while waiting for each throttled search result.

## Out of Scope
- This spec does not cover pagination of search results.  It's assumed all results fit on one page.
- This spec does not cover any specific error handling UI within the `InventorySearch` component itself, only the propagation of errors via the `onError` prop.  The parent component is responsible for displaying error messages.
- Authentication and authorization are assumed to be handled elsewhere. The component should not manage any user credentials.
- This spec doesn't cover i18n/localization.
