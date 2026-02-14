import { motion } from "framer-motion";
import {
  GitCompare,
  ExternalLink,
  BookOpen,
  Puzzle,
  ChevronRight,
} from "lucide-react";

export interface ExplorationPath {
  type: "comparison" | "deep_dive" | "how_to" | "compatibility";
  target?: string;
  label: string;
}

interface ExplorationDockProps {
  paths: ExplorationPath[];
  halilitUrl?: string;
  officialUrl?: string;
  brandName?: string;
  brandColor?: string;
  onExplore?: (path: ExplorationPath) => void;
  onBackToSpectrum?: () => void;
}

const PATH_ICONS = {
  comparison: GitCompare,
  deep_dive: BookOpen,
  how_to: BookOpen,
  compatibility: Puzzle,
};

const PATH_COLORS = {
  comparison: "text-blue-400 bg-blue-500/10 border-blue-500/20 hover:bg-blue-500/20",
  deep_dive: "text-violet-400 bg-violet-500/10 border-violet-500/20 hover:bg-violet-500/20",
  how_to: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20 hover:bg-emerald-500/20",
  compatibility: "text-amber-400 bg-amber-500/10 border-amber-500/20 hover:bg-amber-500/20",
};

/**
 * ExplorationDock — Sticky footer with action buttons and exploration paths.
 */
export const ExplorationDock = ({
  paths,
  halilitUrl,
  officialUrl,
  brandName,
  brandColor = "#3b82f6",
  onExplore,
  onBackToSpectrum,
}: ExplorationDockProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="px-6 py-4 border-t border-zinc-800/60 bg-zinc-950/90 backdrop-blur-md"
    >
      <div className="flex items-center gap-3">
        {/* Exploration paths */}
        {paths.length > 0 && (
          <div className="flex items-center gap-2 flex-1 overflow-x-auto">
            {paths.map((path, i) => {
              const Icon = PATH_ICONS[path.type] || BookOpen;
              const colorClass = PATH_COLORS[path.type] || PATH_COLORS.deep_dive;
              return (
                <button
                  key={i}
                  onClick={() => onExplore?.(path)}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold border transition-all shrink-0 ${colorClass}`}
                >
                  <Icon size={12} />
                  {path.label}
                  <ChevronRight size={10} className="opacity-50" />
                </button>
              );
            })}
          </div>
        )}

        {/* Spacer */}
        {paths.length === 0 && <div className="flex-1" />}

        {/* Action buttons */}
        <div className="flex items-center gap-2 shrink-0">
          {onBackToSpectrum && (
            <button
              onClick={onBackToSpectrum}
              className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-all text-xs font-medium"
            >
              Back to Spectrum
            </button>
          )}

          {officialUrl && (
            <a
              href={officialUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-4 py-2 bg-emerald-700/80 hover:bg-emerald-600 text-white rounded-lg transition-all text-xs font-medium"
            >
              <ExternalLink size={12} />
              {brandName || "Official"}
            </a>
          )}

          {halilitUrl && (
            <a
              href={halilitUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-4 py-2 text-white rounded-lg transition-all text-xs font-medium shadow-lg"
              style={{
                backgroundColor: brandColor,
                boxShadow: `0 4px 14px ${brandColor}30`,
              }}
            >
              <ExternalLink size={12} />
              View on Halilit
            </a>
          )}
        </div>
      </div>
    </motion.div>
  );
};
