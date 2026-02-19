# Spec: Product Detail Image Fallback Implementation
**Target:** src/components/ProductDetail/ProductImage.tsx

## Overview
This component handles displaying a product image. In the event that the primary image URL is unavailable or returns an error, it will display a fallback image from a list of predefined fallback URLs. This ensures a consistent user experience even when image resources are temporarily unavailable.

## Requirements
- The component must accept a `imageUrl` prop, which is the primary URL for the product image.
- The component must accept an optional `altText` prop for accessibility. If not provided, default alt text will be used.
- The component must display the image from the `imageUrl` prop if it loads successfully.
- If the `imageUrl` fails to load (e.g., 404 error), the component should cycle through a predefined list of fallback image URLs.
- A maximum number of retries with fallback images should be implemented to prevent infinite loops.
- The component should use Tailwind CSS for styling, with a dark theme using `slate-900` for background and `blue-500` for error indicators (if any).
- If all fallback images fail, display a default "Image Not Available" icon.
- The component should render an `img` tag.

## Data Contract
```typescript
interface ProductImageProps {
  imageUrl: string;
  altText?: string;
}
```

## Behavior Scenarios
- **Scenario:** Successful Image Load
  - Input: `imageUrl` points to a valid image URL.
  - Outcome: The image from `imageUrl` is displayed, and `altText` is set as the `alt` attribute of the `img` tag.

- **Scenario:** Primary Image Fails, First Fallback Succeeds
  - Input: `imageUrl` returns a 404 error; the first URL in `fallbackImageUrls` is valid.
  - Outcome: The first fallback image is displayed.

- **Scenario:** Primary Image Fails, All Fallbacks Fail
  - Input: `imageUrl` and all URLs in `fallbackImageUrls` return 404 errors.
  - Outcome: The "Image Not Available" icon is displayed.

- **Scenario:** No altText provided
  - Input: `imageUrl` is valid, altText is undefined
  - Outcome: The image is displayed, and the `alt` attribute of the `img` tag is set to "Product Image".

## Out of Scope
- Image optimization (resizing, format conversion) is not handled by this component.
- The list of fallback URLs is hardcoded within the component. Dynamic configuration from a CMS or API is out of scope.
- Image uploading or management is not covered.

```typescript jsx
// src/components/ProductDetail/ProductImage.tsx
import React, { useState, useEffect } from 'react';

interface ProductImageProps {
  imageUrl: string;
  altText?: string;
}

const fallbackImageUrls = [
  '/images/fallback-1.png',
  '/images/fallback-2.png',
  '/images/fallback-3.png',
];

const ImageNotAvailableIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-6 h-6 text-blue-500">
  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
</svg>
);

const ProductImage: React.FC<ProductImageProps> = ({ imageUrl, altText }) => {
  const [currentImageUrl, setCurrentImageUrl] = useState(imageUrl);
  const [errorCount, setErrorCount] = useState(0);
  const maxRetries = fallbackImageUrls.length + 1;

  useEffect(() => {
    setCurrentImageUrl(imageUrl); // Reset to primary image when imageUrl prop changes
    setErrorCount(0); // Reset error count when imageUrl prop changes
  }, [imageUrl]);

  const handleError = () => {
    if (errorCount < maxRetries) {
      if (errorCount < fallbackImageUrls.length) {
        setCurrentImageUrl(fallbackImageUrls[errorCount]);
      }
      setErrorCount(errorCount + 1);
    }
  };

  const imageSource = errorCount <= fallbackImageUrls.length ? currentImageUrl : null;

  return (
    <>
      {imageSource ? (
        <img
          src={imageSource}
          alt={altText || "Product Image"}
          onError={handleError}
          className="w-full h-auto object-cover"
        />
      ) : (
        <div className="flex items-center justify-center h-48 bg-slate-900 rounded-md">
            <ImageNotAvailableIcon/>
          <span className="text-blue-500">Image Not Available</span>
        </div>
      )}
    </>
  );
};

export default ProductImage;
```
