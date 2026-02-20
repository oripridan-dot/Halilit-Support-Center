# Spec: Integrate Responsive Image CDN with AVIF Support

**Version:** 1.0
**Component:** `frontend/src/components/ImageWithFallback.tsx`

## Purpose
To enhance the `ImageWithFallback` component by integrating a responsive image CDN with AVIF support, improving image loading performance, reducing bandwidth consumption, and ensuring optimal image quality across different devices and browsers. This directly addresses the "Zero Broken Images" and "Speed of Service" business goals.

## Requirements
1. **CDN Integration:** Integrate with a responsive image CDN (e.g., Cloudinary, Imgix, or similar). Assume the CDN can transform images to AVIF format and generate responsive versions based on device characteristics.
2. **AVIF Support:** The component must prioritize AVIF format when the browser supports it. The CDN should automatically serve AVIF images to supporting browsers.
3. **Responsive Images:** The component must generate responsive image URLs using the CDN to serve appropriately sized images based on the device's screen size and pixel density. Use the `<picture>` element with `<source>` elements for different image formats and sizes.
4. **Fallback Mechanism:** If the browser doesn't support AVIF or the CDN fails to deliver an AVIF image, the component must fall back to a more widely supported format like WebP or JPEG. Ensure the `<img>` tag includes a `src` attribute with a fallback image URL.
5. **Placeholder Image:** If the `imageUrl` is missing, null, an empty string, or if all CDN transformations fail, the component must display a dark placeholder image (`/placeholder.png` or an inline SVG).
6. **Error Handling:** The component must gracefully handle CDN errors and network issues, displaying the placeholder image if necessary.
7. **Lazy Loading:** Implement lazy loading for images to further improve initial page load performance.
8. **Data Trust Integration:** If a `dataTrust` prop is passed, the `altText` should be automatically updated to include data source attributions.
9. **Cache Busting:** Implement a cache-busting mechanism to ensure that updated images are served to users without browser caching issues.
10. **No External Libraries:** Implement the CDN integration without relying on external UI libraries beyond the existing dependencies (React 18, TypeScript, Tailwind CSS).

## Behavior Scenarios
1. **Scenario:** Browser supports AVIF, and the CDN successfully delivers an AVIF image.
    - Outcome: The component displays the AVIF image, and the browser loads the image from the CDN.
2. **Scenario:** Browser does not support AVIF, but the CDN delivers a WebP image.
    - Outcome: The component displays the WebP image, and the browser loads the image from the CDN.
3. **Scenario:** Browser does not support AVIF or WebP, and the CDN delivers a JPEG image.
    - Outcome: The component displays the JPEG image, and the browser loads the image from the CDN.
4. **Scenario:** The `imageUrl` is missing, null, or an empty string.
    - Outcome: The component displays the dark placeholder image.
5. **Scenario:** The CDN is unavailable, or the image transformation fails.
    - Outcome: The component displays the dark placeholder image.
6. **Scenario:** The image is below the fold and lazy loading is enabled.
    - Outcome: The image is not loaded until it scrolls into the viewport.

## Stitch UI Prompt
```text
// Target Component: ImageWithFallback
// Description: A React component that displays an image with responsive CDN support, AVIF prioritization, fallback mechanism, and lazy loading.

// Layout: None (This is a single image element within a <picture> element, so no specific layout is needed).

// Visual Style: Dark Mode
// * Background: slate-900 (Tailwind CSS)
// * Text Color: gray-300 (Tailwind CSS)
// * Placeholder Background: gray-800 (Tailwind CSS)

// Data Slots:
// 1. imageUrl: The base URL of the image to display. Placeholder: "https://example.com/image.jpg"
// 2. altText: The alt text for the image. Placeholder: "Product Image"
// 3. cdnBaseUrl: The base URL of the image CDN. Placeholder: "https://cdn.example.com/"

// Component Hierarchy:
// * The component consists of a <picture> element.
// * Inside the <picture> element, there are multiple <source> elements for different image formats (AVIF, WebP) and sizes.
// * The last child of the <picture> element is an <img> element with a fallback image format (JPEG) and the placeholder image as the initial `src`.
// * The <img> element should have `loading="lazy"` to enable lazy loading.
// * An `onError` handler on the <img> element should set the `src` to the placeholder image if all other sources fail to load.

// Responsive Image Logic:
// * Use the CDN's URL transformation features to generate responsive image URLs based on device size (e.g., using `srcset` attribute on <source> elements).
// * Example CDN URL transformation: `${cdnBaseUrl}${imageUrl}?format=avif&width=600, ${cdnBaseUrl}${imageUrl}?format=avif&width=1200 2x`
// * The <source> elements should have `type` attributes specifying the image format (e.g., `image/avif`, `image/webp`).

// Fallback Logic:
// * The <img> element's `src` attribute should point to a fallback JPEG image URL generated by the CDN.
// * The <img> element's `onError` handler should set the `src` to the placeholder image if the JPEG image fails to load.

// Placeholder Image:
// * If the `imageUrl` is not provided, display the placeholder image directly within the <img> element.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- `echo "Manual Verification Required: Inspect the component in different browsers (with and without AVIF support) and on different devices to ensure that responsive images are loaded correctly and that the fallback mechanism works as expected."`
