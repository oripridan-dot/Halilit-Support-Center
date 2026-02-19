import React, { useMemo } from 'react';
import { useConductorCatalog, useJITIntelligence } from '../../hooks';

interface SourcingBadgeProps {
  source: 'Official Scout' | 'Inferred Scout';
  'aria-label': string;
}

const SourcingBadge: React.FC<SourcingBadgeProps> = ({ source, 'aria-label': ariaLabel }) => {
  let badgeStyle = '';
  let badgeText = '';

  switch (source) {
    case 'Official Scout':
      badgeStyle = 'bg-blue-100 text-blue-800 dark:bg-blue-700 dark:text-blue-300';
      badgeText = 'Official Scout';
      break;
    case 'Inferred Scout':
      badgeStyle = 'bg-purple-100 text-purple-800 dark:bg-purple-700 dark:text-purple-300';
      badgeText = 'Inferred Scout';
      break;
  }

  return (
    <span
      aria-label={ariaLabel}
      className={`absolute top-0 right-0 text-xs font-semibold mr-2 px-2.5 py-0.5 rounded ${badgeStyle}`}
    >
      {badgeText}
    </span>
  );
};

interface ProductImageProps {
  imageUrl: string | undefined;
  altText: string;
}

const ProductImage: React.FC<ProductImageProps> = ({ imageUrl, altText }) => {
  const isJIT = imageUrl?.includes('thumbnail');

  if (!imageUrl) {
    return (
      <div className="w-full h-64 flex items-center justify-center bg-slate-900 text-white">
        No image available
      </div>
    );
  }

  const badgeSource = isJIT ? 'Inferred Scout' : 'Official Scout';
  const badgeAriaLabel = `Source: ${badgeSource}`;


  return (
    <div className="relative">
      <img src={imageUrl} alt={altText} className="w-full h-64 object-contain" />
      <SourcingBadge source={badgeSource} aria-label={badgeAriaLabel} />
    </div>
  );
};

export default ProductImage;