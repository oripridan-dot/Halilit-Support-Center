# Spec: Enforce Backend Pagination and Remove GalaxyDB

**Version:** 1.7
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API. This version enforces default parameters for pagination.

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
6.  **Default Parameter Handling:** The `useConductorCatalog` hook must explicitly set default values for `page` and `pageSize` when constructing the API request if those values are undefined. This ensures the backend always receives pagination parameters.

## Behavior Scenarios

1.  **Scenario:** Initial Load - No Parameters Specified
    *   Input: The `useConductorCatalog` hook is called without any parameters.
    *   Outcome: The hook fetches data from `/api/conductor/catalog?page=1&pageSize=25`.
    *   Outcome: The hook returns the first page of products (up to 25 items).

2.  **Scenario:** Page Parameter Specified
    *   Input: The `useConductorCatalog` hook is called with `page = 3`.
    *   Outcome: The hook fetches data from `/api/conductor/catalog?page=3&pageSize=25`.
    *   Outcome: The hook returns the third page of products (up to 25 items).

3.  **Scenario:** PageSize Parameter Specified
    *   Input: The `useConductorCatalog` hook is called with `pageSize = 50`.
    *   Outcome: The hook fetches data from `/api/conductor/catalog?page=1&pageSize=50`.
    *   Outcome: The hook returns the first page of products (up to 50 items).

4.  **Scenario:** Both Page and PageSize Parameters Specified
    *   Input: The `useConductorCatalog` hook is called with `page = 2` and `pageSize = 10`.
    *   Outcome: The hook fetches data from `/api/conductor/catalog?page=2&pageSize=10`.
    *   Outcome: The hook returns the second page of products (up to 10 items).

5.  **Scenario:** Search Query, Sort, Filter, and Pagination Parameters Specified
    *   Input: The `useConductorCatalog` hook is called with `page = 3`, `pageSize = 15`, `searchQuery = "keyboard"`, `sortBy = "price"`, `category = "Musical Instruments"`, and `brand = "Roland"`.
    *   Outcome: The hook fetches data from `/api/conductor/catalog?page=3&pageSize=15&searchQuery=keyboard&sortBy=price&category=Musical%20Instruments&brand=Roland`.
    *   Outcome: The hook returns the third page of "keyboard" products (up to 15 items), sorted by price, filtered by "Musical Instruments" category and "Roland" brand.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
