import { useState, useEffect, useCallback } from 'react';

interface UseValidateHeroImageResult {
  isValidating: boolean;
  isValid: boolean | null;
}

const CACHE_KEY_PREFIX = 'image_validation:';
const CACHE_EXPIRY_MS = 24 * 60 * 60 * 1000; // 24 hours

function useValidateHeroImage(imageUrl: string): UseValidateHeroImageResult {
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [isValid, setIsValid] = useState<boolean | null>(null);

  const debouncedValidate = useCallback(
    (url: string) => {
      let timeoutId: NodeJS.Timeout | null = null;

      const validate = async () => {
        if (!url) {
          setIsValid(false);
          return;
        }

        setIsValidating(true);

        const cachedResult = localStorage.getItem(`${CACHE_KEY_PREFIX}${url}`);
        if (cachedResult) {
          const { isValid: cachedIsValid, timestamp } = JSON.parse(cachedResult);
          if (Date.now() - timestamp < CACHE_EXPIRY_MS) {
            setIsValid(cachedIsValid);
            setIsValidating(false);
            return;
          } else {
            localStorage.removeItem(`${CACHE_KEY_PREFIX}${url}`); // Expired, remove from cache
          }
        }

        try {
          const response = await fetch(url, { method: 'HEAD', signal: AbortSignal.timeout(5000) });
          const isValid = response.status >= 200 && response.status < 300;
          setIsValid(isValid);
          if (!isValid) {
            localStorage.setItem(`${CACHE_KEY_PREFIX}${url}`, JSON.stringify({ isValid: false, timestamp: Date.now() }));
          }
        } catch (error: any) {
          console.error(`Error validating image ${url}:`, error);
          setIsValid(false);
          localStorage.setItem(`${CACHE_KEY_PREFIX}${url}`, JSON.stringify({ isValid: false, timestamp: Date.now() }));
        } finally {
          setIsValidating(false);
        }
      };
      
      timeoutId = setTimeout(validate, 500);

      return () => {
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
      };

    },
    []
  );

  useEffect(() => {
    debouncedValidate(imageUrl);
    return () => {
      // Cleanup function to clear the timeout if the component unmounts or the URL changes
      // This is handled inside debouncedValidate already
    };
  }, [imageUrl, debouncedValidate]);

  return { isValidating, isValid };
}

export { useValidateHeroImage, UseValidateHeroImageResult };