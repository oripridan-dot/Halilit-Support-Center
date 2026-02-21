# Spec: Enforce Backend Pagination and Remove GalaxyDB (Final + 💅)
**Version:** 3.2
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the critical issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, handles loading states correctly, refactors the use of `ImageWithFallback`, and displays an animated magnifying glass during data fetching. This final version adds polish to the research animation.

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
    *   Displays a loading indicator while fetching data.

6.  **Filtering and Sorting Parameters:** The `useConductorCatalog` hook must pass the filter and sort state as parameters to the API endpoint.

7.  **Error Handling:** Maintain existing error handling for API requests, displaying error messages to the user if the data cannot be fetched. Render a "retry" banner on API failure.

8.  **Image Fallback:** Refactor the usage of the `ImageWithFallback` component to ensure a consistent image loading experience.

9.  **Skeleton Loading:** Render a skeleton loader while the data is fetching. Use the `ResearchAnimation` component to improve loading UX. Use `brandName: "Halilit"` and `brandColor: "#0ea5e9"` (sky-500). The `ResearchAnimation` component should be displayed while the data is being fetched.

## Stitch UI Prompt
```text
// Target Component: useConductorCatalog Loading State
// Description: Replace the generic loading indicator with a visually appealing "Researching..." animation.
// Layout: N/A - This is a hook, but the implementation affects the UI.
// Visual Style: Dark mode, Tailwind CSS, slate-900 background, sky-500 accents (Halilit brand).
// Data Slots:
//   - brandName: "Halilit" (string)
//   - brandColor: "#0ea5e9" (string)

// Component Hierarchy:
//   - Replace existing loading indicator in any component using useConductorCatalog (e.g., InventoryView) with the ResearchAnimation component.

// Details:
//   - Instead of a simple spinner, use the ResearchAnimation component.
//   - Pass "Halilit" as the brandName prop and "#0ea5e9" as the brandColor prop.
//   - The ResearchAnimation component should be centered within the loading area. Ensure the text is legible against the dark background.

// Tailwind Classes:
//   -  For the surrounding container: flex flex-col items-center justify-center (or similar centering classes).
//   -  For the ResearchAnimation component: className prop can be used to add any additional styles. Make sure the loading area maintains the layout and padding from existing designs.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
