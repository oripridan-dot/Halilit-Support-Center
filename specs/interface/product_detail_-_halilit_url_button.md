# Spec: Product Detail - Halilit URL Button

**Version:** 1.0
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## 1. Purpose

To provide a direct link to the Halilit product page on the Product Detail screen when available, enabling operators to quickly access additional product information and resources. This supports the "Speed of Service" business goal.

## 2. Requirements

1.  **Halilit URL Condition:** A button labeled "View on Halilit Website" (or similar) MUST be displayed on the Product Detail screen ONLY if the `halilit_url` property of the displayed product is present and a valid URL.
2.  **Button Icon:** The button MUST include a clear external link icon (e.g., using `lucide-react`).
3.  **Navigation Action:** When the "View on Halilit Website" button is clicked, the user MUST be navigated to the URL specified in the `halilit_url` property in a new tab or window. Use `window.open(product.halilit_url, '_blank')`.
4.  **URL Validation:** The component MUST perform a basic validation of the `halilit_url` to ensure it is a valid URL before rendering the button. Use a regex validator such as `/^(ftp|http|https):\/\/[^ "]+$/` to validate.
5.  **Button Placement:** The "View on Halilit Website" button MUST be placed prominently near the product's other URL links (e.g., next to the "Official Brand Page" button, if present).
6.  **Button Absence:** If the `halilit_url` property is missing, null, or an invalid URL, the "View on Halilit Website" button MUST NOT be displayed.
7.  **Styling:** The button MUST be styled to be easily identifiable and accessible using Tailwind CSS.

## 3. Behavior Scenarios

1.  **Scenario:** The Product Detail screen loads for a product with a valid `halilit_url` (e.g., `halilit_url: "https://www.halilit.com/product/example"`).
    *   **Outcome:** A "View on Halilit Website" button with an external link icon is visible on the screen.
    *   **Action:** The user clicks the "View on Halilit Website" button.
    *   **Outcome:** A new tab or window opens, navigating to `https://www.halilit.com/product/example`.

2.  **Scenario:** The Product Detail screen loads for a product with a missing `halilit_url` (e.g., `halilit_url: null`).
    *   **Outcome:** No "View on Halilit Website" button is visible on the screen.

3.  **Scenario:** The Product Detail screen loads for a product with an invalid `halilit_url` (e.g., `halilit_url: "not a url"`).
    *   **Outcome:** No "View on Halilit Website" button is visible on the screen.
