# Spec: Product Detail Image Sourcing and Display
**Target:** `frontend/src/components/ProductDetail/ProductImageCarousel.tsx`

## Overview
This component is responsible for displaying a carousel of product images on the product detail page. It fetches image URLs from the backend based on the product ID and renders them using a carousel component. The component should gracefully handle cases where no images are available for a product.

## Requirements
- Fetch image URLs from the `/api/products/{product_id}/images` endpoint.
- Display the images in a horizontal carousel with navigation controls.
- The carousel should support swiping on touch devices.
- Implement a loading state while fetching images.
- Display a placeholder image or a "No images available" message if no images are returned from the API.
- Handle potential errors during image fetching (e.g., network errors).
- Use Tailwind CSS for styling, adhering to the dark theme (slate-900 background, blue-500 accent).

## Data Contract

**API Endpoint:** `/api/products/{product_id}/images` (GET)

**Request:**
- Path Parameter: `product_id` (integer) - The ID of the product.

**Response (Success - 200 OK):**
```json
{
  "images": [
    {
      "url": "string"  // URL of the image
    },
    {
      "url": "string"
    },
    ...
  ]
}
```

**Response (No Images Available - 204 No Content):**
- Empty response body.

**Response (Error - 500 Internal Server Error):**
```json
{
  "detail": "string" // Error message
}
```

**TypeScript Interface:**
```typescript
interface Image {
  url: string;
}

interface ImageResponse {
  images: Image[];
}
```

## Behavior Scenarios

- **Scenario: Product has multiple images**
  - Input: `product_id = 123`, API returns `{"images": [{"url": "https://example.com/image1.jpg"}, {"url": "https://example.com/image2.jpg"}]}`
  - Outcome: A carousel with two images is displayed. Navigation controls are visible, and the user can swipe or click to navigate between images.

- **Scenario: Product has no images**
  - Input: `product_id = 456`, API returns a 204 No Content response.
  - Outcome:  A "No images available" message is displayed in the carousel area. Navigation controls are hidden.

- **Scenario: API returns an error**
  - Input: `product_id = 789`, API returns a 500 Internal Server Error with `{"detail": "Failed to fetch images"}`.
  - Outcome: An error message "Failed to load images" is displayed in the carousel area.

- **Scenario: Loading state**
  - Input: `product_id = 123`, API request takes 2 seconds to respond.
  - Outcome: A loading indicator (e.g., spinner) is displayed in the carousel area for 2 seconds, then the images are displayed.

## Out of Scope
- Image upload functionality.
- Image optimization (resizing, compression).
- Implementing a full image viewer (e.g., zoom functionality).
- Authentication/Authorization for image access.
- Detailed Tailwind CSS configuration (only basic styling is covered).

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
