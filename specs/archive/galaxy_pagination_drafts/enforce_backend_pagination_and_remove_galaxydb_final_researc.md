# Spec: Enforce Backend Pagination and Remove GalaxyDB (Final + Research Animation + Graceful Error Handling + Polished Animation + Stock and CfP Sorting + Skeleton Placeholder)
**Version:** 4.1
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the critical issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, handles loading states correctly, refactors the use of `ImageWithFallback`, displays an animated magnifying glass during data fetching, adds graceful error handling, showing a retry banner if the API fails, improves the research animation, polishes the animation's timing for a smoother user experience, enforces stock and CfP sorting and adds skeleton placeholders during initial catalog load.

## Requirements

1.  **Total `galaxy_db.json` Removal:** Physically DELETE the `frontend/public/data/galaxy_db.json` file.
2.  **`useConductorCatalog` Dependency Isolation:** Ensure the `useConductorCatalog` hook *solely* relies on the `/api/conductor/catalog` endpoint for data. It must NOT attempt to import or read `galaxy_db.json` under any circumstances.
3.  **Backend Pagination Endpoint:** Verify that the `/api/conductor/catalog` endpoint correctly accepts `page`, `pageSize`, `searchQuery`, `sortBy`, `category`, and `brand` query parameters and returns a paginated subset of the catalog data, along with metadata about the total number of items and pages. The backend should default `pageSize` to 25 if not specified, and if `page` is not specified, it should default to 1. If sorting parameters are being passed, preserve them. The sorting MUST put "In Stock" items first, and then sort CfP above non-CfP items within each stock group.
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
    *   Fetches data from the paginated `/api/conductor/catalog` endpoint using the provided parameters, using `react-query`.
    *   Returns the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize` from the API response.
    *   Displays an animated magnifying glass icon during data fetching. This animation must be smooth and visually appealing.
    *   Implements graceful error handling by displaying a "retry" banner if the API fails to load the data. This banner should allow the user to manually retry the data fetch.

6. **Error Handling**:
    * If the API request fails, display a retry banner at the top of the view. The banner should display a user-friendly error message, such as "Failed to load product catalog. Please try again later."
    * The retry banner should include a button that allows the user to manually retry the data fetch.
7. **Image Fallback:** The `useConductorCatalog` hook is responsible for providing the `image_url` to be used by the `ImageWithFallback` component.
8. **Skeleton Loading Placeholder:** Render skeleton placeholders during the initial catalog load (before any data is available). The skeleton should visually mimic the layout of the inventory grid, providing a loading indication to the user.

## Stitch UI Prompt
```text
// Target Component: useConductorCatalog hook and its implementation

// Description: Create a UI for a product catalog loading state. Use a research or magnifying glass animation during the data fetching process. Implement graceful error handling by displaying a "retry" banner with a user-friendly message and a retry button. The hook will provide the data for the ImageWithFallback component. Show skeleton placeholders during the initial load.
// 1. The retry banner should be positioned at the top. Use Tailwind CSS for styling with a slate-900 background and blue-500 accents.
// 2. Use shimmer style skeleton placeholders.
// 3. The skeleton placeholders should mimic the layout of a product grid, with placeholders for images, titles, and prices.
// Layout: Should use a top-down flexbox layout for overall structure, with the retry banner at the top if needed, then the data with research animation or skeleton loader, then the products.
// Style: dark mode, slate-900 background, blue-500 accents.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
