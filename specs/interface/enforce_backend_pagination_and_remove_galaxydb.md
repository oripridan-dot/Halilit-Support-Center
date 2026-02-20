# Spec: Enforce Backend Pagination and Remove GalaxyDB

**Version:** 1.6
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API. This version incorporates image fallback using a shared component.

## Requirements

1.  **Total `galaxy_db.json` Removal:** Physically DELETE the `galaxy_db.json` file from the `frontend/public/data` directory.
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

6.  **Image Fallback Component:** Create (if not exists) and use the `ImageWithFallback` component to display product images with a fallback mechanism.

7.  **Error Handling:** Maintain existing error handling for API requests, displaying error messages to the user if the data cannot be fetched.

## Behavior Scenarios

1.  **Scenario:** Initial Load
    *   Input: `page = 1`, `pageSize = 25`, no search query, default sorting.
    *   Outcome: The hook fetches the first page of catalog data from the backend and returns 25 products (or less if fewer than 25 products exist). The total number of items, total pages, current page, and page size are also returned.

2.  **Scenario:** User Navigates to Next Page
    *   Input: `page = 2`, `pageSize = 25`, no search query, default sorting.
    *   Outcome: The hook fetches the second page of catalog data from the backend and returns 25 products (or less if fewer than 25 products exist). The total number of items, total pages, current page, and page size are also returned.

3.  **Scenario:** User Performs a Search
    *   Input: `page = 1`, `pageSize = 25`, `searchQuery = "keyboard"`, default sorting.
    *   Outcome: The hook fetches the first page of search results from the backend and returns 25 products (or less if fewer than 25 products match the search query). The total number of matching items, total pages, current page, and page size are also returned.

4. **Scenario: API Error**
    * Input: The `/api/conductor/catalog` endpoint returns a 500 error.
    * Outcome: The hook returns an error object, and the UI displays an appropriate error message to the user.

## Stitch UI Prompt
```text
// Component: useConductorCatalog
// Description: React hook that fetches and provides access to a paginated product catalog from a backend API.  Includes filtering, sorting, and pagination support.  Should NOT attempt to read any local files.

// Layout: This is NOT a visual component. It is a React Hook with pagination and filtering logic.
// Visual Style: N/A

// Data Slots:
//  - page: number (current page number)
//  - pageSize: number (number of items per page)
//  - searchQuery: string (search query)
//  - sortBy: string (field to sort by)
//  - category: string (category filter)
//  - brand: string (brand filter)
//  - products: ConductorProduct[] (array of product objects)
//  - totalItems: number (total number of items in the catalog)
//  - totalPages: number (total number of pages in the catalog)
//  - isLoading: boolean (indicates if the data is currently being fetched)
//  - error: any (contains any error that occurred during the data fetch)

//  ConductorProduct interface:
//   - id: string;
//   - name: string;
//   - brand: string;
//   - brand_logo?: string;
//   - galaxy_id?: string;
//   - spectrum_id?: string;
//   - category?: string;
//   - price?: number;
//   - price_eilat?: number;
//   - tier?: string;
//   - image_url?: string;
//   - image_gallery?: string[];
//   - description?: string;
//   - description_short?: string;
//   - specs?: Record<string, unknown>;
//   - features?: string[];
//   - rating?: number;
//   - review_count?: number;
//   - pros?: string[];
//   - cons?: string[];
//   - quality_score?: number;
//   - data_status?: string;
//   - data_missing?: string[];
//   - halilit_url?: string;
//   - official_url?: string;
//   - sources?: string[];
//   - family_id?: string | null;
//   - variant_key?: string | null;
//   - relationship_ids?: string[];

// Instructions:
//  - Implement a React hook using @tanstack/react-query to fetch paginated product catalog data from the /api/conductor/catalog endpoint.
//  - Accept optional parameters for page, pageSize, searchQuery, sortBy, category, and brand.
//  - Construct the API URL with the appropriate query parameters.
//  - Handle loading and error states.
//  - Return the products array, totalItems, totalPages, currentPage, pageSize, isLoading, error, and refetch from the hook.
//  - Ensure that the hook does NOT attempt to read or import the galaxy_db.json file.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- (Manual test): Verify that `galaxy_db.json` is physically deleted from the `frontend/public/data` directory.
- (Manual test): Verify that the Inventory Grid and Product Detail pages load correctly with data fetched from the backend API. Verify that filtering, sorting, and pagination work as expected.
