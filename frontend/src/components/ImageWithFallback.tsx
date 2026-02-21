import React from "react";

interface ImageWithFallbackProps {
  imageUrl: string | undefined | null;
  altText?: string;
  className?: string;
}

const ImageWithFallback: React.FC<ImageWithFallbackProps> = ({
  imageUrl,
  altText,
  className = "w-full h-full object-contain",
}) => {
  const src = imageUrl || "/placeholder.png";
  const defaultAltText = altText || "Product Image";

  return (
    <img
      src={src}
      alt={defaultAltText}
      className={className}
      loading="lazy"
      onError={(e) => {
        e.currentTarget.onerror = null;
        e.currentTarget.src = "/placeholder.png";
      }}
    />
  );
};

export default ImageWithFallback;
