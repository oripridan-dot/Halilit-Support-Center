## Overview

The Halilit Support Center application provides a dashboard for product management, inventory browsing, and detailed product information. It features a dark, data-forward interface with a focus on real-time data and intelligence. The application uses a FastAPI backend to serve data and a React frontend built with TypeScript.

## Frontend Views

*   **DashboardView**: Renders the dashboard with key statistics and the status of the last data ingestion run. Uses `/api/dashboard/stats` to fetch data.
*   **InventoryView**: Displays a searchable list of products.  Accessible via the navigation store.
*   **ProductDetailView**: Shows detailed information for a selected product. Accessible via the navigation store, displaying the product based on `activeProductId`.

## Hooks & State

*   **useDashboardStats**: Fetches dashboard statistics from `/api/dashboard/stats`. Returns an object of type `DashboardStats`.
*   **useConductorCatalog**: Fetches product data, used by `InventoryView` and `ProductDetailView`.
*   **useJITIntelligence**: Manages the state of the JIT (Just-In-Time) intelligence process, providing real-time research and reasoning. Returns `JITIntelligenceState`.
*   **useDebounceThrottle**: Debounces input changes.
*   **NavigationStore**: (Zustand) Manages the application's view state, including:
    *   `currentView`: The current view type (`'DASHBOARD'`, `'INVENTORY'`, `'PRODUCT_DETAIL'`, `'INGESTION_STATUS'`, `'EXPLORER'`).
    *   `activeProductId`: The ID of the currently selected product.
    *   `searchQuery`: The current search query.
    *   `initialCfpFilter`:  Boolean indicating if the call-for-price filter should be applied.
    *   `goToDashboard`, `goToExplorer`, `goToInventory`, `goToProduct` functions.

## Backend API

*   `/api/dashboard/stats`: (GET) Returns dashboard statistics (type `DashboardStats`).

## Data Pipeline

1.  A scraper (not shown in the snapshot) gathers raw product data.
2.  The `product_normalizer.py` module normalizes the raw product data into a consistent format.
3.  The normalized data forms the product catalog.
4.  The frontend consumes the product catalog data.

## Factory Agents

*   **steerer_agent.py**: Identifies gaps in product specifications and generates new specs.
*   **scribe_agent.py**: Generates living documentation based on the codebase.
*   **spec_writer.py**: Translates plain text into detailed specifications.
*   **builder_agent.py**: Materializes code from specifications.

## Key Conventions

*   **Imports**: Uses absolute imports starting from `@/` (e.g., `@/components/ui/input`).
*   **Source Rules**:  The `source_rules.py` file defines the authorized data sources.
