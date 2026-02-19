```markdown
# Halilit Support Center — Architecture Overview

The Halilit Support Center is a web application designed to manage and display product information. It features a dashboard, an inventory view, and detailed product pages. The application retrieves data from a backend API, which processes and normalizes product information. The frontend is built with React and uses libraries like `react-query` and `zustand` for data fetching and state management. The backend is built with FastAPI.

## Frontend Views

*   **DashboardView**: Renders dashboard statistics and last ingestion run status. Uses `/` route or `DASHBOARD` state. Displays metric cards with product counts and ingestion status.
*   **InventoryView**: Displays a list of products. Accessible via `/inventory` route or `INVENTORY` state. Displays product information and can apply a "Call-for-Price" filter.
*   **ProductDetailView**: Displays detailed information for a single product, including an SKU and a copy button. Accessed via `PRODUCT_DETAIL` state.

## Hooks & State

*   **`useConductorCatalog`**: Fetches product data from `/api/conductor/catalog`.
*   **`useJITIntelligence`**: Manages the JIT (Just-In-Time) intelligence phases: `idle`, `snap`, `intel`, `wisdom`, `complete`, and `error`.
*   **`navigationStore`**:  Manages the application's navigation state, including the current view (`DASHBOARD`, `INVENTORY`, `PRODUCT_DETAIL`, `INGESTION_STATUS`), the active product ID, search query, and a flag for the "Call-for-Price" filter.

## Backend API

*   `/api/conductor/catalog`: Returns pre-built product catalog data.
*   `/`: Serves the static frontend assets.

## Data Pipeline

1.  **Scraping**: (Not directly visible in the provided code, but implied) Data is scraped from external sources.
2.  **Normalization**: The `product_normalizer.py` module processes scraped data into a consistent product shape.
3.  **Catalog**: The normalized products are built into a catalog.
4.  **Frontend**: The frontend uses `useConductorCatalog` to fetch the catalog data and renders it in various views.

## Factory Agents

*   **`steerer_agent.py`**: Reads the Master Plan and audits existing specs to identify gaps, then generates new or updated specifications.
*   **`scribe_agent.py`**: Reads the codebase and regenerates documentation.
*   **`spec_writer.py`**: Translates human intent into "Dark Factory" Markdown specifications.
*   **`builder_agent.py`**: Materializes code from a specification.

## Key Conventions

*   **Imports**:  No specific import restrictions are visible in the code samples.
*   **Naming**: No specific naming conventions are visible in the code samples.
*   **Tailwind Theme Tokens**: Uses Tailwind classes for styling (e.g., `bg-blue-100/10`, `text-blue-500`).
*   **Source Rules**:  Data MUST come from authorized sources.  No synthesis.
```