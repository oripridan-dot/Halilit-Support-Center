import React from 'react';

interface ResponsiveImageProps {
  imageBaseUrl: string;
  alt: string;
  sizes: {
    [key: string]: number;
  };
  className?: string;
}

const ResponsiveImage: React.FC<ResponsiveImageProps> = ({
  imageBaseUrl,
  alt,
  sizes,
  className,
}) => {
  const cdnBaseUrl = process.env.NEXT_PUBLIC_CDN_BASE_URL;

  if (!cdnBaseUrl) {
    console.error("NEXT_PUBLIC_CDN_BASE_URL is not defined");
    return (
      <img
        src="" // Or a placeholder
        alt={alt}
        className={`w-full h-auto ${className || ''}`}
        loading="lazy"
      />
    );
  }

  const generateImageUrl = (width: number, format: 'avif' | 'webp' | 'jpg') => {
    return `${cdnBaseUrl}/${imageBaseUrl}_${width}.${format}`;
  };

  const hasSizes = Object.keys(sizes).length > 0;

  if (!hasSizes) {
    return (
      <img
        src={`${cdnBaseUrl}/${imageBaseUrl}_.jpg`}
        alt={alt}
        className={`w-full h-auto ${className || ''}`}
        loading="lazy"
      />
    );
  }


  return (
    <picture>
      {Object.entries(sizes).map(([key, width]) => (
        <React.Fragment key={key}>
          <source
            srcSet={generateImageUrl(width, 'avif')}
            type="image/avif"
            media={`(max-width: ${width}px)`}
          />
          <source
            srcSet={generateImageUrl(width, 'webp')}
            type="image/webp"
            media={`(max-width: ${width}px)`}
          />
        </React.Fragment>
      ))}
      <img
        src={generateImageUrl(
          Object.values(sizes).sort((a, b) => b - a)[0] || 1,
          'jpg'
        )}
        alt={alt}
        className={`w-full h-auto ${className || ''}`}
        loading="lazy"
      />
    </picture>
  );
};

export default ResponsiveImage;