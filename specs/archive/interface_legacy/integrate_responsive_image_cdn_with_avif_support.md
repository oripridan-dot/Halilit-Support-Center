# Spec: Integrate Responsive Image CDN with AVIF Support

**Target:** src/components/ResponsiveImage/ResponsiveImage.tsx

## Overview
This component provides a responsive image solution utilizing a CDN that supports AVIF image format. It automatically selects the appropriate image size based on the device's screen width and prioritizes AVIF format if supported by the browser, falling back to other formats like WebP or JPEG. The goal is to optimize image delivery for performance and visual quality.

## Requirements
- [x] The component should accept an `imagePath` prop representing the base path to the image on the CDN (e.g., `/images/products/my-image`).
- [x] The component should generate `srcset` attributes for `<img>` tag, including different sizes tailored for various screen widths: 320, 640, 960, 1280, and 1920 pixels.
- [x] The component must automatically detect browser support for AVIF format.
- [x] If AVIF is supported, the `srcset` should include AVIF versions of the image for each size.
- [x] If AVIF is not supported, the `srcset` should include WebP versions if supported, otherwise fallback to JPEG.
- [x] The component should apply lazy loading using the `loading="lazy"` attribute.
- [x] The component should include a `placeholder` prop, which is the file path to a low-resolution version of the image (e.g. `/images/products/my-image-placeholder.jpg`). This image should be displayed while the larger image loads.
- [x] The component must use Tailwind CSS for styling, targeting a dark theme with slate-900 background and blue-500 accents where applicable.
- [x] The component must include `alt` attribute with text that is passed via `altText` prop.
- [x] The component should handle cases where the requested image size does not exist on the CDN, defaulting to a smaller available size or displaying an error (see "Behavior Scenarios").
- [x] All CDN URLs should be constructed using HTTPS.

## Data Contract
```typescript
interface ResponsiveImageProps {
  imagePath: string; // Base path to the image on the CDN (e.g., /images/products/my-image)
  altText: string;  // Alt text for the image
  placeholder: string; // Base path to the low-resolution placeholder image.
  className?: string; // Optional CSS class names to apply to the image element.
}
```

## Behavior Scenarios
- **Scenario:** AVIF Support, Large Screen
  - Input: `imagePath="/images/products/product-1", altText="Product 1", placeholder="/images/products/product-1-placeholder.jpg"`, screen width: 1920px, browser supports AVIF.
  - Outcome: Renders an `<img>` tag with the following `srcset` attribute (line breaks added for readability):
    ```html
    <img
      src="/images/products/product-1-1920.avif"
      srcset="
        /images/products/product-1-320.avif 320w,
        /images/products/product-1-640.avif 640w,
        /images/products/product-1-960.avif 960w,
        /images/products/product-1-1280.avif 1280w,
        /images/products/product-1-1920.avif 1920w
      "
      alt="Product 1"
      loading="lazy"
      class="w-full h-auto object-cover bg-slate-900"
      style="background-image: url('/images/products/product-1-placeholder.jpg'); background-size: cover; background-position: center;"
    />
    ```
- **Scenario:** No AVIF Support, Medium Screen
  - Input: `imagePath="/images/products/product-1", altText="Product 1", placeholder="/images/products/product-1-placeholder.jpg"`, screen width: 960px, browser does NOT support AVIF, but supports WebP.
  - Outcome: Renders an `<img>` tag with the following `srcset` attribute:
    ```html
    <img
      src="/images/products/product-1-960.webp"
      srcset="
        /images/products/product-1-320.webp 320w,
        /images/products/product-1-640.webp 640w,
        /images/products/product-1-960.webp 960w,
        /images/products/product-1-1280.webp 1280w,
        /images/products/product-1-1920.webp 1920w
      "
      alt="Product 1"
      loading="lazy"
      class="w-full h-auto object-cover bg-slate-900"
      style="background-image: url('/images/products/product-1-placeholder.jpg'); background-size: cover; background-position: center;"
    />
    ```
- **Scenario:** No AVIF or WebP Support, Small Screen
  - Input: `imagePath="/images/products/product-1", altText="Product 1", placeholder="/images/products/product-1-placeholder.jpg"`, screen width: 320px, browser does NOT support AVIF or WebP.
  - Outcome: Renders an `<img>` tag with the following `srcset` attribute:
    ```html
    <img
      src="/images/products/product-1-320.jpg"
      srcset="
        /images/products/product-1-320.jpg 320w,
        /images/products/product-1-640.jpg 640w,
        /images/products/product-1-960.jpg 960w,
        /images/products/product-1-1280.jpg 1280w,
        /images/products/product-1-1920.jpg 1920w
      "
      alt="Product 1"
      loading="lazy"
      class="w-full h-auto object-cover bg-slate-900"
      style="background-image: url('/images/products/product-1-placeholder.jpg'); background-size: cover; background-position: center;"
    />
    ```
- **Scenario:** Image Size Not Available
  - Input: `imagePath="/images/products/product-1", altText="Product 1", placeholder="/images/products/product-1-placeholder.jpg"`, screen width: 1920px, browser supports AVIF, but `/images/products/product-1-1920.avif` does not exist on the CDN.
  - Outcome: The component should gracefully degrade by using the next smaller size available (e.g., 1280.avif) as the `src` and still include other sizes in the `srcset` (if available).  If *no* sizes are available, display a fallback image (e.g., from public/images/image-unavailable.png) and log an error to the console.
- **Scenario:** Placeholder Image
    - Input: `imagePath="/images/products/product-1", altText="Product 1", placeholder="/images/products/product-1-placeholder.jpg"`, screen width: 1920px, browser supports AVIF, Image loading.
    - Outcome: While the `src` image is loading, the image tag's `background-image` style should be set to the `placeholder` URL, and the `background-size` to `cover`.
- **Scenario:** Classname Passed
  - Input: `imagePath="/images/products/product-1", altText="Product 1", placeholder="/images/products/product-1-placeholder.jpg", className="my-custom-class"`, screen width: 1920px, browser supports AVIF.
  - Outcome: Renders an `<img>` tag that includes the provided classname:
    ```html
    <img
      src="/images/products/product-1-1920.avif"
      srcset=" ... "
      alt="Product 1"
      loading="lazy"
      class="w-full h-auto object-cover bg-slate-900 my-custom-class"
      style="background-image: url('/images/products/product-1-placeholder.jpg'); background-size: cover; background-position: center;"
    />
    ```

## Out of Scope
- [Image optimization (this is handled by the CDN).]
- [Error handling beyond console logging and displaying a default image.]
- [Advanced lazy loading configurations (e.g., using Intersection Observer API directly). `loading="lazy"` is sufficient.]
