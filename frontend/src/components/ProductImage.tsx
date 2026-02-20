// frontend/src/components/ProductImage.tsx
import React from 'react';
import { useValidateHeroImage } from '../../hooks/useValidateHeroImage';

interface ProductImageProps {
  src: string | undefined | null;
  alt: string;
  className?: string;
  isHero?: boolean;
}

const ProductImage: React.FC<ProductImageProps> = ({ src, alt, className, isHero = false }) => {
  const { isValidating, isValid } = useValidateHeroImage(src);

  const handleOnError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    if (!isHero) {
      (e.target as HTMLImageElement).src = '/placeholder.png';
    }
  };

  if (isHero) {
    if (isValidating) {
      return (
        <div className={`bg-gray-300 animate-pulse ${className}`} style={{ width: '100%', height: 'auto', aspectRatio: '16 / 9' }} /> // Example skeleton, adjust dimensions as needed
      );
    }

    if (!isValid || !src) {
      return <img src="/placeholder.png" alt={alt} className={className} />;
    }
  }

  if (!src) {
    return <img src="/placeholder.png" alt={alt} className={className} />;
  }

  return (
    <img
      src={src}
      alt={alt}
      className={className}
      onError={handleOnError}
    />
  );
};

export default ProductImage;