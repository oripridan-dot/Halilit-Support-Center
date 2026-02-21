# Spec: Product Detail - Ecosystem Tab Placeholder

**Version:** 1.0
**Component:** `frontend/src/components/ProductDetail/EcosystemTab.tsx`

## Purpose

To display a placeholder message in the Ecosystem Tab of the Product Detail View when no related products or integrations are available. This addresses Business Goal 1 (Maximize Attachment Rate) by prompting operators to add accessories if none are currently in the graph.

## Requirements

1.  **Data Source:** The `EcosystemTab` component MUST fetch related products and integrations from the `/api/products/{product_id}/ecosystem` endpoint on initial mount.

2.  **No Related Items Condition:** If the API returns an empty `related_products` array and an empty `integrations` array, the component MUST display a placeholder message.

3.  **Placeholder Message:** The placeholder message MUST be: "No related products or integrations found. Check official brand resources for suggestions to manually add."

4.  **Placeholder Styling:** The placeholder message MUST be styled to be visually distinct and easily readable, using Tailwind CSS classes to match the dark theme (e.g., `text-zinc-400 italic`).

5.  **Loading and Error States:** The component MUST continue to handle loading and error states as defined in the existing specification. The placeholder message MUST NOT be displayed during loading or error states.

6.  **Precedence:** The placeholder message MUST take precedence over displaying empty sections for related products and integrations. If there are no related products or integrations, only the placeholder message should be visible.

7. **Empty Array Enforcement:** Verify empty `related_products` and `integrations` are enforced in the backend API response.

## Behavior Scenarios

1.  **Scenario:** The API returns the following response:

```json
{
  "related_products": [],
  "integrations": []
}
```

*   **Outcome:** The Ecosystem Tab displays the message: "No related products or integrations found. Check official brand resources for suggestions to manually add."

2.  **Scenario:** The API returns the following response:

```json
{
  "related_products": [
    {
      "product_id": "1",
      "name": "Product A",
      "description": "Description A",
      "image_url": "image_a.jpg",
      "product_url": "url_a"
    }
  ],
  "integrations": []
}
```

*   **Outcome:** The Ecosystem Tab displays the related product "Product A" and does NOT display the placeholder message.

3.  **Scenario:** The API returns an error.

*   **Outcome:** The Ecosystem Tab displays an error message and does NOT display the placeholder message.

## Stitch UI Prompt
```text
// Target Component: EcosystemTab
// Description: A React component for the Product Detail view that displays related products and integrations. If there are no related items, a placeholder message should be displayed.
// Layout: Flexbox, single column.
// Style: Dark mode, Tailwind CSS.

// Data Slots:
// - relatedProducts: Array of { name, description, imageUrl, productUrl }
// - integrations: Array of { name, description, logoUrl, integrationUrl }

// Component Hierarchy:
// 1. Container div (flex flex-col p-4)
// 2. Conditional: If relatedProducts.length === 0 && integrations.length === 0:
//    - Placeholder message (text-zinc-400 italic)

// Spacing:
// - Padding: 4 on container div.

// Visual Style:
// - Background: slate-900
// - Text color: zinc-400 for placeholder message

// Placeholder Message:
// - Text: "No related products or integrations found. Check official brand resources for suggestions to manually add."
// - Style: italic, text-zinc-400

// Instructions:
// - The component should be written in React with Typescript.
// - Use Tailwind CSS for styling.
// - If relatedProducts and integrations are both empty arrays, display the placeholder message.
// - Prioritize clean and readable code.

//Data mapping: Check that each property in related products and integrations is correctly used
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
