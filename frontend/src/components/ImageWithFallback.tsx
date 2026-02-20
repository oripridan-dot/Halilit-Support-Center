import React from 'react';

interface ImageWithFallbackProps {
    imageUrl: string | undefined | null;
    altText?: string;
}

const ImageWithFallback: React.FC<ImageWithFallbackProps> = ({ imageUrl, altText }) => {
    const defaultAltText = altText || "Product Image";

    return (
        <div className="bg-slate-900">
            <img
                src={imageUrl || "/placeholder.png"}
                alt={defaultAltText}
                onError={(e) => {
                    (e.target as HTMLImageElement).src = "/placeholder.png";
                }}
                className="w-full h-full object-contain"
                loading="lazy"
            />
        </div>
    );
};

export default ImageWithFallback;