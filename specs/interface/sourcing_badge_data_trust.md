# Spec: SourcingBadge — data_trust Integration

**Version:** 1.0
**Files:**

- `frontend/src/components/ProductDetail/SourcingBadge.tsx` (create or update)
- `frontend/src/components/ProductDetail/JITBadge.tsx` (create or update)

## 1. Problem

`ProductDetailView` contains a local `renderBadge()` function that manually assigns badge
styles based on string literals ('Official Scout', 'Commercial Scout', etc.).

`ConductorProduct` already has a structured `data_trust` field:

```ts
data_trust: {
  price_source: "halilit" | "official" | "estimated" | "none";
  specs_source: "halilit" | "official" | "none";
  description_source: "halilit" | "official" | "synthesized" | "none";
  image_source: "halilit" | "official" | "none";
  review_source: "contextual" | "none";
}
```

These should be the single source of truth for all sourcing badges.

## 2. SourcingBadge Component

```tsx
// Props
interface SourcingBadgeProps {
  source:
    | "halilit"
    | "official"
    | "estimated"
    | "synthesized"
    | "contextual"
    | "none";
  label?: string; // Override display text
  size?: "xs" | "sm";
}
```

### 2.1 Source → Visual Mapping

| source        | Label        | Colors                                                  |
| ------------- | ------------ | ------------------------------------------------------- |
| `halilit`     | "Commercial" | `bg-emerald-900/40 text-emerald-400 border-emerald-700` |
| `official`    | "Official"   | `bg-blue-900/40 text-blue-400 border-blue-700`          |
| `estimated`   | "Estimated"  | `bg-amber-900/40 text-amber-400 border-amber-700`       |
| `synthesized` | "AI Summary" | `bg-purple-900/40 text-purple-400 border-purple-700`    |
| `contextual`  | "Reviews"    | `bg-orange-900/40 text-orange-400 border-orange-700`    |
| `none`        | "Unknown"    | `bg-zinc-800 text-zinc-500 border-zinc-700`             |

### 2.2 Component Requirements

- Small pill badge with border: `rounded-full border px-2 py-0.5 text-xs font-medium`
- `aria-label={`Data source: ${label}`}`
- Export as default from `SourcingBadge.tsx`

## 3. JITBadge Component

Shows the current streaming status of JIT intelligence for a product.

```tsx
interface JITBadgeProps {
  productId: string;
}
```

### 3.1 Status → Visual

| jitState.status   | Label                | Color          |
| ----------------- | -------------------- | -------------- |
| `idle` / no state | hidden (render null) | –              |
| `loading`         | "AI Loading…"        | blue + spinner |
| `snap`            | "AI Snap"            | cyan           |
| `intel`           | "AI Intel"           | blue           |
| `wisdom`          | "AI Wisdom"          | violet         |
| `complete`        | "AI Complete"        | emerald        |
| `error`           | "AI Error"           | red            |

## 4. Integration

In `ProductDetailView`, replace `renderBadge()` calls with:

```tsx
<SourcingBadge source={product.data_trust.price_source} />
<SourcingBadge source={product.data_trust.specs_source} />
<JITBadge productId={product.id} />
```

Remove the local `renderBadge()` function entirely.

## 5. Acceptance Criteria

- No `renderBadge()` function in ProductDetailView.
- `SourcingBadge` and `JITBadge` are standalone, reusable components.
- Colors match Three Source Rules: green=Commercial, blue=Official, orange=Contextual.
