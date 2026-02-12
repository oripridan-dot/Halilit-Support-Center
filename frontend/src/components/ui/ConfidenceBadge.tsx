import React from "react";
import { Tooltip } from "./Tooltip";

interface ConfidenceBadgeProps {
  /** Quality score 0-100 */
  score?: number;
  /** Data status label */
  status?: "COMPLETE" | "GOOD" | "PARTIAL" | "MINIMAL" | string;
  /** Compact = small dot indicator, full = label badge */
  compact?: boolean;
}

const statusConfig: Record<
  string,
  { bg: string; text: string; border: string; label: string; dot: string }
> = {
  COMPLETE: {
    bg: "bg-emerald-500/15",
    text: "text-emerald-400",
    border: "border-emerald-500/30",
    label: "Verified",
    dot: "bg-emerald-400",
  },
  GOOD: {
    bg: "bg-green-500/15",
    text: "text-green-400",
    border: "border-green-500/30",
    label: "Good",
    dot: "bg-green-400",
  },
  PARTIAL: {
    bg: "bg-amber-500/15",
    text: "text-amber-400",
    border: "border-amber-500/30",
    label: "Partial",
    dot: "bg-amber-400",
  },
  MINIMAL: {
    bg: "bg-red-500/15",
    text: "text-red-400",
    border: "border-red-500/30",
    label: "Minimal",
    dot: "bg-red-400",
  },
};

/**
 * ConfidenceBadge — shows data quality level.
 * Aligns with Three Source Rules: confidence requires all 3 sources.
 */
export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  score,
  status = "MINIMAL",
  compact = false,
}) => {
  const cfg = statusConfig[status] || statusConfig.MINIMAL;

  if (compact) {
    return (
      <Tooltip
        content={`Data: ${cfg.label} ${score !== undefined ? `(${score}%)` : ""}`}
      >
        <span className={`w-2 h-2 rounded-full ${cfg.dot} inline-block`} />
      </Tooltip>
    );
  }

  return (
    <Tooltip
      content={`Quality Score: ${score ?? "?"}/100 — ${cfg.label} data coverage`}
    >
      <span
        className={`inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-bold rounded-full border uppercase tracking-wider ${cfg.bg} ${cfg.text} ${cfg.border}`}
      >
        <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
        {cfg.label}
        {score !== undefined && <span className="opacity-70">{score}%</span>}
      </span>
    </Tooltip>
  );
};
