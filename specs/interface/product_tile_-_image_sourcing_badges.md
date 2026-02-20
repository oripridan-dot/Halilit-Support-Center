# Spec: Product Tile - Image Sourcing Badges

**Version:** 1.0
**Component:** `frontend/src/components/ProductTile.tsx`

## 1. Purpose

To clearly indicate the source of product images within Product Tiles (e.g., in the Inventory View or Accessory Recommendations), enhancing data integrity and operator trust. This complements the "Product Detail - Image Sourcing" spec, extending the same sourcing clarity to Product Tiles. This feature supports the "Zero Broken Images" business goal by ensuring operators understand if the image is from the official scout or the JIT inferred scout.

## 2. Requirements

1.  **Image Source Badge:** A badge MUST be displayed on or near the product image in Product Tiles, indicating its source.
2.  **Source Mapping:**
    *   If the image URL is from the `ConductorProduct.image_url` property (Official Scout), the badge MUST display "Official Scout".
    *   If the image URL is from the `JITState.snap.thumbnail` property (Inferred Scout from JIT – only applies if JIT data is being consumed in the tile), the badge MUST display "Inferred Scout". If JIT data is not consumed in the tile, do NOT try to find JIT data.
3.  **Badge Styling:** The badge MUST be subtle and not distract from the image itself. Use a light background color and a dark text color for contrast and readability. Use Tailwind CSS to style visually distinct badges for each data source, for example:
    *   Official Scout: `bg-blue-100 text-blue-800 text-xs font-semibold mr-2 px-2.5 py-0.5 rounded dark:bg-blue-700 dark:text-blue-300`
    *   Inferred Scout: `bg-purple-100 text-purple-800 text-xs font-semibold mr-2 px-2.5 py-0.5 rounded dark:bg-purple-700 dark:text-purple-300`
4.  **Badge Absence:** If no image is displayed (fallback image is shown), the badge MUST NOT be displayed.
5.  **Placement:** The badge MUST be consistently placed in the same location relative to the image, such as the top-right or bottom-right corner. Ensure the placement does not obscure critical parts of the image. The badges MUST be displayed *above* the "OUT OF STOCK", or "UNCONFIRMED" badges if they are present.
6.  **Accessibility:** The badge MUST have an `aria-label` attribute that describes the source of the data for screen reader users. For example: `<span aria-label="Source: Official Scout">…</span>`
7.  **Data Availability:** The ProductTile must receive all required data (image URL and source information) from its parent component; it MUST NOT attempt to fetch this data itself.

## 3. Behavior Scenarios

1.  **Scenario:** A Product Tile is rendered with an `image_url` from the `ConductorProduct.image_url` property.
    *   **Outcome:** The Product Tile displays the image and an "Official Scout" badge.
2.  **Scenario:** A Product Tile is rendered with an `image_url` from the `JITState.snap.thumbnail` property.
    *   **Outcome:** The Product Tile displays the image and an "Inferred Scout" badge.
3.  **Scenario:** A Product Tile is rendered with a missing or invalid `image_url`.
    *   **Outcome:** The Product Tile displays the fallback placeholder image, and no sourcing badge is displayed.
4.  **Scenario:** A Product Tile is rendered with both stock is `0` and `image_url` from the `ConductorProduct.image_url` property.
    *   **Outcome:** The Product Tile displays a red border, and "OUT OF STOCK" badge. The "Official Scout" badge is rendered *above* the "OUT OF STOCK" badge.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
