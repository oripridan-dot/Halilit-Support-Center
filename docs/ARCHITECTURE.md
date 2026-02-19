```markdown
## Overview

The Halilit Support Center is a web application designed to provide product information and support. It features a dashboard, inventory view, and product detail view, along with backend services for data fetching, JIT (Just-In-Time) intelligence, and a factory for automated code generation and documentation.

## Frontend Views

*   **DashboardView:**
    *   Route/State: `DASHBOARD`
    *   Renders: Dashboard statistics and metric cards. Uses `DashboardStats` interface.
*   **InventoryView:**
    *   Route/State: `INVENTORY`
    *   Renders: A list of products.
*   **ProductDetailView:**
    *   Route/State: `PRODUCT_DETAIL`
    *   Renders: Detailed product information with sourcing badges.

## Hooks & State

*   **`useConductorCatalog`:**
    *   Purpose: Fetches and provides product catalog data.
    *   Return Shape:  Product data.
*   **`useJITIntelligence`:**
    *   Purpose: Manages the JIT intelligence phases and data.
    *   Return Shape: Data related to JIT intelligence, including phases like "idle", "snap", "intel", "wisdom", "complete", or "error".
*   **`useDebounceValue`:**
    *   Purpose:  Debounces a value.
*   **`useNavigationStore`:**
    *   Purpose: Manages navigation state between views.
    *   Return Shape:  `currentView`, `activeProductId`, `searchQuery`, `initialCfpFilter`, and navigation functions (`goToDashboard`, `goToInventory`).

## Backend API

*   `/api/conductor/catalog`: (GET) Returns product catalog data.
*   (Other endpoints are not specified in the code snapshot.)

## Data Pipeline

1.  A scraper (not shown in the snapshot) fetches data.
2.  `product_normalizer.py` normalizes product data into a consistent format.
3.  The normalized data is used to build a catalog.
4.  The frontend fetches the catalog data via the `/api/conductor/catalog` endpoint.

## Factory Agents

*   `steerer_agent.py`: Identifies critical gaps in specifications and generates or updates specs.
*   `scribe_agent.py`: Generates and updates documentation based on the codebase.
*   `spec_writer.py`: Translates human intent into specifications.
*   `builder_agent.py`: Materializes code from specifications.

## Key Conventions

*   **Imports:** Uses `@tanstack/react-query` for data fetching, `lucide-react` for icons, and `zustand` for state management.
*   **Naming:** Follows standard React component and hook naming conventions.
*   **Tailwind Theme Tokens:** Uses Tailwind CSS with custom color palettes.  `accentColors` object maps accent names (e.g., "blue", "amber") to Tailwind classes.
*   **Source Rules:** Enforced by `backend/source_rules.py`.  All data must come from authorized sources.
```