# Spec: Enforce Backend Pagination and Remove GalaxyDB (Final + Research Animation + Graceful Error Handling)
**Version:** 3.5
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the critical issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, handles loading states correctly, refactors the use of `ImageWithFallback`, displays an animated magnifying glass during data fetching, and adds graceful error handling, showing a retry banner if the API fails.

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
7.  **Error Handling:**
    *   Maintain existing error handling for API requests.
    *   Display a retry banner on API failure with a button to refetch the data.
    *   Ensure the error banner provides informative error messages to the user.
8.  **Image Fallback:** Refactor the usage of the `ImageWithFallback` component to ensure a consistent image loading experience.
9.  **Skeleton Loading:** Render the `ResearchAnimation` component while the data is fetching. Display a magnifying glass animation.

## Stitch UI Prompt
```text
// Target Component: useConductorCatalog's loading state (e.g., inside InventoryView or ProductTile)
// Description:  When the catalog data is loading, show a "Researching..." animation with a progress bar.  If there's an error loading the catalog, show a dismissable error banner with a retry button.

// Use a Flexbox layout to center the ResearchAnimation.
// Use Tailwind CSS dark mode.

// Data Slots:
//   isLoading: boolean - True when the catalog is loading, false otherwise.
//   error: string | null - An error message if the catalog failed to load, null otherwise.
//   retry: () => void - A function to call to retry loading the catalog.
//   brandName?: string - The name of the brand (optional, for theming).
//   brandColor?: string - The brand's accent color (optional, for theming).

// If isLoading is true, show the ResearchAnimation component:
// <ResearchAnimation brandName="{brandName}" brandColor="{brandColor}" message="Fetching catalog data..." progress={50} />

// If error is not null, show a dismissable error banner using Tailwind CSS classes:
// <div className="bg-red-700 text-white p-4 rounded-md shadow-md flex items-center justify-between">
//   <span>Error loading catalog: {error}</span>
//   <button onClick={retry} className="bg-red-800 hover:bg-red-900 text-white font-bold py-2 px-4 rounded">Retry</button>
// </div>

// Ensure the loading and error states are mutually exclusive. Only one should be visible at a time.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- Ensure that `galaxy_db.json` does not exist in `frontend/public/data`
- Run the app. Verify that the Inventory view and Product Detail view load catalog data correctly from the backend.
- Verify that the pagination controls work correctly in the Inventory view.
- Simulate a backend error and verify that the retry banner appears with the correct error message.
- Ensure the "Researching..." animation appears during the loading state, and the error banner appears as specified.
