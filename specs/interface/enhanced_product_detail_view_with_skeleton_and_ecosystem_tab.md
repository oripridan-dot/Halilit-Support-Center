# Spec: Enhanced Product Detail View with Skeleton and Ecosystem Tab
**Version:** 1.0
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## Purpose

Enhance the Product Detail View with a detailed skeleton UI while data is loading and display the Ecosystem Tab. This addresses the "Speed of Service" business goal by providing immediate feedback to the user and the "Maximize Attachment Rate" business goal by displaying related products and integrations.

## Requirements

1. **Replace Loading Spinner:** Replace the existing loading spinner with the `SkeletonProductDetail` component from `frontend/src/components/SkeletonProductDetail.tsx`.

2.  **Render Ecosystem Tab:** Integrate the `<EcosystemTab>` component into the `ProductDetailView`. Pass the `productId` to the `EcosystemTab` component.

3. **Conditional Rendering:**
    - Display the `SkeletonProductDetail` component while `isLoading` is true.
    - Display the actual product details and `<EcosystemTab>` only when `isLoading` is false, no `error`, and `product` is available.
    - Display error message when there is an `error`.
    - Display a "Product not found" message when `product` is not available.

4. **Layout and Styling:** Ensure the `SkeletonProductDetail` and `<EcosystemTab>` components are correctly styled and integrated into the overall layout of the `ProductDetailView`, maintaining the dark theme (slate-900 background, blue-500 accents).

5.  **Ecosystem Tab Placement:** Place the `<EcosystemTab>` component below the product information and image.

## Behavior Scenarios

1. **Scenario:** The Product Detail View is loading data.
    - **Input:** `isLoading` is `true`.
    - **Outcome:** The `SkeletonProductDetail` component is displayed. The loading spinner is no longer visible.

2. **Scenario:** The Product Detail View has loaded data successfully.
    - **Input:** `isLoading` is `false`, `error` is `null`, and `product` is defined.
    - **Outcome:** The product details (name, description, image) are displayed, and the `<EcosystemTab>` component is rendered, displaying related products and integrations.

3. **Scenario:** The Product Detail View encounters an error while loading data.
    - **Input:** `isLoading` is `false`, `error` is not `null`.
    - **Outcome:** The error message is displayed. The `SkeletonProductDetail` and `<EcosystemTab>` are not rendered.

4. **Scenario:** The Product Detail View cannot find the product.
    - **Input:** `isLoading` is `false`, `error` is `null`, and `product` is `undefined` or `null`.
    - **Outcome:** The "Product not found" message is displayed. The `SkeletonProductDetail` and `<EcosystemTab>` are not rendered.

## Stitch UI Prompt
```text
// Target Component: ProductDetailView
// Description: The main view for displaying detailed product information, including a skeleton loading state and an Ecosystem tab for related products and integrations.

// Layout:
// - Use a Grid layout with 2 columns on larger screens (lg:grid-cols-2) and 1 column on smaller screens (grid-cols-1).
// - The grid should have a gap of 6 (gap-6).
// - The main container should have a padding of 4 (p-4).

// Visual Style:
// - Background: slate-900 (bg-slate-900)
// - Minimum height: screen (min-h-screen)
// - Text color: white (text-white) for primary text, zinc-400 (text-zinc-400) for secondary text.
// - Use rounded corners (rounded-lg) and shadow (shadow-md) for image and card elements.
// - Maintain dark theme consistency using Tailwind CSS.

// Component Hierarchy:
// 1. Outer div (bg-slate-900, min-h-screen, pb-6)
// 2. ProductDetailHeader (fixed height, contains product name, stock status, and price information, needs a prop called `product`)
// 3. Grid container (mx-auto, p-4, grid grid-cols-1 lg:grid-cols-2, gap-6)
// 4.  Inside the grid container:
//     - Column 1 (lg:col-span-1): Contains ImageWithFallback (rounded-lg)
//     - Column 2 (lg:col-span-1): Contains product information (name, description,JITBadge)
//     - EcosystemTab (lg:col-span-2): A tab component to display related products and integrations

// Data Slots:
// 1. `productName`: The name of the product (string).
// 2. `productImage`: URL of the main product image (string).
// 3. `productDescription`: A brief description of the product (string).
// 4.  `relatedProducts`: A JSON array of related products with each object having at least: id, name, image_url
// 5.  `integrations`: A JSON array of integrations with each object having at least: id, name, logo_url, description

// Skeleton State:
// - If isLoading is true, render the SkeletonProductDetail component instead of the product details and EcosystemTab.
// - The SkeletonProductDetail component provides a visual representation of the layout while the data is loading (components/SkeletonProductDetail.tsx).

// Empty State:
// - If product is null/undefined, display a message stating "Product not found."

// Error State:
// - If error is not null, display a red banner with an error message.

// Responsive Behavior:
// - On larger screens (lg:), use a two-column layout.
// - On smaller screens, use a single-column layout.

// Spacing:
// - Use margin (m*) and padding (p*) utilities from Tailwind CSS to control spacing between elements. For example, use mb-4 for spacing below the product title.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
