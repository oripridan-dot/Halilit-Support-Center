```markdown
## Overview

The Halilit Support Center is a web application for managing and viewing product information. It features a dashboard, inventory, and product detail views. The application utilizes a backend API to serve product data and leverages AI agents for product intelligence and automated code generation.

## Frontend Views

*   **DashboardView**:
    *   **Route/State**: `DASHBOARD` in `navigationStore`.
    *   **Renders**: Dashboard statistics, including total products, calls for price, top brands, and last ingestion run status. Uses the `DashboardStats` interface.
*   **InventoryView**:
    *   **Route/State**: `INVENTORY` in `navigationStore`.
    *   **Renders**: A grid of product cards, displaying product information. Highlights out-of-stock and unconfirmed products with visual cues.
*   **ProductDetailView**:
    *   **Route/State**: `PRODUCT_DETAIL` in `navigationStore`.
    *   **Renders**: Detailed information for a single product, including a SKU and a copy button.

## Hooks & State

*   **`useConductorCatalog`**: Fetches and provides access to product catalog data from `/api/conductor/catalog`. The hook returns data shaped by the `Product` type.
*   **`useJITIntelligence`**: Manages the JIT (Just-In-Time) Intelligence phases, providing data for the cockpit UI. Returns a `JITPhase` and related data.
*   **`navigationStore`**:
    *   **Purpose**: Manages navigation state between views.
    *   **State**: `currentView` (`DASHBOARD`, `INVENTORY`, `PRODUCT_DETAIL`, `INGESTION_STATUS`), `activeProductId`, `searchQuery`, and `initialCfpFilter`.
*   **`copyStatus` (ProductDetailView)**: Manages the state of the copy button.  Can be `'idle'`, `'success'`, or `'error'`.

## Backend API

*   `/api/conductor/catalog`: Returns pre-built product catalog data.

## Data Pipeline

1.  **Scraper**: Not directly visible in the code, but implied as the source of product data.
2.  **Product Normalizer**: Transforms raw product data into a standardized format, as defined by the `Product` type.
3.  **Catalog**: The normalized product data is stored in a catalog.
4.  **Frontend**: The frontend consumes the catalog data to display product information in various views.

## Factory Agents

*   **`steerer_agent.py`**: Identifies critical gaps in specifications and generates new or updated specs.
*   **`scribe_agent.py`**: Generates and maintains documentation (e.g., this document) based on the codebase.
*   **`spec_writer.py`**: Translates plain text descriptions into detailed Markdown specifications.
*   **`builder_agent.py`**: Materializes code from specifications.

## Key Conventions

*   **Imports**: Uses named imports for React components (`lucide-react`).
*   **Product Type**: The `Product` type is used throughout the application.
*   **Tailwind**: Uses Tailwind CSS for styling (e.g., `bg-blue-100/10`, `text-blue-500`).
*   **Source Rules**: Enforced by `backend/source_rules.py`.  All data must come from authorized sources.
