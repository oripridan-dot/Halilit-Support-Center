# Spec: Product Tile - Image Sourcing Badges

**Target:** `src/components/ProductTile/ProductTileImage.tsx`

## Overview
This component enhances the product tile by displaying badges on top of the product image to indicate the image source. This allows users to quickly identify if the image is a stock photo, a manufacturer-provided image, or an original Halilit-created image.

## Requirements
- The component must display one or more badges on the top-right corner of the product image.
- Badges should be visually distinct using different colors and icons to represent different image sources.
- The badge style should be consistent with the Halilit Support Center's dark theme (slate-900/blue-500 palette).
- The component should accept a prop indicating the image source(s).
- The badges should be positioned absolutely within the image container.
- The component should handle scenarios where a product image has no specified sources or multiple sources.
- Badges should be rendered in a stacked manner, with the most important source appearing on top.  We prioritize Halilit > Manufacturer > Stock.

## Data Contract

**Props:**

```typescript
interface ProductTileImageProps {
  imageUrl: string;
  imageSources?: ImageSource[];
  altText: string;
}

enum ImageSource {
  HALILIT = "halilit",
  MANUFACTURER = "manufacturer",
  STOCK = "stock",
}
```

## Behavior Scenarios

- **Scenario:** No Image Sources
  - Input: `imageUrl: "example.com/product.jpg", imageSources: undefined, altText: "Product Image"`
  - Outcome:  The product image is displayed without any badges.

- **Scenario:** Single Halilit Image Source
  - Input: `imageUrl: "example.com/product.jpg", imageSources: [ImageSource.HALILIT], altText: "Product Image"`
  - Outcome: The product image is displayed with a single "Halilit" badge in the top-right corner.  The badge should have a distinct Halilit brand color (e.g., blue-500) and an appropriate icon (e.g., a camera).

- **Scenario:** Single Manufacturer Image Source
  - Input: `imageUrl: "example.com/product.jpg", imageSources: [ImageSource.MANUFACTURER], altText: "Product Image"`
  - Outcome: The product image is displayed with a single "Manufacturer" badge in the top-right corner. The badge should have a distinct color (e.g., slate-700) and an appropriate icon (e.g., a building).

- **Scenario:** Single Stock Image Source
  - Input: `imageUrl: "example.com/product.jpg", imageSources: [ImageSource.STOCK], altText: "Product Image"`
  - Outcome: The product image is displayed with a single "Stock" badge in the top-right corner. The badge should have a distinct color (e.g., slate-500) and an appropriate icon (e.g., a dollar sign).

- **Scenario:** Multiple Image Sources (Halilit and Manufacturer)
  - Input: `imageUrl: "example.com/product.jpg", imageSources: [ImageSource.HALILIT, ImageSource.MANUFACTURER], altText: "Product Image"`
  - Outcome: The product image is displayed with two badges stacked in the top-right corner. The "Halilit" badge should be on top (closest to the corner) and the "Manufacturer" badge below it.

- **Scenario:** Multiple Image Sources (Halilit, Manufacturer, and Stock)
  - Input: `imageUrl: "example.com/product.jpg", imageSources: [ImageSource.HALILIT, ImageSource.MANUFACTURER, ImageSource.STOCK], altText: "Product Image"`
  - Outcome: The product image is displayed with three badges stacked in the top-right corner. The "Halilit" badge should be on top, followed by "Manufacturer", then "Stock".

- **Scenario:** Multiple Image Sources (Manufacturer and Stock)
  - Input: `imageUrl: "example.com/product.jpg", imageSources: [ImageSource.MANUFACTURER, ImageSource.STOCK], altText: "Product Image"`
  - Outcome: The product image is displayed with two badges stacked in the top-right corner. The "Manufacturer" badge should be on top, followed by "Stock".

## Out of Scope
- Image optimization or resizing.
- Handling image loading errors.
- The specific icons used for each image source (this can be configured separately).
- Responsiveness of the badges on different screen sizes (basic stacking is enough for now).
