import { useState, useEffect, useRef } from 'react';

interface UseValidateHeroImageResult {
  isValidating: boolean;
  isValid: boolean | null;
}

const CACHE_KEY_PREFIX = 'image_validation:';
const CACHE_DURATION_MS = 24 * 60 * 60 * 1000; // 24 hours

function useValidateHeroImage(imageUrl: string): UseValidateHeroImageResult {
  const [isValidating, setIsValidating] = useState(false);
  const [isValid, setIsValid] = useState<boolean | null>(null);
  const debounceTimeout = useRef<NodeJS.Timeout | null>(null);

  const clearDebounce = () => {
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
      debounceTimeout.current = null;
    }
  };

  const validateImage = async (url: string) => {
    if (!url) {
      setIsValid(false);
      return;
    }

    setIsValidating(true);

    const cachedResult = localStorage.getItem(`${CACHE_KEY_PREFIX}${url}`);
    if (cachedResult) {
      const { isValid: cachedIsValid, timestamp } = JSON.parse(cachedResult);
      if (Date.now() - timestamp < CACHE_DURATION_MS) {
        setIsValid(cachedIsValid);
        setIsValidating(false);
        return;
      } else {
        localStorage.removeItem(`${CACHE_KEY_PREFIX}${url}`); // Expired cache
      }
    }

    try {
      const response = await fetch(url, { method: 'HEAD', cache: 'no-cache' });
      const isValid = response.ok && response.status >= 200 && response.status < 300;
      setIsValid(isValid);
      if (!isValid) {
        localStorage.setItem(`${CACHE_KEY_PREFIX}${url}`, JSON.stringify({ isValid: false, timestamp: Date.now() }));
      }
    } catch (error) {
      console.error('Image validation error:', error);
      setIsValid(false);
      localStorage.setItem(`${CACHE_KEY_PREFIX}${url}`, JSON.stringify({ isValid: false, timestamp: Date.now() }));
    } finally {
      setIsValidating(false);
    }
  };

  useEffect(() => {
    if (!imageUrl) {
      setIsValid(false);
      return;
    }
    clearDebounce();
    debounceTimeout.current = setTimeout(() => {
      validateImage(imageUrl);
    }, 500);

    return () => {
      clearDebounce();
    };
  }, [imageUrl]);

  return { isValidating, isValid };
}

export { useValidateHeroImage, UseValidateHeroImageResult };