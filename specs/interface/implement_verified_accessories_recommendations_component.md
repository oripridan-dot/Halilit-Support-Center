# Spec: Implement Verified Accessories Recommendations Component
**Version:** 1.0
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
    -   If no verified accessories are available (API returns an empty list), display the message: "No verified accessories available. Check related products or official brand resources for suggestions to manually add." in a visually distinct manner, using `text-zinc-400 italic`.
8.  **Dark Theme Styling:**
    -   Use Tailwind CSS to style the component, adhering to the dark theme (slate-900 background, blue-500 accents).
9.  **Responsiveness:**
    -   The component must be responsive and adapt to different screen sizes.
10. **Integration Location:**
    - This component MUST be displayed in place of the Related Products section shown in `specs/interface/enhanced_productdetailview_with_skeleton_and_ecosystem_tab.md` after the product details and before the ecosystem tab.

## Data Contract

**`useProductRelationships` Hook:**
```typescript
interface ProductRelationships {
  isLoading: boolean;
  error: string | null;
  verifiedAccessories: ConductorProduct[];
}
```
The hook fetches data internally to create the object above.

## Behavior Scenarios
-   **Scenario:** Initial Load - No Recommendations
    -   Input:  Component mounts, API returns an empty `verifiedAccessories` array.
    -   Outcome: Displays a message "No verified accessories available. Check related products or official brand resources for suggestions to manually add."

-   **Scenario:** Initial Load - Recommendations Available
    -   Input: Component mounts, API returns a list of accessories.
    -   Outcome: Displays a carousel of accessory product recommendations.

-   **Scenario:** API Error
    -   Input:  Component mounts, API returns an error.
    -   Outcome: Displays an error message: "Failed to load accessory recommendations."

## Stitch UI Prompt
```text
// Target Component: VerifiedAccessoriesRecommendations
// Description:  A React component that displays a carousel of verified accessory recommendations.

// Layout: Flexbox, horizontal scrolling. Dark mode, Tailwind CSS.

// Overall Structure:
// Container (flex, horizontal scroll)
//   Accessory Card (repeat)
//     Image
//     Product Name
//     Product Price
//     "Verified" Badge

// Visual Style:
// Dark mode
// Tailwind CSS
// Background: slate-900
// Accent: blue-500
// Text: white for product name, zinc-400 for price

// Data Slots:
// Data Slot: Product Image (URL) - Placeholder: "/placeholder.png"
// Data Slot: Product Name (string) - Placeholder: "Accessory Product Name"
// Data Slot: Product Price (number) - Placeholder: "99.99"

// Component Hierarchy and Spacing:
// Container:
//   - className: "flex space-x-4 overflow-x-auto pb-4"
// Accessory Card:
//   - className: "w-64 shrink-0 rounded-lg overflow-hidden shadow-md bg-slate-800"
//   - Image: className: "w-full h-32 object-cover"
//   - Product Name: className: "text-white font-semibold px-4 py-2"
//   - Product Price: className: "text-zinc-400 px-4 pb-2"
// "Verified" Badge:
//   - className: "absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-md text-xs"

// Loading State: Replace the whole component with a skeleton loader as used elsewhere in the app.

// No Accessories State: Display the message: "No verified accessories available. Check related products or official brand resources for suggestions to manually add."
// Styling: Styling matches existing `No verified accessories available` styling using `text-zinc-400 italic`

// Instructions:
// 1. Create a flex container with horizontal scrolling.
// 2. Repeat the Accessory Card structure for each accessory.
// 3. Implement the data slots with the specified placeholders.
// 4. Add the "Verified" badge.
// 5. Use Tailwind CSS to implement the visual style.
// 6. Implement loading and no accessories states.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- `pytest backend/tests/test_product_relationships.py -v`
