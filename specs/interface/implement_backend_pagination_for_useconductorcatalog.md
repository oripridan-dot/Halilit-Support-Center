# Spec: Implement Backend Pagination for useConductorCatalog

**Version:** 1.4
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Refactor the `useConductorCatalog` hook to fetch product catalog data from the backend in paginated form, addressing the issue of exceeding the 5MB client-side JSON limit. All filter and sort states are passed to the API.

## Requirements

1.  **Remove `galaxy_db.json` dependency:** Ensure the hook solely relies on the `/api/conductor/catalog` endpoint for data.

2.  **Backend Pagination Endpoint:** Ensure the `/api/conductor/catalog` endpoint accepts `page`, `pageSize`, `searchQuery`, `sortBy`, `category`, and `brand` query parameters and returns a paginated subset of the catalog data, along with metadata about the total number of items and pages. The backend should default `pageSize` to 25 if not specified, and if `page` is not specified, it should default to 1. If sorting parameters are being passed, preserve them.

3.  **Data Contract Update:** Ensure the data contract for `/api/conductor/catalog` includes pagination metadata:

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
    *   Accept optional `page`, `pageSize`, `searchQuery`, `sortBy`, `category`, and `brand` parameters with default values of `1`, `25`, `''`, `''`, `''`, and `''` respectively.
    *   Fetch data from the paginated `/api/conductor/catalog` endpoint using the provided parameters.
    *   Return the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize` from the API response.
    *   Use `react-query` to manage the fetching and caching of paginated data.
5.  **Filtering and Sorting Parameters:** The `useConductorCatalog` hook must pass the filter and sort state as parameters for the API call.
```
*   Category: The category being viewed.
*   Brand: The brand being viewed.
```
6.  **Category & Brand Parameters:** The hook must also accept optional parameters for brand and category filtering.

## Behavior Scenarios

1.  **Scenario:** Initial Load - No Parameters
    *   Input: The `useConductorCatalog` hook is called without any parameters.
    *   Outcome: The hook fetches the first page (page 1) of data, with a page size of 25, from `/api/conductor/catalog`.
2.  **Scenario:** Pagination - User Navigates to Page 3
    *   Input: The `useConductorCatalog` hook is called with `page = 3`.
    *   Outcome: The hook fetches the third page of data from `/api/conductor/catalog` with the default page size.

3. **Scenario:** Filtering - category is specified
    *   Input: The `useConductorCatalog` hook is called with `category = 'keyboards'`.
    *   Outcome: The hook fetches the data from `/api/conductor/catalog` only for the category specified.

4.  **Scenario:** Filtering - brand is specified
    *   Input: The `useConductorCatalog` hook is called with `brand = 'roland'`.
    *   Outcome: The hook fetches the data from `/api/conductor/catalog` only for the brand specified.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- `pytest backend/tests/test_catalog_api.py`
