# Spec: ImageWithFallback Component — Lazy Loading

**Version:** 1.1
**Component:** `frontend/src/components/ImageWithFallback.tsx`

## 1. Purpose

Enhance the `ImageWithFallback` component by adding lazy loading to improve initial page load performance, especially for views with numerous product images (e.g., InventoryView). This directly contributes to the "Speed of Service" business goal by reducing the initial load time.

## 2. Requirements

1.  **Lazy Loading Attribute:** Add the `loading="lazy"` attribute to the `<img>` tag within the `ImageWithFallback` component.
2.  **Lazy Loading Threshold:** Images that are initially visible in the viewport should load immediately. Images below the fold should be lazy-loaded.
3.  **Placeholder Styling:** Maintain the existing placeholder image styling to prevent layout shifts during lazy loading.
4.  **Existing Functionality:** Preserve the existing fallback image and error handling functionality of the `ImageWithFallback` component.
5.  **TypeScript:** Ensure the component is correctly typed using TypeScript.

## 3. Behavior Scenarios

1.  **Scenario:** The `ImageWithFallback` component is used to display an image that is initially below the viewport.
    *   **Outcome:** The image is not loaded until it scrolls into the viewport (or is close enough to the viewport to trigger the browser's lazy loading threshold).
2.  **Scenario:** The `ImageWithFallback` component is used to display an image that is initially visible in the viewport.
    *   **Outcome:** The image is loaded immediately.
3.  **Scenario:** The `imageUrl` prop is `null`, `undefined`, or an empty string.
    *   **Outcome:** The placeholder image is displayed, and lazy loading is not applied.
4.  **Scenario:** The `imageUrl` is a valid URL but the image fails to load.
    *   **Outcome:** The placeholder image is displayed, and lazy loading is not applied.

## Stitch UI Prompt
```text
// Target Component: ImageWithFallback
// Description:  A React component that displays an image with a fallback placeholder and lazy loading.

// Layout:  None (This is a single image element, so no specific layout is needed).

// Visual Style: Dark Mode
// * Background: slate-900 (Tailwind CSS)
// * Text Color: gray-300 (Tailwind CSS)
// * Placeholder Background: gray-800 (Tailwind CSS)

// Data Slots:
// 1. imageUrl:  The URL of the image to display.  Placeholder: "https://example.com/image.jpg"
// 2. altText:   The alt text for the image. Placeholder: "Product Image"

// Component Hierarchy:
// * The component consists of a single `img` element.
// * The `img` element should have `loading="lazy"` to enable lazy loading.
// * The `img` element should use a placeholder image as the `src` initially (e.g., "/placeholder.png").  This will be replaced by the `imageUrl` if it loads successfully.
// * An `onError` handler on the `img` element should set the `src` to the placeholder image if the `imageUrl` fails to load.
// * The `img` element should have `alt` attribute set to the value provided in altText.

// Spacing: None

// Tailwind CSS:
// * Placeholder: `bg-gray-800`
// * Image: `object-cover w-full h-full`  (adjust w-full and h-full as necessary for the container)

// Generate a React component with Typescript that implements the ImageWithFallback component.
// Ensure that:
//   - Image has `loading="lazy"` attribute.
//   - onError handler correctly sets the src to "/placeholder.png".
//   - altText is applied to the `alt` attribute.
//   - The placeholder image is used when imageUrl is null/undefined/empty or when the image fails to load.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
