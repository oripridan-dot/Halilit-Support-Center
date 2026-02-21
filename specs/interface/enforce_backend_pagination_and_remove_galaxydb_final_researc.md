# Spec: Enforce Backend Pagination and Remove GalaxyDB (Final + Research Animation + Graceful Error Handling)
**Version:** 3.6
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the critical issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, handles loading states correctly, refactors the use of `ImageWithFallback`, displays an animated magnifying glass during data fetching, adds graceful error handling, showing a retry banner if the API fails, and improves the research animation.

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
8.  **Image Fallback:** Refactor the usage of the `ImageWithFallback` component to ensure a consistent image loading experience, including proper alt text.
9.  **Research Animation:** Display an animated magnifying glass (`ResearchAnimation.tsx`) while data is fetching. The animation should receive `brandName` as a prop. Set the `message` to "Loading products…"

## Stitch UI Prompt
```text
// Target Component: useConductorCatalog (Loading State in Parent View)
// Description: While the useConductorCatalog hook is loading, show a "Researching Halilit..." animation instead of a blank area.

// Component: ResearchAnimation
// Data Slot: brandName = "Halilit"
// Data Slot: message = "Loading products..."

// Layout: Render the ResearchAnimation component in the center of the view, taking up the available space.

// Visual Style:
// - Dark mode
// - Tailwind CSS
// - Base color: slate-900
// - Accent color: blue-500

// Instructions:
// 1.  Locate where the catalog data is being fetched in the parent component.
// 2.  Wrap the ResearchAnimation component in a conditional rendering block that displays only when `isLoading` is true.
// 3.  Ensure that the conditional rendering block doesn't interfere with any existing layout or styling.
// 4.  Make sure brandName="Halilit" and message="Loading products…" are passed in correctly.
// 5.  Add classNames to ResearchAnimation to ensure it fills the appropriate space, such as 'w-full h-full flex items-center justify-center'.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`