# Spec: Implement Backend Pagination for Catalog Data

**Version:** 1.0
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Refactor the `useConductorCatalog` hook to fetch product catalog data from the backend in paginated form, rather than loading the entire `galaxy_db.json` file on the client-side. This addresses the critical issue of exceeding the 5MB client-side JSON limit, improving performance and reducing memory consumption. This aligns with the "Speed of Service" technical standard.

## Requirements

1.  **Backend Pagination Endpoint:** Modify the `/api/conductor/catalog` endpoint to accept `page` and `pageSize` query parameters and return a paginated subset of the catalog data, along with metadata about the total number of items and pages.

2.  **Data Contract Update:** Update the data contract for `/api/conductor/catalog` to include pagination metadata:

    ```typescript
    interface PaginatedCatalogResponse {
      products: ConductorProduct[];
      totalItems: number;
      totalPages: number;
      currentPage: number;
      pageSize: number;
    }
    ```

3.  **`useConductorCatalog` Hook Modification:** Modify the `useConductorCatalog` hook to:
    *   Accept `page` and `pageSize` parameters.
    *   Fetch data from the paginated `/api/conductor/catalog` endpoint using the provided `page` and `pageSize`.
    *   Return the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize` from the API response.
    *   Use `react-query` to manage the fetching and caching of paginated data.

4.  **Default Page Size:** Set a default `pageSize` value of 25 items per page.

5.  **Error Handling:** Maintain existing error handling for API requests, displaying error messages to the user if the data cannot be fetched.

6.  **Remove `galaxy_db.json`:** Remove the `galaxy_db.json` file from the `frontend/public/data` directory, as it will no longer be used.

## Behavior Scenarios

1.  **Scenario:** Initial Load
    *   Input: `page = 1`, `pageSize = 25`
    *   Outcome: The `useConductorCatalog` hook fetches the first 25 products from the backend.
        The `products` array contains the first 25 products.
        `totalItems`, `totalPages`, `currentPage`, and `pageSize` are correctly populated.

2.  **Scenario:** Navigating to Page 2
    *   Input: `page = 2`, `pageSize = 25`
    *   Outcome: The `useConductorCatalog` hook fetches the next 25 products from the backend.
        The `products` array contains products 26-50.
        `currentPage` is 2.

3.  **Scenario:** Error Fetching Data
    *   Input: The backend returns an error (e.g., 500 Internal Server Error).
    *   Outcome: The `useConductorCatalog` hook returns an error state, and an error message is displayed to the user.

## Stitch UI Prompt
```text
// Target Component: useConductorCatalog hook consumer (e.g., InventoryView)
// Description: Update the InventoryView to work with paginated catalog data.
// NOTE: This prompt assumes the backend pagination API and ConductorProduct type
// are already defined.

// Layout: The InventoryView likely uses a grid or list layout to display products.
// This layout needs to be updated to reflect the paginated nature of the data.

// Visual Style: Maintain the dark theme using Tailwind CSS (slate-900 background, blue-500 accents).
// Use existing component styling (e.g., for product tiles) where possible.

// 1. Pagination Controls:
//    - Add pagination controls (previous/next buttons, page number display)
//      below the product list.
//    - The controls should be disabled when on the first/last page.
//    - Use existing Tailwind CSS classes for styling (e.g., rounded-md,
//      px-4, py-2, text-sm, font-medium).

// 2. Data Slots:
//    - Replace the direct use of `products` with the paginated `products` from the
//      `useConductorCatalog` hook.
//    - Display the current page number and total number of pages.
//      Example: "Page [currentPage] of [totalPages]"

// 3. Hook Integration:
//    - Modify the `useConductorCatalog` hook to accept `page` and `pageSize`
//      parameters (default pageSize to 25).
//    - Fetch paginated data from the backend API.

// 4. Loading State:
//    - Display a loading indicator (skeleton loaders) while fetching data.

// 5. Error Handling:
//    - Display an error message if the API request fails.

// Component Hierarchy:
//    - The InventoryView component should contain:
//        - A product list (using existing product tile component)
//        - Pagination controls

// Spacing:
//    - Use Tailwind CSS spacing classes (e.g., py-4, px-6, gap-4) to
//      create appropriate spacing between elements.

// Tailwind CSS Tokens:
//    - Use existing Tailwind CSS color tokens (slate-900, blue-500, etc.)
//      to maintain a consistent dark theme.

// INSTRUCTIONS:
// - You are STITCH. Generate clean, concise, well-formatted and testable React code.
// - Follow all instructions carefully and use all the given DATA SLOTS.
// - Do not hallucinate package imports.
// - Do not include any comments or extraneous text besides code.
// - Focus on clear code and maintainability.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- `pytest backend/tests/test_catalog_api.py -v` (Add pytest check for pagination API)
