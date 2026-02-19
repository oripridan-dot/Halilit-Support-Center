import React from 'react';
import { useValidateHeroImage } from '../hooks/useValidateHeroImage';

interface ProductImageProps {
  src: string | undefined | null;
  alt: string;
  className?: string;
  isHero?: boolean;
}

const ProductImage: React.FC<ProductImageProps> = ({ src, alt, className, isHero = false }) => {
  const placeholderImage = '/placeholder.png';

  const { isValidating, isValid } = useValidateHeroImage(src, isHero);

  const handleError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    if (!isHero) {
      (e.target as HTMLImageElement).src = placeholderImage;
    }
  };


  if (isHero) {
    if (isValidating) {
      return (
        <div className={`bg-gray-200 animate-pulse ${className}`} style={{ width: '100%', height: '100%', aspectRatio: '16/9' }} /> // Example: Shimmering rectangle
      );
    }

    if (!isValid || !src) {
      return <img src={placeholderImage} alt={alt} className={className} />;
    }

    return <img src={src} alt={alt} className={className} onError={handleError} />;

  }


  if (!src) {
    return <img src={placeholderImage} alt={alt} className={className} />;
  }

  return <img src={src} alt={alt} className={className} onError={handleError} />;
};

export default ProductImage;