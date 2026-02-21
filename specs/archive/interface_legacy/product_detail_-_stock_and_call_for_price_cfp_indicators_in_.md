# Spec: Product Detail - Stock and Call for Price (CfP) Indicators in Header (Refactor)

**Version:** 2.0
**Component:** `frontend/src/components/ProductDetail/ProductDetailHeader.tsx`

## 1. Purpose

To refactor the stock status and "Call for Price" (CfP) indicators in the Product Detail header to be more robust, maintainable, and visually consistent. This directly addresses the "Aggressive Out-of-Stock Signaling" and "Pricing Clarity" business goals by ensuring operators can quickly assess product availability and pricing at a glance. The current implementation has styling issues and doesn't properly reuse the StockBadge component.

## 2. Requirements

1.  **Data Source:** The `ProductDetailHeader` component MUST consume the `ConductorProduct` object, which includes the `stock` (number | null) and `price` (number | null) properties.

2.  **Stock Status Indicator:**
    *   If `product.stock === 0`, display a red "OUT OF STOCK" badge with white text, using the `StockBadge` component.
    *   If `product.stock === null`, display an amber "UNCONFIRMED" badge with dark text, using the `StockBadge` component.
    *   If `product.stock > 0`, display a green "IN STOCK" badge with white text, using the `StockBadge` component.
    * The badges must be displayed to the immediate right of the product name, and top-aligned.

3.  **Call for Price (CfP) Indicator:**
    *   If `product.price === null || product.price === 0`, display a prominent "Call for Price" label and a Copy SKU button. The "Call for Price" label must be near the price, but not overlapping it. Follow the implementation detailed in `specs/interface/copy_sku_button_for_product_detail_page.md`.

4.  **Precedence:** If a product is both out of stock (`stock === 0`) and "Call for Price" (`price === null || price === 0`), the "OUT OF STOCK" badge MUST take precedence, appearing before the "Call for Price" indicator and Copy SKU button.

5.  **Dark Theme Styling:** Use Tailwind CSS to style the indicators, adhering to the dark theme (slate-900 background, blue-500 accents).

6.  **Accessibility:** Ensure the indicators have proper ARIA labels for screen readers and sufficient color contrast for readability.

7. **StockBadge Component Reuse:** Refactor the `ProductDetailHeader` to directly use the existing `StockBadge` component for displaying stock status, ensuring consistent styling and behavior. Remove the inline implementation of the badge styles.

8. **Remove inline price styling:** Remove the inline styling for price, and instead use tailwind classes for consistency.

## 3. Behavior Scenarios

1.  **Scenario:** Product A has `stock: 0` and `price: null`.
    *   **Outcome:** The `ProductDetailHeader` displays a red "OUT OF STOCK" badge. To the right of it the component displays "Call for Price" and the "Copy SKU" button.
2.  **Scenario:** Product B has `stock: null` and `price: 99.99`.
    *   **Outcome:** The `ProductDetailHeader` displays an amber "UNCONFIRMED" badge, and the price.
3.  **Scenario:** Product C has `stock: 5` and `price: null`.
    *   **Outcome:** The `ProductDetailHeader` displays a green "IN STOCK" badge. To the right of it the component displays "Call for Price" and the "Copy SKU" button.
4.  **Scenario:** Product D has `stock: 10` and `price: 199.99`.
    *   **Outcome:** The `ProductDetailHeader` displays a green "IN STOCK" badge, and the price.

## Stitch UI Prompt

```
// Target Component: ProductDetailHeader
// Description: A React component that displays the product name, stock status, and price.
// Layout: Flexbox, justify-between
// Visual Style: Dark mode, Tailwind CSS (slate-900 background, white text, red/amber/green accents for stock badges)
// Data Slots:
//   - productName: string (e.g., "Awesome Guitar")
//   - stockStatus: "IN STOCK" | "OUT OF STOCK" | "UNCONFIRMED" | null
//   - price: string (e.g., "₪199.99") or null (if "Call for Price")
//   - sku: string (product SKU for Copy SKU button)

// Structure:
//  <header className="flex items-center justify-between p-6">
//    <div>
//      <h1 className="text-2xl font-semibold text-white">{productName}</h1>
//    </div>
//    <div className="flex items-center space-x-2">
//      {StockBadge component based on stockStatus}
//      {(price === null) ? (
//        <>
//          <span className="text-sm font-medium text-red-500">Call for Price</span>
//          <CopySKUButton sku={sku} />
//        </>
//      ) : (
//        <span className="text-white">price</span>
//      )}
//    </div>
//  </header>

// Detailed Instructions:
//  1.  Use Flexbox for the main layout to position items on the opposite sides of the header.
//  2.  Create a StockBadge component that takes a `status` prop ("IN STOCK", "OUT OF STOCK", "UNCONFIRMED") and displays a styled badge accordingly. Use Tailwind CSS for styling (bg-green-500/red-500/amber-500, text-white/gray-800).
//  3.  For "Call for Price" items (price is null):
//      - Display the text "Call for Price" using `text-sm font-medium text-red-500` classes.
//      - Include a CopySKUButton to copy the product SKU to the clipboard.
//  4.  For items with a valid price, display it using `text-white` class, formatted as ₪{price}.
//  5.  Ensure that "OUT OF STOCK" badge takes precedence if both out of stock and call for price are true.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
