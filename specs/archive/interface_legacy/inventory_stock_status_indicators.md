# Spec: Inventory Stock Status Indicators

**Version:** 1.0
**Component:** `frontend/src/components/views/InventoryView.tsx`

## 1. Purpose

To visually communicate product stock status in the Inventory Master, enabling operators to quickly identify out-of-stock and unconfirmed items. This addresses the "Aggressive Out-of-Stock Signaling" business goal.

## 2. Requirements

1.  **Red Border for Out-of-Stock:** Each row in the Inventory grid MUST have a red border if the corresponding product's `stock` property is equal to 0.
2.  **"OUT OF STOCK" Badge:** Each row in the Inventory grid MUST display an "OUT OF STOCK" badge in a prominent position (e.g., top-right corner of the row) if the corresponding product's `stock` property is equal to 0.  The badge MUST use a red background and white text.
3.  **Amber Border for Unconfirmed Stock:** Each row in the Inventory grid MUST have an amber border if the corresponding product's `stock` property is `null` or `undefined`.
4.  **"UNCONFIRMED" Badge:** Each row in the Inventory grid MUST display an "UNCONFIRMED" badge in a prominent position (e.g., top-right corner of the row) if the corresponding product's `stock` property is `null` or `undefined`. The badge MUST use an amber background and dark text.
5.  **Badge Visibility:** Badges must be visible even when the row is hovered or selected.
6.  **Border Precedence:** If both stock is 0 and the price is null (Call for Price), the out of stock indicators (red border and "OUT OF STOCK" badge) MUST take precedence.
7.  **No Indicators for Confirmed Stock:** If `stock` is a number greater than 0, there MUST NOT be any border or badge related to stock status.

## 3. Behavior Scenarios

1.  **Scenario:** Product A has `stock: 0`.
    *   **Outcome:** The Inventory grid row for Product A has a red border.
    *   **Outcome:** The Inventory grid row for Product A displays an "OUT OF STOCK" badge with a red background and white text.
2.  **Scenario:** Product B has `stock: null`.
    *   **Outcome:** The Inventory grid row for Product B has an amber border.
    *   **Outcome:** The Inventory grid row for Product B displays an "UNCONFIRMED" badge with an amber background and dark text.
3.  **Scenario:** Product C has `stock: 5`.
    *   **Outcome:** The Inventory grid row for Product C has no stock-related border.
    *   **Outcome:** The Inventory grid row for Product C does not display any stock-related badge.
4.  **Scenario:** Product D has `stock: 0` and `price: null`.
    *   **Outcome:** The Inventory grid row for Product D has a red border.
    *   **Outcome:** The Inventory grid row for Product D displays an "OUT OF STOCK" badge with a red background and white text.
    *   **Outcome:** The row also displays a "Call for Price" affordance (as per existing spec).
5.  **Scenario:** The `stock` property is missing (implicitly `undefined`).
    *   **Outcome:** The Inventory grid row has an amber border.
    *   **Outcome:** The Inventory grid row displays an "UNCONFIRMED" badge.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
