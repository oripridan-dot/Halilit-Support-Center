# Spec: Natural Explorer UX Overhaul - Connect Explorer to Inventory
**Version:** 1.1 · Chief v9.7.2
**Component:** `frontend/src/components/views/ExplorerView.tsx`

---

## 1. Purpose & Intent

Connect the Natural Explorer UX to the core Inventory Master by enabling operators to:

- Search for products within the Explorer view.
- See a live, filtered grid of products within a selected category/brand in the Explorer.
- Navigate to product details.

This spec builds upon `specs/interface/04_natural_explorer_ux.md`, enabling a blended browse + search experience.

---

## 2. Requirements

### 2.1 Search Integration

- Add a search input field above the cascading columns in `ExplorerView.tsx`.
- This input should use the debounced search logic from `frontend/src/components/InventorySearch.tsx` (debounce ≤ 150 ms).
- As the user types, the product list in the rightmost column MUST filter in real time.
- The filter MUST apply to product name, brand, and SKU.

### 2.2 Live Filtered Product Grid

- When a Brand, Category, Family, or Series is selected (i.e., a path is active in `navigationStore.explorerPath`), the rightmost column MUST render a live, filtered product grid.
- This grid MUST use the same data and styling as the main Inventory grid (from `InventoryView.tsx`), but without pagination controls (see 2.3).
- The filter parameters for this grid MUST be derived from:
    - `navigationStore.explorerPath`: Apply filters for `brand`, `category`, `family`, and `series`.
    - The search input field (2.1): Apply the search query to product name, brand, and SKU.
- The grid MUST display the product's name, brand, price, and stock status.
- The grid MUST update in real-time as the explorer path or search query changes.

### 2.3 Disable Pagination

- Because the Explorer view displays a filtered subset of the main catalog, pagination is redundant.
- The live product grid within `ExplorerView.tsx` MUST NOT display pagination controls.
- Instead, the entire matching subset of products should render.

### 2.4 Navigation to Product Detail

- Each product in the live product grid MUST be clickable.
- Clicking a product navigates the user to the `PRODUCT_DETAIL` view for that product, using `useNavigationStore().goToProduct(product.id)`.
- A visual hover state MUST indicate clickability (e.g., a background color change).

### 2.5 Preserve Skeleton Loading

- While the product data is loading, the rightmost column MUST display a skeleton loading state. The skeleton should mimic the layout of the live product grid.

### 2.6 Responsiveness

- The search input and live product grid MUST be responsive and adapt to different screen sizes.

---

## Stitch UI Prompt

```
// Target Component: ExplorerView (rightmost column - live product grid)
// Description:  A React component that shows a filtered, live grid of products based on the explorer path and a search query.  It integrates a search input above the grid and enables navigation to the ProductDetailView on click.
// Layout: Use a Flexbox container.  Above the grid, place a search input field. Below that, render a grid of product cards.

// Visual Style:
//  - Dark mode: Tailwind CSS, slate-900 background, blue-500 accents.
//  - Use existing Tailwind styles from the InventoryView and ProductTile components for visual consistency.
//  - Hover effect: A subtle background color change (e.g., slate-800) on product cards when hovered.

// Data Slots:
//  - Search Input: A text input field with a placeholder "Search products...".  Use existing debounce logic from InventoryView.  The search query filters the product grid in real-time.
//  - Product Grid: A responsive grid of product cards.  Each card displays:
//      - Thumbnail image (use ImageWithFallback with dark placeholder).
//      - Product name (text-white, font-semibold).
//      - Brand (text-zinc-400).
//      - Price (text-blue-300).
//      - Stock Status (badge - use StockBadge component if stock === 0, use Tailwind bg-red-500 text-white).
//      - If price is null, display "Call for Price" (text-red-500).
//  - Placeholder: Display "No products found" if the grid is empty.  Use text-zinc-400.

// Component Hierarchy:
//  - Flex container (direction: column)
//      - Search Input
//      - If loading: display Skeleton (animated shimmer effect) mimicking the grid layout
//      - If error: display error message in red
//      - If products.length > 0: Product Grid (responsive grid with product cards)
//      - Else: "No products found" message

// Spacing:
//  - Padding: 4
//  - Gap between grid items: 4
//  - Margin between search input and product grid: 4

// Navigation:
// - Each product card should be clickable and navigate to the ProductDetailView with productId
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
