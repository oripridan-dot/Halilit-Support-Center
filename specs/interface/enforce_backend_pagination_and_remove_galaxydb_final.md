# Spec: Enforce Backend Pagination and Remove GalaxyDB (Final)
**Version:** 3.0
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the critical issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, handles loading states correctly, refactors the use of `ImageWithFallback`, and displays an animated magnifying glass during data fetching.

## Requirements

1.  **Total `galaxy_db.json` Removal:** Physically DELETE the `frontend/public/data/galaxy_db.json` file.
2.  **`useConductorCatalog` Dependency Isolation:** Ensure the `useConductorCatalog` hook *solely* relies on the `/api/conductor/catalog` endpoint for data. It must NOT attempt to import or read `galaxy_db.json` under any circumstances.
3.  **Backend Pagination Endpoint:** Verify that the `/api/conductor/catalog` endpoint correctly accepts `page`, `pageSize`, `searchQuery`, `sortBy`, `category`, and `brand` query parameters and returns a paginated subset of the catalog data, along with metadata about the total number of items and pages. The backend should default `pageSize` to 25 if not specified, and if `page` is not specified, it should default to 1. If sorting parameters are being passed, preserve them.
4.  **Data Contract Validation:** Ensure the data contract for `/api/conductor/catalog` includes pagination metadata:

    ```typescript
    interface PaginatedCatalogResponse {
      products: ConductorProduct[];
      totalItems: number;
      totalPages: number;
      currentPage: number;
      pageSize: number;
    }
    ```

5.  **`useConductorCatalog` Hook Implementation:** Ensure the `useConductorCatalog` hook:
    *   Accepts optional `page`, `pageSize`, `searchQuery`, `sortBy`, `category`, and `brand` parameters with default values of `1`, `25`, `''`, `''`, `''`, and `''` respectively.
    *   Fetches data from the paginated `/api/conductor/catalog` endpoint using the provided parameters.
    *   Returns the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize` from the API response.
    *   Uses `react-query` to manage the fetching and caching of paginated data.
6.  **Filtering and Sorting Parameters:** The `useConductorCatalog` hook must pass the filter and sort state as parameters to the API endpoint.
7.  **Error Handling:** Maintain existing error handling for API requests, displaying error messages to the user if the data cannot be fetched. Render a "retry" banner on API failure.
8.  **Image Fallback:** Refactor the usage of the `ImageWithFallback` component to ensure a consistent image loading experience, including the existing fallback logic.
9.  **Animated Loading State:** Display an animated magnifying glass icon while fetching data, providing a visually engaging loading state. Use `framer-motion` for smooth animation. The magnifying glass should scale up and down subtly.
10. **Skeleton Loading:** Use skeleton loaders for all UI elements that depend on catalog data. This should be shown while the catalog data is fetching.

## Behavior Scenarios

1.  **Scenario:** Initial Load
    *   Input: `page = 1`, `pageSize = 25`, no search query, no filters, no sorting.
    *   Outcome: The hook fetches the first 25 products from the `/api/conductor/catalog` endpoint. The animated magnifying glass icon and skeleton loaders are displayed during the fetch. The hook returns the `products` array, `totalItems`, `totalPages`, `currentPage = 1`, and `pageSize = 25`.
2.  **Scenario:** Navigating to the Next Page
    *   Input: `page = 2`, `pageSize = 25`, no search query, no filters, no sorting.
    *   Outcome: The hook fetches the next 25 products from the `/api/conductor/catalog` endpoint. The animated magnifying glass icon and skeleton loaders are displayed during the fetch. The hook returns the `products` array, `totalItems`, `totalPages`, `currentPage = 2`, and `pageSize = 25`.
3.  **Scenario:** Applying a Search Query
    *   Input: `page = 1`, `pageSize = 25`, `searchQuery = "Roland"`, no filters, no sorting.
    *   Outcome: The hook fetches the first 25 products matching the search query "Roland" from the `/api/conductor/catalog` endpoint, passing `searchQuery = "Roland"` as a parameter. The animated magnifying glass icon and skeleton loaders are displayed during the fetch. The hook returns the filtered `products` array, `totalItems`, `totalPages`, `currentPage = 1`, and `pageSize = 25`.
4.  **Scenario:** Applying a Filter
    *   Input: `page = 1`, `pageSize = 25`, no search query, `category = "Keyboards"`, no sorting.
    *   Outcome: The hook fetches the first 25 products within the "Keyboards" category from the `/api/conductor/catalog` endpoint, passing `category = "Keyboards"` as a parameter.  The animated magnifying glass icon and skeleton loaders are displayed during the fetch. The hook returns the filtered `products` array, `totalItems`, `totalPages`, `currentPage = 1`, and `pageSize = 25`.
5.  **Scenario:** Applying Sorting
    *   Input: `page = 1`, `pageSize = 25`, no search query, no filters, `sortBy = "price"`
    *   Outcome: The hook fetches the first 25 products sorted by price from the `/api/conductor/catalog` endpoint, passing `sortBy = "price"` as a parameter. The animated magnifying glass icon and skeleton loaders are displayed during the fetch. The hook returns the sorted `products` array, `totalItems`, `totalPages`, `currentPage = 1`, and `pageSize = 25`.
6. **Scenario:** API Request Fails
    *   Input: The `/api/conductor/catalog` endpoint returns an error (e.g., 500 Internal Server Error).
    *   Outcome: The hook handles the error and displays an error message to the user. The animated magnifying glass disappears.  A retry banner is displayed.
7.  **Scenario:** No Results Found
    *   Input: `searchQuery` yields no matching results in the catalog.
    *   Outcome: The hook returns an empty `products` array, and the UI displays a "No results found" message.

## Stitch UI Prompt
```text
// Target Component: useConductorCatalog Hook (Loading State Visualization)
// Description:  The loading visualization for the useConductorCatalog hook.
// This is an animated loading indicator to replace all instances of loading and skeleton placeholders.

// Layout: Absolute positioning within the parent container.  The parent container should have position: relative.

// Visual Style:
// - Dark mode
// - Tailwind CSS for styling
// - Animated magnifying glass icon
// - `slate-900` background for container
// - `blue-500` as the animation color

// Component Hierarchy:
// The animated magnifying glass should be centrally positioned.

// Data Slots:
// None - this is purely a visual component.

// Detailed Instructions:
// 1. Create a container div with `position: absolute`, `top: 0`, `left: 0`, `w-full`, `h-full`, `bg-slate-900`, `z-10`, and `flex items-center justify-center`.
// 2. Inside the container, place an animated magnifying glass icon using `framer-motion`. Use a `LucideReact.Search` icon or an equivalent.
// 3. The magnifying glass should scale up and down slightly using `framer-motion`'s `animate` prop.  Use a scale range of 0.8 to 1.2.
// 4. The magnifying glass icon should be styled with `text-blue-500` and a size of `h-8 w-8`.
// 5. The animation should be infinite and use a duration of 1.5 seconds with an `ease` of `easeInOut`.
// 6. This component is used during catalog fetch and will be invisible after data has been retrieved.

```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
