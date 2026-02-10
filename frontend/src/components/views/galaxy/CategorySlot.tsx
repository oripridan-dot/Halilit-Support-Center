import { motion } from "framer-motion";
import React, { useState, useCallback, useMemo } from "react";

interface BrandLogo {
  brand: string;
  logoUrl: string;
}

interface CategorySlotProps {
  id: string;
  name: string;
  image: string;
  fallbackGradient?: string;
  icon?: React.ElementType;
  mainColor?: string;
  count?: number; // Optional product count
  brands?: BrandLogo[]; // Brand logos for this category
  onClick: () => void;
}

export const CategorySlot = React.memo(
  ({
    id,
    name,
    image,
    fallbackGradient,
    icon: Icon,
    mainColor = "#fff",
    count,
    brands = [],
    onClick,
  }: CategorySlotProps) => {
    const [isHovered, setIsHovered] = useState(false);
    const [imgError, setImgError] = useState(false);

    const isDisabled = false; // Allow clicking even with 0 count for now

    const handleMouseEnter = useCallback(() => setIsHovered(true), []);
    const handleMouseLeave = useCallback(() => setIsHovered(false), []);
    const handleImgError = useCallback(() => setImgError(true), []);

    // Pre-compute spotlight gradient (stable across renders when mainColor doesn't change)
    const spotlightBg = useMemo(
      () =>
        `radial-gradient(circle at 50% 0%, ${mainColor}15, transparent 60%)`,
      [mainColor],
    );

    return (
      <motion.div
        className={`relative aspect-square rounded-xl overflow-hidden group w-full flex flex-col transition-all duration-300 ring-1 shadow-2xl ${
          isDisabled
            ? "bg-[#0a0a0a] opacity-40 border border-zinc-900 cursor-not-allowed grayscale pointer-events-none"
            : "bg-[#030303] cursor-pointer ring-white/5 hover:ring-white/20"
        }`}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={onClick}
        style={{
          transform: isHovered ? "translateY(1px)" : "translateY(0)",
        }}
        transition={{ duration: 0.1 }}
      >
        {/* Container for the "Cave" effect */}
        <div className="flex-[3] relative w-full h-full overflow-hidden bg-[#050505]">
          {/* The "Floor/Background" Image */}
          {!imgError && !isDisabled ? (
            <img
              src={image}
              alt={name}
              loading="lazy"
              onError={handleImgError}
              className="w-full h-full object-cover transition-[transform,filter] duration-700 ease-out will-change-transform"
              style={{
                filter: isHovered
                  ? "contrast(110%) brightness(1.1)"
                  : "contrast(100%) brightness(0.8)",
                transform: isHovered ? "scale(1.1)" : "scale(1.0)",
              }}
            />
          ) : isDisabled ? (
            <div className="w-full h-full flex flex-col items-center justify-center bg-zinc-950 text-zinc-800">
              <div className="text-2xl opacity-20 selection:bg-none select-none">
                ∅
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center w-full h-full">
              {Icon &&
                React.createElement(Icon, {
                  className: "w-8 h-8",
                  color: mainColor,
                })}
            </div>
          )}

          {/* -------------------------------------------------------- */}
          {/* DEPTH OVERLAYS: Creating the "Carved In" Illusion        */}
          {/* -------------------------------------------------------- */}

          {/* 1. Deep Inner Shadow (Top/Sides) - The "Overhang" */}
          <div className="absolute inset-0 pointer-events-none shadow-[inset_0_10px_30px_rgba(0,0,0,0.9),inset_0_0_15px_rgba(0,0,0,0.8)] z-10" />

          {/* 2. Bottom Lip Highlight - The "Ledge" catching light */}
          <div className="absolute inset-x-0 bottom-0 h-[1px] bg-white/20 z-20 mix-blend-overlay" />

          {/* 3. Top Edge Shadow - Defining the cut */}
          <div className="absolute inset-x-0 top-0 h-[4px] bg-gradient-to-b from-black to-transparent z-20 opacity-80" />

          {/* Hover Spotlight */}
          <div
            className="absolute inset-0 pointer-events-none transition-opacity duration-300"
            style={{
              background: spotlightBg,
              opacity: isHovered ? 1 : 0,
            }}
          />
        </div>

        {/* Label Area - Title + Brand Logos */}
        <div className="flex-1 bg-gradient-to-t from-[#0a0a0a] to-[#101010] flex flex-col items-center justify-center border-t border-white/10 shrink-0 px-3 py-2 relative z-10 shadow-[0_-5px_15px_rgba(0,0,0,0.5)] gap-2">
          {/* Title Section - With improved readability */}
          <div className="flex flex-col items-center gap-1 w-full">
            <span
              className="text-[11px] font-bold uppercase tracking-[0.08em] text-center line-clamp-2 transition-all duration-300 leading-tight"
              style={{
                color: isHovered ? mainColor : "#e4e4e7",
                textShadow: isHovered
                  ? `0 0 12px ${mainColor}80, 0 2px 4px rgba(0,0,0,0.8)`
                  : "0 1px 2px rgba(0,0,0,0.5)",
                letterSpacing: isHovered ? "0.1em" : "0.08em",
              }}
            >
              {name}
            </span>

            {/* Product Count Badge */}
            {count !== undefined && count > 0 && (
              <span
                className="text-[9px] font-semibold px-2 py-0.5 rounded-full transition-all duration-300"
                style={{
                  backgroundColor: isHovered
                    ? `${mainColor}20`
                    : "rgba(255,255,255,0.05)",
                  color: isHovered ? mainColor : "#a1a1a1",
                  border: isHovered
                    ? `1px solid ${mainColor}50`
                    : "1px solid rgba(255,255,255,0.1)",
                }}
              >
                {count} {count === 1 ? "item" : "items"}
              </span>
            )}
          </div>

          {/* Brand Logos - Bottom panel */}
          {brands.length > 0 && (
            <div className="w-full flex flex-wrap items-center justify-center gap-1.5 pt-1 border-t border-white/5">
              {brands.slice(0, 4).map((brandLogo, idx) => (
                <div
                  key={`${brandLogo.brand}-${idx}`}
                  className="flex-shrink-0 h-5 flex items-center justify-center bg-white/5 rounded px-1 py-0.5 hover:bg-white/10 transition-colors duration-200 group"
                  title={brandLogo.brand}
                >
                  <img
                    src={brandLogo.logoUrl}
                    alt={brandLogo.brand}
                    loading="lazy"
                    className="h-full object-contain max-w-[30px] opacity-70 group-hover:opacity-90 transition-opacity duration-200"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = "none";
                    }}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      </motion.div>
    );
  },
);

CategorySlot.displayName = "CategorySlot";
