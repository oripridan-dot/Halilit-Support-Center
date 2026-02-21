# Spec: WebP Image Format Integration
**Source:** 2026-02-29_proposal_new_image_format_webp.md
**Created:** 2026-02-21
**Status:** BUILT ✅

---

## What was built

`frontend/src/components/ImageWithFallback.tsx` converted from `<img>` to
`<picture>` + `<source type="image/webp">`. A `toWebpSrc()` helper derives a
`.webp` URL from JPEG/PNG/GIF URLs. Added `eager` prop for hero images.
Added React `useState` fallback so a failed image load switches back to
`/placeholder.png` without re-triggering the error.

## Acceptance Criteria
- [x] Existing tests still pass after integration.
- [x] Vite build reports 0 errors (tsc --noEmit passes).
- [x] No new dependencies (stdlib `useState` only).
- [x] Three Source Rules: no synthetic data introduced.
