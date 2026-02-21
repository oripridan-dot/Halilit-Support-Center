# Spec: Enforce Backend Pagination for Catalog Data

**Version:** 1.5
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API.

## Requirements

1.  **Total `galaxy_db.json` Removal:** Physically DELETE the `galaxy_db.json` file from the `frontend/public/data` directory.
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
6.  **Filtering and Sorting Parameters:** The `useConductorCatalog` hook must pass the filter and sort state as parameters to the API.
7. **Error Handling:** Persist all existing error handling and loading states and messages.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- `rm frontend/public/data/galaxy_db.json` # Make sure the file is gone to prevent future accidents
