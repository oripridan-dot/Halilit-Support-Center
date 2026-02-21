# Spec: Product Detail Sourcing Badge
**Target:** `src/components/ProductDetail/SourcingBadge.tsx`

## Overview
This component displays a badge indicating the sourcing status of a product. The badge visually communicates whether the product is sourced internally, externally, or if the sourcing information is unavailable.  The badge will use color-coding and text labels to clearly convey this information to the user.

## Requirements
- The component must accept a `sourcing` prop, which is a string indicating the sourcing status.
- The component must display a badge with appropriate text and color based on the `sourcing` prop value.
- The following sourcing statuses must be supported:
    - "internal": Display a green badge with the text "Internal Sourcing".
    - "external": Display a blue badge with the text "External Sourcing".
    - `null` (or undefined): Display a gray badge with the text "Sourcing Unknown".
- The badge must be styled using Tailwind CSS, adhering to the dark theme's color palette (slate-900/blue-500).
- The component must be implemented in TypeScript.
- The component must be reusable across different product detail pages.
- The badge should be visually distinct and easily noticeable.

## Data Contract
```typescript
interface SourcingBadgeProps {
  sourcing: "internal" | "external" | null | undefined;
}
```

## Behavior Scenarios
- **Scenario:** Internal Sourcing
  - Input: `sourcing="internal"`
  - Outcome: Renders a badge with a green background and the text "Internal Sourcing".  Text should be `slate-900` and background `green-500`.

- **Scenario:** External Sourcing
  - Input: `sourcing="external"`
  - Outcome: Renders a badge with a blue background and the text "External Sourcing". Text should be `slate-900` and background `blue-500`.

- **Scenario:** Unknown Sourcing
  - Input: `sourcing=null`
  - Outcome: Renders a badge with a gray background and the text "Sourcing Unknown". Text should be `slate-900` and background `gray-500`.

- **Scenario:** Undefined Sourcing
  - Input: `sourcing=undefined`
  - Outcome: Renders a badge with a gray background and the text "Sourcing Unknown". Text should be `slate-900` and background `gray-500`.

## Out of Scope
- This specification does not cover fetching the sourcing data. It only covers displaying the badge based on a prop.
- Error handling for invalid `sourcing` prop values is not included. Invalid values are assumed to never occur.
- Badge styling beyond background color and text color is not covered.
