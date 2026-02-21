# Spec: Implement Verified Accessories Recommendations Component
**Version:** 1.2
**Component:** `frontend/src/components/ProductDetail/VerifiedAccessoriesRecommendations.tsx`

## Purpose
To display a curated selection of verified accessory recommendations for a given product on the Product Detail page, directly maximizing attachment rates (Business Goal #1). These recommendations will be fetched from the product relationship graph, ensuring compatibility and operator trust. If no accessories are available, a specific prompt will direct the operator to take action. This spec replaces `specs/interface/accessory_recommendations_component.md` and `specs/interface/product_detail_-_accessory_recommendations.md`

## Requirements
1.  **Data Source:**
    -   Fetch accessory data from the product relationship graph. A new hook, `useProductRelationships(productId: string)`, will provide access to this data. The hook must return an object with the following shape:
        ```typescript
        interface ProductRelationships {
          isLoading: boolean;
          error: string | null;
          verifiedAccessories: ConductorProduct[];
        }
        ```
    - Display only "Verified Accessories", filtering out other relationship types. The `ConductorProduct` interface must align with the type from `useConductorCatalog.ts`.
2.  **Loading State:**
    -   Display a loading indicator (e.g., skeleton loaders) while fetching data. The indicator must match the style of the other loading indicators (i.e. the `SkeletonProductDetail` shimmer effect).
3.  **Error Handling:**
    -   Display an error message if the API request to the graph fails. The error message must be user-friendly.
4.  **Display Accessories:**
    -   If verified accessories are available, display them in a horizontal carousel.
5.  **Accessory Card:**
    -   Each accessory must be displayed as a card with:
        -   A thumbnail image. Use `<ImageWithFallback/>` to ensure no broken images.
        -   The product name
        -   The product price (formatted)
        -   A "Verified" badge in the upper right corner.
        - All elements must be styled using Tailwind CSS, adhering to the dark theme (slate-900 background, blue-500 accents).

6.  **Navigation:**
    -   Clicking an accessory card must navigate the user to the Product Detail page for that accessory, using `useNavigationStore().goToProduct(accessory.id)`.
7.  **No Accessories Message:**
    -   If no verified accessories are available (API returns an empty list), display the message: "No verified accessories available. Check related products or official brand resources for suggestions to manually add." in a visually distinct manner (e.g., italicized text in a muted color).
8. **Dark Theme Styling:** Use Tailwind CSS to style the component, adhering to the dark theme (slate-900 background, blue-500 accents).
9. **Responsiveness:** The component should be responsive and adapt to different screen sizes.
10. **"Verified" Badge:** Display a "Verified" badge on the Accessory card. Use a green background and white text. Position the badge in the upper right corner of the card.
11. **Accessibility:** Ensure all interactive elements are accessible to keyboard and screen reader users.

## Stitch UI Prompt
```text
// Target Component: VerifiedAccessoriesRecommendations
// Description: A React component that displays a carousel of verified accessory recommendations for a product.

// Layout:
//  - Use a horizontal Flexbox layout for the carousel.
//  - Each accessory is displayed as a card.

// Visual Style:
//  - Dark mode, Tailwind CSS
//  - Background: slate-900
//  - Text: white
//  - Accents: blue-500, green-500

// Component Hierarchy:
//  - Container (Flexbox, horizontal scrolling)
//    - Accessory Card (for each accessory)
//      - Image (ImageWithFallback component - Data Slot: accessory_image_url)
//      - Verified Badge (Data Slot: verified_badge_text)
//      - Product Name (Data Slot: accessory_name)
//      - Product Price (Data Slot: accessory_price)

// Data Slots:
//  - accessory_image_url: URL of the accessory's thumbnail image
//  - verified_badge_text: "Verified"
//  - accessory_name: Name of the accessory product (e.g., "Keyboard Stand")
//  - accessory_price: Price of the accessory (e.g., "$49.99")

// Spacing:
//  - Carousel items: space-x-4
//  - Card padding: p-4
//  - Badge position: absolute top-2 right-2

// Error Message:
//  - Display a message "No verified accessories available. Check related products or official brand resources for suggestions to manually add." in italicized zinc-400 text if no accessories are found.

// Loading State: Use the shimmer animation for skeleton loading.

// Interaction:
//  - Each card should be clickable, navigating to the product detail page of the accessory.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- Implement a Playwright test to verify that:
    - The component displays a loading indicator while data is being fetched.
    - The component displays an error message if the API request fails.
    - The component displays the correct accessory information (image, name, price, verified badge) when accessories are available.
    - Clicking an accessory card navigates to the correct product detail page.
    - The component displays the "No verified accessories available" message when no accessories are available.
