# Spec: Fix Canonical Product Type

**Version:** 1.0
**Files:** `frontend/src/types/index.ts`

## 1. Problem

`types/index.ts` currently declares `Product = IngestionProductDraft` — the backend
pipeline model (`halilit_id`, `product_name`, `price_il`, `display?.hero_image`).

The actual catalog API returns a **different, flat shape** defined as `ConductorProduct`
in `frontend/src/hooks/useConductorCatalog.ts`:
`id`, `name`, `brand`, `price`, `price_eilat`, `image_url`, `specs`, `data_trust`, etc.

This mismatch causes silent runtime errors and wrong field access in all components.

## 2. Requirements

1. **Remove** the `Product = IngestionProductDraft` alias from `types/index.ts`.
2. **Import and re-export** `ConductorProduct` from `../hooks/useConductorCatalog` as the
   canonical `Product` type:
   ```ts
   export type { ConductorProduct } from "../hooks/useConductorCatalog";
   export type Product = ConductorProduct;
   ```
3. **Keep** `IngestionProductDraft` exported for any backend-facing utilities that need it
   (re-export from `./generated` as `PipelineProduct`):
   ```ts
   export type PipelineProduct = IngestionProductDraft;
   ```
4. **Keep** all other exports in `types/index.ts` unchanged (BrandIdentity, SpecItem, etc.).
5. **Remove** the `formatPrice` helper (it uses `(product as any).price` cast — no longer needed
   since `ConductorProduct.price` is directly typed).
6. **Update** `OptimizedProduct` alias:
   ```ts
   export type OptimizedProduct = ConductorProduct; // was IngestionProductDraft
   ```

## 3. Acceptance Criteria

- `import type { Product } from '../types'` in any component gives `ConductorProduct` shape.
- `product.price`, `product.name`, `product.id`, `product.image_url`, `product.specs`,
  `product.data_trust` all resolve correctly without `as any` casts.
- No TypeScript errors introduced.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
