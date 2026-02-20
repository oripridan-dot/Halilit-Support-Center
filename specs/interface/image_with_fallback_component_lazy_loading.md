# Spec: Image with Fallback Component & Lazy Loading

**Target:** `src/components/ImageWithFallback.tsx`

## Overview
This React component displays an image from a given URL. If the image fails to load, it displays a fallback image. The component implements lazy loading for improved performance, delaying the loading of images until they are near the viewport.

## Requirements
- The component must accept `src`, `alt`, and `fallbackSrc` props.
- The component must implement lazy loading using the `loading="lazy"` attribute.
- If the primary image fails to load, the fallback image should be displayed.
- The component must maintain aspect ratio while images are loading and when fallback is visible.
- The component must use Tailwind CSS for styling, adhering to the dark theme (slate-900 for background and blue-500 for accents).
- The component should accept arbitrary HTML attributes like `className`, `width`, `height` etc and apply them to the `img` tag.
- The component should be written in TypeScript.

## Data Contract

**Props:**

```typescript
interface ImageWithFallbackProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  alt: string;
  fallbackSrc: string;
  className?: string; // Allow overriding default styles
}
```

## Behavior Scenarios

- **Scenario:** Successful Image Load
  - Input: `src` points to a valid image URL, `alt` is "Example Image", `fallbackSrc` is "fallback.png".
  - Outcome: The image from `src` is displayed with the provided `alt` text.  The fallback image is not displayed. Lazy loading is enabled.

- **Scenario:** Image Load Failure, Fallback Available
  - Input: `src` points to an invalid image URL, `alt` is "Example Image", `fallbackSrc` is "fallback.png".
  - Outcome: The image from `fallbackSrc` is displayed with the provided `alt` text (or a modified alt "Example Image (Fallback)"). The primary image is not displayed. Lazy loading is enabled.

- **Scenario:** Image Load Failure, No Fallback Available (fallbackSrc is an empty string)
  - Input: `src` points to an invalid image URL, `alt` is "Example Image", `fallbackSrc` is "".
  - Outcome: An error icon (e.g., a broken image icon) is displayed instead of the image, with the `alt` text "Example Image (Error)". The primary image and blank fallback image are not displayed. Lazy loading is enabled. The error icon should be styled to fit the aspect ratio of the intended image.

- **Scenario:** Lazy Loading
  - Input: The component is rendered off-screen initially. `src` points to a valid image URL, `alt` is "Example Image", `fallbackSrc` is "fallback.png".
  - Outcome: The image is not loaded until the component is scrolled into or near the viewport. Once visible or nearly visible, the image loads and is displayed.

- **Scenario:** Custom Styling
    - Input: `src` points to a valid image URL, `alt` is "Example Image", `fallbackSrc` is "fallback.png", `className` is "w-32 h-32 rounded-full".
    - Outcome: The image is displayed with the specified width, height, and rounded corners.

## Out of Scope
- Image optimization (e.g., resizing, format conversion).
- Advanced error handling (e.g., logging image load failures).
- Server-side rendering (SSR) specific considerations beyond basic compatibility.
