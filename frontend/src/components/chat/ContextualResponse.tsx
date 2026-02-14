import React, { useMemo } from "react";
import { getContextBackground } from "../../lib/slotBackgrounds";
import { getBrandTheme } from "../../styles/brandThemes";

interface ContextualResponseProps {
  /** Category ID or hint (e.g. "electric-guitars", "drums", "studio") */
  categoryId: string;
  /** Brand name for color tinting */
  brandName?: string;
  /** Content to wrap */
  children: React.ReactNode;
  /** Optional className */
  className?: string;
}

/**
 * ContextualResponse — Wraps content with a category-appropriate
 * background image and brand-colored glassmorphism tinting.
 *
 * Creates a "Mini World" effect:
 *   1. Background image from slotBackgrounds (category-appropriate)
 *   2. Dark overlay for readability
 *   3. Brand-colored radial gradient tint
 *   4. Glassmorphism blur + shine line
 */
export const ContextualResponse = ({
  categoryId,
  brandName,
  children,
  className = "",
}: ContextualResponseProps) => {
  const bg = useMemo(() => getContextBackground(categoryId), [categoryId]);
  const brandTheme = useMemo(
    () => (brandName ? getBrandTheme(brandName) : null),
    [brandName],
  );
  const brandColor = brandTheme?.primary || "#4A90E2";

  return (
    <div
      className={`relative rounded-xl overflow-hidden ${className}`}
      style={{ minHeight: 120 }}
    >
      {/* Layer 1: Background Image */}
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage: `url(${bg.imageUrl})`,
        }}
      />

      {/* Layer 2: Fallback gradient (in case image fails) */}
      <div
        className="absolute inset-0"
        style={{ background: bg.fallbackGradient, opacity: 0.5 }}
      />

      {/* Layer 3: Dark overlay for readability */}
      <div className="absolute inset-0 bg-black/70" />

      {/* Layer 4: Brand radial gradient tint */}
      <div
        className="absolute inset-0"
        style={{
          background: `radial-gradient(ellipse at top left, ${brandColor}15, transparent 60%)`,
        }}
      />

      {/* Layer 5: Category overlay color */}
      <div
        className="absolute inset-0"
        style={{ backgroundColor: bg.overlayColor }}
      />

      {/* Layer 6: Glassmorphism border */}
      <div className="absolute inset-0 border border-white/5 rounded-xl pointer-events-none" />

      {/* Bottom brand shine line */}
      <div
        className="absolute bottom-0 inset-x-0 h-[1px] z-10"
        style={{
          background: `linear-gradient(90deg, transparent 20%, ${brandColor}40, transparent 80%)`,
        }}
      />

      {/* Content */}
      <div className="relative z-10 backdrop-blur-sm">{children}</div>
    </div>
  );
};

export default ContextualResponse;
