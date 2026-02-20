import React from 'react';

interface ImageWithFallbackProps {
  imageUrl: string | null | undefined;
  altText: string;
}

const ImageWithFallback: React.FC<ImageWithFallbackProps> = ({ imageUrl, altText }) => {
  const placeholderImage = '/placeholder.png';
  const cdnBaseUrl = 'https://cdn.example.com';

  const generateCdnUrl = (width: number, format: 'avif' | 'webp' | 'jpg') => {
    if (!imageUrl) {
      return null;
    }
    return `${cdnBaseUrl}/${imageUrl}?width=${width}&format=${format}&quality=auto`;
  };

  if (!imageUrl) {
    return <img src={placeholderImage} alt={altText} className="w-full h-full object-cover" />;
  }

  const smallAvifUrl = generateCdnUrl(320, 'avif');
  const mediumAvifUrl = generateCdnUrl(640, 'avif');
  const largeAvifUrl = generateCdnUrl(1024, 'avif');

  const smallWebpUrl = generateCdnUrl(320, 'webp');
  const mediumWebpUrl = generateCdnUrl(640, 'webp');
  const largeWebpUrl = generateCdnUrl(1024, 'webp');

  const fallbackJpegUrl = generateCdnUrl(1024, 'jpg');


  return (
    <picture>
      {smallAvifUrl && <source srcSet={smallAvifUrl} type="image/avif" media="(max-width: 320px)" />}
      {mediumAvifUrl && <source srcSet={mediumAvifUrl} type="image/avif" media="(max-width: 640px)" />}
      {largeAvifUrl && <source srcSet={largeAvifUrl} type="image/avif" media="(min-width: 641px)" />}

      {smallWebpUrl && <source srcSet={smallWebpUrl} type="image/webp" media="(max-width: 320px)" />}
      {mediumWebpUrl && <source srcSet={mediumWebpUrl} type="image/webp" media="(max-width: 640px)" />}
      {largeWebpUrl && <source srcSet={largeWebpUrl} type="image/webp" media="(min-width: 641px)" />}

      <img
        src={fallbackJpegUrl || placeholderImage}
        alt={altText}
        loading="lazy"
        className="w-full h-full object-cover"
        onError={(e) => {
          if (e.target) {
            e.target.src = placeholderImage;
          }
        }}
      />
    </picture>
  );
};

export default ImageWithFallback;