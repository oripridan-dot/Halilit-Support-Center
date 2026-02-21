# Spec: Final Enforced Backend Pagination and Removal of galaxy_db.json (Performance Enhanced)
**Version:** 6.0
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

To achieve definitive removal of the `galaxy_db.json` file, ensuring optimal performance by enforcing exclusive reliance on the backend API for paginated product catalog data. This addresses exceeding the 5MB client-side JSON limit, preventing future dependence on the local file, and adds polished transition states with skeletons.

## Requirements

1.  **Definitive `galaxy_db.json` Deletion:** The file `frontend/public/data/galaxy_db.json` MUST be physically DELETED. The hook MUST NOT try to load the file.

2.  **Exclusive API Dependency:** The `useConductorCatalog` hook MUST fetch data *solely* from `/api/conductor/catalog`. No attempts to access `galaxy_db.json` are permitted.

3.  **Backend Pagination Contract:** Verify the `/api/conductor/catalog` endpoint correctly handles the following, returning a paginated subset of the catalog:
    *   Query parameters: `page`, `pageSize`, `searchQuery`, `sortBy`, `category`, and `brand`.
    *   Backend defaults: `pageSize` to 25 and `page` to 1 if not specified.
    *   Sorting: Sorts "In Stock" items above "Call for Price" items.

4.  **Strict Data Contract Compliance:** The API response from `/api/conductor/catalog` MUST match:

    ```typescript
    interface PaginatedCatalogResponse {
      products: ConductorProduct[];
      totalItems: number;
      totalPages: number;
      currentPage: number;
      pageSize: number;
    }
    ```

5.  **Enhanced `useConductorCatalog` Hook:**
    *   Accepts optional `page`, `pageSize`, `searchQuery`, `sortBy`, `category`, and `brand` parameters (defaults: `1`, `25`, `''`, `''`, `''`, `''`).
    *   Fetches data using the provided parameters.
    *   Returns `products`, `totalItems`, `totalPages`, `currentPage`, and `pageSize` from the API.
    *   Implements `react-query` for data fetching and caching.
    *   Implement skeleton components for loading states in parent components using the hook.
    *   Render a retry banner on API failure.

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
// Style: rounded corners, bg-zinc-700

// 2. Inventory Grid Skeleton: (Use Bento Grid Layout):
// 3 rows of skeletons for product tiles
//    a. row 1: 4 columns
//    b. row 2: 4 columns
//    c. row 3: 4 columns

// Each Column has the following elements.

// a. Image Skeleton:
//    Layout: Square aspect ratio (e.g., width: 100%, height: auto)
//    Style: rounded corners, bg-zinc-700

// b. Product Name Skeleton:
//    Layout: Single line of text
//    Style: rounded corners, bg-zinc-700, width: 80%

// c. Product Description Skeleton:
//    Layout: Two lines of text
//    Style: rounded corners, bg-zinc-700, width: 60%

// Use subtle animation on skeletons (e.g., a shimmering effect) to indicate the loading state. Ensure skeletons use Tailwind CSS and match the Halilit dark theme.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`