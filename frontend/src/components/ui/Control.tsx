import React, { useMemo } from "react";
import { BaseComponentProps } from "../../types/componentUtils";

type ControlVariant = "1176" | "thumbnail" | "icon";

interface ControlProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>, BaseComponentProps {
  variant?: ControlVariant;
  active?: boolean;
  label?: string;
  icon?: React.ReactNode;
}

/**
 * Control Component
 *
 * Flexible button component with multiple style variants:
 * - "1176": Audio ratio button style
 * - "thumbnail": Galaxy thumbnail button style
 * - "icon": Icon-only button style
 *
 * Features:
 * - Active/inactive state styling
 * - Smooth transitions
 * - Accessible button behavior
 */
export const Control = React.forwardRef<HTMLButtonElement, ControlProps>(
  (
    {
      variant = "1176",
      active = false,
      label,
      icon: _icon,
      children,
      className = "",
      ...props
    },
    ref,
  ) => {
    // Memoize variant-specific styles
    const variantStyles = useMemo(() => {
      const base =
        "transition-all duration-100 whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed";

      switch (variant) {
        case "1176":
          return `${base} px-4 py-1.5 text-[10px] font-black tracking-widest uppercase border rounded ${
            active
              ? "bg-amber-500 border-amber-500 text-black shadow-[0_0_10px_rgba(245,158,11,0.5)] scale-105"
              : "bg-black border-zinc-700 text-zinc-400 hover:border-zinc-500 hover:text-zinc-200"
          }`;

        case "thumbnail":
          return `${base} group relative aspect-square rounded-lg overflow-hidden border border-zinc-800 hover:border-white bg-black`;

        case "icon":
          return `${base} p-2 rounded hover:bg-zinc-800 text-zinc-400 hover:text-white`;

        default:
          return base;
      }
    }, [variant, active]);

    return (
      <button ref={ref} className={`${variantStyles} ${className}`} {...props}>
        {label || children}
      </button>
    );
  },
);

Control.displayName = "Control";
