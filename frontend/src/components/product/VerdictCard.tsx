/**
 * VerdictCard — Compact trusted review verdict
 *
 * Shows a single source verdict with sentiment, summary,
 * and a direct link to the full review.
 * Used inside the Bento Grid review carousel.
 */

import React from "react";
import type { ReviewVerdict } from "../../types";

const SENTIMENT_STYLES = {
  positive: {
    bg: "bg-emerald-500/8",
    border: "border-emerald-500/20",
    text: "text-emerald-400",
    badge: "✓ Positive",
  },
  neutral: {
    bg: "bg-zinc-500/8",
    border: "border-zinc-500/20",
    text: "text-zinc-400",
    badge: "— Neutral",
  },
  negative: {
    bg: "bg-red-500/8",
    border: "border-red-500/20",
    text: "text-red-400",
    badge: "✗ Negative",
  },
};

interface VerdictCardProps {
  verdict: ReviewVerdict;
  compact?: boolean;
}

export const VerdictCard: React.FC<VerdictCardProps> = ({
  verdict,
  compact = false,
}) => {
  const style = SENTIMENT_STYLES[verdict.sentiment] || SENTIMENT_STYLES.neutral;

  return (
    <div
      className={`${style.bg} ${style.border} border rounded-xl p-4 transition-all duration-200 hover:shadow-md`}
    >
      {/* Source header */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-bold text-white">{verdict.source}</span>
        <span className={`text-[10px] font-semibold ${style.text}`}>
          {style.badge}
        </span>
      </div>

      {/* Summary */}
      <p
        className={`text-zinc-300 leading-relaxed ${compact ? "text-[11px] line-clamp-2" : "text-xs line-clamp-3"}`}
      >
        {verdict.summary}
      </p>

      {/* Read full review link */}
      {verdict.url && (
        <a
          href={verdict.url}
          target="_blank"
          rel="noopener noreferrer"
          className={`inline-flex items-center gap-1 mt-2 text-[10px] font-medium ${style.text} hover:underline`}
        >
          Read Full Review ↗
        </a>
      )}
    </div>
  );
};
