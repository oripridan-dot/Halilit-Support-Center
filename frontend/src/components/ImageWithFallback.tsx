import React from 'react';

interface DataTrust {
  source?: string;
  provider?: string;
  [key: string]: any;
}

interface ImageWithFallbackProps {
  imageUrl: string | null | undefined;
  altText: string;
  dataTrust?: DataTrust;
}

const ImageWithFallback: React.FC<ImageWithFallbackProps> = ({ imageUrl, altText, dataTrust }) => {
  const sizes = '(max-width: 320px) 320px, (max-width: 640px) 640px, 1024px';
  const placeholderSrc = '/placeholder.png'; // Assuming placeholder.png is in the public directory

  const generateSrcSet = (width: number, format: 'avif' | 'webp' | 'jpg') => {
    if (!imageUrl) return '';

    let formatParam = '';
    switch (format) {
      case 'avif':
        formatParam = 'f_auto,q_auto';
        break;
      case 'webp':
        formatParam = 'f_webp,q_auto';
        break;
      case 'jpg':
        formatParam = 'f_jpg,q_auto';
        break;
      default:
        formatParam = 'f_auto,q_auto';
    }

    return `${imageUrl}?${formatParam},w_${width} ${width}w`;
  };

  const getAltText = () => {
    if (dataTrust && dataTrust.source) {
      return `${altText} (Source: ${dataTrust.source})`;
    }
    return altText;
  };

  if (!imageUrl) {
    return (
      <div className="bg-slate-900 w-full h-full flex items-center justify-center">
        <img src={placeholderSrc} alt={altText} className="object-cover" loading="lazy" />
      </div>
    );
  }

  return (
    <picture>
      <source
        srcSet={`${generateSrcSet(320, 'avif')}, ${generateSrcSet(640, 'avif')}, ${generateSrcSet(1024, 'avif')}`}
        type="image/avif"
      />
      <source
        srcSet={`${generateSrcSet(320, 'webp')}, ${generateSrcSet(640, 'webp')}, ${generateSrcSet(1024, 'webp')}`}
        type="image/webp"
      />
      <img
        src={`${imageUrl}?f_jpg,q_auto`}
        srcSet={`${generateSrcSet(320, 'jpg')}, ${generateSrcSet(640, 'jpg')}, ${generateSrcSet(1024, 'jpg')}`}
        alt={getAltText()}
        loading="lazy"
        sizes={sizes}
        onError={(e) => {
          (e.target as HTMLImageElement).src = placeholderSrc;
        }}
      />
    </picture>
  );
};

export default ImageWithFallback;