# Evolution Proposal: Meilisearch
**Date:** 2026-02-27
**Proposal ID:** `proposal_meilisearch_integration`
**Type:** NEW_MCP
**Verdict:** RECOMMEND
**Risk Level:** MEDIUM

---

## Problem Addressed
Speed of Service: Search results must sort "In Stock" items above "Call for Price" items by default. The search input must debounce at ≤ 150 ms. Catalog load must render a skeleton within 200 ms.

## The Tool
- **Name:** Meilisearch
- **Source / Docs:** https://www.meilisearch.com/

## Integration Path
1. Deploy a Meilisearch instance. 2. Create an index for the catalog data. 3. Update `specs/01_data/halilit_api.md` to include steps for syncing data to Meilisearch. 4. Modify the `web-search` MCP server to query Meilisearch instead of performing in-memory filtering. 5. Update `specs/interface/inventory_search_stock_cfp_sorting.md` to reflect the change in search implementation. 6. Remove the old filtering code once the new implementation is stable.

## Expected Impact
+50% faster search and sorting, especially for complex queries and large catalogs

## Rationale
Meilisearch provides a fast, typo-tolerant search experience out of the box and can significantly improve the speed of service, addressing a critical business goal. Its built-in sorting capabilities will also allow for easier implementation of the stock-based search results.

---

---
## Chief Verdict — 2026-02-21
**Decision:** `REJECT`
**Reason:** Proposal introduces a framework outside the approved stack (Three Source Rules / Architecture Law).
*(Processed by evolution_manager.py — Chief auto-review)*
