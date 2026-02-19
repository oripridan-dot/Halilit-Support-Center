import { useState, useEffect, useCallback } from 'react';

interface UseValidateHeroImageResult {
  isValidating: boolean;
  isValid: boolean | null;
}

const CACHE_KEY_PREFIX = 'hero_image_validation:';
const CACHE_DURATION_MS = 24 * 60 * 60 * 1000; // 24 hours

function useValidateHeroImage(imageUrl: string): UseValidateHeroImageResult {
  const [isValidating, setIsValidating] = useState(false);
  const [isValid, setIsValid] = useState<boolean | null>(null);

  const validateImage = useCallback(async (url: string) => {
    if (!url) {
      setIsValid(false);
      return;
    }

    const cachedResult = localStorage.getItem(`${CACHE_KEY_PREFIX}${url}`);
    if (cachedResult) {
      const { isValid: cachedIsValid, timestamp } = JSON.parse(cachedResult);
      if (Date.now() - timestamp < CACHE_DURATION_MS) {
        setIsValid(cachedIsValid);
        return;
      } else {
        localStorage.removeItem(`${CACHE_KEY_PREFIX}${url}`); // Expired cache
      }
    }

    setIsValidating(true);
    try {
      const response = await fetch(url, { method: 'HEAD', signal: AbortSignal.timeout(5000) });
      const isValid = response.ok && response.status >= 200 && response.status < 300;
      setIsValid(isValid);
      if (!isValid) {
        localStorage.setItem(`${CACHE_KEY_PREFIX}${url}`, JSON.stringify({ isValid: false, timestamp: Date.now() }));
      } else {
        localStorage.removeItem(`${CACHE_KEY_PREFIX}${url}`);
      }
    } catch (error: any) {
      console.error('Image validation error:', error);
      setIsValid(false);
      localStorage.setItem(`${CACHE_KEY_PREFIX}${url}`, JSON.stringify({ isValid: false, timestamp: Date.now() }));
    } finally {
      setIsValidating(false);
    }
  }, []);

  useEffect(() => {
    validateImage(imageUrl);
  }, [imageUrl, validateImage]);

  return { isValidating, isValid };
}

export default useValidateHeroImage;