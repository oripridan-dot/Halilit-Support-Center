## Overview

The Halilit Support Center is a web application designed to manage and display product information. It features a dashboard, inventory view, and product detail view, with data sourced from a catalog and enriched by a JIT (Just-In-Time) intelligence engine. The application leverages React for the frontend, a FastAPI backend for API endpoints, and a data pipeline that processes product information. A "Dark Factory" provides automated code generation and documentation.

## Frontend Views

*   **DashboardView**: Renders key performance indicators (KPIs) and status information. Uses `/` or `DASHBOARD` state.
*   **InventoryView**: Displays a list of products with filtering and sorting capabilities. Uses `/inventory` or `INVENTORY` state.
*   **ProductDetailView**: Shows detailed information about a specific product, including sourcing and JIT intelligence data. Uses `/product/:productId` or `PRODUCT_DETAIL` state.

## Hooks & State

*   **useConductorCatalog**: Fetches and provides product catalog data. Returns a product catalog.
*   **useJITIntelligence**: Fetches and provides Just-In-Time intelligence data for a product. Returns `jitState` with data from different phases (`snap`, `intel`, `wisdom`, `complete`, `error`).
*   **useDebounceValue**: (In `InventoryView.tsx`) Debounces a value, likely for search input.
*   **NavigationStore**: (Zustand) Manages the application's navigation state, including the current view (`DASHBOARD`, `INVENTORY`, `PRODUCT_DETAIL`, `INGESTION_STATUS`), active product ID, search query, and a flag for the "Call-for-Price" filter.

## Backend API

*   `/api/conductor/catalog`: (GET) Returns product catalog data.
*   `/`: (GET) Serves the frontend application.
*   `/docs`: Serves the FastAPI documentation.
*   `/redoc`: Serves the FastAPI Redoc documentation.
*   `/version`: (GET) Returns the application version.
*   `/api/jit/{product_id}`: (GET) Streams Just-In-Time intelligence data.

## Data Pipeline

1.  A scraper (not shown in the code) collects product information.
2.  The `product_normalizer.py` module normalizes the product data into a consistent format.
3.  The normalized data is used to build a catalog.
4.  The frontend fetches the catalog data via the `/api/conductor/catalog` endpoint and displays the products.

## Factory Agents

*   **steerer_agent.py**: Identifies gaps in product specifications and generates new specifications.
*   **scribe_agent.py**: Generates living documentation based on the codebase.
*   **spec_writer.py**: Translates plain text descriptions into detailed specifications.
*   **builder_agent.py**: Materializes code from specifications.

## Key Conventions

*   **Imports**: Uses `lucide-react` for icons, `@tanstack/react-query` for data fetching, and `zustand` for state management.
*   **Naming**: Follows a consistent naming convention for components, hooks, and variables.
*   **Tailwind**: Uses Tailwind CSS for styling with accent colors: `blue`, `amber`, `green`, `red`, and `zinc`.
*   **Source Rules**: All data must originate from authorized sources. No data synthesis is allowed.
