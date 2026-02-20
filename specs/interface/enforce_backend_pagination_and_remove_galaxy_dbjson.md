# Spec: Enforce Backend Pagination and Remove galaxy_db.json
**Version:** 2.0
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, and ensures loading states are handled correctly. This spec also ensures that totalItems, totalPages, currentPage, and pageSize are returned from the hook.

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
8. **Image Fallback:** Implement image fallback logic. If `product.image_url` is missing or fails to load, use `/placeholder.png`. This logic should use the existing `ImageWithFallback` component.
9. **Hook Return Values:** Ensure that the `useConductorCatalog` hook returns the following values: `data: {products, metadata}`, `isLoading`, `error`, `refetch`.
   - `products` is the array of `ConductorProduct` for the current page.
   - `metadata` is an object containing:
      - `totalItems`: the total number of products in the catalog.
      - `totalPages`: the total number of pages.
      - `currentPage`: the current page number.
      - `pageSize`: the number of products per page.

## Behavior Scenarios

1.  **Scenario:** Initial Load
    *   Input: `page = 1`, `pageSize = 25`, no search query, no filters.
    *   Outcome: The `useConductorCatalog` hook fetches the first page of 25 products from the `/api/conductor/catalog` endpoint.
    *   Outcome: A skeleton loader is displayed while the data is loading.
    *   Outcome: The hook returns the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize` from the API response.
2.  **Scenario:** User Navigates to Page 3
    *   Input: `page = 3`, `pageSize = 25`, no search query, no filters.
    *   Outcome: The `useConductorCatalog` hook fetches the third page of 25 products from the `/api/conductor/catalog` endpoint.
    *   Outcome: The hook returns the `products` array, `totalItems`, `totalPages`, `currentPage = 3`, and `pageSize = 25` from the API response.
3.  **Scenario:** User Applies a Search Query
    *   Input: `page = 1`, `pageSize = 25`, `searchQuery = "Roland"`, no filters.
    *   Outcome: The `useConductorCatalog` hook fetches the first page of 25 products matching the search query "Roland" from the `/api/conductor/catalog` endpoint.
    *   Outcome: The hook returns the filtered `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize` from the API response.
4.  **Scenario:** API Request Fails
    *   Input: The `/api/conductor/catalog` endpoint returns an error (e.g., 500 Internal Server Error).
    *   Outcome: The `useConductorCatalog` hook returns an `error` object.
    *   Outcome: An error message is displayed to the user.
    *   Outcome: A "retry" banner is rendered, allowing the operator to manually refetch.
5.  **Scenario:** Image Loading Fails
    *   Input: One or more `product.image_url` values in the returned data are invalid or return a 404 error.
    *   Outcome: The `ImageWithFallback` component displays the `/placeholder.png` image for those products.
6. **Scenario:** Hook successfully fetches the catalog data
    *   Input: The `/api/conductor/catalog` endpoint returns successfully.
    *   Outcome: The `useConductorCatalog` hook returns an object with the structure `{ data: { products, metadata }, isLoading, error, refetch }`.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
