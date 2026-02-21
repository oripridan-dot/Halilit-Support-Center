# Spec: Implement Verified Accessories Recommendations Component
**Version:** 1.3
**Component:** `frontend/src/components/ProductDetail/VerifiedAccessoriesRecommendations.tsx`

## Purpose
To display a curated selection of verified accessory recommendations for a given product on the Product Detail page, directly maximizing attachment rates (Business Goal #1). These recommendations will be fetched from the product relationship graph, ensuring compatibility and operator trust. If no accessories are available, a specific prompt will direct the operator to take action. This spec supersedes `specs/interface/accessory_recommendations_component.md` and `specs/interface/product_detail_-_accessory_recommendations.md`. This version provides a stitch ui prompt.

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
        -   The product name.
        -   The product price (formatted).
    -   Each accessory card must be clickable, navigating the operator to the Product Detail page for the selected accessory. Use `useNavigationStore().goToProduct(accessory.id)`.
    - The accessories cards must display the "Verified" badge.

6.  **No Accessories Message:**
    -   If no verified accessories are available (API returns an empty list), display the message: "No verified accessories available. Check related products or official brand resources for suggestions to manually add." in a visually distinct manner.

7.  **Prompt Styling:** Style the message to stand out, with `text-zinc-400 italic`.
8.  **Accessibility:** Ensure the carousel and its elements are keyboard-navigable and screen reader-compatible.
9.  **Dark Theme Styling:** Use Tailwind CSS for styling, adhering to the dark theme (slate-900 background, blue-500 accents).
10. **Responsiveness:** The component should be responsive and adapt to different screen sizes.

## Data Contract

**Hook:** `useProductRelationships(productId: string)`

```typescript
interface ProductRelationships {
  isLoading: boolean;
  error: string | null;
  verifiedAccessories: ConductorProduct[];
}
```

**Properties of `ConductorProduct` used:**

-   `id`: string
-   `name`: string
-   `image_url`: string
-   `price`: number | null

## Behavior Scenarios

-   **Scenario:** Initial Load - Verified Accessories Available
    -   Input: Component mounts, API returns a non-empty `verifiedAccessories` array.
    -   Outcome: Displays a horizontal carousel of accessory cards.

-   **Scenario:** Initial Load - No Verified Accessories
    -   Input: Component mounts, API returns an empty `verifiedAccessories` array.
    -   Outcome: Displays the message "No verified accessories available. Check related products or official brand resources for suggestions to manually add."

-   **Scenario:** Loading State
    -   Input: While fetching data, `isLoading` is true.
    -   Outcome: Displays skeleton loaders.

-   **Scenario:** Error State
    -   Input: API request fails, `error` is not null.
    -   Outcome: Displays an error message.

## Stitch UI Prompt

```text
// Target Component: VerifiedAccessoriesRecommendations
// Description: Displays a carousel of accessory product recommendations.

// Layout: Bento Grid
// Visual Style: Dark mode, Tailwind CSS, slate-900 background, blue-500 accents.

// Data Slots:
// 1. accessory_image: Image URL
// 2. accessory_name: Product Name
// 3. accessory_price: Product Price
// 4. no_accessories_message: String to display when no accessories are available.

// Component Hierarchy:
// - Container (Bento Grid)
//   - Title (h2, text-lg font-semibold mb-2, text-white)
//   - Carousel (Flexbox, horizontal scrolling)
//     - Accessory Card (Rounded rectangle, shadow)
//       - Image (Rounded top, aspect ratio 4:3)
//       - Name (Text, truncate)
//       - Price (Text)
//   - No Accessories Message (if no accessories) (Text, italic, text-zinc-400)

// Spacing:
// - Carousel items: space-x-4
// - Title and Carousel: mb-4

// Detailed Instructions:

// Container: Use a Bento Grid layout to organize the title and carousel. The container should fill its available width.
// Title: Display a "Verified Accessories" title using an h2 element with Tailwind classes for text size, font weight, and margin. Text color should be white.
// Carousel: Use a horizontal Flexbox to display the accessory cards. The Flexbox should allow horizontal scrolling.
// Accessory Card: Create a rounded rectangle for each accessory card with a shadow.
// Image: Display the accessory image at the top of the card. Maintain an aspect ratio of 4:3.
// Name: Display the accessory name below the image. Truncate the text if it's too long.
// Price: Display the accessory price below the name.
// No Accessories Message: If no accessories are available, display the "No accessories available" message using an italic font and a zinc-400 text color.
// Loading State: Use skeleton loaders to represent the carousel items while the data is loading.

// Use Tailwind CSS for all styling and ensure the component adheres to the Halilit Support Center's dark theme. Remember to use the correct color tokens for the background and text. The height of the card is 250px. Use the `aspect-w-4 aspect-h-3` classes to manage the images.
// Please ensure you have a 'Verified' badge in the accessory card.
//
Write the complete React/Tailwind code for this component. The accessory cards must link to their product page.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
