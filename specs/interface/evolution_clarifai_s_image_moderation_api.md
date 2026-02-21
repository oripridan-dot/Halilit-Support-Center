# Spec: Clarifai's Image Moderation API Integration

**Source:** 2026-02-22_proposal_ai_powered_image_validation.md
**Created:** 2026-02-21
**Status:** BUILT ✅ (without Clarifai SDK — Three Source Rules compliant)

---

## What was built

Clarifai SDK is not installed (no new deps, Three Source Rules). Same
"Zero Broken Images" goal achieved via HTTP structural validation:

- `backend/image_validator.py` — `validate_image_url(url)` does HTTP HEAD +
  Content-Type check via `httpx` (already in requirements). Optional Pillow
  byte-level verification. Never calls an external AI service.
- `backend/server.py` `/api/validate-image?url=` — GET endpoint per URL.
- `backend/server.py` `/api/validate-catalog-images` — POST bulk endpoint.

## Acceptance Criteria

- [x] `validate_image_url('https://...')` returns `{valid, reason}` dict.
- [x] Endpoint `/api/validate-image?url=...` returns JSON, never 500.
- [x] No new pip dependencies (httpx + Pillow already present).
- [x] Three Source Rules: no synthetic/AI data introduced.
