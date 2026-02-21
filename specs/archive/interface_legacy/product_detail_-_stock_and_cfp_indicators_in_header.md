# Spec: Product Detail - Stock and CfP Indicators in Header

**Version:** 1.0
**Component:** `frontend/src/components/ProductDetail/ProductDetailHeader.tsx`

## 1. Purpose

To prominently display stock status and "Call for Price" (CfP) indicators in the Product Detail header, enabling operators to quickly assess product availability and pricing at a glance. This directly addresses the "Aggressive Out-of-Stock Signaling" and "Pricing Clarity" business goals.

## 2. Requirements

1.  **Data Source:** The `ProductDetailHeader` component MUST consume the `ConductorProduct` object, which includes the `stock` (number | null) and `price` (number | null) properties.

2.  **Stock Status Indicator:**
    *   If `product.stock === 0`, display a red "OUT OF STOCK" badge with white text.
    *   If `product.stock === null`, display an amber "UNCONFIRMED" badge with dark text.
    *   If `product.stock > 0`, display a green "IN STOCK" badge with white text.
    * The badges must be displayed to the immediate right of the product name, and top-aligned.

3.  **Call for Price (CfP) Indicator:**
    *   If `product.price === null || product.price === 0`, display a prominent "Call for Price" label and a Copy SKU button. The "Call for Price" label must be near the price, but not overlapping it. Follow the implementation detailed in `specs/interface/copy_sku_button_for_product_detail_page.md`.

4.  **Precedence:** If a product is both out of stock (`stock === 0`) and "Call for Price" (`price === null || price === 0`), the "OUT OF STOCK" badge MUST take precedence, appearing before the "Call for Price" indicator and Copy SKU button.

5.  **Dark Theme Styling:** Use Tailwind CSS to style the indicators, adhering to the dark theme (slate-900 background, blue-500 accents).

6.  **Accessibility:** Ensure the indicators have proper ARIA labels for screen readers and sufficient color contrast for readability.

## 3. Behavior Scenarios

1.  **Scenario:** Product A has `stock: 0` and `price: null`.
    *   **Outcome:** The Product Detail header displays a red "OUT OF STOCK" badge. It also displays a Copy SKU button.

2.  **Scenario:** Product B has `stock: null` and `price: 129.99`.
    *   **Outcome:** The Product Detail header displays an amber "UNCONFIRMED" badge. The price is displayed as "₪129.99".

3.  **Scenario:** Product C has `stock: 5` and `price: null`.
    *   **Outcome:** The Product Detail header displays a green "IN STOCK" badge. The page also displays a Copy SKU button.

4.  **Scenario:** Product D has `stock: 10` and `price: 249.99`.
    *   **Outcome:** The Product Detail header displays a green "IN STOCK" badge. The price is displayed as "₪249.99".

## Stitch UI Prompt
```text
// Target Component: ProductDetailHeader
// Description: React component displaying product title, stock status and price

// Layout:
//  - Flexbox container with horizontal alignment.
//  - Product title (text-2xl font-semibold text-white)
//  - Conditional stock badge (StockBadge component)
//  - Conditional "Call for Price" indicator and Copy SKU button.
// Style:
//  - Dark mode, Tailwind CSS. slate-900 background. blue-500 accents.
//  - Font: Inter, text-white for main text, slate-400 for secondary text.
// Data Slots:
//  - productName: string (e.g., "Roland FP-30X")
//  - stockStatus: "IN STOCK" | "OUT OF STOCK" | "UNCONFIRMED" | null
//  - price: string (e.g., "₪249.99") or null for "Call for Price"
//  - sku: string (e.g., "FP30X-BK")

// Component Hierarchy:
//  - Flex container (justify-between items-center)
//    - h1.text-2xl.font-semibold.text-white {productName}
//    - div (flex items-center space-x-2)
//      - StockBadge component (conditional, only render if stockStatus is not null)
//        - span (inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold)
//          - Text: {stockStatus}
//      - Conditional "Call for Price"
//        - If price is null or zero, render a "Call for Price" label and a "Copy SKU" button.  Follow existing designs for these components.

// Spacing:
//  - Header padding: p-6
//  - Space between title and stock badge: space-x-4
//  - Space between Stock badge and Call for Price: space-x-2

// Tailwind color tokens: use EXACT colors and shades already defined in other console components.
// - Text color: text-white, text-slate-400.
// - Background color: bg-slate-900, bg-red-500, bg-amber-500, bg-green-500.

Use a Bento Grid layout to position stock badge and call for price indicators adjacent to the header. Be economical.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
