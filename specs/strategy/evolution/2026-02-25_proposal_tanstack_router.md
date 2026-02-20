# Evolution Proposal: @tanstack/router
**Date:** 2026-02-25
**Proposal ID:** `proposal_tanstack_router`
**Type:** NEW_LIBRARY
**Verdict:** RECOMMEND
**Risk Level:** MEDIUM

---

## Problem Addressed
Speed of Service: Search results must sort "In Stock" items above "Call for Price" items by default. The search input must debounce at ≤ 150 ms. Catalog load must render a skeleton within 200 ms.

## The Tool
- **Name:** @tanstack/router
- **Source / Docs:** https://tanstack.com/router/v1

## Integration Path
1. Install @tanstack/router. 2. Refactor existing routing logic in frontend/src/App.js to use TanStack Router's route definitions and navigation hooks. 3. Update the inventory search component (likely in frontend/src/components/InventorySearch.js) to leverage TanStack Router's data fetching capabilities with suspense for faster skeleton rendering and improved UI updates.

## Expected Impact
+20% faster catalog load and search interactions

## Rationale
TanStack Router offers a modern, type-safe routing solution that can significantly improve application performance and developer experience. By leveraging its features, we can address the speed of service bottleneck, improve the user experience, and reduce code complexity.

---
