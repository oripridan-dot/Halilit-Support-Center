# Spec: Implement Backend Pagination for useConductorCatalog (Final + Skeleton Loading)
**Version:** 7.0
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the critical issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API and uses skeleton loading.

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
    *   Implement skeleton components for loading states in parent components using the hook.

## Stitch UI Prompt
```text
// Target Component: useConductorCatalog hook implementation
// Description: This prompt focuses on creating the skeleton loading states

// The component using useConductorCatalog should have a main container with:
// Layout: Flexbox, direction column
// Style: dark mode, slate-900 background

// Before catalog data is loaded, show the following skeleton placeholders:

// 1. Search Input Skeleton:
// Layout: Same size as the actual search input
// Style: rounded corners, bg-zinc-700, h-10

// 2. Inventory Grid Skeleton: (Use Bento Grid or CSS Grid for this)
// Create 5-10 skeleton rows, with each row containing:
// - Image placeholder: rounded corners, bg-zinc-700, w-24, h-24
// - Text placeholders (product name, brand, price): varying widths, bg-zinc-700, h-6, rounded

// Use Tailwind CSS classes for:
// - Container: flex flex-col items-center p-4 slate-900
// - Search Input Skeleton: rounded-md bg-zinc-700 h-10 w-full
// - Grid Row: flex items-center space-x-4
// - Image Placeholder: rounded-md bg-zinc-700 w-24 h-24
// - Text Placeholders: rounded-md bg-zinc-700 h-6 w-32

// The entire skeleton loading UI should shimmer. Use framer-motion for the shimmer effect. The skeleton UI should be responsive.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- Ensure galaxy_db.json is physically deleted from frontend/public/data
- Run the application and verify that the inventory grid and other components using `useConductorCatalog` load data correctly from the backend API.
- Inspect network requests to confirm that only paginated requests are made to `/api/conductor/catalog`.
- Verify correct display of loading skeletons during data fetching.
