# Spec: ProductDetail - Accessory Recommendations

**Version:** 1.0
**Component:** `frontend/src/components/ProductDetail/AccessoryRecommendations.tsx`

## Purpose
To display a list of recommended accessories for a given product on the Product Detail View, enhancing the user experience and potentially increasing sales by highlighting compatible and relevant products. This directly addresses Business Goal #1: Maximize Attachment Rate.

## Requirements

1.  **Data Source:** The component must fetch accessory recommendations from the `/api/products/{productId}/accessories` endpoint.
2.  **API Contract:** The endpoint must return a JSON response with a list of accessory products, each including at least `id`, `name`, `image_url`, and `price`. The type definition is:

    ```typescript
    interface AccessoryProduct {
      id: string;
      name: string;
      image_url: string;
      price: number | null;
    }
    ```
3.  **Loading State:** While fetching accessory data, the component must display a skeleton loading state using Tailwind CSS (see `SkeletonProductDetail.tsx` for examples).
4.  **Empty State:** If the API returns an empty list of accessories, the component must display a placeholder message: "No recommended accessories available. Please check back later or contact support."
5.  **Error Handling:** If the API request fails, the component must display an error message: "Failed to load accessory recommendations."
6.  **Display Limit:** The component should display a maximum of 5 accessory recommendations to prevent overwhelming the user.
7.  **Visual Style:** Accessories must be displayed in a horizontal scrollable list of cards. Each card must contain the accessory's image, name, and price. Use Tailwind CSS for styling, matching the existing design tokens.
8.  **Navigation:** Clicking on an accessory card must navigate the user to the Product Detail View for that accessory using `navigationStore.goToProduct(accessoryId)`.
9.  **Verified Accessory Badge:** If an accessory has been verified as compatible via the Relationship Graph (backend decision), display a small green "Verified" badge on the accessory card. Verification status will be a boolean field returned by the API alongside the other `AccessoryProduct` fields.

## Behavior Scenarios

1.  **Scenario:** Product has accessories
    *   Given: The `/api/products/{productId}/accessories` endpoint returns a list of accessory products.
    *   Then: The component displays the accessory products in a horizontal scrollable list, each with its image, name, and price.

2.  **Scenario:** Product has no accessories
    *   Given: The `/api/products/{productId}/accessories` endpoint returns an empty list.
    *   Then: The component displays the "No recommended accessories available" placeholder message.

3.  **Scenario:** API request fails
    *   Given: The `/api/products/{productId}/accessories` endpoint returns an error.
    *   Then: The component displays the "Failed to load accessory recommendations" error message.

4.  **Scenario:** Loading state
    *   Given: The component is fetching accessory data.
    *   Then: The component displays a skeleton loading state.

5.  **Scenario:** Accessory is clicked
    *   Given: An accessory card is clicked.
    *   Then: The user is navigated to the Product Detail View for that accessory.

## Stitch UI Prompt

```
Bento Grid layout. Dark mode. Tailwind CSS.

The root element is a container with a slate-900 background and rounded corners.

Inside the container:
1. A title "Recommended Accessories" with text-zinc-400 color and a mb-2 margin.
2. A horizontal scrollable list (overflow-x-auto) of accessory cards.

Each accessory card:
- width: 1/3 of the container, shrink-0 to prevent wrapping, rounded-lg corners, overflow-hidden, shadow-md.
- An ImageWithFallback component (refer to existing ImageWithFallback usage in other components). Data slot: `image_url`. alt text is `name`. Aspect ratio 4:3.
- Below the image, a div with:
  - The accessory name (text-white, font-semibold). Data slot: `name`.
  - The accessory price (text-white). Data slot: `price`. Display "Call for Price" if the price is null.
  - A "Verified" badge (small, green) if the accessory is verified (boolean value in data slot: `is_verified`). Use the existing `StockBadge` component and adapt the status.

If no accessories are available, show a placeholder message "No recommended accessories available. Please check back later or contact support." in text-zinc-400.

If loading, use the animate-shimmer effect from SkeletonProductDetail.tsx for the image.

Use existing Tailwind color tokens for all styling.

Data Slots:
- name: string (Accessory Name)
- image_url: string (URL of the accessory image)
- price: number | null (Accessory Price)
- is_verified: boolean (Whether the accessory is verified)
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- `pytest backend/tests/test_api.py -v` (Ensure the `/api/products/{productId}/accessories` endpoint exists and returns the correct data.)
