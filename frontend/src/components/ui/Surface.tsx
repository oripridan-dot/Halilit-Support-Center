import React from "react";

type SurfaceVariant = "bucket" | "screen" | "panel";

interface SurfaceProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: SurfaceVariant;
  active?: boolean;
}

export const Surface = ({
  children,
  variant = "panel",
  active = false,
  className = "",
  ...props
}: SurfaceProps) => {
  const baseStyles = "transition-all duration-300";

  const variants = {
    // The Galaxy View Containers
    bucket:
      "bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden hover:border-zinc-700",

    // The 'Green Screen' Data Readouts
    screen: `bg-black border rounded relative overflow-hidden font-mono ${
      active
        ? "border-amber-500/50 shadow-[0_0_15px_rgba(245,158,11,0.1)]"
        : "border-zinc-800"
    }`,

    // Standard UI Panels
    panel: "bg-[#0e0e10] border-t border-zinc-800",
  };

  return (
    <div
      className={`${baseStyles} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
