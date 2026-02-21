## Overview

This application is a data-driven dashboard and inventory management system for product information, likely for a retail or e-commerce context. It provides views for a dashboard, inventory, and product detail, supported by backend APIs and data processing pipelines. The system emphasizes real-time product intelligence, leveraging AI for live product research. The codebase features a "Dark Factory" for automated code generation, documentation, and strategic planning.

## Frontend Views

*   **DashboardView**: Renders a dense, data-forward dark console. Uses `/api/dashboard/stats` to display stats.
*   **InventoryView**: Displays a paginated list of products.  Uses `useConductorCatalog` hook for data and `useNavigationStore` for search and navigation.
*   **ProductDetailView**: Shows detailed information for a selected product. Uses `useConductorCatalog` and `useNavigationStore` to fetch and display product data.

## Hooks & State

*   **useConductorCatalog**: Fetches product catalog data from `/api/conductor/catalog`. Returns `products`, `totalItems`, `totalPages`, `isLoading`, `isError`, `handleRetry`, and `retryCount`.
*   **useDebounceThrottle**: Debounces input events.
*   **useJITIntelligence**: Manages the Just-In-Time intelligence process. Returns `phase`, `statusMessage`, `snap`, `officialSpecs`, and `visualIntel`.
*   **useNavigationStore**: Manages application-wide navigation state.  Stores `currentView`, `activeProductId`, `searchQuery`, and `initialCfpFilter`. Provides functions to `goToDashboard`, `goToExplorer`, and `goToProduct`, and methods to set the search query.

## Backend API

*   `/api/dashboard/stats` (GET): Returns dashboard statistics as `DashboardStats`.
*   `/api/conductor/catalog` (GET): Returns paginated product catalog data as `PaginatedCatalogResponse`.
*   `/api/jit/product/{product_id}` (GET): Returns product intelligence data, likely as SSE events.

## Data Pipeline

1.  **Scraping**: The system uses scrapers to collect product data.
2.  **Normalization**: The `product_normalizer.py` module processes and standardizes the scraped data. The output is a clean, flat product shape.
3.  **Catalog**: The normalized product data is used to build a product catalog.
4.  **Frontend**: The frontend consumes product data from the catalog via the `/api/conductor/catalog` endpoint.  The `useConductorCatalog` hook handles data fetching.

## Factory Agents

*   **steerer\_agent.py**: Identifies gaps in the product specs and generates or updates them.
*   **scribe\_agent.py**: Generates and updates documentation based on the codebase.
*   **spec\_writer.py**: Translates plain text descriptions into detailed specifications.
*   **builder\_agent.py**: Materializes code from specifications.

## Key Conventions

*   **Imports**: The code uses `lucide-react` for icons and `@tanstack/react-query` for data fetching.
*   **Naming**: No specific naming conventions are explicitly mentioned in the provided code.
*   **Source Rules**: All data must originate from one of three authorized sources, with no data synthesis allowed. The `source_rules.py` file contains the complete rules.
