```markdown
# Halilit Support Center — Application Architecture

## Overview

The Halilit Support Center is a web application designed to manage and display product information, including inventory, pricing, and detailed product specifications. It features a dashboard, inventory view, and product detail view, along with a real-time intelligence engine that provides insights into product data. The application uses a FastAPI backend to serve data and a React frontend for the user interface.  The system emphasizes data accuracy and relies on a strict set of source rules.

## Frontend Views

*   **DashboardView**: Renders dashboard metrics and a summary of product data.  Accessed via the `DASHBOARD` navigation state.
*   **InventoryView**: Displays a filterable and searchable grid of products.  Accessed via the `INVENTORY` navigation state. Accepts an optional `initialCfpFilter` prop to pre-filter for "Call for Price" products.
*   **ProductDetailView**: Shows detailed information for a specific product, including a copy-to-clipboard button for the product's SKU. Accessed via the `PRODUCT_DETAIL` navigation state.

## Hooks & State

*   `useConductorCatalog`: Fetches product data from `/api/conductor/catalog`.
*   `useJITIntelligence`: Manages the JIT (Just-In-Time) Intelligence phases and data for the cockpit UI. Returns: `JITPhase`.
*   `useNavigationStore`:  Manages the application's navigation state. Returns: `currentView`, `activeProductId`, `searchQuery`, `initialCfpFilter` and methods to change the view.
*   `useDebouncedValue`: Debounces a value, used in `InventoryView`.

## Backend API

*   `GET /api/conductor/catalog`: Returns pre-indexed product catalog data.

## Data Pipeline

1.  **Scraping:**  Not explicitly defined in the provided code, but implied as a source of product data.
2.  **Normalization:** The `product_normalizer.py` module processes scraped product data, ensuring a consistent and predictable data shape. It pre-computes galaxy and spectrum IDs and pre-computes search text.
3.  **Catalog:** The normalized product data is built into a catalog.
4.  **Frontend:** The frontend consumes data from the `/api/conductor/catalog` endpoint and displays product information.

## Factory Agents

*   `steerer_agent.py`: Identifies gaps in product specifications and generates new or updated specifications.
*   `scribe_agent.py`: Regenerates documentation to reflect the current state of the codebase.
*   `spec_writer.py`: Translates plain text descriptions into Markdown specifications.
*   `builder_agent.py`: Materializes code from a specification.

## Key Conventions

*   **Imports:**  Code imports are relative, e.g., `from backend import __version__`.
*   **Source Rules:** Data must originate from authorized sources.
```
