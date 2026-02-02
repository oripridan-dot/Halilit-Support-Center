import React, { useMemo } from "react";
import { BaseComponentProps } from "../../types/componentUtils";

type SurfaceVariant = "bucket" | "screen" | "panel";

interface SurfaceProps
  extends React.HTMLAttributes<HTMLDivElement>, BaseComponentProps {
  variant?: SurfaceVariant;
  active?: boolean;
}

/**
 * Surface Component
 *
 * Generic container component with multiple visual variants:
 * - "bucket": Galaxy view containers
 * - "screen": Terminal/data readout style
 * - "panel": Standard UI panel
 *
 * Features:
 * - Active/inactive state styling
 * - Smooth transitions
 * - Flexible layout composition
 */
export const Surface = React.forwardRef<HTMLDivElement, SurfaceProps>(
  (
    { children, variant = "panel", active = false, className = "", ...props },
    ref,
  ) => {
    // Memoize variant styles
    const variantStyles = useMemo(() => {
      const variants: Record<SurfaceVariant, string> = {
        // Galaxy View Containers
        bucket:
          "bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden hover:border-zinc-700",

        // Terminal/Data Readout Style
        screen: `bg-black border rounded relative overflow-hidden font-mono ${
          active
            ? "border-amber-500/50 shadow-[0_0_15px_rgba(245,158,11,0.1)]"
            : "border-zinc-800"
        }`,

        // Standard UI Panel
        panel: "bg-[#0e0e10] border-t border-zinc-800",
      };

      return variants[variant];
    }, [variant, active]);

    return (
      <div
        ref={ref}
        className={`transition-all duration-300 ${variantStyles} ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  },
);

Surface.displayName = "Surface";
