import React, { useState } from "react";

interface ImageWithFallbackProps {
  imageUrl: string | undefined | null;
  altText?: string;
  className?: string;
  /** Set to true for hero/above-fold images so they are not lazy-loaded. */
  eager?: boolean;
}

/**
 * Derive a WebP variant URL from a JPEG/PNG/GIF URL.
 * Convention: replace extension with .webp (common CDN behaviour).
 * If the server does not serve WebP at that path, the browser's native
 * <picture> fallback kicks in and the original <img> src is used instead.
 */
function toWebpSrc(url: string): string | null {
  if (!url || url === "/placeholder.png") return null;
  const replaced = url.replace(/\.(jpe?g|png|gif)(\?.*)?$/i, ".webp$2");
  return replaced !== url ? replaced : null;
}

const ImageWithFallback: React.FC<ImageWithFallbackProps> = ({
  imageUrl,
  altText,
  className = "w-full h-full object-contain",
  eager = false,
}) => {
  const [failed, setFailed] = useState(false);

  const src = !failed && imageUrl ? imageUrl : "/placeholder.png";
  const webpSrc = !failed ? toWebpSrc(src) : null;
  const defaultAltText = altText || "Product Image";

  const handleError = () => {
    if (!failed) setFailed(true);
  };

  return (
    <picture>
      {webpSrc && <source srcSet={webpSrc} type="image/webp" />}
      <img
        src={src}
        alt={defaultAltText}
        className={className}
        loading={eager ? "eager" : "lazy"}
        decoding="async"
        onError={handleError}
      />
    </picture>
  );
};

export default ImageWithFallback;
