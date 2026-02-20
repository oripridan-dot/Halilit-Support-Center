## Overview

The Halilit Support Center is a web application designed as a dense, data-forward console for managing product information and providing real-time intelligence. The frontend offers views for dashboard, inventory, and product details. The backend provides a FastAPI server that serves data and facilitates JIT (Just-In-Time) product intelligence.

## Frontend Views

*   **DashboardView**: Renders a dark console with dashboard statistics. Uses `/api/dashboard/stats` to fetch data.
*   **InventoryView**: Displays a searchable inventory of products. Uses `useConductorCatalog` hook. Filterable by search text, product name, and brand.
*   **ProductDetailView**: Displays detailed information about a product, including responsive images.

## Hooks & State

*   **`useConductorCatalog`**: Fetches and provides product data from the `/api/conductor/catalog` endpoint. Returns an object with `products`, `isLoading`, and `error` properties.
*   **`useDebounceValue`**: Debounces a value to prevent excessive updates.
*   **`useNavigationStore`**: Manages the application's navigation state, including the current view (`DASHBOARD`, `INVENTORY`, `PRODUCT_DETAIL`, `INGESTION_STATUS`, `EXPLORER`), the active product ID, search query, and a flag for an initial call-for-price filter.
*   **`useJITIntelligence`**: Manages the Just-In-Time intelligence phases: `idle`, `snap`, `intel`, `wisdom`, `complete`, `error`.

## Backend API

*   `/api/dashboard/stats` (GET): Returns dashboard statistics in the format of `DashboardStats`.
*   `/api/conductor/catalog` (GET): Returns product catalog data.
*   `/api/jit/product/{product_id}` (GET): Returns JIT intelligence data for a product.

## Data Pipeline

1.  A scraper (not shown in this snapshot) collects product data.
2.  The `product_normalizer.py` normalizes the product data into a consistent format.
3.  The normalized data is used to build a catalog.
4.  The catalog is served by the `/api/conductor/catalog` endpoint and consumed by the frontend.

## Factory Agents

*   `steerer_agent.py`: Identifies gaps in existing specifications and generates new or updated specs.
*   `scribe_agent.py`: Reads the codebase and regenerates documentation.
*   `spec_writer.py`: Translates human intent into Markdown specifications.
*   `builder_agent.py`: Materializes code from a spec.

## Key Conventions

*   **Imports**: Standard React and TypeScript imports, along with `lucide-react` for icons and `@tanstack/react-query` for data fetching.
*   **Naming**: Component names are PascalCase. Files are named consistently.
*   **Tailwind**: The application uses Tailwind CSS for styling.
*   **Source Rules**: All data must come from one of three authorized sources (not specified in the code).
