# Spec: Enforce Backend Pagination and Remove GalaxyDB (Final + Research Animation + Graceful Error Handling + Polished Animation)
**Version:** 3.8
**Component:** `frontend/src/hooks/useConductorCatalog.ts`

## Purpose

Completely remove the `galaxy_db.json` dependency and enforce that the `useConductorCatalog` hook exclusively uses the backend API for fetching product catalog data in paginated form, addressing the critical issue of exceeding the 5MB client-side JSON limit and preventing future accidental reliance on the local file. This ensures that all filter and sort states are passed to the API, includes image validation with fallback, handles loading states correctly, refactors the use of `ImageWithFallback`, displays an animated magnifying glass during data fetching, adds graceful error handling, showing a retry banner if the API fails, improves the research animation, and polishes the animation's timing for a smoother user experience.

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
    *   Returns the `products` array, `totalItems`, `totalPages`, `currentPage`, `pageSize`, `isLoading`, and `error` from the API response.
    *   Uses `react-query` to manage the fetching and caching of paginated data.
6.  **Filtering and Sorting Parameters:** The `useConductorCatalog` hook MUST pass the filter and sort state as parameters to the API endpoint.
7.  **Error Handling:** Maintain existing error handling for API requests, displaying error messages to the user if the data cannot be fetched. Render a "retry" banner on API failure.
8.  **Image Fallback:** Refactor the usage of the `ImageWithFallback` component to ensure a consistent image loading experience.
9.  **Research Animation:** Display an animated magnifying glass icon (research animation) while data is being fetched (`isLoading` is true). Use framer-motion for the animation, ensuring it integrates seamlessly with the dark theme. This animation should be subtle and visually appealing.
10. **Graceful Error Handling:** Display a user-friendly error message and a "Retry" button if the API request fails. Implement exponential backoff for retries.
11. **Polished Animation Timing:** Adjust the animation timing of the magnifying glass animation to create a smoother and more natural effect. Experiment with different easing functions and durations to achieve the desired look and feel.
12. **Retry Button:** Provide a "Retry" button to allow the user to manually trigger a refetch of the catalog data. The "Retry" button should be visually prominent and easy to find.

## Stitch UI Prompt

```text
// Target Component: useConductorCatalog hook usage + retry banner and research animation
// Description: Integrate a retry banner for graceful error handling and an animated magnifying glass during data fetching into the InventoryView.

// Retry Banner:
//   Layout: Absolute position at the top of the InventoryView, full width.
//   Style: Tailwind CSS, dark theme. Background: slate-800. Text: white. Display: "Stats unavailable — [error message]" with a [Retry] button.
//   Placement: Render only when error is not null. The error message should be concise and user-friendly.
//   Retry Button: Tailwind CSS, blue-500 hover effect. On click, call refetch() to retry fetching data.

// Research Animation:
//   Icon: Magnifying glass icon from lucide-react.
//   Animation: framer-motion. Rotate the icon continuously while isLoading is true.
//   Style: Tailwind CSS, blue-500 color.
//   Placement: Display the icon in the center of the InventoryView container while isLoading is true.
//   Fine tune the transition properties for a smoother look.

// ImageWithFallback:
//   Ensure the ImageWithFallback component correctly handles image loading errors by using the "/placeholder.png" image in place of broken links. It MUST have lazy loading enabled.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
