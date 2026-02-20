import { useState, useEffect, useRef } from 'react';

interface UseValidateHeroImageResult {
  isValidating: boolean;
  isValid: boolean | null;
}

const CACHE_KEY_PREFIX = 'hero_image_validation:';
const CACHE_EXPIRY_MS = 24 * 60 * 60 * 1000; // 24 hours

function useValidateHeroImage(imageUrl: string | undefined | null): UseValidateHeroImageResult {
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [isValid, setIsValid] = useState<boolean | null>(null);
  const debounceTimeout = useRef<NodeJS.Timeout | null>(null);

  const clearDebounce = () => {
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
      debounceTimeout.current = null;
    }
  };

  useEffect(() => {
    if (!imageUrl) {
      setIsValid(false);
      return;
    }

    const cachedResult = localStorage.getItem(`${CACHE_KEY_PREFIX}${imageUrl}`);
    if (cachedResult) {
      const { isValid: cachedIsValid, timestamp } = JSON.parse(cachedResult);
      if (Date.now() - timestamp < CACHE_EXPIRY_MS) {
        setIsValid(cachedIsValid);
        return;
      } else {
          localStorage.removeItem(`${CACHE_KEY_PREFIX}${imageUrl}`);
      }
    }

    clearDebounce();
    setIsValidating(true);
    setIsValid(null);

    const validateImage = async () => {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 seconds timeout

        const response = await fetch(imageUrl, { method: 'HEAD', signal: controller.signal });
        clearTimeout(timeoutId);

        if (response.ok) {
          setIsValid(true);
        } else {
          setIsValid(false);
          localStorage.setItem(`${CACHE_KEY_PREFIX}${imageUrl}`, JSON.stringify({ isValid: false, timestamp: Date.now() }));
        }
      } catch (error: any) {
        console.error(`Error validating image ${imageUrl}:`, error);
        setIsValid(false);
        localStorage.setItem(`${CACHE_KEY_PREFIX}${imageUrl}`, JSON.stringify({ isValid: false, timestamp: Date.now() }));
      } finally {
        setIsValidating(false);
      }
    };


    debounceTimeout.current = setTimeout(() => {
        validateImage();
    }, 500);

    return () => {
        clearDebounce();
    };


  }, [imageUrl]);

  return { isValidating, isValid };
}

export { useValidateHeroImage, UseValidateHeroImageResult };