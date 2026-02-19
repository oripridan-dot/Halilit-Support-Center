# Spec: Product Detail - Sourcing Badge

**Version:** 1.0
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## 1. Purpose

To visually indicate the source of truth for different data points displayed on the Product Detail screen, reinforcing data integrity and operator trust. This directly addresses the "Data Integrity" technical standard.

## 2. Requirements

1.  **Badge Display:** A small badge (e.g., a stylized icon or text label) MUST be displayed next to each data point on the Product Detail screen indicating its source.
2.  **Data Point Scope:** The badges MUST be applied to the following data points:
    *   Product Name
    *   Brand Name
    *   Price (both IL and Eilat)
    *   Specifications (each key-value pair)
    *   Image
3.  **Source Mapping:**
    *   **Product Name:** "Official Scout"
    *   **Brand Name:** "Official Scout"
    *   **Price (IL & Eilat):** "Commercial Scout"
    *   **Specifications:** "Official Scout"
    *   **Image:** "Official Scout"
4.  **Badge Styling:** The badge MUST be subtle and not distract from the data itself. Use a light background color and a dark text color for contrast and readability. Use Tailwind CSS to create visually distinct badges for each data source, for example:
    *   Official Scout: `bg-blue-100 text-blue-800 text-xs font-semibold mr-2 px-2.5 py-0.5 rounded dark:bg-blue-700 dark:text-blue-300`
    *   Commercial Scout: `bg-green-100 text-green-800 text-xs font-semibold mr-2 px-2.5 py-0.5 rounded dark:bg-green-700 dark:text-green-300`
5.  **Badge Absence:** If a specific data point is missing (e.g., a product has no price), the badge for that data point MUST NOT be displayed.
6.  **Accessibility:** The badge MUST have an `aria-label` attribute that describes the source of the data for screen reader users. For example: `<span aria-label="Source: Official Scout">…</span>`
7.  **JIT Override:** If the JIT stream provides updated data (name, brand, price), the badge MUST dynamically update to reflect the JIT stream, or a combined badge (Official Scout + JIT). This should only happen once the JIT stream has completed or sent a valid snap with the value.

## 3. Behavior Scenarios

1.  **Scenario:** The Product Detail screen loads for a product with a name, brand, price, and specifications.
    *   **Outcome:** Each of these data points has a corresponding source badge displayed next to it.
    *   **Outcome:** The name and brand badges display "Official Scout".
    *   **Outcome:** The price badge displays "Commercial Scout".
    *   **Outcome:** The specifications badges display "Official Scout".
2.  **Scenario:** The Product Detail screen loads for a product with no price (`price: null`).
    *   **Outcome:** The price field displays "Call for Price".
    *   **Outcome:** The "Call for Price" text DOES NOT have a source badge next to it. The SKU has the "Commercial Scout" badge.
3.  **Scenario:** The Product Detail screen loads and the JIT stream updates the product name.
    *   **Outcome:** The product name is updated with the value from the JIT stream.
    *   **Outcome:** The badge next to the product name now displays "JIT" or "Official Scout + JIT" depending on the design.
4. **Scenario:** The Product Detail screen loads with an invalid image.
    * **Outcome:** The placeholder image is displayed.
    * **Outcome:** There is no source badge displayed on the placeholder image since its value is derived from the component itself.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
