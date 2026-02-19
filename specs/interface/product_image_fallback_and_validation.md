# Spec: Product Image Fallback and Validation

**Version:** 1.0
**Component:** `frontend/src/components/ProductTile.tsx`

## 1. Purpose

To ensure that no broken image links appear in the Halilit Support Center, enhancing visual appeal and user experience. Addresses the "Zero Broken Images" business goal.

## 2. Requirements

1.  **Hero Image Validation:** Before displaying a product's `image_url` in the Product Detail View (Hero image), the system MUST validate that the image URL is accessible and returns a successful HTTP status code (200-299). This validation SHOULD happen asynchronously, ideally during the initial load of the Product Detail data.
2.  **Fallback on Validation Failure:** If the hero image validation fails (e.g., the image URL returns a 404 or the request times out), the system MUST display a professional dark placeholder image (`/placeholder.png` or an inline SVG) instead of the broken image.
3.  **Product Tile Image Fallback:** The image displayed in Product Tiles (e.g., in the Inventory View or Accessory Recommendations) MUST use a dark placeholder image (`/placeholder.png` or an inline SVG) if the `image_url` is missing or fails to load.
4.  **Image Loading Error Handling:** The `<img>` tag in both Product Tiles and the Product Detail View MUST have an `onError` handler that sets the image source to `/placeholder.png` if the image fails to load.
5.  **Placeholder Styling:** The placeholder image MUST maintain the aspect ratio of the original image to prevent layout distortion.  If using an inline SVG, the SVG MUST be styled to have a dark background.
6. **Cache Invalid Images:** The system MUST cache the validation failure of an image URL for at least 24 hours to avoid repeatedly attempting to load a broken image. This cache MUST be keyed by the image URL.
7. **Retry Mechanism (Optional):** The system MAY implement a retry mechanism for image validation failures, but MUST limit retries to a maximum of 3 attempts within a 1-hour period.

## 3. Behavior Scenarios

1.  **Scenario:** Product A has a valid `image_url`.
    *   **Outcome:** The image at `image_url` is displayed in the Product Detail View and any Product Tiles where Product A is shown.
2.  **Scenario:** Product B has an `image_url` that returns a 404 error.
    *   **Outcome:** A dark placeholder image (`/placeholder.png` or an inline SVG) is displayed in place of the broken image in the Product Detail View and any Product Tiles where Product B is shown.  The error is logged.
3.  **Scenario:** Product C has a missing `image_url` (empty string or null).
    *   **Outcome:** A dark placeholder image is displayed in place of the missing image in the Product Detail View and any Product Tiles where Product C is shown.
4.  **Scenario:** The image at `image_url` for Product D initially fails to load due to a network issue.
    *   **Outcome:** A dark placeholder image is displayed. The system MAY retry loading the image later.

