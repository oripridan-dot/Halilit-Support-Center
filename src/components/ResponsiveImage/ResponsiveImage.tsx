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
  sizes = {},
}) => {
  const CDN_BASE_URL = process.env.NEXT_PUBLIC_IMAGE_CDN_URL;

  if (!CDN_BASE_URL) {
    console.warn('NEXT_PUBLIC_IMAGE_CDN_URL is not configured.');
    return (
      <picture className={className}>
        <img src={imageBaseUrl} alt={altText} loading="lazy" className="w-full h-full object-cover" />
      </picture>
    );
  }

  const generateSrcSet = (width: number, format: 'avif' | 'webp' | 'jpg') => {
    return `${CDN_BASE_URL}/${imageBaseUrl.replace(/\.(jpg|jpeg|png)$/, '')}_${width}.${format}`;
  };

  const breakpoints = {
    sm: sizes.sm || 640,
    md: sizes.md || 768,
    lg: sizes.lg || 1024,
    xl: sizes.xl || 1280,
    "2xl": sizes["2xl"] || 1536,
  };

  const hasBreakpoints = Object.keys(breakpoints).length > 0;

  return (
    <picture className={className}>
      {hasBreakpoints &&
        Object.entries(breakpoints)
          .sort(([, widthA], [, widthB]) => (widthA as number) - (widthB as number))
          .map(([size, width]) => {
            const maxWidth = width;
            const mediaQuery = `(min-width: ${maxWidth}px)`;

            return (
              <React.Fragment key={`${size}-avif`}>
                <source
                  srcSet={generateSrcSet(width as number, 'avif')}
                  type="image/avif"
                  media={mediaQuery}
                />
                <source
                  srcSet={generateSrcSet(width as number, 'webp')}
                  type="image/webp"
                  media={mediaQuery}
                />
              </React.Fragment>
            );
          })}
      <img
        src={`${CDN_BASE_URL}/${imageBaseUrl}`}
        alt={altText}
        loading="lazy"
        className="w-full h-full object-cover"
      />
    </picture>
  );
};

export default ResponsiveImage;