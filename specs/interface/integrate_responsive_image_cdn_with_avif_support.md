# Spec: Integrate Responsive Image CDN with AVIF Support

**Version:** 1.1
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
7. **Lazy Loading:** Implement lazy loading for images (already present, ensure it remains functional).
8. **TypeScript:** Ensure the component is correctly typed using TypeScript.
9. **Alt Text:** Ensure `altText` prop is correctly passed to the `<img>` tag.

## Behavior Scenarios
1. **Scenario:** Browser supports AVIF, CDN delivers AVIF image.
   - **Input:** `imageUrl` is a valid URL. The browser sends an Accept header including `image/avif`. The CDN serves an AVIF image.
   - **Outcome:** The component displays the AVIF image. The network request shows the image served as AVIF.
2. **Scenario:** Browser doesn't support AVIF, CDN delivers WebP image.
   - **Input:** `imageUrl` is a valid URL. The browser doesn't send an Accept header including `image/avif`. The CDN serves a WebP image.
   - **Outcome:** The component displays the WebP image. The network request shows the image served as WebP.
3. **Scenario:** `imageUrl` is null/undefined, Placeholder image is displayed.
   - **Input:** `imageUrl` is null or undefined.
   - **Outcome:** The component displays the placeholder image (`/placeholder.png` or inline SVG). No CDN requests are made.
4. **Scenario:** CDN returns an error, Placeholder image is displayed.
   - **Input:** `imageUrl` is a valid URL, but the CDN returns a 500 error or a 404.
   - **Outcome:** The component displays the placeholder image.
5. **Scenario:** Lazy loading is enabled, image is below the fold.
   - **Input:** `imageUrl` is valid and the image is initially below the fold.
   - **Outcome:** The image is not loaded until it is scrolled into view.

## Stitch UI Prompt

```
// Target Component: ImageWithFallback
// Description: A React component that displays an image with responsive sizes, AVIF support, and a fallback image.
// Style: Dark mode, Tailwind CSS, slate-900 background, blue-500 accents.

// Layout:
// - The component uses a <picture> element to provide multiple image sources.
// - Inside the <picture> element, use <source> elements for different image formats (AVIF, WebP, JPEG) and sizes (small, medium, large).
// - The <img> tag is used as a fallback for browsers that don't support the <picture> element.

// Visual Style:
// - Use Tailwind CSS classes to style the images and the fallback placeholder.
// - Use a dark placeholder image (e.g., /placeholder.png) with a dark background.
// - Ensure proper aspect ratio for the images and the placeholder.

// Data Slots:
// - imageUrl: The base URL of the image (string).  This will be transformed by the CDN.
// - altText: The alt text for the image (string).

// Component Hierarchy:
// <picture>
//   <source srcset="[CDN URL for small AVIF]" type="image/avif" media="(max-width: 320px)" />
//   <source srcset="[CDN URL for medium AVIF]" type="image/avif" media="(max-width: 640px)" />
//   <source srcset="[CDN URL for large AVIF]" type="image/avif" media="(min-width: 641px)" />
//   <source srcset="[CDN URL for small WebP]" type="image/webp" media="(max-width: 320px)" />
//   <source srcset="[CDN URL for medium WebP]" type="image/webp" media="(max-width: 640px)" />
//   <source srcset="[CDN URL for large WebP]" type="image/webp" media="(min-width: 641px)" />
//   <img
//     src="[CDN URL for JPEG fallback]"
//     alt="{altText}"
//     loading="lazy"
//     className="w-full h-full object-cover"
//     onError={(e) => (e.target.src = '/placeholder.png')}
//   />
// </picture>

// Spacing: No specific spacing requirements, component should fit within its container.
// Example CDN URLs (replace with actual CDN parameters):
// - Small AVIF: https://cdn.example.com/{imageUrl}?width=320&format=avif&quality=auto
// - Medium AVIF: https://cdn.example.com/{imageUrl}?width=640&format=avif&quality=auto
// - Large AVIF: https://cdn.example.com/{imageUrl}?width=1024&format=avif&quality=auto
// - Small WebP: https://cdn.example.com/{imageUrl}?width=320&format=webp&quality=auto
// - Medium WebP: https://cdn.example.com/{imageUrl}?width=640&format=webp&quality=auto
// - Large WebP: https://cdn.example.com/{imageUrl}?width=1024&format=webp&quality=auto
// - JPEG Fallback: https://cdn.example.com/{imageUrl}?width=1024&format=jpg&quality=auto
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
