/**
 * ReviewVerdictPanel — Displays trusted review verdicts
 *
 * Shows a carousel/grid of review summaries from Golden Circle sources,
 * with sentiment indicators and consensus score.
 */

import React from "react";
import type { ReviewVerdict } from "../../types";

interface ReviewVerdictPanelProps {
  verdicts: ReviewVerdict[];
  consensusScore: number;
}

const SENTIMENT_COLORS = {
  positive: {
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/20",
    text: "text-emerald-400",
    icon: "✓",
  },
  neutral: {
    bg: "bg-zinc-500/10",
    border: "border-zinc-500/20",
    text: "text-zinc-400",
    icon: "—",
  },
  negative: {
    bg: "bg-red-500/10",
    border: "border-red-500/20",
    text: "text-red-400",
    icon: "✗",
  },
};

export const ReviewVerdictPanel: React.FC<ReviewVerdictPanelProps> = ({
  verdicts,
  consensusScore,
}) => {
  if (!verdicts || verdicts.length === 0) return null;

  return (
    <div className="bg-slate-900/80 rounded-xl p-6 border border-slate-800/60">
      {/* Header with consensus score */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
          Trusted Reviews
          <span className="text-[10px] text-zinc-600 font-normal ml-1 uppercase tracking-wider">
            Golden Circle
          </span>
        </h2>
        {consensusScore > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-zinc-500 uppercase tracking-wider">
              Consensus
            </span>
            <div
              className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                consensusScore >= 80
                  ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20"
                  : consensusScore >= 60
                    ? "bg-amber-500/15 text-amber-400 border border-amber-500/20"
                    : "bg-red-500/15 text-red-400 border border-red-500/20"
              }`}
            >
              {consensusScore}/100
            </div>
          </div>
        )}
      </div>

      {/* Verdict cards */}
      <div className="grid gap-3">
        {verdicts.map((verdict, idx) => {
          const style =
            SENTIMENT_COLORS[verdict.sentiment] || SENTIMENT_COLORS.neutral;
          return (
            <div
              key={idx}
              className={`${style.bg} ${style.border} border rounded-lg p-4 transition-all duration-200 hover:brightness-110`}
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex items-center gap-2">
                  <span className={`${style.text} text-sm font-bold`}>
                    {style.icon}
                  </span>
                  <span className="text-xs font-semibold text-white">
                    {verdict.source}
                  </span>
                </div>
                {verdict.url && (
                  <a
                    href={verdict.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[10px] text-zinc-500 hover:text-zinc-300 transition-colors shrink-0"
                  >
                    Source ↗
                  </a>
                )}
              </div>
              <p className="text-sm text-zinc-300 leading-relaxed">
                {verdict.summary}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
