import React from 'react';

interface ImageWithFallbackProps {
  imageUrl: string | null | undefined;
  altText: string;
  placeholderImageUrl: string;
}

const ImageWithFallback: React.FC<ImageWithFallbackProps> = ({
  imageUrl,
  altText,
  placeholderImageUrl,
}) => {
  const cdnUrl = 'https://cdn.example.com';

  if (!imageUrl) {
    return (
      <img
        src={placeholderImageUrl}
        alt={altText}
        className="rounded-md object-cover w-full h-full bg-slate-900"
        loading="lazy"
      />
    );
  }

  const generateSrcSet = (width: number, format: 'avif' | 'webp' | 'jpeg') => {
    return `${cdnUrl}/${imageUrl}?width=${width}&format=${format} ${width}w`;
  };

  return (
    <picture>
      <source
        srcSet={`
          ${generateSrcSet(320, 'avif')},
          ${generateSrcSet(640, 'avif')} 2x,
          ${generateSrcSet(1024, 'avif')} 3x
        `}
        type="image/avif"
      />
      <source
        srcSet={`
          ${generateSrcSet(320, 'webp')},
          ${generateSrcSet(640, 'webp')} 2x,
          ${generateSrcSet(1024, 'webp')} 3x
        `}
        type="image/webp"
      />
      <img
        src={`${cdnUrl}/${imageUrl}?width=640&format=jpeg`}
        alt={altText}
        loading="lazy"
        className="rounded-md object-cover w-full h-full bg-slate-900"
        onError={(e) => {
          (e.target as HTMLImageElement).src = placeholderImageUrl;
        }}
      />
    </picture>
  );
};

export default ImageWithFallback;