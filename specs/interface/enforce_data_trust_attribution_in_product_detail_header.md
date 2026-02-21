# Spec: Enforce Data Trust Attribution in Product Detail Header

**Version:** 1.0
**Component:** `frontend/src/components/ProductDetail/ProductDetailHeader.tsx`

## Purpose

To display data trust/sourcing badges for key product attributes (price, name, description) within the `ProductDetailHeader` component, providing operators with immediate insight into the origin and reliability of the displayed data. This directly addresses the **Data Integrity** technical standard and enhances operator trust, supporting the overall effectiveness of the support center.

## Requirements

1.  **Data Trust Consumption:** The `ProductDetailHeader` component MUST consume the `data_trust` property from the `ConductorProduct` object. This object is already being passed to the component, so no changes to the parent component are needed.

2.  **Data Trust Mapping:** The following badges MUST be displayed, sourced directly from the `ConductorProduct.data_trust` object:

    *   **Price Source:** Display a `SourcingBadge` (already implemented) next to the price, using the `data_trust.price_source` value as the `source` prop.
    *   **Name Source:** Display a `SourcingBadge` next to the product name, using the `data_trust.name_source` value as the `source` prop. If the name source is not available in `data_trust`, use "official" as default value.
    *   **Description Source:** Display a `SourcingBadge` (already implemented) below the product description (if it exists), using the `data_trust.description_source` value as the `source` prop. If there is no description, do not display.

3.  **`SourcingBadge` Component Integration:**  Reuse the existing `SourcingBadge` component (from `src/components/ProductDetail/SourcingBadge.tsx`) to render the data trust badges. Pass the appropriate source value and label from the `data_trust` object. See the mapping in requirement 2.

4.  **Conditional Rendering:** The `SourcingBadge` MUST only be rendered if the corresponding data field (price, name, description) is present and has a defined `source` in the `data_trust` object.

5.  **Styling:** The badges MUST be styled using Tailwind CSS to be visually distinct but not overwhelming. Ensure proper alignment and spacing with the product attributes.

6.  **Accessibility:**  Ensure the badges have proper ARIA labels for screen readers, indicating the source of the data.

## Behavior Scenarios

1.  **Scenario:** Product A has `data_trust: { price_source: "halilit", name_source: "official", description_source: "official" }`.
    *   **Outcome:** The Product Detail header displays the product name with an "Official" badge, the price with a "Commercial" badge, and the description with an "Official" badge below it.
2.  **Scenario:** Product B has `data_trust: { price_source: "none", name_source: "official", description_source: "synthesized" }`.
    *   **Outcome:** The Product Detail header displays the product name with an "Official" badge. The price has no badge. The description has an "AI Summary" badge below it.
3.  **Scenario:** Product C has `data_trust: { price_source: "estimated", name_source: "official", description_source: "none" }` and has no description.
    *   **Outcome:** The Product Detail header displays the product name with an "Official" badge, the price with an "Estimated" badge. There is no badge for description.

## Stitch UI Prompt
```text
// Target Component: ProductDetailHeader
// Description:  A React component that displays the product title, brand, price, and availability.

// Instructions:
// 1. Start with the existing code for ProductDetailHeader.
// 2. Add SourcingBadge components next to the Product Name and Price elements.
// 3. Also, add a SourcingBadge below the product description.
// 4. Use conditional rendering so that the SourcingBadges only appear if data is present.
// 5. The badges should display the data trust of name, price, and description.  Use the following data attributes: data_trust.name_source, data_trust.price_source, data_trust.description_source.
// 6. Use these color mappings for the badges:
//      halilit: bg-emerald-900/40 text-emerald-400 border-emerald-700
//      official: bg-blue-900/40 text-blue-400 border-blue-700
//      estimated: bg-amber-900/40 text-amber-400 border-amber-700
//      synthesized: bg-purple-900/40 text-purple-400 border-purple-700
//      contextual: bg-orange-900/40 text-orange-400 border-orange-700
//      none: bg-zinc-800 text-zinc-500 border-zinc-700
// 7. Make sure to keep all the other components and existing functionality.

// Data Slots:
// product.name: string
// product.price: number
// product.description: string
// product.data_trust.price_source: "halilit" | "official" | "estimated" | "none"
// product.data_trust.name_source:  "official" | "none"
// product.data_trust.description_source: "halilit" | "official" | "synthesized" | "none"

// Styles:
// Use Tailwind CSS for styling. Follow the dark theme of the Halilit Support Center (slate-900 background, blue-500 accents).
// The layout should be flexbox-based to align the price and badges horizontally.
// The SourcingBadge component already exists, so it just needs to be used with appropriate props.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
