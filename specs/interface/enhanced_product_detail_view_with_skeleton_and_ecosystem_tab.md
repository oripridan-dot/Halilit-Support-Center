# Spec: Enhanced Product Detail View with Skeleton and Ecosystem Tab
**Version:** 1.1
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## Purpose

Enhance the Product Detail View with a detailed skeleton UI while data is loading and display the Ecosystem Tab. This addresses the "Speed of Service" business goal by providing immediate feedback to the user and the "Maximize Attachment Rate" business goal by displaying related products and integrations.

## Requirements

1. **Replace Loading Spinner:** Replace the existing loading spinner with the `<SkeletonProductDetail>` component from `frontend/src/components/SkeletonProductDetail.tsx`.

2. **Render Ecosystem Tab:** Integrate the `<EcosystemTab>` component into the `ProductDetailView`. Pass the `productId` to the `EcosystemTab` component.

3. **Conditional Rendering:**
    - Display the `<SkeletonProductDetail>` component while `isLoading` is `true`.
    - Display the actual product details and `<EcosystemTab>` only when `isLoading` is `false`, there is no `error`, and `product` is available.
    - Display an error message when there is an `error`.
    - Display a "Product not found" message when `product` is not available.

4. **Layout and Styling:** Ensure the `<SkeletonProductDetail>` and `<EcosystemTab>` components are correctly styled and integrated into the overall layout of the `ProductDetailView`, maintaining the dark theme (slate-900 background, blue-500 accents).

5. **Ecosystem Tab Placement:** Place the `<EcosystemTab>` component below the product information and image, inside the container.

6. **Image Validation:** Keep the ImageWithFallback logic

7. **Navigation:** Keep navigation via the `useNavigationStore` hook.

## Behavior Scenarios

1. **Scenario:** The Product Detail View is loading data.
    - **Input:** `isLoading` is `true`.
    - **Outcome:** The `<SkeletonProductDetail>` component is displayed. The loading spinner is no longer visible.

2. **Scenario:** The Product Detail View has loaded data successfully.
    - **Input:** `isLoading` is `false`, `error` is `null`, and `product` is defined.
    - **Outcome:** The product details (name, description, image, etc.) and the `<EcosystemTab>` component are displayed. The `<SkeletonProductDetail>` component is no longer visible.

3. **Scenario:** The Product Detail View encounters an error while loading data.
    - **Input:** `isLoading` is `false` and `error` is not `null`.
    - **Outcome:** An error message is displayed to the user.

4. **Scenario:** No product is found for the given ID.
    - **Input:** `isLoading` is `false`, `error` is `null`, and `product` is not defined.
    - **Outcome:** A "Product not found" message is displayed to the user.

## Stitch UI Prompt

```
// Target Component: ProductDetailView
// Description:  A React component that displays detailed information about a product, including a loading skeleton and ecosystem tab.
// Layout: Bento Grid (2x2 on large screens, 1xN on smaller screens)
// Style: Dark mode, Tailwind CSS, slate-900 background, blue-500 accents, zinc-700 placeholders for skeleton.

// Data Slots:
// - Product Name:  STRING  (e.g., "Fender Stratocaster")
// - Product Brand: STRING  (e.g., "Fender")
// - Product Price: NUMBER  (e.g., 799.99)
// - Product Description: STRING (e.g., "The iconic electric guitar...")
// - Image URL: STRING (e.g., "/images/strat.jpg")
// - Related Product 1 Name: STRING (e.g., "Guitar Stand")
// - Related Product 1 Image URL: STRING (e.g., "/images/stand.jpg")
// - Related Product 2 Name: STRING (e.g., "Guitar Case")
// - Related Product 2 Image URL: STRING (e.g., "/images/case.jpg")
// - Integration 1 Name: STRING (e.g., "Ableton Live")
// - Integration 1 Logo URL: STRING (e.g., "/images/ableton.png")
// - Integration 2 Name: STRING (e.g., "Logic Pro X")
// - Integration 2 Logo URL: STRING (e.g., "/images/logic.png")

// Skeleton UI (displayed while loading):
// - Use a shimmer animation for all placeholders (see SkeletonProductDetail.tsx for exact shimmer class).
// - Hero Image:  Aspect ratio 16:9, rounded corners, zinc-700 background.
// - Product Title: Height 5, width 3/4, zinc-700 background, rounded corners.
// - Product Brand: Height 4, width 1/2, zinc-700 background, rounded corners.
// - Product Price: Height 6, width 1/3, zinc-700 background, rounded corners.
// - Description: Three lines of text, each height 4, width full, zinc-700 background, rounded corners.
// - Related Products/Integrations:  Labels are zinc-400, font-medium. The item containers have an aspect ratio of 4:3, zinc-700 background.

// Structure:

// 1.  Parent:  bg-slate-900, min-h-screen, pb-6 (Tailwind classes)
// 2.  Product Detail Header (component already exists).
// 3. Container: container mx-auto p-4 grid grid-cols-1 lg:grid-cols-2 gap-6.
// 4. Inside the grid: an ImageWithFallback on the left (col-span-1 lg:col-span-1), and product information on the right (col-span-1 lg:col-span-1).  The ImageWithFallback should have rounded corners.
// 5.  Below the above (col-span-2 for both mobile and large screens), render the EcosystemTab component.

//  The grid should use Tailwind CSS classes to ensure responsiveness. Ensure there is good spacing between the elements. The shimmer effect should be subtle. Use slate-900 for the main background, and zinc-700 for the placeholders. Accents can be blue-500.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
