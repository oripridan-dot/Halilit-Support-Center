import React from "react";

type ControlVariant = "1176" | "thumbnail" | "icon";

interface ControlProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ControlVariant;
  active?: boolean;
  label?: string; // For 1176 buttons
  icon?: React.ReactNode;
}

export const Control = ({
  variant = "1176",
  active = false,
  label,
  icon: _icon,
  children,
  className = "",
  ...props
}: ControlProps) => {
  // The "1176" Ratio Button Style
  if (variant === "1176") {
    return (
      <button
        className={`
          px-4 py-1.5 text-[10px] font-black tracking-widest uppercase border rounded transition-all duration-100 whitespace-nowrap
          ${
            active
              ? "bg-amber-500 border-amber-500 text-black shadow-[0_0_10px_rgba(245,158,11,0.5)] scale-105"
              : "bg-black border-zinc-700 text-zinc-400 hover:border-zinc-500 hover:text-zinc-200"
          }
          ${className}
        `}
        {...props}
      >
        {label || children}
      </button>
    );
  }

  // The Galaxy Thumbnail Style
  if (variant === "thumbnail") {
    return (
      <button
        className={`group relative aspect-square rounded-lg overflow-hidden border border-zinc-800 hover:border-white transition-all bg-black ${className}`}
        {...props}
      >
        {children}
      </button>
    );
  }

  return <button {...props}>{children}</button>;
};
