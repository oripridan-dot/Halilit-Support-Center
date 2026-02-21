# Spec: Display "Verified" Badge on Accessory Cards

**Version:** 1.0
**Component:** `frontend/src/components/ProductDetail/EcosystemTab.tsx`

## Purpose

To clearly indicate which related products and integrations have been officially verified as compatible, enhancing operator trust and driving attachment rates (Business Goal #1). The current EcosystemTab displays related products and integrations, but does not distinguish between verified and unverified items.

## Requirements

1.  **Data Source Modification:** The `/api/products/{product_id}/ecosystem` endpoint MUST be modified to include a boolean field `is_verified` in both the `related_products` and `integrations` objects.

2.  **Data Contract Update:** The TypeScript interfaces for `RelatedProduct` and `Integration` MUST be updated to include the `is_verified` field:

    ```typescript
    interface RelatedProduct {
      product_id: string;
      name: string;
      description: string;
      image_url: string;
      product_url: string;
      is_verified: boolean; // NEW FIELD
    }

    interface Integration {
      integration_id: string;
      name: string;
      description: string;
      logo_url: string;
      integration_url: string;
      is_verified: boolean; // NEW FIELD
    }
    ```

3.  **"Verified" Badge Display:** If `is_verified` is `true` for a related product or integration, a "Verified" badge MUST be displayed on the corresponding card.
       *  Use existing `StockBadge` with `status="VERIFIED"` to display a styled "Verified" badge.
       *  The badge must be displayed at the top right corner of the card.

4.  **Badge Styling:** The "Verified" badge MUST have a green background and white text for visual distinction, using these Tailwind classes: `bg-green-500 text-white px-2 py-1 rounded-md text-xs font-semibold`.

5.  **Badge Absence:** The "Verified" badge MUST NOT be displayed if `is_verified` is `false` or `null`/`undefined`.

6.  **Accessibility:** The badge should have an appropriate ARIA label (e.g., `aria-label="Verified Accessory"`).

## Behavior Scenarios

1.  **Scenario:** A related product has `is_verified: true`.
    *   **Outcome:** The Product Tile for that related product displays a "Verified" badge with a green background and white text in the top right corner.
2.  **Scenario:** An integration has `is_verified: false`.
    *   **Outcome:** The Product Tile for that integration does not display a "Verified" badge.
3.  **Scenario:** The API returns an error.
    *   **Outcome:** An error message is displayed, and no product or integration cards are rendered.

## Stitch UI Prompt

```text
// Target Component: EcosystemTab — related product and integration cards
// Goal: Add a green "Verified" badge in the top-right corner if data.is_verified === true.

// Layout:
// The EcosystemTab uses a flexbox layout with related products and integrations displayed in distinct sections.
// Each product and integration is displayed within a card. Use rounded corners and a shadow for the cards.
// Use a grid layout for the related products.

// Visual Style:
// Adhere to the dark theme.
// - Background: slate-900 for container
// - Text: zinc-400 for general text, white for headings
// - Card background: slate-800
// - Verified badge: green-500 background, white text
// - Tailwind color tokens only: slate-900, zinc-400, white, green-500.

// Component Hierarchy:
// - div (container, p-4, slate-900)
//   - h2 (section heading, text-lg, font-semibold, mb-2)
//   - div (grid or flex container for cards)
//     - div (card, slate-800, rounded-lg, shadow-md, relative)
//       - ImageWithFallback or img (product/integration image)
//       - div (card content)
//         - h3 (name, font-semibold)
//         - p (description)
//       - span (Verified badge, absolute position, top-2 right-2, green-500 bg, white text, rounded, px-2, py-1, text-xs, font-semibold) — RENDER THIS CONDITIONALLY based on `is_verified`

// Data Slots:
// The code needs to dynamically render the badge based on a boolean prop "is_verified". The value will come from RelatedProduct.is_verified or Integration.is_verified, depending on the type of card.

// Spacing: Use Tailwind spacing utilities (e.g., p-4, mb-2, mt-2) to control spacing between elements.

// Instructions:
// Conditionally render a "Verified" badge in the top-right corner of each product/integration card IF the is_verified prop is true. Use absolute positioning for the badge, and style it with a green background and white text. Use the existing StockBadge component. Follow dark theme style guide precisely and use Tailwind CSS exclusively.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- `pytest backend/tests/test_ecosystem_api.py -v`
