# Spec: Implement Verified Accessories Recommendations Component
**Version:** 1.1
**Component:** `frontend/src/components/ProductDetail/VerifiedAccessoriesRecommendations.tsx`

## Purpose
To display a curated selection of verified accessory recommendations for a given product on the Product Detail page, directly maximizing attachment rates (Business Goal #1). These recommendations will be fetched from the product relationship graph, ensuring compatibility and operator trust. If no accessories are available, a specific prompt will direct the operator to take action.

## Requirements
1.  **Data Source:**
    -   Fetch accessory data from the existing product relationship graph. A new hook, `useProductRelationships(productId: string)`, will provide access to this data. The hook must return an object with the following shape:
        ```typescript
        interface ProductRelationships {
          isLoading: boolean;
          error: string | null;
          verifiedAccessories: ConductorProduct[];
        }
        ```
    - Display only "Verified Accessories", filtering out other relationship types.
2.  **Loading State:**
    -   Display a loading indicator (e.g., skeleton loaders) while fetching data. The indicator must match the style of the other loading indicators.
3.  **Error Handling:**
    -   Display an error message if the API request to the graph fails. The error message must be user-friendly.
4.  **Display Accessories:**
    -   If verified accessories are available, display them in a horizontal carousel.
5.  **Accessory Card:**
    -   Each accessory must be displayed as a card with:
        -   A thumbnail image
        -   The product name
        -   The product price (formatted)
        -  A "Verified" badge in the upper right corner.
6.  **Navigation:**
    -   Clicking an accessory card must navigate the user to the Product Detail page for that accessory, using `useNavigationStore().goToProduct(accessory.id)`.
7.  **No Accessories Message:**
    -   If no verified accessories are available, display the message: "No verified accessories available. Check related products or official brand resources for suggestions to manually add." in a visually distinct manner.
8. **Dark Theme Styling:**
    -   Use Tailwind CSS to style the component, adhering to the dark theme (slate-900 background, blue-500 accents).
9.  **Responsiveness:**
    -   The component should be responsive and adapt to different screen sizes.
10. **"Verified" Badge Implementation**:
    - The "Verified" badge should be implemented as a separate component for reusability and styled with Tailwind CSS. It should have a green background and white text.
11. **Skeleton Loaders**:
    - Implement skeleton loaders for a smooth loading experience. Use the same shimmer animation as other loading states.
12. **Placement**:
    - Ensure the component is correctly integrated into the ProductDetailView layout, ideally below the product information and above the Ecosystem Tab.
13.  **useProductRelationships Hook**:
    -   Implement the `useProductRelationships` hook. The backend must have a `/api/products/{product_id}/relationships` endpoint that returns relationship data.

## Data Contract

**API Endpoint:** `/api/products/{product_id}/relationships` (GET)

**Request:**
*   `product_id` (path parameter): The ID of the product for which to retrieve related products.

**Response (JSON):**

```json
{
  "verifiedAccessories": [
    {
      "id": "string",
      "name": "string",
      "brand": "string",
      "price": number | null,
      "image_url": "string"
    }
  ]
}
```

**TypeScript Interface:**

```typescript
interface ConductorProduct {
  id: string;
  name: string;
  brand: string;
  price: number | null;
  image_url: string;
}

interface ProductRelationships {
  isLoading: boolean;
  error: string | null;
  verifiedAccessories: ConductorProduct[];
}
```

## Behavior Scenarios

-   **Scenario:** Initial Load - Accessories Available
    -   Input: Component mounts with `productId = "123"`, API returns a list of verified accessories.
    -   Outcome: Displays a carousel of accessory cards, each showing the accessory's image, name, price, and a "Verified" badge.
-   **Scenario:** Initial Load - No Accessories Available
    -   Input: Component mounts with `productId = "123"`, API returns an empty list of verified accessories.
    -   Outcome: Displays the message: "No verified accessories available. Check related products or official brand resources for suggestions to manually add.".
-   **Scenario:** API Error
    -   Input: Component mounts with `productId = "123"`, API returns an error (e.g., 500 Internal Server Error).
    -   Outcome: Displays an error message.
-   **Scenario:** Loading State
    -   Input: Component is fetching data.
    -   Outcome: Displays skeleton loaders.

## Stitch UI Prompt

```text
// Target Component: VerifiedAccessoriesRecommendations
// Description:  A React component that displays a horizontal carousel of verified accessory recommendations for a product.
// Styling: Tailwind CSS, dark theme (slate-900 background, blue-500 accents)
// Layout: Flexbox, horizontal scrolling

// Structure:
// - Container (bg-slate-900, p-4)
//   - Title (text-lg, font-semibold, text-white, mb-2): "Verified Accessories"
//   - Carousel (flex, space-x-4, overflow-x-auto, pb-4)
//     - AccessoryCard (repeated for each accessory)

// Data Slots:
// - accessory.image_url: URL of the accessory image
// - accessory.name: Name of the accessory
// - accessory.price: Price of the accessory

// AccessoryCard:
// - Container (w-64, shrink-0, rounded-lg, overflow-hidden, shadow-md, relative)
//   - Image (aspect-w-4, aspect-h-3, w-full, h-32, object-cover): {accessory.image_url}
//   - Content (p-2)
//     - Name (text-sm, font-semibold, text-white, truncate): {accessory.name}
//     - Price (text-xs, text-zinc-400): ₪{accessory.price}
//   - VerifiedBadge (absolute, top-2, right-2, bg-green-500, text-white, px-2, py-1, rounded-md, text-xs): "Verified"

// No Accessories Message:
// - Container (text-zinc-400, italic): "No verified accessories available. Check related products or official brand resources for suggestions to manually add."

// Loading State (Skeleton):
// - Container (w-64, shrink-0, rounded-lg, overflow-hidden, shadow-md)
//   - Image (aspect-w-4, aspect-h-3, animate-shimmer, w-full, h-32, bg-zinc-700)
//   - Content (p-2)
//     - Name (animate-shimmer, h-4, w-3/4, bg-zinc-700, rounded-md, mb-1)
//     - Price (animate-shimmer, h-3, w-1/2, bg-zinc-700, rounded-md)

// Instructions:
// - Use flexbox for the carousel layout.
// - Use truncate class for the accessory name to prevent overflow.
// - The VerifiedBadge should be positioned absolutely in the top-right corner of the AccessoryCard.
// - Ensure all text colors and background colors adhere to the dark theme (slate-900/blue-500 palette).
// - Handle the loading state by displaying a placeholder skeleton UI for each accessory card.
// - Handle the "No accessories available" state by displaying the appropriate message.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- `pytest backend/tests/test_product_relationships.py -v`
