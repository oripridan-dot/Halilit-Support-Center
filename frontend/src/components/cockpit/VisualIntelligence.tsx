/**
 * Visual Intelligence — Signal chain and cheat sheet from JIT stream.
 * Renders when event: visual_intel is received.
 */

import React from "react";
import { motion } from "framer-motion";
import { GitBranch, FileText } from "lucide-react";

export interface SignalChainStep {
  step: number;
  label: string;
  type: string;
}

export interface VisualIntelData {
  signal_chain: SignalChainStep[];
  cheat_sheet: { title: string; bullets: string[] };
}

interface SignalChainCardProps {
  steps: SignalChainStep[];
  brandColor?: string;
}

/**
 * SignalChainCard — Linear flow of features/specs (e.g. input → preamp → output).
 */
export function SignalChainCard({
  steps,
  brandColor = "#3b82f6",
}: SignalChainCardProps) {
  if (!steps?.length) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-5"
      role="region"
      aria-label="Signal chain"
    >
      <div className="flex items-center gap-2 mb-4">
        <GitBranch size={14} style={{ color: brandColor }} aria-hidden />
        <h3 className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider">
          Signal Chain
        </h3>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        {steps.map((s, i) => (
          <React.Fragment key={s.step}>
            <div
              className="px-3 py-1.5 rounded-lg text-[11px] font-medium border bg-zinc-800/40 border-zinc-700/50 text-zinc-200"
              style={{
                borderColor: `${brandColor}40`,
              }}
            >
              {s.label}
            </div>
            {i < steps.length - 1 && (
              <span className="text-zinc-600 font-mono text-[10px]" aria-hidden>
                →
              </span>
            )}
          </React.Fragment>
        ))}
      </div>
    </motion.div>
  );
}

interface CheatSheetCardProps {
  title: string;
  bullets: string[];
  brandColor?: string;
}

/**
 * CheatSheetCard — Quick reference bullets (specs / features).
 */
export function CheatSheetCard({
  title,
  bullets,
  brandColor = "#3b82f6",
}: CheatSheetCardProps) {
  if (!bullets?.length) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.05 }}
      className="rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-5"
      role="region"
      aria-label="Cheat sheet"
    >
      <div className="flex items-center gap-2 mb-3">
        <FileText size={14} style={{ color: brandColor }} aria-hidden />
        <h3 className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider">
          Cheat Sheet
        </h3>
      </div>
      {title && (
        <p className="text-xs font-semibold text-white mb-2 truncate" title={title}>
          {title}
        </p>
      )}
      <ul className="space-y-1.5">
        {bullets.map((b, i) => (
          <li
            key={i}
            className="flex items-start gap-2 text-[11px] text-zinc-300"
          >
            <span
              className="mt-1.5 w-1 h-1 rounded-full shrink-0"
              style={{ backgroundColor: brandColor }}
              aria-hidden
            />
            <span className="leading-relaxed">{b}</span>
          </li>
        ))}
      </ul>
    </motion.div>
  );
}

interface VisualIntelligenceProps {
  data: VisualIntelData | null;
  brandColor?: string;
}

/**
 * Renders both SignalChainCard and CheatSheetCard when JIT has sent visual_intel.
 */
export function VisualIntelligence({
  data,
  brandColor = "#3b82f6",
}: VisualIntelligenceProps) {
  if (!data) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <SignalChainCard steps={data.signal_chain} brandColor={brandColor} />
      <CheatSheetCard
        title={data.cheat_sheet?.title ?? ""}
        bullets={data.cheat_sheet?.bullets ?? []}
        brandColor={brandColor}
      />
    </div>
  );
}
