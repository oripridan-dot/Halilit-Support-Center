import { useState, useEffect } from 'react';

interface UseValidateHeroImageResult {
  isValidating: boolean;
  isValid: boolean | null;
}

/**
 * Probes an image URL by loading it in a hidden Image element.
 * Returns { isValidating, isValid } where isValid is null until
 * the probe settles, true if the image loaded, false if it errored.
 */
export const useValidateHeroImage = (url: string): UseValidateHeroImageResult => {
  const [isValidating, setIsValidating] = useState(false);
  const [isValid, setIsValid] = useState<boolean | null>(null);

  useEffect(() => {
    if (!url) {
      setIsValidating(false);
      setIsValid(null);
      return;
    }

    setIsValidating(true);
    setIsValid(null);

    const img = new Image();

    img.onload = () => {
      setIsValidating(false);
      setIsValid(true);
    };

    img.onerror = () => {
      setIsValidating(false);
      setIsValid(false);
    };

    img.src = url;

    return () => {
      img.onload = null;
      img.onerror = null;
    };
  }, [url]);

  return { isValidating, isValid };
};

