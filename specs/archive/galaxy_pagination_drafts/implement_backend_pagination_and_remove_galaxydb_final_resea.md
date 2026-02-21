# Spec: Implement Backend Pagination and Remove GalaxyDB (Final + Research Animation)
**Version:** 3.3
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the critical issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, handles loading states correctly, refactors the use of `ImageWithFallback`, and displays an animated magnifying glass during data fetching. This final version ensures correct loading state and animation.

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
7.  **Error Handling:** Maintain existing error handling for API requests, displaying error messages to the user if the data cannot be fetched. Render a "retry" banner on API failure.
8.  **Image Fallback:** Refactor the usage of the `ImageWithFallback` component to ensure a consistent image loading experience.
9.  **Research Animation Loading:** Display the `ResearchAnimation` component while the data is fetching and before skeleton loading, passing the `brand` parameter to `ResearchAnimation`.
10. **Skeleton Loading:** Render a skeleton loader while the data is fetching. Use the `ResearchAnimation` component to provide visual feedback while loading.
11. **Loading State Enforcement:** Ensure that the ResearchAnimation is only active during the `isLoading` state, before the skeleton loaders are shown.
12. **Brand Color:** Derive the `brandColor` to be passed to `ResearchAnimation` from a brand color lookup table based on `ConductorProduct.brand`. Default to blue-500 if the brand is not in the table.

## Stitch UI Prompt
```text
// Target Component: useConductorCatalog
// Description: Hook that fetches and manages product catalog data with backend pagination
// Objective: Generate a visual representation of the loading state of the useConductorCatalog hook.

// 1. Initial Loading State (Research Animation):
//    - Use a Bento Grid layout.
//    - Display a full-screen overlay with a semi-transparent slate-900 background.
//    - Vertically and horizontally center a ResearchAnimation component.
//    - Pass a placeholder brandName (e.g., "Halilit").
//    - Pass a placeholder brandColor (e.g., "blue-500").
//    - The message should dynamically change to 'Loading Products'.

// 2. Paginated Content Display:
//    - After loading (initial state is false), display a paginated list of product cards using CSS Grid.
//    - Each card should contain:
//      - A placeholder image (aspect ratio 4:3) with a rounded-md border.
//      - A product name (slate-300 text, font-semibold).
//      - A short product description (slate-500 text).
//      - A "View Product" button (blue-500 background, white text, rounded-md).
//    - Display pagination controls below the grid:
//      - "Previous" button (slate-700 background, white text, rounded-md, disabled on first page).
//      - Page number display (slate-300 text).
//      - "Next" button (blue-500 background, white text, rounded-md, disabled on last page).
//    - Data Slots:
//      - products: Array<{ name: string, description: string, imageUrl: string }>

// 3. Error Handling:
//    - If the API request fails, display an overlay with a slate-900 background.
//    - Center an error message (red-500 text) and a "Retry" button (blue-500 background, white text, rounded-md).
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
