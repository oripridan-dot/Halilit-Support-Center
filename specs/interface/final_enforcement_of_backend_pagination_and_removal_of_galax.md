# Spec: Implement Backend Pagination for useConductorCatalog (Final + Skeleton Loading)
**Version:** 7.1
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
    *   Implements skeleton components for loading states in parent components using the hook, displaying the skeleton until data is loaded.
6. **Skeleton visibility:** Ensure that skeleton components are displayed while the data is loading, enhancing the user experience with visual feedback.

## Stitch UI Prompt
```text
// Target Component: useConductorCatalog hook implementation and its dependent views.
// Description: This prompt focuses on ensuring the correct skeleton loading states are displayed while the hook is fetching data.

// The component using useConductorCatalog should display skeleton placeholders until the data is loaded:

// InventoryView:
// Layout: Flexbox, direction column, with a slate-900 background.

// Skeleton components should be used before catalog data is loaded, including:

// 1. Search Input Skeleton:
// Layout: Same size and placement as the actual search input.
// Style: rounded corners, bg-zinc-700, h-10.

// 2. Inventory Grid Skeleton: (Use CSS Grid)
// Repeat the product tile skeleton based on the pageSize and maintain the grid.
// The skeleton tile must include:
// Image Skeleton: square aspect ratio, bg-zinc-700.
// Title Skeleton: rectangular shape, bg-zinc-700, 2 lines.
// Price Skeleton: short rectangular shape, bg-zinc-700.

// ProductDetailView:
// Description: Should display a full-page skeleton mimicking the ProductDetail layout.
// All values should be skeleton components using rounded corners and bg-zinc-700 color.

// Ensure consistent styling across all skeleton components, using dark mode and Tailwind CSS, and shimmer loading effect.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
