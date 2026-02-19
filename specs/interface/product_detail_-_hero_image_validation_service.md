# Spec: Product Detail - Hero Image Validation Service

**Version:** 1.0
**Component:** `frontend/src/hooks/useValidateHeroImage.ts`

## 1. Purpose

To validate the hero image URL on the Product Detail screen before displaying it, ensuring that only valid images are shown and preventing broken image links. This directly addresses the "Zero Broken Images" business goal.

## 2. Requirements

1.  **Validation Hook:** Create a custom hook `useValidateHeroImage(imageUrl: string)` that accepts an image URL as input.
2.  **Validation State:** The hook MUST return an object with the following properties:
    *   `isValidating: boolean` - Indicates whether the image URL is currently being validated.
    *   `isValid: boolean | null` - Indicates whether the image URL is valid (true), invalid (false), or has not yet been validated (null).
3.  **Validation Logic:** The hook MUST perform the following validation steps:
    *   **Initial Check:** If `imageUrl` is empty or null, set `isValid` to `false` immediately and skip the network request.
    *   **Network Request:** If `imageUrl` is present, make a HEAD request to the image URL.
    *   **Success:** If the HEAD request returns a status code between 200 and 299 (inclusive), set `isValid` to `true`.
    *   **Failure:** If the HEAD request returns a status code outside the 200-299 range, or the request fails due to a network error or timeout, set `isValid` to `false`.
    *   **Cache Invalid Images:** Store the result of a failed validation attempt (`isValid: false`) in `localStorage` (or a similar persistent storage mechanism) for at least 24 hours, keyed by the `imageUrl`. Before making a network request, check if the `imageUrl` exists in the cache, and if so, immediately set `isValid` to `false` without making a network request.
4.  **Asynchronous Validation:** The validation MUST be performed asynchronously to avoid blocking the main thread. Use `useEffect` with an empty dependency array for initial validation and `useEffect` with `imageUrl` as a dependency to re-validate when the `imageUrl` changes.
5.  **Debounce Validation:** Debounce the validation by at least 500ms to avoid unnecessary validation attempts when the `imageUrl` changes rapidly.
6.  **Error Handling:** Handle network errors and timeouts gracefully. Log errors to the console but do not throw exceptions.
7.  **Usage in ProductDetailView:** In the ProductDetailView component, use the `useValidateHeroImage` hook with the product's `image_url`. Display the hero image only if `isValid` is `true` or `null` (still validating). If `isValid` is `false`, display the `/placeholder.png` image instead.
8.  **Loading State:** While `isValidating` is `true`, display a loading indicator (e.g., a spinner or skeleton).

## 3. Behavior Scenarios

1.  **Scenario:** The Product Detail screen loads for a product with a valid `image_url`.
    *   **Outcome:** The `useValidateHeroImage` hook starts validating the `image_url`.
    *   **Outcome:** While `isValidating` is `true`, a loading indicator is displayed.
    *   **Outcome:** After the validation succeeds, `isValid` becomes `true`, and the hero image is displayed.
2.  **Scenario:** The Product Detail screen loads for a product with an invalid `image_url` (e.g., a 404 error).
    *   **Outcome:** The `useValidateHeroImage` hook starts validating the `image_url`.
    *   **Outcome:** While `isValidating` is `true`, a loading indicator is displayed.
    *   **Outcome:** After the validation fails, `isValid` becomes `false`, and the `/placeholder.png` image is displayed.
    *   **Outcome:** The invalid `image_url` is stored in `localStorage` to prevent future validation attempts.
3.  **Scenario:** The Product Detail screen loads for a product with an `image_url` that was previously validated as invalid.
    *   **Outcome:** The `useValidateHeroImage` hook checks `localStorage` and finds the `image_url`.
    *   **Outcome:** `isValid` is immediately set to `false`, and the `/placeholder.png` image is displayed without making a network request.
4.  **Scenario:** The product's `image_url` changes to a valid URL.
    *   **Outcome:** The `useValidateHeroImage` hook re-validates the new `image_url`.
    *   **Outcome:** After the validation succeeds, `isValid` becomes `true`, and the new hero image is displayed.

## 4. Data Contract

```ts
interface UseValidateHeroImageResult {
  isValidating: boolean;
  isValid: boolean | null;
}

function useValidateHeroImage(imageUrl: string): UseValidateHeroImageResult;
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
