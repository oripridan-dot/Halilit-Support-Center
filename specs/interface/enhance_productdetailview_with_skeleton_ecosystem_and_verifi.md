# Spec: Enhance ProductDetailView with Skeleton, Ecosystem, and Verified Accessories (Final)
**Version:** 2.0
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## Purpose

Enhance the Product Detail View with a detailed skeleton UI while data is loading, display the Ecosystem Tab, and display Verified Accessory Recommendations. This addresses the "Speed of Service" business goal by providing immediate feedback to the user and the "Maximize Attachment Rate" business goal by displaying related products and integrations. This spec integrates previous work on the component.

## Requirements

1. **Replace Loading Spinner:** Replace the existing loading spinner with the `<SkeletonProductDetail>` component from `frontend/src/components/SkeletonProductDetail.tsx`.

2. **Render Ecosystem Tab:** Integrate the `<EcosystemTab>` component into the `ProductDetailView`. Pass the `productId` to the `EcosystemTab` component. The tab must include a title: `Related Products and Integrations`.

3. **Render Verified Accessory Recommendations:** Integrate the `<VerifiedAccessoriesRecommendations>` component into the `ProductDetailView`. Pass the `productId` to the `<VerifiedAccessoriesRecommendations>` component. The section must include a title: `Verified Accessories`.

4. **Conditional Rendering:**
    - Display the `<SkeletonProductDetail>` component while `isLoading` is `true`.
    - Display the actual product details, `<EcosystemTab>`, and `<VerifiedAccessoriesRecommendations>` only when `isLoading` is `false`, there is no `error`, and `product` is available.
    - Display an error message when there is an `error`.
    - Display a "Product not found" message when `product` is not available.

5. **Layout and Styling:** Ensure the `<SkeletonProductDetail>`, `<EcosystemTab>`, and `<VerifiedAccessoriesRecommendations>` components are correctly styled and integrated into the overall layout of the `ProductDetailView`, maintaining the dark theme (slate-900 background, blue-500 accents).

6. **Component Placement:** Place the `<EcosystemTab>` component below the product information and image, and the `<VerifiedAccessoriesRecommendations>` component below the `<EcosystemTab>`. The `<VerifiedAccessoriesRecommendations>` should only show verified accessories.

7. **Image Fallback:** The `ImageWithFallback` component must be used for the main product image.

8. **Navigation:** Use `useNavigationStore` hook to handle navigation.

9. **Error Handling:** Display error messages for loading the main product and any related data (Ecosystem, Accessories).

## Behavior Scenarios

1. **Scenario:** The Product Detail View is loading data.
    - **Input:** `isLoading` is `true`.
    - **Outcome:** The `<SkeletonProductDetail>` component is displayed. The loading spinner is no longer visible.

2. **Scenario:** The Product Detail View has successfully loaded data.
    - **Input:** `isLoading` is `false`, there is no `error`, and `product` is available.
    - **Outcome:** The product details, the `<EcosystemTab>`, and `<VerifiedAccessoriesRecommendations>` are displayed. The `<SkeletonProductDetail>` is no longer visible.

3. **Scenario:** The Product Detail View encounters an error while loading data.
    - **Input:** `error` is not `null`.
    - **Outcome:** An error message is displayed.

4. **Scenario:** The Product Detail View does not find the requested product.
    - **Input:** `product` is `null`.
    - **Outcome:** A "Product not found" message is displayed.

## Stitch UI Prompt
```text
// Target Component: ProductDetailView
// Description: Displays details for a selected product, including hero image, pricing, description, ecosystem tab, and accessory recommendations.  Handles loading and error states.  Uses Tailwind CSS dark mode (slate-900 background, blue-500 accents).  Uses React and Typescript.

// Layout: Bento Grid
//  2x2 grid on large screens, stacking on smaller screens.
//  Top Left: Hero Image (ImageWithFallback component)
//  Top Right: Product Information (Title, Brand, Price, Description)
//  Bottom Left: Ecosystem Tab (Related Products and Integrations)
//  Bottom Right: Verified Accessories Recommendations (Carousel)

// Visual Style: Dark Mode, Tailwind CSS
//  Background: slate-900
//  Text: white for headings, zinc-400 for descriptions, blue-500 for active elements
//  Borders: zinc-700 for dividers

// Data Slots:
//  - Hero Image:  "product.image_url" with alt text "product.name".  If unavailable, show /placeholder.png
//  - Product Title: "product.name"
//  - Brand: "product.brand"
//  - Price: "product.price" (formatted with currency)
//  - Description: "product.description"
//  - Related Products:  A list of related products, each with "name", "description", and "image_url"
//  - Integrations:  A list of integrations, each with "name", "description", and "logo_url"
//  - Verified Accessories: A list of accessories, each with "name", "image_url", and "price"

// Component Hierarchy:
//  1. Outer container (bg-slate-900)
//  2. Inner container (mx-auto, p-4, grid grid-cols-1 lg:grid-cols-2 gap-6)
//  3. Left Column:
//      - ImageWithFallback (Hero Image)
//      - Ecosystem Tab (Related Products and Integrations)
//  4. Right Column:
//      - Product Information:
//          - Title (text-2xl font-bold text-white)
//          - Brand (text-lg text-zinc-400)
//          - Price (text-xl text-white)
//          - Description (text-zinc-400)
//      - Verified Accessories Recommendations (Carousel)

// Spacing:
//  - Generous padding around the outer container (p-6)
//  - Moderate spacing between elements within each column (mb-4)
//  - Smaller spacing within the product information section (mt-2)

// Action:
//  Generate a React component that implements this layout and visual style.
//  The component must:
//      - Handle loading and error states.
//      - Display the correct data in each data slot.
//      - Use Tailwind CSS classes for all styling.
//      - Implement the correct component hierarchy and spacing.
//      - Correctly call ImageWithFallback with product.image_url and a placeholder if missing.
//      - Include correct header and a product description.
//      - Ensure that the component is responsive and looks good on all screen sizes.
//      - Correctly implements the loading spinner and "Product not found" message, if needed.
//  Make sure the generated components use slate-900 and blue-500 palette and the same style than the Operator Console.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
