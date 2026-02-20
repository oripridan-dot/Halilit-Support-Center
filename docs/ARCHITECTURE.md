## Overview

The Halilit Support Center is a web application designed as a data-forward console for managing product information and inventory. It features a dark, dense user interface inspired by Vercel and Linear, with a focus on providing power-user tools for product management and real-time intelligence.

## Frontend Views

*   **DashboardView**: `/` or `DASHBOARD` state. Displays key statistics about products, calls, brands, and ingestion status. Uses data fetched from `/api/dashboard/stats`.
*   **InventoryView**: `/inventory` or `INVENTORY` state. A dense data table for viewing and managing product inventory. Uses data fetched via `useConductorCatalog`.
*   **ProductDetailView**: `/product/:id` or `PRODUCT_DETAIL` state. Shows detailed information about a single product, including pricing, stock, and related information. Uses `useConductorCatalog` and `useProductRelationships`.

## Hooks & State

*   `useDashboardStats`: Fetches dashboard statistics from `/api/dashboard/stats`. Returns an object of type `DashboardStats`.
*   `useConductorCatalog`: Fetches product catalog data from `/api/conductor/catalog`. Returns an array of `ConductorProduct` (type not shown).
*   `useJITIntelligence`: Manages the JIT (Just-In-Time) intelligence process. Returns data of type `VerdictData`, `ReviewSource`, `FieldNotesData`, and `ExplorationPath`.
*   `useDebounceValue`: (From `InventoryView.tsx`) Debounces a value.
*   `navigationStore`: (`src/store/navigationStore.ts`) A `zustand` store managing the application's navigation state.
    *   `currentView`: `DASHBOARD`, `INVENTORY`, `PRODUCT_DETAIL`, `INGESTION_STATUS`, or `EXPLORER`.
    *   `activeProductId`: `string | null`.
    *   `searchQuery`: `string | null`.
    *   `initialCfpFilter`: `boolean | null`.

## Backend API

*   `/api/dashboard/stats` (GET): Returns dashboard statistics.
*   `/api/conductor/catalog` (GET): Returns product catalog data.
*   `/` (serves static frontend assets)
*   `/api/jit/product/{product_id}` (GET): Returns JIT intelligence data for a product.

## Data Pipeline

1.  A scraper (not shown in the code) collects product data.
2.  `product_normalizer.py` normalizes product data into a consistent format.
3.  The normalized data is used to build a catalog.
4.  The frontend fetches data from the `/api/conductor/catalog` endpoint and `/api/dashboard/stats`.

## Factory Agents

*   `steerer_agent.py`: Identifies critical gaps in the product specs and generates/updates them.
*   `scribe_agent.py`: Regenerates documentation to reflect the current codebase.
*   `spec_writer.py`: Translates human intent into detailed Markdown specifications.
*   `builder_agent.py`: Materializes code from a specification.

## Key Conventions

*   **Imports**: Uses `lucide-react` for icons.
*   **Naming**: Uses `PascalCase` for React components.
*   **Tailwind**: Uses Tailwind CSS classes extensively.
*   **Source Rules**: Enforced by `backend/source_rules.py`.  Data must come from authorized sources, with no data synthesis.
