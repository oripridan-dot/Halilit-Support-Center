# Spec 01 — Operator Dashboard ("Mission Control")

**Version:** 2.0 · Dark Factory v9.6.1
**Component:** `frontend/src/components/views/DashboardView.tsx`
**Route state:** `currentView === 'DASHBOARD'`
**Data sources:** `/api/dashboard/stats` (FastAPI) · `useConductorCatalog` hook (loading flag only)

---

## 1. Purpose & Intent

Mission Control is the operator's first screen. It gives a single-screen answer to:

> "What is the current state of our catalog and pipeline right now?"

Functional over decorative — no charts, no animations beyond skeleton states, no gamification.
Every metric reflects real data. Empty is better than fake.

---

## 2. Data Contracts

### 2.1 `GET /api/dashboard/stats` → `DashboardStats`

```ts
interface DashboardStats {
  total_products: number;
  calls_for_price: number; // products with price == null or price == 0
  top_brands_count: number; // distinct brand values in catalog
  last_ingestion_run: {
    status: "never" | "running" | "complete" | "failed" | "unknown";
    finished_at: string | null; // ISO datetime or null
    product_count: number | null; // products processed in last run
  };
}
```

**Fetch rules:**

- `staleTime: 30_000`, `retry: 0`
- Parse as `text()` first; if text starts with `<`, backend is down → show error banner, DO NOT crash
- On `res.ok === false`, extract `json.error` for message

---

## 3. Layout Structure

```
┌────────────────────────────────────────────────────────────┐
│  Mission Control          Operator Console · date string   │  Header
├────────────────────────────────────────────────────────────┤
│  ⚠  Stats unavailable — <message>              [Retry]     │  Error banner (conditional)
├──────────┬──────────┬──────────┬──────────────────────────┤
│  📦      │  📞      │  🏷      │  🔄                       │  4 MetricCards
│  Total   │  CfP     │  Brands  │  Last Run                 │
│  products│  count   │  count   │  status + date            │
├──────────┴──────────┴──────────┴──────────────────────────┤
│  Quick Actions (always visible)                            │
│  [Open Inventory Master]   [Data Pipeline]                 │
└────────────────────────────────────────────────────────────┘
```

---

## 4. MetricCard Component

```ts
interface MetricCardProps {
  icon: LucideIcon;
  label: string;
  value: React.ReactNode; // large number or JSX status
  sub?: React.ReactNode; // small hint line below label
  accent: "blue" | "amber" | "green" | "red" | "zinc";
  onClick?: () => void; // if present → render as <button>
}
```

**Loading value:** `<span className="text-zinc-600 animate-pulse">…</span>`
**No-stats value:** String `"—"` — never render `0` when stats are unavailable.
**With stats:** `.toLocaleString()` numbers.

---

## 5. MetricCard Wiring Table

| Card               | Value                        | Sub                                                | Accent                                         | onClick                    |
| ------------------ | ---------------------------- | -------------------------------------------------- | ---------------------------------------------- | -------------------------- |
| Total products     | `stats.total_products`       | "Active SKUs"                                      | blue                                           | `() => goToInventory()`    |
| Call for price     | `stats.calls_for_price`      | "Missing IL price"                                 | amber if > 0 else zinc                         | `() => goToInventoryCfp()` |
| Active brands      | `stats.top_brands_count`     | "Distinct brands in catalog"                       | green                                          | —                          |
| Last ingestion run | `<LastRunStatus run={...}/>` | `"{count} products synced"` or `"No run recorded"` | red if failed, blue if running, zinc otherwise | —                          |

**⚠ CRITICAL — Arrow wrapper rule:**
ALL `onClick` props in JSX MUST use arrow wrappers: `onClick={() => fn()}`.
NEVER `onClick={fn}`. Passing a navigation function directly causes React to call it with
the SyntheticMouseEvent as first argument, which corrupts `searchQuery` in the navigation store
and crashes InventoryView with `filterText.toLowerCase is not a function`.

---

## 6. Error Banner (non-blocking)

Appears when `statsError` is truthy. Sits above the metrics grid. Does NOT replace the view.

```tsx
{
  errorMsg && (
    <div
      className="flex items-center gap-2 mb-6 px-4 py-3
                  bg-amber-900/20 border border-amber-500/30 rounded-xl text-sm"
    >
      <AlertTriangle size={14} className="text-amber-400 shrink-0" />
      <span className="text-amber-300 font-medium">Stats unavailable —</span>
      <span className="text-zinc-400 truncate">{errorMsg}</span>
      <button
        onClick={() => refetch()}
        className="ml-auto shrink-0 px-3 py-1 bg-zinc-700 hover:bg-zinc-600
                       text-zinc-200 text-xs rounded-lg"
      >
        Retry
      </button>
    </div>
  );
}
```

`hasStats = !!stats && !statsError` — gate all stats field access behind this.

---

## 7. LastRunStatus Sub-Component

| status                     | Render                                                |
| -------------------------- | ----------------------------------------------------- |
| `"never"`                  | `"—"` zinc-500                                        |
| `"running"`                | `<Loader2 animate-spin/>` + "Running…" blue-400       |
| `"complete"` / `"unknown"` | `<CheckCircle/>` + date in `en-IL` locale emerald-400 |
| `"failed"`                 | `<XCircle/>` + "Failed" red-400                       |

Date: `new Date(finished_at).toLocaleString("en-IL", { dateStyle: "short", timeStyle: "short" })`

---

## 8. Quick Actions

```tsx
<button onClick={() => goToInventory()}>Open Inventory Master</button>
<button onClick={() => goToIngestionStatus()}>Data Pipeline</button>
```

Both use arrow wrappers. Always rendered (not gated on stats success).

---

## 9. Behavior Scenarios

| Scenario                     | Precondition                    | Expected outcome                                                                       |
| ---------------------------- | ------------------------------- | -------------------------------------------------------------------------------------- |
| Page loads, backend healthy  | Backend up, catalog cached      | Metrics resolve within 2s; no error banner                                             |
| Backend down — HTML returned | Stats endpoint returns HTML 404 | Amber error banner above metrics; cards show "—"; Quick Actions still visible          |
| Stats retry succeeds         | User clicks Retry               | Banner clears; metrics populate                                                        |
| No ingestion ever run        | `status = "never"`              | Last run card shows "—" with zinc accent                                               |
| Ingestion running            | `status = "running"`            | Last run card shows spinner + "Running…"                                               |
| CfP card clicked             | Any                             | → INVENTORY with `initialCfpFilter = true`; InventoryView opens with CfP filter active |
| Total products card clicked  | Any                             | → INVENTORY with no filter pre-applied                                                 |

---

## 10. Navigation Store Requirements

This view requires the following from `navigationStore`:

```ts
goToInventory: (searchQuery?: string) => void;
goToInventoryCfp: () => void;  // sets initialCfpFilter: true before navigating
goToIngestionStatus: () => void;
```

`goToInventoryCfp` MUST set `searchQuery: null` and `initialCfpFilter: true` in state.

---

## 11. Agent Checklist

- [ ] `useDashboardStats` queryFn parses `text()` first, checks for `<` prefix, throws user-friendly message
- [ ] `retry: 0` — no automatic retries
- [ ] `hasStats = !!stats && !statsError` used on every stats field access
- [ ] No full-page error replacement — always inline banner only
- [ ] All `onClick` props use `() =>` arrow wrappers
- [ ] CfP card calls `goToInventoryCfp` (not `goToInventory`)
- [ ] Quick Actions render regardless of stats state
- [ ] TypeScript: no `any`, no non-null assertions without `hasStats` guard
