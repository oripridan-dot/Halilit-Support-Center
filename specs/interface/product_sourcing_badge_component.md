# Spec: Product Sourcing Badge Component
**Target:** src/components/ProductSourcingBadge.tsx

## Overview
This component visually represents the sourcing status of a product in the Halilit Support Center Dark Factory. It displays a badge with text and color indicating whether the product is internally sourced, externally sourced, or has an unknown sourcing status.

## Requirements
- The component must accept a `sourcingStatus` prop, which determines the badge's appearance and text.
- The component must display different text and background colors based on the `sourcingStatus` prop.
- The component must handle three distinct sourcing statuses: "internal", "external", and "unknown".
- The component must be styled using Tailwind CSS, fitting the dark theme of the Halilit Support Center.
- The component must be implemented as a functional React component using TypeScript.
- The component must be accessible and provide appropriate contrast for readability.

## Data Contract

**Props:**

```typescript
interface ProductSourcingBadgeProps {
  sourcingStatus: "internal" | "external" | "unknown";
}
```

## Behavior Scenarios

- **Scenario:** Internal Sourcing
  - Input: `sourcingStatus="internal"`
  - Outcome: Renders a badge with the text "Internal" and a green background (e.g., `bg-green-600`)

- **Scenario:** External Sourcing
  - Input: `sourcingStatus="external"`
  - Outcome: Renders a badge with the text "External" and a blue background (e.g., `bg-blue-600`)

- **Scenario:** Unknown Sourcing
  - Input: `sourcingStatus="unknown"`
  - Outcome: Renders a badge with the text "Unknown" and a gray background (e.g., `bg-gray-600`)

## Out of Scope
- Handling of more than the three specified sourcing statuses.
- Implementing any interactive functionality.
- The component's placement or styling within a larger layout.
- Internationalization of the badge text.

```typescript
// Target: src/components/ProductSourcingBadge.tsx
import React from 'react';

interface ProductSourcingBadgeProps {
  sourcingStatus: "internal" | "external" | "unknown";
}

const ProductSourcingBadge: React.FC<ProductSourcingBadgeProps> = ({ sourcingStatus }) => {
  let badgeText: string;
  let backgroundColorClass: string;

  switch (sourcingStatus) {
    case "internal":
      badgeText = "Internal";
      backgroundColorClass = "bg-green-600";
      break;
    case "external":
      badgeText = "External";
      backgroundColorClass = "bg-blue-600";
      break;
    default:
      badgeText = "Unknown";
      backgroundColorClass = "bg-gray-600";
      break;
  }

  return (
    <div className={`inline-flex items-center rounded-md ${backgroundColorClass} px-2 py-1 text-xs font-medium text-white`}>
      {badgeText}
    </div>
  );
};

export default ProductSourcingBadge;
```
