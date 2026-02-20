# Spec: Integrate Responsive Image CDN with AVIF Support

**Target:** src/components/ResponsiveImage/ResponsiveImage.tsx

## Overview
This component enables the display of responsive images, leveraging a Content Delivery Network (CDN) and providing AVIF image format support for modern browsers.  It dynamically generates image URLs based on screen size and preferred image format (AVIF if supported, falling back to WebP, then JPEG/PNG). The component prioritizes performance by loading appropriately sized images.

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
    - `CDN_BASE_URL` is a configurable environment variable.
    - `image_base_url` is the base image URL provided as a prop.
    - `width` is the image width for a specific breakpoint.
    - `format` is the image format (avif, webp, jpg/png).
- The component should handle potential errors in image loading gracefully, without crashing the application.  (This spec does not specify error handling UI but implies graceful failure.)

## Data Contract

**Props:**

```typescript
interface ResponsiveImageProps {
  imageBaseUrl: string;
  alt: string;
  sizes: {
    [key: string]: number; // e.g., { small: 320, medium: 768, large: 1280 } representing screen width breakpoints
  };
  className?: string; // Optional Tailwind CSS class names
}
```

## Behavior Scenarios

- **Scenario:** Browser supports AVIF, Small Screen
  - Input: `imageBaseUrl` = "images/hero", `alt` = "Hero Image", `sizes` = `{ small: 320, medium: 768, large: 1280 }`, screen width = 320px
  - Outcome:
    - `<picture>` element is rendered.
    - First `<source>` element has `srcset` attribute: `${process.env.NEXT_PUBLIC_CDN_BASE_URL}/images/hero_320.avif` and `type` attribute: "image/avif".
    - Second `<source>` element has `srcset` attribute: `${process.env.NEXT_PUBLIC_CDN_BASE_URL}/images/hero_320.webp` and `type` attribute: "image/webp".
    - `<img>` element has `src` attribute: `${process.env.NEXT_PUBLIC_CDN_BASE_URL}/images/hero_320.jpg`, `alt` attribute: "Hero Image", and `loading` attribute: "lazy".
    - Tailwind classes are applied: `className` prop, plus `w-full h-auto`.

- **Scenario:** Browser does NOT support AVIF, Medium Screen
  - Input: `imageBaseUrl` = "product/thumbnail", `alt` = "Product Thumbnail", `sizes` = `{ small: 320, medium: 768, large: 1280 }`, screen width = 800px (browser AVIF support is disabled for testing)
  - Outcome:
    - `<picture>` element is rendered.
    - First `<source>` element has `srcset` attribute: `${process.env.NEXT_PUBLIC_CDN_BASE_URL}/product/thumbnail_768.webp` and `type` attribute: "image/webp".
    - `<img>` element has `src` attribute: `${process.env.NEXT_PUBLIC_CDN_BASE_URL}/product/thumbnail_768.jpg`, `alt` attribute: "Product Thumbnail", and `loading` attribute: "lazy".
    - Tailwind classes are applied: `className` prop, plus `w-full h-auto`.

- **Scenario:** Large Screen, Custom Class Name
  - Input: `imageBaseUrl` = "blog/post", `alt` = "Blog Post Image", `sizes` = `{ small: 320, medium: 768, large: 1280 }`, screen width = 1400px, `className` = "rounded-lg shadow-md"
  - Outcome:
    - `<picture>` element is rendered.
    - First `<source>` element has `srcset` attribute: `${process.env.NEXT_PUBLIC_CDN_BASE_URL}/blog/post_1280.avif` and `type` attribute: "image/avif".
    - Second `<source>` element has `srcset` attribute: `${process.env.NEXT_PUBLIC_CDN_BASE_URL}/blog/post_1280.webp` and `type` attribute: "image/webp".
    - `<img>` element has `src` attribute: `${process.env.NEXT_PUBLIC_CDN_BASE_URL}/blog/post_1280.jpg`, `alt` attribute: "Blog Post Image", and `loading` attribute: "lazy".
    - Tailwind classes are applied: `rounded-lg shadow-md w-full h-auto`.

- **Scenario:** Empty Sizes Object
  - Input: `imageBaseUrl` = "misc/logo", `alt` = "Company Logo", `sizes` = `{}`, screen width = irrelevant.
  - Outcome:
    - `<img>` element is rendered.
    - `<img>` element has `src` attribute: `${process.env.NEXT_PUBLIC_CDN_BASE_URL}/misc/logo_.jpg`, `alt` attribute: "Company Logo", and `loading` attribute: "lazy". The `width` parameter is missing from the generated URL because no sizes are provided.
    - Tailwind classes are applied: `w-full h-auto`.

## Out of Scope
- Image optimization techniques (e.g., compression, quality settings) are assumed to be handled by the CDN.
- Error handling UI (e.g., displaying a placeholder image or error message) is not specified in this version.  The component should avoid crashing the page but how errors are displayed is left to a future specification.
- Advanced CDN features like image manipulation (cropping, watermarking) are not covered.
- Configuration of the `CDN_BASE_URL` environment variable is out of scope.  It is assumed to be set.
