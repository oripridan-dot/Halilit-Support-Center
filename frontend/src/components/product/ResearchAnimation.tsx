/**
 * ResearchAnimation — Phase-Aware Loading UX for JIT Intelligence
 *
 * Shows a brand-themed "researching…" state that follows the
 * SSE promise phase. Each step animates based on real progress.
 * Builds anticipation: the user watches work happen in real-time.
 */

import React from "react";

interface ResearchAnimationProps {
  brandName?: string;
  brandColor?: string;
  step?: string;
  message?: string;
  progress?: number;
  className?: string;
}

const STEP_ICONS: Record<string, string> = {
  cache_hit: "⚡",
  halilit: "📦",
  brand: "🏭",
  reviews: "⭐",
  synthesis: "🔍",
  rendering: "🧠",
};

export const ResearchAnimation: React.FC<ResearchAnimationProps> = ({
  brandName,
  brandColor,
  step = "",
  message = "Researching…",
  progress = 0,
  className = "",
}) => {
  const icon = STEP_ICONS[step] || "🔍";
  const accentColor = brandColor || "#3b82f6";

  return (
    <div
      className={`flex flex-col items-center justify-center gap-5 p-6 ${className}`}
    >
      {/* Pulsing ring with brand color */}
      <div className="relative">
        <div
          className="w-16 h-16 rounded-full animate-ping absolute inset-0 opacity-20"
          style={{ backgroundColor: accentColor }}
        />
        <div
          className="w-16 h-16 rounded-full flex items-center justify-center relative z-10 border"
          style={{
            background: `${accentColor}15`,
            borderColor: `${accentColor}40`,
          }}
        >
          <span
            className="text-2xl animate-bounce"
            role="img"
            aria-label={message}
          >
            {icon}
          </span>
        </div>
      </div>

      {/* Status text */}
      <div className="text-center space-y-1.5">
        <p className="text-sm text-white font-medium animate-pulse">
          Researching{brandName ? ` ${brandName}` : ""}…
        </p>
        <p className="text-xs text-zinc-400 transition-all duration-500 min-h-[16px]">
          {message}
        </p>
      </div>

      {/* Progress bar */}
      <div className="w-48 h-1 bg-zinc-800 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{
            width: `${Math.min(progress, 100)}%`,
            backgroundColor: accentColor,
          }}
        />
      </div>
    </div>
  );
};
