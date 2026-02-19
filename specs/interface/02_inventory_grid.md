# Spec 02 — Inventory Master (Inventory Grid)

**Version:** 2.0 · Chief v9.7.0
**Component:** `frontend/src/components/views/InventoryView.tsx`
**Route state:** `currentView === 'INVENTORY'`
**Data source:** `useConductorCatalog` hook → `/api/conductor/catalog`

---

## 1. Purpose & Intent

The Inventory Master is the operator's primary working view. It must answer:

> "Show me all products — let me find any product by SKU, brand, or name in under 3 seconds."

This is a **power-user tool**: dense data, full filtering, instant sorting. Not a storefront.

---

## 2. Data Contract

### 2.1 `useConductorCatalog` returns `ConductorProduct[]`

Minimum fields consumed by this view:

```ts
interface ConductorProduct {
  id: string; // Halilit SKU (Commercial Scout — immutable)
  name: string; // Product title (Official Scout)
  brand: string; // Brand name
  category?: string; // Top-level category
  subcategory?: string; // Preferred over category for display
  price?: number | null; // IL price (₪); null = Call for Price
  price_eilat?: number | null; // Eilat price; null = not applicable
  image_url?: string; // Hero image URL
  official_url?: string; // Official brand page (verified if present)
  // Optional runtime field (may not exist in all catalog entries):
  stock?: number; // 0 = OOS; null/absent = unknown
}
```

**Source rules (read-only in this view):**

- `id` and `price` come from Commercial Scout — never modify or invent
- `name`, `image_url` come from Official Scout
- Stock data is typically absent; degrade gracefully

---

## 3. Deep-Link & Initial State

When InventoryView mounts, it reads from `navigationStore`:

```ts
searchQuery: string | null; // Pre-fills text filter input
initialCfpFilter: boolean | null; // If true → CfP toggle starts active
```

**⚠ Guard rule (non-negotiable):**
Both values may be corrupted if a navigation action was called without an arrow wrapper.
Always coerce before use:

```ts
const [filterText, setFilterText] = useState(
  typeof searchQuery === "string" ? searchQuery : "",
);
const [cfpOnly, setCfpOnly] = useState(initialCfpFilter ?? false);
```

---

## 4. Filter State

| State            | Type                             | Default                      | Description                     |
| ---------------- | -------------------------------- | ---------------------------- | ------------------------------- |
| `filterText`     | `string`                         | `""` / `searchQuery`         | Free-text search                |
| `brandFilter`    | `string`                         | `""`                         | Selected brand (empty = all)    |
| `categoryFilter` | `string`                         | `""`                         | Selected category (empty = all) |
| `cfpOnly`        | `boolean`                        | `false` / `initialCfpFilter` | Show only Call-for-Price        |
| `sortField`      | `"name"\|"id"\|"price"\|"brand"` | `"name"`                     | Sort column                     |
| `sortDir`        | `"asc"\|"desc"`                  | `"asc"`                      | Sort direction                  |
| `page`           | `number`                         | `1`                          | Current pagination page         |

**Page reset rule:** Page resets to 1 whenever any filter or sort changes.

---

## 5. Filter Logic (priority order)

```
1. Text search (if filterText non-empty):
   Match if name OR id OR brand OR category contains text (case-insensitive)

2. Brand filter (if brandFilter non-empty):
   Exact brand match

3. Category filter (if categoryFilter non-empty):
   Match (p.category || "General") === categoryFilter

4. CfP filter (if cfpOnly):
   p.price == null || p.price === 0
```

**Safety:** Always coerce `filterText` to string before `.toLowerCase()`:

```ts
const filterStr = typeof filterText === "string" ? filterText : "";
```

---

## 6. Sort Logic

| sortField | Comparison key                                                    |
| --------- | ----------------------------------------------------------------- |
| `"name"`  | `p.name` (localeCompare)                                          |
| `"id"`    | `p.id` (localeCompare)                                            |
| `"brand"` | `p.brand` (localeCompare)                                         |
| `"price"` | `p.price ?? Number.MAX_VALUE` — missing price sorts to **bottom** |

Direction: `"asc"` = natural; `"desc"` = reversed.

---

## 7. Pagination

- `PAGE_SIZE = 50`
- `totalPages = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE))`
- Footer bar: shown only when `totalPages > 1`
- Footer content: `Page {page} of {totalPages} · {sorted.length} results`
- Prev / Next buttons; disabled at boundaries

---

## 8. Toolbar Layout

```
[count label] [search input] [brand ▾] [category ▾] [📞 Call for Price] [sort ▾]
```

- **Search input:** 240px, placeholder "Search by name, SKU or brand…"
- **Brand select:** populated from unique `p.brand` values (sorted A→Z)
- **Category select:** populated from unique `(p.category || "General")` values (sorted A→Z)
- **CfP toggle:** a `<button aria-pressed={cfpOnly}>`; amber when active, zinc when inactive
- **Sort select:** `value="${sortField}:${sortDir}"`, 7 options (name A→Z, name Z→A, SKU A→Z, SKU Z→A, Brand A→Z, Price Low→High, Price High→Low)
- When user types in search input AND `searchQuery !== null`: call `setSearchQuery(null)` to clear the deep-link

---

## 9. Table Columns

| Column        | Source field                           | Notes                                               |
| ------------- | -------------------------------------- | --------------------------------------------------- |
| Product Name  | `name`                                 | With 9×9 thumbnail; truncated                       |
| SKU           | `id`                                   | Monospace font; green dot if `official_url` present |
| Brand         | `brand`                                | Small text                                          |
| Category      | `subcategory ?? category ?? "General"` | Zinc badge                                          |
| Price (IL)    | `price`                                | `₪{n}` or amber "CfP" badge                         |
| Price (Eilat) | `price_eilat`                          | `₪{n}` or "—"                                       |
| Stock         | derived from `stock` field             | `<StockBadge>` component                            |

**Row interaction:**

- `onClick={() => goToProduct(item.id)}`
- `onKeyDown`: Enter or Space also triggers navigation
- `role="button"` + `tabIndex={0}` for keyboard accessibility
- Out-of-stock rows (`stock === 0`): `bg-red-950/10` tint

---

## 10. StockBadge Component

| Condition                 | Badge                                       |
| ------------------------- | ------------------------------------------- |
| `stock === null` / absent | "Unknown" — zinc-500, zinc-900 bg           |
| `stock === 0`             | "Out of Stock" — red-400, red-900/30 bg     |
| `stock > 0`               | "In Stock" — emerald-400, emerald-900/20 bg |

---

## 11. Loading State

Full-height skeleton:

- Toolbar: single `h-4 w-32 bg-zinc-800 rounded animate-pulse` block
- Body: 12× `h-12 bg-zinc-900 rounded animate-pulse` rows

---

## 12. Error State

Amber card with `error` string, Retry button (calls `refetch()`), and Ingestion Status fallback button.
Does NOT crash — product list is empty `[]` when error is set.

---

## 13. Empty State

```tsx
<PackageOpen size={32} className="opacity-40" />
<span>No products match. Adjust filters or search.</span>
```

Centered in viewport; only shown when `sorted.length === 0` and not loading.

---

## 14. Behavior Scenarios

| Scenario                  | Precondition                       | Expected outcome                                                          |
| ------------------------- | ---------------------------------- | ------------------------------------------------------------------------- |
| Opens via CfP card click  | `initialCfpFilter = true` in store | CfP toggle starts active; only CfP products visible                       |
| Opens via search submit   | `searchQuery = "Roland"` in store  | Text filter pre-filled with "Roland"; results filtered                    |
| User types in search      | Any                                | Results filter live (useMemo, no debounce needed — all data is in-memory) |
| User selects brand filter | Brand dropdown changed             | List narrows to that brand; page resets to 1                              |
| Zero results              | All filters produce empty list     | Empty state icon shown                                                    |
| User clicks row           | Any                                | Navigates to `PRODUCT_DETAIL` with `activeProductId = item.id`            |
| Out-of-stock row          | `stock === 0`                      | Red tinted row + "Out of Stock" badge                                     |
| Catalog 1000+ products    | Large catalog                      | Pagination activates; max 50 rows in DOM at once                          |

---

## 15. Sync Effects Required

```ts
// 1. Sync filterText from navigation store deep-link
useEffect(() => {
  if (typeof searchQuery === "string" && searchQuery !== null) {
    setFilterText(searchQuery);
    if (searchQuery === "") setSearchQuery(null);
  }
}, [searchQuery, setSearchQuery]);

// 2. Sync cfpOnly from navigation store deep-link
useEffect(() => {
  if (initialCfpFilter === true) setCfpOnly(true);
  else if (initialCfpFilter === false) setCfpOnly(false);
}, [initialCfpFilter]);

// 3. Reset pagination on any filter/sort change
useEffect(() => {
  setPage(1);
}, [filterText, brandFilter, categoryFilter, cfpOnly, sortField, sortDir]);
```

---

## 16. Agent Checklist

- [ ] `filterText` initial state guards with `typeof searchQuery === "string"`
- [ ] `cfpOnly` initial state uses `initialCfpFilter ?? false`
- [ ] `filterStr = typeof filterText === "string" ? filterText : ""` before `.toLowerCase()`
- [ ] Category filter includes subcategory in text search
- [ ] Price sort: missing price → bottom (`?? Number.MAX_VALUE`)
- [ ] Row `onClick` uses `() => goToProduct(item.id)` (arrow wrapper)
- [ ] Table thumbnail `onError` → opacity fade (no broken image icon)
- [ ] SKU column shows official_url green dot when present
- [ ] Out-of-stock rows get `bg-red-950/10` class
- [ ] Pagination footer hidden when `totalPages === 1`
- [ ] All 3 sync effects implemented
