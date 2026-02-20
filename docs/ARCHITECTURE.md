## Overview

The Halilit Support Center application is a data-driven dashboard for managing product information. It provides views for product inventory, detailed product information, and a dashboard for monitoring key metrics. The application uses a FastAPI backend to serve data and a React frontend built with TypeScript. The backend includes agents for data processing, specification generation, and living documentation, supporting a "Dark Factory" development approach.

## Frontend Views

*   **DashboardView**: `/` (via `DASHBOARD` in `navigationStore`), displays dashboard statistics, including total products, calls for price, top brands count, and last ingestion run status. Uses `useDashboardStats` hook.
*   **InventoryView**: `/inventory` (via `INVENTORY` in `navigationStore`), displays a data table of product inventory. Uses `useConductorCatalog` hook.
*   **ProductDetailView**: Dynamically routed via `PRODUCT_DETAIL` in `navigationStore`, displays detailed information about a specific product. Uses `useConductorCatalog` and `useJITIntelligence` hooks.
*   **Ingestion Status View**: `/ingestion` (via `INGESTION_STATUS` in `navigationStore`). Not explicitly rendered in the provided code, but referenced by the `navigationStore`.
*   **Explorer View**: `/explorer` (via `EXPLORER` in `navigationStore`). Not explicitly rendered in the provided code, but referenced by the `navigationStore`.

## Hooks & State

*   `useDashboardStats`: Fetches dashboard statistics from `/api/dashboard/stats`. Returns an object of type `DashboardStats`.
*   `useConductorCatalog`: Fetches product catalog data from `/api/conductor/catalog`. Returns `ConductorProduct` data.
*   `useJITIntelligence`: Manages the JIT (Just-In-Time) intelligence pipeline for product data. Returns data related to product intelligence.  Uses the `JITPhase` type for status.
*   `useDebounceValue`: Debounces a value.
*   `navigationStore`: (`src/store/navigationStore.ts`) Manages the application's navigation state.
    *   `currentView`: `ViewType` (DASHBOARD, INVENTORY, PRODUCT\_DETAIL, INGESTION\_STATUS, EXPLORER).
    *   `activeProductId`: `string | null`.
    *   `searchQuery`: `string | null`.
    *   `initialCfpFilter`: `boolean | null`.

## Backend API

*   `/api/dashboard/stats`: (GET) Returns dashboard statistics (e.g. `total_products`, `calls_for_price`).
*   `/api/conductor/catalog`: (GET) Returns the product catalog data.
*   `/`: Serves static frontend assets.

## Data Pipeline

1.  A scraper (not shown in the snapshot) fetches product data.
2.  The `product_normalizer.py` normalizes the raw data into a consistent format, producing a flat product shape and pre-computing indices.
3.  The normalized data is used to build the catalog.
4.  The frontend fetches the catalog data via the `/api/conductor/catalog` endpoint.

## Factory Agents

*   `steerer_agent.py`: Identifies critical gaps in product specifications and generates new or updated specs.
*   `scribe_agent.py`: Generates and updates documentation based on the codebase.
*   `spec_writer.py`: Translates plain text descriptions into detailed Markdown specifications.
*   `builder_agent.py`: Materializes code from specifications.

## Key Conventions

*   **Imports**: Uses `lucide-react` for icons, `@tanstack/react-query` for data fetching, and `zustand` for state management.
*   **Product Data**:  The `ConductorProduct` type is the canonical product shape.
*   **Source Rules**: All data must come from one of three authorized sources.
