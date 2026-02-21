# Spec: Product Tile - Ethically Sourced Badge

**Version:** 1.0
**Component:** `frontend/src/components/ProductTile.tsx`

## 1. Purpose

To display an "Ethically Sourced" badge on Product Tiles when this information is available, enhancing data transparency and supporting informed purchasing decisions for operators. This feature complements existing sourcing badges, providing a more granular view of a product's ethical sourcing status.

## 2. Requirements

1.  **Ethical Sourcing Data:** The `ProductTile` component MUST consume ethical sourcing data, when available. The badge MUST display a 'Ethically Sourced' status when product's `ethical_sourcing` property is `Ethically Sourced`.
2.  **Badge Display:** If the `ethical_sourcing` property is `Ethically Sourced`, the Product Tile MUST display an "Ethically Sourced" badge in a prominent position, such as the bottom-left corner of the tile.

3.  **Badge Styling:**
    *   Use a green background (e.g., `bg-green-500`) and white text (e.g., `text-white`).
    *   The badge MUST be visually distinct but not overwhelming. Use Tailwind CSS classes such as `px-2 py-1 rounded-md text-xs font-semibold`.
4.  **Badge Absence:** The "Ethically Sourced" badge MUST NOT be displayed if the `ethical_sourcing` property is not equal to `Ethically Sourced` or is null/undefined.
5.  **Data Source:** Ethical Sourcing data should be part of the `ConductorProduct` interface. If not, then it should be added to the interface. The values include 'Ethically Sourced', 'Partially Sourced', 'Unknown Sourcing'.

6.  **Position:** position the badge in the bottom left.

## 3. Behavior Scenarios

1.  **Scenario:** Product A has `ethical_sourcing: 'Ethically Sourced'`.
    *   **Outcome:** The Product Tile for Product A displays an "Ethically Sourced" badge with a green background and white text in the bottom left corner.
2.  **Scenario:** Product B has `ethical_sourcing: 'Partially Sourced'`.
    *   **Outcome:** The Product Tile for Product B does NOT display an "Ethically Sourced" badge. Other badges can be displayed on the product tile.
3.  **Scenario:** Product C has `ethical_sourcing: null`.
    *   **Outcome:** The Product Tile for Product C does NOT display an "Ethically Sourced" badge.

## 4. ConductorProduct interface

Update `ConductorProduct` interface in `useConductorCatalog.ts`:

```ts
interface ConductorProduct {
  id: string;
  name: string;
  brand: string;
  category?: string;
  subcategory?: string;
  price?: number | null;
  price_eilat?: number | null;
  image_url?: string;
  official_url?: string;
  stock?: number | null;
  /**
   * 'Ethically Sourced' | 'Partially Sourced' | 'Unknown Sourcing' | null.
   */
  ethical_sourcing?: string | null;
}
```

## Stitch UI Prompt
```text
// Target Component: ProductTile
// Description:  A React component that displays a product's image, name, and potentially an "Ethically Sourced" badge. Use tailwind styling.

// Layout:
// The ProductTile component should be a flex container with the image at the top, and the product name below.
// The "Ethically Sourced" badge, when present, should be positioned in the bottom-left corner of the tile. Use absolute positioning for this.

// Visual Style:
// Use a dark mode theme with slate-900 for the background and blue-500 for accents.
// - The Ethically Sourced badge: background-color: green-500; text-color: white; font-size: text-xs; rounded-md; padding: px-2 py-1

// Data Slots:
// - image_url: The URL of the product image.
// - product_name: The name of the product.
// - ethical_sourcing: string ('Ethically Sourced' | 'Partially Sourced' | 'Unknown Sourcing' | null). Show "Ethically Sourced" only if the value equals 'Ethically Sourced'.

// Implementation Details:
// - Use conditional rendering to only display the badge if ethical_sourcing is 'Ethically Sourced'.
// - Place the badge at the bottom left of the tile, use position: absolute.
// - Make sure text is accessible.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
