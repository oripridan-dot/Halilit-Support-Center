```markdown
## Overview

The Halilit Support Center is a web application designed for managing product information and providing support. It features a dashboard, inventory view, and product detail view. The application uses a FastAPI backend to serve data, including a pre-built product catalog and real-time product intelligence. The backend also houses a "Dark Factory" with automated agents for code generation and documentation.

## Frontend Views

*   **DashboardView**:
    *   Route/State: `DASHBOARD` via `navigationStore`.
    *   Renders: Summary metrics, including total products, calls for price, top brands, and last ingestion run status.
*   **InventoryView**:
    *   Route/State: `INVENTORY` via `navigationStore`.
    *   Renders: A list of products from the `/api/conductor/catalog` endpoint, with stock badges.
*   **ProductDetailView**:
    *   Route/State: `PRODUCT_DETAIL` via `navigationStore`, accessed with a `productId` parameter.
    *   Renders: Details of a specific product, with tabs for different sections (e.g., "overview"). Includes an error message if `productId` is missing.

## Hooks & State

*   **`useConductorCatalog`**:
    *   Purpose: Fetches and provides access to product catalog data from `/api/conductor/catalog`.
    *   Return Shape: `products`, `isLoading`, `error`, `refetch`.
*   **`useJITIntelligence`**:
    *   Purpose: Manages the Just-In-Time (JIT) intelligence process for product information.
    *   Return Shape:  Not explicitly defined in the provided code, but manages the different JIT phases.
*   **`useNavigationStore`**:
    *   Purpose: Manages the application's navigation state.
    *   Return Shape: `currentView`, `activeProductId`, `searchQuery`, `initialCfpFilter`, `goToDashboard`, `goToInventory`, `goToProductDetail`, and `goToIngestionStatus` methods.
*   **`useDebounceValue`**:
    *   Purpose:  Debounces a value.
    *   Return Shape: Not defined, likely a debounced value.

## Backend API

*   `/`:
    *   Method: `GET`
    *   Returns: Serves the static frontend assets.
*   `/api/conductor/catalog`:
    *   Method: `GET`
    *   Returns: Product catalog data.
*   (Additional API endpoints might exist, but are not specified in the code.)

## Data Pipeline

1.  **Scraping:** (Not explicitly in this code snapshot) The backend fetches product data.
2.  **Normalization:** The `product_normalizer.py` module processes raw product data into a consistent, flat shape. This includes pre-computing `galaxy_id`, `spectrum_id`, and search text.
3.  **Catalog:** The normalized product data is built into a catalog.
4.  **Frontend:** The frontend fetches data from the `/api/conductor/catalog` endpoint and renders it in the inventory view and other components.

## Factory Agents

*   **`steerer_agent.py`**: Reads the Master Plan and identifies gaps, then generates new or updated specs.
*   **`scribe_agent.py`**: Reads the codebase and regenerates documentation.
*   **`spec_writer.py`**: Translates human intent into specifications.
*   **`builder_agent.py`**: Materializes code from a spec.

## Key Conventions

*   **Imports**: Uses `@tanstack/react-query` for data fetching, `react-router-dom` for routing, `zustand` for state management, and `lucide-react` for icons.
*   **Naming**: Uses PascalCase for React components (e.g., `DashboardView`) and camelCase for variables and functions (e.g., `goToDashboard`).
*   **Tailwind**: Uses Tailwind CSS for styling. Includes accent colors: `blue`, `amber`, `green`, `red`, `zinc`.
*   **Source Rules**: All data must come from one of three authorized sources (defined in `source_rules.py`).
```