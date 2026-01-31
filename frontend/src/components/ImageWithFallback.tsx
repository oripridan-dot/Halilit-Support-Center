import { AlertCircle } from "lucide-react";
import { useState } from "react";

interface ImageWithFallbackProps {
  src?: string;
  alt: string;
  fallbackText?: string;
  className?: string;
}

export const ImageWithFallback = ({
  src,
  alt,
  fallbackText,
  className = "",
}: ImageWithFallbackProps) => {
  const [hasError, setHasError] = useState(!src);
  const [isLoading, setIsLoading] = useState(true);

  if (hasError) {
    return (
      <div
        className={`flex items-center justify-center bg-gradient-to-br from-zinc-800 to-zinc-900 rounded-lg border border-zinc-700 ${className}`}
      >
        <div className="flex flex-col items-center gap-2 text-center p-4">
          <AlertCircle className="w-8 h-8 text-zinc-500" />
          <div className="text-xs text-zinc-500 font-mono">
            No Image Available
          </div>
          {fallbackText && (
            <div className="text-[10px] text-zinc-600">{fallbackText}</div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div
      className={`relative overflow-hidden bg-gradient-to-br from-zinc-800 to-zinc-900 rounded-lg border border-zinc-700 ${className}`}
    >
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-zinc-800/50">
          <div className="animate-pulse text-xs text-zinc-400">Loading...</div>
        </div>
      )}
      <img
        src={src}
        alt={alt}
        className="w-full h-full object-contain opacity-90 hover:opacity-100 transition-opacity"
        onLoad={() => setIsLoading(false)}
        onError={() => {
          setHasError(true);
          setIsLoading(false);
        }}
      />
    </div>
  );
};
