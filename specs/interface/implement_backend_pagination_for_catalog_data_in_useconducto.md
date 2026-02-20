# Spec: Implement Backend Pagination for Catalog Data in `useConductorCatalog`

**Version:** 1.2
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Refactor the `useConductorCatalog` hook to fetch product catalog data from the backend in paginated form, rather than relying solely on the `galaxy_db.json` file. This addresses the critical issue of exceeding the 5MB client-side JSON limit, improving performance, reducing memory consumption, and preparing the codebase for real-time backend updates. This aligns with the "Speed of Service" technical standard.

## Requirements

1.  **Remove `galaxy_db.json` dependency:** Remove all logic that directly loads and processes `galaxy_db.json`. The hook should rely solely on the `/api/conductor/catalog` endpoint for data.
2.  **Backend Pagination Endpoint:** Ensure the `/api/conductor/catalog` endpoint accepts `page` and `pageSize` query parameters and returns a paginated subset of the catalog data, along with metadata about the total number of items and pages. The backend should default `pageSize` to 25 if not specified. If sorting parameters are being passed, preserve them.
3.  **Data Contract Update:** Update the data contract for `/api/conductor/catalog` to include pagination metadata:

    ```typescript
    interface PaginatedCatalogResponse {
      products: ConductorProduct[];
      totalItems: number;
      totalPages: number;
      currentPage: number;
      pageSize: number;
    }
    ```

4.  **`useConductorCatalog` Hook Modification:** Modify the `useConductorCatalog` hook to:
    *   Accept optional `page` and `pageSize` parameters with default values of `1` and `25` respectively.
    *   Fetch data from the paginated `/api/conductor/catalog` endpoint using the provided `page` and `pageSize` parameters.
    *   Return the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize` from the API response.
    *   Use `react-query` to manage the fetching and caching of paginated data.
    *   Preserve `searchQuery` and `initialCfpFilter` when refetching the catalog.
    *   The catalog needs to persist all applied filters when fetching the next page, including search query, and sorting.
5.  **Default Page Size:** Set a default `pageSize` value of 25 items per page.

6.  **Error Handling:** Maintain existing error handling for API requests, displaying error messages to the user if the data cannot be fetched.

## Behavior Scenarios

1.  **Scenario:** Initial Load
    *   Input: No `page` or `pageSize` parameters are provided.
    *   Outcome: The hook fetches the first page of catalog data (page 1, page size 25) from the `/api/conductor/catalog` endpoint.
    *   Outcome: The hook returns the `products` array, `totalItems`, `totalPages`, `currentPage` (1), and `pageSize` (25) from the API response.

2.  **Scenario:** Requesting a Specific Page
    *   Input: `page=3` is provided.
    *   Outcome: The hook fetches the third page of catalog data (page 3, page size 25) from the `/api/conductor/catalog` endpoint.
    *   Outcome: The hook returns the `products` array, `totalItems`, `totalPages`, `currentPage` (3), and `pageSize` (25) from the API response.

3.  **Scenario:** Changing the Page Size
    *   Input: `pageSize=50` is provided.
    *   Outcome: The hook fetches the first page of catalog data (page 1, page size 50) from the `/api/conductor/catalog` endpoint.
    *   Outcome: The hook returns the `products` array, `totalItems`, `totalPages`, `currentPage` (1), and `pageSize` (50) from the API response.

4.  **Scenario:** API Request Fails
    *   Input: The `/api/conductor/catalog` endpoint returns a 500 error.
    *   Outcome: The hook displays an error message to the user.

5.  **Scenario:** Navigating with Search Query, sorting, and filtering.
    *   Precondition: User applies a search query, filter, and sort.
    *   Input: User navigates to the next page.
    *   Outcome: The next page fetches with the previous query, filter, and sort parameters.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
