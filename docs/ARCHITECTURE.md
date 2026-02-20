```markdown
## Overview

The Halilit Support Center is a web application designed for product information and support. It provides a dashboard, inventory, and product detail views, leveraging data fetched from a backend API and enriched by a JIT (Just-In-Time) Intelligence engine. The application utilizes a "Dark Factory" approach for code generation and maintenance, with specialized agents to handle various tasks such as documentation, specification writing, and code building.

## Frontend Views

*   **DashboardView**:
    *   Route/State: `DASHBOARD` (via `navigationStore`)
    *   Renders: Dashboard statistics and metric cards. Fetches data using `useQuery` from `@tanstack/react-query`.
*   **InventoryView**:
    *   Route/State: `INVENTORY` (via `navigationStore`)
    *   Renders: A list of products.  Uses `useConductorCatalog` hook to fetch product data.
*   **ProductDetailView**:
    *   Route/State: `PRODUCT_DETAIL` (via `navigationStore`)
    *   Renders: Detailed information about a specific product.  Uses `useConductorCatalog` and `useJITIntelligence` hooks.

## Hooks & State

*   `useConductorCatalog`:
    *   Purpose: Fetches and provides product catalog data from `/api/conductor/catalog`.
    *   Returns: `products`, `isLoading`, `error`, `refetch`.  Also used to fetch a single product by `productId`.
*   `useJITIntelligence`:
    *   Purpose: Retrieves real-time product intelligence.
    *   Returns: `jitState`.
*   `useDebounceValue`:
    *   Purpose: Debounces a value. (Implementation not shown in snapshot)
*   `useNavigationStore`:
    *   Purpose: Manages the application's navigation state.
    *   Returns: `currentView`, `activeProductId`, `searchQuery`, `initialCfpFilter`, `goToDashboard`, `goToInventory`.

## Backend API

*   `/api/conductor/catalog`:
    *   Method: Not specified in the code snapshot, but presumably `GET`.
    *   Returns: Product catalog data.

## Data Pipeline

1.  **Scraper**: (Not shown in the code snapshot) Scrapes data from external sources.
2.  **Normalizer**: (`backend/product_normalizer.py`) Normalizes product data into a consistent format.  Pre-computes `galaxy_id` and `spectrum_id`.
3.  **Catalog**: The normalized product data is used to build a catalog.
4.  **Frontend**: The frontend fetches data from `/api/conductor/catalog`.

## Factory Agents

*   `backend/factory/builder_agent.py`: Materializes code from specifications.
*   `backend/factory/steerer_agent.py`: Identifies gaps in existing specs and generates new or updated specifications.
*   `backend/factory/scribe_agent.py`: Regenerates documentation to reflect the current codebase.
*   `backend/factory/spec_writer.py`: Translates human intent into detailed Markdown specifications.

## Key Conventions

*   **Imports**: Uses `lucide-react` for icons, `@tanstack/react-query` for data fetching, and `zustand` for state management.
*   **Product Shape**: Canonical product shape defined in `useConductorCatalog.ts`.
*   **Source Rules**: Enforced by `backend/source_rules.py`. Every piece of data MUST come from authorized sources.
```