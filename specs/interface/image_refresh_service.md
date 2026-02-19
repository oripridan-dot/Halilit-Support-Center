# Spec: Image Refresh Service

**Version:** 1.0
**Component:** `frontend/src/hooks/useImageRefresh.ts`

## 1. Purpose

To automatically refresh product images in the Halilit Support Center when the `image_url` is updated in the JIT (Just-In-Time) stream or catalog, addressing the "Zero Broken Images" business goal and ensuring images are always up to date. This spec complements "Product Detail - Dynamic JIT Badge Updates", specifically handling the image refresh logic.

## 2. Requirements

1. **Image Refresh Hook:** Create a custom hook `useImageRefresh(imageUrl: string | undefined | null, productId: string)` that accepts the `imageUrl` and `productId` as input.
2. **Cache Busting:** The hook MUST implement a cache-busting mechanism to force the browser to reload the image when `imageUrl` changes. This can be achieved by appending a unique query parameter to the image URL.
3. **JIT Image Update:** When the JIT stream (`useJITIntelligence`) provides a new `thumbnail` URL, the `ProductImage` component using this hook MUST automatically refresh, displaying the new image. The image URL itself must come from `JITState.snap.thumbnail` only when `JITState.status === 'complete'`.
4. **Catalog Image Update:** If the Conductor Catalog provides an updated `image_url` for a given `productId`, the `ProductImage` component using this hook MUST automatically refresh, displaying the new image.
5. **Cache Busting Parameter:** The cache-busting query parameter MUST be based on a hash of the image URL and the product ID. This ensures that a new URL is generated only when the image URL or product ID changes. For simplicity, this could be a timestamp. Example: `imageUrl?cacheBust=<hash>`.
6. **Debounce Refresh:** The image refresh MUST be debounced to prevent excessive re-renders, especially when the JIT stream emits multiple updates in rapid succession. A debounce time of 200ms should be used.
7.  **Image Validation:** The `ProductImage` MUST still perform validation (using `useValidateHeroImage`) of the newly fetched image (after cache busting) to prevent broken images from appearing if the new URL is also invalid. This is only necessary for hero images.
8. **Component Integration:** The `useImageRefresh` hook must be integrated into the `ProductImage` component.

## 3. Behavior Scenarios

1. **Scenario:** A product's `image_url` is updated in the Conductor Catalog.
   * **Outcome:** The `ProductImage` component on the Product Detail View and in Product Tiles displaying this product automatically refreshes, showing the new image.
2. **Scenario:** The JIT stream provides a new `thumbnail` URL for a product, and `JITState.status === 'complete'`.
   * **Outcome:** The `ProductImage` component on the Product Detail View displaying this product automatically refreshes, showing the JIT thumbnail. The "Inferred Scout" badge is displayed.
3. **Scenario:** The JIT stream provides multiple updates to the `thumbnail` URL in rapid succession.
   * **Outcome:** The `ProductImage` component refreshes only once, 200ms after the last update, preventing excessive re-renders.
4. **Scenario:** An updated `image_url` is invalid (404 error).
    * **Outcome:** The image validation hook (`useValidateHeroImage`) detects the invalid URL.
    * **Outcome:** The `ProductImage` component displays the placeholder image (`/placeholder.png`).

## Verification Commands

- `pnpm tsc --noEmit`
- `pnpm run lint`
