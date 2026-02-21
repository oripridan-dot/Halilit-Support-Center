# Spec: React Query with Optimistic Updates Integration

**Source:** 2026-02-28_proposal_react_query_with_optimistic_updates.md
**Created:** 2026-02-21
**Status:** BUILT ✅

---

## What was built

`frontend/src/components/ProductDetail/EcosystemTab.tsx` refactored:

- Removed `useState`/`useEffect` data-fetching pattern
- Added `useQuery(["ecosystem", productId])` with `staleTime: 60 s`, `retry: 1`
- Added `useMutation` + `onMutate` optimistic update for "pin accessory" action
  (instantly reflects pin state in cached data; rolls back on error)
- Fixed bug: `ImageWithFallback` was using `src=` prop (wrong) — fixed to `imageUrl=`
- Dark-theme styling aligned with app shell (zinc palette)

## Acceptance Criteria

- [x] Existing tests still pass.
- [x] Vite/tsc build 0 errors.
- [x] No new dependencies.
- [x] Three Source Rules satisfied.
