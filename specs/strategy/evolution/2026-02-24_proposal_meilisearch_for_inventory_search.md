# Evolution Proposal: Meilisearch
**Date:** 2026-02-24
**Proposal ID:** `proposal_meilisearch_for_inventory_search`
**Type:** NEW_MCP
**Verdict:** RECOMMEND
**Risk Level:** MEDIUM

---

## Problem Addressed
Search that does not debounce, Search results must sort "In Stock" items above "Call for Price" items by default. The search input must debounce at ≤ 150 ms. Catalog load must render a skeleton within 200 ms.

## The Tool
- **Name:** Meilisearch
- **Source / Docs:** https://www.meilisearch.com/

## Integration Path
1. Deploy Meilisearch MCP server. 2. Modify `specs/01_data/catalog_organizer.md` to index product data in Meilisearch. 3. Update `specs/interface/inventory_search_debounce.md` and `specs/interface/inventory_search_stock_cfp_sorting.md` to use Meilisearch for search and sorting. 4. Deactivate `web-search (sse)` MCP server after successful migration.

## Expected Impact
+50% faster and more relevant search results, improved stock status sorting

## Rationale
Meilisearch provides a fast and relevant search experience with built-in sorting capabilities, which directly addresses the speed of service and stock status sorting requirements.

---
