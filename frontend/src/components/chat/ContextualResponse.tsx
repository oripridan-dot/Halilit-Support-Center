/**
 * ContextualResponse — "Mini World" wrapper for product intelligence cards
 *
 * Renders a glassmorphism card with:
 *  1. A contextual background image (from slotBackgrounds — the "World" layer)
 *  2. A brand-color tint overlay (the "Identity" layer)
 *  3. Blurred glass content surface (the "Glass" layer)
 *  4. Source provenance label + brand indicator dot
 *
 * This component transforms chat responses / intelligence panels into immersive,
 * category-aware visual environments — the user "feels" the setting before reading.
 *
 * Performance: CSS-only animations, no JS paint, GPU-composited transforms.
 */

import React, { memo, useMemo } from "react";
import {
  getContextBackground,
  type BackgroundConfig,
} from "../../lib/slotBackgrounds";
import { getBrandTheme, type BrandVisualTheme } from "../../lib/brandThemes";

interface ContextualResponseProps {
  /** Category ID for background selection (e.g. "electric-guitars", "drums") */
  categoryId: string;
  /** Brand name for color theming (e.g. "Fender", "Nord") */
  brandName: string;
  /** Optional className for outer wrapper */
  className?: string;
  /** Content to render inside the card */
  children: React.ReactNode;
}

export const ContextualResponse = memo(
  ({
    categoryId,
    brandName,
    className = "",
    children,
  }: ContextualResponseProps) => {
    const bgConfig: BackgroundConfig = useMemo(
      () => getContextBackground(categoryId),
      [categoryId],
    );
    const brandTheme: BrandVisualTheme = useMemo(
      () => getBrandTheme(brandName),
      [brandName],
    );

    return (
      <div
        className={`relative w-full overflow-hidden rounded-2xl border border-white/10 shadow-2xl group transition-all duration-500 hover:shadow-[0_0_40px_-10px_rgba(255,255,255,0.05)] ${className}`}
      >
        {/* ─── Layer 1: The "World" Background Image ─── */}
        <div
          className="absolute inset-0 bg-cover bg-center transition-transform duration-[10s] ease-linear group-hover:scale-105"
          style={{ backgroundImage: `url(${bgConfig.imageUrl})` }}
        />

        {/* ─── Layer 2: Category Tint (optional per-category color) ─── */}
        {bgConfig.overlayColor && (
          <div
            className="absolute inset-0 mix-blend-multiply opacity-60"
            style={{ backgroundColor: bgConfig.overlayColor }}
          />
        )}

        {/* ─── Layer 3: Darkness + Readability ─── */}
        <div className="absolute inset-0 bg-gray-900/70" />

        {/* ─── Layer 4: Brand Radial Glow ─── */}
        <div
          className="absolute inset-0 opacity-20 mix-blend-overlay"
          style={{
            background: `radial-gradient(circle at top right, ${brandTheme.primary}, transparent 70%)`,
          }}
        />

        {/* ─── Layer 5: Glass Content Surface ─── */}
        <div className="relative z-10 backdrop-blur-sm bg-black/30 p-6 text-white">
          {/* Header: Context Label + Brand DNA */}
          <div className="flex items-center justify-between mb-4 border-b border-white/10 pb-2">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold uppercase tracking-widest text-white/60">
                {bgConfig.label}
              </span>
              {/* Brand Identity Dot */}
              <span
                className="h-2 w-2 rounded-full"
                style={{
                  backgroundColor: brandTheme.primary,
                  boxShadow: `0 0 10px ${brandTheme.primary}80`,
                }}
              />
            </div>
            <div className="text-[9px] text-white/30 font-mono uppercase tracking-wider">
              {brandName}
            </div>
          </div>

          {/* The Actual Response Content */}
          <div className="prose prose-invert max-w-none prose-p:leading-relaxed prose-li:marker:text-white/50 prose-headings:text-white prose-a:text-blue-400">
            {children}
          </div>
        </div>

        {/* ─── Layer 6: Bottom Shine Line ─── */}
        <div
          className="absolute bottom-0 left-0 h-[2px] w-full opacity-40"
          style={{
            background: `linear-gradient(90deg, transparent, ${brandTheme.primary}, transparent)`,
          }}
        />
      </div>
    );
  },
);
ContextualResponse.displayName = "ContextualResponse";
