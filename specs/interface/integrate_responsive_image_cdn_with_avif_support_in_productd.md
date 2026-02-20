# Spec: Integrate Responsive Image CDN with AVIF Support in ProductDetailView

**Version:** 1.0
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## 1. Purpose

To integrate a responsive image solution using a CDN and AVIF support within the `ProductDetailView`. This aims to improve page load times, reduce bandwidth consumption, and enhance the visual experience by delivering optimized images based on the user's device and browser capabilities.  Addresses the Master Plan goals of "Zero Broken Images" and "Speed of Service".

## 2. Requirements

1. **Replace Existing Image Display:** Remove the direct usage of `<img>` tag for the main product image in the `ProductDetailView`.
2. **Implement ResponsiveImage Component:** Integrate a new `ResponsiveImage` component (spec below). This component will be responsible for generating responsive image URLs and handling format negotiation (AVIF, WebP, JPEG/PNG).
3. **Configure CDN Base URL:** The CDN base URL MUST be configurable via an environment variable (e.g., `NEXT_PUBLIC_IMAGE_CDN_URL`). This variable should be read and passed as a prop to the `ResponsiveImage` component.
4. **Define Image Breakpoints:** Define a set of image breakpoints (widths) to be used for generating responsive image URLs. These breakpoints should cover common screen sizes (e.g., 320, 640, 768, 1024, 1280 pixels).
5. **Pass Image URL and Alt Text:** The `ResponsiveImage` component MUST receive the main product image URL (`product.image_url`) and the product name (`product.name`) as props. The product name should be used as the `alt` text for accessibility.
6. **CDN URL Generation Pattern:** The `ResponsiveImage` component MUST generate image URLs following this pattern: `${CDN_BASE_URL}/${image_url}?w=${width}&fm=${format}`.
   - `CDN_BASE_URL`: The value of the `NEXT_PUBLIC_IMAGE_CDN_URL` environment variable.
   - `image_url`: The original image URL.
   - `width`: The image width for a specific breakpoint.
   - `format`: The image format (avif, webp, jpg).
7. **Loading Attribute:** Implement `loading="lazy"` attribute on the `<img>` tag in `ResponsiveImage` component.
8. **Error Handling:** If any error during image loading should be handled gracefully by displaying a fallback.  The ImageWithFallback component from `/components/ImageWithFallback.tsx` should be re-used here.

## 3. Data Contract

1.  **Existing `ConductorProduct` Interface:**  The `ProductDetailView` already receives a `ConductorProduct` object as a prop.  This object contains the `image_url` (string) and `name` (string) properties needed for the `ResponsiveImage` component.
2.  **Environment Variable:** `NEXT_PUBLIC_IMAGE_CDN_URL` (string) - The base URL of the image CDN.

## 4. Behavior Scenarios

1. **Scenario:** The `ProductDetailView` loads with a valid `product.image_url` and `NEXT_PUBLIC_IMAGE_CDN_URL` is properly configured.
   - **Outcome:** The `ResponsiveImage` component generates responsive image URLs based on the defined breakpoints and CDN URL pattern. The browser loads the most appropriate image based on its screen size and supported formats. The image is displayed correctly in the Product Detail view.
2. **Scenario:** The `ProductDetailView` loads with a missing or invalid `product.image_url`.
   - **Outcome:**  The ImageWithFallback from `/components/ImageWithFallback.tsx` handles the missing image and display the placeholder image.
3. **Scenario:** The `NEXT_PUBLIC_IMAGE_CDN_URL` environment variable is not configured.
   - **Outcome:** The app should either display an error message, or use a sensible default image loading strategy (e.g., direct `<img>` tag) if that's implemented as a fallback.
4. **Scenario:** The browser supports AVIF format.
   - **Outcome:** The `ResponsiveImage` component prioritizes AVIF images by putting the `<source type="image/avif"...` first. The browser loads and displays the AVIF image.
5. **Scenario:** The browser does not support AVIF format but supports WebP.
   - **Outcome:** The `ResponsiveImage` component falls back to WebP images by putting the `<source type="image/webp"...` second. The browser loads and displays the WebP image.
6.  **Scenario:**  The CDN returns an error for one of the image sizes.
    *   **Outcome:** The browser attempts to load the next available size, eventually falling back to the default `<img>` src.

## 5. ResponsiveImage Component Spec

This is a new component that needs to be created:

**Component:** `frontend/src/components/ResponsiveImage.tsx`

### 5.1 Purpose

To display responsive images, leveraging a Content Delivery Network (CDN) and providing AVIF image format support for modern browsers. It dynamically generates image URLs based on screen size and preferred image format (AVIF if supported, falling back to WebP, then JPEG/PNG). The component prioritizes performance by loading appropriately sized images.

### 5.2 Requirements

- The component must accept a base image URL, a set of image sizes (breakpoints), and alt text as props.
- The component must generate different image URLs for each specified breakpoint, using a predefined CDN URL transformation pattern (defined in section 2).
- The component must use the `<picture>` element with `<source>` elements for different image formats and sizes.
- AVIF image format must be prioritized if the browser supports it. WebP should be the secondary format.
- The component must gracefully fall back to JPEG/PNG if AVIF and WebP are not supported.
- The component must use `loading="lazy"` attribute on the `<img>` tag.
- The component must use Tailwind CSS for styling.
- The component should accept a `className` prop to allow for custom styling.
- The component should be fully type-safe using TypeScript.
- The image URL generation should adhere to the following pattern (reiterated): `CDN_BASE_URL/{image_base_url}?w={width}&fm={format}` where:
    - `CDN_BASE_URL` is a configurable environment variable (e.g., `NEXT_PUBLIC_IMAGE_CDN_URL`).
    - `image_base_url` is the base image URL provided as a prop.
    - `width` is the image width for a specific breakpoint.
    - `format` is the image format (avif, webp, jpg).

## Stitch UI Prompt

```text
// Target Component: ResponsiveImage
// Description: A React component that displays responsive images with AVIF and WebP support using a CDN.
// Layout: Uses a <picture> element with <source> elements for different image formats and sizes.
// Visual Style: Dark mode, Tailwind CSS, slate-900 background, blue-500 accents.
//
// Data Slots:
// - CDN_BASE_URL: The base URL of the image CDN (e.g., "https://cdn.example.com").
// - image_url: The base image URL (e.g., "/images/product.jpg").
// - altText: The alt text for the image (e.g., "Product Image").
//
// Component Hierarchy:
// <picture>
//   <source srcset="{CDN_BASE_URL}/{image_url}?w=320&fm=avif" type="image/avif" media="(max-width: 320px)" />
//   <source srcset="{CDN_BASE_URL}/{image_url}?w=640&fm=avif" type="image/avif" media="(max-width: 640px)" />
//   <source srcset="{CDN_BASE_URL}/{image_url}?w=768&fm=avif" type="image/avif" media="(max-width: 768px)" />
//   ... (other AVIF sources for different breakpoints)
//   <source srcset="{CDN_BASE_URL}/{image_url}?w=320&fm=webp" type="image/webp" media="(max-width: 320px)" />
//   ... (other WebP sources for different breakpoints)
//   <img src="{CDN_BASE_URL}/{image_url}?w=1280&fm=jpg" alt="{altText}" loading="lazy" className="w-full h-full object-cover" />
// </picture>
//
// Spacing: No specific spacing requirements.
// Tailwind Color Tokens:  Use slate-900 for background, blue-500 for accents, gray-500 for placeholder text.
//
// Detailed Instructions:
// 1. Create a React functional component named ResponsiveImage.
// 2. Accept props for `CDN_BASE_URL`, `image_url`, `altText`, and `className`.
// 3. Define an array of image breakpoints (e.g., [320, 640, 768, 1024, 1280]).
// 4. Generate <source> elements for AVIF and WebP formats for each breakpoint.
// 5. Generate a default <img> element with a JPEG/PNG format and loading="lazy".
// 6. Apply Tailwind CSS classes for responsive image display (e.g., w-full, h-full, object-cover).
// 7. Use conditional rendering to display a placeholder image if the image URL is missing.
// 8. Add a className prop to allow for additional styling.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- Verify that images on product detail view are loading from the CDN with responsive sizes based on viewport width. Check the Network tab in browser developer tools.
- Manually test different browsers to confirm AVIF/WebP fallback behavior.
- `echo $NEXT_PUBLIC_IMAGE_CDN_URL` (confirm env var is set during test run).
