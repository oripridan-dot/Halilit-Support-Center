# Spec: Enforce Backend Pagination and Remove galaxy_db.json
**Version:** 2.0
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, and ensures loading states are handled correctly. This spec also ensures that totalItems, totalPages, currentPage, and pageSize are returned from the hook.

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
8. **Image Fallback:** Implement image fallback logic. If `product.image_url` is missing or fails to load, use `/placeholder.png`. This logic should use the existing `<ImageWithFallback>` component.
9. **Skeleton Loading State:** While the data is loading, display a skeleton loading state to improve user experience. This skeleton should mimic the layout of the inventory grid.

## Behavior Scenarios

1.  **Scenario:** Initial Load
    *   Input: `page = 1`, `pageSize = 25`, no filters or sorting applied.
    *   Outcome: The `useConductorCatalog` hook fetches the first page of products from the API. A skeleton loading state is displayed while the data is being fetched.
2.  **Scenario:** User Navigates to Page 3
    *   Input: `page = 3`, `pageSize = 25`.
    *   Outcome: The `useConductorCatalog` hook fetches the third page of products from the API.
3.  **Scenario:** API Request Fails
    *   Input: The `/api/conductor/catalog` endpoint returns an error.
    *   Outcome: The `useConductorCatalog` hook displays an error message to the user.
4. **Scenario:** Image URL is broken
    *   Input: A `ConductorProduct` has a broken `image_url`.
    *   Outcome: The `ImageWithFallback` component renders `/placeholder.png`.

## Stitch UI Prompt
```text
// Target Component: useConductorCatalog Hook Consumer
// Description: This prompt is to help implement a skeleton loading state for a component that uses the `useConductorCatalog` hook and displays data in a grid format.
// Desired Layout:  A grid layout mimicking the data, displaying rectangular placeholders for images, text, etc.
// Visual Style: Dark mode, Tailwind CSS, slate-900 background, skeleton placeholders should be a lighter shade of gray (e.g., zinc-700).
// Component Hierarchy:  The main component using the `useConductorCatalog` hook is wrapped in a container. Inside this container, create a grid of skeleton items.
// Data Slots:  N/A (Skeleton loading state, no actual data).
// Spacing and Padding:  Use Tailwind CSS classes (e.g., `p-4`, `gap-4`) to create consistent spacing.
// Placeholder Styles:  Each placeholder element should be a rectangular div with a rounded corner.
// Example Code (Tailwind CSS):
<div className="grid grid-cols-4 gap-4 p-4"> //Container for skeleton
  <div className="bg-zinc-700 rounded-md h-48 w-full"></div> //Placeholder for image
  <div className="bg-zinc-700 rounded-md h-8 w-3/4"></div> //Placeholder for text
  <div className="bg-zinc-700 rounded-md h-6 w-1/2"></div> //Placeholder for text
  //...repeat the placeholder elements as necessary
</div>
//Instructions:
//1.  Generate React TSX code for a component that consumes the `useConductorCatalog` hook.
//2.  Implement a skeleton loading state using rectangular placeholder elements.
//3.  Use Tailwind CSS classes.
//4. Make sure the skeleton placeholders look good with dark theme, slate-900
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- Verify that `frontend/public/data/galaxy_db.json` no longer exists.
- Manually verify that the inventory grid loads the first page of results by default and that navigating pages updates the grid correctly.
- Manually verify that skeleton loading is displayed while the data is loading.
