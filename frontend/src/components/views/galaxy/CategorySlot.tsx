import { motion } from "framer-motion";
import React, { useState } from "react";

interface CategorySlotProps {
  id: string;
  name: string;
  image: string;
  fallbackGradient?: string;
  icon?: React.ElementType;
  mainColor?: string;
  count?: number; // Optional product count
  onClick: () => void;
}

export const CategorySlot = ({
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

  const hasData = count !== undefined && count > 0;
  // If count is undefined (loading), we treat it as clickable but maybe show spinner?
  // For now let's assume if undefined, we don't disable yet.
  // NOTE: Temporarily allow showing empty categories to visualize the UI
  // const isDisabled = count === 0;
  const isDisabled = false; // Allow clicking even with 0 count for now

  return (
    <motion.div
      className={`relative aspect-square rounded-xl overflow-hidden group w-full flex flex-col transition-all duration-300 ring-1 shadow-2xl ${
        isDisabled
          ? "bg-[#0a0a0a] opacity-40 border border-zinc-900 cursor-not-allowed grayscale pointer-events-none"
          : "bg-[#030303] cursor-pointer ring-white/5 hover:ring-white/20"
      }`}
      onMouseEnter={() => !isDisabled && setIsHovered(true)}
      onMouseLeave={() => !isDisabled && setIsHovered(false)}
      onClick={() => !isDisabled && onClick()}
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
            onError={() => setImgError(true)}
            className="w-full h-full object-cover transition-transform duration-700 ease-out will-change-transform"
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

        {/* 2. Bottom Lip Highlight - The "Ledgew" catching light */}
        <div className="absolute inset-x-0 bottom-0 h-[1px] bg-white/20 z-20 mix-blend-overlay" />

        {/* 3. Top Edge Shadow - Defining the cut */}
        <div className="absolute inset-x-0 top-0 h-[4px] bg-gradient-to-b from-black to-transparent z-20 opacity-80" />

        {/* Hover Spotlight */}
        <div
          className="absolute inset-0 pointer-events-none transition-opacity duration-300"
          style={{
            background: `radial-gradient(circle at 50% 0%, ${mainColor}15, transparent 60%)`,
            opacity: isHovered ? 1 : 0,
          }}
        />
      </div>

      {/* Label Area - Integrated into the block */}
      <div className="flex-1 bg-[#080808] flex items-center justify-center border-t border-white/5 shrink-0 px-2 relative z-10 shadow-[0_-5px_15px_rgba(0,0,0,0.5)]">
        <span
          className="text-[10px] font-bold uppercase tracking-widest text-center line-clamp-1 transition-colors duration-300"
          style={{
            color: isHovered ? mainColor : "#52525b",
            textShadow: isHovered ? `0 0 10px ${mainColor}66` : "none",
          }}
        >
          {name}{" "}
          {count !== undefined && count > 0 && (
            <span className="ml-1 opacity-50">({count})</span>
          )}
        </span>
      </div>
    </motion.div>
  );
};
