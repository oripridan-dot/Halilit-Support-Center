# Spec: Enforce Backend Pagination and Remove galaxy_db.json
**Version:** 2.1
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, and ensures loading states are handled correctly. This spec also ensures that `totalItems`, `totalPages`, `currentPage`, and `pageSize` are returned from the hook.

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
8.  **Image Fallback:** Implement image fallback logic. If `product.image_url` is missing or fails to load, use `/placeholder.png`. This logic should use the existing `<ImageWithFallback />` component.

## Behavior Scenarios

1.  **Scenario:** Initial load of InventoryView with no search query.
    *   **Input:** Navigating to InventoryView.
    *   **Outcome:** The `useConductorCatalog` hook fetches the first page (page 1) of products from the `/api/conductor/catalog` endpoint with a page size of 25. A skeleton loading indicator is displayed while data is fetched. Products are displayed with correct image fallbacks.
2.  **Scenario:** User enters a search query.
    *   **Input:** User types "Roland" in the search input.
    *   **Outcome:** The `useConductorCatalog` hook fetches the first page of products matching the search query "Roland" from the `/api/conductor/catalog` endpoint.
3.  **Scenario:** User navigates to page 3 of the inventory.
    *   **Input:** Clicking the "Next" button twice on the InventoryView.
    *   **Outcome:** The `useConductorCatalog` hook fetches page 3 of the inventory from the `/api/conductor/catalog` endpoint.
4.  **Scenario:** The API returns an error.
    *   **Input:** Simulate an API error by causing the `/api/conductor/catalog` endpoint to return a 500 status code.
    *   **Outcome:** Display an error message in a banner. The banner displays a "retry" button that triggers another API call.
5.  **Scenario:** `product.image_url` is invalid or missing.
    *   **Input:** A product in the `/api/conductor/catalog` response has `image_url: null`.
    *   **Outcome:** The `<ImageWithFallback />` component displays the `/placeholder.png` image.

## Stitch UI Prompt
```text
// Target Component: frontend/src/hooks/useConductorCatalog.ts

// Description: This is NOT a component to be rendered. It's a React hook.
// No Stitch prompt can apply here. Focus on the data-fetching logic in the hook.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
