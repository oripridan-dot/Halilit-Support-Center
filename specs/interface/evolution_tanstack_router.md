# Spec: Tanstack Router Integration
**Source:** 2026-02-29_proposal_tanstack_router_for_halilit_app.md
**Created:** 2026-02-21
**Status:** DEFERRED — AC conflict

---

## Why Deferred

The proposal's Acceptance Criteria explicitly state:

> No new dependencies outside the approved stack (package.json audit).

Installing `@tanstack/router` would violate this AC — it is not in the
approved dependency set and requires significant routing-layer refactoring
with no immediate user-visible benefit over the existing Zustand-based
`navigationStore`.

**Resolution:** keep the Zustand navigation store (`navigationStore.ts`).
Revisit when TanStack Router is promoted to the approved stack.

---

## Original Problem
Product detail Ecosystem tab that shows nothing when `related_ids` is empty.

**Addressed by:** `EcosystemTab.tsx` refactor (useQuery, optimistic updates)
in `evolution_react_query_with_optimistic_updates.md` — that spec was built
in the same session and resolves the root cause without a router change.
