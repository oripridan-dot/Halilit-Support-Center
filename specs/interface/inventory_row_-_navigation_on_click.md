# Spec: Inventory Row - Navigation on Click

**Version:** 1.1
**Component:** `frontend/src/components/views/InventoryView.tsx`

## 1. Purpose

To enable navigation to the Product Detail View directly from a row in the Inventory Grid when the row is clicked. This will improve the user experience and speed of service by providing a quick and intuitive way to access more information about a product, thus contributing to the "Speed of Service" business goal. This complements existing navigation affordances such as the global search.

## 2. Requirements

1.  **Clickable Row:** The entire row in the Inventory grid MUST be clickable, acting as a single interactive element.
2.  **Navigation Action:** When a row is clicked, the user MUST be navigated to the Product Detail View for the corresponding product, using `useNavigationStore().goToProduct(product.id)`.
3.  **Accessibility:** The row MUST be accessible to keyboard users. The row should be focusable (e.g., by adding a `tabIndex="0"` attribute) and should trigger the navigation action when the Enter or Space key is pressed while focused.
4.  **Visual Indication:** The row MUST provide a visual indication that it is clickable, such as a subtle hover effect (e.g., a change in background color or a slight shadow). Use Tailwind CSS for styling.
5.  **Prevent Double Navigation:** Ensure that clicking on child elements within the row (e.g., the image or badge) does not trigger multiple navigations or interfere with the intended navigation action of the entire row.
6.  **No Interference with Other Functionality:** The navigation action MUST not interfere with other functionality within the row, such as the display of stock status indicators, Call for Price indicators, or sorting.
7.  **No Broken Links:** Navigation should only occur when a valid `product.id` is available.
8.  **Selected State:** Add a visual selected state to the row when it is clicked.

## 3. Behavior Scenarios

1.  **Scenario:** The user clicks on a row in the Inventory grid.
    *   **Outcome:** The user is navigated to the Product Detail View for the corresponding product. The row should have a selected visual state.
2.  **Scenario:** The user focuses on a row in the Inventory grid using the keyboard and presses Enter or Space.
    *   **Outcome:** The user is navigated to the Product Detail View for the corresponding product. The row should have a selected visual state.
3.  **Scenario:** A row has `product.id` that is null or undefined.
    *   **Outcome:** Clicking on the row should NOT trigger any navigation. The row should not have a selected visual state.

## Stitch UI Prompt
```text
// Target Component: InventoryView row
// Description: A clickable row in the Inventory Grid that navigates to the Product Detail View.
// Layout: Tailwind CSS table row structure.
// Style: Dark mode, Tailwind CSS (slate-900/blue-500).

// Requirements:
// - Make the entire row clickable.
// - On click, navigate to the product detail page using navigationStore.goToProduct(productId).
// - Add hover effect (e.g., background-slate-800).
// - Add focus state for keyboard navigation.
// - Prevent click events on child elements from interfering with row click.
// - Retain existing styles (borders, padding, text colors).
// - Maintain the default `bg-slate-900` color for non-selected rows.
// - Maintain selected styles when focused.

// Data Slots:
// - productId: String - The ID of the product.
// - productName: String - The name of the product.
// - productBrand: String - The brand of the product.
// - productPrice: String - The price of the product.
// - productStock: String - The stock status of the product.

// Hints:
// - Use a button or div with onClick to wrap the row content.
// - Add tabindex="0" for keyboard focus.
// - Use CSS `:hover` and `:focus` pseudo-classes for visual effects.
// - Use navigationStore.goToProduct(productId) to handle navigation.
// - Add a className for `selected` state and add style for selected class.
// - Ensure accessibility. Use aria-label and keyboard navigation.
// - Keep other functionality of the child components such as StockBadge.
// - Avoid styling conflicts with tailwind.

// Example code before transformation:

<tr key={product.id} className="group">
    <td className="px-3 py-2.5 text-zinc-300 text-sm">{product.name}</td>
    <td className="px-3 py-2.5 text-zinc-400 text-sm">{product.id}</td>
    <td className="px-3 py-2.5 text-zinc-400 text-sm">{product.brand}</td>
    <td className="px-3 py-2.5 text-zinc-400 text-sm">{product.price}</td>
    <td className="px-3 py-2.5 text-zinc-400 text-sm">{product.stock}</td>
</tr>

```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
