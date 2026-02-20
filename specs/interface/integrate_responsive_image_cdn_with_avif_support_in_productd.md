# Spec: Integrate Responsive Image CDN with AVIF Support in ProductDetailView

**Version:** 1.1
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## 1. Purpose

To integrate a responsive image solution using a CDN and AVIF support within the `ProductDetailView`. This aims to improve page load times, reduce bandwidth consumption, and enhance the visual experience by delivering optimized images based on the user's device and browser capabilities. Addresses the Master Plan goals of "Zero Broken Images" and "Speed of Service".

## 2. Requirements

1. **Replace Existing Image Display:** Remove the direct usage of `<img>` tag for the main product image in the `ProductDetailView`. Replace it with `<ResponsiveImage/>` component.
2. **Implement ResponsiveImage Component:** Create a new `ResponsiveImage` component (spec below). This component will be responsible for generating responsive image URLs and handling format negotiation (AVIF, WebP, JPEG/PNG). If the component already exists, follow the guidelines below.
3. **Configure CDN Base URL:** The CDN base URL MUST be configurable via an environment variable (e.g., `NEXT_PUBLIC_IMAGE_CDN_URL`). This variable should be read and passed as a prop to the `ResponsiveImage` component.
4. **Define Image Breakpoints:** Define a set of image breakpoints (widths) to be used for generating responsive image URLs. These breakpoints should cover common screen sizes (e.g., 320, 640, 768, 1024, 1280 pixels).
5. **Pass Image URL and Alt Text:** The `ResponsiveImage` component MUST receive the main product image URL (`product.image_url`) and the product name (`product.name`) as props. The product name should be used as the `alt` text for accessibility.
6. **CDN URL Generation Pattern:** The `ResponsiveImage` component MUST generate image URLs following this pattern: `${CDN_BASE_URL}/${image_url}?w=${width}&fm=${format}`.
   - `CDN_BASE_URL`: The value of the `NEXT_PUBLIC_IMAGE_CDN_URL` environment variable.
   - `image_url`: The original image URL.
   - `width`: The image width for a specific breakpoint.
   - `format`: The image format (`avif`, `webp`, or `jpg`).
7. **AVIF Support Detection:** The `ResponsiveImage` component MUST detect browser support for AVIF format using the `Modernizr` library (if not already present in the project) or a similar feature detection mechanism.
8. **Format Prioritization:** If AVIF is supported, the component MUST prioritize AVIF images in the `srcset` attribute. If AVIF is not supported, the component should fallback to WebP if supported, and then to JPEG/PNG.
9. **Lazy Loading:** Implement lazy loading for images using the `loading="lazy"` attribute on the `<img>` tag within the `ResponsiveImage` component.
10. **Placeholder Image:** The `ResponsiveImage` component should use a placeholder image (low-resolution version) while the main image is loading.
11. **Error Handling:** If an image fails to load, the component must display a fallback image or an error message.
12. **Accessibility:** The `<img>` tag MUST include an `alt` attribute that describes the image, even when the placeholder image is displayed.
13. **Dark Theme Styling:** Use Tailwind CSS for styling, adhering to the dark theme (slate-900 background, blue-500 accents).
14. If NEXT_PUBLIC_IMAGE_CDN_URL is not present in the environment variables, then the component `<ResponsiveImage>` should return `<img>` tag and display the `product.image_url` as before with the alt text.
15. Sizes attribute should be configurable through props.

## 3. Behavior Scenarios

1.  **Scenario:** The `NEXT_PUBLIC_IMAGE_CDN_URL` is properly set in the environment variable and the browser supports AVIF.
    *   **Outcome:** The Product Detail hero image is rendered using the `ResponsiveImage` component, with AVIF images prioritized in the `srcset` attribute.
2.  **Scenario:** The `NEXT_PUBLIC_IMAGE_CDN_URL` is properly set in the environment variable, but the browser does not support AVIF.
    *   **Outcome:** The Product Detail hero image is rendered using the `ResponsiveImage` component, with WebP images (if supported) or JPEG/PNG images in the `srcset` attribute.
3.  **Scenario:** The `NEXT_PUBLIC_IMAGE_CDN_URL` is not set in the environment variable.
    *   **Outcome:** The Product Detail hero image is rendered using a standard `<img>` tag with the `product.image_url` as the source.
4.  **Scenario:** An image fails to load.
    *   **Outcome:** The fallback image is displayed.

## Stitch UI Prompt

```text
// Target Component: ProductDetailView
// Description:  Refactor ProductDetailView to use ResponsiveImage component for hero image with CDN support.
// Layout: The ProductDetailView layout remains mostly the same but the image is replaced with ResponsiveImage
// Visual Style: Dark mode, Tailwind CSS, slate-900 background, blue-500 accents. Ensure all other components retain existing styling.
// Data Slots:
//   - imageBaseUrl: A string representing the base URL of the product image (e.g., products/HAL123.jpg). Replace HAL123.jpg by the product.image_url
//   - altText: A string representing the alt text for the image (product name).  Replace value by product.name
// Instructions:
//   1. Locate the <img> tag responsible for displaying the product's hero image.
//   2. Replace the <img> tag with <ResponsiveImage imageBaseUrl={product.image_url} altText={product.name} />
//   3. Ensure that the ResponsiveImage component correctly implements lazy loading.
//   4. Maintain the overall layout and styling of the ProductDetailView.
//   5. Configure responsive breakpoints such as sm: 640, md: 768, lg: 1024, xl: 1280, 2xl: 1536.
// Component Hierarchy: Ensure that other components such as ProductInfo, ProductDocuments, etc., remain untouched and well-integrated.
// Spacing:  Maintain the current spacing between all elements of the ProductDetailView.
// CDN Base URL: Consider using an environment variable to dynamically generate URL's for the CDN
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
