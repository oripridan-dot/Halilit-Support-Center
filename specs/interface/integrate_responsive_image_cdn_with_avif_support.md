# Spec: Integrate Responsive Image CDN with AVIF Support

**Version:** 1.0
**Component:** `src/components/ResponsiveImage/ResponsiveImage.tsx`

## Overview
This component enables the display of responsive images, leveraging a Content Delivery Network (CDN) and providing AVIF image format support for modern browsers.  It dynamically generates image URLs based on screen size and preferred image format (AVIF if supported, falling back to WebP, then JPEG/PNG). The component prioritizes performance by loading appropriately sized images. This is in response to a tech scout proposal to use modern image formats to reduce load times.

## Requirements
- The component must accept a base image URL, a set of image sizes (breakpoints), and optional alt text.
- The component must generate different image URLs for each specified breakpoint, using a predefined CDN URL transformation pattern.
- The component must use the `<picture>` element with `<source>` elements for different image formats and sizes.
- AVIF image format must be prioritized if the browser supports it. WebP should be the secondary format.
- The component must gracefully fall back to JPEG/PNG if AVIF and WebP are not supported.
- The component must use `loading="lazy"` attribute on the `<img>` tag.
- The component must use Tailwind CSS for styling.
- The component should accept a `className` prop to allow for custom styling.
- The component should be fully type-safe using TypeScript.
- The image URL generation should adhere to the following pattern: `CDN_BASE_URL/{image_base_url}_{width}.{format}` where:
    - `CDN_BASE_URL` is a configurable environment variable (e.g., `NEXT_PUBLIC_IMAGE_CDN_URL`).
    - `image_base_url` is the base image URL provided as a prop.
    - `width` is the image width for a specific breakpoint.
    - `format` is the image format (avif, webp, jpg/png).
- The component should handle potential errors in image loading gracefully, without crashing the application.  (This spec does not specify error handling UI but implies graceful failure.)
- The component should utilize browser-native lazy loading.

## Data Contract

**Props:**

```typescript
interface ResponsiveImageProps {
  imageBaseUrl: string;
  altText: string;
  className?: string;
  sizes?: {
    sm?: number; // Small breakpoint (e.g., 640px)
    md?: number; // Medium breakpoint (e.g., 768px)
    lg?: number; // Large breakpoint (e.g., 1024px)
    xl?: number; // Extra-large breakpoint (e.g., 1280px)
    "2xl"?: number; // 2x Extra-large breakpoint (e.g., 1536px)
  };
}
```

**Environment Variables:**

- `NEXT_PUBLIC_IMAGE_CDN_URL`: The base URL of the image CDN (e.g., `https://cdn.example.com`).

## Behavior Scenarios

- **Scenario:** Browser supports AVIF
  - Input: `imageBaseUrl = "products/my-image.jpg", sizes = { md: 768, lg: 1024 }`
  - Expected Output:
    ```html
    <picture>
      <source srcset="CDN_BASE_URL/products/my-image_768.avif" media="(min-width: 768px)" type="image/avif">
      <source srcset="CDN_BASE_URL/products/my-image_1024.avif" media="(min-width: 1024px)" type="image/avif">
      <source srcset="CDN_BASE_URL/products/my-image_768.webp" media="(min-width: 768px)" type="image/webp">
      <source srcset="CDN_BASE_URL/products/my-image_1024.webp" media="(min-width: 1024px)" type="image/webp">
      <img src="CDN_BASE_URL/products/my-image.jpg" alt="Product Image" loading="lazy" />
    </picture>
    ```
- **Scenario:** Browser does not support AVIF but supports WebP
  - Input: `imageBaseUrl = "products/my-image.jpg", sizes = { md: 768, lg: 1024 }`
  - Expected Output: (Browser automatically selects WebP source)
    ```html
    <picture>
      <source srcset="CDN_BASE_URL/products/my-image_768.avif" media="(min-width: 768px)" type="image/avif">
      <source srcset="CDN_BASE_URL/products/my-image_1024.avif" media="(min-width: 1024px)" type="image/avif">
      <source srcset="CDN_BASE_URL/products/my-image_768.webp" media="(min-width: 768px)" type="image/webp">
      <source srcset="CDN_BASE_URL/products/my-image_1024.webp" media="(min-width: 1024px)" type="image/webp">
      <img src="CDN_BASE_URL/products/my-image.jpg" alt="Product Image" loading="lazy" />
    </picture>
    ```

- **Scenario:** No sizes provided
  - Input: `imageBaseUrl = "products/my-image.jpg", sizes = {}`
  - Expected Output:
    ```html
    <picture>
      <img src="CDN_BASE_URL/products/my-image.jpg" alt="Product Image" loading="lazy" />
    </picture>
    ```

## Stitch UI Prompt

```text
// Target Component: ResponsiveImage
// Description: A React component that displays responsive images with AVIF and WebP support.
// Layout:  The component renders a <picture> element. Inside the <picture> element, it has multiple <source> elements for different image formats and sizes, and a fallback <img> element.
// Style:  The component should use Tailwind CSS for styling. The alt text should be descriptive.
// Dark mode, Tailwind CSS, slate-900 background, blue-500 accents.  Lazy loading is enabled.
// Data slots:
// imageBaseUrl: products/my-image.jpg
// altText: Product Image
// sizes: {md: 768, lg: 1024}
// The CDN_BASE_URL is https://cdn.example.com (inferred from .env - do not hardcode).
//  Ensure that different <source> elements are created for avif and webp formats. Ensure the <img> tag has loading="lazy".

// Component hierarchy:
// <picture>
//  <source> (for each size and avif)
//  <source> (for each size and webp)
//  <img> (fallback)
// </picture>
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
