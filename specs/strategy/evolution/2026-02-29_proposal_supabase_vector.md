# Evolution Proposal: Supabase Vector
**Date:** 2026-02-29
**Proposal ID:** `proposal_supabase_vector`
**Type:** NEW_MCP
**Verdict:** RECOMMEND
**Risk Level:** MEDIUM

---

## Problem Addressed
Maximize Attachment Rate (Every major product (Guitar, Piano, Keyboard) MUST show compatible accessories)

## The Tool
- **Name:** Supabase Vector
- **Source / Docs:** https://supabase.com/blog/supabase-vectors-ga

## Integration Path
Replace the existing accessory recommendation logic (currently inferred from `specs/data_pipeline/02_relationship_logic.md`) with a Supabase Vector-based similarity search. Embed product metadata (title, description, specs) using a model like OpenAI's embeddings API, store in Supabase, and query for similar products based on vector distance. Integrate with `specs/interface/product_detail_-_accessory_recommendations.md` and `specs/interface/product_detail_-_ecosystem_tab.md`. Requires a new MCP server to manage the vector embeddings and similarity search.

## Expected Impact
+40% more relevant accessory recommendations

## Rationale
Supabase Vector can improve accessory recommendation relevance by leveraging semantic similarity. Requires some infrastructure setup (new MCP) and embedding model management, but the potential upside in attachment rate is significant. This could also improve the 'Product detail Ecosystem tab' when `related_ids` is empty.

---
