# Spec: Enforce Data Trust Attribution for Specifications in Product Detail View

**Version:** 1.0
**Component:** `frontend/src/components/ProductDetail/ProductDetailHeader.tsx`

## Purpose

To display data trust/sourcing badges for product specifications (specs) within the `ProductDetailHeader` component, providing operators with immediate insight into the origin and reliability of the displayed specs data. This directly addresses the **Data Integrity** technical standard and enhances operator trust, supporting the overall effectiveness of the support center.

## Requirements

1.  **Data Trust Consumption:** The `ProductDetailHeader` component MUST consume the `data_trust` property from the `ConductorProduct` object. This object is already being passed to the component, so no changes to the parent component are needed.

2.  **Data Trust Mapping:** The following badge MUST be displayed, sourced directly from the `ConductorProduct.data_trust` object:

    *   **Specifications Source:** Display a `SourcingBadge` (already implemented) next to the product specifications (specs), using the `data_trust.specs_source` value as the `source` prop. If the specs source is not available in `data_trust`, use "official" as default value.
        *   The badge must be placed next to the Specs.

3.  **`SourcingBadge` Component Integration:** Reuse the existing `SourcingBadge` component (from `src/components/ProductDetail/SourcingBadge.tsx`) to render the data trust badges. Pass the appropriate source value from the `data_trust` object.

4.  **Conditional Rendering:** The `SourcingBadge` MUST only be rendered if the specifications exist.

## Stitch UI Prompt

```text
// Target Component: ProductDetailHeader
// Description: Displays the product name, price, stock status, and Call for Price indicator. It should also include the specification source badges as described below.
// Layout: Flexbox (or CSS Grid for fine-grained control). The header should have a main section displaying general product info and another section displaying prices and badges.
// Visual Style: Dark mode, Tailwind CSS, slate-900 background, blue-500 accents. Use existing Tailwind tokens for consistency.

// Component Hierarchy:
// ProductDetailHeader
//   h1 (Product Name)
//     SourcingBadge (specs source - place directly AFTER the h1, slightly smaller)
//   (Other existing components for price and stock)

// Data Slots:
// productName: "Halilit Guitar Model X" (string)
// price: "₪199.99" (string or number, formatted with currency)
// stockStatus: "IN STOCK", "OUT OF STOCK", or "UNCONFIRMED" (enum)
// sku: "HAL-12345" (string)
// specsSource: "halilit", "official", "estimated", "synthesized", "contextual", "none"

// Tailwind CSS:
// text-white, text-sm, font-medium, rounded-full, px-2, py-0.5, bg-blue-500 (example - adjust based on existing styles)
// dark:text-white, dark:bg-slate-900 (dark mode)

// Spacing: Use consistent spacing between elements (e.g., mt-2, mb-4)
// Ensure the SourcingBadge is visually aligned with the text (e.g., using flex items-center).

Design a React component that displays product details including name, price, and data provenance information. This component adheres to the Halilit dark factory's dark mode visual style. Ensure that all text displays correctly and that data trust badges align visually with the attributes to which they refer.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`