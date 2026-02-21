# Evolution Proposal: Tanstack Router
**Date:** 2026-02-29
**Proposal ID:** `proposal_tanstack_router_for_halilit_app`
**Type:** NEW_LIBRARY
**Verdict:** RECOMMEND
**Risk Level:** MEDIUM

---

## Problem Addressed
Product detail Ecosystem tab that shows nothing when `related_ids` is empty

## The Tool
- **Name:** Tanstack Router
- **Source / Docs:** https://tanstack.com/router/v1

## Integration Path
1. Install Tanstack Router. 2. Refactor the existing routing logic in `frontend/src/App.js` to use Tanstack Router's route definition system. 3. Update the ProductDetailView component to leverage Tanstack Router for prefetching related data and handling loading states.

## Expected Impact
+20% faster loading of product detail page ecosystem tab

## Rationale
Tanstack Router offers features like prefetching and improved data dependency management, which can significantly improve the loading speed of the 'Ecosystem' tab, particularly when no related items exist. This can prevent UI 'dead zones' and lead to more consistent performance.

---
