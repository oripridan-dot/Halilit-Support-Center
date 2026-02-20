# Spec: ProductImage - ImageWithFallback Component

**Version:** 1.0
**Component:** `frontend/src/components/ImageWithFallback.tsx`

## 1. Purpose

To create a reusable component that handles image loading and gracefully falls back to a placeholder image in case of errors or missing URLs. This directly addresses the "Zero Broken Images" business goal. The component provides a consistent way to display images throughout the application, ensuring that no broken image links are ever displayed.

## 2. Requirements

1.  **imageUrl Prop:** The component MUST accept an `imageUrl` prop of type `string | undefined | null`.
2.  **altText Prop:** The component MUST accept an optional `altText` prop of type `string`. If no `altText` is provided, a default alt text, such as "Product Image" should be used.
3.  **Placeholder Image:** If `imageUrl` is `null`, `undefined`, or an empty string, the component MUST display a placeholder image. The placeholder image MUST be a dark, professional-looking image, either served from `/placeholder.png` or an inline SVG.
4.  **Error Handling:** If the `imageUrl` is a valid URL but the image fails to load (e.g., due to a network error or a 404), the component MUST display the same placeholder image.
5.  **Aspect Ratio:** The placeholder image MUST maintain the aspect ratio of the intended image to prevent layout shifting. This can be achieved using CSS.
6.  **onError Handler:** The `<img>` tag MUST have an `onError` handler that sets the image source to the placeholder image.
7.  **Styling:** The component MUST be styled using Tailwind CSS to fit seamlessly into the dark theme of the Halilit Support Center (slate-900 background, blue-500 accents).
8. **Lazy Loading:** Enable lazy loading for images to improve performance.
9. **Data Trust Integration:** (Optional) If `dataTrust` prop is passed, the `altText` should be automatically updated to include data source attributions.

## 3. Behavior Scenarios

1.  **Scenario:** `imageUrl` is a valid URL and the image loads successfully.
    *   **Input:** `imageUrl = "https://example.com/valid-image.jpg"`, `altText = "Product A"`
    *   **Outcome:** The image from `https://example.com/valid-image.jpg` is displayed with `alt="Product A"`.
2.  **Scenario:** `imageUrl` is `null`.
    *   **Input:** `imageUrl = null`, `altText = "Product B"`
    *   **Outcome:** The placeholder image is displayed with `alt="Product B"`.
3.  **Scenario:** `imageUrl` is `undefined`.
    *   **Input:** `imageUrl = undefined`, `altText = "Product C"`
    *   **Outcome:** The placeholder image is displayed with `alt="Product C"`.
4.  **Scenario:** `imageUrl` is an empty string.
    *   **Input:** `imageUrl = ""`, `altText = "Product D"`
    *   **Outcome:** The placeholder image is displayed with `alt="Product D"`.
5.  **Scenario:** `imageUrl` is a valid URL, but the image fails to load.
    *   **Input:** `imageUrl = "https://example.com/broken-image.jpg"`, `altText = "Product E"` (where `https://example.com/broken-image.jpg` returns a 404 error)
    *   **Outcome:** The placeholder image is displayed with `alt="Product E"`.
6.  **Scenario:** No `altText` provided.
    *   **Input:** `imageUrl = "https://example.com/valid-image.jpg"`, `altText = undefined`
    *   **Outcome:** The image from `https://example.com/valid-image.jpg` is displayed with `alt="Product Image"`.

## Stitch UI Prompt

You are an expert React/Tailwind developer. Generate the complete code for a React component called `ImageWithFallback` in `frontend/src/components/ImageWithFallback.tsx`.
It must satisfy these requirements:

1.  **imageUrl Prop:** The component accepts an `imageUrl` prop of type `string | undefined | null`.
2.  **altText Prop:** The component accepts an optional `altText` prop of type `string`. If no `altText` is provided, default to "Product Image".
3.  **Placeholder Image:** If `imageUrl` is `null`, `undefined`, or an empty string, the component displays a placeholder image served from `/placeholder.png`. Use the public directory, so the placeholder is accessible directly.
4.  **Error Handling:** If the `imageUrl` is a valid URL but the image fails to load (e.g., due to a network error or a 404), the component displays the placeholder image.
5.  **Aspect Ratio:** The placeholder image maintains the aspect ratio of the intended image to prevent layout shifting. Use CSS to define `object-fit: contain;`
6.  **onError Handler:** The `<img>` tag has an `onError` handler that sets the image source to `/placeholder.png` if the image fails to load.
7.  **Styling:** The component is styled using Tailwind CSS to fit seamlessly into the dark theme of the Halilit Support Center (slate-900 background, blue-500 accents).
8.  **Lazy Loading:** Enable lazy loading for images to improve performance, add `loading="lazy"` attribute.

The layout is a simple `<img>` tag wrapped in a `<div>`.
Use a `slate-900` background for the container.

```tsx
import React from 'react';

interface ImageWithFallbackProps {
    imageUrl: string | undefined | null;
    altText?: string;
}

const ImageWithFallback: React.FC<ImageWithFallbackProps> = ({ imageUrl, altText }) => {
    const defaultAltText = altText || "Product Image";

    return (
        <div className="bg-slate-900">
            <img
                src={imageUrl || "/placeholder.png"}
                alt={defaultAltText}
                onError={(e) => {
                    (e.target as HTMLImageElement).src = "/placeholder.png";
                }}
                className="object-contain"
                loading="lazy"
            />
        </div>
    );
};

export default ImageWithFallback;
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
