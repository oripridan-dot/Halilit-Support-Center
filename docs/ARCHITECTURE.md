```markdown
# Halilit Support Center — Architecture Overview

This application provides a support center for Halilit products, featuring a dashboard, inventory management, and detailed product information. It leverages a FastAPI backend for data serving and a React frontend for the user interface, with real-time product intelligence powered by Gemini.

## Frontend Views

*   **DashboardView:** `/` Displays dashboard statistics and metrics. Renders `MetricCard` components.
*   **InventoryView:** `/inventory` Displays a list of products. Includes search functionality and filters.
*   **ProductDetailView:** (via `PRODUCT_DETAIL` navigation state). Displays detailed information about a single product, including sourcing and JIT (Just-In-Time) intelligence data.

## Hooks & State

*   `useConductorCatalog`: Fetches product catalog data from the backend. Returns `products`, `isLoading`, and `error`.
*   `useJITIntelligence`: Fetches and processes JIT intelligence for a specific product. Returns `jitState`.
*   `useDebounceValue`: (in `InventoryView`) Debounces a value.
*   `useNavigationStore`: Manages application navigation state. Returns `currentView`, `activeProductId`, `searchQuery`, `initialCfpFilter`, and navigation functions like `goToInventory`.

## Backend API

*   `GET /api/conductor/catalog`: Returns the product catalog data.
*   `/`: Serves static frontend assets.
*   `/docs`: Serves FastAPI documentation.

## Data Pipeline

1.  **Scraping:** (Not shown in code) Data is collected from various sources.
2.  **Normalization:** The `product_normalizer.py` module processes scraped data to produce a canonical product shape.
3.  **Catalog:** The normalized product data is built into a catalog.
4.  **Frontend:** The frontend consumes the catalog data to render the views.

## Factory Agents

*   `steerer_agent.py`: Identifies critical gaps in the system and generates new or updated specifications.
*   `scribe_agent.py`: Generates living documentation based on the codebase.
*   `spec_writer.py`: Translates human intent into specifications.
*   `builder_agent.py`: Materializes code from a specification.

## Key Conventions

*   **Imports:** Uses `lucide-react` for icons.
*   **Naming:**
    *   `MetricCardProps` defines the interface for metric cards in the dashboard.
    *   `StockBadgeProps` defines the interface for stock badges in the inventory view.
*   **Tailwind:** Uses Tailwind CSS for styling. Includes accent colors: `blue`, `amber`, `green`, `red`, and `zinc`.
*   **Source Rules:** Enforced by `source_rules.py`. All data must come from authorized sources; no synthesis is allowed.
```