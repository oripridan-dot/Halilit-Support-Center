import React, { useState, useEffect } from 'react';

interface ImageWithFallbackProps {
  imageUrl?: string;
  altText: string;
  cdnBaseUrl?: string;
  dataTrust?: { source: string; };
  className?: string;
}

const placeholderImage = '/placeholder.png'; // Assuming placeholder image is in public folder

const ImageWithFallback: React.FC<ImageWithFallbackProps> = ({
  imageUrl,
  altText,
  cdnBaseUrl,
  dataTrust,
  className,
}) => {
  const [imageSrc, setImageSrc] = useState<string | undefined>(imageUrl || placeholderImage);
  const [isError, setIsError] = useState(false);

  const generateSrcSet = (url: string | undefined, width: number, format: string) => {
    if (!url || !cdnBaseUrl) return undefined;
    const encodedImageUrl = encodeURIComponent(url);
    return `${cdnBaseUrl}${encodedImageUrl}?format=${format}&width=${width} ${width}w`;
  };

  const handleImageError = () => {
    setIsError(true);
    setImageSrc(placeholderImage);
  };

  useEffect(() => {
    if (imageUrl) {
        setImageSrc(imageUrl);
        setIsError(false); // Reset error state when imageUrl changes
    } else {
        setImageSrc(placeholderImage);
        setIsError(false);
    }
  }, [imageUrl]);

  const finalAltText = dataTrust ? `${altText} - Source: ${dataTrust.source}` : altText;

  if (!imageUrl) {
    return (
      <img
        src={placeholderImage}
        alt={finalAltText}
        className={`bg-gray-800 ${className}`}
        loading="lazy"
      />
    );
  }

  return (
    <picture>
      <source
        srcSet={generateSrcSet(imageUrl, 600, 'avif')}
        type="image/avif"
      />
      <source
        srcSet={generateSrcSet(imageUrl, 600, 'webp')}
        type="image/webp"
      />
      <img
        src={imageSrc}
        alt={finalAltText}
        className={`bg-gray-800 ${className}`}
        onError={handleImageError}
        loading="lazy"
      />
    </picture>
  );
};

export default ImageWithFallback;