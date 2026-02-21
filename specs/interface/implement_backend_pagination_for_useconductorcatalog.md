# Spec: Implement Backend Pagination for `useConductorCatalog`

**Version:** 2.0
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Refactor the `useConductorCatalog` hook to fetch product catalog data from the backend in paginated form, rather than loading the entire `galaxy_db.json` file on the client-side. This addresses the critical issue of exceeding the 5MB client-side JSON limit, improving performance and reducing memory consumption. This aligns with the "Speed of Service" technical standard.

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
7.  **Error Handling:** Maintain existing error handling for API requests, displaying error messages to the user if the data cannot be fetched.
8. **Loading State:** Render a skeleton loader while the data is fetching.

## Behavior Scenarios

1.  **Scenario:** Initial Load
    *   Input: `page = 1`, `pageSize = 25`
    *   Outcome: The hook fetches the first 25 products from the backend API.
    *   Outcome: The hook returns the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize` from the API response.
    *   Outcome: A skeleton loader is displayed while the data is being fetched.

2.  **Scenario:** User Navigates to Page 3
    *   Input: `page = 3`, `pageSize = 25`
    *   Outcome: The hook fetches products 51-75 from the backend API.
    *   Outcome: The hook returns the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize` from the API response.

3.  **Scenario:** API returns an error
    *   Input: The backend API returns a 500 error.
    *   Outcome: The hook returns an error state.
    *   Outcome: An error message is displayed to the user.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
