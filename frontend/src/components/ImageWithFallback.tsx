import React, { useState, useEffect } from 'react';

interface ImageWithFallbackProps {
  imageUrl: string | null | undefined;
  altText: string;
  placeholderImageUrl?: string;
  className?: string;
}

const generateSrcSet = (
  baseUrl: string,
  width: number,
  format: 'avif' | 'webp' | 'jpeg'
): string => {
  try {
    const cdnUrl = new URL(baseUrl);
    const params = new URLSearchParams(cdnUrl.search);
    params.set('f', 'auto'); // Let CDN handle the format, which should negotiate AVIF
    params.set('q', 'auto');
    params.set('w', width.toString());

    return `${cdnUrl.origin}${cdnUrl.pathname}?${params.toString()} ${width}w`;
  } catch (error) {
    console.error('Error generating srcSet URL:', error);
    return ''; // Or return a default value, or handle the error appropriately
  }
};


const ImageWithFallback: React.FC<ImageWithFallbackProps> = ({
  imageUrl,
  altText,
  placeholderImageUrl = '/placeholder.png',
  className,
}) => {
  const [error, setError] = useState(false);

  const handleImageError = () => {
    setError(true);
    console.error('Image loading failed for URL:', imageUrl);
  };

  useEffect(() => {
    setError(false);
  }, [imageUrl]);

  if (!imageUrl || error) {
    return (
      <div className={`bg-slate-900 ${className}`}>
        <img src={placeholderImageUrl} alt={altText} className="object-cover w-full h-full" />
      </div>
    );
  }

  const smallAvif = generateSrcSet(imageUrl, 320, 'avif');
  const mediumAvif = generateSrcSet(imageUrl, 640, 'avif');
  const largeAvif = generateSrcSet(imageUrl, 1024, 'avif');

  const smallWebp = generateSrcSet(imageUrl, 320, 'webp');
  const mediumWebp = generateSrcSet(imageUrl, 640, 'webp');
  const largeWebp = generateSrcSet(imageUrl, 1024, 'webp');

  const fallbackJpeg = generateSrcSet(imageUrl, 640, 'jpeg'); // Use medium size for fallback


  return (
    <picture>
      {smallAvif && <source srcSet={smallAvif} type="image/avif" media="(max-width: 320px)" />}
      {mediumAvif && <source srcSet={mediumAvif} type="image/avif" media="(max-width: 640px)" />}
      {largeAvif && <source srcSet={largeAvif} type="image/avif" media="(min-width: 641px)" />}

      {smallWebp && <source srcSet={smallWebp} type="image/webp" media="(max-width: 320px)" />}
      {mediumWebp && <source srcSet={mediumWebp} type="image/webp" media="(max-width: 640px)" />}
      {largeWebp && <source srcSet={largeWebp} type="image/webp" media="(min-width: 641px)" />}

      <img
        src={fallbackJpeg}
        alt={altText}
        loading="lazy"
        className={`object-cover w-full h-full ${className}`}
        onError={handleImageError}
      />
    </picture>
  );
};

export default ImageWithFallback;