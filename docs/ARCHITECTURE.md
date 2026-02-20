## Overview

The Halilit Support Center is a web application designed to provide product information and support. It features a dashboard, inventory view, and product detail view, along with a backend API that serves product data and facilitates live product intelligence. The application uses a "Dark Factory" approach, with automated agents for code generation, documentation, and strategic planning.

## Frontend Views

*   **DashboardView:**
    *   Route/State: `DASHBOARD`
    *   Renders: Summary metrics (total products, calls for price, top brands, last ingestion run status) and metric cards.
*   **InventoryView:**
    *   Route/State: `INVENTORY`
    *   Renders: A list of products with filters and search functionality.
*   **ProductDetailView:**
    *   Route/State: `PRODUCT_DETAIL`
    *   Renders: Detailed product information, including sourcing badges and JIT badges.

## Hooks & State

*   **`useConductorCatalog`**:
    *   Purpose: Fetches and provides product catalog data.
    *   Return Shape: Undefined in the code snapshot.
*   **`useJITIntelligence`**:
    *   Purpose: Retrieves Just-In-Time (JIT) intelligence data for a product.
    *   Return Shape: `jitState` (containing product information)
*   **`useDebounceValue`**:
    *   Purpose: Debounces a value, likely used for the search input in `InventoryView`.
    *   Return Shape: Undefined in the code snapshot.
*   **`useNavigationStore`**:
    *   Purpose: Manages the application's navigation state.
    *   Return Shape:
        *   `currentView`: The current view type (`DASHBOARD`, `INVENTORY`, `PRODUCT_DETAIL`, `INGESTION_STATUS`).
        *   `activeProductId`: The ID of the currently active product.
        *   `searchQuery`: The current search query.
        *   `initialCfpFilter`:  Whether the Call-for-Price filter is active.
        *   `goToDashboard`: Function to navigate to the dashboard.
        *   `goToInventory`: Function to navigate to the inventory, with optional search query.
        *   `goToProduct`: Function to navigate to a product detail view.
        *   `goToIngestionStatus`: Function to navigate to the ingestion status.

## Backend API

*   `/api/conductor/catalog`: (GET) Returns product catalog data.

## Data Pipeline

1.  A scraper (not shown in the code snapshot) collects product data.
2.  The `product_normalizer.py` normalizes the data, creating a consistent product shape and pre-computing galaxy and spectrum IDs.
3.  The normalized data forms the product catalog, indexed for efficient searching and filtering.
4.  The frontend consumes the catalog data to render the views.

## Factory Agents

*   **`backend/factory/builder_agent.py`**: Materializes code from a specification.
*   **`backend/factory/steerer_agent.py`**: Identifies gaps in product specs and generates new or updated specifications.
*   **`backend/factory/scribe_agent.py`**: Generates and updates documentation based on the codebase.
*   **`backend/factory/spec_writer.py`**: Translates user intent into detailed Markdown specifications.

## Key Conventions

*   **Imports**: Uses `lucide-react` for icons and `@tanstack/react-query` for data fetching.
*   **Naming**: No specific naming conventions are explicitly defined in the provided code.
*   **Tailwind Theme Tokens**: Uses Tailwind CSS with custom colors defined in `MetricCard` component.
*   **Source Rules**: All data must come from one of three authorized sources, with no data synthesis allowed.
