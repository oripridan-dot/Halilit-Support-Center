```markdown
# Halilit Support Center — Architecture

## Overview

The Halilit Support Center is a web application designed to manage and display product information, inventory, and other relevant data for Halilit products. It features a dashboard, inventory view, and product detail view, with a backend API that fetches and processes data. The application uses a "Dark Factory" approach, employing AI agents to automate code generation and documentation.

## Frontend Views

*   **DashboardView**: Renders a dashboard with key metrics and status information.
    *   Component: `frontend/src/components/views/DashboardView.tsx`
    *   State: Accessed via `useNavigationStore`.
    *   Renders: Metric cards displaying product counts, calls for price, top brands, and ingestion run status.
*   **InventoryView**: Displays a list of products with inventory details.
    *   Component: `frontend/src/components/views/InventoryView.tsx`
    *   Route/State: Accessed via React Router and `useNavigationStore`.
    *   Renders: A paginated list of products, and uses a `StockBadge` component to display stock status.
*   **ProductDetailView**: Shows detailed information for a specific product.
    *   Component: `frontend/src/components/views/ProductDetailView.tsx`
    *   Route/State: Uses `productId` from URL parameters.
    *   Renders: Product details, and an `EcosystemTab` component.

## Hooks & State

*   **`useConductorCatalog`**: Fetches and provides product data.
    *   File: `frontend/src/hooks/useConductorCatalog.ts`
    *   Purpose: Retrieves product catalog data from the backend.
    *   Returns: `products`, `isLoading`, `error`, `refetch`.
*   **`useJITIntelligence`**: Manages JIT (Just-In-Time) intelligence data loading.
    *   File: `frontend/src/hooks/useJITIntelligence.ts`
    *   Purpose: Orchestrates the process of fetching and processing product information from various sources (inventory, product pages, brand pages, reviews).
    *   Returns: Not specified in code snapshot.
*   **`useNavigationStore`**: Manages application navigation state.
    *   File: `frontend/src/store/navigationStore.ts`
    *   Purpose: Controls the current view and stores navigation-related data.
    *   Returns: `currentView`, `activeProductId`, `searchQuery`, `initialCfpFilter`, `goToDashboard`, `goToInventory`.
*   **`useDebounceValue`**: Debounces a value.
    *   File: `frontend/src/hooks/useDebounceValue.ts`
    *   Purpose: Debounces a value.
    *   Returns: Not specified in code snapshot.

## Backend API

*   `/api/conductor/catalog`: Returns the product catalog data.
    *   Method: Not specified.
    *   Returns: Pre-built catalog data.

## Data Pipeline

1.  **Scraping**: Not present in the code snapshot, but implied as a data source.
2.  **Product Normalization**:
    *   File: `backend/product_normalizer.py`
    *   Purpose: Transforms scraped product data into a consistent, flat format.
3.  **Catalog Build**: Not specified in the code snapshot.
4.  **Frontend Consumption**: Frontend components fetch data from the API and display it.

## Factory Agents

*   **`backend/factory/builder_agent.py`**: Materializes code from a specification.
*   **`backend/factory/steerer_agent.py`**: Identifies critical gaps and generates new or updated specifications.
*   **`backend/factory/scribe_agent.py`**: Regenerates documentation based on the codebase.
*   **`backend/factory/spec_writer.py`**: Translates human intent into specifications.

## Key Conventions

*   **Imports**:  Uses `@tanstack/react-query` for data fetching, `react-router-dom` for navigation, and `lucide-react` for icons.
*   **Naming**:  Uses PascalCase for React components (e.g., `MetricCard`), and camelCase for variables (e.g., `activeTab`).
*   **Tailwind Theme Tokens**: Utilizes Tailwind CSS for styling, with custom color palettes (e.g., `blue`, `amber`, `green`).
*   **Source Rules**: Enforced by `backend/source_rules.py`.  All data must originate from authorized sources.
```