# Spec: Add Stock Field to ConductorProduct + Fix InventoryView Field Access

**Version:** 1.0
**Files:**

- `frontend/src/hooks/useConductorCatalog.ts`
- `frontend/src/components/views/InventoryView.tsx`

## 1. Problem

The `inventory_stock_status_indicators` spec references `product.stock` but `ConductorProduct`
has no `stock` field. Additionally, `InventoryView` has field access mismatches introduced by
the swarm (e.g. accessing non-existent fields).

## 2. ConductorProduct Stock Field

Add to the `ConductorProduct` interface in `useConductorCatalog.ts`:

```ts
/**
 * Stock status from Halilit inventory (Commercial source).
 * null = unconfirmed (no data), 0 = out of stock, >0 = in stock (quantity).
 */
stock?: number | null;
```

This field is optional because older catalog entries may not have it.

## 3. InventoryView Requirements

### 3.1 Correct Field Usage

All product field reads MUST use `ConductorProduct` shape:

| InventoryView uses      | Should be                                             |
| ----------------------- | ----------------------------------------------------- |
| `product.name`          | ✅ correct                                            |
| `product.brand`         | ✅ correct                                            |
| `product.price`         | ✅ correct (NOT `product.price_il`)                   |
| `product.price_eilat`   | ✅ correct                                            |
| `product.image_url`     | ✅ correct (NOT `product.display?.hero_image`)        |
| `product.specs`         | ✅ correct (NOT `product.specifications?.specs_dict`) |
| `product.tier`          | ✅ correct                                            |
| `product.data_status`   | ✅ correct (NOT `product.status`)                     |
| `product.quality_score` | ✅ correct                                            |

### 3.2 Stock Status Visual Rules

Based on `product.stock`:

| Condition                                        | Border             | Badge                     |
| ------------------------------------------------ | ------------------ | ------------------------- |
| `product.stock === 0`                            | `border-red-500`   | "OUT OF STOCK" red badge  |
| `product.stock == null \|\| stock === undefined` | `border-amber-500` | "UNCONFIRMED" amber badge |
| `product.stock > 0`                              | normal             | none                      |

### 3.3 CfP Indicator

If `product.price === 0 || !product.price` → show "CfP" amber chip on the row.
Out-of-stock indicators take precedence over CfP indicators if both apply.

### 3.4 Click Navigation

Clicking a product row MUST call `useNavigationStore().goToProduct(product.id)`.

### 3.5 Search + Sort

- Search input MUST be debounced (300ms) — filter on `search_text` field for best performance.
- Default sort: in-stock products first, then unconfirmed, then out-of-stock, then CfP.

## 4. Behavior Scenarios

**S1:** `stock === 0` → red border + "OUT OF STOCK" badge visible.
**S2:** `stock === null` → amber border + "UNCONFIRMED" badge visible.
**S3:** `stock > 0` → no border, no badge.
**S4:** Click row → navigates to ProductDetailView for that product.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
