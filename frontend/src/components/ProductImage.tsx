// frontend/src/components/ProductImage.tsx
import React from 'react';
import { useValidateHeroImage } from '../hooks/useValidateHeroImage';

interface ProductImageProps {
  src: string | undefined | null;
  alt: string;
  className?: string;
  isHero?: boolean;
}

const ProductImage: React.FC<ProductImageProps> = ({ src, alt, className, isHero = false }) => {
  const { isValidating, isValid } = useValidateHeroImage(src);

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    if (!isHero) {
      (e.target as HTMLImageElement).src = '/placeholder.png';
    }
  };

  if (isHero) {
    if (isValidating) {
      return (
        <div className={`bg-gray-200 animate-pulse ${className}`} style={{ width: '100%', height: '100%' }}>
        </div>
      );
    }

    if (isValid === false || !src) {
      return <img src="/placeholder.png" alt={alt} className={className} />;
    }

    if (isValid === true) {
      return <img src={src} alt={alt} className={className} />;
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
      onError={handleImageError}
    />
  );
};

export default ProductImage;