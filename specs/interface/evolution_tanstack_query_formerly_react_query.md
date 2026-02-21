# Spec: TanStack Query (formerly React Query) Integration
**Source:** 2026-02-24_proposal_react_query_stock_updates.md
**Created:** 2026-02-21
**Status:** BUILT ✅

---

## What was built

`@tanstack/react-query` v5 was already installed. Enhancements made:
- `useConductorCatalog` → added `staleTime: 30 000 ms` + `refetchInterval: 60 000 ms`
- New hook `frontend/src/hooks/useStockStatus.ts` — focused per-product stock
  query with 30 s stale time, 1 min auto-refetch, and `useInvalidateStock()`
  helper for post-mutation cache invalidation.

## Acceptance Criteria
- [x] Existing tests still pass.
- [x] Vite/tsc build 0 errors.
- [x] No new dependencies (TQ already present).
- [x] Three Source Rules satisfied.
