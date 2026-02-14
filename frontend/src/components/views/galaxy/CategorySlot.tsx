import React, { useState, useCallback } from "react";

/**
 * CategorySlot — Galaxy Dashboard tile (v2)
 *
 * Image on top, label BENEATH the image (not overlaid).
 * Clean, readable layout with hover effects.
 */

interface CategorySlotProps {
  id: string;
  name: string;
  image: string;
  fallbackGradient?: string;
  icon?: React.ElementType;
  mainColor?: string;
  count?: number;
  brands?: unknown[];
  onClick: () => void;
}

export const CategorySlot = React.memo(
  ({
    name,
    image,
    fallbackGradient,
    icon: Icon,
    mainColor = "#fff",
    count,
    onClick,
  }: CategorySlotProps) => {
    const [isHovered, setIsHovered] = useState(false);
    const [imgError, setImgError] = useState(false);

    const handleMouseEnter = useCallback(() => setIsHovered(true), []);
    const handleMouseLeave = useCallback(() => setIsHovered(false), []);
    const handleImgError = useCallback(() => setImgError(true), []);

    return (
      <div
        className="flex flex-col cursor-pointer group"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={onClick}
        style={{
          transform: isHovered ? "translateY(-3px)" : "translateY(0)",
          transition: "transform 0.25s cubic-bezier(.22,1,.36,1)",
        }}
      >
        {/* ── IMAGE AREA ── */}
        <div className="relative aspect-square rounded-xl overflow-hidden bg-[#0a0a0a] ring-1 ring-white/10 group-hover:ring-white/25 shadow-xl transition-shadow duration-300 group-hover:shadow-[0_0_24px_-5px_rgba(255,255,255,0.06)]">
          {/* Background image */}
          <div className="absolute inset-0">
            {!imgError ? (
              <img
                src={image}
                alt=""
                loading="lazy"
                decoding="async"
                onError={handleImgError}
                className="w-full h-full object-cover will-change-transform"
                style={{
                  filter: isHovered
                    ? "contrast(115%) brightness(1.15) saturate(1.1)"
                    : "contrast(105%) brightness(0.8) saturate(0.9)",
                  transform: isHovered ? "scale(1.08)" : "scale(1.0)",
                  transition: "transform 0.6s ease-out, filter 0.6s ease-out",
                }}
              />
            ) : fallbackGradient ? (
              <div
                className="w-full h-full"
                style={{ background: fallbackGradient }}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-zinc-950">
                {Icon ? (
                  <Icon className="w-10 h-10 opacity-15" color={mainColor} />
                ) : (
                  <div className="text-xl opacity-15 text-zinc-700 select-none">
                    ∅
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Subtle vignette for depth */}
          <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-black/5 via-transparent to-black/40" />

          {/* Top edge shine */}
          <div className="absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/15 to-transparent opacity-50" />

          {/* Hover glow */}
          <div
            className="absolute inset-0 pointer-events-none transition-opacity duration-500"
            style={{
              background: `radial-gradient(circle at 50% 50%, ${mainColor}15, transparent 70%)`,
              opacity: isHovered ? 1 : 0,
            }}
          />

          {/* Product count badge */}
          {count !== undefined && count > 0 && (
            <div
              className="absolute top-1.5 right-1.5 z-10 text-[8px] font-bold px-1.5 py-0.5 rounded-md backdrop-blur-sm"
              style={{
                backgroundColor: "rgba(0,0,0,0.55)",
                color: isHovered ? mainColor : "rgba(255,255,255,0.5)",
                transition: "color 0.3s ease",
              }}
            >
              {count}
            </div>
          )}
        </div>

        {/* ── TEXT BENEATH IMAGE ── */}
        <div className="mt-1.5 px-0.5 text-center">
          <span
            className="text-[10px] font-bold uppercase tracking-[0.12em] leading-tight block"
            style={{
              color: isHovered ? "#ffffff" : "#a1a1aa",
              textShadow: isHovered ? `0 0 12px ${mainColor}60` : "none",
              transition: "color 0.3s ease, text-shadow 0.3s ease",
            }}
          >
            {name}
          </span>
        </div>
      </div>
    );
  },
);

CategorySlot.displayName = "CategorySlot";
