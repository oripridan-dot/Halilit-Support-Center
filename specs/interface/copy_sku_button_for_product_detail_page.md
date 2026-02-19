# Spec: Copy SKU Button for Product Detail Page
**Target:** `src/components/ProductDetail/CopySKUButton.tsx`

## Overview
This specification defines a React component for the Halilit Support Center's dark factory interface. This component provides a button that allows users to quickly copy a product's Stock Keeping Unit (SKU) to their clipboard when viewing the product details. This enhances user efficiency by simplifying the process of sharing or referencing specific product SKUs.

## Requirements
- [x] The component must display a button with a clear "Copy SKU" label.
- [x] Clicking the button should copy the product's SKU to the user's clipboard.
- [x] Upon successful copy, the button's label should briefly change to "Copied!" for 2 seconds, then revert to "Copy SKU".
- [x] The component should handle potential errors during the clipboard copy operation. If an error occurs, display an error message (e.g., "Copy Failed") instead of changing to "Copied!". The error message should also disappear after 2 seconds.
- [x] The component must be visually consistent with the dark theme of the Halilit Support Center (slate-900 background, blue-500 accent).
- [x] The component must be reusable and accept the product SKU as a prop.

## Data Contract
**Props:**

```typescript
interface CopySKUButtonProps {
  sku: string;
}
```

Where:
- `sku`:  A string representing the product's Stock Keeping Unit. This value will be copied to the clipboard.

## Behavior Scenarios
- **Scenario:** Successful Copy
  - Input: User clicks the "Copy SKU" button, `sku` prop is "HAL-12345".
  - Outcome: The text "HAL-12345" is copied to the clipboard. The button label changes to "Copied!" for 2 seconds, then reverts to "Copy SKU".

- **Scenario:** Copy Failure
  - Input: User clicks the "Copy SKU" button, clipboard access is denied by the browser. `sku` prop is "HAL-12345".
  - Outcome: The text "Copy Failed" is displayed as the button label for 2 seconds, then reverts to "Copy SKU".

- **Scenario:** Empty SKU
  - Input: User clicks the "Copy SKU" button, `sku` prop is an empty string "".
  - Outcome: An alert box displays "Empty SKU: Cannot copy". The button label remains "Copy SKU". No attempt is made to write to the clipboard.

## Out of Scope
- The implementation of the product detail page itself is out of scope. This specification only covers the copy SKU button.
- Analytics tracking of button clicks.
- Complex error handling or logging beyond displaying a "Copy Failed" message.
