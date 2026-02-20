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