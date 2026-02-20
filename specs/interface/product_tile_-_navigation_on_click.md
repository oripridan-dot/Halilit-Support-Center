# Spec: Product Tile - Navigation on Click

**Version:** 1.0
**Component:** `frontend/src/components/ProductTile.tsx`

## 1. Purpose

To enable navigation to the Product Detail View directly from a Product Tile when the tile is clicked. This will improve the user experience and speed of service by providing a quick and intuitive way to access more information about a product, thus contributing to the "Speed of Service" business goal.

## 2. Requirements

1. **Clickable Tile:** The entire Product Tile MUST be clickable, acting as a single interactive element.
2. **Navigation Action:** When a Product Tile is clicked, the user MUST be navigated to the Product Detail View for the corresponding product, using `useNavigationStore().goToProduct(product.id)`.
3. **Accessibility:** The Product Tile MUST be accessible to keyboard users. The tile should be focusable (e.g., by adding a `tabIndex="0"` attribute) and should trigger the navigation action when the Enter or Space key is pressed while focused.
4. **Visual Indication:** The Product Tile MUST provide a visual indication that it is clickable, such as a subtle hover effect (e.g., a change in background color or a slight shadow). Use Tailwind CSS for styling.
5. **Prevent Double Navigation:** Ensure that clicking on child elements within the Product Tile (e.g., the image or badge) does not trigger multiple navigations or interfere with the intended navigation action of the entire tile.
6. **No Interference with Other Functionality:** The navigation action MUST not interfere with other functionality within the Product Tile, such as the display of stock status indicators or Call for Price indicators.
7. **No Broken Links:** Navigation should only occur when a valid `product.id` is available.

## 3. Behavior Scenarios

1. **Scenario:** The user clicks on a Product Tile in the Inventory View.
    * **Outcome:** The user is navigated to the Product Detail View for the corresponding product.
2. **Scenario:** The user focuses on a Product Tile using the keyboard (Tab key).
    * **Outcome:** The Product Tile is visually highlighted (e.g., with a different background color or border).
3. **Scenario:** The user presses the Enter key while a Product Tile is focused.
    * **Outcome:** The user is navigated to the Product Detail View for the corresponding product.
4. **Scenario:** The user presses the Space key while a Product Tile is focused.
    * **Outcome:** The user is navigated to the Product Detail View for the corresponding product.
5. **Scenario:** A product with invalid id is clicked (or does not exist).
    * **Outcome:** The user is not navigated and an error toast message appears.

## Stitch UI Prompt

You are a React code generator. The component to generate is `ProductTile.tsx`.
It should be a functional component that displays a product's image, name, and optionally a badge. It should be clickable to navigate to the product detail page.

**Layout:** Use a Flexbox layout with `flex flex-col`. The tile should contain an image at the top, followed by product information below.

**Visual Style:** Use a dark theme consistent with the Halilit Support Center (slate-900 background, blue-500 accents). The component should have a subtle hover effect to indicate clickability (e.g., `hover:bg-slate-800`). Use Tailwind CSS.

**Data Slots:**

*   **`imageUrl`:** URL of the product image. Use `/placeholder.png` if the image is missing.
*   **`productName`:** Name of the product.
*   **`productId`:** ID of the product.
*   **`badgeText`:** Optional text for a badge (e.g., "OUT OF STOCK", "UNCONFIRMED"). If empty, do not display the badge.
*   **`badgeColor`:** Tailwind color class for the badge background (e.g., `bg-red-500`, `bg-amber-500`).

**Component Hierarchy:**

1.  Top-level `div` with `flex flex-col` and appropriate padding/margin. Add `cursor-pointer` to signify clickability.
2.  `img` tag for the product image. Use `w-full h-48 object-cover` for styling. Handle image loading errors by showing a placeholder.
3.  `div` for product information (name, badge) with `p-2` for padding.
4.  Optional badge element. Position it in the top-right corner of the image using `absolute top-2 right-2`.

**Accessibility:** Add `tabIndex="0"` to the top-level `div` to make it focusable. Use `aria-label` to provide a descriptive label for screen readers.

```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
