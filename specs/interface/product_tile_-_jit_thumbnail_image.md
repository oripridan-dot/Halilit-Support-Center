# Spec: Product Tile - JIT Thumbnail Image

**Version:** 1.0
**Component:** `frontend/src/components/ProductTile.tsx`

## 1. Purpose

To display JIT-generated thumbnails in Product Tiles when available, providing up-to-date and potentially enhanced product imagery. This leverages JIT intelligence to improve the visual appeal of product listings and supports the "Zero Broken Images" business goal by ensuring that even if the primary image source is unavailable, a JIT-generated thumbnail can be displayed. This also contributes to increased attachment rate, because better images on tiles grab the operator's attention.

## 2. Requirements

1.  **JIT Data Integration:** The Product Tile MUST consume JIT data (if available) for the corresponding product, accessed via the `useJITIntelligence` hook. The `productId` will be passed into the tile.
2.  **Thumbnail Source Priority:** If the JIT stream (`useJITIntelligence`) provides a `thumbnail` URL and `JITState.status === 'complete'`, the Product Tile MUST use this URL as the primary image source, **overriding** the `ConductorProduct.image_url`.
3.  **`JITState.status !== complete` Thumbnail Handling:** If `JITState.status` is NOT `complete`, the Product Tile MUST use the `ConductorProduct.image_url` as the primary image source.
4.  **Fallback to Conductor Image:** If no JIT data is available (`jit === null` or `jit.status !== 'complete'`), the Product Tile MUST use the `ConductorProduct.image_url` as the primary image source.
5.  **Fallback Image:** If both the JIT `thumbnail` and the `ConductorProduct.image_url` are unavailable or fail to load, the Product Tile MUST display a dark placeholder image (`/placeholder.png` or an inline SVG), consistent with the existing image fallback logic.
6.  **onError Handler:** The `<img>` tag MUST have an `onError` handler that sets the image source to `/placeholder.png` if the JIT thumbnail or Conductor image fails to load.
7.  **Alt Text:** The `<img>` tag MUST include an `alt` attribute that describes the image (e.g., the product name), even when the placeholder image is displayed. The alt text should use the product name from `ConductorProduct`.
8.  **No Additional API Calls:** This feature MUST NOT introduce any new API calls or data fetching logic within the Product Tile. It should rely solely on the JIT data stream and the existing `ConductorProduct` data.
9.  **Performance Optimization:** Implement memoization or other performance optimization techniques to prevent unnecessary re-renders of the Product Tile when the JIT data stream updates frequently.

## 3. Behavior Scenarios

1.  **Scenario:** A product has a valid `ConductorProduct.image_url` and a valid JIT `thumbnail` URL with `JITState.status === 'complete'`.
    *   **Outcome:** The Product Tile displays the JIT thumbnail image.
2.  **Scenario:** A product has a valid `ConductorProduct.image_url` and a valid JIT `thumbnail` URL with `JITState.status !== 'complete'`.
    *   **Outcome:** The Product Tile displays the `ConductorProduct.image_url` image.
3.  **Scenario:** A product has a valid JIT `thumbnail` URL with `JITState.status === 'complete'` but the `ConductorProduct.image_url` is missing or invalid.
    *   **Outcome:** The Product Tile displays the JIT thumbnail image.
4.  **Scenario:** A product has a valid JIT `thumbnail` URL with `JITState.status !== 'complete'` and the `ConductorProduct.image_url` is missing or invalid.
    *   **Outcome:** The Product Tile displays the fallback image (`/placeholder.png`).
5.  **Scenario:** A product has neither a valid JIT `thumbnail` (with `JITState.status === 'complete'`) nor a valid `ConductorProduct.image_url`.
    *   **Outcome:** The Product Tile displays the fallback image (`/placeholder.png`).
6.  **Scenario:** A product has a JIT error (JITState.status === 'error').
    *   **Outcome:** The Product Tile displays the ConductorProduct.image_url. If that is invalid, it displays the fallback image.

## Stitch UI Prompt

```prompt
Design a React component named ProductTile, styled with Tailwind CSS in dark mode, that displays a product image with a title and optional badges. Use a CSS Grid for layout. The component receives product data including an image URL (imageUrl), product name (name), and stock status (stock).

Use slate-900 for the background, rounded-lg for rounded corners, and shadow-md for shadow. The overall layout should use a CSS Grid with two rows.

Row 1:
- Product Image: Prioritize a JIT-provided thumbnail (if JITState.status === 'complete') over the standard image URL. Use a dark placeholder image as a fallback if both are invalid.  The image should maintain its aspect ratio and fill the available space, using object-cover. The alt text should be the product name. This image should lazy-load.

Row 2:
- Product Name: Use a font-semibold, text-sm, and text-white for the product name. Truncate with ellipsis if the name is too long.
- Badges (optional):
    - "OUT OF STOCK" Badge: If stock is 0, display a red "OUT OF STOCK" badge (bg-red-500, text-white, px-2, py-1, rounded-md, text-xs).
    - "UNCONFIRMED" Badge: If stock is null, display an amber "UNCONFIRMED" badge (bg-amber-500, text-gray-800, px-2, py-1, rounded-md, text-xs).

Data Slots:
- Product Image URL: <imageUrl>
- Product Name: <name>
- Stock Status: <stock> (0, null, or a number > 0)

Component Hierarchy:
- Grid Container (slate-900, rounded-lg, shadow-md)
    - Image (object-cover, alt=<name>, lazy loading)
    - Product Name (font-semibold, text-sm, text-white, truncate)
    - Badges (optional, red or amber as specified above)

Spacing:
- Use a grid-rows-2 layout
- Use p-2 for overall padding within the ProductTile container.
- Place the badges in the top right corner of the tile.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
