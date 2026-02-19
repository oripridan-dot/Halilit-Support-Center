# Spec: Product Detail - Copy SKU Button

**Version:** 1.0
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## 1. Purpose

To provide a one-tap "Copy SKU" button on the Product Detail screen for "Call for Price" (CfP) items, enabling operators to quickly relay the SKU to the procurement team. This directly supports the "Pricing Clarity" business goal and "Speed of Service".

## 2. Requirements

1.  **CfP Condition:** The "Copy SKU" button MUST only be displayed on the Product Detail screen when the `price` property of the displayed product is `null` or 0.
2.  **Button Label:** The button's label MUST read "Copy SKU".
3.  **Button Icon:** The button MUST include a clear copy icon (e.g., using `lucide-react`).
4.  **Copy Action:** When the "Copy SKU" button is clicked, the product's `id` (Halilit SKU) MUST be copied to the clipboard.
5.  **Success Feedback:** Upon successful copy, a visual confirmation MUST be displayed to the user. This could be a brief tooltip, a temporary change in button text (e.g., "Copied!"), or a Toast notification. This feedback MUST disappear automatically after 2 seconds.
6.  **Error Handling:** If the copy to clipboard action fails (e.g., due to browser security restrictions), an error message MUST be displayed to the user, informing them that the copy failed and instructing them to manually copy the SKU. This message should also disappear automatically after 2 seconds.
7. **Placement:** The "Copy SKU" button MUST be placed prominently near the product SKU and price information on the Product Detail screen, e.g. directly next to the SKU label.
8. **Styling:** The button MUST be styled to be easily identifiable and accessible. Use Tailwind CSS to make a small button.

## 3. Behavior Scenarios

1.  **Scenario:** The Product Detail screen loads for a product with `price: null`.
    *   **Outcome:** A "Copy SKU" button with a copy icon is visible near the product SKU.
    *   **Action:** The user clicks the "Copy SKU" button.
    *   **Outcome:** The product's `id` (SKU) is copied to the clipboard.
    *   **Outcome:** A success message (e.g., "Copied!") appears briefly and disappears after 2 seconds.
2.  **Scenario:** The Product Detail screen loads for a product with `price: 99.99`.
    *   **Outcome:** The "Copy SKU" button is NOT visible.
3.  **Scenario:** The Product Detail screen loads for a product with `price: null`, and the copy to clipboard action fails.
    *   **Action:** The user clicks the "Copy SKU" button.
    *   **Outcome:** An error message is displayed, informing the user that the copy failed and instructing them to manually copy the SKU. The error message disappears after 2 seconds.
4. **Scenario:** User navigates to a product with `price: 0`.
    *   **Outcome:** A "Copy SKU" button with a copy icon is visible near the product SKU.
    *   **Action:** The user clicks the "Copy SKU" button.
    *   **Outcome:** The product's `id` (SKU) is copied to the clipboard.
    *   **Outcome:** A success message (e.g., "Copied!") appears briefly and disappears after 2 seconds.
