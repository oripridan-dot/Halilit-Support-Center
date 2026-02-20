# Spec: Enforce Backend Pagination and Remove galaxy_db.json

**Version:** 1.8
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API and includes image validation with fallback.

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
8. **Image Fallback:** Implement image fallback logic. If `product.image_url` is missing or fails to load, use `/placeholder.png`.

## Behavior Scenarios

1.  **Scenario:** Initial Load
    *   Input: `page=1`, `pageSize=25`, no other parameters.
    *   Outcome: The hook fetches the first 25 products from the backend API. The total number of items and pages are also returned.
2.  **Scenario:** Navigating to the Next Page
    *   Input: `page=2`, `pageSize=25`.
    *   Outcome: The hook fetches the next 25 products from the backend API.
3.  **Scenario:** Applying a Filter
    *   Input: `searchQuery="Roland"`, `page=1`, `pageSize=25`.
    *   Outcome: The hook fetches the first 25 products that match the search query "Roland". The total number of matching items and pages are also returned.
4.  **Scenario:** Applying a Sort
    *   Input: `sortBy="price"`, `page=1`, `pageSize=25`.
    *   Outcome: The hook fetches the first 25 products sorted by price.
5.  **Scenario:** Image Fallback
    * Input: A product has `image_url: null`.
    * Outcome: The product tile or detail view displays the `/placeholder.png` image.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
