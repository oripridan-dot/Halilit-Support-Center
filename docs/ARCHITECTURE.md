## Overview

The Halilit Support Center is a web application designed as a dense, data-forward console for managing product information. It features a dark-themed interface with a Vercel/Linear aesthetic and provides views for dashboard statistics, inventory management, and product detail. The application leverages a backend API to fetch and process data, including real-time product intelligence and a catalog of products.

## Frontend Views

*   **DashboardView**: Renders statistical data, including product counts, calls for price, top brands, and ingestion status. Activated via the `DASHBOARD` view type in the navigation store.
*   **InventoryView**: Displays a data table of product inventory. Activated via the `INVENTORY` view type in the navigation store.
*   **ProductDetailView**: Shows detailed information about a specific product. Activated via the `PRODUCT_DETAIL` view type in the navigation store.

## Hooks & State

*   `useConductorCatalog`: Fetches product data from `/api/conductor/catalog`. Returns a catalog with products, indexes, and metadata.
*   `useJITIntelligence`: Manages the JIT (Just-In-Time) intelligence process for product data, including phases like `snap`, `intel`, `wisdom`.
*   `useDebounceValue`: Debounces a value.
*   `useNavigationStore`: Manages the application's navigation state, including the current view (`DASHBOARD`, `INVENTORY`, `PRODUCT_DETAIL`, `INGESTION_STATUS`), active product ID, search query, and a flag for an initial "Call-for-Price" filter.
*   `useDashboardStats`: Fetches dashboard statistics from `/api/dashboard/stats`.

## Backend API

*   `/api/dashboard/stats`: Returns dashboard statistics (method and return type are inferred from the `useDashboardStats` hook).
*   `/api/conductor/catalog`: Serves product catalog data (method and return type are inferred from the `useConductorCatalog` hook).
*   `/`: Serves static frontend assets.

## Data Pipeline

1.  **Scraper**: (Not directly visible in the provided code, but implied) Extracts product information from external sources.
2.  **Normalizer**: (backend/product\_normalizer.py) Processes raw product data. The `normalize_product()` function guarantees a consistent product shape. Pre-computes galaxy and spectrum IDs.
3.  **Catalog**: The normalized product data forms the product catalog.
4.  **Frontend**: The frontend retrieves the catalog via the `/api/conductor/catalog` endpoint and displays product information in the various views.

## Factory Agents

*   `steerer_agent.py`: Identifies critical gaps in the master plan and generates/updates specifications.
*   `scribe_agent.py`: Generates and maintains the application's documentation.
*   `spec_writer.py`: Translates human intent into detailed Markdown specifications.
*   `builder_agent.py`: Materializes code from specifications.

## Key Conventions

*   **Imports**: Uses `lucide-react` for icons.
*   **Product Data**: All product data originates from one of three authorized sources, per the `source_rules.py`.
*   **Tailwind**: Uses Tailwind CSS classes extensively (e.g., `bg-red-950/40`, `text-red-400`).
*   **Product Shape**: The frontend expects a flat, predictable product shape, matching the output of `product_normalizer.normalize_product()`.
