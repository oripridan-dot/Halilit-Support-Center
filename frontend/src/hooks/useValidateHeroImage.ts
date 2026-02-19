import { useState, useEffect, useCallback } from 'react';

interface UseValidateHeroImageResult {
  isValidating: boolean;
  isValid: boolean | null;
}

function useValidateHeroImage(imageUrl: string): UseValidateHeroImageResult {
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [isValid, setIsValid] = useState<boolean | null>(null);

  const validateImage = useCallback(
    (url: string) => {
      if (!url) {
        setIsValid(false);
        return;
      }

      const cachedInvalid = localStorage.getItem(`invalidImage:${url}`);
      if (cachedInvalid) {
        setIsValid(false);
        return;
      }

      setIsValidating(true);
      setIsValid(null);

      fetch(url, { method: 'HEAD' })
        .then(response => {
          const valid = response.status >= 200 && response.status <= 299;
          setIsValid(valid);
          setIsValidating(false);

          if (!valid) {
            localStorage.setItem(`invalidImage:${url}`, 'true');
            setTimeout(() => {
              localStorage.removeItem(`invalidImage:${url}`);
            }, 24 * 60 * 60 * 1000); // 24 hours
          }
        })
        .catch(error => {
          console.error('Error validating image:', error);
          setIsValid(false);
          setIsValidating(false);

          localStorage.setItem(`invalidImage:${url}`, 'true');
          setTimeout(() => {
            localStorage.removeItem(`invalidImage:${url}`);
          }, 24 * 60 * 60 * 1000); // 24 hours
        });
    },
    []
  );

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    if (imageUrl) {
      timeoutId = setTimeout(() => {
        validateImage(imageUrl);
      }, 500);
    } else {
      setIsValid(false);
    }

    return () => clearTimeout(timeoutId);
  }, [imageUrl, validateImage]);

  return { isValidating, isValid };
}

export default useValidateHeroImage;