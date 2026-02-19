# ARCHITECTURE - Halilit Support Center

## Overview

The Halilit Support Center is a web application designed for product information management and live intelligence gathering. It provides views for exploring product inventory, detailed product information, and a dashboard for monitoring system status. The application leverages a backend API for data retrieval and real-time intelligence via Gemini.

## Frontend Views

*   **DashboardView:** `/` - Displays dashboard metrics including total products, calls for price, top brands count, and the status of the last ingestion run. Uses `MetricCard` components.
*   **InventoryView:** `/inventory` or `DASHBOARD -> INVENTORY` - Shows a paginated list of products, with filtering and search capabilities.
*   **ProductDetailView:** `PRODUCT_DETAIL` state - Displays detailed information about a selected product, including sourcing information via `SourcingBadge`.

## Hooks & State

*   **`useConductorCatalog`:** Fetches and provides access to product data from `/api/conductor/catalog`. Returns products, loading state, and error information. The product data is shaped by `product_normalizer.normalize_product()`.
*   **`useJITIntelligence`:** Manages the JIT (Just-In-Time) intelligence process for a product, handling phases like `snap`, `intel`, `wisdom`, and `complete`.
*   **`useNavigationStore`:** (Zustand) Manages navigation state between views (`DASHBOARD`, `INVENTORY`, `PRODUCT_DETAIL`, `INGESTION_STATUS`), the active product ID, search query, and an initial CFP filter.
*   **`useDebounceValue`:** Debounces a value, used in `InventoryView`.

## Backend API

*   `/api/conductor/catalog`: (GET) Returns the product catalog data.
*   `/api/jit/{product_id}`: (GET) Returns JIT intelligence data for a given product ID (streams SSE events).
*   `/`: (GET) Serves the frontend application.
*   `/docs`: Serves FastAPI documentation.

## Data Pipeline

1.  **Scraping**: (Not visible in this code) Data is scraped from Halilit product pages, official brand pages, and trusted review sites.
2.  **Normalization**: The `product_normalizer.py` module processes raw product data, ensuring a consistent and predictable data shape. It pre-computes galaxy and spectrum IDs.
3.  **Catalog**: The normalized product data is built into a catalog.
4.  **Frontend**: The frontend uses `useConductorCatalog` to fetch the catalog and display product data.

## Factory Agents

*   **`steerer_agent.py`:** Identifies and addresses gaps in product specifications.
*   **`scribe_agent.py`:** Generates and updates documentation (this document).
*   **`spec_writer.py`:** Converts plain text descriptions into detailed specifications.
*   **`builder_agent.py`:** Materializes code from specifications.

## Key Conventions

*   **Imports**: Uses `@tanstack/react-query`, `react-router-dom`, `zustand`, and `lucide-react` icons.
*   **Product Shape**:  The `Product` type (defined in `types.ts`) matches the output of `product_normalizer.normalize_product()`.
*   **Source Rules**: Enforced by `backend/source_rules.py`. Data must come from Halilit, official brands, or trusted reviews.
*   **Pricing**: Prices are sourced from Halilit.
*   **Stock**:  Stock status is displayed using the `StockBadge` component.
*   **Frontend Data**: All product data is pre-indexed in the backend for fast frontend access.
*   **File Cache**:  The JIT agent uses a 7-day TTL file cache.
