/**
 * ExplorationPanelRenderers.tsx
 * Generic recursive renderers + unwrapResult helper.
 * Extracted from ExplorationPanel.tsx to stay under the 700-line ceiling.
 */

import React from "react";
import type { ExplorationResult } from "../../hooks/useExploration";
import {
  META_KEYS,
  getSectionIcon,
  isTipKey,
  formatLabel,
  getTitleFromObj,
} from "./explorationUtils";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface GenericViewProps {
  data: unknown;
  brandColor: string;
}

export interface RenderValueProps {
  value: unknown;
  brandColor: string;
  depth: number;
  label?: string;
}

export interface RenderCardProps {
  obj: Record<string, unknown>;
  brandColor: string;
  depth: number;
  index?: number;
  total?: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Unwraps ExplorationResult content, stripping metadata keys. */
export function unwrapResult(explorationResult: ExplorationResult): unknown {
  if (
    explorationResult.content &&
    Array.isArray(explorationResult.content) &&
    explorationResult.content.length === 1 &&
    typeof explorationResult.content[0] === "object"
  ) {
    return explorationResult.content[0];
  }
  if (explorationResult.content !== undefined) return explorationResult.content;
  const clean: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(explorationResult)) {
    if (!META_KEYS.has(key)) clean[key] = value;
  }
  return clean;
}

// ---------------------------------------------------------------------------
// RenderValue
// ---------------------------------------------------------------------------

export const RenderValue: React.FC<RenderValueProps> = ({
  value,
  brandColor,
  depth,
  label,
}): JSX.Element | null => {
  if (value === null || value === undefined) return null;

  if (typeof value === "string") {
    if (label && isTipKey(label)) {
      return (
        <div className="flex items-start gap-2.5 bg-amber-500/[0.06] border border-amber-500/15 rounded-xl px-4 py-3 mt-1.5">
          <span className="text-amber-400 text-sm mt-0.5 shrink-0">{"\ud83d\udca1"}</span>
          <div>
            <span className="text-[9px] font-bold text-amber-400/70 uppercase tracking-widest">Pro Tip</span>
            <p className="text-xs text-amber-200/80 leading-relaxed mt-0.5">{value}</p>
          </div>
        </div>
      );
    }
    return label ? (
      <div className="mb-2">
        <span className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">{formatLabel(label)}</span>
        <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line mt-0.5">{value}</p>
      </div>
    ) : (
      <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line">{value}</p>
    );
  }

  if (typeof value === "number" || typeof value === "boolean")
    return <span className="text-sm text-zinc-300 font-medium">{String(value)}</span>;

  if (Array.isArray(value)) {
    if (value.length === 0) return null;
    if (value.every((v) => typeof v === "string")) {
      return (
        <ul className="space-y-1.5 ml-0.5">
          {(value as string[]).map((item, idx) => (
            <li key={idx} className="flex items-start gap-2.5 text-sm text-zinc-300">
              <span className="mt-1.5 w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: brandColor }} />
              <span className="leading-relaxed">{item}</span>
            </li>
          ))}
        </ul>
      );
    }
    return (
      <div className="space-y-3">
        {value.map((item, idx) => {
          if (typeof item === "string") {
            return (
              <div key={idx} className="flex items-start gap-2.5 text-sm text-zinc-300">
                <span className="mt-1.5 w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: brandColor }} />
                <span>{item}</span>
              </div>
            );
          }
          if (typeof item !== "object" || item === null)
            return <span key={idx} className="text-xs text-zinc-400">{String(item)}</span>;
          return (
            <RenderCard
              key={idx}
              obj={item as Record<string, unknown>}
              brandColor={brandColor}
              depth={depth + 1}
              index={idx}
              total={value.length}
            />
          );
        })}
      </div>
    );
  }

  if (typeof value === "object") {
    return <RenderCard obj={value as Record<string, unknown>} brandColor={brandColor} depth={depth} />;
  }

  return <span className="text-xs text-zinc-400">{String(value)}</span>;
};

// ---------------------------------------------------------------------------
// RenderCard
// ---------------------------------------------------------------------------

export const RenderCard: React.FC<RenderCardProps> = ({
  obj,
  brandColor,
  depth,
  index,
  total,
}): JSX.Element => {
  const [titleKey, title] = getTitleFromObj(obj);
  const sectionIcon = title ? getSectionIcon(title) : "\u25b8";
  const contentKeys = Object.keys(obj).filter((k) => k !== titleKey && !META_KEYS.has(k));

  return (
    <div
      className="rounded-xl border overflow-hidden"
      style={{
        borderColor: depth < 1 ? `${brandColor}20` : "rgb(51 65 85 / 0.3)",
        backgroundColor: depth < 1 ? `${brandColor}03` : "rgb(30 41 59 / 0.25)",
      }}
    >
      {title && (
        <div
          className="px-4 py-2.5 border-b flex items-center gap-2.5"
          style={{ borderColor: `${brandColor}10`, background: `linear-gradient(90deg, ${brandColor}06, transparent)` }}
        >
          <span className="text-sm">{sectionIcon}</span>
          <h4 className="text-xs font-bold text-zinc-200 tracking-wide uppercase flex-1">{title}</h4>
          {typeof index === "number" && typeof total === "number" && (
            <span className="text-[9px] text-zinc-600">{index + 1}/{total}</span>
          )}
        </div>
      )}
      <div className="px-4 py-3 space-y-2">
        {contentKeys.map((key) => {
          const val = obj[key];
          if (isTipKey(key) && typeof val === "string") {
            return (
              <div key={key} className="flex items-start gap-2.5 bg-amber-500/[0.06] border border-amber-500/15 rounded-xl px-4 py-3">
                <span className="text-amber-400 text-sm mt-0.5 shrink-0">{"\ud83d\udca1"}</span>
                <div>
                  <span className="text-[9px] font-bold text-amber-400/70 uppercase tracking-widest">Pro Tip</span>
                  <p className="text-xs text-amber-200/80 leading-relaxed mt-0.5">{val}</p>
                </div>
              </div>
            );
          }
          return <RenderValue key={key} value={val} brandColor={brandColor} depth={depth + 1} label={key} />;
        })}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// GenericView
// ---------------------------------------------------------------------------

export const GenericView: React.FC<GenericViewProps> = ({ data, brandColor }): JSX.Element => (
  <RenderValue value={data} brandColor={brandColor} depth={0} />
);
