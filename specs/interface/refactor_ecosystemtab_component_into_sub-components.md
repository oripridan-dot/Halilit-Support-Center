# Spec: Refactor EcosystemTab Component into Sub-components

**Version:** 1.0
**Component:** `frontend/src/components/ProductDetail/EcosystemTab.tsx`

## Purpose
To improve the maintainability, readability, and reusability of the `EcosystemTab` component by breaking it down into smaller, focused sub-components. This refactoring will follow the Single Responsibility Principle, making each sub-component easier to understand, test, and modify independently.

## Requirements

1.  **Component Decomposition:** Refactor `EcosystemTab.tsx` into the following sub-components:
    *   `RelatedProducts.tsx`: Displays the list of related products.
    *   `Integrations.tsx`: Displays the list of integrations.
    *   `EcosystemLoading.tsx`: Displays the loading state for the ecosystem tab.
    *   `EcosystemError.tsx`: Displays the error state for the ecosystem tab.
    *   `EcosystemEmpty.tsx`: Displays the empty state for the ecosystem tab.

2.  **Data Flow:** The `EcosystemTab` component should remain responsible for fetching the ecosystem data and managing the optimistic pin/unpin mutation using React Query. It should then pass the relevant data to the sub-components for rendering.

3.  **Single Responsibility Principle:** Each sub-component should have a single, well-defined responsibility. For example, `RelatedProducts.tsx` should only be responsible for rendering the list of related products and handling user interactions related to pinning/unpinning accessories.

4.  **Reusability:** The sub-components should be designed to be reusable in other parts of the application if needed.

5.  **Maintain Existing Functionality:** The refactoring should not introduce any new bugs or regressions. All existing functionality, including the optimistic pin/unpin mutation, must continue to work as expected.

6.  **Tailwind CSS:** Use Tailwind CSS classes consistently throughout all sub-components to maintain a uniform look and feel.

## Behavior Scenarios

1.  **Loading State:** When the ecosystem data is being fetched, the `EcosystemTab` component should display the `EcosystemLoading.tsx` component.
2.  **Error State:** If there is an error fetching the ecosystem data, the `EcosystemTab` component should display the `EcosystemError.tsx` component, passing the error message to be displayed.
3.  **Empty State:** If the ecosystem data is empty (i.e., no related products or integrations), the `EcosystemTab` component should display the `EcosystemEmpty.tsx` component.
4.  **Data Display:** When the ecosystem data is successfully fetched, the `EcosystemTab` component should pass the related products data to the `RelatedProducts.tsx` component and the integrations data to the `Integrations.tsx` component.
5.  **Pin/Unpin Accessory:** Clicking the pin/unpin button in the `RelatedProducts.tsx` component should trigger the optimistic update mutation in the `EcosystemTab` component, and the UI should reflect the change immediately.

## Stitch UI Prompt

```
Refactor the EcosystemTab component into smaller, focused sub-components using React and Tailwind CSS. The EcosystemTab component is responsible for fetching data and managing the pin/unpin mutation using React Query. It should pass data to the following sub-components:

- RelatedProducts.tsx: Displays a list of related products in a horizontal scrollable list of cards with a "Pin" button. Each card should contain the accessory's image, name, and description. Use a flex container with space-x-4 and overflow-x-auto.
- Integrations.tsx: Displays a list of integrations in a similar horizontal scrollable list of cards. Each card should contain the integration's logo, name, and description. Use a flex container with space-x-4 and overflow-x-auto.
- EcosystemLoading.tsx: Displays a loading skeleton with shimmer effect. Use animate-shimmer class.
- EcosystemError.tsx: Displays an error message in a red box. Use bg-red-100 border border-red-400 text-red-700 classes.
- EcosystemEmpty.tsx: Displays a message indicating that no data is available. Use text-zinc-400 classes.

The layout should be a vertical Flexbox with items-start.
The background color is slate-900.
The text color is zinc-400.
Spacing should be 4 between items.
Use rounded-lg and shadow-md for card styling.
Use aspect-w-4 and aspect-h-3 for image containers.

Data Slots:

Related Products:
- Product Image: [image_url]
- Product Name: [name]
- Product Description: [description]
- Pin Button: Displays "Pin" or "Unpin" based on the _pinned state

Integrations:
- Integration Logo: [logo_url]
- Integration Name: [name]
- Integration Description: [description]

Error Component:
- Error Message: [error_message]

Empty Component:
- Empty Message: "No related products or integrations available."
```

## Verification Commands

- `pnpm tsc --noEmit`
- `pnpm run lint`
