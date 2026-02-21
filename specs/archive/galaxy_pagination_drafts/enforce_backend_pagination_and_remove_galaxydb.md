# Spec: Enforce Backend Pagination and Remove GalaxyDB

**Version:** 2.3
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, ensures loading states are handled correctly, refactors the use of `ImageWithFallback`, and implements a research animation while loading.

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
    *   Includes a `ResearchAnimation` component while `isLoading` is true.

6.  **Filtering and Sorting Parameters:** The `useConductorCatalog` hook must pass the filter and sort state as parameters to the API endpoint.
7.  **Error Handling:** Maintain existing error handling for API requests, displaying error messages to the user if the data cannot be fetched. Render a "retry" banner on API failure.
8.  **Image Fallback:** Refactor the usage of the `ImageWithFallback` component to ensure a consistent image loading experience.
9. **Skeleton Loading:** Replace generic loading indicators with the `ResearchAnimation` component (from `frontend/src/components/product/ResearchAnimation.tsx`) while data is fetching. Pass the `brand` to `ResearchAnimation` as the `brandName` prop.

## Behavior Scenarios

1.  **Scenario:** Initial Load
    *   Input: The `useConductorCatalog` hook is called without any parameters.
    *   Outcome: The hook fetches the first page of catalog data (page 1, page size 25) from the `/api/conductor/catalog` endpoint. A `ResearchAnimation` component is rendered while loading.
2.  **Scenario:** Navigating to Page 3
    *   Input: The `useConductorCatalog` hook is called with the `page` parameter set to 3.
    *   Outcome: The hook fetches the third page of catalog data from the `/api/conductor/catalog` endpoint. A `ResearchAnimation` component is rendered while loading.
3.  **Scenario:** Applying a Search Query
    *   Input: The `useConductorCatalog` hook is called with the `searchQuery` parameter set to "Roland".
    *   Outcome: The hook fetches the first page of catalog data, filtered by the search query "Roland", from the `/api/conductor/catalog` endpoint. A `ResearchAnimation` component is rendered while loading.
4.  **Scenario:** API Request Fails
    *   Input: The `/api/conductor/catalog` endpoint returns an error.
    *   Outcome: The hook displays an error message to the user.
5.  **Scenario:** Image URL is invalid
    *   Input: One or more of the products returned has an invalid `image_url`.
    *   Outcome: The `ImageWithFallback` component displays the placeholder image.

## Stitch UI Prompt
```text
// Target Component: useConductorCatalog integration in InventoryView
// Description: Integrate backend pagination and loading animation

// Layout:
// Replace the existing data fetching and rendering logic within InventoryView with the following.

// Visual Style:
// * Dark mode
// * Tailwind CSS

// Component Hierarchy:
// 1. InventoryView
// 2. ResearchAnimation (while loading) or InventoryGrid (when data is available)

// Data Slots:
// * isLoading: boolean (from useConductorCatalog)
// * products: ConductorProduct[] (from useConductorCatalog)
// * brandName: string (product.brand, use "Halilit" if unavailable).

// Instructions:
// Implement backend pagination using react-query for the InventoryView. The component should:

// 1. Fetch data from `/api/conductor/catalog` with page, pageSize, searchQuery, sortBy, category, and brand parameters.  Defaults: page=1, pageSize=25, other filters are empty string.
// 2. DELETE galaxy_db.json.  Ensure that NO code attempts to read this deleted file under any circumstances.
// 3. Render a ResearchAnimation component (refer to frontend/src/components/product/ResearchAnimation.tsx) while `isLoading` is true. Pass brand as brandName, and center the animation in the view.
// 4. When `isLoading` is false, render the InventoryGrid component (existing).

// Code Requirements:
// * Use the correct Tailwind CSS classes for dark mode.
// * Use existing data types as defined in frontend/src/types.

bento layout with ResearchAnimation as a modal overlay
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- Verify in the browser that `galaxy_db.json` is GONE from `frontend/public/data`.
- Verify that the Inventory grid and other views using `useConductorCatalog` load data correctly from the API.
- Verify the ResearchAnimation component is displayed during initial load and page changes.
- Verify that all filter and sort parameters are passed to the backend API.
- Verify that image fallback works correctly.
- Verify that error handling works and a retry banner is displayed on API failure.
