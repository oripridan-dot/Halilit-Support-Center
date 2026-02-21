# Spec: Responsive Image Component
**Target:** src/components/ResponsiveImage.tsx

## Overview
This React component displays an image that adapts to different screen sizes by utilizing the `srcset` attribute of the `<img>` tag. It takes a base image URL and a set of size-specific URLs as input, optimizing image delivery for various devices and network conditions, improving page load times and user experience.

## Requirements
- The component must accept a `baseUrl` prop (string, required) that serves as the base URL for all images, and from which full URLs will be derived.
- The component must accept a `sizes` prop (object, required) which is a mapping of screen size breakpoints (in pixels) to image path extensions.  Keys of the sizes object represent `max-width` media queries.
- The component must accept an `alt` prop (string, required) for accessibility.
- The component must accept a `className` prop (string, optional) for custom styling using Tailwind CSS.
- The component must generate the `srcset` attribute based on the provided `sizes` prop.
- The component must render an `<img>` tag with the calculated `srcset`, `alt`, and `className` attributes.
- The component must use the `baseUrl` and `sizes` prop to create the URLs for the `srcset` attribute.
- The component should use a default `sizes` attribute of `(max-width: 768px) 100vw, 50vw` for the `img` tag. This can be overriden using the `sizesAttr` prop (string, optional).
- The component should leverage Tailwind CSS for dark theme styling.

## Data Contract

**Props:**

```typescript
interface ResponsiveImageProps {
  baseUrl: string; // Base URL of the images (e.g., "https://example.com/images/")
  sizes: { [key: number]: string }; // Object mapping screen size (max-width) to image extensions (e.g., `{ 768: "small.jpg", 1200: "medium.jpg", 1920: "large.jpg" }`)
  alt: string; // Alt text for the image
  className?: string; // Optional Tailwind CSS class names
  sizesAttr?: string; // Optional sizes attribute for the img tag. Default is `(max-width: 768px) 100vw, 50vw`.
}
```

## Behavior Scenarios

- **Scenario:** Basic Usage
  - Input: `baseUrl="https://example.com/images/", sizes={768: "small.jpg", 1200: "medium.jpg", 1920: "large.jpg"}, alt="Example Image", className="rounded-md"`
  - Outcome: Renders an `<img>` tag with `src` of `https://example.com/images/small.jpg` (smallest size), `srcset` of `"https://example.com/images/small.jpg 768w, https://example.com/images/medium.jpg 1200w, https://example.com/images/large.jpg 1920w"`, `alt="Example Image"`, `className="rounded-md"`, and `sizes="(max-width: 768px) 100vw, 50vw"`

- **Scenario:** No className
  - Input: `baseUrl="https://example.com/images/", sizes={768: "small.jpg", 1200: "medium.jpg"}, alt="Another Image"`
  - Outcome: Renders an `<img>` tag with `srcset` of `"https://example.com/images/small.jpg 768w, https://example.com/images/medium.jpg 1200w"`, `alt="Another Image"`, and no additional classes.

- **Scenario:** Empty sizes object
    - Input: `baseUrl="https://example.com/images/", sizes={}, alt="Empty Sizes"`
    - Outcome: Renders an `<img>` tag with `srcset=""`, `alt="Empty Sizes"`, and the `src` attribute should be `baseUrl` joined with the smallest image, or empty string if there are no sizes specified. It should also still render.

- **Scenario:** Custom Sizes Attribute
    - Input: `baseUrl="https://example.com/images/", sizes={768: "small.jpg", 1200: "medium.jpg"}, alt="Custom Sizes", sizesAttr="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 33vw"`
    - Outcome: Renders an `<img>` tag with `srcset` of `"https://example.com/images/small.jpg 768w, https://example.com/images/medium.jpg 1200w"`, `alt="Custom Sizes"`, and `sizes="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 33vw"`.

- **Scenario:** Dark Mode Styling
  - Input: `baseUrl="https://example.com/images/", sizes={768: "small.jpg"}, alt="Dark Image", className="bg-slate-900 text-blue-500"`
  - Outcome: Renders an `<img>` tag with the provided class names and inherits the dark mode styling specified by Tailwind CSS (assuming dark mode is enabled at the application level).

## Out of Scope
- Image optimization techniques beyond `srcset` (e.g., using `<picture>` element with different image formats).
- Lazy loading of images.
- Error handling for image loading failures.
- Image CDN integration.
