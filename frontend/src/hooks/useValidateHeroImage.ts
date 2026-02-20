// frontend/src/hooks/useValidateHeroImage.ts
import { useState, useEffect, useCallback } from 'react';

interface UseValidateHeroImageResult {
  isValidating: boolean;
  isValid: boolean | null;
}

const CACHE_KEY_PREFIX = 'image_validation:';
const CACHE_DURATION_MS = 24 * 60 * 60 * 1000; // 24 hours

function useValidateHeroImage(imageUrl: string): UseValidateHeroImageResult {
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [isValid, setIsValid] = useState<boolean | null>(null);

  const checkCache = useCallback((url: string) => {
    const cacheKey = `${CACHE_KEY_PREFIX}${url}`;
    const cachedData = localStorage.getItem(cacheKey);

    if (cachedData) {
      try {
        const { isValid: cachedIsValid, timestamp } = JSON.parse(cachedData);
        if (Date.now() - timestamp < CACHE_DURATION_MS) {
          return cachedIsValid;
        } else {
          localStorage.removeItem(cacheKey); // Expired cache
          return null;
        }
      } catch (error) {
        console.error('Error parsing cached data:', error);
        localStorage.removeItem(cacheKey); // Corrupted cache
        return null;
      }
    }
    return null;
  }, []);

  const setCache = useCallback((url: string, isValid: boolean) => {
    const cacheKey = `${CACHE_KEY_PREFIX}${url}`;
    const cacheData = JSON.stringify({ isValid, timestamp: Date.now() });
    localStorage.setItem(cacheKey, cacheData);
  }, []);

  useEffect(() => {
    if (!imageUrl) {
      setIsValid(false);
      return;
    }

    const cachedIsValid = checkCache(imageUrl);
    if (cachedIsValid !== null) {
      setIsValid(cachedIsValid);
      return;
    }


    const validateImage = async () => {
      setIsValidating(true);
      try {
        const response = await fetch(imageUrl, { method: 'HEAD', signal: AbortSignal.timeout(5000) });
        const isValid = response.ok && response.status >= 200 && response.status < 300;
        setIsValid(isValid);
        if (!isValid) {
          setCache(imageUrl, false);
        }
      } catch (error: any) {
        console.error(`Error validating image ${imageUrl}:`, error);
        setIsValid(false);
        setCache(imageUrl, false);
      } finally {
        setIsValidating(false);
      }
    };

    const timeoutId = setTimeout(() => {
        validateImage();
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [imageUrl, checkCache, setCache]);

  return { isValidating, isValid };
}

export { useValidateHeroImage };