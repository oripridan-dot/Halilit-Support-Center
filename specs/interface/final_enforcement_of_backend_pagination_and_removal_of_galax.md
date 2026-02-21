# Spec: Implement Backend Pagination for useConductorCatalog (Final + Skeleton Loading)
**Version:** 7.3
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the critical issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API and uses skeleton loading. This specification adds a catch to ensure old versions of the app break gracefully. This version adds logging so that there are no silent errors.

## Requirements

1.  **Total `galaxy_db.json` Removal:** Physically DELETE the `frontend/public/data/galaxy_db.json` file.
2.  **`useConductorCatalog` Dependency Isolation:** Ensure the `useConductorCatalog` hook *solely* relies on the `/api/conductor/catalog` endpoint for data. It must NOT attempt to import or read `galaxy_db.json` under any circumstances.
3.  **Backend Pagination Endpoint:** Verify that the `/api/conductor/catalog` endpoint correctly accepts `page`, `pageSize`, `searchQuery`, `sortBy`, `category`, and `brand` query parameters and returns a paginated subset of the catalog data, along with metadata about the total number of items and pages. The backend should default `pageSize` to 25 if not specified, and if `page` is not specified, it should default to 1. If sorting parameters are being passed, preserve them.
4.  **Data Contract Validation:** Ensure the data contract for `/api/conductor/catalog` includes pagination metadata:

    ```typescript
    interface PaginatedCatalogResponse {
      products: ConductorProduct[];
      totalItems: number;
      totalPages: number;
      currentPage: number;
      pageSize: number;
    }
    ```

5.  **`useConductorCatalog` Hook Implementation:** Ensure the `useConductorCatalog` hook:
    *   Accepts optional `page`, `pageSize`, `searchQuery`, `sortBy`, `category`, and `brand` parameters with default values of `1`, `25`, `''`, `''`, `''`, and `''` respectively.
    *   Fetches data from the paginated `/api/conductor/catalog` endpoint using the provided parameters.
    *   Returns the `products` array, `totalItems`, `totalPages`, `currentPage`, and `pageSize` from the API response.
    *   Uses `react-query` to manage the fetching and caching of paginated data.
    *   Implements skeleton components for loading states in parent components using the hook, displaying the skeleton until data is loaded.
6. **Skeleton visibility:** Ensure that skeleton components are displayed while the data is loading, enhancing the user experience with visual feedback.
7.  **Galaxy DB Check:**
    * Inside the `useConductorCatalog` hook, before any fetch occurs, insert a conditional check:
    ```typescript
      if (process.env.NODE_ENV !== 'production') {
          try {
              const galaxyDb = await import('../../public/data/galaxy_db.json');
              console.warn("Legacy galaxy_db.json is present. This should not happen in production.");
          } catch (e) {
              // File does not exist, which is the desired state.
              console.log("galaxy_db.json not found, as expected.");
          }
      }
    ```

## Stitch UI Prompt
```text
// Target Component: useConductorCatalog hook implementation
// Description: This prompt focuses on creating the skeleton loading states

// The component using useConductorCatalog should have a main container with:
// Layout: Flexbox, direction column
// Style: dark mode, slate-900 background

// Before catalog data is loaded, show the following skeleton placeholders:

// 1. Search Input Skeleton:
// Layout: Same size as the actual search input
// Style: rounded corners, bg-zinc-700, h-10

// 2. Inventory Grid Skeleton: (Use Bento Grid)
// Use shimmer animation for the loading state: bg-gradient-to-r from-zinc-700 via-zinc-600 to-zinc-700 animate-shimmer

// Should implement proper tailwind dark mode
// Should implement proper skeleton loading indicators

```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- Verify that `frontend/public/data/galaxy_db.json` is physically DELETED.
- Verify that components using `useConductorCatalog` display skeleton loading while fetching data.
- Verify that the `useConductorCatalog` hook correctly fetches data from the `/api/conductor/catalog` endpoint with pagination parameters.
- Verify that the pagination parameters are being applied to filter, sort, and search.
- In a non-production environment, confirm that the absence/presence of galaxy_db.json generates expected log messages.
