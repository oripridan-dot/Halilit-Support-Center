# Spec: Enforce Backend Pagination and Remove galaxy_db.json
**Version:** 2.2
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, ensures loading states are handled correctly, and refactors the use of `ImageWithFallback`

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
    *   Uses `react-query` to manage the fetching and caching of paginated data. Displays a skeleton while loading.
6.  **Filtering and Sorting Parameters:** The `useConductorCatalog` hook must pass the filter and sort state as parameters to the API endpoint.
7.  **Error Handling:** Maintain existing error handling for API requests, displaying error messages to the user if the data cannot be fetched. Render a "retry" banner on API failure.
8.  **Image Fallback:** Refactor the usage of the `ImageWithFallback` component to ensure a consistent image loading experience.
9. **Skeleton Loading:** Render a skeleton loader while the data is fetching. Use the `ResearchAnimation.tsx` component.

## Behavior Scenarios

1.  **Scenario:** Initial Load - First Page
    *   Input: `page = 1`, `pageSize = 25`, no search query, no filters, no sorting.
    *   Outcome: The hook fetches the first 25 products from the `/api/conductor/catalog` endpoint. The hook returns the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize`. A skeleton loader is displayed while the data is being fetched.
2.  **Scenario:** Navigating to Next Page
    *   Input: `page = 2`, `pageSize = 25`, no search query, no filters, no sorting.
    *   Outcome: The hook fetches the next 25 products from the `/api/conductor/catalog` endpoint. The hook returns the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize`.
3.  **Scenario:** Applying a Search Query
    *   Input: `page = 1`, `pageSize = 25`, `searchQuery = "Roland"`, no filters, no sorting.
    *   Outcome: The hook fetches the first 25 products that match the search query "Roland" from the `/api/conductor/catalog` endpoint. The hook returns the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize`.
4.  **Scenario:** Applying a Category Filter
    *   Input: `page = 1`, `pageSize = 25`, no search query, `category = "Keyboards"`, no sorting.
    *   Outcome: The hook fetches the first 25 products that belong to the "Keyboards" category from the `/api/conductor/catalog` endpoint. The hook returns the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize`.
5.  **Scenario:** Applying Sorting
    *   Input: `page = 1`, `pageSize = 25`, no search query, no filters, `sortBy = "price"`.
    *   Outcome: The hook fetches the first 25 products, sorted by price, from the `/api/conductor/catalog` endpoint. The hook returns the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize`.
6.  **Scenario:** API Request Fails
    *   Input: Any valid combination of parameters, but the `/api/conductor/catalog` endpoint returns an error (e.g., 500 Internal Server Error).
    *   Outcome: The hook returns an `error` object and does not return any data. An error message is displayed to the user.
7.  **Scenario:** Image fails to load
    * Input: products array is returned, but the image URL returns a 404 error.
    * Outcome: The fallback `/placeholder.png` image is rendered.

## Stitch UI Prompt

```text
// Target Component: useConductorCatalog hook and related InventoryView components
// Description: Refactor the hook to paginate catalog data from the backend API and remove reliance on galaxy_db.json
// Layout: N/A - backend logic change
// Visual Style: N/A - backend logic change
//
// Instructions:
// 1. Locate the useConductorCatalog hook in frontend/src/hooks/useConductorCatalog.ts.
// 2. Remove any code related to importing or reading galaxy_db.json.
// 3. Modify the hook to accept page, pageSize, searchQuery, sortBy, category, and brand parameters.
// 4. Construct the API URL with the provided parameters and fetch data from /api/conductor/catalog.
// 5. Implement pagination logic to handle totalItems, totalPages, currentPage, and pageSize.
// 6. Add skeleton loading while API data is fetching
// 7. Ensure error handling is in place for API requests.
// 8. Refactor all components using the useConductorCatalog hook to account for the data shape change, particularly the ImageWithFallback component.
// Data Slots: N/A - hook logic change

```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- Verify that `frontend/public/data/galaxy_db.json` DOES NOT exist.
- Manually verify in the UI that the inventory grid paginates and filter/sort work correctly.
