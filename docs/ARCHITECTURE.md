```markdown
## Overview

The Halilit Support Center is a web application designed for managing product information and providing insights. It features a dashboard, inventory view, and product detail view. The application uses a backend API to fetch and process data, including a JIT (Just-In-Time) intelligence engine for real-time product research. The backend also includes a "Dark Factory" with automated agents for code generation and documentation.

## Frontend Views

*   **DashboardView**: Renders a dashboard with summary statistics and metric cards. Uses the `/` route via the `DASHBOARD` view state.
*   **InventoryView**: Displays a list of products. Accessible via the `/inventory` route (or the `INVENTORY` view state) and includes search and filtering.
*   **ProductDetailView**: Shows detailed information for a specific product, accessed via the `PRODUCT_DETAIL` view state. Requires a `productId` parameter in the route.

## Hooks & State

*   **`useConductorCatalog`**: Fetches product data from the `/api/conductor/catalog` endpoint and provides access to products, loading state, and potential errors.
*   **`useJITIntelligence`**: Manages the JIT intelligence workflow, providing phases such as `snap`, `intel`, `wisdom`, and `complete`.
*   **`useNavigationStore`**: Manages the application's navigation state, including the current view, active product ID, search query, and a flag for pre-applying the "Call-for-Price" filter.
*   **`useDebounceValue`**: Debounces a value, likely used for filtering in the `InventoryView`.

## Backend API

*   `/api/conductor/catalog` (GET): Returns product catalog data.
*   `/` (GET): Serves the frontend application.
*   `/docs` (GET): Serves FastAPI's auto-generated API documentation.

## Data Pipeline

1.  **Scraping:** Not directly present in the provided code, but implied as the initial source of product data.
2.  **Product Normalization:** The `backend/product_normalizer.py` module processes and normalizes the scraped product data.  It ensures a consistent product shape.
3.  **Catalog Build:** The `build_catalog` function (from `backend/product_normalizer.py`) builds the product catalog.
4.  **Frontend Consumption:** The frontend fetches and displays the processed product data.

## Factory Agents

*   **`steerer_agent.py`**: Identifies gaps in product specifications and generates new or updated specs.
*   **`scribe_agent.py`**: Generates and updates documentation (like this document) based on the codebase.
*   **`spec_writer.py`**: Translates plain text descriptions into detailed specifications.
*   **`builder_agent.py`**: Materializes code from specifications.

## Key Conventions

*   **Imports:**  Code uses `lucide-react` for icons and `react-query` for data fetching.  `zustand` is used for state management.
*   **Naming:**  Components are PascalCase (e.g., `MetricCard`), and hooks are `use...` (e.g., `useConductorCatalog`).
*   **Tailwind:** Uses Tailwind CSS for styling, with color accents like `blue`, `amber`, `green`, `red`, and `zinc`.
*   **Source Rules:** Enforced by `backend/source_rules.py`. Every data point must come from an approved source, and no data synthesis is allowed.
```