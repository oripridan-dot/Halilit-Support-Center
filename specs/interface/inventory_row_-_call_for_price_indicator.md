# Spec: Inventory Row - Call for Price Indicator

**Version:** 1.0
**Component:** `frontend/src/components/views/InventoryView.tsx`

## 1. Purpose

To visually indicate "Call for Price" (CfP) status in the Inventory Master, enabling operators to quickly identify items requiring manual price lookup. This addresses the "Pricing Clarity" business goal.

## 2. Requirements

1.  **CfP Indicator:** Each row in the Inventory grid MUST display a "Call for Price" indicator if the corresponding product's `price` property is `null` or 0.
2.  **Indicator Style:** The "Call for Price" indicator MUST be visually distinct and easily recognizable. Use a specific icon (e.g., `Phone` from `lucide-react`) and text.
3.  **Indicator Placement:** Position the "Call for Price" indicator clearly and consistently within the row, preferably near the price column.
4. **Copy SKU Button:** The Indicator should include a copy SKU affordance as per `specs/interface/copy_sku_button_for_product_detail_page.md`.
5.  **Dark Theme Styling:** Use Tailwind CSS to style the component, adhering to the dark theme (slate-900 background, blue-500 accents).
6. **Conditional Rendering:** Only render the CfP indicator when the price is explicitly null or zero (0).

## 3. Behavior Scenarios

1.  **Scenario:** Product A has `price: null`.
    *   **Outcome:** The Inventory grid row for Product A displays a "Call for Price" indicator with a telephone icon and "Call for Price" text. Clicking on the indicator should copy the SKU.

2.  **Scenario:** Product B has `price: 0`.
    *   **Outcome:** The Inventory grid row for Product B displays a "Call for Price" indicator with a telephone icon and "Call for Price" text. Clicking on the indicator should copy the SKU.

3.  **Scenario:** Product C has `price: 129.99`.
    *   **Outcome:** The Inventory grid row for Product C does not display a "Call for Price" indicator.

## Stitch UI Prompt

```
Design a React component for an Inventory grid row that shows a "Call for Price" indicator when a product's price is null or zero.

The design should adhere to the following constraints:

*   Use Tailwind CSS for styling.
*   Use the dark theme (slate-900 background, blue-500 accents).
*   The indicator should use the "Phone" icon from the lucide-react library.
*   The indicator should display the text "Call for Price".
*   The indicator should be placed near the price column in the row.
*   The indicator should include a copy SKU affordance.
*   Assume the product data is available as a prop.

Here's a sample data structure:

```json
{
    "id": "HAL-12345",
    "name": "Awesome Guitar",
    "brand": "Fender",
    "price": null
}
```

The desired output is a visually appealing and functional React component that indicates a "Call for Price" status.
Here is the data slot reference

*   Product SKU: {product.id}
*   Show a copy sku button.
*   Use Tailwind CSS.
*   Use Dark Mode.
*   Background color should be dark slate 900.
*   Text should be blue 500.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
