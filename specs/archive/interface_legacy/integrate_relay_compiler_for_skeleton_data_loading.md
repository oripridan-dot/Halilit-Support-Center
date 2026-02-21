# Spec: Integrate Relay Compiler for Skeleton Data Loading

**Version:** 1.0
**Component:** `frontend/src/components/SkeletonProductDetail.tsx`

## Purpose

To improve the perceived performance of the Product Detail View by displaying a detailed skeleton UI while data is loading. This will replace the current simple loading spinner with a more visually informative placeholder, addressing the "Speed of Service" business goal by providing immediate feedback to the user. The skeleton UI will be implemented using Tailwind CSS and styled to match the dark theme. Relay Compiler will be evaluated for generating type-safe skeleton data and components.

## Requirements

1. **Skeleton Component:** Create a new component `frontend/src/components/SkeletonProductDetail.tsx` that renders a skeleton UI for the Product Detail View.

2. **Skeleton UI Structure:** The skeleton UI should mimic the structure of the actual Product Detail View, including placeholders for:
    - Hero image
    - Product title
    - Brand
    - Price
    - Description
    - Ecosystem Tab content (Related Products and Integrations)

3. **Skeleton Styling:** Use Tailwind CSS to style the skeleton UI, adhering to the dark theme (slate-900 background, blue-500 accents, zinc-700 placeholders). The skeleton elements should use subtle animations (e.g., a shimmering effect) to indicate that data is loading.

4. **Relay Compiler Evaluation:** Evaluate the feasibility and benefits of using Relay Compiler to generate the skeleton component and associated data types based on a GraphQL schema. If Relay Compiler proves to be a viable solution:
    - Define a GraphQL schema that describes the structure of the product data.
    - Configure Relay Compiler to generate TypeScript code from the schema, including type-safe skeleton data.
    - Integrate the generated code into the `SkeletonProductDetail.tsx` component.

5. **Integration with ProductDetailView:** Modify `frontend/src/components/views/ProductDetailView.tsx` to render the `SkeletonProductDetail` component while the product data is loading (i.e., when `isLoading` is true).

6. **Placeholder Data (if Relay is not used):** If Relay Compiler is not used, create placeholder data with similar shape as `ConductorProduct` to generate component.

7. **Performance:** The skeleton MUST render within 200ms.

## Behavior Scenarios

1. **Scenario:** The Product Detail View is loading data.
    - **Input:** `isLoading` is true in `frontend/src/components/views/ProductDetailView.tsx`.
    - **Outcome:** The `SkeletonProductDetail` component is displayed, showing a skeleton UI with placeholders for the product information.

2. **Scenario:** The Product Detail View has finished loading data.
    - **Input:** `isLoading` is false in `frontend/src/components/views/ProductDetailView.tsx`.
    - **Outcome:** The `SkeletonProductDetail` component is no longer displayed, and the actual product data is rendered.

## Stitch UI Prompt
```text
// Target Component: SkeletonProductDetail
// Description: A React component that renders a skeleton loading state for a product detail page.
// Layout: Bento Grid, 2x2 (adjust as needed)
// Visual Style: Dark mode, Tailwind CSS, slate-900 background, zinc-700 placeholders, blue-500 accents for shimmer.
//
// Grid Row 1, Column 1: Image Placeholder
//   - Shape: Rounded rectangle, aspect ratio 16:9.
//   - Color: zinc-700.
//   - Shimmer animation: Use blue-500 for the shimmer highlight.
//
// Grid Row 1, Column 2: Product Title Placeholder
//   - Shape: Rectangle, width 75% of container, height 2rem.
//   - Color: zinc-700.
//   - Shimmer animation: Use blue-500 for the shimmer highlight.
//   - Spacing: Margin-bottom 0.5rem.
//
// Grid Row 1, Column 2: Brand Placeholder
//   - Shape: Rectangle, width 50% of container, height 1.25rem.
//   - Color: zinc-700.
//   - Shimmer animation: Use blue-500 for the shimmer highlight.
//   - Spacing: Margin-bottom 1rem.
//
// Grid Row 1, Column 2: Price Placeholder
//   - Shape: Rectangle, width 40% of container, height 1.5rem.
//   - Color: zinc-700.
//   - Shimmer animation: Use blue-500 for the shimmer highlight.
//   - Spacing: Margin-bottom 1rem.
//
// Grid Row 2, Column 1+2: Description Placeholder (Multiple Lines)
//   - Shape: Multiple rectangles, each taking up 90% of the container width, height 1rem.
//   - Color: zinc-700.
//   - Shimmer animation: Use blue-500 for the shimmer highlight.
//   - Spacing: Margin-bottom 0.25rem between lines.
//
// Grid Row 3, Column 1+2: Ecosystem Tab Placeholder (Related Products Section)
//   - Title: Text "Related Products" in zinc-400.
//   - Card placeholders: Render 3 card placeholders horizontally, each with rounded corners. Use zinc-700 for the placeholders within the cards, add a shimmer animation using blue-500.
//   - Card Placeholder Width: 30%
//
// Grid Row 4, Column 1+2: Ecosystem Tab Placeholder (Integrations Section)
//   - Title: Text "Integrations" in zinc-400.
//   - Card placeholders: Render 2 card placeholders horizontally, each with rounded corners. Use zinc-700 for the placeholders within the cards, add a shimmer animation using blue-500.
//   - Card Placeholder Width: 45%
//
// Component Hierarchy:
//   - SkeletonProductDetail (Root, Bento Grid)
//     - ImagePlaceholder (Rounded Rectangle)
//     - TitlePlaceholder (Rectangle)
//     - BrandPlaceholder (Rectangle)
//     - PricePlaceholder (Rectangle)
//     - DescriptionPlaceholder (Multiple Rectangles)
//     - RelatedProductsPlaceholder (Section with Card Placeholders)
//     - IntegrationsPlaceholder (Section with Card Placeholders)
//
// Use Tailwind CSS classes to achieve the described styling.
// Aim for a clean and visually appealing skeleton UI that provides clear feedback to the user while the data loads.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- Manually verify that the skeleton UI renders correctly in the Product Detail View while data is loading.
- Manually verify that the skeleton UI is replaced with the actual product data once loading is complete.
- Measure the rendering time of the skeleton to ensure it renders within 200ms.
