```markdown
# Halilit Support Center — Architecture

## Overview

The Halilit Support Center is a web application designed to provide product information and support. It features a dashboard, inventory view, and product detail view. The application uses a FastAPI backend to serve data, including a pre-built product catalog and JIT (Just-In-Time) intelligence. The frontend is built with React and uses `tanstack/react-query` for data fetching and `zustand` for state management.

## Frontend Views

*   **DashboardView**: Renders dashboard statistics and last ingestion run status. Accessed via the `DASHBOARD` view in the navigation store.
*   **InventoryView**: Displays a list of products.  Accessed via the `INVENTORY` view in the navigation store.
*   **ProductDetailView**: Shows detailed information for a specific product, including SKU and a copy button. Accessed via the `PRODUCT_DETAIL` view in the navigation store.

## Hooks & State

*   **`useConductorCatalog`**: Fetches and provides access to the product catalog data from `/api/conductor/catalog`.
*   **`useJITIntelligence`**: Manages the JIT (Just-In-Time) intelligence phases for product research and data loading. Returns JITPhase.
*   **`navigationStore`**:  Manages the application's navigation state (current view, active product ID, search query, and call-for-price filter). Stores `ViewType`, `activeProductId`, `searchQuery`, and `initialCfpFilter`.

## Backend API

*   `/api/conductor/catalog` (GET): Returns the product catalog data.
*   `/api/jit/{product_id}` (GET): Returns JIT intelligence data for a product, streamed via SSE events.

## Data Pipeline

1.  A scraper (not shown in the code) gathers product data.
2.  `product_normalizer.py` normalizes the data into a consistent format.
3.  `build_catalog()` (in `backend/product_normalizer.py`) builds the product catalog.
4.  The frontend consumes the catalog data from the `/api/conductor/catalog` endpoint.

## Factory Agents

*   **`builder_agent.py`**: Materializes code from a specification.
*   **`steerer_agent.py`**: Identifies critical gaps in specifications and generates new/updated specs.
*   **`scribe_agent.py`**: Regenerates documentation based on the codebase.
*   **`spec_writer.py`**: Translates human intent into specifications.

## Key Conventions

*   **Imports**: Uses relative imports within the project.
*   **Product Shape**: Frontend relies on a guaranteed, flat product shape defined by `product_normalizer.normalize_product()`.
*   **Source Rules**:  All data must come from one of three authorized sources, as defined in `backend/source_rules.py`.
