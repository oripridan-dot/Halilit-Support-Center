import { useState, useEffect, useRef } from 'react';

interface UseValidateHeroImageResult {
  isValidating: boolean;
  isValid: boolean | null;
}

const CACHE_KEY_PREFIX = 'image_validation:';
const CACHE_EXPIRY_MS = 24 * 60 * 60 * 1000; // 24 hours

function useValidateHeroImage(imageUrl: string): UseValidateHeroImageResult {
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [isValid, setIsValid] = useState<boolean | null>(null);
  const debounceTimeout = useRef<NodeJS.Timeout | null>(null);
  const initialLoad = useRef(true);

  const clearDebounce = () => {
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
      debounceTimeout.current = null;
    }
  };

  const getCacheKey = (url: string) => `${CACHE_KEY_PREFIX}${url}`;

  const getCachedResult = (url: string): boolean | null => {
    const cacheKey = getCacheKey(url);
    const cachedData = localStorage.getItem(cacheKey);
    if (!cachedData) {
      return null;
    }
    try {
      const { isValid, timestamp } = JSON.parse(cachedData);
      if (Date.now() - timestamp < CACHE_EXPIRY_MS) {
        return isValid;
      }
      localStorage.removeItem(cacheKey); // Expired, remove from cache
      return null;
    } catch (error) {
      console.error('Error parsing cached image validation result:', error);
      localStorage.removeItem(cacheKey); // Corrupted data, remove from cache
      return null;
    }
  };


  const setCachedResult = (url: string, isValid: boolean) => {
    const cacheKey = getCacheKey(url);
    const cacheData = JSON.stringify({ isValid, timestamp: Date.now() });
    localStorage.setItem(cacheKey, cacheData);
  };

  useEffect(() => {
    if (initialLoad.current) {
      initialLoad.current = false;
      return;
    }

    clearDebounce();

    if (!imageUrl) {
      setIsValid(false);
      return;
    }

    const cachedResult = getCachedResult(imageUrl);
    if (cachedResult !== null) {
      setIsValid(cachedResult);
      return;
    }


    setIsValidating(true);

    debounceTimeout.current = setTimeout(() => {
      const validateImage = async () => {
        try {
          const response = await fetch(imageUrl, { method: 'HEAD', cache: 'no-cache' });
          const isValid = response.ok && response.status >= 200 && response.status < 300;
          setIsValid(isValid);
          if (!isValid) {
            setCachedResult(imageUrl, false);
          }
        } catch (error) {
          console.error('Image validation error:', error);
          setIsValid(false);
          setCachedResult(imageUrl, false);
        } finally {
          setIsValidating(false);
        }
      };
      validateImage();

    }, 500); // Debounce
    return () => {
        clearDebounce();
    };

  }, [imageUrl]);

  return { isValidating, isValid };
}

export default useValidateHeroImage;