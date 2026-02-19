# Spec: Product Detail - Side-by-Side Pricing

**Version:** 1.0
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## 1. Purpose

To display the IL price and Eilat price side-by-side on the Product Detail screen, enabling operators to quickly compare prices and provide accurate information to customers. This directly supports the "Pricing Clarity" business goal.

## 2. Requirements

1. **Dual Price Display:** On the Product Detail View, when both `price` (IL price) and `price_eilat` are present and non-null, they MUST be displayed side-by-side in a clear and visually distinct manner.
2. **Currency Labels:** Each price MUST be clearly labeled with its corresponding currency: "₪ (IL)" for `price` and "₪ (Eilat)" for `price_eilat`.
3. **CfP Handling:** If `price` is null, display "Call for Price (IL)". If `price_eilat` is null, display "Not Available (Eilat)". If both are null, display only "Call for Price".
4. **Layout:** The prices and labels should be arranged horizontally, separated by a visual separator (e.g., a vertical line or a small amount of space).
5. **Accessibility:** Ensure that the price information is accessible to screen reader users by providing appropriate `aria-label` attributes.
6. **Styling:** Use Tailwind CSS classes to style the price display for clarity and visual appeal. Ensure sufficient contrast between the text and background.
7. **Edge Cases:**
    - If only `price` is available, display only the IL price.
    - If only `price_eilat` is available, display only the Eilat price.
8. **Component Integration:** This component MUST work seamlessly with the existing "Copy SKU" button and "Sourcing Badge" components.

## 3. Behavior Scenarios

1. **Scenario:** The Product Detail screen loads for a product with `price: 100` and `price_eilat: 85`.
   * **Outcome:** The display shows "₪ (IL): 100 | ₪ (Eilat): 85".
2. **Scenario:** The Product Detail screen loads for a product with `price: null` and `price_eilat: 85`.
   * **Outcome:** The display shows "Call for Price (IL) | ₪ (Eilat): 85".
3. **Scenario:** The Product Detail screen loads for a product with `price: 100` and `price_eilat: null`.
   * **Outcome:** The display shows "₪ (IL): 100 | Not Available (Eilat)".
4. **Scenario:** The Product Detail screen loads for a product with `price: null` and `price_eilat: null`.
   * **Outcome:** The display shows "Call for Price".

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
