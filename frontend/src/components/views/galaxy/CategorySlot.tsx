import { motion } from "framer-motion";
import React, { useState } from "react";

interface CategorySlotProps {
  id: string;
  name: string;
  image: string;
  fallbackGradient?: string;
  icon?: React.ElementType;
  mainColor?: string;
  onClick: () => void;
}

export const CategorySlot = ({
  id,
  name,
  image,
  fallbackGradient,
  icon: Icon,
  mainColor = "#fff",
  onClick,
}: CategorySlotProps) => {
  const [isHovered, setIsHovered] = useState(false);
  const [imgError, setImgError] = useState(false);

  return (
    <motion.div
      className="relative aspect-square rounded-xl bg-[#030303] overflow-hidden group cursor-pointer w-full flex flex-col transition-all duration-300 ring-1 ring-white/5 shadow-2xl"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
      style={{
        transform: isHovered ? "translateY(1px)" : "translateY(0)",
      }}
      transition={{ duration: 0.1 }}
    >
      {/* Container for the "Cave" effect */}
      <div className="flex-[3] relative w-full h-full overflow-hidden bg-[#050505]">
        {/* The "Floor/Background" Image */}
        {!imgError ? (
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
          {name}
        </span>
      </div>
    </motion.div>
  );
};
