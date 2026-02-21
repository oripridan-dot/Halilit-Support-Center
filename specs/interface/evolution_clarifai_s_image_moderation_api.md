# Spec: Clarifai's Image Moderation API Integration
**Source:** 2026-02-22_proposal_ai_powered_image_validation.md
**Created:** 2026-02-21
**Status:** PENDING BUILD

---

## Problem
Zero Broken Images. Hero images in the catalog MUST be validated before display.

## Proposed Solution
1. Integrate the Clarifai API into the `product_detail_hero_image_validation_service.md` service. 2. Modify the service to send hero images to Clarifai for analysis. 3. Update `product_detail_hero_image_validation_service.md` to handle responses from Clarifai, marking images as invalid if they fail validation (e.g., broken, inappropriate content). 4. Implement logic to display fallback images if validation fails. The `halilit_api_fetching_machine_status.md` may also need updates to reflect the status of the image validation service.

## Expected Impact
+20% faster image validation and fallback implementation, improved image quality.

## Acceptance Criteria
- [ ] Existing tests still pass after integration (`pnpm test --run`).
- [ ] Vite build reports 0 errors.
- [ ] No new dependencies outside the approved stack (package.json audit).
- [ ] Three Source Rules: no synthetic data introduced.

## Sandbox Validation Required
Run `sandbox specs/interface/evolution_clarifai_s_image_moderation_api.md` before merging.
