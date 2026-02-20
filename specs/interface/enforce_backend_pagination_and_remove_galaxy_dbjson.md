# Spec: Enforce Backend Pagination and Remove galaxy_db.json
**Version:** 1.9
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, and ensures loading states are handled correctly.

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

## Behavior Scenarios

1.  **Scenario:** Initial Load
    *   Input: `page=1`, `pageSize=25`, no other parameters.
    *   Outcome: The hook fetches the first 25 products from the backend API. The total number of items and pages are also returned. The UI displays a loading skeleton during the initial load.
2.  **Scenario:** Subsequent Page Load
    *   Input: `page=2`, `pageSize=25`.
    *   Outcome: The hook fetches the next 25 products from the backend API. The UI updates to display the new products.
3.  **Scenario:** Filtering
    *   Input: `searchQuery="keyboard"`.
    *   Outcome: The hook fetches the first page of products that match the search query from the backend API.
4.  **Scenario:** Sorting
    *   Input: `sortBy="price"`.
    *   Outcome: The hook fetches the first page of products sorted by price from the backend API.
5.  **Scenario:** Image Load Failure
    *   Input: A product has a broken `image_url`.
    *   Outcome: The `ImageWithFallback` component displays `/placeholder.png`.
6. **Scenario:** API Failure
    * Input: API returns a 500 status.
    * Outcome: A retry banner appears in the UI, offering the operator a chance to refresh the catalog.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- Ensure `galaxy_db.json` no longer exists in `frontend/public/data`.
- Manually verify the UI displays paginated data correctly.
