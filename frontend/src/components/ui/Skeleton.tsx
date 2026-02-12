import React from "react";

interface SkeletonProps {
  className?: string;
  variant?: "text" | "rect" | "circle" | "card";
  count?: number;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = "",
  variant = "rect",
  count = 1,
}) => {
  const baseClass = "animate-pulse bg-zinc-800/60 rounded";

  const variantClass = {
    text: "h-4 w-full rounded",
    rect: "h-32 w-full rounded-lg",
    circle: "h-12 w-12 rounded-full",
    card: "h-64 w-full rounded-xl",
  }[variant];

  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className={`${baseClass} ${variantClass} ${className}`} />
      ))}
    </>
  );
};

/** Skeleton matching the product card layout in Spectrum swim lanes */
export const ProductCardSkeleton: React.FC = () => (
  <div className="bg-zinc-900/50 rounded-xl border border-zinc-800/50 p-4 space-y-3">
    <Skeleton variant="rect" className="!h-48 rounded-lg" />
    <Skeleton variant="text" className="w-3/4" />
    <Skeleton variant="text" className="w-1/2" />
    <div className="flex justify-between items-center pt-2">
      <Skeleton variant="text" className="w-20 !h-6" />
      <Skeleton variant="circle" className="!h-8 !w-8" />
    </div>
  </div>
);

/** Grid of skeleton cards for loading states */
export const ProductGridSkeleton: React.FC<{ count?: number }> = ({
  count = 8,
}) => (
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
    {Array.from({ length: count }).map((_, i) => (
      <ProductCardSkeleton key={i} />
    ))}
  </div>
);

/** Skeleton for the spectrum swim lane view */
export const SpectrumSkeleton: React.FC = () => (
  <div className="w-full space-y-1">
    {Array.from({ length: 5 }).map((_, i) => (
      <div
        key={i}
        className="flex h-24 border-b border-zinc-800/30 animate-pulse"
      >
        <div className="w-32 flex-shrink-0 flex items-center justify-center bg-zinc-900/30 border-r border-zinc-800/30">
          <Skeleton variant="rect" className="!h-10 !w-20" />
        </div>
        <div className="flex-1 flex items-center gap-6 px-8">
          {Array.from({ length: 3 + (i % 3) }).map((_, j) => (
            <Skeleton
              key={j}
              variant="rect"
              className="!w-[60px] !h-[60px] rounded shadow-lg"
            />
          ))}
        </div>
      </div>
    ))}
  </div>
);

/** Skeleton for the product detail page */
export const ProductPageSkeleton: React.FC = () => (
  <div className="w-full h-full bg-slate-950 rounded-lg overflow-hidden flex flex-col animate-pulse">
    {/* Header skeleton */}
    <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900">
      <div className="flex items-center gap-4">
        <Skeleton variant="circle" className="!w-10 !h-10" />
        <div className="space-y-2">
          <Skeleton variant="text" className="!w-20 !h-3" />
          <Skeleton variant="text" className="!w-48 !h-6" />
        </div>
      </div>
      <div className="flex gap-2">
        <Skeleton variant="circle" className="!w-10 !h-10" />
        <Skeleton variant="circle" className="!w-10 !h-10" />
      </div>
    </div>
    {/* Content skeleton */}
    <div className="flex-1 p-6">
      <div className="grid grid-cols-3 gap-6">
        <Skeleton variant="rect" className="!h-64 rounded-lg" />
        <div className="space-y-4">
          <Skeleton variant="rect" className="!h-24 rounded-lg" />
          <Skeleton variant="rect" className="!h-24 rounded-lg" />
          <Skeleton variant="rect" className="!h-24 rounded-lg" />
        </div>
        <div className="space-y-4">
          <Skeleton variant="rect" className="!h-32 rounded-lg" />
          <Skeleton variant="rect" className="!h-32 rounded-lg" />
        </div>
      </div>
    </div>
  </div>
);
