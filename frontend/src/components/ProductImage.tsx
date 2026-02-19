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
  const isJITImage = src?.includes('jit'); // Simple check for JIT images

  const getBadge = () => {
    if (!src) return null;

    if (isJITImage) {
      return (
        <span
          aria-label="Source: Inferred Scout"
          className="bg-purple-100 text-purple-800 text-xs font-semibold mr-2 px-2.5 py-0.5 rounded dark:bg-purple-700 dark:text-purple-300 absolute top-2 right-2"
        >
          Inferred Scout
        </span>
      );
    }

    return (
      <span
        aria-label="Source: Official Scout"
        className="bg-blue-100 text-blue-800 text-xs font-semibold mr-2 px-2.5 py-0.5 rounded dark:bg-blue-700 dark:text-blue-300 absolute top-2 right-2"
      >
        Official Scout
      </span>
    );
  };

  const imageStyle = {
    objectFit: 'contain',
    width: '100%',
    height: '100%',
  };

  if (isHero && isValidating) {
    return (
      <div className={`relative ${className}`}>
        <div className="animate-pulse bg-gray-300 w-full h-full"></div>
      </div>
    );
  }

  if ((isHero && isValid === false) || !src) {
    return (
      <div className={`relative ${className}`}>
        <img src="/placeholder.png" alt={alt} style={imageStyle} className="w-full h-full" />
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <img
        src={src || '/placeholder.png'}
        alt={alt}
        style={imageStyle}
        onError={(e) => {
          if (!isHero) {
            (e.target as HTMLImageElement).src = '/placeholder.png';
          }
        }}
        className="w-full h-full"
      />
      {src && getBadge()}
    </div>
  );
};

export default ProductImage;