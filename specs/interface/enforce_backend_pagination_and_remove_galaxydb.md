# Spec: Enforce Backend Pagination and Remove GalaxyDB

**Version:** 2.2
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, ensures loading states are handled correctly, and refactors the use of `ImageWithFallback`

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
8.  **Image Fallback:** Implement image fallback logic using the `ImageWithFallback` component. If `product.image_url` is missing or fails to load, use the `ImageWithFallback` component with `/placeholder.png` as the fallback.
9.  **ImageWithFallback Usage:** Ensure that the `ImageWithFallback` component is being used correctly within the application to display images, including product images in list views and detail views.

## Behavior Scenarios

1.  **Scenario:** Initial Load - First Page
    *   Input: `page = 1`, `pageSize = 25`, no search query, no filters, no sorting.
    *   Outcome: The hook fetches the first 25 products from the `/api/conductor/catalog` endpoint. The UI displays these products.
2.  **Scenario:** Navigation to Next Page
    *   Input: User clicks the "Next Page" button. `page` increments to 2.
    *   Outcome: The hook fetches the next 25 products (products 26-50) from the `/api/conductor/catalog` endpoint. The UI updates to display these products.
3.  **Scenario:** Search Query Applied
    *   Input: User enters "Roland" in the search input. `searchQuery = "Roland"`.
    *   Outcome: The hook fetches the first 25 products matching "Roland" from the `/api/conductor/catalog` endpoint. The UI displays these products.
4.  **Scenario:** Category Filter Applied
    *   Input: User selects "Keyboards" from the category filter. `category = "Keyboards"`.
    *   Outcome: The hook fetches the first 25 products in the "Keyboards" category from the `/api/conductor/catalog` endpoint. The UI displays these products.
5.  **Scenario:** Image Loading Failure
    *   Input: A product has `image_url = "https://example.com/broken_image.jpg"`.
    *   Outcome: The `ImageWithFallback` component displays the `/placeholder.png` image for that product.
6. **Scenario:** Image URL is Null
    * Input: A product has `image_url = null`.
    * Outcome: The `ImageWithFallback` component displays the `/placeholder.png` image for that product.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- Delete `frontend/public/data/galaxy_db.json` and verify it is NOT accessed at runtime.
- Verify the `/api/conductor/catalog` endpoint is called with appropriate query parameters for pagination, search, filter, and sort.
- Verify that the UI displays the correct number of items per page (default 25).
- Verify that navigation between pages works correctly.
- Verify that image fallback is working as expected using `/placeholder.png`.
