## Overview

The Halilit Support Center application provides product information and inventory management capabilities. It features a frontend built with React, a backend API using FastAPI, and utilizes a data pipeline to fetch, normalize, and serve product data. The application also includes "Factory Agents" for automated code generation, documentation, and strategic planning.

## Frontend Views

*   **DashboardView**:
    *   Route/State: `DASHBOARD` (via `navigationStore`)
    *   Renders: Summary statistics (total products, calls for price, top brands, last ingestion run status) displayed in metric cards.
*   **InventoryView**:
    *   Route/State: `INVENTORY` (via `navigationStore`)
    *   Renders: A paginated list of products, with filtering and search capabilities.
*   **ProductDetailView**:
    *   Route/State: `PRODUCT_DETAIL` (via `navigationStore`)
    *   Renders: Detailed information about a specific product, including images, specifications, and related products.

## Hooks & State

*   `useConductorCatalog`: Fetches and provides product data from the backend. Returns an array of `Product` objects, along with loading state and error information.
*   `useJITIntelligence`: Manages the "JIT Intelligence" process for a product, fetching and processing information in phases (`idle`, `snap`, `intel`, `wisdom`, `complete`, `error`).
*   `useNavigationStore`: A Zustand store managing the application's navigation state, including the current view (`DASHBOARD`, `INVENTORY`, `PRODUCT_DETAIL`, `INGESTION_STATUS`), the active product ID, search query, and a flag for initial call-for-price filter.
*   `useDebounceValue`: A custom hook (inferred from usage in `InventoryView`) used for debouncing search input.

## Backend API

*   `/api/conductor/catalog`: (GET) Returns the product catalog data.
*   `/`: Serves the frontend application.
*   `/docs`: Serves the API documentation (FastAPI).
*   `/redoc`: Serves the API documentation (ReDoc).
*   Other static assets, including frontend assets.
*   `/api/jit/<product_id>`: (GET) Serves JIT intelligence data for a given product ID (inferred).

## Data Pipeline

1.  **Scraping:** (Inferred) Data is fetched from external sources.
2.  **Normalization:** The `product_normalizer.py` module transforms raw product data into a consistent, flat format (`Product` type) with pre-computed fields.
3.  **Catalog Building:** The `build_catalog()` function (inferred from the code) processes the normalized data to create a catalog.
4.  **Serving:** The `/api/conductor/catalog` endpoint serves the catalog data to the frontend.

## Factory Agents

*   `steerer_agent.py`: Identifies and addresses gaps in product specifications based on a "Master Plan."
*   `scribe_agent.py`: Generates and updates documentation based on the codebase.
*   `spec_writer.py`: Translates plain text descriptions into detailed specifications.
*   `builder_agent.py`: Materializes code from specifications.

## Key Conventions

*   **Imports:** Uses absolute imports (e.g. `from backend import ...`).
*   **Product Shape:** Products are normalized to a flat shape in `product_normalizer.py`.
*   **Source Rules:** Enforced by `source_rules.py`; data must come from one of three authorized sources.
