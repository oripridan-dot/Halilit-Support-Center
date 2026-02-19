```markdown
## Overview

The Halilit Support Center is a web application designed to provide product information and support. It features a dashboard, inventory view, and product detail view. The application uses a FastAPI backend to serve data and a React frontend for the user interface. The backend also includes a JIT (Just-In-Time) intelligence engine for live product research and a suite of "Dark Factory" agents for automated development and documentation.

## Frontend Views

*   **DashboardView**: Renders dashboard statistics, including total products, calls for price, top brands count, and the status of the last ingestion run. Uses the `DashboardStats` interface.
*   **InventoryView**: Renders a list of products.  Each product card displays information and indicates out-of-stock or unconfirmed items with visual cues. Uses the `Product` type and `formatPrice` function.
*   **ProductDetailView**: Renders detailed information for a single product, including an SKU and a copy button if the price is zero or null. Uses the `Product` type.
*   **Ingestion Status**: (Implied, from `navigationStore.ts`) Displays the status of data ingestion.

## Hooks & State

*   **useConductorCatalog**: Fetches and provides product catalog data from `/api/conductor/catalog`. The catalog includes a flat array of products and pre-computed indexes.  Returns an object matching the shape of the backend's catalog data.
*   **useJITIntelligence**: Manages the JIT intelligence phases, including `idle`, `snap`, `intel`, `wisdom`, `complete`, and `error`. Returns visual intel (signal_chain, cheat_sheet) for the cockpit UI.
*   **navigationStore**: A Zustand store that manages the application's navigation state, including the current view (`DASHBOARD`, `INVENTORY`, `PRODUCT_DETAIL`, `INGESTION_STATUS`), the active product ID, search query, and an initial call-for-price filter.

## Backend API

*   `/api/conductor/catalog`: (Implied, from `useConductorCatalog.ts`) Serves the product catalog data.
*   `/`: Serves the static frontend assets.
*   `/api/jit/{product_id}`: (Implied, from `backend/jit_agent.py`) Endpoint to trigger JIT intelligence for a given product ID.

## Data Pipeline

1.  **Scraper**: (Implied) Collects data from various sources (not shown in the code).
2.  **Product Normalizer**: Transforms scraped data into a consistent `Product` shape, pre-computing galaxy and spectrum IDs.
3.  **Catalog Build**: (Implied, from `backend/server.py`) Builds the product catalog from the normalized data.
4.  **Frontend**: Consumes the product catalog data via `useConductorCatalog` and displays it in the views.

## Factory Agents

*   **builder\_agent.py**: Materializes code from a specification.
*   **steerer\_agent.py**: Identifies gaps in product specifications and generates new or updated specifications.
*   **scribe\_agent.py**: Regenerates documentation based on the codebase.
*   **spec\_writer.py**: Translates plain text descriptions into Markdown specifications.

## Key Conventions

*   **Imports**:  React components and hooks, data types, and utility functions are imported from various files within the `frontend/src` directory.
*   **Product Type**: The `Product` type is defined in `frontend/src/types.ts` (not shown in the code).
*   **Tailwind Theme Tokens**: The code uses Tailwind CSS for styling, with custom colors such as `bg-bg-elevated`, `blue`, `amber`, `green`, `red`, and `zinc`.
*   **Source Rules**:  All data originates from authorized sources, as defined in `backend/source_rules.py`.  No data synthesis is permitted.
```