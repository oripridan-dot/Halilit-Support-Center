# Evolution Proposal: Next.js Static Site Generation (SSG)
**Date:** 2026-03-01
**Proposal ID:** `proposal_nextjs_static_site_generation`
**Type:** NEW_FRAMEWORK
**Verdict:** RECOMMEND
**Risk Level:** MEDIUM

---

## Problem Addressed
Catalog load must render a skeleton within 200 ms.

## The Tool
- **Name:** Next.js Static Site Generation (SSG)
- **Source / Docs:** https://nextjs.org/docs/basic-features/pages

## Integration Path
1. Introduce Next.js alongside the existing UI framework. 2. Identify components suitable for static pre-rendering (e.g., product tiles, detail view headers). 3. Implement SSG for these components, fetching data during the build process. 4. Update `specs/interface/02_inventory_grid.md` and `specs/interface/03_product_intelligence.md` to reflect the use of pre-rendered skeletons and initial content.

## Expected Impact
+20% faster initial catalog render

## Rationale
Next.js SSG can significantly improve initial load times by pre-rendering UI components, directly addressing the 'Speed of Service' goal and the 200ms skeleton requirement. It offers a balance between performance and ease of integration.

---
