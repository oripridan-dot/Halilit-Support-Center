## Overview

The Halilit Support Center application is a web-based dashboard for managing product information and performing real-time product intelligence. It features a dark-themed interface with data-forward displays, inventory management, and a product detail view. The application uses a FastAPI backend to serve data and an AI-powered JIT (Just-In-Time) Intelligence engine for real-time product research.

## Frontend Views

*   **DashboardView**: Renders the main dashboard, displaying key statistics. Accessed via the `DASHBOARD` view state.
*   **InventoryView**: Displays a searchable list of products. Accessed via the `INVENTORY` view state.
*   **ProductDetailView**: Displays detailed information for a specific product. Accessed via the `PRODUCT_DETAIL` view state and `activeProductId` state.

## Hooks & State

*   **`useDashboardStats`**: Fetches and returns dashboard statistics. Returns a `DashboardStats` object with properties like `total_products`, `calls_for_price`, and `last_ingestion_run`.
*   **`useConductorCatalog`**: Fetches product data from the backend. Returns product data and loading/error states. Returns `ConductorProduct[]`.
*   **`useDebounceValue`**: Debounces a value, preventing rapid updates.
*   **`useJITIntelligence`**: Manages the JIT (Just-In-Time) Intelligence process, returning data based on the current phase. Returns JIT phase and associated data, including `signal_chain` and `cheat_sheet`.
*   **`useNavigationStore`**: Manages the application's navigation state. Returns the `currentView`, `activeProductId`, `searchQuery`, `initialCfpFilter`, and navigation actions like `goToDashboard` and `goToProductDetail`.

## Backend API

*   `/api/dashboard/stats`: (GET) Returns `DashboardStats` data.
*   `/api/conductor/catalog`: (GET) Returns product catalog data.
*   `/api/jit/product/{product_id}`: (GET) Triggers and streams JIT Intelligence data for a given product ID.

## Data Pipeline

1.  **Scraping**: Not directly visible in this code snapshot.
2.  **Normalization**: The `product_normalizer.py` module processes scraped product data. Products are transformed into a canonical shape and indexed.
3.  **Catalog**: The normalized product data is built into a catalog.
4.  **Frontend**: The frontend fetches data from the `/api/conductor/catalog` and `/api/dashboard/stats` endpoints.

## Factory Agents

*   `builder_agent.py`: Materializes code from a specification.
*   `steerer_agent.py`: Identifies gaps in existing specifications and generates new or updated specifications.
*   `scribe_agent.py`: Generates and updates documentation.
*   `spec_writer.py`: Translates human intent into detailed Markdown specifications.

## Key Conventions

*   **Imports**: Uses `lucide-react` for icons, `@tanstack/react-query` for data fetching, and `zustand` for state management.
*   **Naming**: Uses PascalCase for React component names (e.g., `DashboardView`) and camelCase for variables (e.g., `searchQuery`).
*   **Tailwind**: Uses Tailwind CSS for styling (e.g., `bg-zinc-900`, `min-h-screen`, `p-4`).
*   **Source Rules**: Enforced by `backend/source_rules.py`, dictating that all data must come from authorized sources.
