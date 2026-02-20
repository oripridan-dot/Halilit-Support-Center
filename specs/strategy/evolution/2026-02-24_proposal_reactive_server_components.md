# Evolution Proposal: Next.js Reactive Server Components (RSC)
**Date:** 2026-02-24
**Proposal ID:** `proposal_reactive_server_components`
**Type:** NEW_PARADIGM
**Verdict:** RECOMMEND
**Risk Level:** MEDIUM

---

## Problem Addressed
Maximize Attachment Rate: Every major product (Guitar, Piano, Keyboard) MUST show compatible accessories (Stands, Cases, Pedals, Cables) immediately on the Product Detail screen.

## The Tool
- **Name:** Next.js Reactive Server Components (RSC)
- **Source / Docs:** https://nextjs.org/docs/getting-started/react-essentials

## Integration Path
Refactor the ProductDetailView and accessory recommendation components to use RSC for data fetching and rendering.  Specifically, the `specs/interface/product_detail_-_accessory_recommendations.md` component would need to be updated to utilize RSC. The data fetching logic in `specs/data_pipeline/02_relationship_logic.md` and the Halilit API (`specs/01_data/halilit_api.md`) should remain untouched, but accessed via RSC. This would involve rewriting the component as a server component and fetching data directly within the component using `await`.

## Expected Impact
+20% faster rendering of accessory recommendations on initial page load.

## Rationale
RSC allows data fetching and component rendering on the server, reducing client-side JavaScript execution and improving initial load time for accessory recommendations. This directly addresses the 'Maximize Attachment Rate' goal by ensuring accessories are displayed quickly.

---
