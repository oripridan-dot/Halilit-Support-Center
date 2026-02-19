import { useState, useEffect, useMemo } from 'react';
import { useDebounce } from './useDebounce';
import { useValidateHeroImage } from './useValidateHeroImage';

interface UseImageRefreshProps {
  imageUrl: string | undefined | null;
  productId: string;
  isHero?: boolean;
}

export const useImageRefresh = ({ imageUrl, productId, isHero }: UseImageRefreshProps) => {
  const [cacheBustedImageUrl, setCacheBustedImageUrl] = useState<string | undefined>(imageUrl);
  const debouncedImageUrl = useDebounce(imageUrl, 200);

  const hashString = useMemo(() => {
    if (!imageUrl || !productId) {
      return '';
    }
    return `${imageUrl}-${productId}`;
  }, [imageUrl, productId]);

  useEffect(() => {
    if (debouncedImageUrl) {
      const cacheBustParam = `cacheBust=${Date.now()}`;
      const newUrl = debouncedImageUrl.includes('?')
        ? `${debouncedImageUrl}&${cacheBustParam}`
        : `${debouncedImageUrl}?${cacheBustParam}`;
      setCacheBustedImageUrl(newUrl);
    } else {
      setCacheBustedImageUrl(debouncedImageUrl);
    }
  }, [debouncedImageUrl, hashString]);


  const { isValidating, isValid } = useValidateHeroImage(cacheBustedImageUrl || '');


  return {
    cacheBustedImageUrl: isHero && isValid === false ? '/placeholder.png' : cacheBustedImageUrl,
    isValidating,
    isValid,
  };
};