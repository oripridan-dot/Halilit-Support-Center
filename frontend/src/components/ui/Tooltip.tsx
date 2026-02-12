import React, { useState } from "react";

interface TooltipProps {
  content: string;
  children: React.ReactNode;
  position?: "top" | "bottom" | "left" | "right";
}

/**
 * Tooltip — lightweight hover tooltip.
 * Shows contextual info for badges, icons, and truncated text.
 */
export const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  position = "top",
}) => {
  const [visible, setVisible] = useState(false);

  const positionClasses = {
    top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
    left: "right-full top-1/2 -translate-y-1/2 mr-2",
    right: "left-full top-1/2 -translate-y-1/2 ml-2",
  }[position];

  return (
    <div
      className="relative inline-flex"
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      onFocus={() => setVisible(true)}
      onBlur={() => setVisible(false)}
    >
      {children}
      {visible && (
        <div
          role="tooltip"
          className={`absolute z-[100] px-3 py-1.5 text-xs font-medium text-zinc-100 
                      bg-zinc-800 rounded-lg shadow-xl whitespace-nowrap pointer-events-none
                      animate-fade-in border border-zinc-700/50 ${positionClasses}`}
        >
          {content}
          {/* Arrow */}
          <div
            className={`absolute w-2 h-2 bg-zinc-800 border border-zinc-700/50 rotate-45 ${
              position === "top"
                ? "top-full left-1/2 -translate-x-1/2 -mt-1 border-t-0 border-l-0"
                : position === "bottom"
                  ? "bottom-full left-1/2 -translate-x-1/2 -mb-1 border-b-0 border-r-0"
                  : position === "left"
                    ? "left-full top-1/2 -translate-y-1/2 -ml-1 border-l-0 border-b-0"
                    : "right-full top-1/2 -translate-y-1/2 -mr-1 border-r-0 border-t-0"
            }`}
          />
        </div>
      )}
    </div>
  );
};
