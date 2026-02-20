```markdown
# Halilit Support Center — Architecture

## Overview

The Halilit Support Center is a web application designed to provide product information and support. It features a dashboard, inventory, and product detail views, leveraging data fetched from a backend API and enriched by a JIT (Just-In-Time) Intelligence engine. The application utilizes React for the frontend, a FastAPI backend, and various hooks and stores for data management and navigation.

## Frontend Views

*   **DashboardView**: Renders a dashboard with key metrics.
    *   State: Accessed via the `DASHBOARD` view type in `useNavigationStore`.
    *   Renders: Metric cards displaying product counts, calls for price, top brands, and last ingestion run status.
*   **InventoryView**: Displays a product inventory with filtering and search capabilities.
    *   State: Accessed via the `INVENTORY` view type in `useNavigationStore`.
    *   Renders: A list of products, search input, and filter controls.
*   **ProductDetailView**: Shows detailed information about a specific product.
    *   State: Accessed via the `PRODUCT_DETAIL` view type in `useNavigationStore`, activated by clicking on a product from the `InventoryView`.
    *   Renders: Product details, including sourcing badges, JIT badges, product name, brand, price, and image.

## Hooks & State

*   `useConductorCatalog`: Fetches product data from the `/api/conductor/catalog` endpoint.
    *   Returns: `products`, `isLoading`, `error`, `refetch`.  Also used to fetch data for a single product.
*   `useJITIntelligence`: Manages the JIT (Just-In-Time) Intelligence process for product data enrichment.
    *   Returns: `jitState`
*   `useDebounceValue`: (From `InventoryView.tsx`) Debounces a value, likely for search input.
*   `useNavigationStore`: Manages the application's navigation state.
    *   Returns: `currentView`, `activeProductId`, `searchQuery`, `initialCfpFilter`, `goToDashboard`, `goToInventory`, `goToProduct`.

## Backend API

*   `/api/conductor/catalog`: (GET) Serves the product catalog data.  Returns a pre-indexed catalog: `products[]`, `indexes` (by_galaxy, by_spectrum, by_brand), and `metadata` (galaxy_counts, spectrum_counts, brand_counts, galaxies).

## Data Pipeline

1.  **Scraping:** (Implied, not directly visible in the code) External data sources are scraped (e.g., product pages).
2.  **Normalization:** The `product_normalizer.py` module processes and normalizes the scraped product data into a consistent, flat format.
3.  **Catalog:** The normalized data is built into a catalog.
4.  **Frontend:** The frontend consumes the catalog data via the `/api/conductor/catalog` endpoint and the JIT Intelligence data.

## Factory Agents

*   `backend/factory/builder_agent.py`: Materializes code from a specification.
*   `backend/factory/steerer_agent.py`: Identifies gaps in existing specifications and generates new or updated specifications.
*   `backend/factory/scribe_agent.py`: Regenerates the `docs/ARCHITECTURE.md` file based on the codebase.
*   `backend/factory/spec_writer.py`: Translates human intent into detailed specifications.

## Key Conventions

*   **Imports**: Uses `lucide-react` for icons.
*   **Price Formatting**: Uses the `formatPrice` function from `./src/types`.
*   **Source Rules:** Enforced by `backend/source_rules.py`, dictating that all data must originate from authorized sources.
*   **Tailwind**:  Uses Tailwind CSS for styling, with custom accent color tokens (`blue`, `amber`, `green`, `red`, `zinc`).
```