# Spec: Integrate Responsive Image CDN with AVIF Support

**Version:** 1.0
**Component:** `frontend/src/components/ImageWithFallback.tsx`

## Purpose
To enhance the `ImageWithFallback` component by integrating a responsive image CDN with AVIF support, improving image loading performance, reducing bandwidth consumption, and ensuring optimal image quality across different devices and browsers. This directly addresses the "Zero Broken Images" and "Speed of Service" business goals.

## Requirements
1. **CDN Integration:** Integrate with a responsive image CDN (e.g., Cloudinary, Imgix, or similar). Assume the CDN can transform images to AVIF format and generate responsive versions based on device characteristics via URL parameters. The exact URL parameters will depend on the chosen CDN (e.g. Cloudinary: `f_auto,q_auto` for format and quality). Use a placeholder CDN URL `https://cdn.example.com`.
2. **AVIF Support:** The component must prioritize AVIF format when the browser supports it. The CDN should automatically serve AVIF images to supporting browsers via content negotiation (Accept header).
3. **Responsive Images:** Generate responsive image URLs using the CDN to serve appropriately sized images based on the device's screen size and pixel density. Use the `<picture>` element with `<source>` elements for different image formats and sizes. Create three sizes: small (320w), medium (640w), and large (1024w).
4. **Fallback Mechanism:** If the browser doesn't support AVIF or the CDN fails to deliver an AVIF image, the component must fall back to WebP and then to JPEG. Ensure the `<img>` tag includes a `src` attribute with a fallback image URL.
5. **Placeholder Image:** If the `imageUrl` is missing, null, an empty string, or if all CDN transformations fail, the component must display a dark placeholder image (`/placeholder.png` or an inline SVG).
6. **Error Handling:** The component must gracefully handle CDN errors and network issues, displaying the placeholder image if necessary.
7. **Lazy Loading:** Implement lazy loading using the `loading="lazy"` attribute on the `<img>` tag.
8. **Existing Functionality:** Preserve the existing fallback image and error handling functionality of the `ImageWithFallback` component.
9. **TypeScript:** Ensure the component is correctly typed using TypeScript.

## Behavior Scenarios

1. **Scenario:** Browser supports AVIF, and the CDN delivers an AVIF image.
    *   **Outcome:** The browser displays the AVIF image. The network request shows that the CDN served the AVIF image.
2. **Scenario:** Browser does not support AVIF, and the CDN delivers a WebP image.
    *   **Outcome:** The browser displays the WebP image. The network request shows that the CDN served the WebP image.
3. **Scenario:** Browser does not support AVIF or WebP, and the CDN delivers a JPEG image.
    *   **Outcome:** The browser displays the JPEG image. The network request shows that the CDN served the JPEG image.
4. **Scenario:** The CDN returns an error for all image formats.
    *   **Outcome:** The placeholder image is displayed.
5. **Scenario:** The `imageUrl` prop is `null`, `undefined`, or an empty string.
    *   **Outcome:** The placeholder image is displayed.
6. **Scenario:** The image is below the fold and lazy loading is enabled.
    *   **Outcome:** The image is not loaded until it scrolls into the viewport.

## Stitch UI Prompt
```text
// Target Component: ImageWithFallback
// Description: A React component that displays an image with responsive sizes, AVIF support via CDN, and a fallback placeholder.
// Layout:  Uses a <picture> element with <source> elements for different image formats and sizes.  The <img> tag provides a final fallback.
// Style: Dark mode, Tailwind CSS. Use slate-900 for background.
// Data Slots:
//   - imageUrl:  The base image URL.  Assume a CDN will transform this URL.
//   - altText:   The alt text for the image.
//   - placeholderImageUrl: The URL for a dark placeholder image.

// Component Hierarchy:
//  <picture>
//    <source srcset="CDN_URL?width=320&format=avif CDN_URL?width=640&format=avif 2x, CDN_URL?width=1024&format=avif 3x" type="image/avif">
//    <source srcset="CDN_URL?width=320&format=webp CDN_URL?width=640&format=webp 2x, CDN_URL?width=1024&format=webp 3x" type="image/webp">
//    <img src="CDN_URL?width=640&format=jpeg" alt="{altText}" loading="lazy" class="rounded-md object-cover w-full h-full" onError="this.src='{placeholderImageUrl}'">
//  </picture>

// Instructions:
//  1. Use Tailwind CSS classes for styling.
//  2. Ensure the component handles loading states and errors gracefully.
//  3. The <img> tag must have an onError handler that sets the src to the placeholder image.
//  4. Replace CDN_URL with a placeholder CDN URL like "https://cdn.example.com/{imageUrl}".
//  5. The component should be responsive and adapt to different screen sizes.

// Example values for data slots:
//  imageUrl: "products/guitar.jpg"
//  altText: "Electric Guitar"
//  placeholderImageUrl: "/placeholder.png"

// Spacing: No specific spacing requirements, but ensure the image fits well within its container.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
