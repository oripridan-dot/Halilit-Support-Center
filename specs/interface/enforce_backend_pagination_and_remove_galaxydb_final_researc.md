# Spec: Enforce Backend Pagination and Remove GalaxyDB (Final + Research Animation + Graceful Error Handling + Polished Animation + Stock and CfP Sorting + Skeleton Placeholder)
**Version:** 4.1
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the critical issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, handles loading states correctly, refactors the use of `ImageWithFallback`, displays an animated magnifying glass during data fetching, adds graceful error handling, showing a retry banner if the API fails, improves the research animation, polishes the animation's timing for a smoother user experience, enforces stock and CfP sorting and adds skeleton placeholders during initial catalog load.

## Requirements

1.  **Total `galaxy_db.json` Removal:** Physically DELETE the `frontend/public/data/galaxy_db.json` file.
2.  **`useConductorCatalog` Dependency Isolation:** Ensure the `useConductorCatalog` hook *solely* relies on the `/api/conductor/catalog` endpoint for data. It must NOT attempt to import or read `galaxy_db.json` under any circumstances.
3.  **Backend Pagination Endpoint:** Verify that the `/api/conductor/catalog` endpoint correctly accepts `page`, `pageSize`, `searchQuery`, `sortBy`, `category`, and `brand` query parameters and returns a paginated subset of the catalog data, along with metadata about the total number of items and pages. The backend should default `pageSize` to 25 if not specified, and if `page` is not specified, it should default to 1. If sorting parameters are being passed, preserve them. The sorting MUST put "In Stock" items first, and then sort CfP above non-CfP within each stock group.
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
    *   Uses `react-query` to manage data fetching and caching.
    *   Displays a polished "research animation" (e.g., animated magnifying glass icon) during data fetching, providing clear visual feedback. Use `framer-motion` for the animation. The animation timing should be tweaked for smoothness.
    *   Implements graceful error handling with a "retry" banner MUST be implemented to address API failures.
    *   `ImageWithFallback` MUST be used for all product images, ensuring a consistent and reliable image loading experience.
    *   Stock and CfP sorting MUST be applied according to Spec `interface/inventory_search_stock_cfp_sorting.md`.
    *   Displays skeleton placeholders while the initial catalog data is loaded.

6. **Skeleton Placeholder:** Display skeleton placeholders for the product grid and other relevant UI elements while the catalog is initially loading. This provides immediate visual feedback to the user and enhances the perceived performance.

## Stitch UI Prompt

```text
// Target Component: useConductorCatalog hook implementation / InventoryView
// Description: This prompt focuses on creating the skeleton loading states

// The component using useConductorCatalog should have a main container with:
// Layout: Flexbox, direction column
// Style: dark mode, slate-900 background

// Before catalog data is loaded, show the following skeleton placeholders:

// 1. Search Input Skeleton:
// Layout: Same size as the actual search input
// Style: rounded corners, bg-zinc-700, h-10

// 2. Inventory Grid Skeleton: (Use Bento Grid or CSS Grid)
//    Create a grid with 2-4 columns, each representing a product card.
//    Each product card skeleton should have:

//    - Image Skeleton:
//      Layout: Placeholder rectangle with aspect ratio 4:3
//      Style: rounded corners, bg-zinc-700

//    - Title Skeleton:
//      Layout: Short line
//      Style: rounded corners, bg-zinc-700

//    - Price Skeleton:
//      Layout: Short line
//      Style: rounded corners, bg-zinc-700

// 3. Implement research animation while loading, similar to a magnifying glass zooming.
// 4. Use the retry banner from react-query for errors, slate-900 background and blue-500 text.

// Tailwind Dark Mode Palette: slate-900, zinc-700, blue-500.  Use standard Tailwind tokens only, no hex codes.
// Ensure sufficient spacing between skeleton elements to mimic actual product cards.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
