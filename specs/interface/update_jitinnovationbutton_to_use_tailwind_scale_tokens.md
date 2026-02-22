# Spec: Update JitInnovationButton to Use Tailwind Scale Tokens
**Target:** src/components/JitInnovationButton.tsx

## Overview
This specification details the changes required to update the `JitInnovationButton` component to utilize Tailwind CSS scale tokens for background colors instead of hardcoded hex values. This will improve maintainability and consistency with the project's design system.

## Requirements
- [x] Replace the hardcoded hex color value used for the button's background with a corresponding Tailwind CSS color scale token.
- [x] Ensure the button's text color remains legible against the new background color.  Adjust text color using Tailwind CSS tokens if necessary.
- [x] The button should maintain its original appearance and functionality after the update, only the implementation of the color changes.
- [x] The button should use `blue-500` as the primary color.
- [x] The hover state of the button should use `blue-700` for the background.
- [x] Tailwind classes must be applied conditionally to ensure correct styling.

## Data Contract
The `JitInnovationButton` component likely accepts props, though their precise definition is not included in the request. We'll assume it accepts a `label` string and an optional `onClick` handler.

```typescript
interface JitInnovationButtonProps {
  label: string;
  onClick?: () => void;
}
```

## Behavior Scenarios
- **Scenario:** Initial Render
  - Input: `label="Innovate"`
  - Outcome: The button renders with the text "Innovate" and a background color of `blue-500`.  The text color should be white.
- **Scenario:** Hover State
  - Input: Mouse hovers over the button.
  - Outcome: The button's background color changes to `blue-700`.
- **Scenario:** Click Event
  - Input: User clicks the button.
  - Outcome: The `onClick` handler (if provided) is executed.
- **Scenario:** No onClick event
  - Input: User clicks the button and no onClick event is provided.
  - Outcome: The application renders as normal, but with no visible response to the action.

## Out of Scope
- [ ]  This spec does not cover the creation of new Tailwind CSS color scale tokens if they don't already exist. It assumes the `blue-500` and `blue-700` colors are available.
- [ ]  This spec does not include any changes to the button's size, shape, font, or other visual attributes beyond the background color and hover state.
- [ ]  This spec does not include any changes to the button's functionality or event handling beyond calling the `onClick` handler.
