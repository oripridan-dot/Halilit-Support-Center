# Spec: Enhance ProductDetailView with Skeleton and Ecosystem Tab and Accessory Recs
**Version:** 2.2
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## Purpose

Enhance the Product Detail View with a detailed skeleton UI while data is loading, display the Ecosystem Tab, and accessory recommendations. This addresses the "Speed of Service" business goal by providing immediate feedback to the user and the "Maximize Attachment Rate" business goal by displaying related products and integrations. This spec aims to consolidate and finalize the integration of these features into the ProductDetailView.

## Requirements

1. **Replace Loading Spinner:** Replace the existing loading spinner with the `<SkeletonProductDetail>` component from `frontend/src/components/SkeletonProductDetail.tsx`. Ensure the shimmer animation is visible and correctly styled.

2. **Render Ecosystem Tab:** Integrate the `<EcosystemTab>` component into the `ProductDetailView`. Pass the `productId` to the `EcosystemTab` component. The Ecosystem Tab must include a title: `Related Products and Integrations`.

3. **Render Accessory Recommendations:** Integrate the `<VerifiedAccessoriesRecommendations>` component into the `ProductDetailView`. Pass the `productId` to the `<VerifiedAccessoriesRecommendations>` component. The section must include a title: `Verified Accessories`.

4. **Conditional Rendering:**
    - Display the `<SkeletonProductDetail>` component while `isLoading` is `true`.
    - Display the actual product details, `<EcosystemTab>`, and `<VerifiedAccessoriesRecommendations>` only when `isLoading` is `false`, there is no `error`, and `product` is available. The image must load correctly at this stage.
    - Display an error message when there is an `error`. Present error messages to the operator in a banner at the top of the screen.
    - Display a "Product not found" message when `product` is not available. The message must be user-friendly and indicate how to navigate back to the inventory grid.

5. **Layout and Styling:** Ensure the `<SkeletonProductDetail>`, `<EcosystemTab>`, and `<VerifiedAccessoriesRecommendations>` components are correctly styled and integrated into the overall layout of the `ProductDetailView`, maintaining the dark theme (slate-900 background, blue-500 accents). No layout shifts are allowed.

6. **Placement of Components:** Place the `<EcosystemTab>` component below the product information and image, with the `<VerifiedAccessoriesRecommendations>` component following it. The skeleton loader and product detail information should occupy the top sections.

7. **Image Validation:** Keep the ImageWithFallback logic.

8. **Navigation:** Maintain navigation via the `useNavigationStore` hook. Clicking an accessory or related product should navigate to that product's detail page. Implement lazy loading for all product images, ensuring smooth scrolling and optimal performance.

9. **Error Handling:** When loading, display the `SkeletonProductDetail` component. When the API fails, display an error banner at the top of the screen. When there is no product found, show a "Product not found" message on screen and a button which uses `useNavigationStore` to return to the inventory grid.

## Stitch UI Prompt
```text
// Target Component: ProductDetailView
// Description: Displays the Product Detail View with skeleton loading, Ecosystem Tab, and Verified Accessories Recommendations.
// Layout: Bento Grid or CSS Grid
// Visual Style: Dark mode, Tailwind CSS, slate-900 background, blue-500 accents
//
// 1.  Skeleton Loading: While isLoading is true, display the SkeletonProductDetail component.  This component should shimmer and mimic the layout of the real product details.
// 2.  Product Details: When isLoading is false, display the product details.
//      -  Name: Display the product name in a large, prominent font.
//      -  Brand: Display the brand name below the product name.
//      -  Price: Display the price.
//      -  Description: Display the product description.
//      -  Image: Display the product image using the ImageWithFallback component.
// 3.  Ecosystem Tab: Display the EcosystemTab component below the product details.  The EcosystemTab should load related products and integrations. The ecosystem tab must be titled "Related Products and Integrations".
// 4.  Verified Accessories Recommendations: Display the VerifiedAccessoriesRecommendations component below the EcosystemTab. The section must be titled "Verified Accessories".
// 5.  Error State: If there's an error loading the product details, display an error message (red banner).
// 6.  Product Not Found: If the product is not found, display a "Product not found" message and a back button.
//
// Data Slots:
// - Product Name: string - "Halilit Product Name"
// - Brand Name: string - "Halilit Brand Name"
// - Price: string - "$99.99"
// - Description: string - "A detailed description of the Halilit product."
// - Image URL: string - "https://example.com/halilit_product_image.jpg"
// - Related Products: array of { name: string, image_url: string, description: string }
// - Integrations: array of { name: string, logo_url: string, description: string }
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
