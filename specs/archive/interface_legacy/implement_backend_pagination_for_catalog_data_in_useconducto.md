# Spec: Implement Backend Pagination for Catalog Data in `useConductorCatalog`

**Version:** 1.5
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Refactor the `useConductorCatalog` hook to fetch product catalog data from the backend in paginated form, rather than relying on the entire catalog being loaded at once. This addresses exceeding the 5MB client-side JSON limit, improving performance, and reducing memory consumption. This aligns with the "Speed of Service" technical standard. This version updates the hook so filter and sort data are passed to the API. Image fallback logic is added.

## Requirements

1.  **Remove `galaxy_db.json` dependency:** Ensure the hook solely relies on the `/api/conductor/catalog` endpoint for data. Delete the `galaxy_db.json` file from `frontend/public/data`.

2.  **Backend Pagination Endpoint:** Ensure the `/api/conductor/catalog` endpoint accepts `page`, `pageSize`, `searchQuery`, `sortBy`, `category`, and `brand` query parameters and returns a paginated subset of the catalog data, along with metadata about the total number of items and pages. The backend should default `pageSize` to 25 if not specified and if `page` is not specified, it should default to 1. If sorting parameters are being passed, preserve them.

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
    *   Accept optional `page`, `pageSize`, `searchQuery`, `sortBy`, `category`, and `brand` parameters with default values of `1`, `25`, `''`, `''`, `''`, and `''` respectively.
    *   Fetch data from the paginated `/api/conductor/catalog` endpoint using the provided parameters.
    *   Return the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize` from the API response.
    *   Use `react-query` to manage the fetching and caching of paginated data.

5.  **Filtering and Sorting Parameters:** The `useConductorCatalog` hook must pass the filter and sort state as parameters to the `/api/conductor/catalog` endpoint.
6.  **Loading State:** Implement a loading state within the hook to indicate when data is being fetched from the API.
7.  **Error Handling:** Implement error handling to display an error message if the API request fails.

## Behavior Scenarios

1.  **Scenario:** Initial Load
    *   Input: `page = 1`, `pageSize = 25`, `searchQuery = ''`, `sortBy = ''`, `category = ''`, `brand = ''`
    *   Outcome: The hook fetches the first 25 products from the `/api/conductor/catalog` endpoint and returns them. `totalItems`, `totalPages`, `currentPage`, and `pageSize` are also returned.
2.  **Scenario:** User Navigates to Page 2
    *   Input: `page = 2`, `pageSize = 25`, `searchQuery = ''`, `sortBy = ''`, `category = ''`, `brand = ''`
    *   Outcome: The hook fetches the next 25 products (26-50) from the `/api/conductor/catalog` endpoint and returns them. `totalItems`, `totalPages`, `currentPage`, and `pageSize` are also returned.
3.  **Scenario:** User Searches for "Roland"
    *   Input: `page = 1`, `pageSize = 25`, `searchQuery = 'Roland'`, `sortBy = ''`, `category = ''`, `brand = ''`
    *   Outcome: The hook fetches the first 25 products that match the search query "Roland" from the `/api/conductor/catalog` endpoint and returns them. `totalItems`, `totalPages`, `currentPage`, and `pageSize` are also returned, reflecting the total number of Roland products.
4.  **Scenario:** API Request Fails
    *   Input: Any valid combination of parameters, but the API returns an error.
    *   Outcome: The hook catches the error and returns an error message. The component using the hook displays the error message to the user.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
