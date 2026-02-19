# Spec: Product Detail - Image Sourcing

**Version:** 1.0
**Component:** `frontend/src/components/ProductImage.tsx`

## 1. Purpose

To clearly indicate the source of product images on the Product Detail View and in Product Tiles. This enhances data integrity and operator trust and aligns with the "Zero Broken Images" business goal by ensuring operators understand if the image is from the official scout or the JIT inferred scout.

## 2. Requirements

1.  **Image Source Badge:** A badge MUST be displayed on or near the product image (both in ProductDetailView and ProductTile) indicating its source.
2.  **Source Mapping:**
    *   If the image URL is from the `ConductorProduct.image_url` property (Official Scout), the badge MUST display "Official Scout".
    *   If the image URL is from the `JITState.snap.thumbnail` property (Inferred Scout from JIT), the badge MUST display "Inferred Scout".
3.  **Badge Styling:** The badge MUST be subtle and not distract from the image itself. Use a light background color and a dark text color for contrast and readability. Use Tailwind CSS to style visually distinct badges for each data source, for example:
    *   Official Scout: `bg-blue-100 text-blue-800 text-xs font-semibold mr-2 px-2.5 py-0.5 rounded dark:bg-blue-700 dark:text-blue-300`
    *   Inferred Scout: `bg-purple-100 text-purple-800 text-xs font-semibold mr-2 px-2.5 py-0.5 rounded dark:bg-purple-700 dark:text-purple-300`
4.  **Badge Absence:** If no image is displayed (fallback image is shown), the badge MUST NOT be displayed.
5.  **Placement:** The badge MUST be consistently placed in the same location relative to the image, such as the top-right or bottom-right corner. Ensure the placement does not obscure critical parts of the image.
6.  **Accessibility:** The badge MUST have an `aria-label` attribute that describes the source of the data for screen reader users. For example: `<span aria-label="Source: Official Scout">…</span>`
7. **Component Integration:** The `ProductImage` component must determine image source and display the corresponding badge.
8.  **Dynamic Update:** If the image source changes due to JIT data arrival, the badge MUST dynamically update to reflect the new source and use the associated styling (see "Spec: Product Detail - Dynamic JIT Badge Updates").

## 3. Behavior Scenarios

1.  **Scenario:** The Product Detail screen loads for a product with `image_url` from the catalog.
    *   **Outcome:** The product image is displayed with an "Official Scout" badge.
2.  **Scenario:** The Product Detail screen loads for a product, and later the JIT stream provides a `thumbnail` image.
    *   **Outcome:** The product image updates to the `thumbnail` from the JIT stream.
    *   **Outcome:** The badge updates to "Inferred Scout."
3.  **Scenario:** The Product Detail screen loads for a product, `image_url` is invalid, and the fallback image is displayed.
    *   **Outcome:** The fallback image is shown.
    *   **Outcome:** No badge is displayed.
4.  **Scenario:** An accessory is displayed in ProductDetailView with a valid image URL from catalog.
    *   **Outcome:** The product image is displayed with an "Official Scout" badge.
5.  **Scenario:** A product in InventoryView with a valid image URL from catalog.
    *   **Outcome:** The product image is displayed with an "Official Scout" badge.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
