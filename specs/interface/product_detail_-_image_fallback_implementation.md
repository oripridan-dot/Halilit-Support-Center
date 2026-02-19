# Spec: Product Detail - Image Fallback Implementation

**Version:** 1.0
**Component:** `frontend/src/components/ProductImage.tsx`

## 1. Purpose

To provide a reusable component for displaying product images with a robust fallback mechanism, ensuring that no broken image links appear on the Product Detail View or in Product Tiles. This directly addresses the "Zero Broken Images" business goal. This uses the previously defined `useValidateHeroImage` hook to cache bad image URLs.

## 2. Requirements

1.  **Reusable Component:** Create a new React component named `ProductImage` (located at `frontend/src/components/ProductImage.tsx`).
2.  **Props:** The `ProductImage` component MUST accept the following props:
    *   `src: string | undefined | null`: The URL of the image to display.
    *   `alt: string`: The alt text for the image. This is required for accessibility.
    *   `className?: string`: Optional Tailwind CSS class names for styling the image.
    * `isHero?: boolean`: Optional boolean indicating if this is a hero image; defaults to false.
3.  **Image Validation (Hero Image):** If `isHero` is true, the component MUST use the `useValidateHeroImage(src)` hook to determine if the image URL is valid.  The hook's results (`isValidating`, `isValid`) are used for rendering.
4. **Conditional Rendering Based on Validation:**
    * If `isHero` is true and `isValidating` is true, display a loading skeleton (e.g., a shimmering rectangle with the same dimensions as the eventual image).
    * If `isHero` is true and `isValid` is `false` or `src` is falsy, render the fallback image.
    * If `isHero` is true and `isValid` is `true`, or `isHero` is false, proceed with standard image rendering with fallback.
5.  **Fallback Image:** If the `src` prop is missing, null, or an empty string, or if `isHero` is false and the image fails to load (onError), the component MUST display a dark placeholder image (`/placeholder.png`).
6.  **onError Handler:** The `<img>` tag MUST have an `onError` handler that sets the image source to `/placeholder.png` if the image fails to load, and `isHero` is false. If `isHero` is true, the hook already handles the invalidation and fallback.
7.  **Alt Text:** The `<img>` tag MUST always have an `alt` attribute. The value of the `alt` attribute MUST be the value of the `alt` prop passed to the component.
8.  **Styling:** The component MUST accept a `className` prop to allow for flexible styling using Tailwind CSS. The `className` prop MUST be applied to the `<img>` tag.
9. **Placeholder Styling:** The placeholder image MUST maintain the aspect ratio of the original image to prevent layout distortion. If using an inline SVG, the SVG MUST be styled to have a dark background.
10. **Usage in ProductTile and ProductDetailView:** Replace all direct usages of `<img>` tags for product images in `ProductTile.tsx` and `ProductDetailView.tsx` with the `<ProductImage>` component. When rendering the main product image in `ProductDetailView.tsx`, set `isHero` to `true`.

## 3. Behavior Scenarios

1.  **Scenario:** The `ProductImage` component is used in a `ProductTile` with a valid `src` prop.
    *   **Outcome:** The image is displayed.
2.  **Scenario:** The `ProductImage` component is used in a `ProductTile` with a missing `src` prop.
    *   **Outcome:** The `/placeholder.png` image is displayed.
3.  **Scenario:** The `ProductImage` component is used in a `ProductTile` with a `src` prop that points to a broken image.
    *   **Outcome:** Initially, the broken image might be attempted, then the `onError` handler triggers and the `/placeholder.png` image is displayed.
4.  **Scenario:** The `ProductImage` component is used in `ProductDetailView` with `isHero` set to `true` and the `src` prop is a valid image URL.
    *   **Outcome:** The image is displayed after validation.
5.  **Scenario:** The `ProductImage` component is used in `ProductDetailView` with `isHero` set to `true` and the `src` prop is an invalid image URL.
    *   **Outcome:** The `useValidateHeroImage` hook returns `isValid: false`, and the `/placeholder.png` image is displayed. The image URL is cached as invalid.
6. **Scenario:** The `ProductImage` component is used in `ProductDetailView` with `isHero` set to `true` and the `src` prop is being validated.
    * **Outcome:** A loading skeleton is displayed.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
