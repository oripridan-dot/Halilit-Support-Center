# Spec: Product Tile - Image Validation and Fallback

**Version:** 1.0
**Component:** `frontend/src/components/ProductTile.tsx`

## 1. Purpose

To ensure that product images in Product Tiles always display correctly, even if the original image URL is broken or invalid, contributing to the "Zero Broken Images" business goal. This spec builds upon existing image handling strategies and provides a complete solution within the ProductTile component.

## 2. Requirements

1.  **Image URL Handling:** The Product Tile MUST accept a product object with an `image_url` property (string or undefined/null).
2. **Image Validation (Non-Hero Images):** Because ProductTiles are used heavily, but are NOT considered hero images, the validation should be skipped, and the fallback should be used on error.
3.  **Fallback Image:** If the `image_url` is missing, null, or an empty string, OR if the image fails to load (onError), the Product Tile MUST display a dark placeholder image (`/placeholder.png` or an inline SVG).
4.  **onError Handler:** The `<img>` tag MUST have an `onError` handler that sets the image source to `/placeholder.png` if the image fails to load.
5.  **Placeholder Styling:** The placeholder image MUST maintain the aspect ratio of the original image to prevent layout distortion. If using an inline SVG, the SVG MUST be styled to have a dark background.
6. **Alt Text:** The `<img>` tag MUST include an `alt` attribute that describes the image (e.g., the product name), even when the placeholder image is displayed.
7.  **CSS Styling:** Use Tailwind CSS to style the image and placeholder for consistent appearance across the application.
8. **No Validation Hook Dependency:** The ProductTile component itself should not use `useValidateHeroImage`, as validation is not needed for non-hero tiles.

## 3. Behavior Scenarios

1.  **Scenario:** The Product Tile receives a product with a valid `image_url`.
    *   **Outcome:** The image is displayed correctly.
2.  **Scenario:** The Product Tile receives a product with a missing `image_url` (null, undefined, or empty string).
    *   **Outcome:** The dark placeholder image is displayed.
    *   **Outcome:** The `alt` attribute is set to the product name.
3.  **Scenario:** The Product Tile receives a product with an `image_url` that returns a 404 error.
    *   **Outcome:** The dark placeholder image is displayed after the image fails to load.
    *   **Outcome:** The `alt` attribute is set to the product name.
4.  **Scenario:** The Product Tile receives a product with a very long `image_url` that potentially times out.
    *   **Outcome:** The dark placeholder image is displayed after the image fails to load.
    *   **Outcome:** The `alt` attribute is set to the product name.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
