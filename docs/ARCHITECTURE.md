```markdown
# Halilit Support Center — Architecture Overview

The Halilit Support Center is a web application designed for managing product information and providing real-time intelligence. It features a dashboard, inventory view, and product detail view, with backend services for data fetching, JIT (Just-In-Time) intelligence, and a factory for automated code generation and documentation.

## Frontend Views

*   **DashboardView**: `/` (via `NavigationStore`). Displays summary statistics and the status of the last data ingestion run. Uses components like `MetricCard`.
*   **InventoryView**: `/inventory` (via `NavigationStore`). Displays a list of products fetched from `/api/conductor/catalog`. Includes a search filter and stock badges.
*   **ProductDetailView**: `/product/:id` (via `NavigationStore`). Displays detailed information about a product, including accessory recommendations fetched from `/api/v1/products/{productId}/accessories`.

## Hooks & State

*   **`useConductorCatalog`**: Fetches and provides access to product data from `/api/conductor/catalog`. Returns `products`, `isLoading`, and `error`.
*   **`useJITIntelligence`**: Manages the JIT (Just-In-Time) intelligence process, tracking phases like `snap`, `intel`, `wisdom`, and `complete`.
*   **`useDebounceValue`**: Debounces a value. (Used in `InventoryView`).
*   **`useNavigationStore`**: Manages application navigation between Dashboard, Inventory, and Product Detail views. Stores `currentView`, `activeProductId`, `searchQuery`, and `initialCfpFilter`.

## Backend API

*   `/api/conductor/catalog`: (GET) Returns product catalog data.
*   `/api/v1/products/{productId}/accessories`: (GET) Returns accessory recommendations for a given product.
*   `/`: (GET) Serves the static frontend assets.

## Data Pipeline

1.  **Scraping**: (implied, not shown). Data is scraped from external sources (not defined in the provided code).
2.  **Normalization**: The `product_normalizer.py` module processes scraped data into a consistent product shape.  This module pre-computes galaxy and spectrum IDs.
3.  **Catalog Build**: The `build_catalog` function (in `backend/server.py`) builds the catalog (loaded from frontend/public/data/).
4.  **Frontend Consumption**: The frontend consumes the catalog data via the `/api/conductor/catalog` endpoint and accessory data via the `/api/v1/products/{productId}/accessories` endpoint.

## Factory Agents

*   **`steerer_agent.py`**: Identifies gaps in existing specs and generates new or updated specs.
*   **`scribe_agent.py`**: Reads the codebase and regenerates documentation.
*   **`spec_writer.py`**: Translates human intent into Markdown specifications.
*   **`builder_agent.py`**: Materializes code from a specification.

## Key Conventions

*   **Imports**:  Uses `@tanstack/react-query`, `lucide-react` for icons, `react-router-dom`, `next/router`, and `zustand` for state management.
*   **Product Shape**: Canonical product shape defined in `useConductorCatalog.ts` and normalized by `product_normalizer.py`.
*   **Tailwind**: Uses Tailwind CSS for styling, with custom accent color tokens (`blue`, `amber`, `green`, `red`, `zinc`).
*   **Source Rules**: Enforced by `backend/source_rules.py`.  All data must come from authorized sources.
