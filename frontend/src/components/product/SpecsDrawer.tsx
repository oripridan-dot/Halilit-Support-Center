/**
 * SpecsDrawer — Full specifications overlay
 *
 * A slide-out drawer that shows ALL product specifications.
 * Available in a click from the Bento Grid.
 * Specs are grouped and searchable.
 */

import React, { useState, useMemo } from "react";

interface SpecsDrawerProps {
  specs: Record<string, string>;
  productName: string;
  brandColor?: string;
  onClose: () => void;
}

export const SpecsDrawer: React.FC<SpecsDrawerProps> = ({
  specs,
  productName,
  brandColor = "#3b82f6",
  onClose,
}) => {
  const [search, setSearch] = useState("");

  const filteredSpecs = useMemo(() => {
    if (!search) return Object.entries(specs);
    const q = search.toLowerCase();
    return Object.entries(specs).filter(
      ([key, value]) =>
        key.toLowerCase().includes(q) ||
        String(value).toLowerCase().includes(q),
    );
  }, [specs, search]);

  const specCount = Object.keys(specs).length;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Drawer */}
      <div
        className="relative w-full max-w-lg bg-slate-950 border-l border-slate-800/60 
                    animate-in slide-in-from-right duration-300 flex flex-col"
      >
        {/* Header */}
        <div
          className="px-6 py-4 border-b border-slate-800/60 shrink-0"
          style={{ background: `${brandColor}05` }}
        >
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span className="text-lg">📋</span>
                Full Specifications
              </h2>
              <p className="text-[11px] text-zinc-500 mt-0.5">
                {productName} — {specCount} specs
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-slate-800 rounded-lg transition-colors text-zinc-400 hover:text-white"
            >
              ✕
            </button>
          </div>

          {/* Search */}
          {specCount > 5 && (
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search specifications…"
              className="w-full px-3 py-2 bg-slate-800/60 border border-slate-700/50 rounded-lg 
                         text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500/50"
            />
          )}
        </div>

        {/* Specs list */}
        <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
          {filteredSpecs.length === 0 ? (
            <p className="text-sm text-zinc-500 text-center py-8">
              {search
                ? "No matching specifications."
                : "No specifications available."}
            </p>
          ) : (
            <div className="space-y-0.5">
              {filteredSpecs.map(([key, value], idx) => (
                <div
                  key={key}
                  className={`flex justify-between items-start py-2.5 px-3 rounded-lg ${
                    idx % 2 === 0 ? "bg-slate-800/20" : ""
                  }`}
                >
                  <span className="text-xs text-zinc-400 capitalize font-medium min-w-0 pr-4">
                    {key.replace(/_/g, " ")}
                  </span>
                  <span className="text-xs text-white font-semibold text-right shrink-0 max-w-[55%]">
                    {typeof value === "object"
                      ? JSON.stringify(value)
                      : String(value)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
