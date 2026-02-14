import { motion } from "framer-motion";
import React, { useState, useCallback, useMemo } from "react";

interface CategorySlotProps {
  id: string;
  name: string;
  image: string;
  fallbackGradient?: string;
  icon?: React.ElementType;
  mainColor?: string;
  count?: number;
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
    onClick,
  }: CategorySlotProps) => {
    const [isHovered, setIsHovered] = useState(false);
    const [imgError, setImgError] = useState(false);

    const handleMouseEnter = useCallback(() => setIsHovered(true), []);
    const handleMouseLeave = useCallback(() => setIsHovered(false), []);
    const handleImgError = useCallback(() => setImgError(true), []);

    const spotlightBg = useMemo(
      () =>
        `radial-gradient(circle at 50% 0%, ${mainColor}20, transparent 60%)`,
      [mainColor],
    );

    return (
      <motion.div
        className="relative aspect-square rounded-xl overflow-hidden group w-full flex flex-col transition-all duration-300 ring-1 shadow-2xl bg-[#030303] cursor-pointer ring-white/5 hover:ring-white/20"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={onClick}
        style={{
          transform: isHovered ? "translateY(1px)" : "translateY(0)",
        }}
        transition={{ duration: 0.1 }}
      >
        {/* Background Image Container */}
        <div className="flex-[3] relative w-full h-full overflow-hidden bg-[#050505]">
          {!imgError ? (
            <img
              src={image}
              alt={name}
              loading="lazy"
              onError={handleImgError}
              className="w-full h-full object-cover transition-[transform,filter] duration-700 ease-out will-change-transform"
              style={{
                filter: isHovered
                  ? "contrast(110%) brightness(1.15) saturate(1.1)"
                  : "contrast(105%) brightness(1.0) saturate(1.05)",
                transform: isHovered ? "scale(1.08)" : "scale(1.0)",
              }}
            />
          ) : (
            <div
              className="flex items-center justify-center w-full h-full"
              style={{ background: fallbackGradient || `linear-gradient(135deg, ${mainColor}20, #111)` }}
            >
              {Icon &&
                React.createElement(Icon, {
                  className: "w-8 h-8 opacity-40",
                  color: mainColor,
                })}
            </div>
          )}

          {/* Inner shadow for depth */}
          <div className="absolute inset-0 pointer-events-none shadow-[inset_0_10px_30px_rgba(0,0,0,0.7),inset_0_0_15px_rgba(0,0,0,0.6)] z-10" />

          {/* Bottom edge highlight */}
          <div className="absolute inset-x-0 bottom-0 h-[1px] bg-white/15 z-20 mix-blend-overlay" />

          {/* Top cut shadow */}
          <div className="absolute inset-x-0 top-0 h-[4px] bg-gradient-to-b from-black to-transparent z-20 opacity-70" />

          {/* Hover spotlight glow */}
          <div
            className="absolute inset-0 pointer-events-none transition-opacity duration-300"
            style={{
              background: spotlightBg,
              opacity: isHovered ? 1 : 0,
            }}
          />

          {/* Bottom brand-color shine line on hover */}
          <div
            className="absolute inset-x-0 bottom-0 h-[2px] z-30 transition-opacity duration-300"
            style={{
              background: `linear-gradient(90deg, transparent, ${mainColor}80, transparent)`,
              opacity: isHovered ? 1 : 0,
            }}
          />
        </div>

        {/* Label Area — crisp text, no logos */}
        <div className="flex-1 bg-zinc-950 flex flex-col items-center justify-center border-t border-zinc-800/50 shrink-0 px-2 py-1.5 relative z-10 gap-0.5">
          <span
            className="text-[10px] font-bold uppercase tracking-[0.12em] text-center line-clamp-2 transition-colors duration-200 leading-tight"
            style={{
              color: isHovered ? mainColor : "#e4e4e7",
              textShadow: isHovered
                ? `0 0 12px ${mainColor}40`
                : "0 1px 3px rgba(0,0,0,0.8)",
            }}
          >
            {name}
          </span>

          {count !== undefined && count > 0 && (
            <span
              className="text-[8px] font-semibold px-1.5 py-px rounded-full transition-colors duration-200 tabular-nums"
              style={{
                backgroundColor: isHovered
                  ? `${mainColor}15`
                  : "rgba(255,255,255,0.04)",
                color: isHovered ? mainColor : "#71717a",
              }}
            >
              {count}
            </span>
          )}
        </div>
      </motion.div>
    );
  },
);

CategorySlot.displayName = "CategorySlot";
