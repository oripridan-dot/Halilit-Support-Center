/**
 * ZoomControl — Semantic zoom slider for the Spectrum V2 view.
 *
 * Shows current zoom level and allows stepping through:
 * Galaxy → Constellation → Cluster → Star
 *
 * Supports mouse wheel and keyboard shortcuts.
 */
import React, { useCallback, useEffect } from "react";
import { useSpectrumV2Store } from "../../store/spectrumV2Store";
import { ZOOM_ORDER, ZOOM_META } from "../../types/spectrum";
import type { ZoomLevel } from "../../types/spectrum";

export const ZoomControl: React.FC = () => {
  const { zoom, setZoom, zoomIn, zoomOut } = useSpectrumV2Store();
  const currentIdx = ZOOM_ORDER.indexOf(zoom);

  // Keyboard shortcuts: + / - or [ / ]
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      )
        return;
      if (e.key === "+" || e.key === "=" || e.key === "]") {
        e.preventDefault();
        zoomIn();
      } else if (e.key === "-" || e.key === "[") {
        e.preventDefault();
        zoomOut();
      }
    },
    [zoomIn, zoomOut],
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div
      className="flex items-center gap-2 bg-zinc-900/80 backdrop-blur-sm
                    rounded-full px-3 py-1.5 border border-zinc-800/50"
    >
      {/* Zoom Out */}
      <button
        onClick={zoomOut}
        disabled={currentIdx <= 0}
        className="text-zinc-400 hover:text-white disabled:text-zinc-700
                   disabled:cursor-not-allowed transition-colors p-0.5"
        title="Zoom out ([ or -)"
      >
        <svg
          className="w-3.5 h-3.5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M20 12H4" />
        </svg>
      </button>

      {/* Zoom Level Indicators */}
      <div className="flex items-center gap-0.5">
        {ZOOM_ORDER.map((level, idx) => {
          const meta = ZOOM_META[level];
          return (
            <button
              key={level}
              onClick={() => setZoom(level)}
              className={`
                relative group flex items-center justify-center
                w-7 h-7 rounded-full transition-all duration-200
                ${
                  idx === currentIdx
                    ? "bg-amber-500/20 ring-1 ring-amber-500/60 text-amber-400 scale-110"
                    : idx < currentIdx
                      ? "bg-zinc-800/60 text-zinc-400 hover:bg-zinc-800"
                      : "text-zinc-600 hover:text-zinc-400"
                }
              `}
              title={`${meta.label}: ${meta.description}`}
            >
              <span className="text-xs">{meta.icon}</span>

              {/* Tooltip */}
              <span
                className="absolute -bottom-8 left-1/2 -translate-x-1/2
                               bg-black text-white text-[9px] px-2 py-1 rounded
                               whitespace-nowrap opacity-0 group-hover:opacity-100
                               transition-opacity pointer-events-none border border-zinc-800
                               z-50"
              >
                {meta.label}
              </span>
            </button>
          );
        })}
      </div>

      {/* Zoom In */}
      <button
        onClick={zoomIn}
        disabled={currentIdx >= ZOOM_ORDER.length - 1}
        className="text-zinc-400 hover:text-white disabled:text-zinc-700
                   disabled:cursor-not-allowed transition-colors p-0.5"
        title="Zoom in (] or +)"
      >
        <svg
          className="w-3.5 h-3.5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 4v16m8-8H4"
          />
        </svg>
      </button>

      {/* Current Level Label */}
      <div className="h-4 w-px bg-zinc-800 mx-0.5" />
      <span className="text-amber-400/80 text-[9px] font-bold uppercase tracking-[0.15em]">
        {ZOOM_META[zoom]?.label}
      </span>
    </div>
  );
};
