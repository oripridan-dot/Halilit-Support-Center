# Spec: Final Enforcement of Backend Pagination and Removal of `galaxy_db.json` with Enhanced UI Feedback and Stock/CfP Sorting

**Version:** 5.0
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

This specification represents the culmination of efforts to eliminate reliance on the large `galaxy_db.json` file, ensuring optimal performance and scalability for the Halilit Support Center. This version introduces polished UI elements for loading, error handling, and enhanced control over sorting based on stock and "Call for Price" (CfP) status. It completely removes `galaxy_db.json`, enforcing backend pagination and providing a seamless user experience.

## Requirements

1.  **Irreversible `galaxy_db.json` Elimination:** Physically DELETE the `frontend/public/data/galaxy_db.json` file. No vestige of this file should remain in the codebase.

2.  **Unwavering Dependency Isolation:** The `useConductorCatalog` hook MUST *exclusively* fetch data from the `/api/conductor/catalog` endpoint. Any attempt to access or import `galaxy_db.json` will constitute a failure.

3.  **Robust Backend Pagination Implementation:** The `/api/conductor/catalog` endpoint MUST correctly interpret `page`, `pageSize`, `searchQuery`, `sortBy`, `category`, and `brand` query parameters, delivering a paginated response with accurate metadata: `products`, `totalItems`, `totalPages`, `currentPage`, `pageSize`. The backend MUST default `pageSize` to 25 and `page` to 1 if these parameters are omitted. The sorting MUST place "In Stock" items first, then sort CfP above non-CfP items within each stock group.

4.  **Strict Data Contract Adherence:** The `/api/conductor/catalog` endpoint's response MUST conform to the following TypeScript interface:

    ```typescript
    interface PaginatedCatalogResponse {
      products: ConductorProduct[];
      totalItems: number;
      totalPages: number;
      currentPage: number;
      pageSize: number;
    }
    ```

5.  **`useConductorCatalog` Hook Implementation — The Final Word:**
    *   The hook MUST accept optional `page`, `pageSize`, `searchQuery`, `sortBy`, `category`, and `brand` parameters, defaulting to `1`, `25`, `''`, `''`, `''`, and `''` respectively.
    *   Data retrieval from the paginated `/api/conductor/catalog` endpoint MUST leverage the provided parameters.
    *   The hook MUST accurately return `products`, `totalItems`, `totalPages`, `currentPage`, and `pageSize` from the API response.
    *   `react-query` MUST manage data fetching and caching.
    *   A polished "research animation" (e.g., animated magnifying glass icon) MUST be displayed during data fetching, providing clear visual feedback.
    *   Graceful error handling with a "retry" banner MUST be implemented to address API failures.
    *   `ImageWithFallback` MUST be used for all product images, ensuring a consistent and reliable image loading experience.
    *   Stock and CfP sorting MUST be applied according to Spec `interface/inventory_search_stock_cfp_sorting.md`.

6.  **Aggressive Filtering and Sorting Integration:** The `useConductorCatalog` hook must seamlessly integrate filtering and sorting, ensuring all user-specified criteria are communicated to the backend API.

7.  **Loading State Enforcement:** A loading state with a research animation MUST be actively displayed while catalog data is being fetched.

## Stitch UI Prompt

```text
// Target Component: InventoryView or ProductTile (depending on where you use the hook)
// Description: The component that consumes the useConductorCatalog hook
// Style: Dark mode, Tailwind CSS, slate-900 background, blue-500 accents

// Layout:
// The layout depends on the parent component (InventoryView or ProductTile). For InventoryView, it's a grid; for ProductTile, it's a card.

// Visual Style:
// Background: slate-900
// Text: zinc-400
// Primary color: blue-500 (for interactive elements like buttons/links)
// Accent color: zinc-700 (for separators/borders)

// State Management:
// Assume that the component is connected to a Zustand store that provides the following state:
// - isLoading: boolean (true while the data is loading, false otherwise)
// - error: string | null (error message if there's an error, null otherwise)
// - totalItems: number (total number of items in the catalog)
// - currentPage: number (current page number)
// - pageSize: number (number of items per page)
// - products: ConductorProduct[] (array of products to display)

// Create a React component that displays a loading indicator (a magnifying glass icon with a subtle animation),
// an error message (if there's an error), or the product data (if there's no error and the data is loaded).

// Data Slots:
// - isLoading: {boolean} - If true, display a loading indicator instead of the product data.
// - error: {string | null} - If not null, display an error message.
// - totalItems: {number} - The total number of products.
// - currentPage: {number} - The current page number.
// - pageSize: {number} - The number of products per page.
// - products: {ConductorProduct[]} - An array of product objects.

// Component Hierarchy:
// 1. Conditional rendering:
//    - If isLoading: Display the loading indicator (animated magnifying glass).
//    - Else if error: Display the error message.
//    - Else: Display the product data.

// Spacing:
// Use Tailwind CSS spacing classes (e.g., `mt-4`, `mb-2`, `p-4`) for consistent spacing throughout the component.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- Ensure `frontend/public/data/galaxy_db.json` is physically deleted.
- Manual test: Verify that the InventoryView and other catalog views function correctly with filtering, sorting, and pagination. Confirm that stock and CfP sorting are applied correctly.
