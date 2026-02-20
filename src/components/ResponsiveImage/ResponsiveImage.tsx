import React from 'react';

interface ResponsiveImageProps {
  imageBaseUrl: string;
  altText: string;
  className?: string;
  sizes?: {
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
    "2xl"?: number;
  };
}

const ResponsiveImage: React.FC<ResponsiveImageProps> = ({
  imageBaseUrl,
  altText,
  className,
  sizes,
}) => {
  const CDN_BASE_URL = process.env.NEXT_PUBLIC_IMAGE_CDN_URL;

  if (!CDN_BASE_URL) {
    console.error('NEXT_PUBLIC_IMAGE_CDN_URL is not defined');
    return (
      <div className="bg-slate-900 text-red-500 p-2">
        Image CDN URL not configured.
      </div>
    );
  }

  const generateImageUrl = (width: number, format: 'avif' | 'webp' | 'jpg' | 'png') => {
    return `${CDN_BASE_URL}/${imageBaseUrl.replace(/\.(jpg|jpeg|png)$/, '')}_${width}.${format}`;
  };

  const hasSizes = sizes && Object.keys(sizes).length > 0;

  return (
    <picture className={className}>
      {hasSizes &&
        Object.entries(sizes!).map(([key, width]) => (
          <>
            <source
              key={`${key}-avif`}
              srcSet={generateImageUrl(width!, 'avif')}
              media={`(min-width: ${width}px)`}
              type="image/avif"
            />
            <source
              key={`${key}-webp`}
              srcSet={generateImageUrl(width!, 'webp')}
              media={`(min-width: ${width}px)`}
              type="image/webp"
            />
          </>
        ))}
      <img
        src={`${CDN_BASE_URL}/${imageBaseUrl}`}
        alt={altText}
        loading="lazy"
      />
    </picture>
  );
};

export default ResponsiveImage;