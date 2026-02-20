```markdown
## Overview

The Halilit Support Center application is a web-based platform designed for product information and support. It features a dashboard, inventory, and product detail views, with real-time data integration and a focus on providing accurate and up-to-date product information. The application leverages a backend API to serve data, powered by a data pipeline that includes scraping, normalization, and catalog generation. A "Dark Factory" is used to generate and maintain code.

## Frontend Views

*   **DashboardView:** Renders a mission control view with product statistics and ingestion status. Uses the `/api/dashboard/stats` endpoint.
*   **InventoryView:** Displays a list of inventory items. Allows filtering based on a search query.
*   **ProductDetailView:** Shows detailed information for a specific product, including images, an ecosystem tab, and a JIT badge.

## Hooks & State

*   **useConductorCatalog:** Fetches and manages product catalog data from the `/api/catalog` endpoint. Returns data, loading state, error, and a refetch function.
*   **useJITIntelligence:** Retrieves real-time product intelligence data. Returns JIT product data.
*   **useNavigationStore:** Manages application navigation state, including the current view, active product ID, search query, and a flag for the call-for-price filter. Returns state and methods for navigation.
*   **useDebounceThrottle:**  Debounces and throttles a function call.

## Backend API

*   **`/api/dashboard/stats` (GET):** Returns dashboard statistics (total products, calls for price, top brands count, last ingestion run details).
*   **`/api/catalog` (GET):**  Endpoint for the product catalog.
*   **`/` (GET):** Serves static frontend assets.
*   **`/api/jit/product/{product_id}` (GET):** JIT Intelligence endpoint (streams live product research via Gemini).

## Data Pipeline

1.  **Scraper:** (Not directly visible in the provided code, but implied) Extracts product data from external sources.
2.  **Product Normalizer:** Processes and standardizes the scraped data to create a consistent product shape.
3.  **Catalog:** Stores and serves the normalized product data.
4.  **Frontend:** Displays the product data in the various views.

## Factory Agents

*   **backend/factory/builder_agent.py:** Materializes code from a specification.
*   **backend/factory/steerer_agent.py:** Identifies critical gaps in existing specs and generates new or updated specifications.
*   **backend/factory/scribe_agent.py:** Regenerates documentation to reflect the current state of the application.
*   **backend/factory/spec_writer.py:** Translates human intent into "Dark Factory" Markdown specifications.

## Key Conventions

*   **Imports:** Uses absolute imports (e.g., `@/components/common/ImageWithFallback`).
*   **Source Rules:** Enforced by `backend/source_rules.py`.  All data must come from one of three authorized sources.
*   **Tailwind:** (Implied, not explicitly shown)
```