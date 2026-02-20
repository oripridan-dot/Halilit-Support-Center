# Synthesis Directive — genome_inventory_grid

## Target
InventoryGrid component in the main application UI.

## Fitness Goal
MAX_SCAN_VELOCITY (fastest possible filtering of the grid on user search input)

## Required States
- LOADING → `isLoading` from `useConductorCatalog` hook. `animate-pulse` on skeleton cards.
- ERROR → `error` from `useConductorCatalog` hook. Use the specified Tailwind classes for error display.
- EMPTY → Check `data?.products.length === 0` after successful load. Apply Tailwind classes.
- READY → Check `!isLoading && !error && data?.products.length > 0`. Render the product grid.
- SEARCH_ACTIVE → `useState` hook for search term. `useEffect` to filter `data.products` based on the search term. Render filter chip.
- NO_RESULTS → Check `filteredProducts.length === 0` after search.  Render empty state with search icon.

## Required Traits
- ColorPhenotype → Use Tailwind's `dark:` variants and the provided slate/zinc palette.
- AccessibilityPhenotype → Add `aria-label` attributes to all interactive elements (search bar, sort dropdown, grid items). Ensure keyboard navigation.
- ErrorBoundaryPhenotype → Wrap the entire component in a `<GlobalErrorBoundary>` or use a local `try/catch` block during data fetching and rendering to prevent crashes.
- GridDensityPhenotype → Implement a `useState` hook to control grid column count (4 columns for COMFORTABLE on xl screens).
- QualityScorePhenotype → Create a reusable `QualityScoreBadge` component that renders a badge with a background color based on the score: green (>80), amber (50-80), red (<50).
- PricePhenotype → Display both `price` and `price_eilat` from `ConductorProduct`.  Only show `price_eilat` if it differs from `price`.
- SearchPhenotype → Implement client-side fuzzy search using a library like `fuse.js` or `fast-levenshtein` on the `search_text` field of each `ConductorProduct`. Debounce input to avoid excessive filtering.
- SortPhenotype → Implement a `useState` hook for the selected sort option.  Persist the selection in `sessionStorage`. Use a `useEffect` to sort the `data.products` array based on the selected option.

## Phenotype Assertions (must ALL pass after build)
- Search must filter visually within 16ms (no re-fetch)
- Quality score badge colors must follow the three-tier threshold
- DUAL_PRICE: only show Eilat price if it differs from IL price
- NEVER invent prices — only render prices from Commercial source

## Environment Contracts
- Use `useConductorCatalog` hook to fetch catalog data.
- Use `ConductorProduct` interface as the type for individual product data.
- Use `CatalogMetadata` interface for catalog metadata.
- Use `import { useQuery } from '@tanstack/react-query';`
- Use `Product` data structure for each Inventory Item. `interface Product {id:string, name:string, brand:string, price:number, price_eilat:number, quality_score:number, image_url:string, search_text:string}`

## Builder Instructions
1.  Prioritize performance: Debounce search input, memoize expensive computations (e.g., filtering and sorting), and use virtualized lists if necessary to handle large catalogs.
2.  Implement the sort functionality using a pure function, ensuring that the original `data.products` array is not mutated.
3.  Create a reusable `ProductCard` component to render individual products in the grid. The card should display the image, brand, title, price(s), and quality score badge.
4.  Implement robust error handling to gracefully handle network errors and invalid data. Display user-friendly error messages.
5.  Ensure that the component is fully responsive and adapts to different screen sizes. Use Tailwind's responsive modifiers.
