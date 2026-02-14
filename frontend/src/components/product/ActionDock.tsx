/**
 * ActionDock — The "Exploration Engine" UI
 *
 * A sticky footer of interactive mission buttons that invite workers
 * to dive deeper: Compare, Deep Dive, Setup Guide, Artist Spotlight, etc.
 * Each button triggers a JIT exploration action.
 *
 * Design: Floating dock at the bottom, branded accent colors,
 * glowing buttons that feel like "skills in a game."
 */

import React from "react";
import type { ExplorationPath } from "../../types";

interface ActionDockProps {
  paths: ExplorationPath[];
  onExplore: (path: ExplorationPath) => void;
  brandColor?: string;
  isExploring?: boolean;
  className?: string;
}

const ICON_MAP: Record<string, string> = {
  compare: "⚔️",
  specs: "📋",
  setup: "🛠️",
  artists: "🎧",
  warning: "⚠️",
  accessories: "🎒",
  deep_dive: "🎓",
  how_to: "🛠️",
  field_notes: "⚠️",
  artist_spotlight: "🎧",
  comparison: "⚔️",
};

export const ActionDock: React.FC<ActionDockProps> = ({
  paths,
  onExplore,
  brandColor = "#3b82f6",
  isExploring = false,
  className = "",
}) => {
  if (!paths || paths.length === 0) return null;

  return (
    <div className={`${className}`}>
      <div className="flex items-center gap-2 mb-3">
        <div
          className="w-1 h-4 rounded-full"
          style={{ backgroundColor: brandColor }}
        />
        <h3 className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider">
          Explore Deeper
        </h3>
      </div>

      <div className="flex flex-wrap gap-2">
        {paths.map((path, idx) => {
          const icon = ICON_MAP[path.icon] || ICON_MAP[path.type] || "🔍";

          return (
            <button
              key={idx}
              onClick={() => onExplore(path)}
              disabled={isExploring}
              className="group relative flex items-center gap-2.5 px-4 py-2.5 rounded-xl 
                         bg-slate-800/60 border border-slate-700/50 
                         hover:border-opacity-80 hover:bg-slate-800 
                         transition-all duration-300 
                         disabled:opacity-50 disabled:cursor-wait
                         hover:shadow-lg hover:-translate-y-0.5"
              style={{
                ["--dock-color" as string]: brandColor,
              }}
              title={path.description}
            >
              {/* Glow effect on hover */}
              <div
                className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
                style={{
                  background: `radial-gradient(ellipse at center, ${brandColor}08 0%, transparent 70%)`,
                }}
              />

              <span className="text-base relative z-10">{icon}</span>
              <span className="text-xs font-semibold text-zinc-300 group-hover:text-white transition-colors relative z-10">
                {path.label}
              </span>

              {/* Hover accent line */}
              <div
                className="absolute bottom-0 left-3 right-3 h-px opacity-0 group-hover:opacity-60 transition-opacity duration-300"
                style={{ backgroundColor: brandColor }}
              />
            </button>
          );
        })}
      </div>
    </div>
  );
};
