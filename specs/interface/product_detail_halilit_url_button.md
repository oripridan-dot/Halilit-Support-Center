# Spec: Product Detail - Halilit URL Button
**Target:** `src/components/ProductDetail/HalilitURLButton.tsx`

## Overview
This React component renders a button that links to the product's official page on the Halilit website. The button's visibility depends on the existence of a valid Halilit URL associated with the product data. The button styling is consistent with the dark theme.

## Requirements
- The component must be a functional React component.
- The component must receive a `halilitUrl` prop, which can be either a valid URL string or `null` or `undefined`.
- If `halilitUrl` is a valid URL string, the button must render.
- If `halilitUrl` is `null` or `undefined`, the button must NOT render (return null).
- The button text must be "View on Halilit Website".
- The button must open the Halilit URL in a new tab/window.
- The button must use Tailwind CSS for styling, adhering to the dark theme (slate-900/blue-500 palette).
- The button must have appropriate accessibility attributes (e.g., `aria-label`).

## Data Contract

**Props:**

```typescript
interface HalilitURLButtonProps {
  halilitUrl: string | null | undefined;
}
```

## Behavior Scenarios
- **Scenario:** Valid Halilit URL Provided
  - Input: `halilitUrl = "https://www.halilit.com/product/my-awesome-toy"`
  - Outcome: A button is rendered with the text "View on Halilit Website". Clicking the button opens the URL in a new tab. The button is styled according to the dark theme (slate-900 background, blue-500 text on hover). The button has `aria-label="View my-awesome-toy on Halilit Website"`.

- **Scenario:** Null Halilit URL Provided
  - Input: `halilitUrl = null`
  - Outcome: The component renders nothing (returns null).

- **Scenario:** Undefined Halilit URL Provided
  - Input: `halilitUrl = undefined`
  - Outcome: The component renders nothing (returns null).

- **Scenario:** Empty String Halilit URL Provided
  - Input: `halilitUrl = ""`
  - Outcome: The component renders nothing (returns null).  This is technically invalid but should be treated as if there is no Halilit URL.

## Out of Scope
- The fetching of the product data is out of scope.  This component only handles the display of the button, given a URL.
- Error handling for invalid URLs (e.g., malformed URLs) is out of scope.  The component assumes the URL, if present, is valid.
- The specific product detail page layout is out of scope.  This component is just the button.
