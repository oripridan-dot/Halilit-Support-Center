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
6. **Error Handling:** The component must gracefully handle CDN errors and network issues, displaying the placeholder image if necessary. Log errors for monitoring.
7. **Lazy Loading:** Maintain lazy loading functionality as defined in existing `ImageWithFallback` spec.
8. **Typescript:** Ensure the component is correctly typed using Typescript.

## Behavior Scenarios

1. **Scenario:** Browser supports AVIF, CDN is available.
    - Input: `imageUrl` is a valid URL.
    - Outcome: The component displays the AVIF image served from the CDN, with responsive sizing applied.
2. **Scenario:** Browser does not support AVIF, CDN is available.
    - Input: `imageUrl` is a valid URL.
    - Outcome: The component displays the WebP or JPEG image served from the CDN, with responsive sizing applied.
3. **Scenario:** CDN is unavailable.
    - Input: `imageUrl` is a valid URL.
    - Outcome: The component displays the placeholder image. Error is logged.
4. **Scenario:** `imageUrl` is missing, null, or an empty string.
    - Input: `imageUrl` is null.
    - Outcome: The component displays the placeholder image.
5. **Scenario:** Image loading fails after CDN transformation.
    - Input: CDN returns an error for the transformed image.
    - Outcome: The component displays the placeholder image. Error is logged.
6. **Scenario:** Lazy loading enabled, image below the fold.
    - Input: `imageUrl` is a valid URL, image is below the fold.
    - Outcome: Image is not loaded until it is scrolled into view. AVIF/WebP/JPEG and responsive sizing are applied when loaded.

## Stitch UI Prompt
```text
// Target Component: ImageWithFallback
// Description:  A React component that displays an image with responsive sizing, AVIF support, and a fallback placeholder.

// Layout: Use a <picture> element with <source> elements for different image formats and sizes, and an <img> tag for the fallback.
// Style: Dark mode, Tailwind CSS, slate-900 background for the placeholder, blue-500 accents for loading indicators (if any).
// Responsiveness: Use breakpoints for small (320w), medium (640w), and large (1024w) screens.

// Data Slots:
//   - imageUrl: string (The base image URL)
//   - altText: string (The alt text for the image)
//   - placeholderImageUrl: string (URL for the dark placeholder image, default: /placeholder.png)

// Component Hierarchy:
// <picture>
//   <source srcset="[CDN URL for AVIF, small]" type="image/avif" media="(max-width: 320px)" />
//   <source srcset="[CDN URL for AVIF, medium]" type="image/avif" media="(max-width: 640px)" />
//   <source srcset="[CDN URL for AVIF, large]" type="image/avif" media="(min-width: 641px)" />
//   <source srcset="[CDN URL for WebP, small]" type="image/webp" media="(max-width: 320px)" />
//   <source srcset="[CDN URL for WebP, medium]" type="image/webp" media="(max-width: 640px)" />
//   <source srcset="[CDN URL for WebP, large]" type="image/webp" media="(min-width: 641px)" />
//   <img src="[CDN URL for JPEG, medium]" alt="[altText]" loading="lazy" className="object-cover w-full h-full" onError="this.src='[placeholderImageUrl]'" />
// </picture>

// Tailwind CSS:
//  - object-cover: Ensures the image covers the entire container.
//  - w-full: Makes the image take up the full width of its container.
//  - h-full: Makes the image take up the full height of its container.

// CDN URL Transformation Example (Cloudinary):
//  - [imageUrl]?f_auto,q_auto,w_320   (AVIF, auto quality, 320px width)
//  - [imageUrl]?f_auto,q_auto,w_640   (AVIF, auto quality, 640px width)
//  - [imageUrl]?f_auto,q_auto,w_1024  (AVIF, auto quality, 1024px width)

// Use the following Tailwind CSS color tokens from the Halilit Operator Console:
// - Background: slate-900
// - Accents: blue-500
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
