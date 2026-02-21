# Spec: Implement Backend Pagination and Remove GalaxyDB (Final)
**Version:** 3.4
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the critical issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, handles loading states correctly, and refactors the use of `ImageWithFallback`. This final version enforces a loading state.

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
    *   Uses `isloading` from `useQuery` to determine the loading state. The view MUST display a skeleton while loading.
6.  **Filtering and Sorting Parameters:** The `useConductorCatalog` hook must pass the filter and sort state as parameters to the API endpoint.
7.  **Error Handling:** Maintain existing error handling for API requests, displaying error messages to the user if the data cannot be fetched. Render a "retry" banner on API failure.
8.  **Image Fallback:** Refactor the usage of the `ImageWithFallback` component to ensure a consistent image loading experience.

## Stitch UI Prompt

```text
// Target Component: useConductorCatalog hook with Paginated Catalog Response
// Description:  A hook that fetches product catalog data from the backend in paginated form, handling loading, error, and data states.
// Layout: N/A (This is a hook, not a UI component)
// Visual Style: N/A (This is a hook, not a UI component)
//
// Data Slots:
// - products: array of ConductorProduct objects. Each object has properties like id, name, description, imageUrl, category, brand, and price.
// - totalItems: total number of products in the catalog (number).
// - totalPages: total number of pages (number).
// - currentPage: current page number (number).
// - pageSize: number of products per page (number).
// - isLoading: boolean indicating whether the data is currently being fetched.
// - error: error object if the API request failed (can be null).
//
// Instructions:
// 1. Implement a React hook called `useConductorCatalog` in TypeScript.
// 2. Use `react-query` to manage fetching and caching of paginated data from the `/api/conductor/catalog` endpoint.
// 3. Accept optional parameters for `page`, `pageSize`, `searchQuery`, `sortBy`, `category`, and `brand` with default values.
// 4. Construct the API request URL with these parameters.
// 5. Return the `products` array, `totalItems`, `totalPages`, `currentPage`, `pageSize`, `isLoading`, and `error` from the hook.
// 6. Ensure that the hook handles loading and error states correctly.
// 7. Ensure type safety using the provided TypeScript interfaces.
// 8. Ensure `galaxy_db.json` is completely unused.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
