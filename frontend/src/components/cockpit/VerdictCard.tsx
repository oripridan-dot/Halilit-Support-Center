import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, ThumbsUp, ThumbsDown } from "lucide-react";

export interface VerdictData {
  text: string;
  badge?: string;
  source?: string;
  pros?: string[];
  cons?: string[];
}

interface VerdictCardProps {
  verdict: VerdictData | null;
  brandColor?: string;
  isLoading?: boolean;
}

/**
 * VerdictCard — AI-generated summary with pros/cons pills.
 * Streams in from JIT intelligence.
 */
export const VerdictCard = ({
  verdict,
  brandColor = "#3b82f6",
  isLoading = false,
}: VerdictCardProps) => {
  if (isLoading) {
    return (
      <div className="rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-5 animate-pulse">
        <div className="h-3 w-24 bg-zinc-800 rounded mb-3" />
        <div className="h-2 w-full bg-zinc-800/60 rounded mb-2" />
        <div className="h-2 w-4/5 bg-zinc-800/60 rounded mb-4" />
        <div className="flex gap-2">
          <div className="h-5 w-16 bg-zinc-800/40 rounded-full" />
          <div className="h-5 w-20 bg-zinc-800/40 rounded-full" />
        </div>
      </div>
    );
  }

  if (!verdict) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-5 relative overflow-hidden"
      >
        {/* Brand accent line */}
        <div
          className="absolute top-0 left-0 right-0 h-[2px]"
          style={{
            background: `linear-gradient(90deg, transparent, ${brandColor}, transparent)`,
          }}
        />

        {/* Header */}
        <div className="flex items-center gap-2 mb-3">
          <Sparkles size={14} style={{ color: brandColor }} />
          <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider">
            AI Verdict
          </span>
          {verdict.badge && (
            <span
              className="ml-auto text-[10px] font-bold px-2 py-0.5 rounded-full border"
              style={{
                color: brandColor,
                borderColor: `${brandColor}40`,
                backgroundColor: `${brandColor}10`,
              }}
            >
              {verdict.badge}
            </span>
          )}
        </div>

        {/* Verdict text */}
        <p className="text-sm text-zinc-200 leading-relaxed mb-4">
          {verdict.text}
        </p>

        {/* Pros & Cons pills */}
        <div className="flex flex-wrap gap-2">
          {verdict.pros?.map((pro, i) => (
            <span
              key={`pro-${i}`}
              className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full"
            >
              <ThumbsUp size={10} />
              {pro}
            </span>
          ))}
          {verdict.cons?.map((con, i) => (
            <span
              key={`con-${i}`}
              className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium bg-orange-500/10 text-orange-400 border border-orange-500/20 rounded-full"
            >
              <ThumbsDown size={10} />
              {con}
            </span>
          ))}
        </div>

        {/* Source attribution */}
        {verdict.source && (
          <p className="mt-3 text-[10px] text-zinc-600">
            Source: {verdict.source}
          </p>
        )}
      </motion.div>
    </AnimatePresence>
  );
};
