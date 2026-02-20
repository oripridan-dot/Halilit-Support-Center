# Spec: Integrate Responsive Image CDN with AVIF Support

**Version:** 1.0
**Component:** `frontend/src/components/ImageWithFallback.tsx`

## Purpose
To enhance the `ImageWithFallback` component by integrating a responsive image CDN with AVIF support, improving image loading performance, reducing bandwidth consumption, and ensuring optimal image quality across different devices and browsers. This directly addresses the "Zero Broken Images" and "Speed of Service" business goals.

## Requirements
1. **CDN Integration:** Integrate with a responsive image CDN (e.g., Cloudinary, Imgix, or similar). Assume the CDN can transform images to AVIF format and generate responsive versions based on device characteristics via URL parameters. The exact URL parameters will depend on the chosen CDN (e.g. Cloudinary: `f_auto,q_auto` for format and quality).
2. **AVIF Support:** The component must prioritize AVIF format when the browser supports it. The CDN should automatically serve AVIF images to supporting browsers via content negotiation (Accept header).
3. **Responsive Images:** Generate responsive image URLs using the CDN to serve appropriately sized images based on the device's screen size and pixel density. Use the `<picture>` element with `<source>` elements for different image formats and sizes. Create three sizes: small (320w), medium (640w), and large (1024w).
4. **Fallback Mechanism:** If the browser doesn't support AVIF or the CDN fails to deliver an AVIF image, the component must fall back to WebP and then to JPEG. Ensure the `<img>` tag includes a `src` attribute with a fallback image URL.
5. **Placeholder Image:** If the `imageUrl` is missing, null, an empty string, or if all CDN transformations fail, the component must display a dark placeholder image (`/placeholder.png` or an inline SVG).
6. **Error Handling:** The component must gracefully handle CDN errors and network issues, displaying the placeholder image if necessary.
7. **Lazy Loading:** Implement lazy loading for images to further improve initial page load performance using the `loading="lazy"` attribute on the `<img>` tag.
8. **Data Trust Integration:** If a `dataTrust` prop is passed, the `altText` should be automatically updated to include data source attributions.
9. **Placeholder Styling:** The placeholder image MUST maintain the aspect ratio of the original image to prevent layout distortion.

## Behavior Scenarios
1. **Scenario:** Browser supports AVIF, CDN serves AVIF.
  - Input: `imageUrl` is a valid CDN URL.
  - Outcome: The browser loads the AVIF image from the CDN.
2. **Scenario:** Browser does NOT support AVIF, CDN serves WebP.
  - Input: `imageUrl` is a valid CDN URL.
  - Outcome: The browser loads the WebP image from the CDN.
3. **Scenario:** Browser does NOT support AVIF or WebP, CDN serves JPEG.
  - Input: `imageUrl` is a valid CDN URL.
  - Outcome: The browser loads the JPEG image from the CDN.
4. **Scenario:** CDN URL is invalid or returns an error.
  - Input: `imageUrl` is an invalid CDN URL.
  - Outcome: The placeholder image is displayed.
5. **Scenario:** `imageUrl` is null or undefined.
  - Input: `imageUrl` is null.
  - Outcome: The placeholder image is displayed.
6. **Scenario:** Data Trust is provided.
  - Input: `imageUrl` is a valid CDN URL, and `dataTrust` object is passed.
  - Outcome: Image is loaded, `altText` reflects sourcing.

## Stitch UI Prompt
```text
// Target Component: ImageWithFallback
// Description: A React component that displays an image with responsive sizing, AVIF support, lazy loading, and a fallback placeholder.
// Layout:  The component uses a <picture> element containing <source> elements for different image formats (AVIF, WebP, JPEG) and sizes (small, medium, large) and a default <img> tag for fallback. The <img> tag should also have the loading="lazy" attribute.
// Visual Style:  Dark mode, Tailwind CSS. Use slate-900 for the background of the placeholder and blue-500 for any loading indicators.
// Data Slots:
//   - imageUrl: The base URL of the image on the CDN (string).
//   - altText:  The alt text for the image (string).
//   - dataTrust: [Optional] An object that includes attribution information.
// The CDN URLs should use URL parameters for AVIF, WebP, and JPEG formats. Example (Cloudinary):
//   - AVIF: imageUrl + '?f_auto,q_auto,w_<width>'
//   - WebP: imageUrl + '?f_webp,q_auto,w_<width>'
//   - JPEG: imageUrl + '?f_jpg,q_auto,w_<width>'
// Create <source> elements for each size (320w, 640w, 1024w) and each format (AVIF, WebP). Use the "sizes" attribute on the <img> tag to specify the image sizes for different screen widths.
// Ensure lazy loading is enabled using loading="lazy" on the <img> tag.
// Ensure error handling and fallback to placeholder.png (if cdn transformations fails).
// Keep dark factory color scheme (Tailwind CSS, slate-900, blue-500).
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- Verify in browser that AVIF images are served to supporting browsers.
- Verify in browser that WebP images are served to browsers that support WebP but not AVIF.
- Verify in browser that JPEG images are served to browsers that do not support AVIF or WebP.
- Verify that the placeholder image is displayed when the image URL is invalid.
- Inspect the `<picture>` element in the browser's developer tools to ensure that the `<source>` elements are correctly generated with the appropriate `srcset` attributes.
