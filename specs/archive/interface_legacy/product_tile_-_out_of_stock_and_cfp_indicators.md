# Spec: Product Tile - Out of Stock and CfP Indicators

**Version:** 1.0
**Component:** `frontend/src/components/ProductTile.tsx`

## 1. Purpose

To visually communicate product stock status and Call for Price (CfP) status in Product Tiles, enabling operators to quickly identify out-of-stock and CfP items in lists and grids. This aligns with the "Aggressive Out-of-Stock Signaling" and "Pricing Clarity" business goals. The existing `inventory_stock_status_indicators.md` and `product_detail_-_copy_sku_button.md` cover similar functionality, but not within the ProductTile component itself.

## 2. Requirements

1.  **Red Border for Out-of-Stock:** The Product Tile MUST have a red border if the corresponding product's `stock` property is equal to 0. Use Tailwind CSS class `border-red-500`.
2.  **"OUT OF STOCK" Badge:** The Product Tile MUST display an "OUT OF STOCK" badge in a prominent position (e.g., top-right corner of the tile) if the corresponding product's `stock` property is equal to 0. The badge MUST use a red background and white text. Use Tailwind CSS classes `bg-red-500 text-white px-2 py-1 rounded-md text-xs`.
3.  **Amber Border for Unconfirmed Stock:** The Product Tile MUST have an amber border if the corresponding product's `stock` property is `null` or `undefined`. Use Tailwind CSS class `border-amber-500`.
4.  **"UNCONFIRMED" Badge:** The Product Tile MUST display an "UNCONFIRMED" badge in a prominent position (e.g., top-right corner of the tile) if the corresponding product's `stock` property is `null` or `undefined`. The badge MUST use an amber background and dark text. Use Tailwind CSS classes `bg-amber-500 text-gray-800 px-2 py-1 rounded-md text-xs`.
5.  **CfP Indicator:** If the product's `price` property is `null` or 0, the Product Tile MUST display a "Call for Price" indicator. This can be text or an icon. Suggested text: "Call for Price".
6. **CfP Placement:** Position the "Call for Price" indicator clearly and consistently, typically near the product name or a price display area.
7. **Badge Visibility:** Badges must be visible even when the tile is hovered over or selected. Use Tailwind CSS to ensure sufficient contrast and prevent the badge from being obscured.
8.  **Border Precedence:** If both stock is 0 and the price is null (Call for Price), the out of stock indicators (red border and "OUT OF STOCK" badge) MUST take precedence.
9.  **No Indicators for Confirmed Stock/Price:** If `stock` is a number greater than 0 and `price` is a number greater than 0, there MUST NOT be any border or badge related to stock or CfP status.

## 3. Behavior Scenarios

1.  **Scenario:** Product A has `stock: 0` and `price: 100`.
    *   **Outcome:** The Product Tile for Product A has a red border.
    *   **Outcome:** The Product Tile for Product A displays an "OUT OF STOCK" badge with a red background and white text.
    *   **Outcome:** The Product Tile shows the price.
2.  **Scenario:** Product B has `stock: null` and `price: 100`.
    *   **Outcome:** The Product Tile for Product B has an amber border.
    *   **Outcome:** The Product Tile for Product B displays an "UNCONFIRMED" badge with an amber background and dark text.
    *   **Outcome:** The Product Tile shows the price.
3.  **Scenario:** Product C has `stock: 10` and `price: null`.
    *   **Outcome:** The Product Tile for Product C has no border related to stock.
    *   **Outcome:** The Product Tile for Product C does not display any stock related badges.
    *   **Outcome:** The Product Tile displays "Call for Price".
4. **Scenario:** Product D has `stock: 0` and `price: null`.
    *   **Outcome:** The Product Tile for Product D has a red border.
    *   **Outcome:** The Product Tile for Product D displays an "OUT OF STOCK" badge.
    *   **Outcome:** Call for Price may or may not be displayed depending on badge location.
5. **Scenario:** Product E has `stock: 5` and `price: 150`.
    *   **Outcome:** The Product Tile for Product E has no border or stock-related badges.
    *   **Outcome:** The Product Tile shows the price.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
