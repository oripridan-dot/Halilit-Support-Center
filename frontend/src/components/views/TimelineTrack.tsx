import React, { useMemo, useCallback } from "react";

// Generate a consistent HSL color from a string
const getBrandColor = (str: string) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const h = Math.abs(hash) % 360;
  return `hsl(${h}, 70%, 60%)`;
};

export const TimelineTrack = ({
  brand,
  products,
  zoom,
  onHover,
  activeId,
  priceRange,
  isPriceAxis = false,
}: {
  brand: string;
  products: any[];
  zoom: number;
  onHover: (p: any) => void;
  activeId?: string;
  priceRange?: [number, number];
  isPriceAxis?: boolean;
}) => {
  const brandColor = useMemo(() => getBrandColor(brand), [brand]);

  // Memoized hover handler
  const handleProductHover = useCallback(
    (product: any) => {
      onHover(product);
    },
    [onHover],
  );

  // Calculate position and width based on price
  const getPositionAndWidth = (product: any) => {
    // Simple proportional width based on zoom
    const baseWidth = 100 * zoom;
    return { width: Math.max(baseWidth, 60) };
  };

  return (
    <div className="flex w-full bg-[#1a1a1a] border-b border-[#2a2a2a] h-32 group hover:bg-[#222] transition-colors relative">
      {/* Ambient Brand Glow */}
      <div
        className="absolute inset-0 pointer-events-none opacity-0 group-hover:opacity-5 transition-opacity duration-500"
        style={{ backgroundColor: brandColor }}
      />

      {/* Track Header (Left Control Panel) */}
      <div className="w-48 flex-shrink-0 bg-[#111] border-r border-[#2a2a2a] flex flex-col justify-center px-4 relative z-10 shadow-lg">
        {/* Brand Accent Bar */}
        <div
          className="absolute left-0 top-0 bottom-0 w-1"
          style={{ backgroundColor: brandColor }}
        />

        <h3 className="text-zinc-100 font-bold text-sm truncate" title={brand}>
          {brand}
        </h3>
        <p className="text-[10px] text-zinc-500 mt-0.5 font-mono">
          {products.length} products
        </p>

        {/* Track Controls */}
        <div className="flex gap-2 mt-2">
          <div className="w-2 h-2 rounded-full bg-green-500/50" />
          <div className="w-2 h-2 rounded-full bg-yellow-500/50" />
          <div className="w-2 h-2 rounded-full bg-blue-500/50" />
        </div>
      </div>

      {/* Track Content (Price Axis Timeline) */}
      <div className="flex-1 overflow-x-auto overflow-y-hidden flex items-center p-1 bg-[#161616] relative custom-scrollbar">
        {/* Grid Background */}
        {isPriceAxis && priceRange && (
          <div
            className="absolute inset-0 pointer-events-none opacity-5 w-full h-full"
            style={{
              backgroundImage:
                "linear-gradient(90deg, #555 1px, transparent 1px)",
              backgroundSize: `${150 * zoom}px 100%`,
            }}
          ></div>
        )}

        {/* Clips Container - Flex layout for visible products */}
        <div className="h-full inline-flex items-center gap-1 p-1 min-w-full">
          {products.map((product, index) => {
            const { width } = getPositionAndWidth(product);
            const isActive = activeId === product.id;
            // Create unique key combining brand, id, and index to avoid key warnings
            const uniqueKey = `${brand}-${product.id}-${index}`;

            return (
              <div
                key={uniqueKey}
                style={{
                  width: `${Math.max(width, 70)}px`,
                  borderColor: isActive ? brandColor : "#333",
                }}
                className={`h-[80%] flex-shrink-0 relative rounded flex flex-col items-center justify-center overflow-hidden cursor-pointer transition-all duration-200 border
                        ${
                          isActive
                            ? "ring-1 z-10 scale-y-110 shadow-2xl bg-[#2a2a2a]"
                            : "bg-[#222] hover:border-zinc-500 hover:brightness-110 hover:z-5"
                        }
                    `}
                onMouseEnter={() => handleProductHover(product)}
                title={product.label || product.name}
              >
                {/* Active Glow */}
                {isActive && (
                  <div
                    className="absolute inset-0 pointer-events-none opacity-20"
                    style={{ backgroundColor: brandColor }}
                  />
                )}

                {/* Thumbnail Image */}
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.label}
                    className="h-[90%] w-[90%] object-contain opacity-85 hover:opacity-100 transition-opacity"
                    loading="lazy"
                    onError={(e) => {
                      e.currentTarget.style.display = "none";
                    }}
                  />
                ) : product.image_hero?.url ? (
                  <img
                    src={product.image_hero.url}
                    alt={product.label}
                    className="h-[90%] w-[90%] object-contain opacity-85 hover:opacity-100 transition-opacity"
                    loading="lazy"
                    onError={(e) => {
                      e.currentTarget.style.display = "none";
                    }}
                  />
                ) : (
                  <div className="text-[7px] text-zinc-700 font-mono text-center p-1 break-words">
                    NO IMG
                  </div>
                )}

                {/* Clip Label Overlay */}
                <div className="absolute bottom-0 inset-x-0 bg-black/80 backdrop-blur-sm p-0.5">
                  <p className="text-[7px] text-zinc-200 truncate font-mono leading-tight">
                    {product.label || product.name}
                  </p>
                  {product.price && (
                    <p className="text-[6px] text-green-400 font-mono leading-tight">
                      ${product.price.toFixed(0)}
                    </p>
                  )}
                </div>

                {/* Tier Badge */}
                {product.tier === "diamond" && (
                  <div className="absolute top-1 right-1 w-2 h-2 bg-cyan-400 rounded-full shadow-lg ring-1 ring-black border border-white/20" />
                )}
                {product.tier === "gold" && (
                  <div className="absolute top-1 right-1 w-2 h-2 bg-amber-400 rounded-full shadow-lg ring-1 ring-black" />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
