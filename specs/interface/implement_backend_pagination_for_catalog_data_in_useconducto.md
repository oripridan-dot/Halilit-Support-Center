# Spec: Implement Backend Pagination for Catalog Data in `useConductorCatalog`

**Version:** 1.1
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Refactor the `useConductorCatalog` hook to fetch product catalog data from the backend in paginated form, rather than loading the entire `galaxy_db.json` file on the client-side. This addresses the critical issue of exceeding the 5MB client-side JSON limit, improving performance and reducing memory consumption. This aligns with the "Speed of Service" technical standard.

## Requirements

1.  **Backend Pagination Endpoint:** Modify the `/api/conductor/catalog` endpoint to accept `page` and `pageSize` query parameters and return a paginated subset of the catalog data, along with metadata about the total number of items and pages. The backend should default `pageSize` to 25 if not specified.

2.  **Data Contract Update:** Update the data contract for `/api/conductor/catalog` to include pagination metadata:

    ```typescript
    interface PaginatedCatalogResponse {
      products: ConductorProduct[];
      totalItems: number;
      totalPages: number;
      currentPage: number;
      pageSize: number;
    }
    ```

3.  **`useConductorCatalog` Hook Modification:** Modify the `useConductorCatalog` hook to:
    *   Accept optional `page` and `pageSize` parameters with default values of `1` and `25` respectively.
    *   Fetch data from the paginated `/api/conductor/catalog` endpoint using the provided `page` and `pageSize` parameters.
    *   Return the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize` from the API response.
    *   Use `react-query` to manage the fetching and caching of paginated data.
    *   Persist `searchQuery` and `initialCfpFilter` when refetching.

4.  **Default Page Size:** Set a default `pageSize` value of 25 items per page.

5.  **Error Handling:** Maintain existing error handling for API requests, displaying error messages to the user if the data cannot be fetched.

6.  **Remove `galaxy_db.json`:** Remove the `galaxy_db.json` file from the `frontend/public/data` directory, as it will no longer be used. The backend must now supply the data.

7. **Initial Load:** The catalog data should load on the first page by default.

## Behavior Scenarios

1.  **Scenario:** Initial Load
    *   Input: `useConductorCatalog()` is called with no arguments.
    *   Outcome: The hook fetches the first page (page 1) of catalog data with a page size of 25. The hook returns `products`, `totalItems`, `totalPages`, `currentPage` (1), and `pageSize` (25).

2.  **Scenario:** Changing Page Size
    *   Input: `useConductorCatalog({ pageSize: 50 })` is called.
    *   Outcome: The hook fetches the first page of catalog data with a page size of 50. The hook returns `products`, `totalItems`, `totalPages`, `currentPage` (1), and `pageSize` (50).

3.  **Scenario:** Navigating to Page 3
    *   Input: `useConductorCatalog({ page: 3 })` is called.
    *   Outcome: The hook fetches the third page of catalog data with a page size of 25. The hook returns `products`, `totalItems`, `totalPages`, `currentPage` (3), and `pageSize` (25).

4.  **Scenario:** API Returns Error
    *   Input: The `/api/conductor/catalog` endpoint returns an error.
    *   Outcome: The hook returns an error state, and an error message is displayed to the user.

5.  **Scenario:** API Returns Empty Data
    *   Input: The `/api/conductor/catalog` endpoint returns an empty `products` array.
    *   Outcome: The hook returns an empty `products` array, but `totalItems`, `totalPages`, `currentPage`, and `pageSize` are still populated.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- Verify in the browser that the catalog loads and paginates correctly with default and custom page sizes. Check the network tab to confirm that the `/api/conductor/catalog` endpoint is being called with the correct `page` and `pageSize` parameters.
