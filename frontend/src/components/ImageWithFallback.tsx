import React from 'react';

interface ImageWithFallbackProps {
  imageUrl: string | undefined | null;
  altText?: string;
}

const ImageWithFallback: React.FC<ImageWithFallbackProps> = ({ imageUrl, altText }) => {
  const defaultAltText = altText || "Product Image";
  const placeholderImage = "/placeholder.png";
  const cdnBaseUrl = "https://cdn.example.com"; // Replace with your CDN base URL

  const generateSrcSet = (width: number, format: 'avif' | 'webp' | 'jpg') => {
    if (!imageUrl) return '';
    return `${cdnBaseUrl}/${imageUrl}?width=${width}&format=${format}&quality=auto`;
  };

  if (!imageUrl) {
    return (
      <div className="bg-slate-900">
        <img
          src={placeholderImage}
          alt={defaultAltText}
          className="w-full h-full object-cover"
          loading="lazy"
        />
      </div>
    );
  }

  return (
    <picture>
      <source
        srcSet={`${generateSrcSet(320, 'avif')}`}
        type="image/avif"
        media="(max-width: 320px)"
      />
      <source
        srcSet={`${generateSrcSet(640, 'avif')}`}
        type="image/avif"
        media="(max-width: 640px)"
      />
      <source
        srcSet={`${generateSrcSet(1024, 'avif')}`}
        type="image/avif"
        media="(min-width: 641px)"
      />
      <source
        srcSet={`${generateSrcSet(320, 'webp')}`}
        type="image/webp"
        media="(max-width: 320px)"
      />
      <source
        srcSet={`${generateSrcSet(640, 'webp')}`}
        type="image/webp"
        media="(max-width: 640px)"
      />
      <source
        srcSet={`${generateSrcSet(1024, 'webp')}`}
        type="image/webp"
        media="(min-width: 641px)"
      />
      <img
        src={`${generateSrcSet(1024, 'jpg')}`}
        alt={defaultAltText}
        loading="lazy"
        className="w-full h-full object-cover"
        onError={(e) => (e.target.src = placeholderImage)}
      />
    </picture>
  );
};

export default ImageWithFallback;