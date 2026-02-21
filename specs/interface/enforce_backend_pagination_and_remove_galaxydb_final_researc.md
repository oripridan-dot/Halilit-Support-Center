# Spec: Enforce Backend Pagination and Remove GalaxyDB (Final + Research Animation + Graceful Error Handling + Polished Animation + Stock and CfP Sorting)
**Version:** 4.0
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the critical issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, handles loading states correctly, refactors the use of `ImageWithFallback`, displays an animated magnifying glass during data fetching, adds graceful error handling, showing a retry banner if the API fails, improves the research animation, polishes the animation's timing for a smoother user experience, and enforces stock and CfP sorting.

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
    *   Uses `react-query` to manage the fetching and caching of paginated data.
    *   Displays a loading indicator with an animated magnifying glass while fetching data.
    *   Implements graceful error handling, displaying a retry banner if the API request fails.
    *   Refactors the usage of the `ImageWithFallback` component to ensure a consistent image loading experience.
6.  **Stock and CfP Sorting:** Implement the stock and CfP sorting logic *within the hook* when fetching data. Prioritize "In Stock" (stock > 0) items first, then "Unconfirmed Stock" (stock === null), then "Out of Stock" (stock === 0). Within each stock group, prioritize non-CfP items (price !== null && price > 0) before CfP items (price === null || price === 0).
7.  **Research Animation:** Implement a visually engaging research animation (magnifying glass) to indicate that data is being fetched. Polish the animation for a smooth user experience. The animation MUST only display while loading.
8.  **Graceful Error Handling:** Implement a retry banner to inform users of API request failures, providing a retry action.

## Stitch UI Prompt

```text
// Target Component: useConductorCatalog hook + InventoryGrid
// Description: A React hook for fetching paginated catalog data + UI integration
//
// The goal is to display a list of Halilit products with responsive images and the ability to sort and filter them based on stock status and price.
// Include a loading animation and error handling.
//
// Layout:
//   - InventoryGrid: A grid layout for the products
//   - ProductTile: A component for each product in the grid, displaying the image, name, and price.
//   - PaginationControls: Controls for navigating between pages of products.

// Data Slots (Use these placeholders in the code - DO NOT hardcode real values):
//   - products: ConductorProduct[] - An array of product objects
//   - product.id: string - The unique ID of the product (e.g., "HAL-1234")
//   - product.name: string - The name of the product (e.g., "Keyboard")
//   - product.brand: string - The brand of the product (e.g., "Yamaha")
//   - product.price: number - The price of the product (e.g., 299.99)
//   - product.image_url: string - The URL of the product image (e.g., "https://example.com/keyboard.jpg")
//   - product.stock: number | null - The stock quantity, null for unconfirmed, 0 for out of stock, > 0 for in stock
//   - product.price_eilat: number | null - Price in Eilat

// Visual Style:
//   - Dark mode: Use Tailwind CSS with a slate-900 background for the main container and blue-500 accents for interactive elements.
//   - Use a subtle gray for text labels and product names.
//   - Red for out-of-stock indicators, amber for unconfirmed stock.
//   - Pagination controls with a light background and rounded corners.
//   - Ensure proper spacing between elements for a clean and professional look.

// Component Hierarchy:
//   - InventoryGrid (main container)
//     - ResearchAnimation (magnifying glass loading indicator – animated) - Display only when loading is true
//     - ProductTile (repeated for each product)
//        - ImageWithFallback (display image or placeholder)
//        - ProductName (product.name)
//        - PriceDisplay (product.price, product.price_eilat)
//        - StockStatusBadge (If product.stock is 0, null, > 0 - uses red, amber or green)
//        - CallForPriceIndicator (If price is null or zero - copies SKU on tap)
//     - PaginationControls

// Special Instructions:
//   - The ResearchAnimation MUST fade in smoothly on load and have a smooth magnifying glass icon animation (subtle scale and rotation) that suggests "research" is in progress.
//   - Display a retry banner if there is an error, using Tailwind's amber-500 for the banner background. Include a prominent "Retry" button using Tailwind's blue-500 as the background on hover.
//   - Sort the product array FIRST by stock status (In Stock > Unconfirmed > Out of Stock) and THEN by price (non-CfP > CfP) within each stock status group. Use a stable sort to maintain the original order of products with the same stock status and price.

```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
