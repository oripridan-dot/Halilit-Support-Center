# Spec: Implement Backend Pagination for Catalog Data in `useConductorCatalog`

**Version:** 1.3
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Refactor the `useConductorCatalog` hook to fetch product catalog data from the backend in paginated form, rather than relying on the entire catalog being loaded at once. This addresses exceeding the 5MB client-side JSON limit, improving performance, reducing memory consumption. This aligns with the "Speed of Service" technical standard. This version updates the hook so filter and sort data are passed to the API.

## Requirements

1.  **Remove `galaxy_db.json` dependency:** Ensure the hook solely relies on the `/api/conductor/catalog` endpoint for data.

2.  **Backend Pagination Endpoint:** Ensure the `/api/conductor/catalog` endpoint accepts `page`, `pageSize`, `searchQuery` and `sortBy` query parameters and returns a paginated subset of the catalog data, along with metadata about the total number of items and pages. The backend should default `pageSize` to 25 if not specified and if `page` is not specified, it should default to 1. If sorting parameters are being passed, preserve them.

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
    *   Accept optional `page`, `pageSize`, `searchQuery` and `sortBy` parameters with default values of `1`, `25`, `''` and `''` respectively.
    *   Fetch data from the paginated `/api/conductor/catalog` endpoint using the provided parameters.
    *   Return the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize` from the API response.
    *   Use `react-query` to manage the fetching and caching of paginated data.
5.  **Type Changes:** Update the `ConductorCatalogResponse` type

    ```typescript
    interface ConductorCatalogResponse {
      data: PaginatedCatalogResponse;
      isLoading: boolean;
      error: any;
      refetch: () => void;
    }
    ```

6.  **Search and Sort Parameters:** Ensure the `useConductorCatalog` hook correctly passes the `searchQuery` and `sortBy` parameters to the `/api/conductor/catalog` endpoint.

## Behavior Scenarios

1.  **Scenario:** Initial Load
    *   Input: No `page`, `pageSize`, `searchQuery` or `sortBy` parameters are provided.
    *   Outcome: The hook fetches the first page (page 1) of catalog data with a page size of 25, no search applied, and no sorting applied.
2.  **Scenario:** User navigates to page 3 with a page size of 50 and applies a search.
    *   Input: `page = 3`, `pageSize = 50`, `searchQuery = 'keyboard'`.
    *   Outcome: The hook fetches page 3 of the catalog data with a page size of 50, filtered by "keyboard".

3.  **Scenario:** An error occurs while fetching data.
    *   Input: The `/api/conductor/catalog` endpoint returns an error.
    *   Outcome: The hook returns an error state, and an error message is displayed to the user.

4.  **Scenario:** No data is returned from the API.
    *   Input: The `/api/conductor/catalog` endpoint returns an empty `products` array and `totalItems = 0`.
    *   Outcome: The hook returns an empty `products` array, and the UI displays a message indicating that no products were found.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
