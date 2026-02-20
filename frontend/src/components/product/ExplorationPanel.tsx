/**
 * ExplorationPanel — Main shell component.
 * Sub-components live in ExplorationPanelGuideView.tsx and ExplorationPanelRenderers.tsx.
 */

import React, { useMemo } from "react";
import type { ExplorationResult } from "../../hooks/useExploration";
import { SetupGuideView } from "./ExplorationPanelGuideView";
import type { GuideData, GuideSection } from "./ExplorationPanelGuideView";
import { GenericView, unwrapResult } from "./ExplorationPanelRenderers";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ExplorationPanelProps {
  result: ExplorationResult;
  onClose: () => void;
  brandColor?: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const EXPLORATION_TYPE_LABELS: Record<string, string> = {
  setup: "Setup Guide",
  artists: "Artist Spotlight",
  issues: "Field Notes & Known Issues",
  accessories: "Essential Accessories",
  deep_dive: "Deep Dive",
  compare: "Comparison",
};

const EXPLORATION_TYPE_ICONS: Record<string, string> = {
  setup: "\ud83d\udee0\ufe0f",
  artists: "\ud83c\udfa7",
  issues: "\u26a0\ufe0f",
  accessories: "\ud83c\udf92",
  deep_dive: "\ud83c\udf93",
  compare: "\u2694\ufe0f",
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const ExplorationPanel: React.FC<ExplorationPanelProps> = ({
  result,
  onClose,
  brandColor = "#3b82f6",
}): JSX.Element => {
  const topic = result.topic || result.action_type;
  const label = EXPLORATION_TYPE_LABELS[topic] || "Exploration";
  const icon = EXPLORATION_TYPE_ICONS[topic] || "\ud83d\udd0d";

  const isSetupGuide = useMemo(() => {
    const data = (result.content ?? result) as Record<string, unknown>;
    return topic === "setup" && Array.isArray((data as { sections?: unknown[] }).sections);
  }, [result, topic]);

  const guideData = useMemo((): GuideData | null => {
    if (!isSetupGuide) return null;
    const data = (result.content ?? result) as Record<string, unknown>;
    return {
      title: (data.title as string) || label,
      overview: (data.overview as string) || "",
      sections: (data as { sections?: GuideSection[] }).sections || [],
    };
  }, [result, isSetupGuide, label]);

  return (
    <div className="bg-slate-950/95 rounded-2xl border border-slate-700/40 overflow-hidden shadow-2xl shadow-black/40 backdrop-blur-sm">
      {/* Header */}
      <div className="relative px-6 py-4 border-b border-slate-800/60 overflow-hidden">
        <div className="absolute inset-0 opacity-[0.07]" style={{ background: `linear-gradient(135deg, ${brandColor}, transparent 60%)` }} />
        <div className="relative flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
              style={{ backgroundColor: `${brandColor}15`, border: `1px solid ${brandColor}30` }}
            >
              {icon}
            </div>
            <div>
              <h3 className="text-sm font-bold text-white tracking-wide">{guideData?.title || label}</h3>
              <p className="text-[10px] text-zinc-500 mt-0.5">AI-generated guide</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-lg text-zinc-500 hover:text-white hover:bg-slate-800/80 transition-all"
          >
            {"\u2715"}
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="max-h-[70vh] overflow-y-auto custom-scrollbar">
        {isSetupGuide && guideData ? (
          <SetupGuideView guide={guideData} brandColor={brandColor} />
        ) : result.format === "text" && typeof result.content === "string" ? (
          <div className="p-6">
            <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line">{result.content}</p>
          </div>
        ) : (
          <div className="p-6">
            <GenericView data={unwrapResult(result)} brandColor={brandColor} />
          </div>
        )}
      </div>
    </div>
  );
};
