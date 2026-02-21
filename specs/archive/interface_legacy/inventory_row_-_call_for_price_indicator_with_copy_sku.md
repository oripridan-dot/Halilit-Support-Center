# Spec: Inventory Row - Call for Price Indicator (with Copy SKU)
**Version:** 1.1
**Component:** `frontend/src/components/views/InventoryView.tsx`

## 1. Purpose

To visually indicate "Call for Price" (CfP) status in the Inventory Master, enabling operators to quickly identify items requiring manual price lookup. This addresses the "Pricing Clarity" business goal, and to include a convenient "Copy SKU" button to improve operator efficiency.

## 2. Requirements

1.  **CfP Indicator:** Each row in the Inventory grid MUST display a "Call for Price" indicator if the corresponding product's `price` property is `null` or 0.
2.  **Indicator Style:** The "Call for Price" indicator MUST be visually distinct and easily recognizable. Use a specific icon (e.g., `Phone` from `lucide-react`) and text.
3.  **Indicator Placement:** Position the "Call for Price" indicator clearly and consistently within the row, preferably near the price column.
4.  **Copy SKU Button:** The Indicator MUST include a "Copy SKU" button.
5.  **Copy Functionality:** Clicking the "Copy SKU" button should copy the product's SKU to the user's clipboard.
6.  **Success Indication:** Upon successful copy, the button's label should briefly change to "Copied!" for 2 seconds, then revert to "Copy SKU".
7.  **Error Handling:** The component should handle potential errors during the clipboard copy operation. If an error occurs, display an error message (e.g., "Copy Failed") instead of changing to "Copied!". The error message should also disappear after 2 seconds.
8.  **Dark Theme Styling:** Use Tailwind CSS to style the component, adhering to the dark theme (slate-900 background, blue-500 accents).
9.  **Conditional Rendering:** Only render the CfP indicator when the price is explicitly null or zero (0).
10. **Accessibility:** Ensure the button has proper accessibility labels for screen readers.

## 3. Behavior Scenarios

1.  **Scenario:** Product A has `price: null`.
    *   **Outcome:** The Inventory grid row for Product A displays a "Call for Price" indicator with a telephone icon and "Call for Price" text, and a "Copy SKU" button. Clicking the "Copy SKU" button copies the product's SKU.

2.  **Scenario:** Product B has `price: 0`.
    *   **Outcome:** The Inventory grid row for Product B displays a "Call for Price" indicator with a telephone icon and "Call for Price" text, and a "Copy SKU" button. Clicking the "Copy SKU" button copies the product's SKU.

3.  **Scenario:** Product C has `price: 129.99`.
    *   **Outcome:** The Inventory grid row for Product C does not display a "Call for Price" indicator or a "Copy SKU" button.

4. **Scenario:** The user clicks the "Copy SKU" button, and the copy is successful.
    * **Outcome:** The button text changes to "Copied!" for 2 seconds.

5. **Scenario:** The user clicks the "Copy SKU" button, and the copy fails.
    * **Outcome:** The button text changes to "Copy Failed" for 2 seconds.

## Stitch UI Prompt

```text
// Target Component: InventoryView
// Description: Modify the InventoryView component to include a "Call for Price" indicator with a copy SKU button in each row when the product price is null or 0.
// Layout: The InventoryView uses a table layout (likely a `<table>` element, but this may be virtualized).  The indicator should be positioned near the `price` column for that row.
// Visual Style:
//  - Dark theme: slate-900 background, blue-500 accents.
//  - "Call for Price" indicator:
//    - Use the `Phone` icon from `lucide-react`.
//    - Text: "Call for Price"
//    - Tailwind classes: `flex items-center gap-1 px-2 py-1 rounded-md text-xs font-semibold bg-zinc-800 text-zinc-300` or similar.
//  - "Copy SKU" button:
//    - Use a subtle style that fits the dark theme. Tailwind classes like `bg-zinc-700 hover:bg-zinc-600 text-zinc-300 rounded-md px-2 py-1 text-xs`
//    - Initial text: "Copy SKU"
//    - On success: "Copied!" (briefly)
//    - On failure: "Copy Failed" (briefly)
// Data Slots:
//  - Each row represents a product.  The `price` and `id` (SKU) are used for this feature.
//  - `price`: number | null | undefined (If null or 0, show the indicator)
//  - `id`: string (The SKU to copy)
// Component Hierarchy:
//  - The InventoryView component displays a list of product rows.
//  - Inside each product row, if the product's `price` is null or 0, include the "Call for Price" indicator with the "Copy SKU" button.
// Spacing: Use consistent spacing with Tailwind CSS classes (e.g., `mr-2`, `ml-auto`) to align the elements.
// Interactive behavior: The "Copy SKU" button should copy the product's SKU to the clipboard when clicked. Provide feedback (Copied!/Copy Failed) for a brief duration after the click action.
// Accessibility: Ensure that the 'Copy SKU' button is properly labelled for accessibility.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
